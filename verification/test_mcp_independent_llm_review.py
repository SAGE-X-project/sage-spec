"""Prevent a scoped LLM review from being silently promoted to audit or pass."""

import copy
import json
from pathlib import Path
import unittest

import check_mcp_independent_llm_review as review


ROOT = Path(__file__).resolve().parents[1]


class IndependentLlmReviewTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((ROOT / 'verification/mcp-independent-llm-review.json').read_text())

    def changed(self, update, message):
        candidate = copy.deepcopy(self.record)
        update(candidate)
        with self.assertRaisesRegex(ValueError, message):
            review.verify_record(ROOT, candidate)

    def test_open_findings_are_recorded(self):
        self.assertEqual(review.verify_record(ROOT, self.record)['open_findings'],
                         ['LLM-01', 'LLM-02'])

    def test_third_party_audit_cannot_be_claimed(self):
        self.changed(lambda r: r.update(third_party_audit='PASS'), 'promoted')

    def test_findings_cannot_be_closed_without_correction(self):
        self.changed(lambda r: r['findings'][0].update(status='CLOSED'),
                     'open normative')

    def test_findings_cannot_be_omitted(self):
        self.changed(lambda r: r['findings'].pop(), 'open normative')

    def test_independence_cannot_be_invented(self):
        self.changed(lambda r: r.update(organizationally_external=True), 'promoted')


if __name__ == '__main__':
    unittest.main()
