"""Check the coordinated 0.10.0 design snapshot without claiming execution."""

import argparse
import hashlib
import json
import re
from pathlib import Path

from check_mcp_errata_adoption import ROOT, pinned_path, verify as verify_prior
from review_target import pinned_path as reviewed_path


OWNERS = {
    "mrevision-hop-authorized": "EXEC-02",
    "mrevision-hop-unapproved": "EXEC-02",
    "mrevision-parent-no-grant": "EXEC-05",
    "mrevision-did-consumer": "RESOLVE-01",
    "mrevision-extra-jwk-authority": "RESOLVE-01",
}
REVISED_REQUIREMENTS = {"R-14", "R-37"}


def require(condition, label):
    if not condition:
        raise ValueError(label)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(root=ROOT):
    verify_prior(root)
    record = json.loads((root / "verification/spec-revision-adoption.json").read_text())
    prior_path = root / "verification/mcp-errata-adoption.json"
    prior = json.loads(prior_path.read_text())
    require(record["kind"] == "coordinated-normative-design-revision"
            and record["schema_version"] == 1
            and record["protocol_version"] == "0.10.0"
            and record["status"] == "AMENDED_NORMATIVE_DESIGN", "record identity")
    require(record["prior_revision"] == "858f8de56a8f04adaeed7380291d55d237842094"
            and record["prior_adoption"] == "verification/mcp-errata-adoption.json"
            and sha256(prior_path) == record["prior_adoption_sha256"], "prior provenance")
    require(record["counts"] == {"rule_groups": 91, "historical_parent_cases": 466,
                                  "new_parent_cases": 5, "total_parent_cases": 471,
                                  "mandatory_children": 26}, "counts")
    require(record["new_case_ids"] == list(OWNERS)
            and record["changed_requirement_ids"] == sorted(REVISED_REQUIREMENTS),
            "revision membership")
    require(record["conformance"] == "NOT_ESTABLISHED"
            and record["inspector_revised_cases"] == "NOT_RUN"
            and record["external_audit"] == "NOT_PERFORMED"
            and record["release_or_tag_created"] is False,
            "unsupported evidence promotion")
    required_files = {"charter.md", "profiles/agent-mcp-security.md",
                      "spec/00-overview.md", "spec/03-rfc9421.md",
                      "spec/10-resolution.md", "spec/11-registries.md",
                      "verification/traceability.json", "README.md", "PROCESS.md",
                      "CHANGELOG.md", "verification/inspector-plan.md",
                      "verification/standards-revision-decisions.md",
                      "architecture/migration-plan.md", "guides/integration.md"}
    require(set(record["current_sha256"]) == required_files, "snapshot files")
    for name, expected in record["current_sha256"].items():
        reviewed_path(root, name, expected)

    old = json.loads(pinned_path(root, prior, "verification/traceability.json").read_text())
    current = json.loads(reviewed_path(root, "verification/traceability.json",
                                       record["current_sha256"]["verification/traceability.json"]).read_text())
    require(current["protocol_version"] == old["protocol_version"] == "0.10.0"
            and current["status"] == old["status"] == "verification_plan_not_executed"
            and current["mandatory_subscenarios"] == old["mandatory_subscenarios"]
            and len(current["mandatory_subscenarios"]) == 26,
            "plan status or children")
    old_req = {item["id"]: item for item in old["requirements"]}
    new_req = {item["id"]: item for item in current["requirements"]}
    require(len(old_req) == len(new_req) == 45 and set(old_req) == set(new_req),
            "requirement membership")
    for ident, item in new_req.items():
        prior_item = old_req[ident]
        require(item["evidence_status"] == "planned_not_executed"
                and item["rule_ids"] == prior_item["rule_ids"],
                "requirement mapping: " + ident)
        if ident not in REVISED_REQUIREMENTS:
            require(item == prior_item, "historical requirement changed: " + ident)
        else:
            require(item["description"] != prior_item["description"],
                    "missing requirement clarification: " + ident)

    old_cases = {item["id"]: item for item in old["cases"]}
    cases = {item["id"]: item for item in current["cases"]}
    require(len(old_cases) == 466 and len(cases) == len(current["cases"]) == 471
            and set(cases) == set(old_cases) | set(OWNERS), "case membership")
    require(all(cases[ident] == item for ident, item in old_cases.items()),
            "historical case changed")
    old_rules = {item["id"]: item for item in old["rules"]}
    rules = {item["id"]: item for item in current["rules"]}
    require(len(old_rules) == len(rules) == len(current["rules"]) == 91
            and set(old_rules) == set(rules), "rule membership")
    for ident, rule in rules.items():
        previous = old_rules[ident]
        stable = {key: value for key, value in rule.items() if key not in ("line", "case_ids")}
        old_stable = {key: value for key, value in previous.items()
                      if key not in ("line", "case_ids")}
        require(stable == old_stable and rule["evidence_status"] == "planned_not_executed",
                "historical rule changed: " + ident)
        require(rule["case_ids"] == previous["case_ids"]
                + [case_id for case_id, owner in OWNERS.items() if owner == ident],
                "rule case mapping: " + ident)
        source = rule["source"]
        historical = root / "verification/history/llm-review-target-2026-09-25" / source
        lines = (historical if historical.is_file() else root / source).read_text().splitlines()
        found = [number for number, line in enumerate(lines, 1)
                 if (line.startswith("#") and re.search(r"\b" + re.escape(ident) + r"\b", line))
                 or re.match(r"^\*\*" + re.escape(ident) + r"\b", line)]
        require(bool(found) and rule["line"] == found[0], "rule location: " + ident)
    for ident, owner in OWNERS.items():
        case = cases[ident]
        require(case["rule_id"] == owner
                and case["mode"] == "unit_and_bounded_local_runtime"
                and case["evidence_status"] == "planned_not_executed"
                and all(case[key] for key in ("input", "preconditions", "expected")),
                "new case plan: " + ident)
    profile = (root / "profiles/agent-mcp-security.md").read_text()
    require("independently authorize" in " ".join(profile.split())
            and "imply transitive delegation" in profile
            and "parent_call_id" in profile, "multihop authority text")
    return {"rules": 91, "parent_cases": 471, "new_parent_cases": 5,
            "mandatory_children": 26, "conformance": "NOT_ESTABLISHED"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        result = verify(args.root)
    except (ValueError, KeyError, OSError, TypeError) as error:
        parser.exit(1, "Specification revision check FAIL: " + str(error) + "\n")
    print("Specification revision consistency PASS: " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
