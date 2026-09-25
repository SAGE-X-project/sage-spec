"""Check the ADOPT-06 review package without treating preparation as review."""

import argparse
import hashlib
import json
from pathlib import Path

from check_mcp_evidence_adoption import verify as verify_evidence
from review_target import pinned_path as reviewed_path


ROOT = Path(__file__).resolve().parents[1]
TARGET = 'd86ca1a4d326d6090e50d100b834d38ec204a2c2'
INSPECTOR = '58cffde89e45096b12d834fb562ea856d46b1c0b'
SOURCES = {
    'profiles/non-http-mcp-security.md',
    'profiles/non-http-mcp-tool.json',
    'profiles/agent-mcp-security.md',
    'spec/01-crypto.md',
    'spec/03-rfc9421.md',
    'spec/04-hpke.md',
    'spec/05-session.md',
    'spec/08-transport.md',
    'spec/09-registry.md',
    'verification/traceability.json',
    'verification/inspector-plan.md',
    'verification/standards.md',
    'verification/standards-revision-decisions.md',
    'verification/post-adoption-errata-review.md',
    'verification/mcp-evidence-adoption.json',
    'verification/mcp-evidence-adoption.md',
    'verification/mcp-errata-adoption.json',
    'verification/spec-revision-adoption.json',
}
AREAS = [
    'cryptographic-key-and-signature-role-separation',
    'outer-signature-aead-and-message-correlation',
    'setup-state-machine-and-fixed-acknowledgement',
    'output-publication-and-callback-ordering',
    'protected-call-admission-and-close-ordering',
    'deadlines-replay-recovery-and-resource-exhaustion',
    'trusted-agent-host-registry-and-component-boundaries',
    'excluded-transports-and-version-compatibility',
]


def require(condition, label):
    if not condition:
        raise ValueError(label)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_record(root, record):
    require(set(record) == {
        'schema_version', 'kind', 'protocol_version', 'finding', 'status',
        'external_audit', 'reviewer', 'review_report', 'conformance',
        'release_claim', 'target_repository', 'target_revision',
        'inspector_revision', 'target_sha256', 'review_areas', 'evidence_limits',
    }, 'package shape')
    require(record['schema_version'] == 1
            and record['kind'] == 'mcp-external-review-package'
            and record['protocol_version'] == '0.10.0'
            and record['finding'] == 'ADOPT-06'
            and record['status'] == 'READY_FOR_EXTERNAL_REVIEW'
            and record['external_audit'] == 'NOT_PERFORMED'
            and record['reviewer'] is None
            and record['review_report'] is None
            and record['conformance'] == 'NOT_ESTABLISHED'
            and record['release_claim'] is False,
            'external review or conformance promoted')
    require(record['target_repository'] == 'SAGE-X-project/sage-spec'
            and record['target_revision'] == TARGET
            and record['inspector_revision'] == INSPECTOR,
            'review target changed')
    require(set(record['target_sha256']) == SOURCES, 'target file inventory')
    for name, digest in record['target_sha256'].items():
        reviewed_path(root, name, digest)
    require(record['target_sha256']['verification/mcp-evidence-adoption.json']
            == 'f10d4b9457b28b475f786822c49d8706bd996ced9ced5df4efa4d7db778a75d9',
            'adoption evidence identity')
    require(record['review_areas'] == AREAS, 'review scope changed')
    require(record['evidence_limits'] == {
        'old_binding_overlay_parent_pass': 71,
        'later_spec_cases_not_run': 14,
        'deployed_agent_host': 'NOT_RUN',
        'live_registry_source': 'NOT_RUN',
        'ins11': 'INCOMPLETE',
    }, 'evidence limits promoted')
    document = (root / 'verification/mcp-external-review-package.md').read_text()
    require('READY_FOR_EXTERNAL_REVIEW' in document
            and 'NOT_PERFORMED' in document
            and 'NOT_ESTABLISHED' in document
            and TARGET in document and INSPECTOR in document
            and 'reviewer' in document.lower(),
            'review request text')
    return {'finding': 'ADOPT-06', 'status': 'READY_FOR_EXTERNAL_REVIEW',
            'external_audit': 'NOT_PERFORMED', 'conformance': 'NOT_ESTABLISHED'}


def verify(root=ROOT, inspector_root=None):
    verify_evidence(root, inspector_root)
    record = json.loads((root / 'verification/mcp-external-review-package.json').read_text())
    return verify_record(root, record)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--inspector-root', type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.root, args.inspector_root)
    except (ValueError, KeyError, OSError, TypeError) as error:
        parser.exit(1, 'MCP external review package check FAIL: ' + str(error) + '\n')
    print('MCP external review package PASS: ' + json.dumps(result, sort_keys=True))
