"""Keep issue status labels consistent and unblock dependents (specs/002 CA-008).

Run by .github/workflows/issue-flow.yml on issue events, daily and on demand.
It only edits `status:*` labels. It never closes, assigns, comments on or
dispatches anything, and it never reads repository code from a pull request.

The reconciler is state-based: every run reads current labels, label history
and dependency states, computes a final label set per issue, and only then
writes. The triggering event only says that something changed.

Rules (docs/operating-model.md):
  * An open issue carries exactly one of ready / in-progress / blocked once it has
    any. The most recently added of them wins (from the issue's label history);
    without history, in-progress > blocked > ready.
  * A closed issue carries no status label.
  * Dependencies are every `#N` in the issue's `## Dependencies` section, or on a
    `Depends-on:` line anywhere. A dependency is satisfied when it is an issue
    closed as completed, or a merged pull request.
  * `status:blocked` becomes `status:ready` once every declared dependency is
    satisfied; `status:ready` becomes `status:blocked` while one is not. A block
    with no declared dependency is left alone.
  * `status:hold` is a manual block: the reconciler only removes `status:ready`
    from a held issue and otherwise leaves its labels alone.
"""
import json
import os
import re
import subprocess
from urllib.parse import quote

READY, IN_PROGRESS, BLOCKED, HOLD = (
    'status:ready', 'status:in-progress', 'status:blocked', 'status:hold')
PRECEDENCE = (IN_PROGRESS, BLOCKED, READY)
STATUS = set(PRECEDENCE)
ALL_STATUS = STATUS | {HOLD}

_FENCE = re.compile(r'^\s*(```|~~~).*?^\s*\1[^\n]*$', re.M | re.S)
_HEADING = re.compile(r'^#{1,6}\s+(.*?)\s*$', re.M)
_DEPENDS_ON_LINE = re.compile(r'^\s*depends-on\s*:(.*)$', re.I | re.M)
# `#N` not preceded by a word character, slash or dot (so `owner/repo#N` and
# `x#N` are not references to this repository).
_REF = re.compile(r'(?<![\w/.])#(\d+)\b')


class NotFound(RuntimeError):
    """The referenced issue or pull request does not exist (HTTP 404/410)."""


def _refs(text):
    return {int(n) for n in _REF.findall(text)}


def _is_dependencies_heading(title):
    return title.strip('*#: \t').lower() == 'dependencies'


def dependencies(body):
    """Issue numbers this issue declares it depends on (over-detection is safe)."""
    if not body:
        return set()
    text = _FENCE.sub('', body)
    found = set()
    for match in _DEPENDS_ON_LINE.finditer(text):
        found |= _refs(match.group(1))
    headings = list(_HEADING.finditer(text))
    for index, heading in enumerate(headings):
        if not _is_dependencies_heading(heading.group(1)):
            continue
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        found |= _refs(text[heading.end():end])
    return found


def plan(subject, completed, newest=None):
    """Return (labels to add, labels to remove) for one issue.

    `completed` maps dependency numbers to True when satisfied. `newest` is the
    most recently added of the issue's current status labels, if known. The
    result is derived from the final label set, so no label is both added and
    removed and an issue that has a status label keeps exactly one.
    """
    labels = set(subject['labels'])
    if subject['state'] != 'open':
        return set(), labels & ALL_STATUS
    present = labels & STATUS
    if HOLD in labels:
        return set(), present & {READY}
    if newest in present:
        keep = newest
    else:
        keep = next((s for s in PRECEDENCE if s in present), None)
    if keep is None:
        return set(), set()
    deps = dependencies(subject.get('body')) - {subject['number']}
    if deps:
        satisfied = all(completed.get(n, False) for n in deps)
        if keep == BLOCKED and satisfied:
            keep = READY
        elif keep == READY and not satisfied:
            keep = BLOCKED
    return {keep} - labels, present - {keep}


def _is_issue(item):
    return not item.get('pull_request')


def reconcile(event_name, event, gh):
    """Plan every affected issue from current state, then apply all writes."""
    cache = {}

    def satisfied(number):
        if number not in cache:
            try:
                found = gh.issue(number)
            except NotFound:
                cache[number] = False
            else:
                if found.get('pull_request'):
                    cache[number] = bool(found.get('merged'))
                else:
                    cache[number] = (found['state'] == 'closed'
                                     and found.get('state_reason') == 'completed')
        return cache[number]

    def plan_for(subject):
        present = set(subject['labels']) & STATUS
        newest = gh.latest_added(subject['number'], present) if len(present) > 1 else None
        deps = dependencies(subject.get('body')) - {subject['number']}
        return plan(subject, {n: satisfied(n) for n in deps}, newest=newest)

    subjects = []
    number = (event.get('issue') or {}).get('number') if event_name == 'issues' else None
    if number:
        triggering = gh.issue(number)
        if triggering['state'] != 'open':
            subjects.append(triggering)
    subjects.extend(gh.open_issues())

    # Plan everything first: a lookup failure aborts the run before any write.
    plans = [(s['number'], plan_for(s)) for s in subjects if _is_issue(s)]

    actions = []
    for issue_number, (add, remove) in plans:
        if add:
            gh.add_labels(issue_number, sorted(add))
        for label in sorted(remove):
            gh.remove_label(issue_number, label)
        if add or remove:
            actions.append({'issue': issue_number, 'add': sorted(add), 'remove': sorted(remove)})
    return actions


class GitHub:
    """Minimal `gh api` client for one repository."""

    def __init__(self, repository, run=subprocess.run):
        self.repository = repository
        self.run = run

    def _api(self, *args, allow_missing=False):
        result = self.run(['gh', 'api', *args], capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            missing = 'HTTP 404' in result.stderr or 'HTTP 410' in result.stderr
            if missing and allow_missing:
                return ''
            if missing:
                raise NotFound(result.stderr.strip()[:200])
            raise RuntimeError(f'gh api failed: {result.stderr.strip()[:200]}')
        return result.stdout

    @staticmethod
    def _shape(raw):
        shaped = {'number': raw['number'], 'state': raw['state'],
                  'state_reason': raw.get('state_reason'), 'body': raw.get('body') or '',
                  'labels': [label['name'] for label in raw.get('labels', [])]}
        if 'pull_request' in raw:
            shaped['pull_request'] = True
            shaped['merged'] = bool((raw['pull_request'] or {}).get('merged_at'))
        return shaped

    @staticmethod
    def _lines(out):
        return [json.loads(line) for line in out.splitlines() if line.strip()]

    def open_issues(self):
        out = self._api('--paginate', f'repos/{self.repository}/issues?state=open&per_page=100',
                        '--jq', '.[]')
        return [self._shape(raw) for raw in self._lines(out)]

    def issue(self, number):
        return self._shape(json.loads(self._api(f'repos/{self.repository}/issues/{number}')))

    def latest_added(self, number, candidates):
        """The most recently added label among `candidates`, from issue events."""
        out = self._api('--paginate', f'repos/{self.repository}/issues/{number}/events?per_page=100',
                        '--jq', '.[]')
        newest = None
        for event in self._lines(out):
            name = (event.get('label') or {}).get('name')
            if event.get('event') == 'labeled' and name in candidates:
                newest = name
        return newest

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
