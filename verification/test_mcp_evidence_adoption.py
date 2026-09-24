"""Preserve the distinction between execution evidence and protocol conformance."""

import copy
import json
from pathlib import Path
import unittest

import check_mcp_evidence_adoption as evidence


ROOT = Path(__file__).resolve().parents[1]


class EvidenceAdoptionTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((ROOT / 'verification/mcp-evidence-adoption.json').read_text())

    def check_changed(self, change, message):
        changed = copy.deepcopy(self.record)
        change(changed)
        with self.assertRaisesRegex(ValueError, message):
            evidence.verify_record(ROOT, changed)

    def test_pinned_evidence_remains_incomplete(self):
        result = evidence.verify_record(ROOT, self.record)
        self.assertEqual(result['ADOPT-05'], 'EVIDENCE_LINKED_WITH_SCOPE_LIMITS')
        self.assertEqual(result['ADOPT-06'], 'PENDING_EXTERNAL')

    def test_conformance_cannot_be_promoted(self):
        self.check_changed(lambda r: r.update(conformance='PASS'), 'promotion')

    def test_external_review_cannot_be_invented(self):
        self.check_changed(lambda r: r.update(external_audit='COMPLETE'), 'promotion')

    def test_historical_plan_cannot_be_rewritten(self):
        self.check_changed(lambda r: r['historical_plan'].update(execution='PASS'), 'plan boundary')

    def test_later_cases_cannot_be_counted_in_old_overlay(self):
        self.check_changed(lambda r: r['inspector']['binding_overlay'].update(parent_pass=85), 'binding scope')

    def test_ci_artifact_identity_cannot_change(self):
        self.check_changed(lambda r: r['inspector']['source_ci'].update(artifact_digest='sha256:' + '0' * 64),
                           'CI provenance')

    def test_source_digest_cannot_change(self):
        self.check_changed(lambda r: r['source_sha256'].update({'profiles/non-http-mcp-security.md': '0' * 64}),
                           'specification source')

    def test_external_finding_remains_pending(self):
        self.check_changed(lambda r: r['dispositions'].update({'ADOPT-06': 'RESOLVED'}),
                           'finding disposition')


if __name__ == '__main__':
    unittest.main()
