"""Synthetic fixtures for the issue-flow label reconciler (specs/002 CA-008)."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'issue_flow.py'


def load():
    spec = importlib.util.spec_from_file_location('issue_flow', SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def issue(number, labels=(), body='', state='open', state_reason=None):
    return {'number': number, 'labels': list(labels), 'body': body,
            'state': state, 'state_reason': state_reason}


BLOCKED_BY_1 = '## Dependencies\n- Blocked by #1 (S01); accepted contracts required.\n\n## Owned paths\nx\n'


class FakeGitHub:
    """In-memory stand-in for the GitHub issues API."""

    def __init__(self, *issues):
        self.issues = {i['number']: dict(i, labels=list(i['labels'])) for i in issues}
        self.calls = []

    def open_issues(self):
        return [dict(i, labels=list(i['labels']))
                for i in self.issues.values() if i['state'] == 'open']

    def issue(self, number):
        found = self.issues[number]
        return dict(found, labels=list(found['labels']))

    def add_labels(self, number, labels):
        self.calls.append(('add', number, tuple(sorted(labels))))
        for label in labels:
            if label not in self.issues[number]['labels']:
                self.issues[number]['labels'].append(label)

    def remove_label(self, number, label):
        self.calls.append(('remove', number, label))
        if label in self.issues[number]['labels']:
            self.issues[number]['labels'].remove(label)

    def labels(self, number):
        return sorted(self.issues[number]['labels'])


class DependencyParsingTests(unittest.TestCase):
    def setUp(self):
        self.flow = load()

    def test_blocked_by_in_dependencies_section(self):
        self.assertEqual(self.flow.dependencies(BLOCKED_BY_1), {1})

    def test_several_dependencies_in_one_line(self):
        body = '## Dependencies\n- Blocked by #1, #2 and #7.\n'
        self.assertEqual(self.flow.dependencies(body), {1, 2, 7})

    def test_depends_on_line_anywhere(self):
        body = 'Some text.\n\nDepends-on: #3, #4\n'
        self.assertEqual(self.flow.dependencies(body), {3, 4})

    def test_references_outside_dependencies_section_are_ignored(self):
        body = '## Initial wave\n- [ ] #1 — S01\n- [ ] #2 — blocked by #1\n'
        self.assertEqual(self.flow.dependencies(body), set())

    def test_no_predecessor_text(self):
        body = '## Dependencies\nNo predecessor issue; ready for review.\n'
        self.assertEqual(self.flow.dependencies(body), set())

    def test_empty_or_missing_body(self):
        self.assertEqual(self.flow.dependencies(None), set())
        self.assertEqual(self.flow.dependencies(''), set())


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.flow = load()

    def plan(self, subject, deps=None, added=None):
        return self.flow.plan(subject, deps or {}, added=added)

    def test_added_status_label_replaces_the_others(self):
        subject = issue(1, ['claude:scheduled', 'status:ready', 'status:in-progress'])
        self.assertEqual(self.plan(subject, added='status:in-progress'),
                         (set(), {'status:ready'}))

    def test_adding_ready_releases_an_in_progress_lock(self):
        subject = issue(1, ['status:in-progress', 'status:ready'])
        self.assertEqual(self.plan(subject, added='status:ready'),
                         (set(), {'status:in-progress'}))

    def test_sweep_keeps_in_progress_over_ready(self):
        subject = issue(1, ['status:ready', 'status:in-progress'])
        self.assertEqual(self.plan(subject), (set(), {'status:ready'}))

    def test_sweep_keeps_blocked_over_ready(self):
        subject = issue(2, ['status:ready', 'status:blocked'])
        self.assertEqual(self.plan(subject), (set(), {'status:ready'}))

    def test_non_status_labels_are_never_touched(self):
        subject = issue(3, ['project:sentinel', 'claude:scheduled'])
        self.assertEqual(self.plan(subject), (set(), set()))

    def test_blocked_issue_becomes_ready_when_all_dependencies_completed(self):
        subject = issue(2, ['status:blocked'], BLOCKED_BY_1)
        self.assertEqual(self.plan(subject, {1: True}),
                         ({'status:ready'}, {'status:blocked'}))

    def test_blocked_issue_stays_blocked_while_a_dependency_is_open(self):
        subject = issue(2, ['status:blocked'], '## Dependencies\nBlocked by #1, #5\n')
        self.assertEqual(self.plan(subject, {1: True, 5: False}), (set(), set()))

    def test_dependency_closed_not_planned_does_not_unblock(self):
        subject = issue(2, ['status:blocked'], BLOCKED_BY_1)
        self.assertEqual(self.plan(subject, {1: False}), (set(), set()))

    def test_manual_block_without_dependencies_is_left_alone(self):
        subject = issue(2, ['status:blocked'], 'Waiting on a host decision.')
        self.assertEqual(self.plan(subject), (set(), set()))

    def test_ready_issue_with_open_dependency_is_blocked(self):
        subject = issue(2, ['status:ready'], BLOCKED_BY_1)
        self.assertEqual(self.plan(subject, {1: False}),
                         ({'status:blocked'}, {'status:ready'}))

    def test_in_progress_issue_is_not_reblocked(self):
        subject = issue(2, ['status:in-progress'], BLOCKED_BY_1)
        self.assertEqual(self.plan(subject, {1: False}), (set(), set()))

    def test_self_reference_is_not_a_dependency(self):
        subject = issue(2, ['status:blocked'], '## Dependencies\nBlocked by #2 and #1\n')
        self.assertEqual(self.plan(subject, {1: True}),
                         ({'status:ready'}, {'status:blocked'}))

    def test_closed_issue_drops_every_status_label(self):
        subject = issue(1, ['claude:scheduled', 'status:in-progress', 'status:ready'],
                        state='closed', state_reason='completed')
        self.assertEqual(self.plan(subject),
                         (set(), {'status:in-progress', 'status:ready'}))


class ReconcileTests(unittest.TestCase):
    def setUp(self):
        self.flow = load()

    def test_closing_a_dependency_unblocks_its_dependents(self):
        gh = FakeGitHub(
            issue(1, ['claude:scheduled', 'status:in-progress'],
                  state='closed', state_reason='completed'),
            issue(2, ['claude:scheduled', 'status:blocked'], BLOCKED_BY_1),
            issue(3, ['claude:scheduled', 'status:blocked'], BLOCKED_BY_1),
            issue(6, ['type:tracking'], '## Initial wave\n- [ ] #1\n'),
        )
        self.flow.reconcile('issues', {'action': 'closed', 'issue': {'number': 1}}, gh)
        self.assertEqual(gh.labels(1), ['claude:scheduled'])
        self.assertEqual(gh.labels(2), ['claude:scheduled', 'status:ready'])
        self.assertEqual(gh.labels(3), ['claude:scheduled', 'status:ready'])
        self.assertEqual(gh.labels(6), ['type:tracking'])

    def test_labeled_event_uses_the_added_label(self):
        gh = FakeGitHub(issue(1, ['status:in-progress', 'status:ready']))
        event = {'action': 'labeled', 'issue': {'number': 1},
                 'label': {'name': 'status:ready'}}
        self.flow.reconcile('issues', event, gh)
        self.assertEqual(gh.labels(1), ['status:ready'])

    def test_sweep_repairs_every_open_issue(self):
        gh = FakeGitHub(
            issue(1, ['status:ready', 'status:in-progress']),
            issue(2, ['status:ready'], BLOCKED_BY_1),
        )
        self.flow.reconcile('workflow_dispatch', {}, gh)
        self.assertEqual(gh.labels(1), ['status:in-progress'])
        self.assertEqual(gh.labels(2), ['status:blocked'])

    def test_consistent_state_makes_no_calls(self):
        gh = FakeGitHub(
            issue(1, ['status:in-progress']),
            issue(2, ['status:blocked'], BLOCKED_BY_1),
        )
        self.flow.reconcile('schedule', {}, gh)
        self.assertEqual(gh.calls, [])

    def test_pull_request_items_are_ignored(self):
        gh = FakeGitHub(issue(9, ['status:ready', 'status:blocked']))
        gh.issues[9]['pull_request'] = {'url': 'x'}
        self.flow.reconcile('schedule', {}, gh)
        self.assertEqual(gh.calls, [])

    def test_adds_are_applied_before_removals(self):
        gh = FakeGitHub(
            issue(1, [], state='closed', state_reason='completed'),
            issue(2, ['status:blocked'], BLOCKED_BY_1),
        )
        self.flow.reconcile('schedule', {}, gh)
        self.assertEqual(gh.calls, [('add', 2, ('status:ready',)),
                                    ('remove', 2, 'status:blocked')])


class GitHubClientTests(unittest.TestCase):
    def setUp(self):
        self.flow = load()

    def test_label_names_are_url_encoded_on_removal(self):
        seen = []

        class Done:
            returncode, stdout, stderr = 0, '', ''

        def run(args, **_):
            seen.append(args)
            return Done()

        client = self.flow.GitHub('owner/repo', run=run)
        client.remove_label(4, 'status:in-progress')
        self.assertIn('repos/owner/repo/issues/4/labels/status%3Ain-progress', seen[0])

    def test_removing_an_absent_label_is_not_an_error(self):
        class Missing:
            returncode, stdout, stderr = 1, '', 'gh: Label does not exist (HTTP 404)'

        client = self.flow.GitHub('owner/repo', run=lambda args, **_: Missing())
        client.remove_label(4, 'status:ready')

    def test_other_api_failures_raise(self):
        class Broken:
            returncode, stdout, stderr = 1, '', 'gh: Forbidden (HTTP 403)'

        client = self.flow.GitHub('owner/repo', run=lambda args, **_: Broken())
        with self.assertRaises(RuntimeError):
            client.remove_label(4, 'status:ready')


if __name__ == '__main__':
    unittest.main()
