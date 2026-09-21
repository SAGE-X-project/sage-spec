"""Validate proposed resolution evidence; no protocol execution."""
import copy
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from verify import load, require
ROOT = Path(__file__).resolve().parent
NAMES = '''close-before-reservation close-after-reservation close-after-admission
crash-after-admission ready-past-setup stale-setup-completion
protected-timeout-before-admission protected-timeout-after-admission
ready-session-expiry signature-intent signature-result signature-carriage
missing-signing-key'''.split()


def inputs():
    return load(ROOT / 'resolutions.json'), {n: (ROOT / n).read_bytes() for n in
        ('design-review.md', 'design-review.json', 'resolutions.md', 'tool.json')}


def validate(record, files):
    require(record['kind'] == 'mcp-design-resolution' and
            record['method'] == 'SAME_AUTHOR_CORRECTION_AND_REREVIEW', 'review method')
    require(record['reviewed_revision'] == '05c9069e651c0b0debb699e329a7e9093a466741', 'review revision')
    for key, expected in dict(external_review='NOT_PERFORMED', adoption='PROPOSAL_NOT_ADOPTED',
                             conformance='NOT_ESTABLISHED', protocol_cases={'NOT_RUN': 71},
                             lifecycle={'NOT_RUN': 37}).items():
        require(record[key] == expected, 'unsupported claim: ' + key)
    require(set(record['files']) == set(files), 'file membership')
    for name, data in files.items():
        require(record['files'][name] == hashlib.sha256(data).hexdigest(), 'file hash')
    cases = record['cases']
    require(len(cases) == 13 and {c['id'] for c in cases} == {'mres-' + n for n in NAMES}, 'case membership')
    for case in cases:
        require(set(case) == {'id', 'finding', 'input', 'expected', 'status', 'planned_method'}, 'case schema')
        require(case['status'] == 'NOT_RUN' and case['planned_method'] == 'unit_and_bounded_local_runtime', 'case execution')
        require(all(isinstance(case[k], str) and len(case[k]) >= 15 for k in ('input', 'expected')), 'missing scenario')
    findings = record['findings']
    require(len(findings) == 3 and {f['id'] for f in findings} == {'DREV-01', 'DREV-02', 'DREV-03'}, 'finding membership')
    seen = set()
    for finding in findings:
        require(finding['status'] == 'RESOLVED_IN_DRAFT' and finding['execution'] == 'NOT_RUN', 'resolution promotion')
        identifiers = finding['case_ids']
        require(identifiers and len(identifiers) == len(set(identifiers)), 'duplicate or empty mapping')
        require(set(identifiers) == {c['id'] for c in cases if c['finding'] == finding['id']}, 'case relation')
        require(not seen.intersection(identifiers), 'duplicate coverage')
        seen.update(identifiers)
    require(seen == {c['id'] for c in cases}, 'missing coverage')


class Integrity(unittest.TestCase):
    def test_valid(self):
        validate(*inputs())

    def test_changed_sources(self):
        for name in inputs()[1]:
            record, files = inputs()
            files[name] += b'changed'
            with self.subTest(name=name), self.assertRaises(ValueError):
                validate(record, files)

    def test_promotion(self):
        for mutate in (lambda r: r.update(external_review='PASS'),
                       lambda r: r['findings'][0].update(status='RESOLVED'),
                       lambda r: r['cases'][0].update(status='PASS')):
            record, files = inputs()
            mutate(record)
            with self.assertRaises(ValueError):
                validate(record, files)

    def test_wrong_membership(self):
        for mutate in (lambda r: r['cases'].pop(),
                       lambda r: r['cases'].__setitem__(0, copy.deepcopy(r['cases'][1])),
                       lambda r: r['findings'][0]['case_ids'].append('missing'),
                       lambda r: r['cases'][0].update(finding='DREV-03')):
            record, files = inputs()
            mutate(record)
            with self.assertRaises(ValueError):
                validate(record, files)

    def test_cli_valid_and_changed_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / 'proposal'
            shutil.copytree(ROOT, dest, ignore=shutil.ignore_patterns('__pycache__'))
            command = [sys.executable, '-B', str(dest / 'verify_resolutions.py')]
            result = subprocess.run(command, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('NOT_RUN', result.stdout)
            (dest / 'resolutions.md').write_text('changed')
            result = subprocess.run(command, capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn('PASS', result.stdout)


if __name__ == '__main__':
    if '--self-test' in sys.argv:
        unittest.main(argv=[sys.argv[0]])
    else:
        try:
            validate(*inputs())
        except (ValueError, KeyError, TypeError, OSError) as error:
            print(f'Resolution consistency FAIL: {error}', file=sys.stderr)
            sys.exit(1)
        print('Resolution consistency PASS: three draft resolutions, 13 new planned cases NOT_RUN; no external review.')
