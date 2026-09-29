#!/usr/bin/env python3
"""Build the informative current-design graph without altering historical AST evidence."""

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "analysis/current-design-overlay.json"
TRACE_PATH = "verification/traceability.json"
HISTORICAL_GRAPH_PATH = "analysis/graphs.json"
EXPECTED_TRACE_SHA256 = "a83a28338a9e3f15cd7846ce251db2f915d9ffffaf7162bc749b7f38d784aae7"
EXPECTED_HISTORICAL_GRAPH_SHA256 = "9ebc83fd13d9abd96f1080e5c95ab8e35f148d94ec81a88e64b8f137d6026f3c"

# A document can span several implementation responsibilities. These edges are
# candidates for clause-level mapping, not claims that every rule needs every layer.
SOURCE_LAYERS = {
    "PROCESS.md": (),
    "charter.md": (),
    "profiles/agent-mcp-security.md": ("L2", "L3"),
    "profiles/non-http-mcp-security.md": ("L0", "L1", "L2", "L3"),
    "spec/00-overview.md": ("L0", "L2", "L3"),
    "spec/01-crypto.md": ("L0", "L1", "L2"),
    "spec/02-jcs.md": ("L0",),
    "spec/03-rfc9421.md": ("L0", "L1", "L3"),
    "spec/04-hpke.md": ("L0", "L1", "L2"),
    "spec/05-session.md": ("L1", "L2"),
    "spec/06-did-sage.md": ("L0", "L2"),
    "spec/07-a2a.md": ("L0", "L1", "L2"),
    "spec/08-transport.md": ("L0", "L1"),
    "spec/09-registry.md": ("L0", "L1", "L2"),
    "spec/10-resolution.md": ("L0", "L2"),
    "spec/11-registries.md": ("L0", "L1", "L2"),
}

LAYER_LABELS = {
    "L0": "Exact bytes and canonical representation",
    "L1": "Cryptographic validity under supplied inputs",
    "L2": "Trusted identity, policy and admission",
    "L3": "Host assembly and effect mediation",
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    trace_file = ROOT / TRACE_PATH
    old_graph_file = ROOT / HISTORICAL_GRAPH_PATH
    if digest(trace_file) != EXPECTED_TRACE_SHA256:
        raise ValueError("traceability changed; review the design mapping and pin a new revision")
    if digest(old_graph_file) != EXPECTED_HISTORICAL_GRAPH_SHA256:
        raise ValueError("historical AST graph changed; preserve or explicitly replace its provenance")

    trace = json.loads(trace_file.read_text())
    old_graph = json.loads(old_graph_file.read_text())
    requirements = trace["requirements"]
    rules = trace["rules"]
    cases = trace["cases"]
    if (trace["protocol_version"], len(requirements), len(rules), len(cases)) != (
        "0.10.0", 45, 91, 481
    ):
        raise ValueError("unexpected normative trace inventory")
    sources = {rule["source"] for rule in rules}
    if sources != set(SOURCE_LAYERS):
        raise ValueError("source inventory changed; classify every source explicitly")

    nodes = []
    edges = []
    for layer, label in LAYER_LABELS.items():
        nodes.append({"id": "layer:" + layer, "kind": "implementation_responsibility",
                      "label": label, "evidence": "reviewed_design"})
    for source in sorted(sources):
        nodes.append({"id": "doc:sage-spec:" + source, "kind": "current_trace_source",
                      "path": source, "sha256": digest(ROOT / source),
                      "evidence": "authored_normative_trace"})
        for layer in SOURCE_LAYERS[source]:
            edges.append({"from": "doc:sage-spec:" + source, "to": "layer:" + layer,
                          "kind": "responsibility_candidate",
                          "evidence": "reviewed_design_inference"})

    for requirement in requirements:
        rid = "requirement:" + requirement["id"]
        nodes.append({"id": rid, "kind": "requirement", "label": requirement["id"],
                      "evidence_status": requirement["evidence_status"]})
        for rule_id in requirement["rule_ids"]:
            edges.append({"from": rid, "to": "rule:" + rule_id,
                          "kind": "constrained_by",
                          "evidence": "authored_normative_trace"})
    for rule in rules:
        rid = "rule:" + rule["id"]
        nodes.append({"id": rid, "kind": "rule_group", "label": rule["id"],
                      "source": rule["source"], "line": rule["line"],
                      "evidence_status": rule["evidence_status"]})
        edges.append({"from": rid, "to": "doc:sage-spec:" + rule["source"],
                      "kind": "specified_by", "evidence": "authored_normative_trace"})
        for case_id in rule["case_ids"]:
            edges.append({"from": rid, "to": "case:" + case_id,
                          "kind": "planned_verification",
                          "evidence": "authored_normative_trace"})
    for case in cases:
        nodes.append({"id": "case:" + case["id"], "kind": "planned_case",
                      "label": case["id"], "rule_id": case["rule_id"],
                      "mode": case["mode"], "evidence_status": case["evidence_status"]})

    node_ids = [node["id"] for node in nodes]
    if len(node_ids) != len(set(node_ids)):
        raise ValueError("duplicate graph node")
    known = set(node_ids)
    if any(edge["from"] not in known or edge["to"] not in known for edge in edges):
        raise ValueError("dangling graph edge")
    cases_from_rules = [edge["to"] for edge in edges
                        if edge["kind"] == "planned_verification"]
    if set(cases_from_rules) != {"case:" + case["id"] for case in cases}:
        raise ValueError("case coverage differs from traceability")
    rule_case_pairs = {(edge["from"], edge["to"]) for edge in edges
                       if edge["kind"] == "planned_verification"}
    if any(("rule:" + case["rule_id"], "case:" + case["id"])
           not in rule_case_pairs for case in cases):
        raise ValueError("primary case owner missing from traceability links")

    nodes.sort(key=lambda item: item["id"])
    edges.sort(key=lambda item: (item["from"], item["kind"], item["to"]))
    return {
        "schema_version": 1,
        "kind": "sage-current-design-overlay",
        "status": "INFORMATIVE_RESPONSIBILITY_MAPPING",
        "protocol_version": "0.10.0",
        "traceability": {"path": TRACE_PATH, "sha256": EXPECTED_TRACE_SHA256,
                         "requirements": len(requirements), "rule_groups": len(rules),
                         "planned_cases": len(cases)},
        "historical_ast_graph": {
            "path": HISTORICAL_GRAPH_PATH,
            "sha256": EXPECTED_HISTORICAL_GRAPH_SHA256,
            "raw_packages": old_graph["counts"]["raw_packages"],
            "raw_symbols": old_graph["counts"]["raw_symbols"],
            "status": "HISTORICAL_STATIC_EVIDENCE_NOT_REPARSED",
        },
        "limits": [
            "Document-to-layer edges are responsibility candidates, not clause verdicts.",
            "Planned cases are not executed results.",
            "Historical AST edges are not current implementation conformance.",
        ],
        "counts": {"nodes": len(nodes), "edges": len(edges)},
        "nodes": nodes,
        "edges": edges,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="fail if the committed overlay differs from current inputs")
    args = parser.parse_args()
    graph = build()
    metadata = {key: value for key, value in graph.items()
                if key not in {"nodes", "edges"}}
    prefix = json.dumps(metadata, indent=2, ensure_ascii=False)
    rendered = prefix[:-2] + ",\n"
    for index, field in enumerate(("nodes", "edges")):
        items = graph[field]
        lines = ["    " + json.dumps(item, ensure_ascii=False, sort_keys=True)
                 for item in items]
        rendered += "  " + json.dumps(field) + ": [\n"
        rendered += ",\n".join(lines) + "\n  ]"
        rendered += ",\n" if index == 0 else "\n"
    rendered += "}\n"
    if args.check:
        if OUTPUT.read_text() != rendered:
            raise SystemExit("current design overlay is stale")
        print("Current design overlay PASS")
    else:
        OUTPUT.write_text(rendered)
        print("Wrote", OUTPUT)


if __name__ == "__main__":
    main()
