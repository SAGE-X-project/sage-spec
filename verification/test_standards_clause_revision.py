"""Regression checks for the active and historical standards revision gates."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from check_standards_clause_revision import ROOT, verify, verify_current_sources
from check_standards_scope_revision import verify as verify_prior_scope
from check_mcp_independent_llm_rereview import verify as verify_prior_llm


class StandardsClauseRevisionTests(unittest.TestCase):
    def test_current_and_historical_sources_pass(self):
        self.assertEqual(verify(ROOT)['planned_cases'], 489)

    def test_current_source_change_fails(self):
        record = json.loads((ROOT / 'verification/standards-clause-revision.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory)
            for name in record['current_sha256']:
                target = copy / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, target)
            target = copy / 'spec/03-rfc9421.md'
            target.write_text(target.read_text().replace('`ed25519`', '`rsa`', 1))
            with self.assertRaisesRegex(ValueError, 'current source bytes'):
                verify_current_sources(copy, record)

    def test_evidence_promotion_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory)
            shutil.copytree(ROOT, copy, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns('.git', '__pycache__'))
            path = copy / 'verification/standards-clause-revision.json'
            record = json.loads(path.read_text())
            record['conformance'] = 'ESTABLISHED'
            path.write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError, 'unsupported evidence promotion'):
                verify(copy)

    def test_historical_source_change_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory)
            shutil.copytree(ROOT, copy, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns('.git', '__pycache__'))
            path = copy / 'verification/history/standards-clauses-base-2026-09-29/spec/03-rfc9421.md'
            path.write_text(path.read_text() + '\nchanged\n')
            with self.assertRaisesRegex(ValueError, 'historical source bytes'):
                verify(copy)

    def test_historical_checks_still_reject_current_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory)
            shutil.copytree(ROOT, copy, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns('.git', '__pycache__'))
            path = copy / 'spec/03-rfc9421.md'
            path.write_text(path.read_text() + '\nchanged\n')
            for check in (verify_prior_scope, verify_prior_llm):
                with self.subTest(check=check.__name__):
                    with self.assertRaisesRegex(ValueError, 'current source bytes'):
                        check(copy)


if __name__ == '__main__':
    unittest.main()
