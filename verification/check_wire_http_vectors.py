"""Check offline wire-envelope and HTTP-signature binding reference bytes."""

import base64
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

from check_standards_vectors import (COVERED, RESPONSE_COVERED,
                                     response_signature_base,
                                     response_signature_input, signature_base,
                                     signature_input)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = 'verification/vectors/wire-http-binding-0.10.0.json'
EXPECTED_FIXTURE_SHA256 = '17de2b6ca0eaf71cb7e1ad4c569b2a7b0e235f1ba9992c05fcacde86fbcf6a63'
SOURCE_PATHS = {
    'spec/01-crypto.md', 'spec/02-jcs.md', 'spec/03-rfc9421.md',
    'spec/04-hpke.md', 'spec/06-did-sage.md', 'spec/08-transport.md',
}
VERSION = '0.10.0'
TAG = 'sage-0.10.0'
INIT_FIELDS = {
    'v', 'task', 'ctx', 'initDid', 'respDid', 'initKid', 'respKid',
    'kemKid', 'suite', 'combiner', 'nonce', 'enc', 'ephC',
}
UUID4 = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}')


def require(condition, label):
    if not condition:
        raise ValueError(label)


def no_duplicate_object(pairs):
    value = {}
    for key, member in pairs:
        require(key not in value, 'duplicate JSON member')
        value[key] = member
    return value


def parse_json(raw):
    return json.loads(raw, object_pairs_hook=no_duplicate_object,
                      parse_float=lambda _: require(False, 'noninteger number'),
                      parse_constant=lambda _: require(False, 'invalid number'))


def jcs_subset(value):
    """RFC 8785 bytes for this fixture's printable ASCII, integer subset."""
    if isinstance(value, dict):
        require(all(isinstance(k, str) for k in value), 'nonstring key')
        for key, member in value.items():
            jcs_subset(key)
            jcs_subset(member)
    elif isinstance(value, list):
        for member in value:
            jcs_subset(member)
    elif isinstance(value, str):
        require(all(0x20 <= ord(c) <= 0x7e and c not in '\\"'
                    for c in value), 'outside restricted JCS subset')
    else:
        require(type(value) in (int, bool) and
                (type(value) is bool or 0 <= value < 2**53),
                'outside restricted JCS subset')
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False).encode('ascii')


def b64url(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b'=').decode()


def decode_b64url(encoded):
    require(isinstance(encoded, str) and
            re.fullmatch(r'[A-Za-z0-9_-]*', encoded) is not None,
            'base64url alphabet')
    raw = base64.urlsafe_b64decode(encoded + '=' * (-len(encoded) % 4))
    require(b64url(raw) == encoded, 'noncanonical base64url')
    return raw


def public_key_pem(encoded):
    der = base64.b64decode(encoded, validate=True)
    require(base64.b64encode(der).decode() == encoded and
            b'\x06\x03\x2b\x65\x70' in der, 'Ed25519 public key encoding')
    return b'-----BEGIN PUBLIC KEY-----\n' + base64.encodebytes(der) + (
        b'-----END PUBLIC KEY-----\n')


def verify_ed25519(message, signature, public, label):
    raw = decode_b64url(signature)
    require(len(raw) == 64, label + ' signature width')
    with tempfile.TemporaryDirectory() as directory:
        tmp = Path(directory)
        (tmp / 'key.pem').write_bytes(public_key_pem(public))
        (tmp / 'message').write_bytes(message)
        (tmp / 'signature').write_bytes(raw)
        result = subprocess.run(
            ['openssl', 'pkeyutl', '-verify', '-pubin', '-inkey',
             str(tmp / 'key.pem'), '-rawin', '-in', str(tmp / 'message'),
             '-sigfile', str(tmp / 'signature')],
            capture_output=True, text=True, timeout=10, check=False)
        require(result.returncode == 0, label + ' independent OpenSSL verification')


def signature_field(encoded):
    raw = decode_b64url(encoded)
    return 'sig1=:' + base64.b64encode(raw).decode() + ':'


def check_common(body, expected_did, expected_recipient, key, now):
    require(body['version'] == VERSION and body['did'] == expected_did and
            body['recipient'] == expected_recipient and
            body['kid'] == key['kid'] and key['did'] == body['did'] and
            key['alg'] == 'ed25519' and key['state'] == 'accepted' and
            UUID4.fullmatch(body['id']) and
            type(body['created']) is int and type(body['expires']) is int and
            0 < body['expires'] - body['created'] <= 300 and
            body['created'] <= now + 30 and now < body['expires'] + 30 and
            len(decode_b64url(body['nonce'])) == 16 and
            body['encoding'] == 'plain' and 'session_id' not in body and
            len(decode_b64url(body['signature'])) == 64,
            'wire common binding')
    require(set(body) <= {
        'version', 'id', 'did', 'recipient', 'kid', 'created', 'expires',
        'nonce', 'encoding', 'signature', 'context_id', 'task_id', 'role',
        'metadata', 'payload', 'message_id', 'request_hash', 'success',
        'data', 'error',
    }, 'wire unknown member')


def check_http_request(http, body, key):
    raw = http['body_utf8'].encode('utf-8')
    digest = 'sha-256=:' + base64.b64encode(hashlib.sha256(raw).digest()).decode() + ':'
    require(http['method'] == 'POST' and
            http['target_uri'] == 'https://processor.example.com/sage/messages' and
            http['authority'] == 'processor.example.com' and
            http['content_type'] == 'application/json' and
            http['content_digest'] == digest and
            http['x_sage_did'] == body['did'] and
            http['x_sage_version'] == body['version'] and
            http['keyid'] == body['kid'] == key['kid'] and
            http['alg'] == key['alg'] == 'ed25519' and
            http['created'] == body['created'] and
            http['expires'] == body['expires'] and
            http['nonce'] == body['nonce'] and
            http['tag'] == TAG and http['covered_components'] == COVERED,
            'HTTP request/body binding')
    sig_input = signature_input(http, http['keyid'], http['alg'])
    base = signature_base(http, sig_input).encode('ascii')
    require(http['signature_input'] == sig_input and
            http['signature_base_ascii'].encode('ascii') == base and
            http['signature_field'] == signature_field(http['signature_b64url']),
            'HTTP request signature bytes')
    verify_ed25519(base, http['signature_b64url'], key['public_spki_der_b64'],
                   'HTTP request')


def check_http_response(request, response, body, key):
    raw = response['body_utf8'].encode('utf-8')
    digest = 'sha-256=:' + base64.b64encode(hashlib.sha256(raw).digest()).decode() + ':'
    require(response['status'] == 503 and
            response['content_type'] == 'application/json' and
            response['content_digest'] == digest and
            response['x_sage_did'] == body['did'] and
            response['x_sage_version'] == body['version'] and
            response['keyid'] == body['kid'] == key['kid'] and
            response['alg'] == key['alg'] == 'ed25519' and
            response['created'] == body['created'] and
            response['expires'] == body['expires'] and
            response['nonce'] == body['nonce'] and
            response['tag'] == TAG and
            response['covered_components'] == RESPONSE_COVERED,
            'HTTP response/body binding')
    sig_input = response_signature_input(response, response['keyid'],
                                         response['alg'])
    base = response_signature_base(request, response,
                                   request['signature_field'], sig_input).encode('ascii')
    require(response['signature_input'] == sig_input and
            response['signature_base_ascii'].encode('ascii') == base and
            response['signature_field'] == signature_field(response['signature_b64url']),
            'HTTP response signature bytes')
    verify_ed25519(base, response['signature_b64url'], key['public_spki_der_b64'],
                   'HTTP response')


def verify_data(root, data):
    require(data['schema_version'] == 1 and
            data['kind'] == 'wire-http-binding-independent-fixture' and
            data['protocol_version'] == VERSION and
            data['status'] == 'OFFLINE_REFERENCE_NOT_PROTOCOL_CONFORMANCE' and
            data['provenance']['limitations'].startswith('No HPKE SetupBase'),
            'fixture identity or evidence status')
    require(set(data['source_sha256']) == SOURCE_PATHS, 'source inventory')
    for name, digest in data['source_sha256'].items():
        require(hashlib.sha256((root / name).read_bytes()).hexdigest() == digest,
                'source bytes: ' + name)
    keys = data['public_keys']
    require(set(keys) == {'initiator', 'responder'} and
            keys['initiator']['did'] != keys['responder']['did'] and
            keys['initiator']['kid'] != keys['responder']['kid'],
            'fixture identities')
    request = data['http_request']
    response = data['http_response']
    req_body = parse_json(request['body_utf8'])
    res_body = parse_json(response['body_utf8'])
    now = data['reference_now']
    require(type(now) is int, 'reference time')
    check_common(req_body, keys['initiator']['did'], keys['responder']['did'],
                 keys['initiator'], now)
    require(set(req_body) == {
        'version', 'id', 'did', 'recipient', 'kid', 'created', 'expires',
        'nonce', 'encoding', 'signature', 'context_id', 'role', 'payload',
        'metadata',
    } and req_body['role'] == 'initiator' and
            UUID4.fullmatch(req_body['context_id']) and
            req_body['metadata'] == {'purpose': 'offline-binding-fixture'},
            'request envelope schema')
    init = parse_json(decode_b64url(req_body['payload']))
    require(set(init) == INIT_FIELDS and
            decode_b64url(req_body['payload']) == jcs_subset(init) and
            init['v'] == VERSION and init['task'] == 'hpke/init@0.10.0' and
            init['ctx'] == req_body['context_id'] and
            init['initDid'] == req_body['did'] and
            init['respDid'] == req_body['recipient'] and
            init['initKid'] == req_body['kid'] and
            init['respKid'] == keys['responder']['kid'] and
            init['kemKid'] == data['kem_key_reference'] and
            init['nonce'] == req_body['nonce'] and
            init['suite'] == 'hpke-base+x25519+hkdf-sha256' and
            init['combiner'] == 'e2e-x25519-hkdf-v1' and
            len(decode_b64url(init['enc'])) == 32 and
            len(decode_b64url(init['ephC'])) == 32,
            'initiation payload shape only')
    req_signed = dict(req_body)
    del req_signed['signature']
    req_input = b'sage-wire-request|0.10.0\n' + jcs_subset(req_signed)
    require(data['wire_request_signature_input_ascii'].encode('ascii') == req_input,
            'wire request signature input')
    verify_ed25519(req_input, req_body['signature'],
                   keys['initiator']['public_spki_der_b64'], 'wire request')
    check_http_request(request, req_body, keys['initiator'])

    check_common(res_body, keys['responder']['did'], keys['initiator']['did'],
                 keys['responder'], now)
    require(set(res_body) == {
        'version', 'id', 'did', 'recipient', 'kid', 'created', 'expires',
        'nonce', 'encoding', 'signature', 'context_id', 'role',
        'message_id', 'request_hash', 'success', 'data', 'error',
    } and res_body['id'] != req_body['id'] and
            res_body['nonce'] != req_body['nonce'] and
            res_body['context_id'] == req_body['context_id'] and
            res_body['role'] == 'responder' and
            res_body['message_id'] == req_body['id'] and
            res_body['request_hash'] == b64url(hashlib.sha256(jcs_subset(req_body)).digest()) and
            res_body['success'] is False and
            res_body['error'] == 'unavailable' and res_body['data'] == '',
            'response/request binding')
    res_signed = dict(res_body)
    del res_signed['signature']
    res_input = b'sage-wire-response|0.10.0\n' + jcs_subset(res_signed)
    require(data['wire_response_signature_input_ascii'].encode('ascii') == res_input,
            'wire response signature input')
    verify_ed25519(res_input, res_body['signature'],
                   keys['responder']['public_spki_der_b64'], 'wire response')
    check_http_response(request, response, res_body, keys['responder'])
    return {'wire_signatures_verified': 2, 'http_signatures_verified': 2,
            'implementation_conformance': 'NOT_ESTABLISHED'}


def verify(root=ROOT):
    raw = (root / FIXTURE).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == EXPECTED_FIXTURE_SHA256,
            'fixture bytes')
    return verify_data(root, parse_json(raw))


if __name__ == '__main__':
    print(json.dumps(verify(), sort_keys=True))
