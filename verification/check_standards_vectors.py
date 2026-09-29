"""Check independent, inert 0.10.0 standards-clause reference vectors."""

import argparse
import base64
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = 'verification/vectors/standards-clauses-0.10.0.json'
EXPECTED_FIXTURE_SHA256 = '9498da58d79e227295e623c3d4031c2525e68dfe4f8ddcaf1746631ff19572a5'
SOURCE_PATHS = {
    'spec/01-crypto.md', 'spec/03-rfc9421.md', 'spec/06-did-sage.md',
    'spec/08-transport.md', 'spec/10-resolution.md', 'spec/11-registries.md',
    'verification/traceability.json',
}
CASE_IDS = [
    'msca-http-ed25519', 'msca-http-p256', 'msca-http-private-alg',
    'msca-http-only-private-key', 'msca-http-no-substitution',
    'msca-did-prefix-case', 'msca-did-url-prefix-case',
    'msca-private-suite-non-http-scope',
]
HTTP_ALGS = {'ed25519', 'ecdsa-p256-sha256'}
P256_ORDER = int('ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551', 16)
COVERED = [
    '"@method"', '"@target-uri"', '"@authority"', '"content-type"',
    '"content-digest"', '"x-sage-did"', '"x-sage-version"',
]
RESPONSE_COVERED = [
    '"@status"', '"@method";req', '"@target-uri";req',
    '"@authority";req', '"content-digest";req', '"signature";req',
    '"x-sage-version";req', '"content-type"', '"content-digest"',
    '"x-sage-did"', '"x-sage-version"',
]


def require(condition, label):
    if not condition:
        raise ValueError(label)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decode_b64(value):
    raw = base64.b64decode(value, validate=True)
    require(base64.b64encode(raw).decode() == value, 'noncanonical base64')
    return raw


def decode_b64url(value):
    require(re.fullmatch(r'[A-Za-z0-9_-]*', value) is not None, 'base64url alphabet')
    raw = base64.urlsafe_b64decode(value + '=' * (-len(value) % 4))
    require(base64.urlsafe_b64encode(raw).rstrip(b'=').decode() == value,
            'noncanonical base64url')
    return raw


def signature_input(request, keyid, alg):
    parameters = (
        f';keyid="{keyid}";alg="{alg}";created={request["created"]}'
        f';expires={request["expires"]};nonce="{request["nonce"]}"'
        f';tag="{request["tag"]}"'
    )
    return 'sig1=(' + ' '.join(COVERED) + ')' + parameters


def signature_base(request, sig_input):
    values = [
        request['method'], request['target_uri'], request['authority'],
        request['content_type'], request['content_digest'],
        request['x_sage_did'], request['x_sage_version'],
    ]
    return '\n'.join(f'{name}: {value}' for name, value in zip(COVERED, values)) + (
        '\n"@signature-params": ' + sig_input.removeprefix('sig1='))


def response_signature_input(response, keyid, alg):
    return ('sig1=(' + ' '.join(RESPONSE_COVERED) + ')'
            + f';keyid="{keyid}";alg="{alg}";created={response["created"]}'
            + f';expires={response["expires"]};nonce="{response["nonce"]}"'
            + f';tag="{response["tag"]}"')


def response_signature_base(request, response, request_signature, sig_input):
    values = [
        str(response['status']), request['method'], request['target_uri'],
        request['authority'], request['content_digest'], request_signature,
        request['x_sage_version'], response['content_type'],
        response['content_digest'], response['x_sage_did'],
        response['x_sage_version'],
    ]
    return '\n'.join(f'{name}: {value}' for name, value in
                     zip(RESPONSE_COVERED, values)) + (
                         '\n"@signature-params": ' + sig_input.removeprefix('sig1='))


def http_gate(case):
    if case['alg'] not in HTTP_ALGS:
        return 'REJECT_HTTP_ALG'
    if case['inner_kid'] != case['outer_keyid']:
        return 'REJECT_KEYID_MISMATCH'
    keys = case['record_keys'] if 'record_keys' in case else [case['record_key']]
    if not any(key['kid'] == case['outer_keyid'] and key['alg'] == case['alg']
               and key['state'] == 'accepted' for key in keys):
        return 'REJECT_NO_MATCHING_HTTP_KEY'
    return 'ALLOW'


def der_integer(value):
    raw = value.to_bytes((value.bit_length() + 7) // 8 or 1, 'big')
    if raw[0] & 0x80:
        raw = b'\x00' + raw
    return b'\x02' + bytes([len(raw)]) + raw


def verify_signature(case):
    public = decode_b64(case['record_key']['public_spki_der_b64'])
    raw = decode_b64(case['signature_b64'])
    require(len(raw) == 64, 'signature width')
    if case['alg'] == 'ed25519':
        require(b'\x06\x03\x2b\x65\x70' in public, 'Ed25519 public key OID')
        signature = raw
    else:
        require(b'\x06\x08\x2a\x86\x48\xce\x3d\x03\x01\x07' in public,
                'P-256 public key OID')
        r = int.from_bytes(raw[:32], 'big')
        s = int.from_bytes(raw[32:], 'big')
        require(1 <= r < P256_ORDER and 1 <= s <= P256_ORDER // 2,
                'P-256 low-S signature')
        inner = der_integer(r) + der_integer(s)
        signature = b'\x30' + bytes([len(inner)]) + inner
    pem = (b'-----BEGIN PUBLIC KEY-----\n' + base64.encodebytes(public)
           + b'-----END PUBLIC KEY-----\n')
    with tempfile.TemporaryDirectory() as directory:
        tmp = Path(directory)
        (tmp / 'key.pem').write_bytes(pem)
        (tmp / 'base').write_bytes(case['signature_base_ascii'].encode('ascii'))
        (tmp / 'sig').write_bytes(signature)
        if case['alg'] == 'ed25519':
            command = ['openssl', 'pkeyutl', '-verify', '-pubin', '-inkey',
                       str(tmp / 'key.pem'), '-rawin', '-in', str(tmp / 'base'),
                       '-sigfile', str(tmp / 'sig')]
        else:
            command = ['openssl', 'dgst', '-sha256', '-verify',
                       str(tmp / 'key.pem'), '-signature', str(tmp / 'sig'),
                       str(tmp / 'base')]
        result = subprocess.run(command, capture_output=True, text=True,
                                timeout=10, check=False)
        require(result.returncode == 0, 'independent OpenSSL verification: '
                + case['case_id'] + ': ' + result.stderr.strip())


def verify_data(root, data):
    require(data['schema_version'] == 1
            and data['kind'] == 'standards-clause-independent-fixtures'
            and data['protocol_version'] == '0.10.0'
            and data['status'] == 'OFFLINE_REFERENCE_VECTORS_NOT_IMPLEMENTATION_RESULTS'
            and data['normative_revision'] ==
            '1c97e509424f06ffe48161fb948778563adbd62b',
            'fixture identity or evidence status')
    require(set(data['source_sha256']) == SOURCE_PATHS, 'source inventory')
    for name, digest in data['source_sha256'].items():
        require(sha(root / name) == digest, 'source bytes: ' + name)
    trace = json.loads((root / 'verification/traceability.json').read_text())
    planned = {case['id']: case for case in trace['cases']}
    require([case['case_id'] for case in data['cases']] == CASE_IDS
            and all(planned[name]['evidence_status'] == 'planned_not_executed'
                    for name in CASE_IDS), 'planned case correspondence')
    provenance = data['provenance']
    require(all(provenance[key] for key in ('construction', 'signatures', 'limitations'))
            and 'not a SAGE wire envelope' in provenance['limitations'],
            'vector provenance or scope')

    request = data['http_request']
    require(request['method'] == 'POST'
            and request['target_uri'] == 'https://processor.example.com/sage/messages'
            and request['authority'] == 'processor.example.com'
            and request['content_type'] == 'application/json'
            and request['x_sage_did'] ==
            'did:sage:web:agents.example.com:billing-bot'
            and request['x_sage_version'] == '0.10.0'
            and request['covered_components'] == COVERED
            and request['tag'] == 'sage-0.10.0'
            and request['expires'] - request['created'] == 300
            and len(decode_b64url(request['nonce'])) == 16,
            'fixed HTTP seam inputs')
    expected_digest = 'sha-256=:' + base64.b64encode(
        hashlib.sha256(request['body_utf8'].encode('utf-8')).digest()).decode() + ':'
    require(request['content_digest'] == expected_digest, 'received-body digest')
    response = data['http_response']
    response_digest = 'sha-256=:' + base64.b64encode(
        hashlib.sha256(response['body_utf8'].encode('utf-8')).digest()).decode() + ':'
    require(response['status'] == 200
            and response['content_type'] == 'application/json'
            and response['content_digest'] == response_digest
            and response['x_sage_did'] ==
            'did:sage:web:processor.example.com:processor'
            and response['x_sage_version'] == '0.10.0'
            and response['covered_components'] == RESPONSE_COVERED
            and response['tag'] == 'sage-0.10.0'
            and response['expires'] - response['created'] == 300
            and len(decode_b64url(response['nonce'])) == 16,
            'fixed response seam inputs')

    by_id = {case['case_id']: case for case in data['cases']}
    for name in CASE_IDS[:2]:
        case = by_id[name]
        alg = 'ed25519' if name.endswith('ed25519') else 'ecdsa-p256-sha256'
        require(case['kind'] == 'http-signature-seam'
                and case['alg'] == alg and case['record_key']['alg'] == alg
                and case['suite_support'] == ('mandatory' if alg == 'ed25519'
                                              else 'optional')
                and http_gate(case) == 'ALLOW'
                and case['expected'] == {
                    'algorithm': 'ALLOW', 'key_binding': 'MATCH',
                    'cryptographic_signature': 'VALID',
                    'whole_http_and_envelope': 'NOT_EVALUATED'},
                'positive HTTP suite decision: ' + name)
        expected_input = signature_input(request, case['outer_keyid'], alg)
        require(case['signature_input'] == expected_input
                and case['signature_base_ascii'] ==
                signature_base(request, expected_input)
                and case['signature_field'] == 'sig1=:' + case['signature_b64'] + ':',
                'exact HTTP signature bytes: ' + name)
        verify_signature(case)
        reply = case['response']
        reply_input = response_signature_input(response, reply['keyid'], alg)
        require(reply['alg'] == alg
                and reply['record_key']['kid'] == reply['keyid']
                and reply['record_key']['alg'] == alg
                and reply['record_key']['state'] == 'accepted'
                and reply['keyid'].startswith(response['x_sage_did'] + '#')
                and reply['signature_input'] == reply_input
                and reply['signature_base_ascii'] == response_signature_base(
                    request, response, case['signature_field'], reply_input)
                and reply['signature_field'] ==
                    'sig1=:' + reply['signature_b64'] + ':'
                and reply['expected'] == {
                    'request_signature_binding': 'EXACT_RECEIVED_FIELD',
                    'cryptographic_signature': 'VALID',
                    'whole_response': 'NOT_EVALUATED'},
                'request-bound response bytes: ' + name)
        verify_signature(reply)

    private = by_id['msca-http-private-alg']
    require(private['kind'] == 'http-algorithm-seam'
            and private['alg'] == 'sage-secp256k1-keccak256'
            and http_gate(private) == private['expected']['decision'] ==
            'REJECT_HTTP_ALG'
            and private['expected']['remote_status'] == 401
            and private['expected']['dispatch_count'] == 0
            and private['signature_input'] ==
            signature_input(request, private['outer_keyid'], private['alg'])
            and private['signature_base_ascii'] ==
            signature_base(request, private['signature_input']),
            'private HTTP algorithm verdict')
    only_private = by_id['msca-http-only-private-key']
    substitution = by_id['msca-http-no-substitution']
    for case, kind, outcome in (
        (only_private, 'http-key-selection-seam', 'REJECT_NO_MATCHING_HTTP_KEY'),
        (substitution, 'http-key-selection-seam', 'REJECT_KEYID_MISMATCH'),
    ):
        require(case['kind'] == kind and http_gate(case) == outcome
                and case['expected'] == {'decision': outcome, 'dispatch_count': 0},
                'key selection verdict: ' + case['case_id'])
    require(only_private['record_keys'] == [
        {'kid': only_private['inner_kid'], 'alg': 'sage-secp256k1-keccak256',
         'state': 'accepted'}], 'private-only record shape')
    require(substitution['inner_kid'] != substitution['outer_keyid']
            and {key['alg'] for key in substitution['record_keys']} ==
            {'ed25519', 'sage-secp256k1-keccak256'}, 'substitution record shape')

    for name, is_url in (('msca-did-prefix-case', False),
                         ('msca-did-url-prefix-case', True)):
        case = by_id[name]
        require(case['kind'] == 'did-prefix-seam'
                and case['expected'] == {'lookup_count_for_rejected': 0}
                and len(case['identifiers']) == 3, 'DID case shape: ' + name)
        canonical = case['identifiers'][0]['value']
        require(canonical.startswith('did:sage:')
                and ('#' in canonical) == is_url
                and case['identifiers'][0]['expected'] == 'VALID_PREFIX',
                'canonical DID prefix: ' + name)
        for altered in case['identifiers'][1:]:
            require(altered['value'] in (canonical.replace('did:', 'DID:', 1),
                                         canonical.replace('sage:', 'SAGE:', 1))
                    and not altered['value'].startswith('did:sage:')
                    and altered['expected'] == 'id.malformed',
                    'mixed-case DID rejection: ' + name)

    non_http = by_id['msca-private-suite-non-http-scope']
    require(non_http['kind'] == 'non-http-suite-seam'
            and non_http['binding'] == 'wire-envelope'
            and non_http['alg'] == 'sage-secp256k1-keccak256'
            and non_http['record_keys'] == [
                {'kid': non_http['kid'], 'alg': non_http['alg'], 'state': 'accepted'}]
            and non_http['expected'] == {
                'decision': 'ELIGIBLE_FOR_NON_HTTP_SUITE_CHECKS',
                'cryptographic_signature': 'NOT_EVALUATED',
                'whole_envelope': 'NOT_EVALUATED'},
            'non-HTTP private suite scope')

    jwk = data['jwk_representation']
    key = jwk['jwk']
    x = decode_b64url(key['x'])
    y = decode_b64url(key['y'])
    sec1 = b'\x04' + x + y
    spki = decode_b64(jwk['public_spki_der_b64'])
    require(jwk['rule_ids'] == ['RESOLVE-01', 'TABLE-03']
            and jwk['source'] == 'RFC 8812 section 3.1'
            and set(key) == {'kty', 'crv', 'x', 'y'}
            and key['kty'] == 'EC' and key['crv'] == 'secp256k1'
            and len(x) == len(y) == 32
            and jwk['public_sec1_hex'] == sec1.hex()
            and b'\x06\x05\x2b\x81\x04\x00\x0a' in spki
            and spki.endswith(sec1)
            and jwk['expected'] == {
                'key_representation': 'VALID_UNCOMPRESSED_POINT_SHAPE',
                'jose_algorithm': 'NOT_INFERRED',
                'sage_signing_suite': 'NOT_INFERRED',
                'whole_resolution': 'NOT_EVALUATED'},
            'RFC 8812 JWK representation boundary')
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'public.der'
        path.write_bytes(spki)
        result = subprocess.run(['openssl', 'pkey', '-pubin', '-inform', 'DER',
                                 '-in', str(path), '-noout'], capture_output=True,
                                text=True, timeout=10, check=False)
        require(result.returncode == 0, 'independent secp256k1 point parsing')
    return {'case_vectors': len(CASE_IDS), 'independent_signatures_verified': 4,
            'implementation_conformance': 'NOT_ESTABLISHED'}


def verify(root=ROOT):
    path = root / FIXTURE
    require(sha(path) == EXPECTED_FIXTURE_SHA256, 'fixed vector bytes')
    data = json.loads(path.read_text())
    return verify_data(root, data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        result = verify(args.root)
    except (ValueError, KeyError, OSError, TypeError, subprocess.TimeoutExpired,
            FileNotFoundError) as error:
        parser.exit(1, 'Standards vectors FAIL: ' + str(error) + '\n')
    print('Standards vectors PASS: ' + json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
