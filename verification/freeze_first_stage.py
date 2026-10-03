"""Bind the reviewed, unreleased 0.10.0 design to exact source bytes."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / 'verification/first-stage-baseline.json'
SOURCE_REVISION = '1820ab5eafb843e1c13f4c46c34aeeb28d934ac9'
SOURCES = (
    'charter.md', 'PROCESS.md', 'CHANGELOG.md',
    'profiles/agent-mcp-security.md',
    'profiles/non-http-mcp-security.md',
    'profiles/non-http-mcp-tool.json',
    *(f'spec/{number:02d}-{name}.md' for number, name in enumerate((
        'overview', 'crypto', 'jcs', 'rfc9421', 'hpke', 'session',
        'did-sage', 'a2a', 'transport', 'registry', 'resolution', 'registries'))),
    'verification/traceability.json',
    'verification/standards-application-matrix.md',
    'verification/vectors/registry-operator-0.10.0.json',
    'verification/vectors/web-registry-media-0.10.0.json',
    'verification/vectors/standards-clauses-0.10.0.json',
    *(f'vectors/{name}.json' for name in (
        'crypto', 'did', 'hpke', 'jcs', 'rfc9421', 'session')),
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def inspect(root=ROOT):
    trace = json.loads((root / 'verification/traceability.json').read_bytes())
    operators = json.loads((root / 'verification/vectors/registry-operator-0.10.0.json').read_bytes())
    standards = (root / 'verification/standards-application-matrix.md').read_text()
    rules = {item['id']: item for item in trace['rules']}
    cases = {item['id']: item for item in trace['cases']}
    children = {item['id']: item for item in trace['mandatory_subscenarios']}
    require(trace['protocol_version'] == '0.10.0' and
            len(trace['requirements']) == 45 and len(rules) == 91 and
            len(cases) == 489 and len(children) == 26,
            'normative traceability inventory')
    require(len(operators['cases']) == 17 and
            len({row['id'] for row in operators['cases']}) == 17,
            'operator subcondition inventory')
    for row in operators['cases']:
        parent = cases.get(row['parent_case_id'])
        require(parent is not None and parent['rule_id'] in ('REG-03', 'REG-08')
                and row['expected'] and row['precondition']
                and row['evidence_status'] == 'planned_not_executed',
                'unmapped operator subcondition: ' + row['id'])
    for rule in rules.values():
        source = root / rule['source']
        lines = source.read_text().splitlines()
        require(1 <= rule['line'] <= len(lines) and
                rule['id'] in lines[rule['line'] - 1],
                'rule source anchor: ' + rule['id'])
    source_rows = [line for line in standards.splitlines() if line.startswith('| [')]
    require(len(source_rows) == 22, 'standards source rows')
    if (root / '.git').exists():
        for name in SOURCES:
            committed = subprocess.check_output(
                ['git', 'show', f'{SOURCE_REVISION}:{name}'],
                cwd=root, timeout=10)
            require((root / name).read_bytes() == committed,
                    'source differs from frozen revision: ' + name)
    return {
        'schema_version': 1,
        'kind': 'sage-0.10.0-first-stage-design-baseline',
        'protocol_version': '0.10.0',
        'normative_source_revision': SOURCE_REVISION,
        'status': 'DESIGN_BASELINE_REVIEWED_INSPECTOR_PENDING',
        'counts': {'requirements': 45, 'rule_groups': 91, 'parent_cases': 489,
                   'traceability_children': 26, 'operator_subconditions': 17,
                   'standards_sources': 22},
        'source_sha256': {name: digest(root / name) for name in SOURCES},
        'implementation_conformance': 'NOT_ESTABLISHED',
        'independent_external_audit': 'NOT_PERFORMED',
    }


def verify(root=ROOT):
    actual = json.loads((root / 'verification/first-stage-baseline.json').read_bytes())
    require(actual == inspect(root), 'first-stage design baseline drift')
    return actual


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    try:
        result = inspect()
        if args.write:
            RECORD.write_text(json.dumps(result, indent=2) + '\n')
        else:
            verify()
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as error:
        parser.exit(1, 'First-stage baseline FAIL: ' + str(error) + '\n')
    print('First-stage design baseline PASS: 489 parents, 26 children, 17 operator subconditions')


if __name__ == '__main__':
    main()
