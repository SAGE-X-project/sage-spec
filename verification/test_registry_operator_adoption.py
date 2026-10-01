"""Regression checks for the versioned operator design record."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from check_registry_operator_adoption import ROOT, verify


FILES = (
    'verification/registry-operator-adoption.json',
    'verification/web-registry-media-contract.json',
    'verification/vectors/registry-operator-0.10.0.json',
    'verification/vectors/web-registry-media-0.10.0.json',
    'verification/traceability.json',
    'verification/history/registry-operator-base-2026-10-01/spec/09-registry.md',
    'verification/history/registry-operator-base-2026-10-01/analysis/current-design-overlay.json',
    'verification/history/web-registry-media-base-2026-09-30/spec/09-registry.md',
    'verification/history/web-registry-media-base-2026-09-30/analysis/current-design-overlay.json',
    'spec/09-registry.md',
    'analysis/current-design-overlay.json',
    'proposals/registry-operator-transaction/README.md',
)


class RegistryOperatorAdoptionTests(unittest.TestCase):
    def test_current_record(self):
        self.assertEqual(verify(ROOT)['operator_subconditions'], 17)

    def test_tampering_fails_closed(self):
        changes = (
            ('verification/vectors/registry-operator-0.10.0.json', 'verdict'),
            ('verification/history/registry-operator-base-2026-10-01/spec/09-registry.md', 'history'),
            ('spec/09-registry.md', 'current'),
            ('verification/registry-operator-adoption.json', 'claim'),
        )
        for filename, kind in changes:
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for name in FILES:
                    target = root / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(ROOT / name, target)
                target = root / filename
                if kind == 'verdict':
                    value = json.loads(target.read_text())
                    value['cases'][0]['expected'] = 'REJECT_UNCHANGED'
                    target.write_text(json.dumps(value))
                elif kind == 'claim':
                    value = json.loads(target.read_text())
                    value['conformance'] = 'ESTABLISHED'
                    target.write_text(json.dumps(value))
                else:
                    target.write_text(target.read_text() + '\nchanged\n')
                with self.assertRaises(ValueError):
                    verify(root)


if __name__ == '__main__':
    unittest.main()
