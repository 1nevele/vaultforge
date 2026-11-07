"""Keep issue status labels consistent and unblock dependents (specs/002 CA-008).

Run by .github/workflows/issue-flow.yml on issue events, daily and on demand.
It only edits `status:*` labels. It never closes, assigns, comments on or
dispatches anything, and it never reads repository code from a pull request.

Rules (docs/operating-model.md):
  * An issue carries at most one status label. A newly added status label wins;
    otherwise the precedence is in-progress > blocked > ready.
  * A closed issue carries no status label (this releases the executor lock).
  * Dependencies are `Blocked by #N` / `Depends on #N` lines in the issue's
    `## Dependencies` section, or a `Depends-on: #N` line anywhere.
  * `status:blocked` becomes `status:ready` once every declared dependency is
    closed as completed. A block with no declared dependency is manual and left
    alone. A `status:ready` issue with an open dependency becomes blocked.
"""
import json
import os
import re
import subprocess
from urllib.parse import quote

READY, IN_PROGRESS, BLOCKED = 'status:ready', 'status:in-progress', 'status:blocked'
PRECEDENCE = (IN_PROGRESS, BLOCKED, READY)
STATUS = set(PRECEDENCE)

_REFS = r'#\d+(?:\s*(?:,|and|&)?\s*#\d+)*'
_SECTION_LINK = re.compile(rf'\b(?:blocked\s+by|depends\s+on)\s*:?\s*({_REFS})', re.I)
_ANYWHERE_LINK = re.compile(rf'^\s*depends-on\s*:\s*({_REFS})', re.I | re.M)
_HEADING = re.compile(r'^#{1,6}\s+(.*)$', re.M)


def _numbers(refs):
    return {int(n) for n in re.findall(r'#(\d+)', refs)}


def dependencies(body):
    """Issue numbers this issue declares it depends on."""
    if not body:
        return set()
    found = set()
    for match in _ANYWHERE_LINK.finditer(body):
        found |= _numbers(match.group(1))
    headings = list(_HEADING.finditer(body))
    for index, heading in enumerate(headings):
        if heading.group(1).strip().lower() != 'dependencies':
            continue
        end = headings[index + 1].start() if index + 1 < len(headings) else len(body)
        for match in _SECTION_LINK.finditer(body[heading.end():end]):
            found |= _numbers(match.group(1))
    return found


def plan(subject, completed, added=None):
    """Return (labels to add, labels to remove) for one issue.

    `completed` maps dependency issue numbers to True when that issue is closed
    as completed; missing or False means the dependency is not satisfied.
    """
    labels = set(subject['labels'])
    present = labels & STATUS
    if subject['state'] != 'open':
        return set(), present
    if added in present:
        keep = added
    else:
        keep = next((s for s in PRECEDENCE if s in present), None)
    remove = present - {keep} if keep else set()
    deps = dependencies(subject.get('body')) - {subject['number']}
    satisfied = all(completed.get(n, False) for n in deps)
    if keep == BLOCKED and deps and satisfied:
        return {READY}, remove | {BLOCKED}
    if keep == READY and deps and not satisfied:
        return {BLOCKED}, remove | {READY}
    return set(), remove


def _is_issue(item):
    return 'pull_request' not in item


def reconcile(event_name, event, gh):
    """Apply the rules to the event's issue, then sweep every open issue."""
    actions = []
    cache = {}

    def completed(number):
        if number not in cache:
            try:
                found = gh.issue(number)
            except Exception:  # unknown/foreign reference: never satisfied
                cache[number] = False
            else:
                cache[number] = (found['state'] == 'closed'
                                 and found.get('state_reason') == 'completed')
        return cache[number]

    def apply(subject, added=None):
        if not _is_issue(subject):
            return
        deps = dependencies(subject.get('body')) - {subject['number']}
        add, remove = plan(subject, {n: completed(n) for n in deps}, added=added)
        if add:
            gh.add_labels(subject['number'], sorted(add))
        for label in sorted(remove):
            gh.remove_label(subject['number'], label)
        if add or remove:
            actions.append({'issue': subject['number'],
                            'add': sorted(add), 'remove': sorted(remove)})

    number = (event.get('issue') or {}).get('number')
    if event_name == 'issues' and number:
        added = (event.get('label') or {}).get('name') if event.get('action') == 'labeled' else None
        apply(gh.issue(number), added=added)
    for subject in gh.open_issues():
        if subject['number'] != number:
            apply(subject)
    return actions


class GitHub:
    """Minimal `gh api` client for one repository."""

    def __init__(self, repository, run=subprocess.run):
        self.repository = repository
        self.run = run

    def _api(self, *args, allow_missing=False):
        result = self.run(['gh', 'api', *args], capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            if allow_missing and 'HTTP 404' in result.stderr:
                return ''
            raise RuntimeError(f'gh api failed: {result.stderr.strip()[:200]}')
        return result.stdout

    @staticmethod
    def _shape(raw):
        shaped = {'number': raw['number'], 'state': raw['state'],
                  'state_reason': raw.get('state_reason'), 'body': raw.get('body') or '',
                  'labels': [label['name'] for label in raw.get('labels', [])]}
        if 'pull_request' in raw:
            shaped['pull_request'] = True
        return shaped

    def open_issues(self):
        out = self._api('--paginate', f'repos/{self.repository}/issues?state=open&per_page=100',
                        '--jq', '.[]')
        return [self._shape(json.loads(line)) for line in out.splitlines() if line.strip()]

    def issue(self, number):
        return self._shape(json.loads(self._api(f'repos/{self.repository}/issues/{number}')))

    def add_labels(self, number, labels):
        fields = [arg for label in labels for arg in ('-f', f'labels[]={label}')]
        self._api('-X', 'POST', f'repos/{self.repository}/issues/{number}/labels', *fields)

    def remove_label(self, number, label):
        self._api('-X', 'DELETE',
                  f'repos/{self.repository}/issues/{number}/labels/{quote(label, safe="")}',
                  allow_missing=True)


def main():
    event_name = os.environ['GITHUB_EVENT_NAME']
    with open(os.environ['GITHUB_EVENT_PATH']) as handle:
        event = json.load(handle)
    actions = reconcile(event_name, event, GitHub(os.environ['GITHUB_REPOSITORY']))
    print(json.dumps({'event': event_name, 'changes': actions}, sort_keys=True))


if __name__ == '__main__':
    main()
