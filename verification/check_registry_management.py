"""Check a proposed documentary contract; never execute or authorize a Registry."""
from pathlib import Path
import hashlib
import json

BASE = 'proposals/management-security-binding/'
MANIFEST = 'profiles/sage-0.11.0/registry-management.json'
DOCUMENT = 'profiles/sage-0.11.0/registry-management.md'
SELECTED = {
    'profiles/sage-0.11.0/README.md': '65104242f4fd5f21da146d1db85a0962b7a19a479f5db2849139d244fd949068',
    'profiles/sage-0.11.0/selection.json': '1f634918db2a14c8ed1db6eba7a8d93cc7b327029e86140d494dc677c82ac919',
    '.github/workflows/profile-selection.yml': 'ed1a39173edcf2d35b4937ba5ef7f259e663a0f26b42e35d515032bfa3a32a3b',
}
LIMITS = dict(record_bytes=65536, command_bytes=262144, history_bytes=262144,
              lifetime_keys=128, services=16, active_grants=128,
              whole_calldata_bytes=148804, agent_id_bytes=64, key_name_bytes=32,
              algorithm_bytes=24, raw_key_bytes=65, proof_bytes=65,
              signer_url_bytes=189, service_type_bytes=64, service_uri_bytes=2048,
              claim_window_blocks=256, safe_seconds=9007199254740991,
              maximum_version='18446744073709551615')
KEYS = set('kind status adoption revision protocol_version source_revision source_sha256 document document_sha256 requirements domains methods limits schemas grammar algorithms principal lifecycle grants guard_order rank8 errors reserved_errors events headroom source_evidence implementation_and_operating excluded'.split())
OPERATIONS = {
    'revealClaim': ('create', ['controller', 'keys', 'services', 'salt']),
    'activate': ('activate', []), 'addKey': ('add-key', ['key']),
    'revokeKey': ('revoke-key', ['name']), 'updateServices': ('update-services', ['services']),
    'authorizeOperator': ('authorize-operator', ['operator', 'scope']),
    'revokeOperator': ('revoke-operator', ['operator', 'scope']), 'deactivate': ('deactivate', []),
}

REVIEWED_POLICY = {'grammar': {'agent_id': '[A-Za-z0-9._-]{1,64}; exclude . and ..', 'key_name': '[A-Za-z0-9_-]{1,32}', 'address': '0x[0-9a-f]{40}', 'version': '[1-9][0-9]*; uint64', 'uri': 'RFC3986 HTTPS absolute URI; no userinfo or fragment; preserve bytes; no fetch'}, 'lifecycle': {'create': ['absent', 'controller', 'created', 'require-usable-signer'], 'activate': ['created', 'controller-or-exact-grant', 'active', 'require-usable-signer-remove-activate-grants'], 'add-key': ['active', 'controller-or-exact-grant', 'active', 'append-one-immutable-key'], 'revoke-key': ['created-or-active', 'controller-or-active-exact-grant', 'same-or-deactivated', 'retain-target-terminal-if-last-usable-signer'], 'update-services': ['active', 'controller-or-exact-grant', 'active', 'replace-complete-array'], 'authorize-operator': ['created-or-active', 'controller', 'same', 'insert-one-absent-pair'], 'revoke-operator': ['created-or-active', 'controller', 'same', 'remove-one-present-pair'], 'deactivate': ['created-or-active', 'controller-or-exact-grant', 'deactivated', 'remove-all-grants']}, 'guard_order': ['bounded-canonical-framing', 'value-then-registry-context', 'scalar-content-grammar', 'identity-claim-or-history', 'actual-principal', 'state-then-predecessor-then-version-capacity', 'claim-window-then-admission-time', 'operation-targets-entry-structure-prospective-size', 'new-proofs-signing-before-kem', 'complete-successor-cleanup-serialization-recheck', 'atomic-commit-one-event'], 'rank8': {'create': ['key-name-order-equality:KeyNameReused', 'key-name-inversion:InvalidEntry', 'raw-material-duplicate:KeyMaterialReused', 'service-order-or-key-collision:InvalidEntry', 'new-entry-structure'], 'activate': [], 'add-key': ['lifetime-cap:BoundsExceeded', 'used-name:KeyNameReused', 'used-material:KeyMaterialReused', 'current-service-collision:InvalidEntry', 'new-entry-structure'], 'revoke-key': ['missing-or-revoked-key:KeyUnavailable'], 'update-services': ['service-order-or-key-collision:InvalidEntry'], 'authorize-operator': ['controller-target-or-state-scope:InvalidEntry', 'active-pair:GrantAlreadyPresent', 'grant-cap:BoundsExceeded'], 'revoke-operator': ['controller-target:InvalidEntry', 'absent-pair:GrantUnavailable'], 'deactivate': []}, 'excluded': ['optional-web-management', 'erc-companion', 'erc-payment-wallet', 'reputation', 'validation', 'projection-alg-kid-jsonld', 'new-gas-or-key-cap', 'controller-transfer-recovery', 'public-initializer-test-controls', 'implicit-old-record-migration']}

def require(condition, reason):
    if not condition:
        raise ValueError(reason)

def load(path):
    def pairs(items):
        out = {}
        for key, value in items:
            require(key not in out, 'duplicate JSON member')
            out[key] = value
        return out
    def constant(value):
        raise ValueError('nonfinite JSON number: ' + value)
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=pairs, parse_constant=constant)

def exact(actual, expected, reason):
    require(type(actual) is type(expected), reason + ': type')
    if isinstance(expected, dict):
        require(set(actual) == set(expected), reason + ': members')
        for key in expected:
            exact(actual[key], expected[key], reason + '.' + key)
    elif isinstance(expected, list):
        require(len(actual) == len(expected), reason + ': length')
        for a, e in zip(actual, expected):
            exact(a, e, reason)
    else:
        require(actual == expected, reason + ': value')

def validate(value, root):
    require(type(value) is dict and set(value) == KEYS, 'manifest root')
    exact({k: value[k] for k in ['kind', 'status', 'adoption', 'revision', 'protocol_version', 'source_revision']},
          {'kind': 'sage-chain-management-binding', 'status': 'PROPOSED_CHAIN_BINDING',
           'adoption': 'EXPLICIT_DECISION_REQUIRED', 'revision': 1, 'protocol_version': '0.11.0',
           'source_revision': '040436d0239330e3f5fc760489cf2a63729fa4a4'}, 'proposal identity')
    require(value['document'] == DOCUMENT, 'fixed documentary path')
    doc = (root / DOCUMENT).read_bytes()
    require(hashlib.sha256(doc).hexdigest() == value['document_sha256'], 'document identity')
    text = doc.decode('utf-8')
    exact(value['requirements'], ['CM-%02d' % n for n in range(1, 10)], 'requirement inventory')
    require('PROPOSED CHAIN BINDING' in text, 'document status')
    require(all(text.count('— ' + n + '\n') == 1 for n in value['requirements']), 'document anchors')
    for name, digest in SELECTED.items():
        require(hashlib.sha256((root / name).read_bytes()).hexdigest() == digest, 'frozen selection source')
    selected = load(root / 'profiles/sage-0.11.0/selection.json')
    expected_sources = dict(selected['baseline_sha256'], **SELECTED)
    exact(value['source_sha256'], expected_sources, 'complete fixed input inventory')
    require(len(expected_sources) == 32, 'source count')
    for name, digest in expected_sources.items():
        require(hashlib.sha256((root / name).read_bytes()).hexdigest() == digest, 'public input changed: ' + name)
    domains = {x['name']: {'value': x['value'], 'utf8_hex': x['utf8_hex']}
               for x in selected['domain_entries'] if x['name'] in ['registry_chain_binding', 'registry_pop', 'registry_claim']}
    exact(value['domains'], domains, 'selected domain bytes')
    require(all(v['value'].encode().hex() == v['utf8_hex'] for v in value['domains'].values()), 'domain UTF8')
    mapping = load(root / (BASE + 'chain-command-map.json'))
    abi = load(root / (BASE + 'contract-abi.json'))
    signatures = load(root / (BASE + 'contract-signatures.json'))
    methods = {n: {'kind': v['kind'], 'operation': v['operation'],
                   'minimum_head_bytes': v['minimumHeadBytes'], 'maximum_calldata_bytes': v['maximumCalldataBytes']}
               for n, v in mapping['methods'].items()}
    exact(value['methods'], methods, '13 methods and framing bounds')
    require(set(methods) == {a['name'] for a in abi} == set(signatures) and len(methods) == 13, 'ABI method closure')
    require(sum(v['kind'] == 'mutation' for v in methods.values()) == 8, 'mutation count')
    exact(value['limits'], LIMITS, 'bounds without bool/integer substitution')
    exact(value['schemas'], {
        'record': ['id', 'controller', 'keys', 'services', 'state', 'version'],
        'key_required': ['name', 'alg', 'key', 'proof', 'state'], 'key_optional': ['expires'],
        'proof': ['signer', 'value'], 'service': ['name', 'type', 'uri'],
        'claim': ['registryId', 'agentId', 'controller', 'keys', 'services', 'salt'],
        'chain_command': mapping['chainCommandFields'], 'history': mapping['historyFields'],
        'grant': ['operator', 'scope'], 'arguments': {op: args for op, args in OPERATIONS.values()},
        'unknown_members': 'REJECT'}, 'closed schemas')
    exact(value['principal'], {'source': 'Registry.msg.sender', 'accounts': ['EOA', 'CONTRACT_WALLET'],
                              'substitutions': 'FORBIDDEN', 'controller_transfer': False,
                              'forwarder_identity': False, 'wallet_signature_callback': False}, 'actual caller')
    exact(value['algorithms'], {'mandatory_signing': ['ed25519'],
          'optional_signing': ['ecdsa-p256-sha256', 'sage-secp256k1-keccak256'], 'kem_only': ['x25519'],
          'unknown_or_unsupported': 'REJECT_NO_ALTERNATE_KEY_OR_ALGORITHM', 'new_kem_admission_narrowing': False,
          'key_proof_order': 'ALL_NEW_SIGNING_PROOFS_THEN_NEW_KEM_ENDORSEMENTS'}, 'role and algorithm namespaces')
    require(set(value['lifecycle']) == set(value['schemas']['arguments']) == set(value['rank8']), 'operation closure')
    exact(value['grants'], {'created': ['activate', 'deactivate'],
          'active': ['add-key', 'revoke-key', 'update-services', 'deactivate'],
          'sort': ['operator_ASCII', 'scope_ASCII'], 'controller_may_grant_self': False,
          'operator_may_delegate': False}, 'scope policy')
    outcome = load(root / (BASE + 'outcomes/schemas.json'))
    exact(value['errors'], sorted(k for k, v in outcome.items() if v['kind'] == 'error'), 'diagnostics')
    exact(value['events'], {k: v for k, v in outcome.items() if v['kind'] == 'event'}, 'event schemas')
    exact(value['reserved_errors'], ['ClaimMismatch'], 'reserved not emitted')
    exact(value['headroom'], {'status': 'PROPOSED_EXPLICIT_NEW_ADMISSION_RESTRICTION',
          'applies': 'EVERY_NONTERMINAL_PROSPECTIVE_SUCCESSOR_BEFORE_PROOFS', 'size_only_state': 'deactivated',
          'size_only_version': '18446744073709551615', 'actual_record_bound_first': True,
          'fixed_subtraction_equivalent': False, 'old_profile_reads_affected': False,
          'version_exhaustion_bypass': False}, 'explicit narrowing boundary')
    exact(value['source_evidence'], {'one_finalized_block': True, 'inner_call_success_required': True,
          'outer_receipt_sufficient': False, 'complete_history_required': True,
          'durable_monotone_and_terminal_facts': True, 'automatic_fork_selection': False,
          'authenticated_reconfiguration_required': True}, 'source evidence')
    exact(value['implementation_and_operating'], {'status': 'NOT_IMPLEMENTED_OR_QUALIFIED',
          'compiler': None, 'verifier': None, 'chain_id': None, 'rpc': None, 'address': None,
          'code_hash': None, 'abi_hash': None, 'finality_policy': None, 'gas_budget': None,
          'deployment_authorized': False, 'readiness': False, 'new_runtime_conformance_verdicts': 0}, 'no invented operating approval')
    for name, expected in REVIEWED_POLICY.items():
        exact(value[name], expected, 'reviewed policy.' + name)
    return {'scope': 'proposed documentary source/schema consistency only; no contract execution',
            'status': 'PROPOSED_CHAIN_BINDING', 'sources': 32, 'requirements': 9,
            'methods': 13, 'mutations': 8, 'errors': 22, 'events': 2,
            'new_runtime_conformance_verdicts': 0, 'operating_readiness': False}

if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    print(json.dumps(validate(load(root / MANIFEST), root), indent=2))
