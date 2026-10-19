"""Fixed artifact mutations only; no network, signing, command admission or EVM."""
import contextlib
import copy
import io
import json
from pathlib import Path
import runpy
import tempfile
import unittest

from check_chain_map import load, verify

ROOT = Path(__file__).parent
MAPPING = load(ROOT / 'chain-command-map.json')
SIGNATURES = load(ROOT / 'contract-signatures.json')


class ChainMapTests(unittest.TestCase):
    def test_complete_scope_and_cli(self):
        result = verify(MAPPING, SIGNATURES)
        self.assertEqual((result['methods'], result['record_mutations'], result['reads'],
                          result['claim_methods'], result['mapped_input_paths']), (13, 8, 4, 1, 51))
        self.assertEqual(result['contract_execution'], 'NOT_RUN')
        self.assertEqual(result['new_conformance_verdicts'], 0)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            runpy.run_path(str(ROOT / 'check_chain_map.py'), run_name='__main__')
        self.assertEqual(json.loads(output.getvalue()), result)

    def reject(self, mutate, message, signatures=None):
        changed = copy.deepcopy(MAPPING)
        mutate(changed)
        with self.assertRaisesRegex(ValueError, message):
            verify(changed, signatures or SIGNATURES)

    def test_closed_status_and_separate_actor_contracts(self):
        self.reject(lambda x: x.update(extra=True), 'closed map')
        self.reject(lambda x: x.update(status='ADOPTED'), 'candidate status')
        self.reject(lambda x: x['webInputFields'].append('actor'), 'field inventory')
        self.reject(lambda x: x['chainCommandFields'].remove('actor'), 'field inventory')
        self.reject(lambda x: x['derived'].update(actor='tx.origin'), 'derived authority')
        self.reject(lambda x: x['derived'].pop('createSalt'), 'derived authority')
        self.reject(lambda x: x.update(reservedErrors=[]), 'reserved diagnostic')

    def test_limits_are_exact_integers_and_closed(self):
        self.reject(lambda x: x['limits'].update(extra=1), 'limit inventory')
        for value in [True, 128.0, '128', 127]:
            self.reject(lambda x: x['limits'].update(lifetimeKeys=value), 'integer limits')

    def test_methods_and_mutability_are_complete(self):
        self.reject(lambda x: x['methods'].pop('registryId'), 'method inventory')
        self.reject(lambda x: x['methods']['commitClaim'].update(operation='create'), 'method semantics')
        self.reject(lambda x: x['methods']['revealClaim'].update(kind='read'), 'method semantics')
        sig = copy.deepcopy(SIGNATURES)
        sig['historyItem']['mutability'] = 'nonpayable'
        with self.assertRaisesRegex(ValueError, 'mutability'):
            verify(MAPPING, sig)
        sig.pop('registryId')
        with self.assertRaisesRegex(ValueError, 'method inventory'):
            verify(MAPPING, sig)

    def test_exact_input_paths_types_destinations_and_shape(self):
        self.reject(lambda x: x['methods']['record'].update(extra=1), 'closed method')
        self.reject(lambda x: x['methods']['record'].update(inputs=None), 'input rows')
        self.reject(lambda x: x['methods']['record']['inputs'][0].update(extra=1), 'closed input row')
        self.reject(lambda x: x['methods']['record']['inputs'][0].update(path=False), 'input strings')
        self.reject(lambda x: x['methods']['record']['inputs'][0].update(abiType='bytes'), 'ordered ABI')
        self.reject(lambda x: x['methods']['record']['inputs'][0].update(target='actor'), 'input destination')
        self.reject(lambda x: x['methods']['revealClaim']['inputs'].pop(), 'ordered ABI')
        self.reject(lambda x: x['methods']['revealClaim']['inputs'][-1].update(target='arguments.salt'), 'input destination')
        self.reject(lambda x: x['methods']['revealClaim']['inputs'].reverse(), 'ordered ABI')
        for index in [5, 6, 7, 8, 9]:
            self.reject(lambda x: x['methods']['revealClaim']['inputs'][index].update(target='actor'), 'input destination')

    def test_duplicate_layout_and_destination(self):
        changed = copy.deepcopy(MAPPING)
        sig = copy.deepcopy(SIGNATURES)
        changed['methods']['record']['inputs'] *= 2
        sig['record']['inputLayout'] *= 2
        with self.assertRaisesRegex(ValueError, 'unique inputs'):
            verify(changed, sig)

    def test_load_rejects_duplicates_non_json_text_and_size(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'artifact.json'
            cases = [(b'', 'bounded'), (b' ' * 262145, 'bounded'),
                     (b'{"x":1,"\\u0078":2}', 'duplicate'),
                     (b'{"x":NaN}', 'non-JSON'), (b'{"x":"\\ud800"}', 'ASCII'),
                     (b'{"x":"\\n"}', 'ASCII')]
            for raw, message in cases:
                path.write_bytes(raw)
                with self.assertRaisesRegex(ValueError, message):
                    load(path)
            for raw in [b'{', b'\xff']:
                path.write_bytes(raw)
                with self.assertRaises((ValueError, UnicodeError)):
                    load(path)
            path.write_text('{"text":["ordinary",null,true,2]}')
            self.assertEqual(load(path)['text'], ['ordinary', None, True, 2])


if __name__ == '__main__':
    unittest.main()
