"""Verify the MCP evidence addendum without promoting design or host conformance."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from check_spec_revision_adoption import verify as verify_spec_revision


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / 'verification/mcp-evidence-adoption.json'
INSPECTOR_REVISION = '58cffde89e45096b12d834fb562ea856d46b1c0b'
SOURCE_REVISION = '5df183d10a3c8018518dfa40ece9152a34b56fc1'
BINDING_REVISION = '520e5ed9a896ff8ba8ade776484f41084957aaa2'
DISPOSITIONS = {
    'ADOPT-01': 'RESOLVED_IN_ADOPTED_DESIGN',
    'ADOPT-02': 'RESOLVED_IN_AMENDED_DESIGN',
    'ADOPT-03': 'RESOLVED_IN_AMENDED_DESIGN',
    'ADOPT-04': 'RESOLVED_IN_ADOPTED_DESIGN',
    'ADOPT-05': 'EVIDENCE_LINKED_WITH_SCOPE_LIMITS',
    'ADOPT-06': 'PENDING_EXTERNAL',
}
SOURCES = {
    'verification/mcp-adoption.json',
    'verification/mcp-errata-adoption.json',
    'verification/post-adoption-errata-review.json',
    'profiles/non-http-mcp-security.md',
    'verification/traceability.json',
    'verification/history/mcp-adoption-2026-09-21/verification/traceability.json',
}
INSPECTOR_FILES = {
    'docs/evidence/ins11-integrated-verdict/report.json',
    'docs/evidence/ins11-integrated-verdict/ci-reports/mcp-binding.json',
    'docs/evidence/mcp-client-provenance/report.json',
}


def require(condition, label):
    if not condition:
        raise ValueError(label)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_record(root, record, inspector_root=None):
    require(set(record) == {'schema_version', 'kind', 'protocol_version', 'status',
                            'conformance', 'external_audit', 'source_spec_revision',
                            'reviewed_binding_revision', 'source_sha256', 'dispositions',
                            'historical_plan', 'inspector', 'scope_limits'}, 'record shape')
    require(record['schema_version'] == 1
            and record['kind'] == 'mcp-post-adoption-evidence-addendum'
            and record['protocol_version'] == '0.10.0'
            and record['status'] == 'EVIDENCE_LINKED_WITH_SCOPE_LIMITS'
            and record['conformance'] == 'NOT_ESTABLISHED'
            and record['external_audit'] == 'NOT_PERFORMED'
            and record['source_spec_revision'] == SOURCE_REVISION
            and record['reviewed_binding_revision'] == BINDING_REVISION,
            'status or revision promotion')
    require(record['dispositions'] == DISPOSITIONS, 'finding disposition')
    require(set(record['source_sha256']) == SOURCES, 'source inventory')
    for name, digest in record['source_sha256'].items():
        require(sha(root / name) == digest, 'specification source: ' + name)
    adoption = json.loads((root / 'verification/mcp-adoption.json').read_text())
    errata = json.loads((root / 'verification/mcp-errata-adoption.json').read_text())
    require(adoption['status'] == 'ADOPTED_NORMATIVE_DESIGN'
            and adoption['external_audit'] == 'NOT_PERFORMED'
            and errata['status'] == 'AMENDED_NORMATIVE_DESIGN'
            and errata['dispositions']['ADOPT-05'] == 'OPEN_PROVENANCE'
            and errata['dispositions']['ADOPT-06'] == 'PENDING_EXTERNAL',
            'historical adoption changed')
    historical = json.loads((root / 'verification/history/mcp-adoption-2026-09-21/verification/traceability.json').read_text())
    current = json.loads((root / 'verification/traceability.json').read_text())
    plan = record['historical_plan']
    require(plan == {'binding_parent_cases': 71, 'mandatory_children': 26,
                     'execution': 'NOT_RUN', 'current_total_parent_cases': 471,
                     'later_parent_cases_outside_pinned_overlay': 14,
                     'later_cases_execution': 'NOT_RUN'}, 'plan boundary')
    require(historical['binding_adoption']['parent_cases'] == 71
            and historical['binding_adoption']['mandatory_child_assertions'] == 26
            and historical['binding_adoption']['execution'] == 'NOT_RUN'
            and len(historical['cases']) == 457
            and len(historical['mandatory_subscenarios']) == 26
            and all(item['status'] == 'NOT_RUN' for item in historical['mandatory_subscenarios'])
            and len(current['cases']) == 471
            and len(current['cases']) - len(historical['cases']) == 14
            and all(item['evidence_status'] == 'planned_not_executed' for item in current['cases']),
            'historical or revised cases promoted')

    inspector = record['inspector']
    require(set(inspector['files']) == INSPECTOR_FILES
            and inspector['checkout_revision'] == INSPECTOR_REVISION
            and inspector['integrated_verdict_revision'] == '2b278fc23e9a55d1dc90554e1b976bc6104ae791'
            and inspector['ins11'] == 'INCOMPLETE'
            and inspector['deployed_host'] == inspector['live_registry'] == 'NOT_RUN',
            'Inspector source or deployment promotion')
    overlay = inspector['binding_overlay']
    require(overlay == {'parent_pass': 71, 'mandatory_children_per_core': 26,
                        'protected_pairs_pass': 4, 'restart_pass': 8,
                        'go_revision': '1f2dd87643e42b7ed3beda6956158ff23dcc7ea2',
                        'rust_revision': '40b5a8c6d76d952131013d8a034f819fd31b7ca0'},
            'binding scope changed')
    ci = inspector['source_ci']
    require(ci == {'run_id': 35933387031,
                   'head_sha': '690a8e0f85897e0615abb1cd0c7980442100c50e',
                   'artifact_id': 10781767710,
                   'artifact_name': 'mcp-native-interop-690a8e0f85897e0615abb1cd0c7980442100c50e',
                   'artifact_digest': 'sha256:701eef92d20f4fddb8fece47e9763d9501f5bd4a44b85f27446b3e7583e8e61d',
                   'conclusion': 'success'}, 'CI provenance changed')
    require(record['scope_limits'] == {
        'nine_mcp_errata_cases': 'NOT_RUN',
        'five_later_spec_cases': 'NOT_RUN',
        'supplementary_core_provenance': 'CORE_BOUNDARY_OBSERVED_ONLY',
        'same_revision_full_protocol_execution': False,
        'external_review': 'NOT_PERFORMED',
    }, 'scope limits promoted')
    document = (root / 'verification/mcp-evidence-adoption.md').read_text()
    for ident, disposition in DISPOSITIONS.items():
        require(f'| {ident} | `{disposition}` |' in document,
                'document disposition: ' + ident)
    if inspector_root is not None:
        revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=inspector_root, text=True).strip()
        require(revision == INSPECTOR_REVISION, 'Inspector checkout revision')
        for name, digest in inspector['files'].items():
            require(sha(inspector_root / name) == digest, 'Inspector source: ' + name)
        verdict = json.loads((inspector_root / 'docs/evidence/ins11-integrated-verdict/report.json').read_text())
        binding = json.loads((inspector_root / 'docs/evidence/ins11-integrated-verdict/ci-reports/mcp-binding.json').read_text())
        extra = json.loads((inspector_root / 'docs/evidence/mcp-client-provenance/report.json').read_text())
        require(verdict['spec_revision'] == BINDING_REVISION
                and verdict['source_ci'] == {key: ci[key] for key in ('run_id', 'head_sha', 'artifact_id', 'artifact_name', 'artifact_digest', 'conclusion')}
                and verdict['ins11'] == 'INCOMPLETE'
                and verdict['conformance'] == 'NOT_ESTABLISHED'
                and verdict['scopes']['registry_source'] == 'NOT_RUN'
                and verdict['scopes']['agent_host']['status'] == 'NOT_RUN'
                and verdict['scopes']['mcp_binding']['go_revision'] == overlay['go_revision']
                and verdict['scopes']['mcp_binding']['rust_revision'] == overlay['rust_revision']
                and verdict['unresolved']['mcp_go_revision_differs_from_lifecycle'] is True,
                'integrated verdict promotion')
        require(binding['spec_revision'] == BINDING_REVISION
                and binding['status'] == 'EVIDENCE_CHECKED'
                and binding['historical_catalog'] == {'NOT_RUN': 71}
                and binding['current_parent_cases'] == {'PASS': 71, 'PARTIAL': 0, 'NOT_RUN': 0}
                and binding['mandatory_children']['go']['mandatory_children'] == 26
                and binding['mandatory_children']['go']['revision'] == overlay['go_revision']
                and binding['mandatory_children']['rust']['mandatory_children'] == 26
                and binding['mandatory_children']['rust']['revision'] == overlay['rust_revision']
                and binding['protected_pairs'] == {'PASS': 4}
                and binding['restart_observations'] == {'PASS': 8}
                and binding['conformance'] == 'NOT_ESTABLISHED', 'binding evidence promotion')
        require(extra['status'] == 'CORE_BOUNDARY_OBSERVED'
                and extra['deployed_host'] == 'NOT_RUN'
                and extra['conformance'] == 'NOT_ESTABLISHED', 'supplementary core promotion')
    return {'ADOPT-05': 'EVIDENCE_LINKED_WITH_SCOPE_LIMITS',
            'ADOPT-06': 'PENDING_EXTERNAL', 'conformance': 'NOT_ESTABLISHED'}


def verify(root=ROOT, inspector_root=None):
    verify_spec_revision(root)
    record = json.loads((root / 'verification/mcp-evidence-adoption.json').read_text())
    return verify_record(root, record, inspector_root)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--inspector-root', type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.root, args.inspector_root)
    except (ValueError, KeyError, OSError, TypeError) as error:
        parser.exit(1, 'MCP evidence adoption check FAIL: ' + str(error) + '\n')
    print('MCP evidence adoption consistency PASS: ' + json.dumps(result, sort_keys=True))
