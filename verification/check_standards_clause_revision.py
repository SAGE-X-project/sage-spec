"""Verify the current standards clauses and preserved historical inputs."""

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = 'verification/history/standards-clauses-base-2026-09-29'
NEW_OWNERS = {
    'msca-http-ed25519': 'MSG-01',
    'msca-http-p256': 'MSG-01',
    'msca-http-private-alg': 'MSG-01',
    'msca-http-only-private-key': 'TRANSPORT-05',
    'msca-http-no-substitution': 'TRANSPORT-05',
    'msca-did-prefix-case': 'ID-01',
    'msca-did-url-prefix-case': 'ID-01',
    'msca-private-suite-non-http-scope': 'TABLE-02',
}
CURRENT_PATHS = {
    '.github/workflows/check.yml', 'README.md', 'PROCESS.md', 'CHANGELOG.md',
    'guides/integration.md',
    'spec/00-overview.md', 'spec/01-crypto.md', 'spec/03-rfc9421.md',
    'spec/06-did-sage.md', 'spec/08-transport.md', 'spec/10-resolution.md',
    'spec/11-registries.md', 'verification/standards-application-matrix.md',
    'verification/traceability.json', 'verification/inspector-plan.md',
    'verification/standards-clause-revision.md',
    'analysis/build-current-design-overlay.py',
    'analysis/current-design-overlay.json', 'analysis/current-design-overlay.md',
}


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_current_sources(root=ROOT, record=None):
    """Current-source gate; historical checks must never replace this call."""
    if record is None:
        record = json.loads((root / 'verification/standards-clause-revision.json').read_text())
    require(set(record['current_sha256']) == CURRENT_PATHS, 'current source inventory')
    for name, digest in record['current_sha256'].items():
        require(sha(root / name) == digest, 'current source bytes: ' + name)
    return record


def verify(root=ROOT):
    record = verify_current_sources(root)
    require(record['schema_version'] == 1
            and record['kind'] == 'standards-clause-normative-revision'
            and record['protocol_version'] == '0.10.0'
            and record['base_revision'] == 'e24994324fe11c526c717d805a512623c7d26d61'
            and record['status'] == 'AMENDED_NORMATIVE_DESIGN_PENDING_EXECUTION'
            and record['historical_snapshot_root'] == SNAPSHOT,
            'revision identity')
    require(record['prior_audit'] == 'verification/standards-clause-audit.md'
            and sha(root / record['prior_audit']) == record['prior_audit_sha256']
            and record['prior_standards_scope_record'] ==
            'verification/standards-scope-revision.json'
            and sha(root / record['prior_standards_scope_record']) ==
            record['prior_standards_scope_record_sha256'],
            'prior review provenance')
    require(record['counts'] == {'requirements': 45, 'rule_groups': 91,
                                 'historical_parent_cases': 481,
                                 'new_parent_cases': 8,
                                 'total_parent_cases': 489,
                                 'mandatory_children': 26}
            and record['new_case_ids'] == list(NEW_OWNERS),
            'case counts or membership')
    require(record['core_implementation'] == 'NOT_RUN'
            and record['inspector_new_cases'] == 'NOT_RUN'
            and record['external_audit'] == 'NOT_PERFORMED'
            and record['conformance'] == 'NOT_ESTABLISHED'
            and record['release_or_tag_created'] is False,
            'unsupported evidence promotion')

    from check_mcp_independent_llm_rereview import SOURCE_PATHS
    old_scope = json.loads((root / record['prior_standards_scope_record']).read_text())
    llm = json.loads((root / 'verification/mcp-independent-llm-rereview.json').read_text())
    historical = record['historical_sha256']
    require(set(historical) == set(old_scope['current_sha256']) | SOURCE_PATHS,
            'historical source inventory')
    for name, digest in historical.items():
        require(sha(root / SNAPSHOT / name) == digest,
                'historical source bytes: ' + name)
    for name, digest in old_scope['current_sha256'].items():
        require(historical[name] == digest, 'prior standards source: ' + name)
    for name, digest in llm['source_sha256'].items():
        require(historical[name] == digest, 'prior LLM review source: ' + name)

    previous = json.loads((root / SNAPSHOT / 'verification/traceability.json').read_text())
    current = json.loads((root / 'verification/traceability.json').read_text())
    require(previous['protocol_version'] == current['protocol_version'] == '0.10.0'
            and previous['status'] == current['status'] == 'verification_plan_not_executed'
            and previous['requirements'] == current['requirements']
            and previous['mandatory_subscenarios'] == current['mandatory_subscenarios']
            and previous['binding_adoption'] == current['binding_adoption']
            and previous['binding_required_observations'] ==
                current['binding_required_observations']
            and len(previous['rules']) == len(current['rules']) == 91
            and len(previous['cases']) == 481 and len(current['cases']) == 489,
            'plan baseline')
    old_cases = {case['id']: case for case in previous['cases']}
    new_cases = {case['id']: case for case in current['cases']}
    require(len(old_cases) == 481 and len(new_cases) == 489
            and set(new_cases) == set(old_cases) | set(NEW_OWNERS)
            and all(new_cases[name] == case for name, case in old_cases.items()),
            'historical case mutation')
    old_rules = {rule['id']: rule for rule in previous['rules']}
    new_rules = {rule['id']: rule for rule in current['rules']}
    require(set(old_rules) == set(new_rules), 'rule inventory')
    for name, rule in new_rules.items():
        old = old_rules[name]
        require({k: v for k, v in rule.items() if k not in ('line', 'case_ids')} ==
                {k: v for k, v in old.items() if k not in ('line', 'case_ids')},
                'historical rule mutation: ' + name)
        added = [case_id for case_id, owner in NEW_OWNERS.items() if owner == name]
        require(rule['case_ids'] == old['case_ids'] + added,
                'rule case mapping: ' + name)
        source = (root / rule['source']).read_text().splitlines()
        require(1 <= rule['line'] <= len(source)
                and name in source[rule['line'] - 1],
                'current rule anchor: ' + name)
    for name, owner in NEW_OWNERS.items():
        case = new_cases[name]
        require(case['rule_id'] == owner
                and case['mode'] == 'unit_and_bounded_local_runtime'
                and case['evidence_status'] == 'planned_not_executed'
                and all(case[key] for key in ('input', 'preconditions', 'expected')),
                'new case plan: ' + name)

    http = (root / 'spec/03-rfc9421.md').read_text()
    did = (root / 'spec/06-did-sage.md').read_text()
    jwk = (root / 'spec/10-resolution.md').read_text()
    transport = (root / 'spec/08-transport.md').read_text()
    registry = (root / 'spec/11-registries.md').read_text()
    report = (root / 'verification/standards-clause-revision.md').read_text()
    require('`alg` MUST be exactly `ed25519` or' in http
            and '`ecdsa-p256-sha256`' in http
            and 'private' in http and 'No other key' in http
            and '%s"did:sage:"' in did and 'id.malformed' in did
            and 'RFC 7405' in did and 'RFC 8812' in jwk
            and 'ES256K' in jwk and 'secp256k1/Keccak signing key' in transport
            and 'HTTP `alg`' in registry
            and all(mark in report for mark in
                    ('SCA-01', 'SCA-02', 'SCA-03', 'NOT_ESTABLISHED',
                     'NOT_PERFORMED', '489')),
            'normative decision or evidence limits')
    graph = json.loads((root / 'analysis/current-design-overlay.json').read_text())
    require(graph['traceability']['planned_cases'] == 489
            and graph['traceability']['sha256'] ==
            record['current_sha256']['verification/traceability.json'],
            'current graph source')
    return {'rule_groups': 91, 'planned_cases': 489,
            'new_cases': 8, 'conformance': 'NOT_ESTABLISHED'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        result = verify(args.root)
    except (ValueError, KeyError, OSError, TypeError) as error:
        parser.exit(1, 'Standards clause revision FAIL: ' + str(error) + '\n')
    print('Standards clause revision PASS: ' + json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
