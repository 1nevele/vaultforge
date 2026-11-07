"""Fail-closed tests for the deterministic PR risk gate (blocks high-risk diffs)."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / 'tools' / 'risk_gate.py'


class RiskGateTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(MODULE.is_file(), 'risk gate module is not implemented')
        spec = importlib.util.spec_from_file_location('risk_gate', MODULE)
        assert spec is not None and spec.loader is not None
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)

    def test_low_for_small_doc_only_diff(self):
        self.assertEqual(self.mod.compute_risk(['docs/a.md'], 2, 0), 'low')

    def test_medium_for_source_code_change(self):
        self.assertEqual(self.mod.compute_risk(['tools/widget.py'], 12, 4), 'medium')

    def test_high_for_sensitive_paths(self):
        for path in ('.github/workflows/anything.yml', '.claude/settings.json',
                      '.coderabbit.yaml', 'CODEOWNERS', '.github/CODEOWNERS',
                      'AGENTS.md', 'tools/risk_gate.py', 'tools/tests/test_risk_gate.py'):
            with self.subTest(path=path):
                self.assertEqual(self.mod.compute_risk([path], 1, 0), 'high')

    def test_high_for_large_diff_regardless_of_path(self):
        self.assertEqual(self.mod.compute_risk(['docs/a.md'], 300, 150), 'high')

    def test_medium_for_moderate_diff(self):
        self.assertEqual(self.mod.compute_risk(['docs/a.md'], 60, 10), 'medium')

    def test_risk_is_max_across_all_files(self):
        self.assertEqual(self.mod.compute_risk(['docs/a.md', 'tools/x.py'], 3, 0), 'medium')
        self.assertEqual(self.mod.compute_risk(['docs/a.md', '.github/workflows/x.yml'], 1, 0), 'high')

    def test_decide_blocks_only_on_high(self):
        self.assertEqual(self.mod.decide('low'), 0)
        self.assertEqual(self.mod.decide('medium'), 0)
        self.assertEqual(self.mod.decide('high'), 1)

    def test_empty_file_list_is_low(self):
        self.assertEqual(self.mod.compute_risk([], 0, 0), 'low')


if __name__ == '__main__':
    unittest.main()
