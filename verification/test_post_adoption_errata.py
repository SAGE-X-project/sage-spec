"""Safe consistency tests for the adopted MCP errata review."""

import copy
import json
import unittest
from pathlib import Path

from check_post_adoption_errata import ROOT, verify_record


class ErrataReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads((ROOT / "verification/post-adoption-errata-review.json").read_text())

    def test_reviewed_record(self):
        self.assertEqual(verify_record(ROOT, self.record)["open_normative"], 2)

    def test_historical_open_status_cannot_replace_current_disposition(self):
        changed = copy.deepcopy(self.record)
        changed["findings"][0]["status"] = "OPEN"
        with self.assertRaisesRegex(ValueError, "finding disposition"):
            verify_record(ROOT, changed)

    def test_missing_source_anchor_is_rejected(self):
        changed = copy.deepcopy(self.record)
        changed["findings"][1]["anchors"].append("unsupported protected-call limit")
        with self.assertRaisesRegex(ValueError, "source anchors"):
            verify_record(ROOT, changed)

    def test_conformance_promotion_is_rejected(self):
        changed = copy.deepcopy(self.record)
        changed["conformance"] = "ESTABLISHED"
        with self.assertRaisesRegex(ValueError, "conformance promotion"):
            verify_record(ROOT, changed)


if __name__ == "__main__":
    unittest.main()
