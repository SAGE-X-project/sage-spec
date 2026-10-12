"""Check that the A2A and DID adoption record rejects drift and evidence promotion."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from check_a2a_did_adoption import HISTORY, PROFILE, PROPOSAL, RECORD, ROOT, TRACE, prior_path, verify


def tracked_files():
    listed = subprocess.run(['git', 'ls-files', '--cached', '--others', '--exclude-standard'],
                            cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [name for name in listed.splitlines() if (ROOT / name).is_file()]


class A2ADidAdoptionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = tracked_files()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in self.files:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)

    def rewrite(self, name, change, repin=True):
        path = self.root / name
        path.write_text(change(path.read_text()))
        if repin:
            record_path = self.root / RECORD
            record = json.loads(record_path.read_text())
            record['current_sha256'][name] = hashlib.sha256(path.read_bytes()).hexdigest()
            record_path.write_text(json.dumps(record))

    def test_adopted_snapshot_passes(self):
        self.assertEqual(verify(self.root)['rule_groups'], 104)

    def test_unpinned_change_fails(self):
        self.rewrite(PROFILE, lambda text: text + '\n', repin=False)
        with self.assertRaisesRegex(ValueError, 'current bytes'):
            verify(self.root)

    def test_empty_relationship_rule_is_required(self):
        self.rewrite('spec/10-resolution.md', lambda text: text.replace(
            'with no member is omitted, never projected as an empty array', 'may be empty'))
        with self.assertRaisesRegex(ValueError, 'chapter 10 amendments'):
            verify(self.root)

    def test_case_must_match_reviewed_plan(self):
        def change(text):
            trace = json.loads(text)
            next(c for c in trace['cases'] if c['id'] == 'didp-05-deactivated')['input'] = 'other'
            return json.dumps(trace)
        self.rewrite(TRACE, change)
        with self.assertRaisesRegex(ValueError, 'reviewed plan'):
            verify(self.root)

    def test_existing_case_is_frozen(self):
        def change(text):
            trace = json.loads(text)
            trace['cases'][0]['expected'] = 'changed'
            return json.dumps(trace)
        self.rewrite(TRACE, change)
        with self.assertRaisesRegex(ValueError, 'existing case changed'):
            verify(self.root)

    def test_execution_claim_is_refused(self):
        path = self.root / RECORD
        record = json.loads(path.read_text())
        record['conformance'] = 'ESTABLISHED'
        path.write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError, 'evidence promotion'):
            verify(self.root)

    def test_proposal_stays_a_snapshot(self):
        name = PROPOSAL + '/README.md'
        path = self.root / name
        path.write_text(path.read_text().replace('proposed design, not adopted', 'adopted'))
        record_path = self.root / RECORD
        record = json.loads(record_path.read_text())
        record['proposal_sha256'][name] = hashlib.sha256(path.read_bytes()).hexdigest()
        record_path.write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError, 'historical snapshot'):
            verify(self.root)

    def test_prior_path_redirects_only_changed_files(self):
        self.assertEqual(prior_path(self.root, TRACE), self.root / HISTORY / TRACE)
        self.assertEqual(prior_path(self.root, 'spec/09-registry.md'), self.root / 'spec/09-registry.md')
        (self.root / RECORD).unlink()
        self.assertEqual(prior_path(self.root, TRACE), self.root / TRACE)


if __name__ == '__main__':
    unittest.main()
