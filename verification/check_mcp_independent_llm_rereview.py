"""Pin the scoped ADOPT-06 LLM re-review without promoting conformance."""

import base64
import hashlib
import json
from pathlib import Path

from check_standards_clause_revision import verify_current_sources


ROOT = Path(__file__).resolve().parents[1]
TARGET = '5bcf511e604579afa63f434013447f44b6858828'
PREVIOUS_SHA256 = 'c873043816693f192c8209cadd895797ce9085b9a9387850c6ae4a0f3c362e4f'
SOURCE_MANIFEST_SHA256 = '3055141fbc2bafdf3598fabaf6c30846361cdcd4f1375f3d2824765bfed67e8a'
SOURCE_PATHS = {
    'profiles/non-http-mcp-security.md',
    'profiles/non-http-mcp-tool.json',
    'profiles/agent-mcp-security.md',
    'spec/00-overview.md', 'spec/01-crypto.md', 'spec/02-jcs.md',
    'spec/03-rfc9421.md', 'spec/04-hpke.md',
    'spec/05-session.md', 'spec/06-did-sage.md',
    'spec/07-a2a.md', 'spec/08-transport.md',
    'spec/09-registry.md', 'spec/10-resolution.md',
    'spec/11-registries.md',
    'verification/vectors/registry-proof-0.10.0.json',
}
HISTORICAL_ROOT = 'verification/history/standards-clauses-base-2026-09-29'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def verify_record(root, record):
    # Preserve the old review inputs while independently rejecting changes to
    # the active specification. The historical copy cannot satisfy this gate.
    verify_current_sources(root)
    require(record['schema_version'] == 1 and
            record['kind'] == 'mcp-independent-llm-rereview' and
            record['finding'] == 'ADOPT-06' and
            record['protocol_version'] == '0.10.0' and
            record['target_revision'] == TARGET and
            record['previous_review'] ==
            'verification/mcp-independent-llm-review.json' and
            record['previous_review_sha256'] == PREVIOUS_SHA256,
            'review identity and lineage')
    require(record['status'] == 'SCOPED_LLM_REREVIEW_COMPLETE' and
            record['organizationally_external'] is False and
            record['third_party_audit'] == 'NOT_PERFORMED' and
            record['implementation_conformance'] == 'NOT_ESTABLISHED' and
            record['release_claim'] is False,
            'review claim promoted')
    reviewer = record['reviewer']
    require(reviewer['identity'] == 'Codex LLM in a separate fresh context' and
            reviewer['affiliation'] ==
            'same service and workspace as the authoring agent' and
            reviewer['conflict'] == 'not organizationally independent' and
            all(reviewer[key] for key in ('method', 'scope', 'limits')),
            'reviewer identity, conflict or scope')
    source = record['source_sha256']
    require(type(source) is dict and set(source) == SOURCE_PATHS and
            digest(json.dumps(source, sort_keys=True,
                              separators=(',', ':')).encode()) ==
            SOURCE_MANIFEST_SHA256,
            'reviewed source manifest')
    for name, expected in source.items():
        require(digest((root / HISTORICAL_ROOT / name).read_bytes()) == expected,
                'reviewed source bytes: ' + name)
    descriptor = json.loads((root / HISTORICAL_ROOT /
                             'profiles/non-http-mcp-tool.json').read_text())
    canonical = json.dumps(descriptor, sort_keys=True,
                           separators=(',', ':'), ensure_ascii=False).encode()
    descriptor_sha = hashlib.sha256(canonical).digest()
    require(canonical.isascii() and record['descriptor_check'] == {
        'jcs_bytes': 1141,
        'sha256_hex': descriptor_sha.hex(),
        'sha256_jcs': 'sha256-jcs:' +
        base64.urlsafe_b64encode(descriptor_sha).rstrip(b'=').decode(),
    } and len(canonical) == 1141 and
            descriptor_sha.hex() ==
            '7f8d2790a0d3de142cf69a1ac59c66f01830e21515d5fd37e9f18c98868a3ed4',
            'fixed descriptor bytes and digest')
    require(digest((root / record['previous_review']).read_bytes()) ==
            PREVIOUS_SHA256, 'historical review bytes')
    findings = record['previous_finding_dispositions']
    require([row['id'] for row in findings] == ['LLM-01', 'LLM-02'] and
            all(row['status'] == 'RESOLVED_IN_NORMATIVE_TEXT' and
                row['anchors'] and row['evidence'] and row['limit']
                for row in findings) and
            findings[0]['anchors'] ==
            ['spec/00-overview.md:64', 'spec/09-registry.md:88-98'] and
            findings[1]['anchors'] ==
            ['spec/09-registry.md:24-36', 'spec/09-registry.md:45-53',
             'spec/09-registry.md:106-115', 'spec/11-registries.md:46-66'],
            'previous finding dispositions')
    require(record['new_non_http_mcp_findings'] == [] and
            record['previously_recorded_separate_findings'] ==
            ['SCA-01', 'SCA-02', 'SCA-03'] and
            bool(record['next_gate']),
            'scope and next gate')
    report = (root / 'verification/mcp-independent-llm-rereview.md').read_text()
    require(all(term in report for term in
                (TARGET, 'SCOPED_LLM_REREVIEW_COMPLETE',
                 'LLM-01', 'LLM-02', 'SCA-01', 'SCA-02', 'SCA-03',
                 'NOT_PERFORMED', 'NOT_ESTABLISHED')),
            'human-readable review report')
    return {'finding': 'ADOPT-06', 'status': record['status'],
            'text_findings_resolved': ['LLM-01', 'LLM-02'],
            'third_party_audit': record['third_party_audit'],
            'implementation_conformance': record['implementation_conformance']}


def verify(root=ROOT):
    path = root / 'verification/mcp-independent-llm-rereview.json'
    return verify_record(root, json.loads(path.read_text()))


if __name__ == '__main__':
    try:
        result = verify()
    except (ValueError, KeyError, OSError, TypeError) as error:
        raise SystemExit('MCP independent LLM re-review FAIL: ' + str(error)) from error
    print('MCP independent LLM re-review PASS: ' +
          json.dumps(result, sort_keys=True))
