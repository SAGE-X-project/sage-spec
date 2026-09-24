"""Safe consistency tests for the revised MCP design snapshot."""

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from check_mcp_errata_adoption import ROOT, verify


class ErrataAdoptionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "spec"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(".git", "__pycache__"))

    def change_current_trace(self, mutate):
        path = self.root / "verification/traceability.json"
        plan = json.loads(path.read_text())
        mutate(plan)
        path.write_text(json.dumps(plan, indent=2) + "\n")
        record_path = self.root / "verification/mcp-errata-adoption.json"
        record = json.loads(record_path.read_text())
        record["current_sha256"]["verification/traceability.json"] = hashlib.sha256(path.read_bytes()).hexdigest()
        record_path.write_text(json.dumps(record, indent=2) + "\n")

    def test_revised_plan_remains_unexecuted(self):
        self.assertEqual(verify(self.root)["new_parent_cases"], 9)

    def test_profile_identity_cannot_drift(self):
        with (self.root / "profiles/non-http-mcp-security.md").open("a") as stream:
            stream.write("\nChanged rule\n")
        with self.assertRaisesRegex(ValueError, "current identity"):
            verify(self.root)

    def test_old_case_cannot_be_rewritten(self):
        self.change_current_trace(lambda plan: plan["cases"][0].update(expected="changed"))
        with self.assertRaisesRegex(ValueError, "historical case changed"):
            verify(self.root)

    def test_new_case_cannot_be_promoted(self):
        self.change_current_trace(lambda plan: next(case for case in plan["cases"]
                                                 if case["id"] == "merrata-server-overlap")
                                  .update(evidence_status="PASS"))
        with self.assertRaisesRegex(ValueError, "new case plan"):
            verify(self.root)


if __name__ == "__main__":
    unittest.main()
