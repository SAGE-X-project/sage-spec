# Purpose, vision, and evidence boundaries

Status: analysis and design interpretation for SAGE protocol **0.10.0**. Source commits and the complete current documentation inventory are in [graphs.json](graphs.json); [graphs.md](graphs.md) documents the method and limitations. Statements labelled **Observed** are source observations, **Historical** are retained prior conclusions, and **Design inference** are this draft's interpretation. None is an executed security proof.

## Purpose supported by current sources

**Observed:** `sage/README.md:12` describes authenticated, encrypted Agent communication using DID, HPKE and HTTP Message Signatures. `sage/docs/refactoring/STRATEGY.md:8,19,43–45` explicitly extends the audience to Agent/MCP implementers, requires tamper-evident requests and responses, and places protocol and conformance evidence before core and binding implementation. These files were read at `c7709b7486e0da94336edc0931fddd87f6a45343`.

**Design inference:** SAGE's useful unit is an authenticated interaction with enforceable processing rules. Its purpose is to let independently developed Agents and MCP servers establish who authorized a concrete exchange, detect alteration/replay, and refuse unverified execution or result consumption. A library is one delivery mechanism; the specification determines interoperability. Blockchain registration anchors identity/key/card lookup within the declared trust model; registration is not a proof that all software at that identity remains honest.

**Design inference from the approved Seed:** 0.10.0 adds a local integration security boundary to that channel-level purpose. A trusted Client establishes the user-request record and authorizes a derived execution request. Untrusted Plugin/MCP/Skill processing may change bytes; protected verification detects a mismatch and refuses execution. The trusted boundary includes original-request storage, verification code, signing keys, reference component hashes and mandatory enforcement paths. If those trusted facilities are compromised, the approved guarantee no longer applies. Registration-time compromise remains excluded and is deferred without promising a particular subsequent version.

This does not imply that a signed request is semantically safe. The Client owns the transformation from natural-language intent to concrete approved arguments; the protocol owns detectable alteration after that authorization. Authentic malicious content, an LLM's poor judgment, and semantic equivalence of arbitrary prompts do not become cryptographic properties.

## Current implementation evidence and resulting design gaps

| Observation at pinned source | Relationship to 0.10.0 | Evidence status / next check |
|---|---|---|
| Go `pkg/agent/core/rfc9421/verifier_http.go:46–58` aliases the session replay contract; `:71–88` provides default/injected guards. | Reusable enforcement primitive exists. Shared replay policy can be integrated instead of implemented independently per Plugin. | Source read and AST import edge observed; restart/persistence properties require tests. |
| Same file `:83–88,434,558–564` permits nil guard, disabling replay and optional expected DID. | A flexible library API is not itself the mandatory integration profile. An adapter must supply independent identity expectations and enforce replay configuration. | Observed source; no new runtime test executed. |
| Same file `:120` onward implements response signing; `:596–620` defines strict request/response options. | Existing request/response signing is a foundation for the wire profile; exact 0.10.0 coverage must still be compared against the new normative clauses. | Observed source; presence of a function is not conformance. |
| Rust `src/rfc9421/verifier.rs:71,86,143–190,215–227` has strict options and request/response verification. | Rust is an independent implementation candidate, not a competing source of wire truth. | Source read only; Rust AST was outside this analysis. |
| Rust `README.md:5–11` claims shared old-draft vector alignment and explicitly says live Go/Rust interoperability has not been exercised. | Old-draft vector compatibility cannot certify 0.10.0 or live interchange. | Claim attributed to README, not independently rerun. |
| Inspector `pkg/inspect/http.go:148–155,207–217` disables replay and sets `ExpectedDID` from parsed message DID. | Offline inspection can explain signatures but cannot establish expected caller identity or enforce live replay policy from those inputs alone. | Source read at `05b890d973cf3b62a82ba412462af746aa5c266d`; new inspector contract must provide trusted context and capture-set state. |
| Current graph includes CLI, examples, crypto/DID/session/transport, storage and telemetry packages. | The existing repository contains both protocol libraries and application concerns; ownership should be separated conceptually before physical extraction. | AST observed; see [repository roles](../architecture/repository-roles.md). |

These are targeted checks, not an exhaustive implementation-diff audit. In particular, no claim is made that the existing cores implement the approved component-hash or mandatory-execution integration profile. Their compliance remains unverified until clause-driven checks are implemented and run.

## Historical lineage and changed assumptions

`docs/refactoring/v2/review/04-purpose-and-vision.md` preserves the earlier evolution from framework claims to protocol-first development. `01-documentation-graph.md` reports an earlier 105-file second pass; `02-code-graph.md` and `11-repository-split-and-research-plan.md` record older package counts and planned releases. Those snapshots are useful rationale, not current measured counts or binding schedules. The present inventory has 161 tracked Markdown files and the existing AST tool selects 58 Go packages.

The older strategy's statements about Rust lacking shared vectors are superseded **as a repository claim** by the current Rust README; we have not rerun its tests. Likewise, old descriptions of endpoint compromise being excluded are narrower than the approved Seed's protected-Client/untrusted-component boundary. They must not silently override the new threat model. Older document versions, package release numbers and `1.0.0-draft` labels do not define the new target protocol version, **0.10.0**.

## Desired outcomes and validation boundaries

1. An independent implementer can derive the same signed bytes, parser decisions, state transitions and failure outcomes from the specification.
2. Agent/MCP adapters can enforce mandatory verification without relying on an LLM deciding to call a security tool or a user approving every action.
3. Go and Rust cores, then thin language SDKs, demonstrate matching accept/reject decisions and live bidirectional exchanges at pinned versions.
4. Registration/lookup services and component manifests remain supporting trust infrastructure, with explicit freshness/revocation and execution-binding policies.
5. Demonstrations compare the same attack and workload with SAGE disabled/enabled, measure detection and refusal, and include residual attacks that SAGE does not solve.

Items 1–5 are design goals. Static graphs do not establish them. Dynamic adversarial tests, cross-implementation exchange, implementation review and appropriate formal modelling remain future evidence, assigned in the [inspector plan](../verification/inspector-plan.md). No throughput, universal hook availability, complete exploit prevention or semantic prompt-safety claim is made.
