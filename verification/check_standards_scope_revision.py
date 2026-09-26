"""Check the 0.10.0 standards-scope snapshot without claiming conformance."""

import argparse
import hashlib
import json
from pathlib import Path

from check_registry_proof_adoption import verify_record as verify_prior_record


ROOT = Path(__file__).resolve().parents[1]
NEW_CASES = {
    'mstand-problem-fields': 'unit_and_bounded_local_runtime',
    'mstand-problem-type-publication': 'deployment_or_document_review',
}


def require(condition, label):
    if not condition:
        raise ValueError(label)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(root=ROOT):
    record = json.loads((root / 'verification/standards-scope-revision.json').read_text())
    prior_path = root / record['prior_record']
    prior = json.loads(prior_path.read_text())
    verify_prior_record(root, prior)
    require(record['schema_version'] == 1
            and record['kind'] == 'standards-application-normative-clarification'
            and record['protocol_version'] == '0.10.0'
            and record['status'] == 'DESIGN_REVIEWED_PENDING_EXECUTION'
            and record['base_revision'] == 'bdbe5598c2cf63dada68c6939cfdeb28073cf71f'
            and record['prior_record'] == 'verification/registry-proof-revision.json'
            and sha(prior_path) == record['prior_record_sha256']
            and record['prior_source_snapshot_root'] ==
            'verification/history/registry-proof-2026-09-26',
            'revision provenance')
    require(record['counts'] == {'rule_groups': 91, 'historical_parent_cases': 479,
                                 'new_parent_cases': 2, 'total_parent_cases': 481,
                                 'mandatory_children': 26}
            and record['new_case_ids'] == list(NEW_CASES), 'case count or membership')
    require(record['core_implementation'] == 'NOT_RUN'
            and record['inspector_new_cases'] == 'NOT_RUN'
            and record['problem_type_publication'] == 'NOT_VERIFIED'
            and record['external_audit'] == 'NOT_PERFORMED'
            and record['conformance'] == 'NOT_ESTABLISHED'
            and record['release_or_tag_created'] is False,
            'unsupported evidence promotion')
    expected_files = {'spec/00-overview.md', 'spec/10-resolution.md',
                      'verification/standards.md',
                      'verification/standards-application-matrix.md',
                      'verification/traceability.json',
                      'verification/inspector-plan.md', 'README.md',
                      'PROCESS.md', 'CHANGELOG.md',
                      'verification/check_registry_proof_adoption.py'}
    require(set(record['current_sha256']) == expected_files, 'source inventory')
    for name, digest in record['current_sha256'].items():
        require(sha(root / name) == digest, 'current source: ' + name)

    previous = json.loads((root / record['prior_source_snapshot_root'] /
                           'verification/traceability.json').read_text())
    current = json.loads((root / 'verification/traceability.json').read_text())
    require(previous['protocol_version'] == current['protocol_version'] == '0.10.0'
            and previous['status'] == current['status'] == 'verification_plan_not_executed'
            and previous['requirements'] == current['requirements']
            and previous['mandatory_subscenarios'] == current['mandatory_subscenarios']
            and previous['binding_adoption'] == current['binding_adoption']
            and len(previous['rules']) == len(current['rules']) == 91
            and len(previous['cases']) == 479 and len(current['cases']) == 481,
            'plan baseline')
    prior_cases = {case['id']: case for case in previous['cases']}
    cases = {case['id']: case for case in current['cases']}
    require(len(cases) == 481 and set(cases) == set(prior_cases) | set(NEW_CASES)
            and all(cases[name] == case for name, case in prior_cases.items()),
            'historical case mutation')
    prior_rules = {rule['id']: rule for rule in previous['rules']}
    rules = {rule['id']: rule for rule in current['rules']}
    require(set(rules) == set(prior_rules), 'rule membership')
    for name, rule in rules.items():
        old = prior_rules[name]
        require({k: v for k, v in rule.items() if k != 'case_ids'} ==
                {k: v for k, v in old.items() if k != 'case_ids'},
                'historical rule mutation: ' + name)
        expected = old['case_ids'] + (list(NEW_CASES) if name == 'RESOLVE-05' else [])
        require(rule['case_ids'] == expected, 'rule case mapping: ' + name)
    for name, mode in NEW_CASES.items():
        case = cases[name]
        require(case['rule_id'] == 'RESOLVE-05' and case['mode'] == mode
                and case['evidence_status'] == 'planned_not_executed'
                and all(case[key] for key in ('input', 'preconditions', 'expected')),
                'new case plan: ' + name)

    overview = (root / 'spec/00-overview.md').read_text()
    resolution = (root / 'spec/10-resolution.md').read_text()
    matrix = (root / 'verification/standards-application-matrix.md').read_text()
    require('DID Resolution Candidate Recommendation Draft, 28 August 2026' in overview
            and '2026/CRD-did-resolution-1.0-20260828/' in overview
            and 'HTTP response status MUST equal' in resolution
            and 'Publication is not established' in matrix,
            'standards scope or publication claim')
    return {'rules': 91, 'parent_cases': 481, 'new_cases': 2,
            'conformance': 'NOT_ESTABLISHED'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        result = verify(args.root)
    except (ValueError, KeyError, OSError, TypeError) as error:
        parser.exit(1, 'Standards scope check FAIL: ' + str(error) + '\n')
    print('Standards scope check PASS: ' + json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
