"""Finite metadata refusal schedules and independent schema-capacity controls."""
from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path
import runpy
import tempfile
import unittest

import check_registry_management as guard

ROOT = Path(__file__).resolve().parents[1]

class RegistryManagementTests(unittest.TestCase):
    def setUp(self):
        self.value = guard.load(ROOT / guard.MANIFEST)

    def test_fixed_public_contract(self):
        actual = guard.validate(self.value, ROOT)
        self.assertEqual((actual['sources'], actual['methods'], actual['mutations']), (32, 13, 8))
        self.assertEqual((actual['errors'], actual['events']), (22, 2))
        self.assertEqual(actual['new_runtime_conformance_verdicts'], 0)
        self.assertIs(actual['operating_readiness'], False)

    def test_top_level_and_nested_type_refusals(self):
        for value in [None, [], {}, dict(self.value, extra=1)]:
            with self.subTest(value=type(value).__name__), self.assertRaises(ValueError):
                guard.validate(value, ROOT)
        for field in ['limits', 'methods', 'algorithms', 'schemas', 'lifecycle', 'source_sha256']:
            value = deepcopy(self.value)
            value[field] = []
            with self.subTest(field=field), self.assertRaises(ValueError):
                guard.validate(value, ROOT)

    def test_metadata_cannot_change_adoption_or_authorize_operations(self):
        for field, replacement in [('status', 'PROPOSED_CHAIN_BINDING'), ('adoption', 'IMPLICIT'),
                                   ('revision', True), ('protocol_version', '0.10.0'),
                                   ('source_revision', 'main')]:
            value = deepcopy(self.value)
            value[field] = replacement
            with self.subTest(field=field), self.assertRaises(ValueError):
                guard.validate(value, ROOT)
        for field, replacement in [('readiness', True), ('compiler', 'fixture'),
                                   ('deployment_authorized', True), ('gas_budget', 5000000000),
                                   ('new_runtime_conformance_verdicts', False)]:
            value = deepcopy(self.value)
            value['implementation_and_operating'][field] = replacement
            with self.subTest(field=field), self.assertRaises(ValueError):
                guard.validate(value, ROOT)

    def test_authority_roles_and_irreversible_boundaries(self):
        cases = [
            ('principal', 'source', 'tx.origin'),
            ('principal', 'controller_transfer', True),
            ('algorithms', 'mandatory_signing', ['Ed25519']),
            ('algorithms', 'kem_only', ['ed25519']),
            ('algorithms', 'new_kem_admission_narrowing', True),
            ('grants', 'operator_may_delegate', True),
            ('source_evidence', 'outer_receipt_sufficient', True),
            ('source_evidence', 'automatic_fork_selection', True),
            ('headroom', 'old_profile_reads_affected', True),
            ('headroom', 'version_exhaustion_bypass', True),
            ('headroom', 'fixed_subtraction_equivalent', True),
        ]
        for group, field, replacement in cases:
            value = deepcopy(self.value)
            value[group][field] = replacement
            with self.subTest(group=group, field=field), self.assertRaises(ValueError):
                guard.validate(value, ROOT)

    def test_exact_source_domain_method_and_schema_inventory(self):
        cases = [
            lambda v: v['source_sha256'].pop('spec/09-registry.md'),
            lambda v: v['source_sha256'].update({'../outside': '0' * 64}),
            lambda v: v['domains']['registry_claim'].update(value='sage-claim-0.11.0'),
            lambda v: v['methods'].pop('deactivate'),
            lambda v: v['methods']['revealClaim'].update(maximum_calldata_bytes=136516),
            lambda v: v['schemas']['chain_command'].remove('actor'),
            lambda v: v['schemas']['arguments']['create'].remove('salt'),
            lambda v: v['errors'].remove('ClaimMismatch'),
            lambda v: v['reserved_errors'].append('InvalidKeyProof'),
            lambda v: v['events']['ClaimCommitted']['layout'].reverse(),
            lambda v: v['lifecycle']['revoke-key'].__setitem__(0, 'active'),
            lambda v: v['rank8']['add-key'].reverse(),
            lambda v: v['guard_order'].reverse(),
            lambda v: v['excluded'].__setitem__(0, 'implicit-companion'),
            lambda v: v['grammar'].update(key_name='[A-Za-z0-9._-]{1,32}'),
            lambda v: v['requirements'].pop(),
        ]
        for index, mutate in enumerate(cases):
            value = deepcopy(self.value)
            mutate(value)
            with self.subTest(schedule=index), self.assertRaises(ValueError):
                guard.validate(value, ROOT)

    def test_bounds_are_exact_integers_and_preserve_required_capacity(self):
        for name in ['lifetime_keys', 'services', 'active_grants', 'claim_window_blocks']:
            value = deepcopy(self.value)
            value['limits'][name] -= 1
            with self.subTest(name=name), self.assertRaises(ValueError):
                guard.validate(value, ROOT)
        for replacement in [True, 128.0, '128']:
            value = deepcopy(self.value)
            value['limits']['lifetime_keys'] = replacement
            with self.subTest(replacement=replacement), self.assertRaises(ValueError):
                guard.validate(value, ROOT)

    def test_json_duplicates_nonfinite_and_malformed_are_not_lost(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'fixed.json'
            for text in ['{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}', '{']:
                path.write_text(text)
                with self.subTest(text=text), self.assertRaises(ValueError):
                    guard.load(path)

    def test_document_and_frozen_file_changes_are_detected(self):
        # Separate scratch files, never edits to the repository or public sources.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = set(self.value['source_sha256']) | {guard.DOCUMENT}
            for name in paths:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / name).read_bytes())
            value = deepcopy(self.value)
            value['document'] = '../outside'
            with self.assertRaises(ValueError):
                guard.validate(value, root)
            doc = root / guard.DOCUMENT
            original = doc.read_bytes()
            doc.write_bytes(original + b'changed')
            with self.assertRaises(ValueError):
                guard.validate(self.value, root)
            doc.write_bytes(original)
            fixed = root / 'spec/09-registry.md'
            fixed.write_bytes(fixed.read_bytes() + b'changed')
            with self.assertRaises(ValueError):
                guard.validate(self.value, root)
            fixed.write_bytes((ROOT / 'spec/09-registry.md').read_bytes())
            selected = root / 'profiles/sage-0.11.0/README.md'
            selected.write_bytes(selected.read_bytes() + b'changed')
            with self.assertRaises(ValueError):
                guard.validate(self.value, root)

    def test_independent_capacity_arithmetic(self):
        # Literal schema examples, not generated calldata, signatures or submissions.
        compact = lambda v: json.dumps(v, ensure_ascii=True, separators=(',', ':'))
        pair = {'operator': '0x' + 'f' * 40, 'scope': 'update-services'}
        self.assertEqual(len(compact(pair)), 83)
        self.assertEqual(len(compact([pair] * 128)), 10753)
        self.assertLess(10753 + 1024, self.value['limits']['history_bytes'])
        self.assertLess(65536 + 4096, self.value['limits']['command_bytes'])
        prefix = b'sage-pop-0.11.0'
        fields = [b'eip155:' + b'1' * 32 + b':' + b'0x' + b'f' * 40,
                  b'a' * 64, b'k' * 32, b'sage-secp256k1-keccak256', b'\x04' + b'\x01' * 64]
        framed = prefix + b''.join(len(field).to_bytes(2, 'big') + field for field in fields)
        self.assertEqual([len(field) for field in fields], [82, 64, 32, 24, 65])
        self.assertEqual(max(map(len, self.value['algorithms']['mandatory_signing'] + self.value['algorithms']['optional_signing'])), self.value['limits']['algorithm_bytes'])
        self.assertEqual(len(prefix), 15)
        self.assertEqual(len(framed), 292)
        self.assertEqual(framed[:19], b'sage-pop-0.11.0\x00Rei')

    def test_cli_states_no_execution_or_readiness(self):
        stream = io.StringIO()
        with redirect_stdout(stream):
            runpy.run_path(str(ROOT / 'verification/check_registry_management.py'), run_name='__main__')
        result = json.loads(stream.getvalue())
        self.assertEqual(result['status'], 'ADOPTED_CHAIN_MANAGEMENT_BINDING')
        self.assertIs(result['operating_readiness'], False)
        self.assertEqual(result['new_runtime_conformance_verdicts'], 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
