# MCP post-adoption execution evidence

This addendum closes **ADOPT-05 as an evidence-linking task only**. The original
[design adoption](mcp-adoption.json), [errata design adoption](mcp-errata-adoption.json)
and [post-adoption review](post-adoption-errata-review.md) remain historical
snapshots. No normative rule, historical plan verdict, protocol conformance
verdict or external-review status changes here. The [machine-readable record](mcp-evidence-adoption.json)
pins both the specification inputs and the Inspector reports by SHA-256.

| Finding | Current disposition | Basis |
| --- | --- | --- |
| ADOPT-01 | `RESOLVED_IN_ADOPTED_DESIGN` | Exact active output completion is serialized; unrelated callbacks have no authority. |
| ADOPT-02 | `RESOLVED_IN_AMENDED_DESIGN` | The amended profile specifies one active protected exchange per owner, overload, correlation, deadline and close behavior. |
| ADOPT-03 | `RESOLVED_IN_AMENDED_DESIGN` | The amended profile pins the local binding identifier and complete descriptor digest before setup. |
| ADOPT-04 | `RESOLVED_IN_ADOPTED_DESIGN` | The adopted binding has one normative profile, traceability and compatibility record. |
| ADOPT-05 | `EVIDENCE_LINKED_WITH_SCOPE_LIMITS` | Inspector's 71-parent overlay, 26 child assertions per core, four protected pairs and eight restart observations are pinned to their original core revisions, CI run and artifact digest. |
| ADOPT-06 | `PENDING_EXTERNAL` | No independent external review has been performed on this candidate. |

The 2026-09-21 historical plan still has **71 binding parent cases and 26
mandatory child assertions `NOT_RUN`**. Inspector's separate 71-parent PASS
overlay tests the binding at spec revision `520e5ed`; it does not rewrite that
plan. The later amended design has nine additional MCP cases, and the following
specification revision has five more cases. All 14 remain planned `NOT_RUN` in
the current traceability map. The supplementary MCP Client core provenance
report records local root/hop tests at still later Go/Rust revisions; it is
not part of the 71-parent overlay or deployed-host evidence.

The [Inspector integrated verdict](https://github.com/SAGE-X-project/sage-inspector/blob/58cffde89e45096b12d834fb562ea856d46b1c0b/docs/evidence/ins11-integrated-verdict/report.json)
remains INS-11 `INCOMPLETE` and conformance `NOT_ESTABLISHED`. Its binding
overlay uses Go `1f2dd87643e42b7ed3beda6956158ff23dcc7ea2` and Rust
`40b5a8c6d76d952131013d8a034f819fd31b7ca0`. The later lifecycle audit
uses a different Go revision; these observations cannot be combined into one
deployed revision. The linked [CI run](https://github.com/SAGE-X-project/sage-inspector/actions/runs/35933387031)
and artifact are identified by run ID, artifact ID and digest. The artifact
metadata was checked against GitHub on 2026-09-24; its 30-day retention may expire,
so the pinned sources and tests
must be rerun for a later full raw-evidence audit.

The candidate is now ready to **request** ADOPT-06 review against an exact
post-merge revision. An external reviewer must establish independence, review
the state machine, fixed acknowledgement, owner admission and output ordering,
deadlines, algorithm boundary and excluded transports, and record findings and
their disposition. Until then ADOPT-06 is pending, the deployed Registry Source
and Agent host remain `NOT_RUN`, and no release or conformance claim follows.

Run the local consistency check with the pinned Inspector checkout:

```sh
python3 -B verification/test_mcp_evidence_adoption.py
python3 -B verification/check_mcp_evidence_adoption.py \
  --inspector-root /path/to/sage-inspector
```
