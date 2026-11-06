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
            nonce='d'*64, input_sha256='e'*64,
            files=['docs/code-review.md', '.coderabbit.yaml'])
        self.current = copy.deepcopy(self.expected)
        self.verdict = {k:v for k,v in self.expected.items() if k != 'files'}
        self.verdict.update(decision='approve', complete=True, findings=[],
            reviewed_files=['.coderabbit.yaml', 'docs/code-review.md'],
            summary='No blocking defects identified in the supplied complete change.')

    def check(self):
        return self.mod.validate_review(self.verdict, self.expected, self.current)

    def test_paginated_gh_output_conserves_every_page(self):
        self.assertEqual(self.mod.decode_pages('[{"id":1}]\n[{"id":2}]\n'), [[{'id':1}], [{'id':2}]])
        with self.assertRaises(ValueError): self.mod.decode_pages('[1]\nNOT_JSON')
        with self.assertRaises(ValueError): self.mod.decode_pages('{"id":1}')

    def test_valid_clean_current_review_accepts(self):
        self.assertEqual(self.check(), self.verdict['summary'])

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


if __name__ == '__main__': unittest.main()
