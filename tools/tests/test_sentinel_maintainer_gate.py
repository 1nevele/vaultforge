"""Synthetic fixtures for the PR-only merge/notification gate."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'sentinel_maintainer_gate.py'

class MaintainerGateTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('maintainer_gate', SCRIPT)
        assert spec is not None and spec.loader is not None
        self.gate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.gate)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.state = Path(self.temp.name) / 'gate.json'

    def poll(self, snapshot):
        return self.gate.poll(self.state, lambda: snapshot)

    def test_issue_activity_without_pr_never_wakes(self):
        snapshot = {'prs': {}, 'issues': {'7': {'updated_at': 'new'}}}
        self.assertFalse(self.poll(snapshot)['wakeAgent'])
        snapshot['issues']['7']['updated_at'] = 'changed'
        self.assertFalse(self.poll(snapshot)['wakeAgent'])

    def test_empty_queue_does_not_fetch_issues(self):
        paths = []
        def api(path, query):
            paths.append(path)
            return []
        self.assertEqual(self.gate.fetch_snapshot(api), {'prs': {}})
        self.assertEqual(paths, ['pulls?state=open&per_page=100'])

    def test_unacknowledged_work_is_retried(self):
        snapshot = {'prs': {'20': {'head': 'a'}}}
        first = self.poll(snapshot)
        self.assertEqual(first, self.poll(snapshot))

    def test_unchanged_blocker_sleeps_but_revision_wakes(self):
        snapshot = {'prs': {'20': {'head': 'a', 'checks': ['failed']}}}
        event = self.poll(snapshot)
        self.gate.acknowledge(self.state, event['event_id'])
        self.assertFalse(self.poll(snapshot)['wakeAgent'])
        snapshot['prs']['20']['head'] = 'b'
        self.assertTrue(self.poll(snapshot)['wakeAgent'])

    def test_ci_completion_wakes_without_new_commit(self):
        snapshot = {'prs': {'20': {'head': 'a', 'checks': ['pending']}}}
        event = self.poll(snapshot)
        self.gate.acknowledge(self.state, event['event_id'])
        snapshot['prs']['20']['checks'] = ['success']
        self.assertTrue(self.poll(snapshot)['wakeAgent'])

    def test_issue_only_change_ignored_with_open_pr(self):
        snapshot = {'prs': {'20': {'head': 'a'}}, 'issues': {'7': 'before'}}
        event = self.poll(snapshot)
        self.gate.acknowledge(self.state, event['event_id'])
        snapshot['issues']['7'] = 'after'
        self.assertFalse(self.poll(snapshot)['wakeAgent'])

    def test_ack_does_not_swallow_later_pr_activity(self):
        first = self.poll({'prs': {'20': {'head': 'a'}}})
        self.gate.acknowledge(self.state, first['event_id'])
        self.assertTrue(self.poll({'prs': {'20': {'head': 'b'}}})['wakeAgent'])

    def test_stale_ack_is_rejected(self):
        first = self.poll({'prs': {'20': {'head': 'a'}}})
        self.poll({'prs': {'20': {'head': 'b'}}})
        with self.assertRaises(ValueError):
            self.gate.acknowledge(self.state, first['event_id'])

    def test_fetch_failure_sleeps_without_consuming_pending(self):
        self.poll({'prs': {'20': {'head': 'a'}}})
        previous = self.state.read_text()
        def fail():
            raise RuntimeError('synthetic failure')
        self.assertFalse(self.gate.poll(self.state, fail)['wakeAgent'])
        self.assertEqual(previous, self.state.read_text())

    def test_closed_last_pr_triggers_one_notification_reconciliation(self):
        event = self.poll({'prs': {'20': {'head': 'a'}}})
        self.gate.acknowledge(self.state, event['event_id'])
        closed = self.poll({'prs': {}})
        self.assertTrue(closed['wakeAgent'])
        self.gate.acknowledge(self.state, closed['event_id'])
        self.assertFalse(self.poll({'prs': {}})['wakeAgent'])

    def test_snapshot_has_review_checks_and_pr_comments_not_own_feedback(self):
        def api(path, query):
            if path.startswith('pulls?'):
                return [{'number': 20, 'head': 'abc', 'base': 'def', 'draft': False}]
            if '/reviews?' in path:
                return [{'id': 1, 'user': 'coderabbitai[bot]', 'state': 'CHANGES_REQUESTED'},
                        {'id': 2, 'user': '1nevele', 'state': 'COMMENTED'}]
            if '/check-runs?' in path:
                return [{'id': 3, 'name': 'test', 'conclusion': 'success'}]
            if '/comments?' in path:
                return [{'id': 4, 'user': 'host'}, {'id': 5, 'user': '1nevele'}]
            return []
        pr = self.gate.fetch_snapshot(api)['prs']['20']
        self.assertEqual(len(pr['reviews']), 1)
        self.assertEqual(len(pr['comments']), 1)
        self.assertEqual(len(pr['inline_comments']), 1)
        self.assertEqual(pr['checks'][0]['id'], 3)

if __name__ == '__main__':
    unittest.main()
