"""Check the versioned REG-03/REG-08 operator design adoption record."""

import hashlib
import json
from pathlib import Path

from check_web_registry_media_contract import verify as verify_media


ROOT = Path(__file__).resolve().parents[1]
RECORD = 'verification/registry-operator-adoption.json'
VECTOR = 'verification/vectors/registry-operator-0.10.0.json'
HISTORY = 'verification/history/registry-operator-base-2026-10-01'
SPEC = 'spec/09-registry.md'
OVERLAY = 'analysis/current-design-overlay.json'
TRACE = 'verification/traceability.json'
CANDIDATE = 'proposals/registry-operator-transaction/README.md'
EXPECTED = {
    'controller-grant': ('REG-03-P', 'ACCEPT_ONE_VERSION_AND_GRANT'),
    'exact-scope-write': ('REG-03-P', 'ACCEPT_ONE_NAMED_TRANSITION'),
    'controller-revoke': ('REG-03-P', 'ACCEPT_ONE_VERSION_AND_REMOVE_ONLY_TARGET'),
    'state-retirement': ('REG-03-P', 'ACCEPT_ONE_VERSION_AND_RETIRE_INELIGIBLE'),
    'explicit-regrant': ('REG-03-P', 'ACCEPT_ONE_VERSION_AND_GRANT'),
    'expired-key-management': ('REG-03-P', 'ACCEPT_MANAGEMENT_ONLY_NO_MESSAGE_AUTHORITY'),
    'duplicate-or-missing-grant': ('REG-03-P', 'REJECT_UNCHANGED'),
    'grant-capacity': ('REG-03-P', 'REJECT_UNCHANGED'),
    'stale-version': ('REG-03-N01', 'REJECT_UNCHANGED'),
    'competing-commands': ('REG-03-N02', 'ONE_COMMIT_OTHER_STALE_BY_LINEARIZATION'),
    'uncertain-commit': ('REG-03-N02', 'QUARANTINE_NO_SUCCESS_CLAIM'),
    'restart-history': ('REG-03-N02', 'RECOVER_EXACT_VERSION_AND_GRANTS'),
    'deactivated-management': ('REG-03-N03', 'REJECT_UNCHANGED'),
    'operator-delegates': ('REG-03-N04', 'REJECT_UNCHANGED'),
    'scope-or-identity-mismatch': ('REG-03-N04', 'REJECT_UNCHANGED'),
    'public-read-atomicity': ('REG-08-P', 'COMPLETE_OLD_OR_NEW_RECORD'),
    'storage-authority-loss': ('REG-08-N03', 'NO_CONFORMANCE_OR_SUCCESS_CLAIM'),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(root=ROOT):
    record = json.loads((root / RECORD).read_text())
    require(record == {
        'schema_version': 1,
        'kind': 'registry-operator-normative-clarification',
        'protocol_version': '0.10.0',
        'base_revision': 'd07fcd2ac38ea6519394a10c390db55bed993cfd',
        'status': 'NORMATIVE_DESIGN_PENDING_EXECUTION',
        'historical_root': HISTORY,
        'historical_spec_sha256': '828ce810f851c42ab8da76bbc5cfa1cc61fa523ce197b9f784f4aba0a0b345a9',
        'historical_overlay_sha256': '4951d79d94417533083b0ce6d9d86562a002275730a5f99a857a262cde318e9a',
        'current_spec_sha256': 'e8572cc037fd0fc84e678be436cc47854c5fd700aacbc141937d79ee03ea6017',
        'current_overlay_sha256': '483670d6ef23b01eef2304cd058d3b9f08c4680569e380ed20f2d18d54d3b585',
        'traceability_sha256': '410b1ffb7e6da0462d8c3b3ecae4ba6ed2a9c1f0bc14583fe4d17fa4d7ef5ba7',
        'candidate_sha256': '0bd2246185ca376e8d5331dd2d7e7d19cc3e86c6a22854f62f729b65c36b1b82',
        'subconditions_path': VECTOR,
        'subconditions_sha256': 'c79ecaa507b8d92e2847924f1e4a19330ecfc2749372bfaa99d5503fd023046b',
        'rule_groups': 91,
        'parent_cases': 489,
        'mandatory_children': 26,
        'new_subconditions': 17,
        'go_core_execution': 'NOT_RUN',
        'rust_core_execution': 'NOT_RUN',
        'registry_service_execution': 'NOT_RUN',
        'inspector_execution': 'NOT_RUN',
        'deployed_storage_observation': 'NOT_RUN',
        'external_audit': 'NOT_PERFORMED',
        'conformance': 'NOT_ESTABLISHED',
        'release_or_tag_created': False,
    }, 'adoption record shape or evidence claim')
    for path, digest in (
        (f'{HISTORY}/{SPEC}', record['historical_spec_sha256']),
        (f'{HISTORY}/{OVERLAY}', record['historical_overlay_sha256']),
        (SPEC, record['current_spec_sha256']),
        (OVERLAY, record['current_overlay_sha256']),
        (TRACE, record['traceability_sha256']),
        (CANDIDATE, record['candidate_sha256']),
        (VECTOR, record['subconditions_sha256']),
    ):
        require(sha(root / path) == digest, 'source bytes: ' + path)
    old = (root / HISTORY / SPEC).read_text()
    current = (root / SPEC).read_text()
    require('## 9. Operator transactions' not in old
            and '## 9. Operator transactions — REG-03 and REG-08' in current
            and '128 grants may be active' in current
            and 'Only the authenticated controller MAY authorize or revoke a grant' in current
            and 'Two commands using the same expected' in current
            and 'MUST quarantine further' in current
            and 'MUST recover grant and' in current,
            'normative operator clause')
    trace = json.loads((root / TRACE).read_text())
    rules = {item['id']: item for item in trace['rules']}
    cases = {item['id']: item for item in trace['cases']}
    require(len(trace['requirements']) == 45 and len(rules) == 91
            and len(cases) == 489 and len(trace['mandatory_subscenarios']) == 26,
            'traceability counts')
    for rule_id in ('REG-03', 'REG-08'):
        require(rules[rule_id]['source'] == SPEC
                and rules[rule_id]['evidence_status'] == 'planned_not_executed',
                'rule mapping: ' + rule_id)
    vectors = json.loads((root / VECTOR).read_text())
    require(set(vectors) == {'schema_version', 'kind', 'protocol_version', 'scope', 'cases'}
            and vectors['schema_version'] == 1
            and vectors['kind'] == 'registry-operator-transaction-subconditions'
            and vectors['protocol_version'] == '0.10.0'
            and 'no core, service, or deployment result' in vectors['scope'],
            'vector metadata')
    require(len(vectors['cases']) == 17
            and [item['id'] for item in vectors['cases']] == list(EXPECTED),
            'vector identities')
    for item in vectors['cases']:
        parent, verdict = EXPECTED[item['id']]
        require(set(item) == {'id', 'parent_case_id', 'precondition', 'expected', 'evidence_status'}
                and item['parent_case_id'] == parent
                and item['expected'] == verdict
                and isinstance(item['precondition'], str) and item['precondition'].strip()
                and item['evidence_status'] == 'planned_not_executed'
                and cases[parent]['rule_id'] == parent[:6]
                and parent in rules[parent[:6]]['case_ids']
                and cases[parent]['evidence_status'] == 'planned_not_executed',
                'vector mapping or claim: ' + item['id'])
    overlay = json.loads((root / OVERLAY).read_text())
    require(overlay['traceability']['sha256'] == record['traceability_sha256']
            and overlay['traceability']['planned_cases'] == 489
            and any(node.get('path') == SPEC
                    and node.get('sha256') == record['current_spec_sha256']
                    for node in overlay['nodes']), 'current overlay mapping')
    verify_media(root)
    return {'rule_groups': 91, 'parent_cases': 489,
            'operator_subconditions': 17, 'conformance': 'NOT_ESTABLISHED'}


if __name__ == '__main__':
    try:
        result = verify()
    except (ValueError, KeyError, OSError, TypeError) as error:
        raise SystemExit('Registry operator adoption check FAIL: ' + str(error)) from error
    print('Registry operator adoption check PASS: ' + json.dumps(result, sort_keys=True))
