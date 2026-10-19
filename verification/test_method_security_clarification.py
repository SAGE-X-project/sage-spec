"""Exercise historical-byte preservation and refusal of evidence promotion."""

import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from check_method_security_clarification import (
    CHAPTER, FILES, HISTORY, OVERLAY, RECORD, ROOT,
    at_previous_adoption, verify,
)


class MethodSecurityClarificationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        names = set(FILES) | {HISTORY + '/' + name for name in FILES} | {
            RECORD, 'verification/a2a-did-adoption.json',
            'verification/method-security-clarification-review.md',
        }
        for name in names:
            dest = self.root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, dest)

    def alter_record(self, change):
        path = self.root / RECORD
        value = json.loads(path.read_text())
        change(value)
        path.write_text(json.dumps(value))

    def test_current_analysis_and_previous_snapshot_are_distinct(self):
        result = verify(self.root)
        self.assertEqual(result['new_conformance_verdicts'], 0)
        self.assertEqual(result['runtime_execution'], 'NOT_RUN')
        self.assertNotEqual((self.root / CHAPTER).read_bytes(),
                            at_previous_adoption(self.root, CHAPTER).read_bytes())
        self.assertEqual(at_previous_adoption(self.root, 'spec/09-registry.md'),
                         self.root / 'spec/09-registry.md')

    def test_current_text_drift_cannot_hide_behind_old_snapshot(self):
        path = self.root / CHAPTER
        path.write_bytes(path.read_bytes() + b'\n')
        with self.assertRaisesRegex(ValueError, 'current bytes'):
            at_previous_adoption(self.root, CHAPTER)

    def test_repin_cannot_weaken_previous_normative_rule(self):
        path = self.root / CHAPTER
        before = path.read_text()
        path.write_text(before.replace('MUST NOT try', 'MAY try'))
        self.assertNotEqual(path.read_text(), before)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        self.alter_record(lambda r: r['current_sha256'].__setitem__(CHAPTER, digest))
        with self.assertRaisesRegex(ValueError, 'pre-existing normative text'):
            verify(self.root)

    def test_history_drift_is_not_an_authorized_new_baseline(self):
        path = self.root / HISTORY / CHAPTER
        path.write_bytes(path.read_bytes() + b'\n')
        with self.assertRaisesRegex(ValueError, 'preserved adopted bytes'):
            verify(self.root)

    def test_joint_repin_cannot_normalize_away_changed_baseline_bytes(self):
        chapter = self.root / CHAPTER
        chapter.write_bytes(chapter.read_bytes().replace(b'\n', b'\r\n'))
        digest = hashlib.sha256(chapter.read_bytes()).hexdigest()
        overlay = self.root / OVERLAY
        graph = json.loads(overlay.read_text())
        node = next(n for n in graph['nodes']
                    if n['id'] == 'doc:sage-spec:' + CHAPTER)
        node['sha256'] = digest
        overlay.write_text(json.dumps(graph))
        overlay_digest = hashlib.sha256(overlay.read_bytes()).hexdigest()
        self.alter_record(lambda r: r['current_sha256'].update({
            CHAPTER: digest, OVERLAY: overlay_digest}))
        with self.assertRaisesRegex(ValueError, 'analysis boundaries|pre-existing normative text'):
            verify(self.root)

    def test_repin_cannot_change_another_overlay_node(self):
        path = self.root / OVERLAY
        graph = json.loads(path.read_text())
        node = next(n for n in graph['nodes'] if n['id'] == 'layer:L0')
        node['label'] = 'changed authority'
        path.write_text(json.dumps(graph))
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        self.alter_record(lambda r: r['current_sha256'].__setitem__(OVERLAY, digest))
        with self.assertRaisesRegex(ValueError, 'overlay changed beyond'):
            verify(self.root)

    def test_review_drift_is_detected(self):
        path = self.root / 'verification/method-security-clarification-review.md'
        path.write_bytes(path.read_bytes() + b'\n')
        with self.assertRaisesRegex(ValueError, 'review provenance'):
            verify(self.root)

    def test_no_new_pass_or_operational_claim(self):
        for field, value in [
            ('new_conformance_verdicts', {'privacy': 'PASS'}),
            ('runtime_execution', 'PASS'),
            ('operating_roots_selected', True),
            ('wire_acceptance_changed', True),
            ('authentication_rule_adopted', True),
            ('fork_policy_adopted', True),
        ]:
            with self.subTest(field=field):
                original = (self.root / RECORD).read_bytes()
                self.alter_record(lambda r: r.__setitem__(field, value))
                with self.assertRaisesRegex(ValueError, 'evidence promotion'):
                    verify(self.root)
                (self.root / RECORD).write_bytes(original)

    def test_no_historical_failure_is_removed(self):
        self.alter_record(lambda r: r['historical_verdicts'].pop(
            'did11-cr20260305#security-requirements.5'))
        with self.assertRaisesRegex(ValueError, 'seven historical findings'):
            verify(self.root)

    def test_inventory_cannot_redirect_to_unchecked_file(self):
        self.alter_record(lambda r: r['current_sha256'].__setitem__(
            '../outside', '0' * 64))
        with self.assertRaisesRegex(ValueError, 'exact file inventory'):
            verify(self.root)


if __name__ == '__main__':
    unittest.main()
