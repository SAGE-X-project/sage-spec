"""Mutation checks for the independent standards-clause vector package."""

import base64
import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from check_standards_vectors import (FIXTURE, ROOT, SOURCE_PATHS, P256_ORDER,
                                     http_gate, verify, verify_data)


class StandardsVectorTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / FIXTURE).read_text())

    def test_fixed_reference_vectors(self):
        result = verify(ROOT)
        self.assertEqual(result['case_vectors'], 8)
        self.assertEqual(result['independent_signatures_verified'], 4)
        self.assertEqual(result['implementation_conformance'], 'NOT_ESTABLISHED')

    def test_changed_signature_fails_independent_crypto_check(self):
        candidate = copy.deepcopy(self.data)
        case = candidate['cases'][0]
        raw = bytearray(base64.b64decode(case['signature_b64']))
        raw[0] ^= 1
        case['signature_b64'] = base64.b64encode(raw).decode()
        case['signature_field'] = 'sig1=:' + case['signature_b64'] + ':'
        with self.assertRaisesRegex(ValueError, 'independent OpenSSL verification'):
            verify_data(ROOT, candidate)

    def test_high_s_p256_fails_profile_check(self):
        candidate = copy.deepcopy(self.data)
        case = candidate['cases'][1]
        raw = bytearray(base64.b64decode(case['signature_b64']))
        low_s = int.from_bytes(raw[32:], 'big')
        raw[32:] = (P256_ORDER - low_s).to_bytes(32, 'big')
        case['signature_b64'] = base64.b64encode(raw).decode()
        case['signature_field'] = 'sig1=:' + case['signature_b64'] + ':'
        with self.assertRaisesRegex(ValueError, 'P-256 low-S signature'):
            verify_data(ROOT, candidate)

    def test_request_signature_substitution_changes_response_base(self):
        candidate = copy.deepcopy(self.data)
        reply = candidate['cases'][0]['response']
        reply['signature_base_ascii'] = reply['signature_base_ascii'].replace(
            '"signature";req: sig1=:', '"signature";req: sig1=:X', 1)
        with self.assertRaisesRegex(ValueError, 'request-bound response bytes'):
            verify_data(ROOT, candidate)

    def test_did_prefix_alias_is_not_accepted(self):
        candidate = copy.deepcopy(self.data)
        candidate['cases'][5]['identifiers'][1]['expected'] = 'VALID_PREFIX'
        with self.assertRaisesRegex(ValueError, 'mixed-case DID rejection'):
            verify_data(ROOT, candidate)

    def test_optional_suite_does_not_substitute_a_key(self):
        case = copy.deepcopy(self.data['cases'][1])
        case['record_key']['alg'] = 'ed25519'
        self.assertEqual(http_gate(case), 'REJECT_NO_MATCHING_HTTP_KEY')

    def test_current_spec_drift_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in SOURCE_PATHS | {FIXTURE}:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, target)
            path = root / 'spec/03-rfc9421.md'
            path.write_text(path.read_text() + '\nchanged\n')
            with self.assertRaisesRegex(ValueError, 'source bytes'):
                verify(root)

    def test_evidence_promotion_fails(self):
        candidate = copy.deepcopy(self.data)
        candidate['status'] = 'IMPLEMENTATION_CONFORMANT'
        with self.assertRaisesRegex(ValueError, 'fixture identity or evidence status'):
            verify_data(ROOT, candidate)


if __name__ == '__main__':
    unittest.main()
