# Post-adoption review of the non-HTTP MCP binding

This review re-evaluates the six findings in the earlier [Inspector adoption-readiness
review](https://github.com/SAGE-X-project/sage-inspector/blob/2b278fc23e9a55d1dc90554e1b976bc6104ae791/docs/mcp-adoption-readiness-review.md)
against the adopted SAGE 0.10.0 design at `520e5ed9a896ff8ba8ade776484f41084957aaa2`.
The earlier review examined a proposal at `70abcda876879697cae91f1182ce5c9148211e8d`;
its `PROPOSAL_NOT_ADOPTED` and `BLOCKED` labels describe that earlier revision, not the
current normative status. The [adoption record](mcp-adoption.json) remains
`ADOPTED_NORMATIVE_DESIGN`, with conformance `NOT_ESTABLISHED` and external audit
`NOT_PERFORMED`. This document records findings; it changes no normative requirement.
The [machine-readable review](post-adoption-errata-review.json) pins the inputs and
dispositions.

| Finding | Current disposition | Basis and remaining work |
| --- | --- | --- |
| ADOPT-01 | `RESOLVED_IN_ADOPTED_DESIGN` | The profile forbids a callback from dispatching, publishing readiness or reentering the owner during `OUTPUT_PENDING` (lines 77–89). Its output algorithm queues synchronous completion, serializes publication of the *exact active* full-send operation after final checks, and rejects stale or duplicate completion (lines 380–403). This gives completion a controlled path without granting unrelated callbacks authority. A future editorial revision could state this relationship in one sentence, but the original semantic conflict does not remain a blocking erratum. |
| ADOPT-02 | `OPEN_NORMATIVE` | The one-outstanding limit at lines 91–103 applies to **control** requests. A singular pending invocation, one pending output, and an instruction to limit work (lines 327–329, 387–390, 504–510) do not set a numerical limit on READY-state **protected** calls. The profile does not fully define what happens to a second attempt, its request-ID reservation, correlation, response publication order, per-call deadline and close handling. Decide and state the per-owner limit and overload outcome. Single-flight is a reasonable candidate, but this review does not adopt it. A shared gate may serve multiple owners (lines 475–480), so its capacity must be distinguished from each owner's limit. |
| ADOPT-03 | `OPEN_NORMATIVE` | Trusted pre-traffic selection and no fallback are required (lines 15–28); discovery compares the complete JCS descriptor (lines 163–179), and the adoption record pins its file SHA-256. None of these assigns a stable versioned *local binding identifier*, defines the normative digest calculation for the complete descriptor, or requires construction-time rejection of configured mismatches before setup. Define those deployment checks without inventing a wire negotiation field. The provenance hash in the adoption record is not by itself a peer configuration rule. |
| ADOPT-04 | `RESOLVED_IN_ADOPTED_DESIGN` | The binding has a single normative profile and descriptor (lines 239–252), 14 binding rule groups with 71 parent cases and 26 mandatory child assertions in [traceability](traceability.json), and compatible adoption/change records in [PROCESS](../PROCESS.md) and [CHANGELOG](../CHANGELOG.md). The adoption checker verifies the pinned normative files and case mapping. This closes the earlier proposal-integration finding without implying runtime conformance. |
| ADOPT-05 | `OPEN_PROVENANCE` | Historical binding plans correctly remain 71 `NOT_RUN` parent cases and 26 `NOT_RUN` children in the adoption snapshot (lines 744–751). Later [Inspector integrated evidence](https://github.com/SAGE-X-project/sage-inspector/blob/2b278fc23e9a55d1dc90554e1b976bc6104ae791/docs/evidence/ins11-integrated-verdict/report.json) reports a separate 71-parent PASS overlay, 26 child assertions per core, four protected pairs and eight restart cases, while its overall verdict is `INCOMPLETE`. The adoption record does not link that later Inspector revision, CI source, report hashes or scope. Add a separate, revision-pinned evidence addendum; preserve the historical `NOT_RUN` statuses and do not promote conformance. The MCP-binding CI evidence uses Go `1f2dd87643e42b7ed3beda6956158ff23dcc7ea2`, while the later lifecycle review uses Go `2fb4755ba38d1c90adea5089402fcc6b8981fd71`; do not present them as one deployment revision. |
| ADOPT-06 | `PENDING_EXTERNAL` | The adoption record explicitly states `external_audit: NOT_PERFORMED`. Earlier separate-agent internal review is not an independent external review. Once the normative gaps and evidence provenance have a candidate revision, obtain a review that records reviewer independence, reviewed revision, findings and disposition. This is an assurance follow-up, not a reversal of design adoption. |

The next specification change should resolve ADOPT-02 and ADOPT-03 as one reviewable
normative revision, update traceability and compatibility records, then add the
ADOPT-05 evidence addendum without rewriting the historical plan. ADOPT-06 follows
against that fixed candidate. Implementation and Inspector validation then use the
new pinned revision. The preserved design branch and its uncommitted work remain
separate from this review.

Run the local review control and existing adoption checks:

```sh
python3 -B verification/test_post_adoption_errata.py
python3 -B verification/check_post_adoption_errata.py
python3 -B verification/test_mcp_adoption.py
python3 -B verification/check_mcp_adoption.py
```

The review checker may additionally verify the pinned Inspector files when an
Inspector checkout is available with `--inspector-root /absolute/path/to/sage-inspector`.
Passing these checks establishes document identity and review consistency, not
protocol conformance or completion of the open findings.
