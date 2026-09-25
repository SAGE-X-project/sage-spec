"""Check that fixed PoP bytes and KEM selection reject plausible mutations."""

import copy
import json
from pathlib import Path
import unittest

import check_registry_proof_revision as fixture


ROOT = Path(__file__).resolve().parents[1]


class RegistryProofRevisionTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((ROOT / 'verification/vectors/registry-proof-0.10.0.json').read_text())

    def changed(self, update, message):
        candidate = copy.deepcopy(self.record)
        update(candidate)
        with self.assertRaisesRegex(ValueError, message):
            fixture.verify_record(candidate)

    def test_exact_fixture(self):
        self.assertEqual(fixture.verify_record(self.record)['challenge_vectors'], 2)

    def test_field_cannot_be_duplicated(self):
        self.changed(lambda r: r['challenge_vectors'][0].update(
            challenge_hex=r['challenge_vectors'][0]['challenge_hex'] + '00'),
            'trailing or duplicated')

    def test_length_cannot_include_field(self):
        self.changed(lambda r: r['challenge_vectors'][0].update(
            challenge_hex=r['challenge_vectors'][0]['challenge_hex'][:32] + '001a'
            + r['challenge_vectors'][0]['challenge_hex'][36:]), 'field length')

    def test_signing_key_cannot_be_selected_as_kem(self):
        self.changed(lambda r: r['kem_selection'].update(
            selected_kid=r['kem_selection']['record_id'] + '#sign-1'),
            'KEM key selection')

    def test_kem_signature_cannot_be_accepted(self):
        self.changed(lambda r: r['negative_verdicts'][1].update(verdict='accept'),
                     'negative role verdicts')


if __name__ == '__main__':
    unittest.main()
