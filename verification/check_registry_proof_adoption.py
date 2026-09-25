"""Validate the registry proof correction and its preserved review target."""

import hashlib
import json
import re
from pathlib import Path

from check_mcp_independent_llm_review import verify as verify_review
from check_registry_proof_revision import verify as verify_fixture


ROOT = Path(__file__).resolve().parents[1]
OWNERS = {
    'mllm-kem-alg-valid': 'REG-01',
    'mllm-kem-alg-case': 'REG-01',
    'mllm-kem-selection': 'REG-02',
    'mllm-pop-exact-bytes': 'REG-04',
    'mllm-pop-duplicate-field': 'REG-04',
    'mllm-kem-signature-reject': 'TABLE-02',
    'mllm-kem-type-valid': 'TABLE-03',
    'mllm-kem-key-length': 'TABLE-03',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_record(root, record):
    require(record['schema_version'] == 1
            and record['kind'] == 'registry-proof-normative-correction'
            and record['protocol_version'] == '0.10.0'
            and record['status'] == 'NORMATIVE_CORRECTION_LLM_REREVIEWED'
            and record['prior_review_revision'] == 'cb02dbd8a773c88e7eb52956bade205f1bd871c8'
            and record['review_target_revision'] == 'd86ca1a4d326d6090e50d100b834d38ec204a2c2',
            'revision identity')
    require(record['prior_review_report'] == 'verification/mcp-independent-llm-review.json'
            and sha(root / record['prior_review_report']) == record['prior_review_report_sha256']
            and record['historical_snapshot_root'] == 'verification/history/llm-review-target-2026-09-25',
            'prior review provenance')
    old_files = {'spec/00-overview.md', 'spec/09-registry.md',
                 'spec/11-registries.md', 'verification/traceability.json',
                 'verification/inspector-plan.md', 'README.md', 'PROCESS.md',
                 'CHANGELOG.md'}
    require(set(record['historical_sha256']) == old_files
            and set(record['current_sha256']) == old_files | {
                'verification/vectors/registry-proof-0.10.0.json',
                'verification/registry-proof-revision.md'}, 'revision source inventory')
    for name, digest in record['historical_sha256'].items():
        require(sha(root / record['historical_snapshot_root'] / name) == digest,
                'historical source: ' + name)
    for name, digest in record['current_sha256'].items():
        require(sha(root / name) == digest, 'current source: ' + name)
    require(record['finding_dispositions'] == {
        'LLM-01': 'CORRECTED_IN_TEXT_PENDING_REREVIEW',
        'LLM-02': 'CORRECTED_IN_TEXT_PENDING_REREVIEW',
    } and record['independent_rereview'] == 'FRESH_CONTEXT_LLM_NO_NEW_FINDINGS'
            and record['reviewer'] == {
                'identity': 'Codex LLM in a fresh context',
                'affiliation': 'same service and workspace as the authoring agent',
                'organizationally_external': False,
                'method': 'read-only source and exact-byte fixture re-review',
                'scope': 'LLM-01 and LLM-02 normative correction, eight planned cases and local fixture',
                'first_pass': 'unobservable raw-key provenance claim corrected',
                'second_pass': 'no remaining concrete ambiguity found in scope',
                'limits': 'No formal analysis, live registration, full handshake, core or Inspector execution, host test, or third-party audit.',
            }
            and record['core_implementation'] == 'NOT_RUN'
            and record['inspector_revised_cases'] == 'NOT_RUN'
            and record['third_party_audit'] == 'NOT_PERFORMED'
            and record['conformance'] == 'NOT_ESTABLISHED'
            and record['release_or_tag_created'] is False,
            'evidence claim promoted')
    require(record['counts'] == {'rule_groups': 91, 'historical_parent_cases': 471,
                                 'new_parent_cases': 8, 'total_parent_cases': 479,
                                 'mandatory_children': 26}
            and record['new_case_ids'] == list(OWNERS), 'plan counts or cases')
    old = json.loads((root / record['historical_snapshot_root'] /
                      'verification/traceability.json').read_text())
    current = json.loads((root / 'verification/traceability.json').read_text())
    require(old['protocol_version'] == current['protocol_version'] == '0.10.0'
            and old['status'] == current['status'] == 'verification_plan_not_executed'
            and old['requirements'] == current['requirements']
            and old['mandatory_subscenarios'] == current['mandatory_subscenarios']
            and old['binding_adoption'] == current['binding_adoption']
            and len(old['rules']) == len(current['rules']) == 91
            and len(old['cases']) == 471 and len(current['cases']) == 479,
            'plan baseline')
    old_cases = {case['id']: case for case in old['cases']}
    cases = {case['id']: case for case in current['cases']}
    require(len(cases) == 479 and set(cases) == set(old_cases) | set(OWNERS)
            and all(cases[name] == case for name, case in old_cases.items()),
            'historical case mutation')
    old_rules = {rule['id']: rule for rule in old['rules']}
    rules = {rule['id']: rule for rule in current['rules']}
    require(set(rules) == set(old_rules), 'rule membership')
    for name, rule in rules.items():
        prior = old_rules[name]
        stable = lambda value: {key: item for key, item in value.items()
                                if key not in ('line', 'case_ids')}
        require(stable(rule) == stable(prior)
                and rule['case_ids'] == prior['case_ids']
                + [case_id for case_id, owner in OWNERS.items() if owner == name],
                'rule mapping: ' + name)
        lines = (root / rule['source']).read_text().splitlines()
        found = [number for number, line in enumerate(lines, 1)
                 if (line.startswith('#') and re.search(r'\b' + re.escape(name) + r'\b', line))
                 or re.match(r'^\*\*' + re.escape(name) + r'\b', line)]
        require(found and rule['line'] == found[0], 'current rule location: ' + name)
    for name, owner in OWNERS.items():
        case = cases[name]
        require(case['rule_id'] == owner
                and case['mode'] == 'unit_and_bounded_local_runtime'
                and case['evidence_status'] == 'planned_not_executed'
                and all(case[key] for key in ('input', 'preconditions', 'expected')),
                'new case plan: ' + name)
    overview = (root / 'spec/00-overview.md').read_text()
    registry = (root / 'spec/09-registry.md').read_text()
    tables = (root / 'spec/11-registries.md').read_text()
    require('only the 16-bit unsigned big-endian byte length' in overview
            and 'each field appears\nexactly once after its length' in registry
            and 'For a registry X25519 key, the exact `alg` value is lowercase ASCII `x25519`' in tables
            and 'MUST NOT appear as a message\nsignature `alg`' in tables,
            'normative correction text')
    return {'status': record['status'], 'rules': 91, 'parent_cases': 479,
            'new_cases': 8, 'conformance': 'NOT_ESTABLISHED'}


def verify(root=ROOT, inspector_root=None):
    verify_review(root, inspector_root)
    verify_fixture(root)
    record = json.loads((root / 'verification/registry-proof-revision.json').read_text())
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
        parser.exit(1, 'Registry proof correction check FAIL: ' + str(error) + '\n')
    print('Registry proof correction PASS: ' + json.dumps(result, sort_keys=True))
