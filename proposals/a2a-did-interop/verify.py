"""Check the A2A and DID proposal's traceability only.

This runs no A2A exchange, DID resolution or cryptography. It checks that the
proposal is still a proposal, that its basis pins exact sources and related
projects, that every rule group has positive and negative planned cases, and
that the external review guide neither claims adoption nor drifts from the
pinned revisions.
"""
import copy
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parent
RULES = {f'A2AB-{n:02d}' for n in range(1, 8)} | {f'DIDP-{n:02d}' for n in range(1, 6)}
OUTCOMES = {'ACCEPT', 'REJECT', 'NOT_ELIGIBLE', 'ABORT', 'PROJECT', 'ERROR'}
NEGATIVE = {'REJECT', 'NOT_ELIGIBLE', 'ABORT', 'ERROR'}
POSITIVE = {'ACCEPT', 'PROJECT'}
SOURCES = {'a2a-specification', 'a2a-proto', 'did-core-1.0', 'did-1.1', 'did-1.1-context',
           'did-resolution', 'cid-1.0', 'rfc8785', 'rfc7515', 'rfc9864', 'rfc9457'}
HEX64 = '[0-9a-f]{64}'
HEX40 = '[0-9a-f]{40}'
DID11_CONTEXT_SHA256 = 'ea216ecc1cb02cd39b693dba2250141e270ba0bf95890be107dd9a9e8e43de85'
RELATED = {'did-go', 'did-inspector'}
DATE = '[0-9]{4}-[0-9]{2}-[0-9]{2}'


def unique(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError('duplicate JSON member')
        value[key] = item
    return value


def load(path):
    return json.loads(path.read_bytes(), object_pairs_hook=unique)


def require(value, message):
    if not value:
        raise ValueError(message)


def check_basis(basis):
    require(set(basis) == {'kind', 'status', 'conformance', 'sage_version', 'a2a_protocol_version',
                           'did_projections', 'reviewed', 'sage_baseline', 'external_sources',
                           'related_projects', 'hash_note', 'related_note'},
            'closed basis')
    require(basis['kind'] == 'proposal-basis' and basis['status'] == 'PROPOSAL_NOT_ADOPTED' and
            basis['conformance'] == 'NOT_ESTABLISHED', 'proposal promotion')
    require(basis['sage_version'] == '0.10.0' and basis['a2a_protocol_version'] == '1.0' and
            basis['did_projections'] == ['did-core-1.0', 'did-1.1'], 'version scope')
    baseline = basis['sage_baseline']
    require(set(baseline) == {'normative_source_revision', 'branch_base_revision'} and
            all(re.fullmatch(HEX40, v) for v in baseline.values()), 'baseline revisions')
    sources = basis['external_sources']
    require(set(sources) == SOURCES, 'external source set')
    for name, row in sources.items():
        require(set(row) == {'url', 'revision', 'status', 'sha256'}, 'source schema: ' + name)
        require(row['url'].startswith('https://') and re.fullmatch(HEX64, row['sha256']), 'source pin: ' + name)
        require(all(type(row[k]) is str and row[k] for k in ('revision', 'status')), 'source status: ' + name)
    require(sources['did-1.1-context']['sha256'] == DID11_CONTEXT_SHA256, 'DID 1.1 context digest')
    require('/v1.0.1/' in sources['a2a-specification']['url'] and '/v1.0.1/' in sources['a2a-proto']['url'],
            'A2A release pin')
    require(sources['did-1.1']['status'] == 'W3C Candidate Recommendation Snapshot' and
            sources['did-resolution']['status'] == 'W3C Candidate Recommendation Draft' and
            sources['did-core-1.0']['status'] == 'W3C Recommendation', 'W3C maturity is stated, not promoted')
    check_related(basis['related_projects'])
    require(type(basis['related_note']) is str and 'adopt no rule' in basis['related_note'], 'related note')


def check_related(related):
    require(set(related) == RELATED, 'related project set')
    for name, row in related.items():
        require(set(row) == {'repository', 'revision', 'observed', 'license', 'role', 'evidence'},
                'related schema: ' + name)
        require(row['repository'] == 'https://github.com/SAGE-X-project/' + name and
                re.fullmatch(HEX40, row['revision']) and re.fullmatch(DATE, row['observed']), 'related pin: ' + name)
        require(type(row['role']) is str and row['role'] and type(row['evidence']) is list, 'related role: ' + name)
    require('not implemented before adoption' in related['did-go']['role'], 'advanced/sage status')
    require(related['did-go']['evidence'] == [] and len(related['did-inspector']['evidence']) == 2,
            'inspector evidence set')
    for report in related['did-inspector']['evidence']:
        require(set(report) == {'path', 'sha256', 'profile', 'subject', 'subject_revision', 'requirement'},
                'evidence schema')
        require(report['path'].startswith('docs/evidence/') and re.fullmatch(HEX64, report['sha256']), 'evidence pin')
        require(report['subject'] == 'did-go' and len(report['subject_revision']) >= 7 and
                related['did-go']['revision'].startswith(report['subject_revision']), 'evidence subject revision')
        counts = report['requirement']
        require(set(counts) == {'statements', 'PASS', 'FAIL', 'NOT_APPLICABLE', 'NOT_RUN'} and
                all(type(v) is int and v >= 0 for v in counts.values()) and
                counts['statements'] == sum(v for k, v in counts.items() if k != 'statements'),
                'evidence totals')
    require([r['profile'] for r in related['did-inspector']['evidence']] == ['did-core-1.0', 'did-1.1'],
            'evidence profiles')


def check_plan(plan, text):
    require(plan['kind'] == 'proposal-case-plan' and plan['status'] == 'NOT_RUN' and
            plan['conformance'] == 'NOT_ESTABLISHED' and set(plan) == {'kind', 'status', 'conformance', 'cases'},
            'plan promotion')
    headings = re.findall(r'^## ((?:A2AB|DIDP)-\d{2}): ', text, re.M)
    require(len(headings) == len(set(headings)) and set(headings) == RULES, 'rule catalog')
    seen = set()
    covered, positive, negative = ({r: 0 for r in RULES} for _ in range(3))
    for case in plan['cases']:
        keys = {'id', 'rule', 'precondition', 'input', 'expected', 'status', 'evidence'}
        if case.get('expected') in ('ERROR', 'PROJECT') or 'detail' in case:
            keys = keys | {'detail'}
        require(set(case) == keys, 'case schema: ' + str(case.get('id')))
        require(case['id'] not in seen and case['id'].startswith(case['rule'].lower() + '-'), 'case identity')
        seen.add(case['id'])
        require(case['rule'] in RULES and case['status'] == 'NOT_RUN', 'case promotion or rule')
        require(case['expected'] in OUTCOMES, 'undefined outcome')
        require(all(type(case[k]) is str and len(case[k]) >= 15 for k in keys - {'id', 'rule', 'expected', 'status'}),
                'missing scenario evidence')
        covered[case['rule']] += 1
        positive[case['rule']] += case['expected'] in POSITIVE
        negative[case['rule']] += case['expected'] in NEGATIVE
    require(all(n >= 3 for n in covered.values()), 'missing rule cases')
    require(all(positive[r] >= 1 and negative[r] >= 1 for r in RULES), 'missing positive or negative case')
    return len(seen)


def check_text(text):
    require(text.startswith('# A2A 1.0 binding and DID 1.0/1.1 projection proposal\n'), 'title')
    require('Status: **proposed design, not adopted**.' in text, 'status statement')
    flat = ' '.join(text.split())
    for phrase in ('is not adoption or a protocol release', 'Every planned case is `NOT_RUN`',
                   'not a Recommendation', 'never an alias', 'never fetched'):
        require(phrase in flat, 'required statement: ' + phrase)
    require('—' not in text, 'em dash in proposal text')


def check_pins(basis, text, guide):
    related = basis['related_projects']
    for name, row in related.items():
        require(row['revision'] in text and row['revision'] in guide, 'related revision not cited: ' + name)
    for report in related['did-inspector']['evidence']:
        counts = report['requirement']
        phrase = '{} PASS and 0 FAIL of {}'.format(counts['PASS'], counts['statements'])
        require(counts['FAIL'] > 0 or phrase in ' '.join(text.split()), 'evidence totals not cited: ' + report['profile'])


def check_guide(guide):
    require(guide.startswith('# External review guide: A2A 1.0 binding and DID 1.0/1.1 projections\n'),
            'guide title')
    flat = ' '.join(guide.split())
    for phrase in ('proposed design, not adopted', 'Every planned case is `NOT_RUN`',
                   'python3 -B proposals/a2a-did-interop/verify.py --self-test'):
        require(phrase in flat, 'required guide statement: ' + phrase)
    for n in range(1, 6):
        require('### OPEN-{}'.format(n) in guide, 'guide lacks OPEN-{}'.format(n))
    require(flat.count('Recommendation to the reviewers') >= 5, 'recommendations are not marked')
    require('—' not in guide, 'em dash in guide text')


def validate(basis, plan, text, guide):
    check_basis(basis)
    check_text(text)
    check_guide(guide)
    check_pins(basis, text, guide)
    return check_plan(plan, text)


def inputs():
    return (load(ROOT / 'basis.json'), load(ROOT / 'cases.json'), (ROOT / 'README.md').read_text(),
            (ROOT / 'external-review.md').read_text())


class Integrity(unittest.TestCase):
    def setUp(self):
        self.values = inputs()

    def refused(self, change):
        values = list(copy.deepcopy(self.values))
        change(values)
        with self.assertRaises(ValueError):
            validate(*values)

    def test_valid(self):
        self.assertEqual(validate(*self.values), 90)

    def test_promotion(self):
        self.refused(lambda v: v[0].update(status='ADOPTED'))
        self.refused(lambda v: v[1].update(status='PASS'))
        self.refused(lambda v: v[1]['cases'][0].update(status='PASS'))
        self.refused(lambda v: v[0]['external_sources']['did-1.1'].update(status='W3C Recommendation'))

    def test_missing_rule_or_negative(self):
        self.refused(lambda v: v[1].update(cases=[c for c in v[1]['cases'] if c['rule'] != 'A2AB-04']))
        self.refused(lambda v: v[1].update(cases=[c for c in v[1]['cases']
                                                  if not (c['rule'] == 'A2AB-03' and c['expected'] != 'ACCEPT')]))
        self.refused(lambda v: v[1].update(cases=[c for c in v[1]['cases']
                                                  if not (c['rule'] == 'A2AB-06' and c['expected'] == 'ACCEPT')]))

    def test_duplicate_and_schema(self):
        self.refused(lambda v: v[1]['cases'].append(v[1]['cases'][0]))
        self.refused(lambda v: v[1]['cases'][0].update(extra='x'))
        self.refused(lambda v: v[1]['cases'][-1].pop('detail'))
        self.refused(lambda v: v[1]['cases'][0].update(expected='PASS'))

    def test_source_pins(self):
        self.refused(lambda v: v[0]['external_sources'].pop('rfc9864'))
        self.refused(lambda v: v[0]['external_sources']['did-1.1-context'].update(sha256='0' * 64))
        self.refused(lambda v: v[0]['sage_baseline'].update(branch_base_revision='main'))

    def test_related_projects(self):
        self.refused(lambda v: v[0]['related_projects'].pop('did-inspector'))
        self.refused(lambda v: v[0]['related_projects']['did-go'].update(revision='main'))
        self.refused(lambda v: v[0]['related_projects']['did-go'].update(role='implements advanced/sage'))
        self.refused(lambda v: v[0]['related_projects']['did-inspector']['evidence'][0].update(subject_revision='0000000'))
        self.refused(lambda v: v[0]['related_projects']['did-inspector']['evidence'][1]['requirement'].update(PASS=308))
        self.refused(lambda v: v[0]['related_projects']['did-go'].update(revision='0' * 40))
        self.refused(lambda v: v[0].pop('related_note'))

    def test_guide(self):
        self.refused(lambda v: v.__setitem__(3, v[3].replace('proposed design, not adopted', 'adopted design')))
        self.refused(lambda v: v.__setitem__(3, v[3].replace('### OPEN-4', '### Service type')))
        self.refused(lambda v: v.__setitem__(3, v[3].replace('Recommendation to the reviewers', 'Decision')))
        self.refused(lambda v: v.__setitem__(3, v[3] + '\nAdopted \u2014 done.\n'))

    def test_text(self):
        self.refused(lambda v: v.__setitem__(2, v[2].replace('## DIDP-05: ', '## DIDP-5: ')))
        self.refused(lambda v: v.__setitem__(2, v[2].replace('never an alias', 'an alias')))
        self.refused(lambda v: v.__setitem__(2, v[2] + '\n## A2AB-01: Duplicate\n'))


def main():
    if '--self-test' in sys.argv:
        result = unittest.main(argv=[sys.argv[0]], exit=False).result
        sys.exit(0 if result.wasSuccessful() else 1)
    print(json.dumps({'status': 'PROPOSAL_NOT_ADOPTED', 'cases': validate(*inputs()), 'execution': 'NOT_RUN'}))


if __name__ == '__main__':
    main()
