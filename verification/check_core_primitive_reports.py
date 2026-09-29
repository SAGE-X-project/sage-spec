"""Audit current-core JCS/signature reports without promoting primitive passes."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
INSPECTOR_REVISION = 'f104c8c3ce072e7a64d5a0092623e45ffb8d287b'
SUITE_SHA256 = '8b7b202db497bb40a65b64f62a4afc0a3bd0a24b624fd76557d69f4b211bdd26'
SUBJECTS = {
    'go': {
        'report_sha256': '1420e0507771052095135203ae33f43fdabd6bbf0e6f1e2fdc5e5598e33b0de7',
        'revision': '49379baadc6baec9ca8b4bb7d15bf43d65144bd7',
        'executable_sha256': 'd38bb983ec644e001637336529ced4104d4117fd18aad0ea3665df556935a1bd',
        'counts': {'PASS': 27, 'FAIL': 18, 'UNSUPPORTED': 2, 'NOT_RUN': 0},
        'unsupported': {'p256-compressed-key', 'secp256k1-compressed-key'},
        'fail': {
            'jcs-duplicate', 'jcs-escaped-duplicate', 'jcs-surrogate',
            'jcs-negative-zero', 'jcs-negative-decimal-zero', 'jcs-negative-underflow',
            'ed25519-identity-A', 'ed25519-identity-R',
            'ed25519-mixed-A', 'ed25519-mixed-R', 'p256-high-s', 'p256-der',
            'secp256k1-high-s', 'secp256k1-der', 'secp256k1-truncated',
            'secp256k1-wrong-recovery', 'secp256k1-recovery-2',
            'secp256k1-recovery-27',
        },
    },
    'rust': {
        'report_sha256': '9b7a24695db2a5a9e6639b77cb3bbe4ebee6e257ca9842a6bbe0a5fd308b5500',
        'revision': 'ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396',
        'executable_sha256': '5d99976690b31cfd173fb204d39eb0525fb0d644a10584b50a93260734c5af92',
        'counts': {'PASS': 31, 'FAIL': 16, 'UNSUPPORTED': 0, 'NOT_RUN': 0},
        'unsupported': set(),
        'fail': {
            'jcs-negative-zero', 'jcs-negative-decimal-zero', 'jcs-negative-underflow',
            'ed25519-identity-A', 'ed25519-identity-R',
            'ed25519-mixed-A', 'ed25519-mixed-R', 'p256-high-s', 'p256-der',
            'p256-compressed-key', 'secp256k1-high-s', 'secp256k1-der',
            'secp256k1-compressed-key', 'secp256k1-truncated',
            'secp256k1-wrong-recovery', 'secp256k1-recovery-2',
        },
    },
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check(inspector_root):
    revision = subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=inspector_root, text=True).strip()
    require(revision == INSPECTOR_REVISION, 'Inspector revision')
    raw = (inspector_root / 'vectors/0.10.0/jcs-signatures.json').read_bytes()
    require(hashlib.sha256(raw).hexdigest() == SUITE_SHA256, 'fixture bytes')
    suite = json.loads(raw)
    require(len(suite['cases']) == 47, 'fixture case count')
    for name, expected in SUBJECTS.items():
        report_bytes = (ROOT / 'verification/evidence' /
                        f'core-jcs-crypto-{name}.json').read_bytes()
        require(hashlib.sha256(report_bytes).hexdigest() == expected['report_sha256'],
                name + ' raw report bytes')
        report = json.loads(report_bytes)
        require(report['schema_version'] == 1 and
                report['protocol_version'] == suite['protocol_version'] and
                report['profile'] == suite['profile'] and
                report['suite_id'] == suite['id'] and
                report['suite_sha256'] == SUITE_SHA256 and
                report['sources'] == suite['sources'] and
                report['status'] == 'FAIL' and
                report['counts'] == expected['counts'] and
                report['subject']['revision'] == expected['revision'] and
                report['subject']['executable_sha256'] == expected['executable_sha256'] and
                len(report['results']) == len(suite['cases']), name + ' report identity')
        for case, result in zip(suite['cases'], report['results']):
            case_id = case['id']
            status = ('FAIL' if case_id in expected['fail'] else
                      'UNSUPPORTED' if case_id in expected['unsupported'] else 'PASS')
            require(result['case_id'] == case_id and
                    result['operation'] == case['operation'] and
                    result['rule_ids'] == case['rule_ids'] and
                    result['source_ids'] == case['source_ids'] and
                    result['expected'] == case['expected'] and
                    result['actual']['case_id'] == case_id and
                    result['actual']['schema_version'] == 1 and
                    result['status'] == status, name + ' case ' + case_id)
            if status == 'PASS':
                require(result['actual']['verdict'] == case['expected']['verdict'] and
                        result['actual']['output'] == case['expected']['output'],
                        name + ' pass ' + case_id)
            elif status == 'UNSUPPORTED':
                require(result['actual']['verdict'] == 'UNSUPPORTED',
                        name + ' unsupported ' + case_id)
            else:
                require(result['actual']['verdict'] != case['expected']['verdict'] or
                        result['actual']['output'] != case['expected']['output'],
                        name + ' failure ' + case_id)
    return {name: data['counts'] for name, data in SUBJECTS.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inspector-root', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(check(args.inspector_root), sort_keys=True))


if __name__ == '__main__':
    main()
