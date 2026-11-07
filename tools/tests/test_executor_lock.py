"""Executor claim lock against a throwaway bare remote (specs/002 CA-003)."""
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'executor_lock.py'
IDENTITY = {'GIT_AUTHOR_NAME': 't', 'GIT_AUTHOR_EMAIL': 't@example.invalid',
            'GIT_COMMITTER_NAME': 't', 'GIT_COMMITTER_EMAIL': 't@example.invalid'}


def load():
    spec = importlib.util.spec_from_file_location('executor_lock', SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(cwd, *args, env=None):
    return subprocess.run(['git', *args], cwd=cwd, check=True, capture_output=True,
                          text=True, env={**os.environ, **IDENTITY, **(env or {})}).stdout.strip()


class ExecutorLockTests(unittest.TestCase):
    def setUp(self):
        self.lock = load()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.remote = root / 'remote.git'
        git(root, 'init', '-q', '--bare', str(self.remote))
        self.a, self.b = root / 'a', root / 'b'
        for clone in (self.a, self.b):
            git(root, 'clone', '-q', str(self.remote), str(clone))

    def tip_message(self):
        return git(self.a, 'log', '-1', '--format=%s', 'FETCH_HEAD') if self.fetch() else None

    def fetch(self):
        try:
            git(self.a, 'fetch', '-q', 'origin', f'refs/heads/{self.lock.BRANCH}')
            return True
        except subprocess.CalledProcessError:
            return False

    def test_first_acquire_bootstraps_the_branch_and_holds_it(self):
        token = self.lock.acquire(self.a)
        self.assertRegex(token, r'^[0-9a-f]{32}$')
        self.assertEqual(self.tip_message(), f'held {token}')

    def test_second_acquire_is_refused_while_held(self):
        self.lock.acquire(self.a)
        self.assertIsNone(self.lock.acquire(self.b))

    def test_release_then_another_run_can_acquire(self):
        token = self.lock.acquire(self.a)
        self.assertTrue(self.lock.release(self.a, token))
        self.assertEqual(self.tip_message(), f'free {token}')
        self.assertIsNotNone(self.lock.acquire(self.b))

    def test_release_with_a_foreign_token_changes_nothing(self):
        token = self.lock.acquire(self.a)
        self.assertFalse(self.lock.release(self.b, '0' * 32))
        self.assertEqual(self.tip_message(), f'held {token}')

    def test_check_reports_whether_the_token_still_holds(self):
        token = self.lock.acquire(self.a)
        self.assertTrue(self.lock.check(self.b, token))
        self.assertFalse(self.lock.check(self.b, '0' * 32))

    def test_stale_lock_is_broken_and_the_old_holder_learns_it_lost(self):
        old = '@1000000000 +0000'
        token_a = self.lock.acquire(self.a, env={'GIT_COMMITTER_DATE': old})
        token_b = self.lock.acquire(self.b)
        self.assertIsNotNone(token_b)
        self.assertNotEqual(token_a, token_b)
        self.assertFalse(self.lock.check(self.a, token_a))
        self.assertFalse(self.lock.release(self.a, token_a))
        self.assertEqual(self.tip_message(), f'held {token_b}')

    def test_fresh_lock_is_not_broken(self):
        token = self.lock.acquire(self.a)
        self.assertIsNone(self.lock.acquire(self.b, stale_minutes=30))
        self.assertTrue(self.lock.check(self.a, token))

    def test_claim_from_an_outdated_tip_is_rejected(self):
        # A read the tip, then B acquired: A's push of a child of the old tip loses.
        self.lock.release(self.a, self.lock.acquire(self.a))
        old_tip = self.lock.fetch_tip(self.a)
        token_b = self.lock.acquire(self.b)
        self.assertIsNotNone(token_b)
        self.assertIsNone(self.lock.try_claim(self.a, old_tip))
        self.assertEqual(self.tip_message(), f'held {token_b}')

    def test_bootstrap_race_has_one_winner(self):
        # Both runs saw no lock branch; the second creation is not a fast-forward.
        self.assertIsNone(self.lock.fetch_tip(self.b))
        token_a = self.lock.acquire(self.a)
        self.assertIsNone(self.lock.try_claim(self.b, None))
        self.assertEqual(self.tip_message(), f'held {token_a}')

    def test_unrecognised_tip_counts_as_held_until_stale(self):
        git(self.a, 'commit', '-q', '--allow-empty', '-m', 'someone else')
        git(self.a, 'push', '-q', 'origin', f'HEAD:refs/heads/{self.lock.BRANCH}')
        self.assertIsNone(self.lock.acquire(self.b))
        self.assertIsNone(self.lock.current_token(self.b))
        self.assertIsNotNone(self.lock.acquire(self.b, stale_minutes=0))

    def test_git_failures_raise_instead_of_reading_as_held(self):
        git(self.a, 'remote', 'set-url', 'origin', str(Path(self.tmp.name) / 'missing.git'))
        with self.assertRaises(self.lock.LockError):
            self.lock.acquire(self.a)

    def test_policy_rejection_raises_instead_of_reading_as_held(self):
        # A pre-receive hook stands in for a ruleset or proxy refusing the push.
        hook = self.remote / 'hooks' / 'pre-receive'
        hook.write_text('#!/bin/sh\necho denied >&2\nexit 1\n')
        hook.chmod(0o755)
        with self.assertRaises(self.lock.LockError):
            self.lock.acquire(self.a)

    def test_reset_frees_a_held_lock_and_its_holder_learns_it_lost(self):
        token = self.lock.acquire(self.a)
        self.assertTrue(self.lock.reset(self.b))
        self.assertEqual(self.tip_message(), f'free {token}')
        self.assertFalse(self.lock.check(self.a, token))
        self.assertTrue(self.lock.reset(self.b))  # already free: nothing to do
        self.assertIsNotNone(self.lock.acquire(self.b))

    def test_lock_commits_carry_no_files(self):
        self.lock.acquire(self.a)
        self.fetch()
        self.assertEqual(git(self.a, 'ls-tree', 'FETCH_HEAD'), '')

    def test_cli_exit_codes(self):
        run = lambda *args: subprocess.run(['python3', '-B', str(SCRIPT), *args], cwd=self.a,
                                           capture_output=True, text=True,
                                           env={**os.environ, **IDENTITY})
        acquired = run('acquire')
        self.assertEqual(acquired.returncode, 0)
        token = acquired.stdout.strip()
        self.assertEqual(run('acquire').returncode, 3)
        self.assertEqual(run('check', token).returncode, 0)
        self.assertEqual(run('release', token).returncode, 0)
        self.assertEqual(run('check', token).returncode, 3)
        self.assertEqual(run('bogus').returncode, 2)
        self.assertEqual(run('acquire', '--stale-minutes', '-1').returncode, 2)
        self.assertEqual(run('acquire', '--stale-minutes', 'x').returncode, 2)
        self.assertEqual(run('acquire').returncode, 0)
        self.assertEqual(run('reset').returncode, 0)
        git(self.a, 'remote', 'set-url', 'origin', str(Path(self.tmp.name) / 'missing.git'))
        failed = run('acquire')
        self.assertEqual(failed.returncode, 1)
        self.assertIn('executor_lock:', failed.stderr)


if __name__ == '__main__':
    unittest.main()
