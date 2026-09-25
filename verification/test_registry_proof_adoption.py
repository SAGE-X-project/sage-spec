"""Keep the registry correction separate from historical or runtime evidence."""

import copy
import json
from pathlib import Path
import unittest

import check_registry_proof_adoption as revision


ROOT = Path(__file__).resolve().parents[1]


class RegistryProofAdoptionTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((ROOT / 'verification/registry-proof-revision.json').read_text())

    def changed(self, update, message):
        candidate = copy.deepcopy(self.record)
        update(candidate)
        with self.assertRaisesRegex(ValueError, message):
            revision.verify_record(ROOT, candidate)

    def test_unexecuted_correction(self):
        self.assertEqual(revision.verify_record(ROOT, self.record)['parent_cases'], 479)

    def test_prior_review_cannot_change(self):
        self.changed(lambda r: r.update(prior_review_report_sha256='0' * 64),
                     'prior review provenance')

    def test_old_snapshot_cannot_change(self):
        self.changed(lambda r: r['historical_sha256'].update({'spec/09-registry.md': '0' * 64}),
                     'historical source')

    def test_rereview_cannot_be_invented(self):
        self.changed(lambda r: r.update(independent_rereview='PASS'),
                     'evidence claim promoted')

    def test_conformance_cannot_be_invented(self):
        self.changed(lambda r: r.update(conformance='PASS'), 'evidence claim promoted')

    def test_new_case_cannot_disappear(self):
        self.changed(lambda r: r['new_case_ids'].pop(), 'plan counts or cases')


if __name__ == '__main__':
    unittest.main()
