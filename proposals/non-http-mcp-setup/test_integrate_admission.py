import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from integrate_admission import ROOT, render


class IntegrationTests(unittest.TestCase):
    def test_complete_effective_plan_and_no_promotion(self):
        outputs=render();plan=json.loads(outputs['integrated-cases.json'])
        self.assertEqual(len(plan['cases']),71)
        self.assertEqual(len({c['id'] for c in plan['cases']}),71)
        self.assertEqual(plan['protocol_cases'],{'NOT_RUN':71})
        self.assertEqual(plan['lifecycle'],{'NOT_RUN':37})
        self.assertEqual(plan['external_review'],'NOT_PERFORMED')
        self.assertEqual(plan['status'],'PROPOSAL_NOT_ADOPTED')
        counts={}
        for c in plan['cases']:
            counts[c['change']]=counts.get(c['change'],0)+1
            self.assertEqual(c['status'],'NOT_RUN')
            old=c['historical_source']['case']
            if c['change']=='NO_DIRECT_ADMISSION_CHANGE':
                self.assertEqual((c['scenario'],c['expected']),(old['input'],old['expected']))
            elif c['change']=='STRENGTHEN_OBSERVATION' and c['id']!='madd-bounded-cancellation':
                self.assertTrue(c['expected'].startswith(old['expected']+'; additionally:'))
        self.assertEqual(counts,plan['change_counts'])
        self.assertEqual(sorted(counts.values()),[8,10,53])

    def test_replaced_admission_and_cleanup_wording(self):
        text=render()['integrated-candidate.md']
        self.assertNotIn('Define final admission as the\nserialized transition',text)
        self.assertIn('Durable EXECUTING is an execution fence, not final owner admission.',text)
        self.assertIn('finite completion/cancellation bound',text)
        self.assertIn('If expiry precedes queue insertion: zero admissions/effects',text)
        self.assertEqual(text.count('## Final dispatch admission and closure'),1)

    def copied(self,directory):
        root=Path(directory)
        names=set(json.loads((ROOT/'integrated-inputs.json').read_text())['files'])
        names.update(('integrated-inputs.json','integrate_admission.py','consolidate.py'))
        for name in names:shutil.copyfile(ROOT/name,root/name)
        return root

    def test_changed_sources_and_manifest_fail(self):
        for name in ('integrated-inputs.json','admission-close-contract.md','admission-case-impact.json'):
            with self.subTest(name=name),tempfile.TemporaryDirectory() as directory:
                root=self.copied(directory)
                with (root/name).open('a') as f:f.write('\n')
                with self.assertRaises(ValueError):render(root)

    def test_real_cli_write_check_and_output_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            root=self.copied(directory)
            def invoke(mode):
                return subprocess.run([sys.executable,'-B',str(root/'integrate_admission.py'),mode],capture_output=True,text=True,timeout=10)
            self.assertNotEqual(invoke('--check').returncode,0)
            self.assertEqual(invoke('--write').returncode,0)
            self.assertEqual(invoke('--check').returncode,0)
            for name,expected in render().items():
                p=root/name;self.assertEqual(p.read_text(),expected)
                p.write_text(expected+'\n')
                self.assertNotEqual(invoke('--check').returncode,0)
                p.write_text(expected)


if __name__=='__main__':unittest.main()
