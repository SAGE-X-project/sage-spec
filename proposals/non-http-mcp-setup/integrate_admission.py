"""Reproduce the unadopted integrated admission candidate and effective case plan."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from consolidate import section, replace_once

ROOT = Path(__file__).resolve().parent
MANIFEST_SHA = '79cc4ec7381152e2eeafee9890a8a456227b19a0cc0e284f3154ac0e2fa5f088'


def render(root=ROOT):
    raw = (root/'integrated-inputs.json').read_bytes()
    if hashlib.sha256(raw).hexdigest() != MANIFEST_SHA:
        raise ValueError('integration manifest changed')
    manifest = json.loads(raw)
    texts = {}
    for name, digest in manifest['files'].items():
        raw = (root/name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != digest:
            raise ValueError('integration source changed: '+name)
        texts[name] = raw.decode()
    old = texts['consolidated.md']
    body = '## Scope and compatibility\n\n' + section(old, '## Scope and compatibility', '## Evidence and adoption status')
    old_admission = section(body, '## Final dispatch admission and closure', '## Operation deadline classes')
    candidate = texts['admission-close-contract.md']
    concrete = '## Final dispatch admission and closure\n\n' + '''Durable EXECUTING is an execution fence, not final owner admission. Final admission
is the atomic local handoff of the exact invocation into its pinned protected
execution queue after successful fencing and final owner, authority and time checks.
Actual worker effects and durable completion are separately observed events. Owner
closure and queue insertion share one serialization point; the fence alone grants
no execution authority. No new wire field or durable journal state is introduced.
Existing journal rows cannot certify negotiated owner admission.
If expiry precedes queue insertion: zero admissions/effects are permitted. If insertion
already won, expiry closes the failed invocation without proving rollback; preserve
its durable outcome or conservative uncertainty under the post-admission rules.

''' + '### Ownership and synchronization\n\n' + section(candidate, '## Ownership and synchronization', '## Required evidence before implementation claims')
    # Lower the remaining copied section headings beneath the admission section.
    concrete = concrete.replace('\n## ', '\n### ')
    body = replace_once(body, '## Final dispatch admission and closure\n\n'+old_admission, concrete.rstrip())
    body = replace_once(body, 'Handoff and reservation are not final admission.',
                        'Preparation, reservation and durable fencing are not final admission.')
    body = replace_once(body, 'not substitute an earlier handoff for that event.',
                        'not substitute earlier preparation or storage for protected queue insertion.')
    header = '''# Integrated authenticated non-HTTP MCP admission candidate

Status: **PROPOSAL_NOT_ADOPTED**; SAGE **0.10.0**, MCP **2025-06-18**.
This is the current integrated review candidate. Conditional MUST/SHOULD requirements
are not an adopted normative release. It supersedes the historical consolidated
proposal for this candidate's admission definition only; historical source documents
and reports remain frozen and are not alternative implementation choices.

Generated with `python3 -B integrate_admission.py --write` from
[integrated-inputs.json](integrated-inputs.json). `--check` verifies both outputs.
The [effective case plan](integrated-cases.json) has one assertion per existing case,
with historical inputs recorded only as provenance. This integration incorporates
the expiry-order and finite-cleanup clarifications. It is not external review,
core execution, normative adoption or reconciliation of the unpublished baseline.

'''
    footer = '''

## Effective evidence and adoption status

The effective plan contains **71 NOT_RUN** cases: eight redefined admission assertions,
ten strengthened observations and fifty-three retained assertions. Full description
and expected result are in integrated-cases.json; historical assertions there are
provenance, not selectable alternatives. The fixed tool descriptor is unchanged.
No case is satisfied by generating this document or by a historical primitive test.

The 37 historical lifecycle cases remain NOT_RUN; conformance is NOT_ESTABLISHED.
Existing finite models do not implement this admission candidate. Independent review
is NOT_PERFORMED. Next: review this exact candidate and effective plan, reconcile the
profile, descriptor adoption, compatibility and traceability, and explicitly adopt
before claiming implementation of a normative binding. No new private review or
model result can substitute for that decision. HTTP mapping, general MCP support
and whole-host protection remain outside this binding's claim.
'''
    impact = json.loads(texts['admission-case-impact.json'])
    changes = {c['id']:c for c in impact['cases']}
    cases = []
    for name in ('cases.json', 'addendum-cases.json', 'resolutions.json'):
        for original in json.loads(texts[name])['cases']:
            ident = original['id']; change = changes[ident]
            if change['source'] != name or original['status'] != 'NOT_RUN':
                raise ValueError('case provenance or status')
            scenario, expected = original['input'], original['expected']
            if change['category'] == 'REDEFINE_ADMISSION_ASSERTION':
                scenario = expected = change['candidate_assertion']
            elif change['category'] == 'STRENGTHEN_OBSERVATION':
                scenario += '; additionally: '+change['candidate_assertion']
                expected += '; additionally: '+change['candidate_assertion']
                if ident == 'madd-bounded-cancellation':
                    expected = ('Before admission: revoke rights and observe zero effects. After admission: '
                                'preserve outcome without rollback or redispatch. Bound workers and buffers; '
                                'finite cleanup requires bounded completion/cancellation providers. Unsupported '
                                'providers cannot satisfy cleanup; occupied-slot denial is only fail-closed degradation.')
            cases.append(dict(id=ident, status='NOT_RUN', change=change['category'],
                scenario=scenario, expected=expected,
                historical_source=dict(file=name, case=original),
                planned_method='unit_and_bounded_local_runtime'))
    if len(cases) != 71 or len({c['id'] for c in cases}) != 71 or set(changes) != {c['id'] for c in cases}:
        raise ValueError('effective case membership')
    plan = dict(kind='integrated-mcp-admission-plan', status='PROPOSAL_NOT_ADOPTED',
                external_review='NOT_PERFORMED', conformance='NOT_ESTABLISHED',
                source_revision=manifest['revision'], input_manifest_sha256=MANIFEST_SHA,
                protocol_cases={'NOT_RUN':71}, lifecycle={'NOT_RUN':37},
                change_counts=impact['counts'], cases=cases)
    return {'integrated-candidate.md':header+body+footer,
            'integrated-cases.json':json.dumps(plan,indent=2)+'\n'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write',action='store_true')
    mode.add_argument('--check',action='store_true')
    args=parser.parse_args()
    try:
        for name, content in render().items():
            path=ROOT/name
            if args.write:path.write_text(content)
            elif path.read_text()!=content:raise ValueError('generated output changed: '+name)
    except (ValueError,KeyError,OSError) as error:
        print('Integration FAIL: '+str(error),file=sys.stderr)
        return 1
    print('Integration PASS: one candidate and 71 effective NOT_RUN cases; no adoption or protocol execution')
    return 0


if __name__=='__main__':raise SystemExit(main())
