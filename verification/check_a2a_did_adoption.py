"""Check the A2A 1.0 binding and DID projection adoption record."""

import hashlib
import json
from pathlib import Path

from check_method_security_clarification import at_previous_adoption


ROOT = Path(__file__).resolve().parents[1]
RECORD = 'verification/a2a-did-adoption.json'
HISTORY = 'verification/history/a2a-did-base-2026-10-12'
TRACE = 'verification/traceability.json'
PROFILE = 'profiles/a2a-1.0-binding.md'
PROPOSAL = 'proposals/a2a-did-interop'
NEW_RULES = [f'A2AB-{n:02d}' for n in range(1, 8)] + [f'DIDP-{n:02d}' for n in range(1, 6)] + ['TABLE-08']
TABLE_CASES = ['TABLE-08-P', 'TABLE-08-N01']
CHANGED = {
    'CHANGELOG.md', 'PROCESS.md', 'README.md', 'charter.md',
    'spec/06-did-sage.md', 'spec/10-resolution.md', 'spec/11-registries.md',
    'analysis/build-current-design-overlay.py', 'analysis/current-design-overlay.json',
    'analysis/current-design-overlay.md', 'verification/build_core_gap_index.py',
    'verification/core-gap-index.json', 'verification/inspector-plan.md', TRACE,
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prior_path(root, name):
    """Return the bytes an earlier record pinned for a file this adoption changed."""
    if name in CHANGED and (root / RECORD).is_file():
        return root / HISTORY / name
    return root / name


def check_trace(root):
    old = json.loads((root / HISTORY / TRACE).read_text())
    new = json.loads((root / TRACE).read_text())
    for key in ('schema_version', 'protocol_version', 'status', 'scope',
                'mandatory_subscenarios', 'binding_required_observations', 'binding_adoption'):
        require(old[key] == new[key], 'unchanged trace member: ' + key)
    require([r['id'] for r in old['requirements']] == [r['id'] for r in new['requirements']],
            'requirement identities')
    for before, after in zip(old['requirements'], new['requirements']):
        added = after['rule_ids'][len(before['rule_ids']):]
        require(after['rule_ids'][:len(before['rule_ids'])] == before['rule_ids']
                and set(added) <= set(NEW_RULES)
                and {k: v for k, v in after.items() if k != 'rule_ids'} ==
                {k: v for k, v in before.items() if k != 'rule_ids'},
                'requirement change: ' + after['id'])
    old_rules = {r['id']: r for r in old['rules']}
    new_rules = {r['id']: r for r in new['rules']}
    require(set(new_rules) - set(old_rules) == set(NEW_RULES)
            and set(old_rules) <= set(new_rules) and len(new_rules) == 104,
            'rule inventory')
    for rule_id, before in old_rules.items():
        after = new_rules[rule_id]
        require({k: v for k, v in after.items() if k != 'line'} ==
                {k: v for k, v in before.items() if k != 'line'},
                'existing rule changed: ' + rule_id)
    old_cases = {c['id']: c for c in old['cases']}
    new_cases = {c['id']: c for c in new['cases']}
    require(all(new_cases.get(k) == v for k, v in old_cases.items()), 'existing case changed')
    plan = json.loads((root / PROPOSAL / 'cases.json').read_text())['cases']
    added = [c for c in new['cases'] if c['id'] not in old_cases]
    require([c['id'] for c in added if c['rule_id'] != 'TABLE-08'] ==
            [c['id'] for c in plan if c['rule'].startswith('DIDP')] +
            [c['id'] for c in plan if c['rule'].startswith('A2AB')]
            and [c['id'] for c in added if c['rule_id'] == 'TABLE-08'] == TABLE_CASES
            and len(new_cases) == 583, 'new case inventory')
    by_id = {c['id']: c for c in plan}
    for case in added:
        source = by_id.get(case['id'])
        require(case['evidence_status'] == 'planned_not_executed'
                and case['id'] in new_rules[case['rule_id']]['case_ids'],
                'new case claim or owner: ' + case['id'])
        if source:
            require(case['rule_id'] == source['rule'] and case['input'] == source['input']
                    and case['preconditions'] == source['precondition']
                    and case['expected'].startswith(source['expected'] + '.'),
                    'case differs from the reviewed plan: ' + case['id'])
    for rule_id in NEW_RULES:
        rule = new_rules[rule_id]
        lines = (root / rule['source']).read_text().splitlines()
        require(rule['evidence_status'] == 'planned_not_executed'
                and rule_id in lines[rule['line'] - 1] and lines[rule['line'] - 1].startswith('## ')
                and len(rule['case_ids']) >= 2,
                'new rule mapping: ' + rule_id)
    return new


def check_text(root):
    profile = (root / PROFILE).read_text()
    require(profile.startswith('# A2A 1.0 binding for SAGE 0.10.0\n')
            and 'Status: **ADOPTED_NORMATIVE_DESIGN**' in profile
            and all(f'## A2AB-{n:02d}:' in profile for n in range(1, 8))
            and 'https://sage-x-project.github.io/sage-spec/a2a/0.10.0/binding' in profile
            and 'https://sage-x-project.github.io/sage-spec/a2a/0.10.0/extension' in profile
            and '0 < expires - issued <= 86400' in profile
            and 'proposal' not in profile.split('## A2AB-01')[1],
            'profile clauses')
    old10 = (root / HISTORY / 'spec/10-resolution.md').read_text()
    new10 = (root / 'spec/10-resolution.md').read_text()
    require('empty verification methods and relationship arrays' in old10
            and 'empty verification methods and relationship arrays' not in new10
            and 'with no member is omitted, never projected as an empty array' in new10
            and all(f'— DIDP-{n:02d} (' in new10 for n in range(1, 6))
            and '| `representation.unsupported` | Unsupported representation | 406 |' in new10
            and 'No\nunregistered `application/did`' in old10
            and 'unregistered `application/did`' not in new10,
            'chapter 10 amendments')
    tables = (root / 'spec/11-registries.md').read_text()
    require('## 8. Service types — TABLE-08 (R-3, R-34)' in tables
            and '| `A2AInterface` |' in tables and '| `sage-a2a-card+jws` |' in tables
            and '| `representation.unsupported` |' in tables, 'chapter 11 amendments')
    require('A2A card signatures use the JWS protected header `kid`' in
            (root / 'spec/06-did-sage.md').read_text(), 'chapter 06 amendment')
    proposal = (root / PROPOSAL / 'README.md').read_text()
    require('Status: **proposed design, not adopted**.' in proposal,
            'the proposal must stay a historical snapshot')


def verify(root=ROOT):
    record = json.loads((root / RECORD).read_text())
    require(set(record) == {
        'schema_version', 'kind', 'protocol_version', 'base_revision', 'status',
        'historical_root', 'historical_sha256', 'current_sha256', 'proposal_sha256',
        'counts', 'new_rule_ids', 'owner_review', 'go_core_execution', 'rust_core_execution',
        'did_go_advanced_sage', 'inspector_execution', 'external_audit', 'conformance',
        'release_or_tag_created'}, 'record members')
    require(record['schema_version'] == 1
            and record['kind'] == 'a2a-did-normative-design-adoption'
            and record['protocol_version'] == '0.10.0'
            and record['base_revision'] == '054fcb5dc0781b7c906f81bd47ccb20160a13df0'
            and record['status'] == 'ADOPTED_NORMATIVE_DESIGN_PENDING_EXECUTION'
            and record['historical_root'] == HISTORY
            and record['new_rule_ids'] == NEW_RULES,
            'adoption identity')
    require(record['counts'] == {'requirements': 45, 'prior_rule_groups': 91, 'new_rule_groups': 13,
                                 'rule_groups': 104, 'prior_parent_cases': 489,
                                 'new_parent_cases': 94, 'parent_cases': 583,
                                 'mandatory_children': 26}, 'counts')
    require(all(record[k] == 'NOT_RUN' for k in (
                'go_core_execution', 'rust_core_execution', 'did_go_advanced_sage',
                'inspector_execution'))
            and record['external_audit'] == 'NOT_PERFORMED'
            and record['conformance'] == 'NOT_ESTABLISHED'
            and record['release_or_tag_created'] is False
            and record['owner_review'] == f'{PROPOSAL}/review.md',
            'unsupported evidence promotion')
    require(set(record['historical_sha256']) == CHANGED, 'historical inventory')
    for name, digest in record['historical_sha256'].items():
        require(sha(root / HISTORY / name) == digest, 'historical bytes: ' + name)
    require(set(record['current_sha256']) == CHANGED | {PROFILE}, 'current inventory')
    for name, digest in record['current_sha256'].items():
        require(sha(at_previous_adoption(root, name)) == digest, 'current bytes: ' + name)
    for name, digest in record['proposal_sha256'].items():
        require(name.startswith(PROPOSAL + '/') and sha(root / name) == digest,
                'proposal bytes: ' + name)
    trace = check_trace(root)
    check_text(root)
    trace_sha = record['current_sha256'][TRACE]
    overlay = json.loads((root / 'analysis/current-design-overlay.json').read_text())
    gaps = json.loads((root / 'verification/core-gap-index.json').read_text())
    require(overlay['traceability'] == {'path': TRACE, 'sha256': trace_sha, 'requirements': 45,
                                        'rule_groups': 104, 'planned_cases': 583}
            and any(node.get('path') == PROFILE for node in overlay['nodes'])
            and gaps['traceability_sha256'] == trace_sha and gaps['counts']['rules'] == 104,
            'overlay or core gap index not rebuilt from the adopted plan')
    return {'rule_groups': len(trace['rules']), 'parent_cases': len(trace['cases']),
            'new_rule_groups': 13, 'conformance': 'NOT_ESTABLISHED'}


if __name__ == '__main__':
    try:
        result = verify()
    except (ValueError, KeyError, OSError, TypeError, IndexError) as error:
        raise SystemExit('A2A and DID adoption check FAIL: ' + str(error)) from error
    print('A2A and DID adoption check PASS: ' + json.dumps(result, sort_keys=True))
