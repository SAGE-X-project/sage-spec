"""Check the revised web-origin media contract and bounded header vectors."""

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OLD_SHA256 = '2f7e5468bf87e7a402c7853584fca8e345b5055a0625f7068a71e80e6321eb02'
TRACE_SHA256 = '410b1ffb7e6da0462d8c3b3ecae4ba6ed2a9c1f0bc14583fe4d17fa4d7ef5ba7'
OLD_OVERLAY_SHA256 = '9c477886bef7fe9bc9983d65d541654dd965f09a656c0de38c5a71d0be99d463'
VECTOR_PATH = 'verification/vectors/web-registry-media-0.10.0.json'
RECORD_PATH = 'verification/web-registry-media-contract.json'
OLD_PATH = 'verification/history/web-registry-media-base-2026-09-30/spec/09-registry.md'
OPERATOR_SNAPSHOT = 'verification/history/registry-operator-base-2026-10-01'
CASE_IDS = (
    'lowercase-json', 'mixed-case-json', 'wrong-type', 'did-document-type',
    'problem-detail-type', 'missing-type', 'parameterized-json',
    'duplicate-type', 'combined-type', 'gzip-coding',
    'explicit-identity-coding', 'trailer-type', 'trailer-coding',
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def media_decision(header_lines, trailer_lines=None):
    """Evaluate only the REG-08 media/coding subcondition, not a full record."""
    require(isinstance(header_lines, list), 'header list')
    require(trailer_lines is None or isinstance(trailer_lines, list), 'trailer list')
    content_types = []
    content_encodings = []
    for section, lines in (('header', header_lines), ('trailer', trailer_lines or [])):
        for line in lines:
            require(isinstance(line, list) and len(line) == 2
                    and all(isinstance(value, str) for value in line), 'header line')
            name, value = line
            require(re.fullmatch(r'[A-Za-z][A-Za-z-]*', name) is not None
                    and all(ord(char) < 128 and char not in '\r\n\x00' for char in value),
                    'header syntax')
            if section == 'trailer' and name.lower() in (
                    'content-type', 'content-encoding'):
                return 'RECORD_INVALID'
            if name.lower() == 'content-type':
                content_types.append(value.strip(' \t'))
            elif name.lower() == 'content-encoding':
                content_encodings.append(value)
    if (len(content_types) != 1 or content_encodings
            or re.fullmatch(r'application/json', content_types[0], re.I) is None):
        return 'RECORD_INVALID'
    return 'MEDIA_ACCEPT'


def verify_vectors(vectors):
    require(vectors['schema_version'] == 1
            and vectors['kind'] == 'web-registry-media-subcondition-vectors'
            and vectors['protocol_version'] == '0.10.0'
            and vectors['rule_id'] == 'REG-08'
            and 'no record validation' in vectors['scope'], 'vector scope')
    cases = vectors['cases']
    require([item['id'] for item in cases] == list(CASE_IDS), 'vector identities')
    for item in cases:
        positive = item['id'] in ('lowercase-json', 'mixed-case-json')
        expected_parent = 'REG-08-P' if positive else 'REG-08-N04'
        expected_verdict = 'MEDIA_ACCEPT' if positive else 'RECORD_INVALID'
        require(item['parent_case_id'] == expected_parent
                and item['expected'] == expected_verdict
                and item['expected'] == media_decision(
                    item['header_lines'], item.get('trailer_lines')),
                'vector decision: ' + item['id'])
    require(sum(item['expected'] == 'MEDIA_ACCEPT' for item in cases) == 2,
            'positive subconditions')
    return len(cases)


def verify(root=ROOT):
    record = json.loads((root / RECORD_PATH).read_text())
    media_root = (root / OPERATOR_SNAPSHOT
                  if (root / 'verification/registry-operator-adoption.json').is_file()
                  else root)
    require(record == {
        'schema_version': 1,
        'kind': 'web-registry-media-normative-correction',
        'protocol_version': '0.10.0',
        'base_revision': '6d216736fa7561f672066789d4801a768d0d0500',
        'status': 'NORMATIVE_DESIGN_PENDING_EXECUTION',
        'historical_source': OLD_PATH,
        'historical_sha256': OLD_SHA256,
        'current_source': 'spec/09-registry.md',
        'current_sha256': record['current_sha256'],
        'historical_overlay': 'verification/history/web-registry-media-base-2026-09-30/analysis/current-design-overlay.json',
        'historical_overlay_sha256': OLD_OVERLAY_SHA256,
        'current_overlay': 'analysis/current-design-overlay.json',
        'current_overlay_sha256': record['current_overlay_sha256'],
        'traceability_sha256': TRACE_SHA256,
        'vectors': VECTOR_PATH,
        'vectors_sha256': record['vectors_sha256'],
        'rule_groups': 91,
        'parent_cases': 489,
        'mandatory_children': 26,
        'inspector_execution': 'NOT_RUN',
        'core_implementation': 'NOT_RUN',
        'external_audit': 'NOT_PERFORMED',
        'conformance': 'NOT_ESTABLISHED',
        'release_or_tag_created': False,
    }, 'correction record shape or evidence claim')
    require(sha(root / OLD_PATH) == OLD_SHA256, 'historical source bytes')
    require(sha(media_root / record['current_source']) == record['current_sha256']
            and record['current_sha256'] != OLD_SHA256, 'current source bytes')
    require(sha(root / 'verification/traceability.json') == TRACE_SHA256,
            'unchanged traceability bytes')
    require(sha(root / record['historical_overlay']) == OLD_OVERLAY_SHA256,
            'historical overlay bytes')
    require(sha(media_root / record['current_overlay']) == record['current_overlay_sha256']
            and record['current_overlay_sha256'] != OLD_OVERLAY_SHA256,
            'current overlay bytes')
    require(sha(root / VECTOR_PATH) == record['vectors_sha256'], 'vector bytes')
    old = (root / OLD_PATH).read_text()
    current = (media_root / record['current_source']).read_text()
    require('The response header section MUST contain exactly' not in old
            and 'The response header section MUST contain exactly' in current
            and 'a receiver MUST reject any `Content-Encoding` field' in current
            and 'in the trailer section MUST also be rejected' in current
            and '`record.invalid`' in current
            and '`size.exceeded`' in current,
            'normative media and error decision')
    trace = json.loads((root / 'verification/traceability.json').read_text())
    overlay = json.loads((media_root / record['current_overlay']).read_text())
    require(overlay['traceability']['sha256'] == TRACE_SHA256
            and overlay['traceability']['planned_cases'] == 489
            and any(node.get('path') == 'spec/09-registry.md'
                    and node.get('sha256') == record['current_sha256']
                    for node in overlay['nodes']), 'current overlay source')
    cases = {case['id']: case for case in trace['cases']}
    rules = {rule['id']: rule for rule in trace['rules']}
    require(len(trace['rules']) == 91 and len(cases) == 489
            and len(trace['mandatory_subscenarios']) == 26
            and rules['REG-08']['source'] == 'spec/09-registry.md'
            and {'REG-08-P', 'REG-08-N04'} <= set(rules['REG-08']['case_ids'])
            and all(cases[ident]['rule_id'] == 'REG-08'
                    and cases[ident]['evidence_status'] == 'planned_not_executed'
                    for ident in ('REG-08-P', 'REG-08-N04')),
            'traceability or case status')
    count = verify_vectors(json.loads((root / VECTOR_PATH).read_text()))
    return {'rule': 'REG-08', 'header_vectors': count,
            'planned_parent_cases': 489, 'conformance': 'NOT_ESTABLISHED'}


if __name__ == '__main__':
    try:
        result = verify()
    except (ValueError, KeyError, OSError, TypeError) as error:
        raise SystemExit('Web registry media check FAIL: ' + str(error)) from error
    print('Web registry media check PASS: ' + json.dumps(result, sort_keys=True))
