"""Check that the design baseline rejects source and inventory drift."""

import json
from pathlib import Path
import shutil
import tempfile
import unittest

from freeze_first_stage import ROOT, SOURCES, inspect, verify


class FirstStageBaselineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in SOURCES:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        record = self.root / 'verification/first-stage-baseline.json'
        shutil.copyfile(ROOT / 'verification/first-stage-baseline.json', record)

    def test_exact_snapshot_passes(self):
        self.assertEqual(verify(self.root)['counts']['operator_subconditions'], 17)

    def test_normative_byte_change_fails(self):
        path = self.root / 'spec/09-registry.md'
        path.write_text(path.read_text() + '\n')
        with self.assertRaisesRegex(ValueError, 'baseline drift'):
            verify(self.root)

    def test_missing_operator_subcondition_fails(self):
        path = self.root / 'verification/vectors/registry-operator-0.10.0.json'
        value = json.loads(path.read_bytes())
        value['cases'].pop()
        path.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, 'operator subcondition inventory'):
            inspect(self.root)


if __name__ == '__main__':
    unittest.main()
