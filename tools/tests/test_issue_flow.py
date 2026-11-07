"""Synthetic fixtures for the issue-flow label reconciler (specs/002 CA-008)."""
import importlib.util
import json
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
    """In-memory stand-in for the GitHub issues API, with label history."""

    def __init__(self, flow, *issues, errors=None):
        self.flow = flow
        self.repository = 'owner/repo'
        self.issues = {i['number']: dict(i, labels=list(i['labels'])) for i in issues}
        # Label history in the order labels were added (oldest first).
        self.history = {n: list(i['labels']) for n, i in self.issues.items()}
        self.errors = errors or {}
        self.calls = []

    def open_issues(self):
        return [dict(i, labels=list(i['labels']))
                for i in self.issues.values() if i['state'] == 'open']

    def closed_with_status(self):
        return [dict(i, labels=list(i['labels'])) for i in self.issues.values()
                if i['state'] != 'open' and set(i['labels']) & self.flow.ALL_STATUS]

    def issue(self, number):
        if number in self.errors:
            raise self.errors[number]
        if number not in self.issues:
            raise self.flow.NotFound(number)
        found = self.issues[number]
        return dict(found, labels=list(found['labels']))

    def latest_added(self, number, candidates):
        added = [label for label in self.history[number] if label in candidates]
        return added[-1] if added else None

    def add_labels(self, number, labels):
        self.calls.append(('add', number, tuple(sorted(labels))))
        for label in labels:
            if label not in self.issues[number]['labels']:
                self.issues[number]['labels'].append(label)
            self.history[number].append(label)

    def remove_label(self, number, label):
        self.calls.append(('remove', number, label))
        if label in self.issues[number]['labels']:
            self.issues[number]['labels'].remove(label)

    def labels(self, number):
        return sorted(self.issues[number]['labels'])


class DependencyParsingTests(unittest.TestCase):
    def setUp(self):
        self.flow = load()

    def deps(self, body):
        return self.flow.dependencies(body, 'owner/repo')

    def test_blocked_by_in_dependencies_section(self):
        self.assertEqual(self.deps(BLOCKED_BY_1), {1})

    def test_several_dependencies_in_one_line(self):
        self.assertEqual(self.deps('## Dependencies\n- Blocked by #1, #2 and #7.\n'), {1, 2, 7})

    def test_annotated_references_all_count(self):
        body = '## Dependencies\n- Blocked by #1 (S01), #3 (S03)\n- Blocked by #4 (S04) and #5 (S05)\n'
        self.assertEqual(self.deps(body), {1, 3, 4, 5})

    def test_list_items_under_a_blocked_by_line_count(self):
        self.assertEqual(self.deps('## Dependencies\nBlocked by:\n- #1\n- #3\n'), {1, 3})

    def test_depends_on_line_anywhere_counts_every_reference(self):
        self.assertEqual(self.deps('Some text.\n\nDepends-on: #3 (S03), #4\n'), {3, 4})

    def test_references_outside_dependencies_section_are_ignored(self):
        body = '## Initial wave\n- [ ] #1 — S01\n- [ ] #2 — blocked by #1\n'
        self.assertEqual(self.deps(body), set())

    def test_foreign_references_are_kept_as_unsatisfiable_keys(self):
        self.assertEqual(self.deps('## Dependencies\nBlocked by other/repo#9 and #2\n'),
                         {2, 'other/repo#9'})

    def test_same_repository_full_references_and_urls_count(self):
        body = ('## Dependencies\n- owner/repo#3\n- https://github.com/owner/repo/issues/4\n'
                '- https://github.com/owner/repo/pull/5\n- https://github.com/other/repo/issues/6\n')
        self.assertEqual(self.deps(body), {3, 4, 5, 'other/repo#6'})

    def test_a_deeper_sub_heading_does_not_end_the_section(self):
        body = '## Dependencies\n- #1\n### Also needed\n- #3\n## Owned paths\n- #9\n'
        self.assertEqual(self.deps(body), {1, 3})

    def test_html_comments_are_ignored(self):
        self.assertEqual(self.deps('## Dependencies\n<!-- e.g. Blocked by #12 -->\n- #2\n'), {2})

    def test_heading_with_a_qualifier_is_recognized(self):
        self.assertEqual(self.deps('## Dependencies (hard)\n- #7\n'), {7})

    def test_heading_variants_are_recognized(self):
        for heading in ('## Dependencies:', '### Dependencies ##', '## dependencies'):
            with self.subTest(heading=heading):
                self.assertEqual(self.deps(f'{heading}\n- Blocked by #4\n'), {4})

    def test_a_hash_line_inside_a_code_fence_does_not_end_the_section(self):
        body = '## Dependencies\n```\n# example\n```\n- Blocked by #8\n'
        self.assertEqual(self.deps(body), {8})

    def test_no_predecessor_text(self):
        self.assertEqual(self.deps('## Dependencies\nNo predecessor issue; ready for review.\n'), set())

    def test_empty_or_missing_body(self):
        self.assertEqual(self.deps(None), set())
        self.assertEqual(self.deps(''), set())


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.flow = load()

    def plan(self, subject, deps=None, newest=None):
        return self.flow.plan(subject, deps or {}, newest=newest)

    def test_newest_status_label_replaces_the_others(self):
        subject = issue(1, ['claude:scheduled', 'status:ready', 'status:in-progress'])
        self.assertEqual(self.plan(subject, newest='status:in-progress'), (set(), {'status:ready'}))

    def test_newest_ready_releases_an_in_progress_lock(self):
        subject = issue(1, ['status:in-progress', 'status:ready'])
        self.assertEqual(self.plan(subject, newest='status:ready'), (set(), {'status:in-progress'}))

    def test_without_history_in_progress_beats_ready(self):
        self.assertEqual(self.plan(issue(1, ['status:ready', 'status:in-progress'])),
                         (set(), {'status:ready'}))

    def test_without_history_blocked_beats_ready(self):
        self.assertEqual(self.plan(issue(2, ['status:ready', 'status:blocked'])),
                         (set(), {'status:ready'}))

    def test_non_status_labels_are_never_touched(self):
        self.assertEqual(self.plan(issue(3, ['project:sentinel', 'claude:scheduled'])), (set(), set()))

    def test_blocked_issue_becomes_ready_when_all_dependencies_completed(self):
        subject = issue(2, ['status:blocked'], BLOCKED_BY_1)
        self.assertEqual(self.plan(subject, {1: True}), ({'status:ready'}, {'status:blocked'}))

    def test_blocked_issue_stays_blocked_while_a_dependency_is_open(self):
        subject = issue(2, ['status:blocked'], '## Dependencies\nBlocked by #1, #5\n')
        self.assertEqual(self.plan(subject, {1: True, 5: False}), (set(), set()))

    def test_dependency_closed_not_planned_does_not_unblock(self):
        subject = issue(2, ['status:blocked'], BLOCKED_BY_1)
        self.assertEqual(self.plan(subject, {1: False}), (set(), set()))

    def test_block_without_dependencies_is_left_alone(self):
        self.assertEqual(self.plan(issue(2, ['status:blocked'], 'Waiting on a decision.')), (set(), set()))

    def test_ready_issue_with_open_dependency_is_blocked(self):
        subject = issue(2, ['status:ready'], BLOCKED_BY_1)
        self.assertEqual(self.plan(subject, {1: False}), ({'status:blocked'}, {'status:ready'}))

    def test_in_progress_issue_is_not_reblocked(self):
        subject = issue(2, ['status:in-progress'], BLOCKED_BY_1)
        self.assertEqual(self.plan(subject, {1: False}), (set(), set()))

    def test_self_reference_is_not_a_dependency(self):
        subject = issue(2, ['status:blocked'], '## Dependencies\nBlocked by #2 and #1\n')
        self.assertEqual(self.plan(subject, {1: True}), ({'status:ready'}, {'status:blocked'}))

    def test_closed_issue_drops_every_status_label(self):
        subject = issue(1, ['claude:scheduled', 'status:in-progress', 'status:ready'],
                        state='closed', state_reason='completed')
        self.assertEqual(self.plan(subject), (set(), {'status:in-progress', 'status:ready'}))

    # An issue must never be left without a status label by a plan.
    def test_newest_blocked_with_completed_dependencies_becomes_ready_not_empty(self):
        subject = issue(2, ['claude:scheduled', 'status:ready', 'status:blocked'], BLOCKED_BY_1)
        add, remove = self.plan(subject, {1: True}, newest='status:blocked')
        self.assertEqual((add, remove), (set(), {'status:blocked'}))

    def test_newest_ready_with_open_dependency_becomes_blocked_not_empty(self):
        subject = issue(2, ['status:blocked', 'status:ready'], BLOCKED_BY_1)
        add, remove = self.plan(subject, {1: False}, newest='status:ready')
        self.assertEqual((add, remove), (set(), {'status:ready'}))

    def test_plan_never_adds_and_removes_the_same_label(self):
        for labels in (['status:blocked', 'status:ready'], ['status:ready'], ['status:blocked']):
            for done in (True, False):
                for newest in (None, 'status:blocked', 'status:ready'):
                    with self.subTest(labels=labels, done=done, newest=newest):
                        add, remove = self.plan(issue(2, labels, BLOCKED_BY_1), {1: done}, newest)
                        self.assertFalse(add & remove)
                        final = (set(labels) | add) - remove
                        self.assertEqual(len(final & self.flow.STATUS), 1)

    # status:hold is an executor flag: the reconciler keeps it and the underlying
    # status follows the normal rules, so lifting the hold restores the issue.
    def test_hold_is_kept_and_the_underlying_status_is_untouched(self):
        subject = issue(2, ['status:hold', 'status:ready'], BLOCKED_BY_1)
        self.assertEqual(self.plan(subject, {1: True}), (set(), set()))

    def test_hold_does_not_stop_normal_unblocking(self):
        subject = issue(2, ['status:hold', 'status:blocked'], BLOCKED_BY_1)
        self.assertEqual(self.plan(subject, {1: True}), ({'status:ready'}, {'status:blocked'}))

    def test_closed_issue_drops_hold_too(self):
        subject = issue(2, ['status:hold'], state='closed', state_reason='completed')
        self.assertEqual(self.plan(subject), (set(), {'status:hold'}))


class ReconcileTests(unittest.TestCase):
    def setUp(self):
        self.flow = load()

    def gh(self, *issues, **kwargs):
        return FakeGitHub(self.flow, *issues, **kwargs)

    def test_closing_a_dependency_unblocks_its_dependents(self):
        gh = self.gh(
            issue(1, ['claude:scheduled', 'status:in-progress'], state='closed', state_reason='completed'),
            issue(2, ['claude:scheduled', 'status:blocked'], BLOCKED_BY_1),
            issue(3, ['claude:scheduled', 'status:blocked'], BLOCKED_BY_1),
            issue(6, ['type:tracking'], '## Initial wave\n- [ ] #1\n'),
        )
        self.flow.reconcile('issues', {'action': 'closed', 'issue': {'number': 1}}, gh)
        self.assertEqual(gh.labels(1), ['claude:scheduled'])
        self.assertEqual(gh.labels(2), ['claude:scheduled', 'status:ready'])
        self.assertEqual(gh.labels(3), ['claude:scheduled', 'status:ready'])
        self.assertEqual(gh.labels(6), ['type:tracking'])

    def test_lock_release_follows_label_history_not_the_event(self):
        gh = self.gh(issue(1, ['status:in-progress']))
        gh.add_labels(1, ['status:ready'])  # host releases the lock
        gh.calls.clear()
        # A superseding run carries no label payload at all.
        self.flow.reconcile('issues', {'action': 'edited', 'issue': {'number': 1}}, gh)
        self.assertEqual(gh.labels(1), ['status:ready'])

    def test_reclaim_after_release_keeps_the_claim(self):
        gh = self.gh(issue(1, ['status:in-progress']))
        gh.add_labels(1, ['status:ready'])
        gh.add_labels(1, ['status:in-progress'])  # re-claimed before reconciling
        # A late run for the release event must not undo the newer claim.
        event = {'action': 'labeled', 'issue': {'number': 1}, 'label': {'name': 'status:ready'}}
        self.flow.reconcile('issues', event, gh)
        self.assertEqual(gh.labels(1), ['status:in-progress'])

    def test_executor_back_off_by_re_adding_ready_leaves_the_issue_ready(self):
        gh = self.gh(issue(1, ['claude:scheduled', 'status:ready']))
        gh.add_labels(1, ['status:in-progress'])          # claim
        self.flow.reconcile('schedule', {}, gh)             # issue flow removes ready
        gh.add_labels(1, ['status:ready'])                  # back-off step
        self.flow.reconcile('schedule', {}, gh)
        self.assertEqual(gh.labels(1), ['claude:scheduled', 'status:ready'])

    def test_lifting_a_hold_leaves_the_issue_ready(self):
        gh = self.gh(issue(1, ['claude:scheduled', 'status:in-progress']))
        gh.add_labels(1, ['status:ready', 'status:hold'])   # abandon: retry later, held
        self.flow.reconcile('schedule', {}, gh)
        gh.remove_label(1, 'status:hold')                   # host lifts the hold
        self.flow.reconcile('schedule', {}, gh)
        self.assertEqual(gh.labels(1), ['claude:scheduled', 'status:ready'])

    def test_foreign_dependency_keeps_the_issue_blocked(self):
        gh = self.gh(issue(2, ['status:blocked'], '## Dependencies\n- other/repo#9\n'))
        self.flow.reconcile('schedule', {}, gh)
        self.assertEqual(gh.labels(2), ['status:blocked'])
        self.assertEqual(gh.calls, [])

    def test_sweep_cleans_closed_issues_that_still_carry_status_labels(self):
        gh = self.gh(issue(4, ['claude:scheduled', 'status:in-progress'],
                           state='closed', state_reason='completed'),
                     issue(5, ['type:tracking'], state='closed', state_reason='completed'))
        self.flow.reconcile('schedule', {}, gh)
        self.assertEqual(gh.labels(4), ['claude:scheduled'])
        self.assertEqual(gh.labels(5), ['type:tracking'])

    def test_write_is_skipped_when_labels_changed_after_planning(self):
        gh = self.gh(issue(1, ['claude:scheduled', 'status:ready']))
        gh.add_labels(1, ['status:in-progress'])          # claim; plan will drop ready
        gh.calls.clear()
        original = gh.issue

        def issue_then_back_off(number):
            if number == 1 and 'status:in-progress' in gh.issues[1]['labels']:
                gh.issues[1]['labels'].remove('status:in-progress')   # executor backs off
            return original(number)

        gh.issue = issue_then_back_off
        self.flow.reconcile('schedule', {}, gh)
        self.assertEqual(gh.labels(1), ['claude:scheduled', 'status:ready'])
        self.assertEqual(gh.calls, [])

    def test_write_is_skipped_when_the_issue_closed_after_planning(self):
        gh = self.gh(issue(1, [], state='closed', state_reason='completed'),
                     issue(2, ['status:blocked'], BLOCKED_BY_1))
        original = gh.issue

        def issue_then_close(number):
            if number == 2:
                gh.issues[2]['state'] = 'closed'      # closed between planning and writing
            return original(number)

        gh.issue = issue_then_close
        self.flow.reconcile('schedule', {}, gh)
        self.assertEqual(gh.labels(2), ['status:blocked'])
        self.assertEqual(gh.calls, [])

    def test_closed_issues_need_no_dependency_or_history_lookups(self):
        gh = self.gh(issue(9, ['status:ready', 'status:blocked'], '## Dependencies\n- #77\n',
                           state='closed', state_reason='completed'),
                     errors={77: RuntimeError('gh api failed: HTTP 502')})
        gh.latest_added = lambda *_: self.fail('history looked up for a closed issue')
        self.flow.reconcile('schedule', {}, gh)
        self.assertEqual(gh.labels(9), [])

    def test_sweep_repairs_every_open_issue(self):
        gh = self.gh(issue(1, ['status:ready', 'status:in-progress']),
                     issue(2, ['status:ready'], BLOCKED_BY_1))
        self.flow.reconcile('workflow_dispatch', {}, gh)
        self.assertEqual(gh.labels(1), ['status:in-progress'])
        self.assertEqual(gh.labels(2), ['status:blocked'])

    def test_consistent_state_makes_no_calls(self):
        gh = self.gh(issue(1, ['status:in-progress']), issue(2, ['status:blocked'], BLOCKED_BY_1))
        self.flow.reconcile('schedule', {}, gh)
        self.assertEqual(gh.calls, [])

    def test_pull_request_items_are_ignored(self):
        gh = self.gh(issue(9, ['status:ready', 'status:blocked']))
        gh.issues[9]['pull_request'] = True
        self.flow.reconcile('schedule', {}, gh)
        self.assertEqual(gh.calls, [])

    def test_adds_are_applied_before_removals(self):
        gh = self.gh(issue(1, [], state='closed', state_reason='completed'),
                     issue(2, ['status:blocked'], BLOCKED_BY_1))
        self.flow.reconcile('schedule', {}, gh)
        self.assertEqual(gh.calls, [('add', 2, ('status:ready',)), ('remove', 2, 'status:blocked')])

    def test_missing_dependency_counts_as_unsatisfied(self):
        gh = self.gh(issue(2, ['status:blocked'], '## Dependencies\nBlocked by #404\n'))
        self.flow.reconcile('schedule', {}, gh)
        self.assertEqual(gh.labels(2), ['status:blocked'])

    def test_lookup_failure_aborts_without_any_write(self):
        gh = self.gh(issue(2, ['status:ready'], BLOCKED_BY_1),
                     issue(3, ['status:ready', 'status:in-progress']),
                     errors={1: RuntimeError('gh api failed: HTTP 502')})
        with self.assertRaises(RuntimeError):
            self.flow.reconcile('schedule', {}, gh)
        self.assertEqual(gh.calls, [])

    def test_a_failed_write_does_not_stop_other_issues_and_is_raised(self):
        gh = self.gh(issue(2, ['status:ready', 'status:in-progress']),
                     issue(3, ['status:ready', 'status:in-progress']))

        def remove_label(number, label):
            gh.calls.append(('remove', number, label))
            if number == 2:
                raise RuntimeError('gh api failed: HTTP 403')
            gh.issues[number]['labels'].remove(label)

        gh.remove_label = remove_label
        with self.assertRaisesRegex(RuntimeError, '#2'):
            self.flow.reconcile('schedule', {}, gh)
        self.assertEqual(gh.labels(3), ['status:in-progress'])

    def test_merged_pull_request_dependency_counts_as_completed(self):
        gh = self.gh(issue(21, [], state='closed'),
                     issue(2, ['status:blocked'], '## Dependencies\nBlocked by #21\n'))
        gh.issues[21]['pull_request'] = True
        gh.issues[21]['merged'] = True
        self.flow.reconcile('schedule', {}, gh)
        self.assertEqual(gh.labels(2), ['status:ready'])


class GitHubClientTests(unittest.TestCase):
    def setUp(self):
        self.flow = load()

    @staticmethod
    def result(code=0, out='', err=''):
        class Result:
            returncode, stdout, stderr = code, out, err
        return Result()

    def client(self, *results):
        seen = []
        queue = list(results)

        def run(args, **_):
            seen.append(args)
            return queue.pop(0) if queue else self.result()

        return self.flow.GitHub('owner/repo', run=run), seen

    def test_label_names_are_url_encoded_on_removal(self):
        client, seen = self.client()
        client.remove_label(4, 'status:in-progress')
        self.assertIn('repos/owner/repo/issues/4/labels/status%3Ain-progress', seen[0])

    def test_removing_an_absent_label_is_not_an_error(self):
        client, _ = self.client(self.result(1, err='gh: Label does not exist (HTTP 404)'))
        client.remove_label(4, 'status:ready')

    def test_other_api_failures_raise(self):
        client, _ = self.client(self.result(1, err='gh: Forbidden (HTTP 403)'))
        with self.assertRaises(RuntimeError):
            client.remove_label(4, 'status:ready')

    def test_missing_issue_raises_not_found(self):
        client, _ = self.client(self.result(1, err='gh: Not Found (HTTP 404)'))
        with self.assertRaises(self.flow.NotFound):
            client.issue(404)

    def test_add_labels_sends_each_label_as_an_array_field(self):
        client, seen = self.client()
        client.add_labels(4, ['status:ready', 'status:blocked'])
        self.assertEqual(seen[0][-4:], ['-f', 'labels[]=status:ready', '-f', 'labels[]=status:blocked'])

    def test_closed_with_status_queries_each_status_label_once_per_issue(self):
        raw = json.dumps({'number': 4, 'state': 'closed', 'state_reason': 'completed',
                          'body': '', 'labels': [{'name': 'status:ready'}, {'name': 'status:hold'}]})
        results = [self.result(0, out=raw + '\n') if i in (0, 3) else self.result()
                   for i in range(4)]
        client, seen = self.client(*results)
        found = client.closed_with_status()
        self.assertEqual([i['number'] for i in found], [4])
        self.assertEqual(len(seen), 4)
        self.assertTrue(all('state=closed' in ' '.join(args) for args in seen))

    def test_open_issues_parses_paginated_lines_and_marks_pull_requests(self):
        lines = '\n'.join([
            json.dumps({'number': 2, 'state': 'open', 'body': None, 'labels': [{'name': 'status:blocked'}]}),
            json.dumps({'number': 21, 'state': 'open', 'body': 'x', 'labels': [],
                        'pull_request': {'merged_at': None}}),
        ])
        client, seen = self.client(self.result(0, out=lines + '\n'))
        found = client.open_issues()
        self.assertIn('--paginate', seen[0])
        self.assertEqual([i['number'] for i in found], [2, 21])
        self.assertEqual(found[0]['labels'], ['status:blocked'])
        self.assertEqual(found[0]['body'], '')
        self.assertTrue(found[1]['pull_request'])

    def test_merged_pull_request_is_shaped_as_merged(self):
        raw = {'number': 21, 'state': 'closed', 'state_reason': None, 'body': '', 'labels': [],
               'pull_request': {'merged_at': '2026-11-07T09:52:36Z'}}
        client, _ = self.client(self.result(0, out=json.dumps(raw)))
        self.assertTrue(client.issue(21)['merged'])

    def test_latest_added_ignores_labels_added_by_the_workflow_itself(self):
        events = '\n'.join(json.dumps(e) for e in [
            {'event': 'labeled', 'label': {'name': 'status:in-progress'}, 'actor': {'login': '46tsoh'}},
            {'event': 'labeled', 'label': {'name': 'status:blocked'},
             'actor': {'login': 'github-actions[bot]'}},
        ])
        client, _ = self.client(self.result(0, out=events + '\n'))
        self.assertEqual(client.latest_added(1, {'status:in-progress', 'status:blocked'}),
                         'status:in-progress')

    def test_latest_added_reads_label_history(self):
        events = '\n'.join(json.dumps(e) for e in [
            {'event': 'labeled', 'label': {'name': 'status:in-progress'}},
            {'event': 'labeled', 'label': {'name': 'status:ready'}},
            {'event': 'unlabeled', 'label': {'name': 'status:ready'}},
            {'event': 'labeled', 'label': {'name': 'project:sentinel'}},
        ])
        client, seen = self.client(self.result(0, out=events + '\n'))
        newest = client.latest_added(1, {'status:in-progress', 'status:ready'})
        self.assertEqual(newest, 'status:ready')
        self.assertIn('repos/owner/repo/issues/1/events?per_page=100', seen[0])


if __name__ == '__main__':
    unittest.main()
