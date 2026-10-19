"""Check candidate metadata coverage; never admit a command or call a chain."""
import json
import re
from pathlib import Path

FIELDS = {
    'webInputFields': ['binding', 'registry', 'did', 'operation', 'expectedVersion', 'arguments'],
    'chainCommandFields': ['binding', 'registry', 'did', 'operation', 'expectedVersion', 'arguments', 'actor'],
    'historyFields': ['version', 'previousVersion', 'actor', 'operation', 'commandDigest', 'target',
                      'automaticRemovals', 'admitted', 'recordDigest', 'grantsDigest'],
}
DERIVED = {'binding': 'configured binding', 'registry': 'configured registry',
           'did': 'configured registry and exact agentId', 'actor': 'actual Registry msg.sender',
           'initialKeyState': 'accepted', 'createExpectedVersion': '',
           'createSalt': 'revealed ABI bytes32; canonical base64url'}
LIMITS = {'recordBytes': 65536, 'historyItemBytes': 262144, 'commandItemBytes': 262144,
          'lifetimeKeys': 128, 'services': 16, 'activeGrants': 128}
OPERATIONS = {'revealClaim': 'create', 'activate': 'activate', 'addKey': 'add-key',
              'revokeKey': 'revoke-key', 'updateServices': 'update-services',
              'authorizeOperator': 'authorize-operator', 'revokeOperator': 'revoke-operator',
              'deactivate': 'deactivate'}
READS = {'registryId', 'record', 'activeGrants', 'historyItem'}
SCOPE = 'candidate argument mapping only; Registry execution NOT_RUN'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    raw = path.read_bytes()
    require(0 < len(raw) <= 262144, 'bounded artifact')

    def pairs(rows):
        result = {}
        for k, v in rows:
            require(k not in result, 'duplicate artifact member')
            result[k] = v
        return result

    def invalid_constant(value):
        raise ValueError('non-JSON constant')

    value = json.loads(raw.decode('utf-8'), object_pairs_hook=pairs, parse_constant=invalid_constant)

    def ascii_strings(node):
        if isinstance(node, str):
            require(all(32 <= ord(c) <= 126 for c in node), 'ASCII artifact text')
        elif isinstance(node, list):
            for v in node:
                ascii_strings(v)
        elif isinstance(node, dict):
            for k, v in node.items():
                ascii_strings(k)
                ascii_strings(v)

    ascii_strings(value)
    return value


def verify(mapping, signatures):
    require(type(mapping) is dict and set(mapping) == set(FIELDS) |
            {'status', 'scope', 'derived', 'limits', 'reservedErrors', 'methods'}, 'closed map')
    require(mapping['status'] == 'UNADOPTED' and mapping['scope'] == SCOPE, 'candidate status')
    for k, expected in FIELDS.items():
        require(mapping[k] == expected, 'exact field inventory')
    require(mapping['derived'] == DERIVED, 'derived authority and salt')
    require(type(mapping['limits']) is dict and set(mapping['limits']) == set(LIMITS), 'limit inventory')
    require(all(type(mapping['limits'][k]) is int and mapping['limits'][k] == v
                for k, v in LIMITS.items()), 'exact integer limits')
    require(mapping['reservedErrors'] == ['ClaimMismatch'], 'reserved diagnostic')
    expected_methods = set(OPERATIONS) | READS | {'commitClaim'}
    methods = mapping['methods']
    require(type(methods) is dict and set(methods) == expected_methods == set(signatures), 'method inventory')
    input_count = 0
    for name, method in methods.items():
        require(type(method) is dict and set(method) == {'kind', 'operation', 'inputs'}, 'closed method')
        kind = 'mutation' if name in OPERATIONS else 'read' if name in READS else 'claim'
        require(method['kind'] == kind and method['operation'] == OPERATIONS.get(name), 'method semantics')
        rows = method['inputs']
        require(type(rows) is list, 'input rows')
        layouts, targets = [], []
        for row in rows:
            require(type(row) is dict and set(row) == {'path', 'abiType', 'target'}, 'closed input row')
            require(all(type(v) is str for v in row.values()), 'exact input strings')
            layouts.append(row['path'] + ':' + row['abiType'])
            targets.append(row['target'])
            path = row['path']
            if path == 'agentId':
                expected = 'read.agentId' if kind == 'read' else 'did.agentId'
            elif path == 'expectedVersion':
                expected = 'expectedVersion/decimal'
            elif path == 'version':
                expected = 'read.version/decimal'
            elif path == 'commitment':
                expected = 'claim.commitment'
            elif path == 'salt':
                expected = 'arguments.salt/base64url'
            else:
                base = re.sub(r'^entry(?=\.|$)', 'key', path)
                base = base.replace('.serviceType', '.type').replace('.signer', '.proof.signer')
                base = re.sub(r'\.proof$', '.proof.value', base)
                base = base.replace('.hasExpiry', '.expires/presence')
                suffix = '/base64url' if path.endswith(('.key', '.proof')) else ''
                suffix = '/value' if path.endswith('.expires') else suffix
                suffix = '/address' if path in {'controller', 'operator'} else suffix
                expected = 'arguments.' + base + suffix
            require(row['target'] == expected, 'exact input destination')
        require(layouts == signatures[name]['inputLayout'], 'complete ordered ABI input coverage')
        require(len(layouts) == len(set(layouts)) and len(targets) == len(set(targets)), 'unique inputs and destinations')
        require(signatures[name]['mutability'] == ('view' if kind == 'read' else 'nonpayable'), 'ABI mutability')
        input_count += len(rows)
    return {'scope': SCOPE, 'status': 'UNADOPTED', 'methods': len(methods),
            'record_mutations': len(OPERATIONS), 'reads': len(READS), 'claim_methods': 1,
            'mapped_input_paths': input_count, 'contract_execution': 'NOT_RUN', 'new_conformance_verdicts': 0}


if __name__ == '__main__':
    root = Path(__file__).parent
    print(json.dumps(verify(load(root / 'chain-command-map.json'), load(root / 'contract-signatures.json'))))
