"""Consistency tests for the coordinated specification snapshot."""

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from check_spec_revision_adoption import ROOT, verify


class SpecRevisionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / "spec"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(".git", "__pycache__"))

    def change_trace(self, change):
        path = self.root / "verification/traceability.json"
        plan = json.loads(path.read_text())
        change(plan)
        path.write_text(json.dumps(plan, indent=2) + "\n")
        record_path = self.root / "verification/spec-revision-adoption.json"
        record = json.loads(record_path.read_text())
        record["current_sha256"]["verification/traceability.json"] = hashlib.sha256(path.read_bytes()).hexdigest()
        record_path.write_text(json.dumps(record, indent=2) + "\n")

    def test_snapshot_is_planned(self):
        self.assertEqual(verify(self.root)["parent_cases"], 471)

    def test_prior_case_cannot_change(self):
        self.change_trace(lambda plan: plan["cases"][0].update(expected="changed"))
        with self.assertRaisesRegex(ValueError, "historical case changed"):
            verify(self.root)

    def test_new_case_cannot_be_promoted(self):
        self.change_trace(lambda plan: next(case for case in plan["cases"]
                                            if case["id"] == "mrevision-hop-unapproved")
                          .update(evidence_status="PASS"))
        with self.assertRaisesRegex(ValueError, "new case plan"):
            verify(self.root)

    def test_new_case_cannot_be_detached(self):
        self.change_trace(lambda plan: next(rule for rule in plan["rules"]
                                            if rule["id"] == "EXEC-02")["case_ids"]
                          .remove("mrevision-hop-unapproved"))
        with self.assertRaisesRegex(ValueError, "rule case mapping"):
            verify(self.root)

    def test_normative_file_cannot_drift(self):
        with (self.root / "profiles/agent-mcp-security.md").open("a") as stream:
            stream.write("\nChanged trust rule\n")
        with self.assertRaisesRegex(ValueError, "current identity"):
            verify(self.root)


if __name__ == "__main__":
    unittest.main()
