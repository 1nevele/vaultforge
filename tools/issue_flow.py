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
  * Dependencies are every `#N`, same-repository `owner/repo#N` or issue/PR URL in
    the issue's `## Dependencies` section (up to the next heading of the same or
    higher level) or on a `Depends-on:` line anywhere. A dependency is satisfied
    when it is an issue closed as completed, or a merged pull request. A reference
    to another repository is never satisfied here, so it keeps the issue blocked.
  * `status:blocked` becomes `status:ready` once every declared dependency is
    satisfied; `status:ready` becomes `status:blocked` while one is not. A block
    with no declared dependency is left alone.
  * `status:hold` is a flag for the executor (skip this issue). The reconciler
    keeps it and applies the rules above to the issue's other status labels, so
    lifting the hold restores the issue to the queue.
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
BOT = 'github-actions[bot]'

_FENCE = re.compile(r'^\s*(```|~~~).*?^\s*\1[^\n]*$', re.M | re.S)
_COMMENT = re.compile(r'<!--.*?-->', re.S)
_HEADING = re.compile(r'^(#{1,6})\s+(.*?)\s*$', re.M)
_DEPENDS_ON_LINE = re.compile(r'^\s*depends-on\s*:(.*)$', re.I | re.M)
# `#N`, `owner/repo#N`, or a github.com issue/pull URL. A bare `#N` must not
# follow a word character, slash or dot.
_REF = re.compile(
    r'https?://github\.com/(?P<url_repo>[\w.-]+/[\w.-]+)/(?:issues|pull)/(?P<url_n>\d+)'
    r'|(?P<full_repo>[\w.-]+/[\w.-]+)#(?P<full_n>\d+)'
    r'|(?<![\w/.])#(?P<n>\d+)\b')


class NotFound(RuntimeError):
    """The referenced issue or pull request does not exist (HTTP 404/410)."""


def _refs(text, repository):
    """Same-repository numbers as ints; other repositories as 'owner/repo#N' keys."""
    found = set()
    for match in _REF.finditer(text):
        if match.group('n'):
            found.add(int(match.group('n')))
            continue
        repo = match.group('url_repo') or match.group('full_repo')
        number = int(match.group('url_n') or match.group('full_n'))
        found.add(number if repo.lower() == repository.lower() else f'{repo}#{number}')
    return found


def _is_dependencies_heading(title):
    words = title.strip('*#: \t').lower().split()
    return bool(words) and words[0].rstrip(':') == 'dependencies'


def dependencies(body, repository=''):
    """What this issue declares it depends on (over-detection is the safe side)."""
    if not body:
        return set()
    text = _COMMENT.sub('', _FENCE.sub('', body))
    found = set()
    for match in _DEPENDS_ON_LINE.finditer(text):
        found |= _refs(match.group(1), repository)
    headings = list(_HEADING.finditer(text))
    for index, heading in enumerate(headings):
        if not _is_dependencies_heading(heading.group(2)):
            continue
        level = len(heading.group(1))
        end = next((h.start() for h in headings[index + 1:] if len(h.group(1)) <= level),
                   len(text))
        found |= _refs(text[heading.end():end], repository)
    return found


def plan(subject, completed, newest=None, repository=''):
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
    if newest in present:
        keep = newest
    else:
        keep = next((s for s in PRECEDENCE if s in present), None)
    if keep is None:
        return set(), set()
    deps = dependencies(subject.get('body'), repository) - {subject['number']}
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

    repository = getattr(gh, 'repository', '')

    def satisfied(number):
        if isinstance(number, str):  # another repository: never satisfied here
            return False
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
        deps = dependencies(subject.get('body'), repository) - {subject['number']}
        return plan(subject, {n: satisfied(n) for n in deps}, newest=newest,
                    repository=repository)

    subjects = []
    number = (event.get('issue') or {}).get('number') if event_name == 'issues' else None
    if number:
        triggering = gh.issue(number)
        if triggering['state'] != 'open':
            subjects.append(triggering)
    subjects.extend(gh.open_issues())

    # Plan everything first: a lookup failure aborts the run before any write.
    plans = [(s['number'], plan_for(s)) for s in subjects if _is_issue(s)]

    # A write failure on one issue must not stop the others; report all at the end.
    actions, failures = [], []
    for issue_number, (add, remove) in plans:
        try:
            if add:
                gh.add_labels(issue_number, sorted(add))
            for label in sorted(remove):
                gh.remove_label(issue_number, label)
        except RuntimeError as error:
            failures.append(f'#{issue_number}: {error}')
            continue
        if add or remove:
            actions.append({'issue': issue_number, 'add': sorted(add), 'remove': sorted(remove)})
    if failures:
        raise RuntimeError('label writes failed: ' + '; '.join(failures))
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
        """The most recently added label among `candidates`, from issue events.

        Labels this workflow added itself are skipped, so a write from a stale
        plan can never outrank a person's or the executor's later choice.
        """
        out = self._api('--paginate', f'repos/{self.repository}/issues/{number}/events?per_page=100',
                        '--jq', '.[]')
        newest = None
        for event in self._lines(out):
            name = (event.get('label') or {}).get('name')
            actor = (event.get('actor') or {}).get('login')
            if event.get('event') == 'labeled' and name in candidates and actor != BOT:
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
