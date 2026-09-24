"""Verify the revised MCP normative design without promoting runtime evidence."""

import argparse
import hashlib
import json
import re
from pathlib import Path

from check_mcp_adoption import pinned_path as original_pinned_path, verify as verify_historical
from check_mcp_errata_candidate import verify_digest


ROOT = Path(__file__).resolve().parents[1]
HISTORY = Path("verification/history/mcp-errata-2026-09-24")
OWNERS = {
    "merrata-config-valid": "MSET-01",
    "merrata-config-reject": "MSET-01",
    "merrata-config-change": "MSET-01",
    "merrata-local-single-flight": "MOWN-02",
    "merrata-server-overlap": "MOWN-02",
    "merrata-deferred-frame": "MOWN-02",
    "merrata-pending-followup": "MOWN-02",
    "merrata-deadline-close": "MOWN-02",
    "merrata-shared-owners": "MOWN-02",
}


def require(condition, label):
    if not condition:
        raise ValueError(label)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pinned_path(root, record, name):
    expected = record["current_sha256"][name]
    historical = root / HISTORY / name
    path = historical if historical.is_file() else root / name
    require(sha256(path) == expected, "current identity: " + name)
    return path


def verify(root=ROOT):
    verify_historical(root)
    record = json.loads((root / "verification/mcp-errata-adoption.json").read_text())
    old_record = json.loads((root / record["prior_adoption"]).read_text())
    require(record["kind"] == "mcp-errata-normative-design-adoption" and record["schema_version"] == 1,
            "record identity")
    require(record["status"] == "AMENDED_NORMATIVE_DESIGN" and record["protocol_version"] == "0.10.0"
            and record["mcp_version"] == "2025-06-18", "revision status/version")
    require(record["prior_revision"] == "497c1045e2cc9b9d118d958443e678f212f57803"
            and sha256(root / record["prior_adoption"]) == record["prior_adoption_sha256"],
            "prior adoption provenance")
    require(record["conformance"] == "NOT_ESTABLISHED" and record["inspector_revised_cases"] == "NOT_RUN"
            and record["external_audit"] == "NOT_PERFORMED" and record["release_or_tag_created"] is False,
            "unsupported evidence promotion")
    require(record["counts"] == {"rule_groups": 91, "historical_parent_cases": 457,
                                  "new_parent_cases": 9, "total_parent_cases": 466,
                                  "mandatory_children": 26}, "counts")
    require(record["new_case_ids"] == list(OWNERS), "new case identities")
    require(record["historical_errata_review"] == "verification/post-adoption-errata-review.json"
            and sha256(root / record["historical_errata_review"]) == record["historical_errata_review_sha256"]
            and record["dispositions"] == {"ADOPT-02": "RESOLVED_IN_AMENDED_DESIGN",
                                           "ADOPT-03": "RESOLVED_IN_AMENDED_DESIGN",
                                           "ADOPT-05": "OPEN_PROVENANCE",
                                           "ADOPT-06": "PENDING_EXTERNAL"}, "errata disposition")
    for name, expected in record["candidate_inputs_sha256"].items():
        require(sha256(root / "proposals/non-http-mcp-errata" / name) == expected,
                "candidate input: " + name)
    for name, expected in record["current_sha256"].items():
        pinned_path(root, record, name)
    for name, expected in record["historical_sha256"].items():
        require((name not in old_record["normative_sha256"]
                 or expected == old_record["normative_sha256"][name])
                and sha256(root / record["historical_snapshot_root"] / name) == expected,
                "historical identity: " + name)

    descriptor = (root / record["descriptor"]).read_bytes()
    require(hashlib.sha256(descriptor).hexdigest() == record["descriptor_file_sha256"],
            "descriptor file identity")
    manifest = json.loads((root / "proposals/non-http-mcp-errata/descriptor-digest.json").read_text())
    verify_digest(manifest, descriptor)
    require(record["binding_identifier"] == manifest["binding_identifier"]
            and record["descriptor_digest"] == manifest["descriptor_digest"],
            "binding vector")

    historical = json.loads((root / record["historical_snapshot_root"] / "verification/traceability.json").read_text())
    current = json.loads(pinned_path(root, record, "verification/traceability.json").read_text())
    require(current["status"] == historical["status"] == "verification_plan_not_executed"
            and current["requirements"] == historical["requirements"]
            and current["mandatory_subscenarios"] == historical["mandatory_subscenarios"],
            "historical plan boundary")
    old_cases = {case["id"]: case for case in historical["cases"]}
    cases = {case["id"]: case for case in current["cases"]}
    require(len(old_cases) == len(historical["cases"]) == 457
            and len(cases) == len(current["cases"]) == 466
            and set(cases) == set(old_cases) | set(OWNERS), "case membership")
    require(all(cases[ident] == original for ident, original in old_cases.items()),
            "historical case changed")
    require(len(current["mandatory_subscenarios"]) == 26, "child membership")
    old_rules = {rule["id"]: rule for rule in historical["rules"]}
    rules = {rule["id"]: rule for rule in current["rules"]}
    require(len(rules) == len(current["rules"]) == len(old_rules) == 91
            and set(rules) == set(old_rules), "rule membership")
    for ident, rule in rules.items():
        old = old_rules[ident]
        same = {key: value for key, value in rule.items() if key not in ("line", "case_ids")}
        old_same = {key: value for key, value in old.items() if key not in ("line", "case_ids")}
        require(same == old_same, "historical rule changed: " + ident)
        require(rule["case_ids"] == old["case_ids"] + [case_id for case_id in OWNERS if OWNERS[case_id] == ident],
                "rule case mapping: " + ident)
        source = (pinned_path(root, record, rule["source"])
                  if rule["source"] in record["current_sha256"]
                  else original_pinned_path(root, old_record, rule["source"]))
        lines = source.read_text().splitlines()
        found = [line_no for line_no, line in enumerate(lines, 1)
                 if (line.startswith("#") and re.search(r"\b" + re.escape(ident) + r"\b", line))
                 or re.match(r"^\*\*" + re.escape(ident) + r"\b", line)]
        require(bool(found) and rule["line"] == found[0], "current rule location: " + ident)
    for ident, owner in OWNERS.items():
        case = cases[ident]
        require(case["rule_id"] == owner and case["evidence_status"] == "planned_not_executed"
                and case["mode"] in ("unit_and_bounded_local_runtime", "unit_state_machine")
                and all(case[field] for field in ("input", "preconditions", "expected")),
                "new case plan: " + ident)
    profile = (root / "profiles/non-http-mcp-security.md").read_text()
    require(record["binding_identifier"] in profile and record["descriptor_digest"] in profile
            and "One active protected exchange per owner" in profile,
            "normative profile content")
    return {"rules": 91, "parent_cases": 466, "new_parent_cases": 9,
            "binding_children": 26, "conformance": "NOT_ESTABLISHED"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        result = verify(args.root)
    except (ValueError, KeyError, OSError, TypeError) as error:
        parser.exit(1, "MCP errata adoption check FAIL: " + str(error) + "\n")
    print("MCP errata adoption consistency PASS: " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
