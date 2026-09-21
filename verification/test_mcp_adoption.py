import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from check_mcp_adoption import ROOT, verify, digest


class AdoptionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        record=json.loads((ROOT/'verification/mcp-adoption.json').read_text())
        names=set(record['normative_sha256'])|{'verification/mcp-adoption.json','verification/check_mcp_adoption.py'}
        names|={'proposals/non-http-mcp-setup/'+n for n in record['reviewed_candidate_sha256']}
        names.add('proposals/non-http-mcp-setup/tool.json')
        for name in names:
            dest=self.root/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,dest)

    def mutate_trace(self,fn):
        p=self.root/'verification/traceability.json';t=json.loads(p.read_text());fn(t);p.write_text(json.dumps(t))
        rpath=self.root/'verification/mcp-adoption.json';r=json.loads(rpath.read_text());r['normative_sha256']['verification/traceability.json']=digest(p.read_bytes());rpath.write_text(json.dumps(r))

    def test_complete_adoption_without_runtime_claim(self):
        self.assertEqual(verify(self.root),{'rules':91,'parent_cases':457,'binding_children':26,'conformance':'NOT_ESTABLISHED'})

    def test_baseline_case_change(self):
        self.mutate_trace(lambda t:t['cases'][0].update(expected='changed'))
        with self.assertRaisesRegex(ValueError,'baseline cases changed'):verify(self.root)

    def test_reference_and_child_controls(self):
        source=(self.root/'verification/traceability.json').read_bytes()
        for mutate,error in [(lambda t:next(r for r in t['rules'] if r['id']=='MSET-08').update(line=11),'rule defining location'),
                             (lambda t:t['mandatory_subscenarios'][0].update(status='PASS'),'child assertions changed')]:
            (self.root/'verification/traceability.json').write_bytes(source)
            self.mutate_trace(mutate)
            with self.assertRaisesRegex(ValueError,error):verify(self.root)

    def test_real_cli_and_duplicate_rejection(self):
        command=[sys.executable,'-B',str(self.root/'verification/check_mcp_adoption.py'),'--root',str(self.root)]
        good=subprocess.run(command,capture_output=True,text=True,timeout=10)
        self.assertEqual(good.returncode,0,good.stderr)
        self.mutate_trace(lambda t:t['cases'].append(t['cases'][-1]))
        bad=subprocess.run(command,capture_output=True,text=True,timeout=10)
        self.assertNotEqual(bad.returncode,0)
        self.assertIn('case membership',bad.stderr)


if __name__=='__main__':unittest.main()
