"""Fail-closed review contract tests; fixtures are not live model evidence."""
import copy
import importlib.util
from pathlib import Path
from typing import Any
import unittest

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / 'tools' / 'claude_review.py'


class ReviewContractTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(MODULE.is_file(), 'deterministic review validator is not implemented')
        spec = importlib.util.spec_from_file_location('claude_review', MODULE)
        assert spec is not None and spec.loader is not None
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)
        self.expected: dict[str, Any] = dict(repository_id=1448718197, pr=8,
            head_sha='a'*40, base_sha='b'*40, policy_sha='c'*40,
            nonce='d'*64, input_sha256='e'*64, risk_ceiling='low',
            files=['docs/code-review.md', '.coderabbit.yaml'])
        self.current = copy.deepcopy(self.expected)
        self.verdict = {k:v for k,v in self.expected.items() if k not in ('files', 'risk_ceiling')}
        self.verdict.update(decision='approve', complete=True, findings=[],
            reviewed_files=['.coderabbit.yaml', 'docs/code-review.md'],
            risk='low', risk_ceiling='low',
            summary='No blocking defects identified in the supplied complete change.')

    def check(self):
        return self.mod.validate_review(self.verdict, self.expected, self.current)

    def test_risk_ceiling_low_for_small_doc_only_diff(self):
        self.assertEqual(self.mod.compute_risk_ceiling(['docs/code-review.md'], 2, 0), 'low')

    def test_risk_ceiling_medium_for_source_code_change(self):
        self.assertEqual(self.mod.compute_risk_ceiling(['tools/widget.py'], 12, 4), 'medium')

    def test_risk_ceiling_high_for_workflow_or_sensitive_paths(self):
        for path in ('.github/workflows/anything.yml', '.claude/settings.json',
                      'tools/claude_review.py', 'AGENTS.md'):
            with self.subTest(path=path):
                self.assertEqual(self.mod.compute_risk_ceiling([path], 1, 0), 'high')

    def test_risk_ceiling_high_for_large_diff_regardless_of_path(self):
        self.assertEqual(self.mod.compute_risk_ceiling(['docs/a.md'], 300, 150), 'high')

    def test_risk_ceiling_medium_for_moderate_diff(self):
        self.assertEqual(self.mod.compute_risk_ceiling(['docs/a.md'], 60, 10), 'medium')

    def test_risk_ceiling_is_max_across_all_files(self):
        self.assertEqual(self.mod.compute_risk_ceiling(['docs/a.md', 'tools/x.py'], 3, 0), 'medium')
        self.assertEqual(self.mod.compute_risk_ceiling(['docs/a.md', '.github/workflows/x.yml'], 1, 0), 'high')

    def test_paginated_gh_output_conserves_every_page(self):
        self.assertEqual(self.mod.decode_pages('[{"id":1}]\n[{"id":2}]\n'), [[{'id':1}], [{'id':2}]])
        with self.assertRaises(ValueError): self.mod.decode_pages('[1]\nNOT_JSON')
        with self.assertRaises(ValueError): self.mod.decode_pages('{"id":1}')

    def test_valid_clean_current_review_accepts(self):
        self.assertEqual(self.check()['summary'], self.verdict['summary'])

    def test_reject_verdict_blocks(self):
        self.verdict['decision'] = 'reject'
        with self.assertRaises(ValueError): self.check()

    def test_blocked_verdict_blocks(self):
        self.verdict['decision'] = 'blocked'
        with self.assertRaises(ValueError): self.check()

    def test_any_finding_blocks_even_if_decision_claims_approve(self):
        self.verdict['findings'] = [{'severity':'important','path':'x','message':'defect'}]
        with self.assertRaises(ValueError): self.check()

    def test_incomplete_review_blocks(self):
        self.verdict['complete'] = False
        with self.assertRaises(ValueError): self.check()

    def test_truthy_string_is_not_complete(self):
        self.verdict['complete'] = 'true'
        with self.assertRaises(ValueError): self.check()

    def test_unknown_fields_block(self):
        self.verdict['override'] = True
        with self.assertRaises(ValueError): self.check()

    def test_missing_field_blocks(self):
        del self.verdict['nonce']
        with self.assertRaises(ValueError): self.check()

    def test_each_wrong_identity_blocks(self):
        for name in ('repository_id','pr','head_sha','base_sha','policy_sha','nonce','input_sha256'):
            with self.subTest(name=name):
                candidate=copy.deepcopy(self.verdict)
                candidate[name] = 9 if isinstance(candidate[name],int) else 'f'*len(candidate[name])
                with self.assertRaises(ValueError):
                    self.mod.validate_review(candidate,self.expected,self.current)

    def test_head_base_policy_or_pr_change_blocks(self):
        for name in ('repository_id','pr','head_sha','base_sha','policy_sha','nonce','input_sha256','files'):
            with self.subTest(name=name):
                now=copy.deepcopy(self.current)
                now[name] = [] if name=='files' else 9 if isinstance(now[name],int) else 'f'*len(now[name])
                with self.assertRaises(ValueError): self.mod.validate_review(self.verdict,self.expected,now)

    def test_missing_or_extra_reviewed_file_blocks(self):
        for files in ([], ['docs/code-review.md'], ['docs/code-review.md','.coderabbit.yaml','other']):
            self.verdict['reviewed_files']=files
            with self.assertRaises(ValueError): self.check()

    def test_duplicate_coverage_blocks(self):
        self.verdict['reviewed_files']=['docs/code-review.md','.coderabbit.yaml','.coderabbit.yaml']
        with self.assertRaises(ValueError): self.check()

    def test_boolean_repository_identity_blocks(self):
        self.verdict['repository_id']=True
        with self.assertRaises(ValueError): self.check()

    def test_empty_or_oversized_summary_blocks(self):
        for summary in ('', ' ', 'x'*2001):
            self.verdict['summary']=summary
            with self.assertRaises(ValueError): self.check()

    def test_nonobject_result_blocks(self):
        for bad in (None, [], 'approve', True):
            with self.assertRaises(ValueError): self.mod.validate_review(bad,self.expected,self.current)

    def test_no_changed_files_cannot_obtain_approval(self):
        self.expected['files']=[]; self.current['files']=[]; self.verdict['reviewed_files']=[]
        with self.assertRaises(ValueError): self.check()

    def test_low_risk_clean_approve_is_merge_eligible(self):
        outcome = self.check()
        self.assertTrue(outcome['merge_eligible'])
        self.assertEqual(outcome['risk'], 'low')
        self.assertEqual(outcome['summary'], self.verdict['summary'])

    def test_medium_or_high_ceiling_blocks_merge_eligibility_even_if_clean(self):
        for ceiling in ('medium', 'high'):
            with self.subTest(ceiling=ceiling):
                self.expected['risk_ceiling'] = ceiling
                self.current['risk_ceiling'] = ceiling
                self.verdict['risk_ceiling'] = ceiling
                self.verdict['risk'] = ceiling
                outcome = self.check()
                self.assertFalse(outcome['merge_eligible'])
                self.assertEqual(outcome['risk'], ceiling)

    def test_model_cannot_self_report_below_the_deterministic_ceiling(self):
        self.verdict['risk_ceiling'] = 'high'
        self.verdict['risk'] = 'low'
        with self.assertRaises(ValueError): self.check()

    def test_unknown_risk_value_blocks(self):
        self.verdict['risk'] = 'none'
        with self.assertRaises(ValueError): self.check()

    def test_risk_ceiling_identity_mismatch_blocks(self):
        self.verdict['risk_ceiling'] = 'medium'
        with self.assertRaises(ValueError): self.check()


if __name__ == '__main__': unittest.main()
