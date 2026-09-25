"""Keep review preparation distinct from independent review and conformance."""

import copy
import json
from pathlib import Path
import unittest

import check_mcp_external_review_package as review


ROOT = Path(__file__).resolve().parents[1]


class ExternalReviewPackageTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((ROOT / 'verification/mcp-external-review-package.json').read_text())

    def changed(self, update, message):
        candidate = copy.deepcopy(self.record)
        update(candidate)
        with self.assertRaisesRegex(ValueError, message):
            review.verify_record(ROOT, candidate)

    def test_unreviewed_package_is_ready(self):
        self.assertEqual(review.verify_record(ROOT, self.record)['status'],
                         'READY_FOR_EXTERNAL_REVIEW')

    def test_preparation_cannot_be_called_review(self):
        self.changed(lambda r: r.update(status='REVIEWED'), 'promoted')

    def test_reviewer_cannot_be_invented(self):
        self.changed(lambda r: r.update(reviewer='unverified'), 'promoted')

    def test_report_cannot_be_invented(self):
        self.changed(lambda r: r.update(review_report='pass'), 'promoted')

    def test_conformance_cannot_be_promoted(self):
        self.changed(lambda r: r.update(conformance='PASS'), 'promoted')

    def test_scope_cannot_be_shrunk(self):
        self.changed(lambda r: r['review_areas'].pop(), 'scope changed')

    def test_host_cannot_be_promoted(self):
        self.changed(lambda r: r['evidence_limits'].update(deployed_agent_host='PASS'),
                     'limits promoted')

    def test_source_digest_cannot_change(self):
        self.changed(lambda r: r['target_sha256'].update({'profiles/non-http-mcp-security.md': '0' * 64}),
                     'review target identity')


if __name__ == '__main__':
    unittest.main()
