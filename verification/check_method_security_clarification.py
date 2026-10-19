"""Verify a descriptive revision without promoting historical conformance.

Hashes and unchanged-byte checks establish document provenance, not the
semantic correctness of security analysis. Independent review remains separate.
"""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = 'verification/method-security-clarification.json'
HISTORY = 'verification/history/method-security-base-2026-10-19'
BASE = '06b50e177ccd22bce7d70fd80c2d7f822ae3fd3b'
CHAPTER = 'spec/06-did-sage.md'
OVERLAY = 'analysis/current-design-overlay.json'
FILES = {CHAPTER, OVERLAY}
ANALYZED = {
    'did11-cr20260305#privacy-requirements.1',
    'did11-cr20260305#security-requirements.2',
    'did11-cr20260305#security-requirements.13',
}
OPEN = {
    'did11-cr20260305#security-requirements.1',
    'did11-cr20260305#security-requirements.5',
    'did11-cr20260305#security-requirements.6',
    'res10-crd20261001#vdr-forks.1',
}
PINNED_BASE = {
    CHAPTER: 'fa7e180a37971ec382968d826857a3c4735f2a5f476c939d7aaf48349cea5691',
    OVERLAY: '8173f44baeab7db57fd29e0992d4273409e1d52eb15b35f1ffe329ec584ba432',
}


def require(condition, message):
    if not condition:
        raise ValueError('method-security clarification: ' + message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(root=ROOT):
    root = Path(root)
    record = json.loads((root / RECORD).read_text())
    require(set(record) == {
        'schema_version', 'kind', 'protocol_version', 'status', 'base_revision',
        'historical_root', 'baseline_sha256', 'current_sha256',
        'analysis_statement_ids', 'incomplete_statement_ids',
        'historical_verdicts', 'new_conformance_verdicts', 'independent_review',
        'wire_acceptance_changed', 'authentication_rule_adopted',
        'fork_policy_adopted', 'runtime_execution', 'operating_roots_selected',
    }, 'record members')
    require(type(record['schema_version']) is int and record['schema_version'] == 1
            and record['kind'] == 'sage-method-security-clarification'
            and record['protocol_version'] == '0.10.0'
            and record['status'] == 'ADOPTED_DOCUMENTARY_ANALYSIS'
            and record['base_revision'] == BASE
            and record['historical_root'] == HISTORY, 'identity and scope')
    require(all(record[k] is False for k in (
        'wire_acceptance_changed', 'authentication_rule_adopted',
        'fork_policy_adopted', 'operating_roots_selected'))
        and record['runtime_execution'] == 'NOT_RUN'
        and record['new_conformance_verdicts'] == {}, 'unsupported evidence promotion')
    require(isinstance(record['analysis_statement_ids'], list)
            and isinstance(record['incomplete_statement_ids'], list)
            and len(record['analysis_statement_ids']) == len(ANALYZED)
            and set(record['analysis_statement_ids']) == ANALYZED
            and len(record['incomplete_statement_ids']) == len(OPEN)
            and set(record['incomplete_statement_ids']) == OPEN
            and record['historical_verdicts'] == {
                name: 'FAIL' for name in ANALYZED | OPEN}, 'seven historical findings')
    require(set(record['baseline_sha256']) == FILES
            and set(record['current_sha256']) == FILES, 'exact file inventory')
    earlier = json.loads((root / 'verification/a2a-did-adoption.json').read_text())
    for name in FILES:
        require(record['baseline_sha256'][name] == earlier['current_sha256'][name]
                and sha(root / HISTORY / name) == record['baseline_sha256'][name],
                'preserved adopted bytes: ' + name)
        require(sha(root / name) == record['current_sha256'][name],
                'current bytes: ' + name)
    require(all(record['baseline_sha256'][name] == digest
                for name, digest in PINNED_BASE.items()), 'fixed normative baseline')
    before = (root / HISTORY / CHAPTER).read_bytes()
    after = (root / CHAPTER).read_bytes()
    start = b'### 6.1. Assets, participants and trust boundaries\n'
    end = b'## 7. Change in 0.10.0\n'
    require(after.count(start) == 1 and after.count(end) == 1,
            'analysis boundaries')
    a, b = after.index(start), after.index(end)
    require(a < b and after[:a] + after[b:] == before,
            'pre-existing normative text changed')
    old_graph = json.loads((root / HISTORY / OVERLAY).read_text())
    expected = json.loads(json.dumps(old_graph))
    nodes = [node for node in expected['nodes']
             if node.get('id') == 'doc:sage-spec:' + CHAPTER]
    require(len(nodes) == 1, 'unique chapter node')
    nodes[0]['sha256'] = record['current_sha256'][CHAPTER]
    require(json.loads((root / OVERLAY).read_text()) == expected,
            'overlay changed beyond the chapter digest')
    review = record['independent_review']
    require(set(review) == {'path', 'sha256', 'scope'}
            and review['path'] == 'verification/method-security-clarification-review.md'
            and review['scope'] == 'documentary analysis only; no conformance verdict'
            and sha(root / review['path']) == review['sha256'],
            'independent review provenance')
    return {'historical_findings': 7, 'analysis_scopes': 3,
            'incomplete_scopes': 4, 'new_conformance_verdicts': 0,
            'runtime_execution': 'NOT_RUN'}


def at_previous_adoption(root, name):
    """Validate the new revision before reading a previous adoption's bytes."""
    root = Path(root)
    if name in FILES and (root / RECORD).is_file():
        verify(root)
        return root / HISTORY / name
    return root / name


if __name__ == '__main__':
    print(json.dumps(verify(), sort_keys=True))
