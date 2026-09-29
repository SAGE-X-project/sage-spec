"""Prevent a scoped ADOPT-06 re-review from becoming a release claim."""

import copy
import json
from pathlib import Path
import unittest

import check_mcp_independent_llm_rereview as review


ROOT = Path(__file__).resolve().parents[1]


class MCPIndependentLLMRereviewTests(unittest.TestCase):
    def setUp(self):
        path = ROOT / 'verification/mcp-independent-llm-rereview.json'
        self.record = json.loads(path.read_text())

    def changed(self, update, message):
        candidate = copy.deepcopy(self.record)
        update(candidate)
        with self.assertRaisesRegex(ValueError, message):
            review.verify_record(ROOT, candidate)

    def test_pinned_review(self):
        result = review.verify_record(ROOT, self.record)
        self.assertEqual(result['text_findings_resolved'], ['LLM-01', 'LLM-02'])
        self.assertEqual(result['third_party_audit'], 'NOT_PERFORMED')

    def test_target_revision_cannot_change(self):
        self.changed(lambda r: r.update(target_revision='unreviewed'),
                     'identity and lineage')

    def test_source_digest_cannot_change(self):
        self.changed(lambda r: r['source_sha256'].update(
            {'spec/09-registry.md': '0' * 64}), 'reviewed source manifest')

    def test_external_audit_cannot_be_claimed(self):
        self.changed(lambda r: r.update(third_party_audit='PASS'),
                     'review claim promoted')

    def test_implementation_pass_cannot_be_claimed(self):
        self.changed(lambda r: r.update(implementation_conformance='PASS'),
                     'review claim promoted')

    def test_finding_disposition_cannot_change(self):
        self.changed(lambda r: r['previous_finding_dispositions'][0].update(
            status='FULLY_CONFORMANT'), 'previous finding dispositions')

    def test_new_findings_cannot_be_silently_erased(self):
        self.changed(lambda r: r['new_non_http_mcp_findings'].append('new'),
                     'scope and next gate')

    def test_descriptor_digest_cannot_change(self):
        self.changed(lambda r: r['descriptor_check'].update(
            sha256_jcs='sha256-jcs:wrong'), 'fixed descriptor bytes')


if __name__ == '__main__':
    unittest.main()
