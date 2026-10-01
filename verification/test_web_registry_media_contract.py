"""Regression controls for the bounded REG-08 media decision."""

import copy
import json
import tempfile
import unittest
from pathlib import Path

from check_web_registry_media_contract import (ROOT, VECTOR_PATH, media_decision,
                                                verify, verify_vectors)


class WebRegistryMediaContractTests(unittest.TestCase):
    def test_current_contract_and_vectors(self):
        self.assertEqual(verify(ROOT)['header_vectors'], 13)

    def test_parameter_duplicate_and_coding_fail_closed(self):
        valid = [['Content-Type', 'application/json']]
        self.assertEqual(media_decision(valid), 'MEDIA_ACCEPT')
        self.assertEqual(media_decision([['content-type', 'Application/JSON']]),
                         'MEDIA_ACCEPT')
        for changed in ([],
                        valid + [['content-type', 'application/json']],
                        [['Content-Type', 'application/json; charset=utf-8']],
                        valid + [['Content-Encoding', 'identity']]):
            with self.subTest(changed=changed):
                self.assertEqual(media_decision(changed), 'RECORD_INVALID')
        self.assertEqual(media_decision(valid, [['Content-Type', 'text/plain']]),
                         'RECORD_INVALID')

    def test_changed_expected_verdict_fails(self):
        vectors = json.loads((ROOT / VECTOR_PATH).read_text())
        altered = copy.deepcopy(vectors)
        altered['cases'][6]['expected'] = 'MEDIA_ACCEPT'
        with self.assertRaisesRegex(ValueError, 'vector decision'):
            verify_vectors(altered)

    def test_historical_or_current_source_drift_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            copy_root = Path(directory)
            for name in ('verification/web-registry-media-contract.json',
                         'verification/registry-operator-adoption.json',
                         'verification/history/web-registry-media-base-2026-09-30/spec/09-registry.md',
                         'verification/history/web-registry-media-base-2026-09-30/analysis/current-design-overlay.json',
                         'verification/history/registry-operator-base-2026-10-01/spec/09-registry.md',
                         'verification/history/registry-operator-base-2026-10-01/analysis/current-design-overlay.json',
                         'spec/09-registry.md', 'verification/traceability.json',
                         'analysis/current-design-overlay.json', VECTOR_PATH):
                target = copy_root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / name).read_bytes())
            current = (copy_root / 'verification/history/registry-operator-base-2026-10-01'
                       / 'spec/09-registry.md')
            current.write_text(current.read_text() + '\nchanged\n')
            with self.assertRaisesRegex(ValueError, 'current source bytes'):
                verify(copy_root)


if __name__ == '__main__':
    unittest.main()
