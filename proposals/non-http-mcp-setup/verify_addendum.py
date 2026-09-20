"""Check document integrity, not protocol execution or normative mapping semantics."""
import copy
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from verify import load, require

ROOT = Path(__file__).resolve().parent
CASE_NAMES = '''plaintext-boundary record-boundary wire-boundary utf8-and-escapes
result-representations post-effect-oversize post-reservation-size-failure
inner-size-replay mutable-buffer synchronous-completion duplicate-completion
old-incarnation bounded-cancellation history-capacity close-before-handoff
close-after-handoff cross-language-setup restart-consumption'''.split()


def inputs():
    return (load(ROOT / 'addendum-cases.json'), load(ROOT / 'reconciliation.json'),
            load(ROOT / 'cases.json'), load(ROOT / 'basis.json'),
            (ROOT / 'addendum.md').read_bytes())


def validate(addendum, mapping, original, basis, text):
    for obj in (addendum, mapping):
        require(obj['status'] == 'PROPOSAL_NOT_ADOPTED', 'adoption claim')
        require(obj['conformance'] == 'NOT_ESTABLISHED', 'conformance claim')
        require(obj['external_review'] == 'NOT_PERFORMED', 'review claim')
        require(obj['lifecycle'] == {'NOT_RUN': 37}, 'historical claim')
    require(addendum['kind'] == 'mcp-setup-supplemental-case-plan', 'plan kind')
    require(addendum['actual_core_execution'] is False, 'execution claim')
    require(addendum['basis_revision'] == '48d5f579cbf781143e0bbed89c8771a3b6367544', 'addendum basis')
    require(addendum['addendum_sha256'] == hashlib.sha256(text).hexdigest(), 'addendum hash')
    require(addendum['original_cases'] == {'NOT_RUN': 40} and
            addendum['supplemental_cases'] == {'NOT_RUN': 18}, 'case totals')
    cases = addendum['cases']
    expected = {'madd-' + name for name in CASE_NAMES}
    require(len(cases) == 18 and {c['id'] for c in cases} == expected, 'supplemental membership')
    for case in cases:
        require(set(case) == {'id', 'obligation', 'input', 'expected', 'planned_method', 'status'}, 'case schema')
        require(case['status'] == 'NOT_RUN', 'case promotion')
        require(case['obligation'] in {'limits', 'owner'}, 'obligation')
        require(case['planned_method'] in {'unit', 'unit_and_local_runtime'}, 'planned method')
        require(all(isinstance(case[k], str) and len(case[k]) >= 15 for k in ('input', 'expected')), 'scenario missing')
    require(mapping['kind'] == 'mcp-adoption-reconciliation' and
            mapping['method'] == 'AUTHORING_AGENT_DOCUMENT_COMPARISON', 'mapping provenance')
    require(mapping['proposal_revision'] == '55949a6b7b0de33f94992db595540ae58c92d13f', 'mapping revision')
    require(mapping['proposal_cases'] == {'NOT_RUN': 40}, 'mapping totals')
    baseline = mapping['local_baseline']
    require(baseline['state'] == 'PRE_EXISTING_UNCOMMITTED_DESIGN' and
            baseline['rule_count'] == 77 and baseline['case_count'] == 386, 'baseline claim')
    files = baseline['files']
    require(set(files) == set(basis['local_design']['files']) | {'verification/traceability.json'}, 'baseline membership')
    for name, digest in basis['local_design']['files'].items():
        require(files[name] == digest, 'baseline disagreement')
    require(files['verification/traceability.json'] == 'c4db008e83ad9491559941ce6cb36960eea4fe3ba1ec6c698d7d77ea91ea009c', 'traceability identity')
    original_cases = {c['id']: c for c in original['cases']}
    require(len(original_cases) == len(original['cases']) == 40, 'original membership')
    require(not expected.intersection(original_cases), 'case namespace collision')
    rows = mapping['mappings']
    require(len(rows) == 8 and {r['proposed_rule'] for r in rows} ==
            {f'MSET-{n:02d}' for n in range(1, 9)}, 'mapping rule membership')
    seen = set()
    for row in rows:
        require(row['disposition'] == 'REVIEW_REQUIRED' and row['execution'] == 'NOT_RUN', 'mapping promotion')
        for field, pattern in [('baseline_rule_ids', r'[A-Z]+-\d{2}'),
                               ('baseline_requirement_ids', r'R-([1-9]|[1-3][0-9]|4[0-5])')]:
            values = row[field]
            require(values and len(values) == len(set(values)) and
                    all(re.fullmatch(pattern, v) for v in values), 'reference syntax')
        require(row['proposed_case_ids'], 'empty mapping')
        for ident in row['proposed_case_ids']:
            require(ident in original_cases and ident not in seen, 'mapping case identity')
            case = original_cases[ident]
            require(case['rule'] == row['proposed_rule'] and case['status'] == 'NOT_RUN', 'mapping case relation')
            seen.add(ident)
    require(seen == set(original_cases), 'incomplete mapping')
    return 58


class Integrity(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(validate(*inputs()), 58)

    def test_false_claims(self):
        for index, key, value in [(0, 'actual_core_execution', True), (0, 'external_review', 'PASS'),
                                  (1, 'status', 'ADOPTED'), (1, 'lifecycle', {'PASS': 37})]:
            values = list(copy.deepcopy(inputs()))
            values[index][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate(*values)

    def test_changed_text(self):
        values = list(inputs())
        values[4] += b'changed'
        with self.assertRaises(ValueError):
            validate(*values)

    def test_case_omission_duplicate_and_promotion(self):
        for mutate in [lambda x: x['cases'].pop(),
                       lambda x: x['cases'].__setitem__(0, x['cases'][1]),
                       lambda x: x['cases'][0].update(status='PASS')]:
            values = list(copy.deepcopy(inputs()))
            mutate(values[0])
            with self.assertRaises(ValueError):
                validate(*values)

    def test_wrong_mapping(self):
        for mutate in [lambda x: x['mappings'][0]['proposed_case_ids'].pop(),
                       lambda x: x['mappings'][0]['proposed_case_ids'].append('missing'),
                       lambda x: x['mappings'][0].update(proposed_rule='MSET-02'),
                       lambda x: x['local_baseline']['files'].update({'spec/05-session.md': '0' * 64})]:
            values = list(copy.deepcopy(inputs()))
            mutate(values[1])
            with self.assertRaises(ValueError):
                validate(*values)

    def test_cli_valid_and_corrupt_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'proposal'
            shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns('__pycache__'))
            command = [sys.executable, str(target / 'verify_addendum.py')]
            result = subprocess.run(command, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('58 planned cases', result.stdout)
            (target / 'addendum.md').write_text('changed')
            result = subprocess.run(command, capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn('PASS', result.stdout)

    def test_cli_duplicate_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'proposal'
            shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns('__pycache__'))
            (target / 'addendum-cases.json').write_text('{"status":0,"status":1}')
            result = subprocess.run([sys.executable, str(target / 'verify_addendum.py')],
                                    capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn('PASS', result.stdout)


if __name__ == '__main__':
    if '--self-test' in sys.argv:
        unittest.main(argv=[sys.argv[0]])
    else:
        try:
            count = validate(*inputs())
        except (ValueError, KeyError, TypeError, OSError) as error:
            print(f'Document consistency FAIL: {error}', file=sys.stderr)
            sys.exit(1)
        print(f'Document consistency PASS: {count} planned cases; protocol NOT_RUN; '
              'no external review or normative mapping semantics verified.')
