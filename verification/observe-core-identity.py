"""Record bounded, benign DID parser observations from pinned core adapters."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import build_core_gap_index as INDEX

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'verification/identity-parser-observations.json'
CASES = [
    ('canonical-web', 'did:sage:web:agents.example.com:alice', 'ACCEPT'),
    ('legacy-alias', 'did:sage:ETH:0xabc', 'REJECT'),
    ('legacy-chain', 'did:sage:ethereum:0xabc', 'REJECT'),
    ('extra-locator', 'did:sage:ethereum:0xabc:extra', 'REJECT'),
    ('fragment-in-did', 'did:sage:ethereum:0xabc#key-1', 'REJECT'),
    ('uppercase-scheme', 'DID:sage:web:agents.example.com:alice', 'REJECT'),
]
EXPECTED_ACTUAL = ['REJECT', 'ACCEPT', 'ACCEPT', 'ACCEPT', 'ACCEPT', 'REJECT']
ADAPTER_HASHES = {
    'go': 'd38bb983ec644e001637336529ced4104d4117fd18aad0ea3665df556935a1bd',
    'rust': '5d99976690b31cfd173fb204d39eb0525fb0d644a10584b50a93260734c5af92',
}


def request(case_id, did):
    return {
        'schema_version': 1, 'protocol_version': '0.10.0',
        'profile': 'primitive-foundation', 'case_id': case_id,
        'operation': 'sage.did.validate',
        'input': {'did': did, 'supported_kinds': ['eip155', 'web']},
    }


def observe(name, path):
    revision = INDEX.GO_REVISION if name == 'go' else INDEX.RUST_REVISION
    rows = []
    for case_id, did, expected in CASES:
        process = subprocess.run(
            [str(path)], input=json.dumps(request(case_id, did)),
            text=True, capture_output=True, timeout=10, check=True)
        actual = json.loads(process.stdout)
        if actual['case_id'] != case_id or actual['schema_version'] != 1:
            raise ValueError(name + ' adapter identity mismatch')
        rows.append({'id': case_id, 'did': did, 'expected': expected,
                     'actual': actual['verdict'],
                     'status': 'PASS' if actual['verdict'] == expected else 'FAIL'})
    return {'revision': revision,
            'adapter_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'observations': rows}


def report(go, rust):
    return {'schema_version': 1, 'spec_revision': INDEX.SPEC_REVISION,
            'scope': 'Legacy primitive DID entry point; not a full identity or host verdict.',
            'subjects': {'go': observe('go', go), 'rust': observe('rust', rust)}}


def check(data):
    if (data['schema_version'] != 1 or
            data['spec_revision'] != INDEX.SPEC_REVISION or
            data['scope'] != 'Legacy primitive DID entry point; not a full identity or host verdict.'):
        raise ValueError('specification identity changed')
    if set(data['subjects']) != {'go', 'rust'}:
        raise ValueError('subject set changed')
    for name, subject in data['subjects'].items():
        revision = INDEX.GO_REVISION if name == 'go' else INDEX.RUST_REVISION
        if (subject['revision'] != revision or
                subject['adapter_sha256'] != ADAPTER_HASHES[name]):
            raise ValueError(name + ' core identity changed')
        rows = subject['observations']
        if len(rows) != len(CASES):
            raise ValueError(name + ' case count changed')
        for row, (case_id, did, expected), actual in zip(rows, CASES, EXPECTED_ACTUAL):
            if row != {'id': case_id, 'did': did, 'expected': expected,
                       'actual': actual,
                       'status': 'PASS' if actual == expected else 'FAIL'}:
                raise ValueError(name + ' bounded verdict changed')
    return {'cases_per_core': len(CASES), 'failed_per_core': 5,
            'passed_per_core': 1}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--go-adapter', type=Path)
    parser.add_argument('--rust-adapter', type=Path)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    if args.write:
        if not args.go_adapter or not args.rust_adapter:
            parser.error('--write requires both adapters')
        OUTPUT.write_text(json.dumps(report(args.go_adapter, args.rust_adapter), indent=2) + '\n')
    print(json.dumps(check(json.loads(OUTPUT.read_bytes())), sort_keys=True))


if __name__ == '__main__':
    main()
