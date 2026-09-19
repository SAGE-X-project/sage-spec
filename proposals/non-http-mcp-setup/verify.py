"""Validate proposal traceability only; no protocol or cryptographic execution."""
import copy
import hashlib
import json
from pathlib import Path
import re
import sys
import unittest
ROOT=Path(__file__).resolve().parent

def unique(pairs):
    value={}
    for k,v in pairs:
        if k in value:raise ValueError('duplicate JSON member')
        value[k]=v
    return value

def load(path):return json.loads(path.read_bytes(),object_pairs_hook=unique)
def require(value,message):
    if not value:raise ValueError(message)
def validate(basis,plan,text,schema):
    require(basis['status']=='PROPOSAL_NOT_ADOPTED' and basis['conformance']=='NOT_ESTABLISHED','proposal promotion')
    require(basis['sage_version']=='0.10.0' and basis['mcp_version']=='2025-06-18','version mismatch')
    require(basis['lifecycle']=={'NOT_RUN':37},'historical promotion')
    require(basis['tool_schema_sha256']==hashlib.sha256(schema).hexdigest(),'schema mismatch')
    require(basis['local_design']['state']=='PRE_EXISTING_UNCOMMITTED_DESIGN','baseline provenance')
    require(all(re.fullmatch('[0-9a-f]{64}',v) for v in basis['local_design']['files'].values()),'source hash')
    require(plan['kind']=='proposal-case-plan' and plan['status']=='NOT_RUN' and plan['conformance']=='NOT_ESTABLISHED','plan promotion')
    rules=set(re.findall(r'^## (MSET-\d{2}) —',text,re.M));require(rules=={f'MSET-{n:02d}' for n in range(1,9)},'rule catalog')
    seen=set();covered={rule:0 for rule in rules}
    for c in plan['cases']:
        require(set(c)=={'id','rule','precondition','input','expected','status','evidence'},'case schema')
        require(c['id'] not in seen and c['id'].startswith(c['rule'].lower()+'-'),'case identity');seen.add(c['id'])
        require(c['rule'] in rules and c['status']=='NOT_RUN','case promotion or rule')
        require(c['expected'] in {'ALLOW_SETUP','CLOSE','DENY_EFFECT','READY','NO_REEXECUTION','DENY_CLAIM'},'undefined outcome')
        require(all(type(c[k]) is str and len(c[k])>=15 for k in ('precondition','input','evidence')),'missing scenario evidence')
        covered[c['rule']]+=1
    require(all(n>=3 for n in covered.values()),'missing rule cases')
    return len(seen)

def inputs():return load(ROOT/'basis.json'),load(ROOT/'cases.json'),(ROOT/'README.md').read_text(),(ROOT/'tool.json').read_bytes()
class Integrity(unittest.TestCase):
    def setUp(self):self.values=inputs()
    def reject(self,change):
        values=copy.deepcopy(self.values);change(values)
        with self.assertRaises(ValueError):validate(*values)
    def test_valid(self):self.assertEqual(validate(*self.values),31)
    def test_promotion(self):
        self.reject(lambda v:v[0].update(status='ADOPTED'))
        self.reject(lambda v:v[1]['cases'][0].update(status='PASS'))
    def test_missing_rule(self):self.reject(lambda v:v[1].update(cases=[x for x in v[1]['cases'] if x['rule']!='MSET-04']))
    def test_duplicate(self):self.reject(lambda v:v[1]['cases'].append(v[1]['cases'][0]))
    def test_schema_and_history(self):
        self.reject(lambda v:v[0].update(tool_schema_sha256='0'*64))
        self.reject(lambda v:v[0].update(lifecycle={'PASS':37}))
if __name__=='__main__':
    if '--self-test' in sys.argv:unittest.main(argv=[sys.argv[0]])
    else:print(f'Document consistency PASS: {validate(*inputs())} planned cases; all protocol execution NOT_RUN; proposal not adopted.')
