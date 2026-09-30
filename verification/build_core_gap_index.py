"""Keep every 0.10.0 rule in the pinned Go/Rust source-review queue."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
SPEC_REVISION = '44df132fee5925182018ce089dc82435cb353f8a'
GO_REVISION = '49379baadc6baec9ca8b4bb7d15bf43d65144bd7'
RUST_REVISION = 'ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396'
OUTPUT = ROOT / 'verification/core-gap-index.json'

# These are starting locations, not claims that an implementation meets a rule.
CANDIDATES = {
    'spec/00-overview.md': ('pkg/agent', 'src/lib.rs'),
    'spec/01-crypto.md': ('pkg/agent/crypto/keys', 'src/crypto'),
    'spec/02-jcs.md': ('pkg/agent/crypto/jcs', 'src/jcs'),
    'spec/03-rfc9421.md': ('pkg/agent/core/rfc9421', 'src/rfc9421'),
    'spec/04-hpke.md': ('pkg/agent/hpke', 'src/hpke'),
    'spec/05-session.md': ('pkg/agent/session', 'src/session'),
    'spec/06-did-sage.md': ('pkg/agent/did', 'src/did'),
    'spec/07-a2a.md': ('pkg/agent/did/a2a.go', 'src/did/a2a.rs'),
    'spec/08-transport.md': ('pkg/agent/transport', 'src/hpke/completion010'),
    'spec/09-registry.md': ('pkg/agent/registry010', 'src/registry010'),
    'spec/10-resolution.md': ('pkg/agent/did/resolver.go', 'src/did/resolver.rs'),
    'spec/11-registries.md': ('pkg/agent/registry010', 'src/registry010'),
    'profiles/agent-mcp-security.md': ('pkg/agent/guard010', 'src/guard010'),
    'profiles/non-http-mcp-security.md': ('pkg/agent/guard010', 'src/guard010'),
    'PROCESS.md': (None, None),
    'charter.md': (None, None),
}
REVIEWED = {
    'OVERVIEW-01': 'PARTIAL_SOURCE_REVIEW_WITH_GRAMMAR_GAP',
    'OVERVIEW-02': 'PARTIAL_SOURCE_REVIEW',
    'OVERVIEW-03': 'PARTIAL_SOURCE_AND_EXISTING_TEST_REVIEW',
    'OVERVIEW-04': 'DOCUMENT_CONTROL_REVIEW',
    'MSG-01': 'SOURCE_GAP_FOR_P256_AND_PARTIAL_ED25519_REVIEW',
    'MSG-02': 'PARTIAL_SOURCE_AND_EXISTING_TEST_REVIEW',
    'MSG-03': 'PARTIAL_SOURCE_AND_EXISTING_TEST_REVIEW',
    'MSG-04': 'PARTIAL_SOURCE_AND_EXISTING_TEST_REVIEW',
    'MSG-05': 'PARTIAL_SOURCE_AND_EXISTING_TEST_REVIEW',
    'MSG-06': 'HOST_BOUNDARY_NOT_ESTABLISHED',
    'HPKE-01': 'PARTIAL_SOURCE_AND_EXISTING_TEST_REVIEW',
    'HPKE-02': 'PARTIAL_SOURCE_AND_EXISTING_TEST_REVIEW',
    'HPKE-03': 'PARTIAL_SOURCE_AND_EXISTING_TEST_REVIEW',
    'HPKE-04': 'PARTIAL_SOURCE_AND_EXISTING_TEST_REVIEW',
    'HPKE-05': 'PARTIAL_SOURCE_AND_EXISTING_TEST_REVIEW',
    'HPKE-06': 'PARTIAL_SOURCE_REVIEW_HOST_BOUNDARY_PENDING',
    'SESSION-01': 'PARTIAL_SOURCE_AND_EXISTING_TEST_REVIEW',
    'SESSION-02': 'PARTIAL_SOURCE_AND_EXISTING_TEST_REVIEW',
    'SESSION-03': 'PARTIAL_SOURCE_AND_EXISTING_TEST_REVIEW_INTEROPERABILITY_BOUNDARY',
    'SESSION-04': 'PARTIAL_SOURCE_AND_EXISTING_TEST_REVIEW',
    'SESSION-05': 'PARTIAL_SOURCE_AND_EXISTING_TEST_REVIEW_WINDOW_MOVEMENT_UNREACHABLE',
    'SESSION-06': 'PARTIAL_SOURCE_AND_EXISTING_TEST_REVIEW',
    'CRYPTO-01': 'SOURCE_AND_BOUNDED_RUNTIME_GAP',
    'CRYPTO-02': 'SOURCE_AND_BOUNDED_RUNTIME_GAP',
    'CRYPTO-03': 'PARTIAL_SOURCE_REVIEW',
    'CRYPTO-04': 'PARTIAL_SOURCE_REVIEW',
    'CRYPTO-05': 'PARTIAL_SOURCE_REVIEW',
    'JCS-01': 'SOURCE_AND_BOUNDED_RUNTIME_GAP',
    'JCS-02': 'PARTIAL_SOURCE_REVIEW',
    'JCS-03': 'PARTIAL_RUNTIME_REVIEW',
    'JCS-04': 'SOURCE_GAP',
    'ID-01': 'SOURCE_AND_BOUNDED_RUNTIME_GAP',
    'ID-02': 'SOURCE_GAP',
    'ID-03': 'PARTIAL_SOURCE_REVIEW',
    'ID-04': 'SOURCE_GAP_FOR_010_MUTATION_API',
    'CARD-01': 'SOURCE_GAP_FOR_SAGE_CARD_SCHEMA',
    'CARD-02': 'SOURCE_GAP_FOR_SAGE_CARD_PROOF',
    'CARD-03': 'SOURCE_GAP_FOR_CURRENT_REGISTRY_CARD_VALIDATION',
    'TRANSPORT-01': 'PARTIAL_STRICT_SUBSET_WITH_SCHEMA_GAP',
    'TRANSPORT-02': 'PARTIAL_SIGNED_SUBSET_WITH_COVERAGE_GAP',
    'TRANSPORT-03': 'PARTIAL_RESPONSE_BINDING_WITH_PROFILE_GAP',
    'TRANSPORT-04': 'PARTIAL_REPLAY_TRANSACTION_WITH_HOST_BOUNDARY_PENDING',
    'TRANSPORT-05': 'PARTIAL_HTTP_BINDING_WITH_SUITE_AND_HOST_GAP',
    'TRANSPORT-06': 'WIRE_TRANSPORT_HOST_PATH_NOT_ESTABLISHED',
    'REG-01': 'SOURCE_GAP_FOR_COMPLETE_RECORD_VALIDATION',
    'REG-02': 'PARTIAL_KEY_SELECTION_WITH_SOURCE_BOUNDARY',
    'REG-03': 'SOURCE_GAP_FOR_LIFECYCLE_MUTATION',
    'REG-04': 'PARTIAL_CHALLENGE_WITH_PROOF_VERIFIER_GAP',
    'REG-05': 'PARTIAL_FRESH_OBSERVATION_WITH_DEPLOYMENT_BOUNDARY',
    'REG-06': 'DEPLOYMENT_BINDING_NOT_ESTABLISHED',
    'REG-07': 'RESERVED_PROFILE_REJECTION_NOT_ESTABLISHED',
    'REG-08': 'WEB_PROFILE_BINDING_NOT_ESTABLISHED',
    'RESOLVE-01': 'SOURCE_GAP_FOR_CURRENT_DOCUMENT_PROJECTION',
    'RESOLVE-02': 'SOURCE_GAP_FOR_AUTHORITY_BOUND_RESOLUTION',
    'RESOLVE-03': 'SOURCE_GAP_FOR_RESOLUTION_METADATA',
    'RESOLVE-04': 'PARTIAL_EXACT_KEY_SELECTION_WITH_DEREFERENCE_GAP',
    'RESOLVE-05': 'OPTIONAL_HTTP_BINDING_NOT_ESTABLISHED',
}


def build():
    source = (ROOT / 'verification/traceability.json').read_bytes()
    trace = json.loads(source)
    if len(trace['rules']) != 91 or {r['source'] for r in trace['rules']} != set(CANDIDATES):
        raise ValueError('rule count or source set changed; update the index deliberately')
    rows = []
    for rule in trace['rules']:
        go, rust = CANDIDATES[rule['source']]
        rows.append({
            'rule_id': rule['id'], 'source': rule['source'],
            'case_count': len(rule['case_ids']),
            'status': REVIEWED.get(rule['id'], 'PENDING_CLAUSE_REVIEW'),
            'go_source_candidate': go, 'rust_source_candidate': rust,
        })
    return {
        'schema_version': 1, 'protocol_version': '0.10.0',
        'spec_revision': SPEC_REVISION,
        'traceability_sha256': hashlib.sha256(source).hexdigest(),
        'go_revision': GO_REVISION, 'rust_revision': RUST_REVISION,
        'scope': ('Source candidates are navigation hints, not conformance; '
                  'only the named reviewed rules have bounded findings.'),
        'counts': {'rules': len(rows), 'reviewed': len(REVIEWED),
                   'pending': len(rows) - len(REVIEWED)},
        'rules': rows,
    }


def check_core_paths(result, go_root, rust_root):
    for name, root, revision in (
            ('go_source_candidate', go_root, GO_REVISION),
            ('rust_source_candidate', rust_root, RUST_REVISION)):
        if root is None:
            continue
        actual = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
        if actual != revision:
            raise ValueError(f'{root}: expected {revision}, got {actual}')
        for row in result['rules']:
            candidate = row[name]
            if candidate and not (root / candidate).exists():
                raise ValueError(f"{row['rule_id']}: missing {root / candidate}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--go-root', type=Path)
    parser.add_argument('--rust-root', type=Path)
    args = parser.parse_args()
    result = build()
    check_core_paths(result, args.go_root, args.rust_root)
    encoded = (json.dumps(result, indent=2) + '\n').encode()
    if args.write:
        OUTPUT.write_bytes(encoded)
    elif OUTPUT.read_bytes() != encoded:
        raise ValueError('core gap index differs from pinned traceability')
    print(json.dumps(result['counts'], sort_keys=True))


if __name__ == '__main__':
    main()
