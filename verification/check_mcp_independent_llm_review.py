"""Validate the scoped ADOPT-06 LLM review without promoting its claims."""

import json
from pathlib import Path

from check_mcp_external_review_package import ROOT, TARGET, verify as verify_package
from review_target import pinned_path as reviewed_path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify_record(root, record):
    require(record['schema_version'] == 1
            and record['kind'] == 'mcp-independent-llm-review'
            and record['finding'] == 'ADOPT-06'
            and record['protocol_version'] == '0.10.0'
            and record['target_revision'] == TARGET
            and record['review_package'] == 'verification/mcp-external-review-package.json',
            'review identity')
    require(record['status'] == 'REVIEWED_WITH_OPEN_FINDINGS'
            and record['organizationally_external'] is False
            and record['third_party_audit'] == 'NOT_PERFORMED'
            and record['implementation_conformance'] == 'NOT_ESTABLISHED'
            and record['release_claim'] is False,
            'review claim promoted')
    reviewers = record['reviewers']
    require([r['id'] for r in reviewers] == ['LLM-MCP', 'LLM-CRYPTO']
            and all('same service and workspace' in r['affiliation'] for r in reviewers)
            and all(r['conflict'] == 'not organizationally independent' for r in reviewers)
            and reviewers[0]['finding_ids'] == []
            and reviewers[1]['finding_ids'] == ['LLM-01', 'LLM-02'],
            'reviewer identity or conflict')
    package = json.loads((root / record['review_package']).read_text())
    require(set(reviewers[0]['hash_checked_paths']).issubset(package['target_sha256']),
            'reviewer scope')
    supplemental = record['supplemental_target_sha256']
    require(supplemental == {
        'spec/00-overview.md': '26731b6d91994677548cff3efabfb0f5d9406de53b4e030bfb637f28137e8a85',
        'spec/11-registries.md': '668a2c0ccf51651463829d4de80bce4206231f48c3860f6a195f9380f1c14a4b',
    }, 'supplemental target identity')
    for name, digest in supplemental.items():
        reviewed_path(root, name, digest)
    require([f['id'] for f in record['findings']] == ['LLM-01', 'LLM-02']
            and [f['severity'] for f in record['findings']] == ['medium', 'high']
            and all(f['status'] == 'OPEN_NORMATIVE' for f in record['findings']),
            'open normative findings')
    for finding in record['findings']:
        require(all((root / anchor.split(':')[0]).is_file()
                    for anchor in finding['anchors'])
                and all(finding[key] for key in ('trigger', 'ambiguity', 'consequence', 'correction')),
                'finding evidence')
    document = (root / 'verification/mcp-independent-llm-review.md').read_text()
    require(all(term in document for term in (
        TARGET, 'REVIEWED_WITH_OPEN_FINDINGS', 'LLM-01', 'LLM-02',
        'NOT_PERFORMED', 'NOT_ESTABLISHED', 'not\nan organizationally independent',
    )), 'review report claim or linkage')
    return {'finding': 'ADOPT-06', 'status': record['status'],
            'open_findings': [f['id'] for f in record['findings']]}


def verify(root=ROOT, inspector_root=None):
    verify_package(root, inspector_root)
    record = json.loads((root / 'verification/mcp-independent-llm-review.json').read_text())
    return verify_record(root, record)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--inspector-root', type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.root, args.inspector_root)
    except (ValueError, KeyError, OSError, TypeError) as error:
        parser.exit(1, 'MCP independent LLM review check FAIL: ' + str(error) + '\n')
    print('MCP independent LLM review PASS: ' + json.dumps(result, sort_keys=True))
