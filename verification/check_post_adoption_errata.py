"""Check the adopted MCP errata review's pinned inputs and finding boundaries."""

import argparse
import hashlib
import json
from pathlib import Path

from check_mcp_adoption import pinned_path, verify as verify_adoption


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "ADOPT-01": "RESOLVED_IN_ADOPTED_DESIGN",
    "ADOPT-02": "OPEN_NORMATIVE",
    "ADOPT-03": "OPEN_NORMATIVE",
    "ADOPT-04": "RESOLVED_IN_ADOPTED_DESIGN",
    "ADOPT-05": "OPEN_PROVENANCE",
    "ADOPT-06": "PENDING_EXTERNAL",
}


def require(condition, label):
    if not condition:
        raise ValueError(label)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_record(root, record, inspector_root=None):
    adoption = json.loads((root / "verification/mcp-adoption.json").read_text())
    require(record["kind"] == "post-adoption-mcp-errata-review" and record["schema_version"] == 1, "review schema")
    require(record["protocol_version"] == adoption["protocol_version"] == "0.10.0", "protocol version")
    require(record["adoption"] == adoption["status"] == "ADOPTED_NORMATIVE_DESIGN", "adoption status")
    require(record["conformance"] == adoption["conformance"] == "NOT_ESTABLISHED", "conformance promotion")
    require(record["external_audit"] == adoption["external_audit"] == "NOT_PERFORMED", "external audit promotion")
    require(record["adopted_spec_revision"] == "520e5ed9a896ff8ba8ade776484f41084957aaa2", "reviewed spec revision")
    require(record["historical_proposal_revision"] == "70abcda876879697cae91f1182ce5c9148211e8d", "historical proposal revision")
    findings = record["findings"]
    require(len(findings) == 6 and {f["id"] for f in findings} == set(EXPECTED), "finding membership")
    document = (root / "verification/post-adoption-errata-review.md").read_text()
    for finding in findings:
        ident, status = finding["id"], finding["status"]
        require(status == EXPECTED[ident], "finding disposition: " + ident)
        require(f"| {ident} | `{status}` |" in document, "document disposition: " + ident)
        source = finding["source"]
        require(source in adoption["normative_sha256"] or source == "verification/mcp-adoption.json", "finding source: " + ident)
        content = (pinned_path(root, adoption, source) if source in adoption['normative_sha256'] else root / source).read_text()
        require(finding["anchors"] and all(anchor in content for anchor in finding["anchors"]), "source anchors: " + ident)
    inspector = record["inspector"]
    require(inspector["revision"] == "2b278fc23e9a55d1dc90554e1b976bc6104ae791", "inspector revision")
    require(inspector["ins11"] == "INCOMPLETE", "INS-11 promotion")
    require(inspector["source_ci_run_id"] == 35933387031 and inspector["source_ci_artifact_id"] == 10781767710, "CI source")
    require(inspector["source_ci_artifact_digest"] == "sha256:701eef92d20f4fddb8fece47e9763d9501f5bd4a44b85f27446b3e7583e8e61d", "CI artifact digest")
    for key in ("historical_review", "integrated_verdict", "mcp_binding_report"):
        item = inspector[key]
        require(item["path"].startswith("docs/") and len(item["sha256"]) == 64, "Inspector source: " + key)
        if inspector_root is not None:
            require(sha256(inspector_root / item["path"]) == item["sha256"], "Inspector source hash: " + key)
    if inspector_root is not None:
        verdict = json.loads((inspector_root / inspector["integrated_verdict"]["path"]).read_text())
        require(verdict["spec_revision"] == record["adopted_spec_revision"], "Inspector spec revision")
        require(verdict["ins11"] == "INCOMPLETE" and verdict["conformance"] == "NOT_ESTABLISHED", "Inspector verdict promotion")
        require(verdict["source_ci"]["run_id"] == inspector["source_ci_run_id"], "Inspector CI run")
        require(verdict["source_ci"]["artifact_id"] == inspector["source_ci_artifact_id"], "Inspector CI artifact")
        require(verdict["source_ci"]["artifact_digest"] == inspector["source_ci_artifact_digest"], "Inspector CI digest")
        require(verdict["scopes"]["mcp_binding"]["parent_pass"] == 71, "MCP parent evidence")
        require(verdict["scopes"]["mcp_binding"]["mandatory_children_per_core"] == 26, "MCP child evidence")
        require(verdict["unresolved"]["mcp_go_revision_differs_from_lifecycle"] is True, "mixed Go revisions")
    return {"findings": len(findings), "open_normative": 2, "conformance": "NOT_ESTABLISHED"}


def verify(root=ROOT, inspector_root=None):
    verify_adoption(root)
    record = json.loads((root / "verification/post-adoption-errata-review.json").read_text())
    return verify_record(root, record, inspector_root)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--inspector-root", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.root, args.inspector_root)
    except (ValueError, KeyError, OSError, TypeError) as error:
        parser.exit(1, "Post-adoption errata check FAIL: " + str(error) + "\n")
    print("Post-adoption errata consistency PASS: " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
