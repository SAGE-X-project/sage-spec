"""Check normative adoption identity and plan consistency, not runtime conformance."""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def digest(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode()
def require(ok,label):
    if not ok:raise ValueError(label)

def verify(root=ROOT):
    record=json.loads((root/'verification/mcp-adoption.json').read_text())
    require(record['status']=='ADOPTED_NORMATIVE_DESIGN' and record['protocol_version']=='0.10.0','adoption identity')
    require(record['conformance']=='NOT_ESTABLISHED' and record['external_audit']=='NOT_PERFORMED' and record['release_or_tag_created'] is False,'unsupported promotion')
    for name,h in record['normative_sha256'].items():
        require(digest((root/name).read_bytes())==h,'normative identity: '+name)
    base=root/'proposals/non-http-mcp-setup'
    for name,h in record['reviewed_candidate_sha256'].items():
        require(digest((base/name).read_bytes())==h,'reviewed input: '+name)
    require((root/record['descriptor']).read_bytes()==(base/'tool.json').read_bytes(),'descriptor changed')
    trace=json.loads((root/record['traceability']).read_text())
    require(trace['status']=='verification_plan_not_executed','trace promotion')
    rules={r['id']:r for r in trace['rules']};cases={c['id']:c for c in trace['cases']};requirements={r['id']:r for r in trace['requirements']}
    require(len(rules)==len(trace['rules'])==91,'rule membership')
    require(len(cases)==len(trace['cases'])==457,'case membership')
    require(len(requirements)==len(trace['requirements'])==45,'requirement membership')
    plan=json.loads((base/'integrated-cases.json').read_text())
    binding={c['id']:c for c in plan['cases']}
    require(len(binding)==71 and binding.keys()<=cases.keys(),'binding membership')
    baseline=[c for c in trace['cases'] if c['id'] not in binding]
    require(len(baseline)==386 and digest(canonical(baseline))==record['baseline_cases_sha256'],'baseline cases changed')
    for r in rules.values():
        require(r['evidence_status']=='planned_not_executed','rule promotion')
        require(set(r['requirements'])<=requirements.keys() and r['requirements'],'rule requirements')
        require(set(r['case_ids'])<=cases.keys() and r['case_ids'],'rule cases')
        lines=(root/r['source']).read_text().splitlines()
        headings=[i for i,line in enumerate(lines,1) if line.startswith('#') and re.search(r'\b'+re.escape(r['id'])+r'\b',line)]
        labels=[i for i,line in enumerate(lines,1) if re.match(r'^\*\*'+re.escape(r['id'])+r'\b',line)]
        require(bool(headings or labels) and r['line']==(headings or labels)[0],'rule defining location')
        if r.get('mapping_kind')!='mandatory_child_assertions':
            require(all(cases[c]['rule_id']==r['id'] for c in r['case_ids']),'primary case ownership')
    for requirement in requirements.values():
        require(requirement['evidence_status']=='planned_not_executed','requirement promotion')
        require(set(requirement['rule_ids'])<=rules.keys(),'requirement rule reference')
        require(all(requirement['id'] in rules[r]['requirements'] for r in requirement['rule_ids']),'requirement backlink')
    for c in cases.values():
        require(c['evidence_status']=='planned_not_executed','case promotion')
        require(c['rule_id'] in rules and c['id'] in rules[c['rule_id']]['case_ids'],'case owner')
    children=trace['mandatory_subscenarios']
    require(children==plan['mandatory_subscenarios'] and len(children)==26,'child assertions changed')
    require(len({c['id'] for c in children})==26,'child identity')
    require(all(c['status']=='NOT_RUN' and c['parent_case'] in binding for c in children),'child status or parent')
    require(set(rules['MOWN-06']['case_ids'])=={c['parent_case'] for c in children},'secondary child coverage')
    for ident,original in binding.items():
        adopted=cases[ident]
        require(adopted['mode']==original['planned_method'],'case method')
        if ident!='mset-08-proposal-scope':
            require(adopted['input']==original['scenario'] and adopted['expected']==original['expected'],'binding assertion changed')
        else:
            require('adoption' in adopted['input'] and 'DENY_CLAIM' in adopted['expected'],'adoption evidence boundary')
    return {'rules':91,'parent_cases':457,'binding_children':26,'conformance':'NOT_ESTABLISHED'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    args=parser.parse_args()
    try:result=verify(args.root)
    except (ValueError,KeyError,OSError) as error:
        parser.exit(1,'Adoption check FAIL: '+str(error)+'\n')
    print('Adoption consistency PASS: '+json.dumps(result))

if __name__=='__main__':main()
