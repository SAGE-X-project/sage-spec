"""Mutation checks for the offline wire and HTTP binding fixture."""

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from check_wire_http_vectors import (FIXTURE, ROOT, SOURCE_PATHS, b64url,
                                     decode_b64url, jcs_subset, parse_json,
                                     verify, verify_data)


class WireHttpVectorTests(unittest.TestCase):
    def setUp(self):
        self.data = parse_json((ROOT / FIXTURE).read_bytes())

    def test_four_signatures_and_scope(self):
        self.assertEqual(verify(ROOT), {
            'wire_signatures_verified': 2,
            'http_signatures_verified': 2,
            'implementation_conformance': 'NOT_ESTABLISHED',
        })

    def test_changed_request_payload_fails_inner_signature(self):
        candidate = copy.deepcopy(self.data)
        body = parse_json(candidate['http_request']['body_utf8'])
        init = parse_json(decode_b64url(body['payload']))
        init['enc'] = b64url(bytes(32))
        body['payload'] = b64url(jcs_subset(init))
        candidate['http_request']['body_utf8'] = json.dumps(body, separators=(',', ':'))
        with self.assertRaisesRegex(ValueError, 'wire request signature input'):
            verify_data(ROOT, candidate)

    def test_changed_inner_signature_fails_openssl(self):
        candidate = copy.deepcopy(self.data)
        body = parse_json(candidate['http_request']['body_utf8'])
        raw = bytearray(decode_b64url(body['signature']))
        raw[0] ^= 1
        body['signature'] = b64url(raw)
        candidate['http_request']['body_utf8'] = json.dumps(body, separators=(',', ':'))
        with self.assertRaisesRegex(ValueError, 'wire request independent OpenSSL verification'):
            verify_data(ROOT, candidate)

    def test_changed_http_target_fails_outer_binding(self):
        candidate = copy.deepcopy(self.data)
        candidate['http_request']['target_uri'] = 'https://processor.example.com/other'
        with self.assertRaisesRegex(ValueError, 'HTTP request/body binding'):
            verify_data(ROOT, candidate)

    def test_changed_response_request_hash_fails_exact_binding(self):
        candidate = copy.deepcopy(self.data)
        body = parse_json(candidate['http_response']['body_utf8'])
        body['request_hash'] = 'A' * 43
        candidate['http_response']['body_utf8'] = json.dumps(body, separators=(',', ':'))
        with self.assertRaisesRegex(ValueError, 'response/request binding'):
            verify_data(ROOT, candidate)

    def test_different_outer_key_is_not_substituted(self):
        candidate = copy.deepcopy(self.data)
        candidate['http_request']['keyid'] = candidate['public_keys']['responder']['kid']
        with self.assertRaisesRegex(ValueError, 'HTTP request/body binding'):
            verify_data(ROOT, candidate)

    def test_response_outer_signature_uses_exact_request_signature_field(self):
        candidate = copy.deepcopy(self.data)
        candidate['http_request']['signature_field'] += 'X'
        with self.assertRaisesRegex(ValueError, 'HTTP request signature bytes'):
            verify_data(ROOT, candidate)

    def test_response_context_mismatch_fails(self):
        candidate = copy.deepcopy(self.data)
        body = parse_json(candidate['http_response']['body_utf8'])
        body['context_id'] = '123e4567-e89b-42d3-a456-426614174999'
        candidate['http_response']['body_utf8'] = json.dumps(body, separators=(',', ':'))
        with self.assertRaisesRegex(ValueError, 'response/request binding'):
            verify_data(ROOT, candidate)

    def test_duplicate_json_member_fails(self):
        candidate = copy.deepcopy(self.data)
        candidate['http_request']['body_utf8'] = candidate['http_request'][
            'body_utf8'].replace('{', '{"version":"0.10.0",', 1)
        with self.assertRaisesRegex(ValueError, 'duplicate JSON member'):
            verify_data(ROOT, candidate)

    def test_source_drift_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in SOURCE_PATHS | {FIXTURE}:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, target)
            path = root / 'spec/08-transport.md'
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
