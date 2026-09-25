"""Check 0.10.0 registry proof bytes and KEM-role specification fixtures."""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREFIX = b'sage-pop-0.10.0'
SIGNING = {'ed25519', 'sage-secp256k1-keccak256', 'ecdsa-p256-sha256'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_vector(vector):
    challenge = bytes.fromhex(vector['challenge_hex'])
    require(challenge.startswith(PREFIX), 'PoP domain')
    offset = len(PREFIX)
    fields = [vector['registry_id'].encode('ascii'), vector['agent_id'].encode('ascii'),
              vector['name'].encode('ascii'), vector['alg'].encode('ascii'),
              bytes.fromhex(vector['public_key_hex'])]
    for expected in fields:
        require(offset + 2 <= len(challenge), 'PoP length missing')
        size = int.from_bytes(challenge[offset:offset + 2], 'big')
        offset += 2
        require(size == len(expected), 'PoP field length')
        require(challenge[offset:offset + size] == expected, 'PoP field bytes')
        offset += size
    require(offset == len(challenge), 'PoP trailing or duplicated bytes')
    require(hashlib.sha256(challenge).hexdigest() == vector['challenge_sha256'],
            'PoP digest')
    require(vector['alg'] in SIGNING | {'x25519'}
            and len(fields[-1]) == 32, 'key algorithm or fixture length')


def verify_record(record):
    require(record['schema_version'] == 1
            and record['protocol_version'] == '0.10.0'
            and record['kind'] == 'registry-proof-and-kem-role-fixture'
            and record['status'] == 'SPECIFICATION_FIXTURE_NOT_IMPLEMENTATION_CONFORMANCE',
            'fixture identity')
    vectors = record['challenge_vectors']
    require([(v['name'], v['alg'], v['purpose']) for v in vectors] == [
        ('sign-1', 'ed25519', 'signing-key possession'),
        ('kem-a', 'x25519', 'signing-key endorsement of a KEM key'),
    ], 'fixture roles')
    for vector in vectors:
        check_vector(vector)
    selection = record['kem_selection']
    eligible = [key for key in selection['keys']
                if key['alg'] == 'x25519' and key['state'] == 'accepted'
                and selection['now'] < key['expires']]
    require(eligible and selection['selected_kid'] == selection['record_id'] + '#'
            + min(key['name'] for key in eligible), 'KEM key selection')
    require(record['negative_verdicts'] == [
        {'name': 'upper-case-kem-alg', 'alg': 'X25519', 'verdict': 'reject'},
        {'name': 'kem-as-signature', 'alg': 'x25519',
         'operation': 'message-signature', 'verdict': 'reject'},
        {'name': 'wrong-length-kem-key', 'alg': 'x25519',
         'public_key_hex': '8520f0098930a754748b7ddcb43ef75a0dbf3a0d26381af4eba4a98eaa9b4e',
         'verdict': 'reject'},
        {'name': 'duplicate-pop-fields', 'verdict': 'reject'},
    ], 'negative role verdicts')
    require(len(bytes.fromhex(record['negative_verdicts'][2]['public_key_hex'])) == 31,
            'invalid KEM length fixture')
    return {'challenge_vectors': len(vectors), 'kem_kid': selection['selected_kid'],
            'implementation_conformance': 'NOT_ESTABLISHED'}


def verify(root=ROOT):
    record = json.loads((root / 'verification/vectors/registry-proof-0.10.0.json').read_text())
    return verify_record(record)


if __name__ == '__main__':
    try:
        result = verify()
    except (ValueError, KeyError, OSError, TypeError) as error:
        raise SystemExit('Registry proof fixture FAIL: ' + str(error)) from error
    print('Registry proof fixture PASS: ' + json.dumps(result, sort_keys=True))
