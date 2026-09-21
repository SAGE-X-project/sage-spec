# Cryptographic composition and trust-boundary review

**Current status:** findings below are the initial review snapshot. All five were
subsequently closed at the document level in the [closure re-review](crypto-trust-closure.md).
The initial hold is superseded by GO for Inspector implementation, not security certification.

Date: **2026-09-14**. Target: **SAGE 0.10.0 working draft**.
Decision: **REVISE before full sage-inspector implementation**. A narrow reporting,
parsing and independent-fixture foundation is technically ready; no Inspector code
was started. The finding register is [machine-readable JSON](crypto-trust-review.json).

## Review method and independence

This is a separate adversarial review pass over the current specification and
selected Inspector source, not an external cryptographic audit. The reviewer is the
same assistant that coordinated the draft; organizational/model independence is
not claimed. No new reviewer consensus or formal proof is claimed. The local review
does not treat existing SAGE implementation behaviour as the normative answer.

An Ouroboros project-status query reported zero execution sessions. A standalone
QA invocation was blocked by automatic approval review because sending the private
specification to that service lacked destination-specific authorization. No QA
verdict or score was produced and the invocation was not retried. This local
assessment is advisory; it is not an Ouroboros APPROVED/REJECTED engine result.

Scope: all 12 spec chapters, Execution Guard profile and integration guide; focus
on crypto/domain encoding, handshake/session lifecycle, replay, policy/capture,
load/dispatch and result boundaries. The JSON pins actual pre-review file hashes.
`f4a4e7f` is only the spec repository base, not a commit containing these drafts.
Inspector source was read at `05b890d973cf3b62a82ba412462af746aa5c266d`.
No source repository, Seed, historical vector or normative chapter was changed.

## Verdict and severity

No concrete signature-forgery, key-recovery or outside-attacker decryption attack
was demonstrated in this pass. That statement is not proof that none exists.
One P1 contract gap and four P2 ambiguities prevent freezing all expected conformance
verdicts. P1 here means fix before the affected implementation contract is frozen;
it is not a demonstrated remote exploit. P2 means a materially ambiguous fixture or
boundary rule. Missing assurance and deployment assumptions are listed separately.

| Decision area | Verdict | Reason |
|---|---|---|
| Full Inspector protocol/Execution Guard implementation | Hold | CST-01..05 need normative resolution before freezing affected oracles |
| Report format, exact-version case loader, strict parsing, independent primitive fixtures | Scoped GO | Stable work can proceed without deciding the open state contracts |
| Experimental harness to investigate crypto/state assumptions | Scoped GO | Reports must remain experimental and cannot certify unresolved behaviour |
| Production/full-profile security approval | Hold | Independent composition and host-isolation evidence are absent |

The recommended next action is to resolve CST-01..05 in the existing spec, review
the changed contracts, then start the bounded Inspector foundation. This decision
does not authorize silent implementation of a guessed wire rule. It also avoids
requiring a finished Inspector as a prerequisite to building Inspector itself.

## Findings and closure criteria

### CST-01 — P1: Pending duplicate indication has no defined protected encoding

Sources: `profiles/agent-mcp-security.md:137`, `profiles/agent-mcp-security.md:184`, `profiles/agent-mcp-security.md:208`.

**Observed:** Receive an identical intent while its first execution is still running. EXEC-05 requires duplicate/pending indication, but result.status only permits completed/rejected/unknown. unknown denotes crash uncertainty; a later completed result can conflict with the prior result. Core transport permits one terminal response.

**Required resolution:** Specify the exact authenticated duplicate/pending representation, whether it is terminal, and how the eventual result is retrieved or awaited across direct MCP and HTTP. Retain zero redispatch and no UNKNOWN bypass.

**Closure checks (not executed):** concurrent identical duplicate while RESERVED; duplicate while EXECUTING then eventual completion; duplicate after durable completion; crash UNKNOWN distinct from ordinary pending; same call with changed intent rejected.

Do not fix this by automatically mapping pending to rejected/unknown or by assigning a new call ID. Select an explicit terminal/wait/query contract and reconcile it with the one-terminal-response transport rule. No new wire status is adopted by this review.

### CST-02 — P2: Policy digest has no defined committed bytes or explicit deployment-binding contract

Sources: `profiles/agent-mcp-security.md:75`, `profiles/agent-mcp-security.md:116`, `profiles/agent-mcp-security.md:146`.

**Observed:** Two protected policy engines enforce the same rules but hash raw policy text versus a canonical object. The wire defines 64 hex characters and approval, but neither a derivation nor a versioned opaque-binding contract. Recovery also refers to a policy epoch without specifying its binding to this digest.

**Required resolution:** Define a domain/version-bound policy artifact commitment, or explicitly define policy_digest as a deployment-pinned identifier with immutable byte-to-policy/epoch mapping. A universal policy language is unnecessary. Specify update, rollback and outstanding-intent invalidation.

**Closure checks (not executed):** independent identical policy-binding fixture; changed effective policy invalidates old authorization; old epoch rejected after ledger-loss recovery; peer supplied unknown policy digest rejected.

This does not require peers to execute an identical policy language or disclose the original prompt. It requires a testable association between the signed identifier and the protected policy revision actually approved.

### CST-03 — P2: Caller AAD and complete AAD limits need one receiver rule

Sources: `spec/05-session.md:44`, `spec/05-session.md:58`.

**Observed:** callerAAD of 4034 bytes satisfies its stated 4096-byte bound but produces 4097 complete bytes. The additional complete-4096 rule names the sender, leaving receiver rejection of a nonconforming peer insufficiently explicit.

**Required resolution:** State that both sender and receiver enforce complete AAD <=4096, giving callerAAD <=4033 for this version, or choose a different explicit common limit. Clarify that the serialized metadata limit is separate.

**Closure checks (not executed):** callerAAD4033 produces complete4096 accepted when otherwise valid; callerAAD4034 produces complete4097 rejected; metadata fits4096 but full callerAAD exceeds limit.

### CST-04 — P2: Per-record session identity/key binding is not enumerated

Sources: `spec/08-transport.md:29`, `spec/05-session.md:10`, `spec/04-hpke.md:100`.

**Observed:** A legitimate session participant holding another active DID/key constructs a valid new outer signature and AEAD record with the existing sid/context/role. Chapter08 enumerates sid/context/role matches but not the full T participant/key tuple; chapter04 requires unchanged bindings. Implementers can disagree whether another accepted signer is permitted.

**Required resolution:** List stored session tuple and exact per-role did/recipient/kid/context checks, including whether a second active signing key of the same DID requires re-handshake. Make the existing changed-binding closure rule executable.

**Closure checks (not executed):** different sender DID with valid signature and deliberately valid session record; different recipient DID with valid record; different active kid same DID; revoked selected key with another usable key; correct original participant tuple.

This scenario assumes a participant can legitimately compute a new record; it is not an outsider forging AEAD. General peer checks may already reject it in an implementation. The finding requests an explicit normative tuple so two independent implementations cannot choose different answers.

### CST-05 — P2: Provisional first-record acceptance needs explicit transport exception and transition order

Sources: `spec/04-hpke.md:89`, `spec/08-transport.md:34`.

**Observed:** Responder is RESPONSE_SENT and needs its first valid initiator record to become ESTABLISHED, while generic transport language requires an established session. A strict generic state check can reject that necessary first record. The more specific handshake clause suggests an exception but does not enumerate it.

**Required resolution:** State the sole provisional receive exception, the relevant pending deadline, and the ordering of envelope/AEAD/replay/key-confirmation versus execution authorization. Specify whether an authenticated but policy-denied record confirms the session without dispatch.

**Closure checks (not executed):** valid first initiator record before pending deadline; first record exactly at expired pending deadline; forged first record leaves provisional state unchanged; two simultaneous first records transition once; valid record with denied tool policy causes zero effects.

HPKE-05 can reasonably be read as the specific exception to the generic transport rule. This is a clarification requirement for the test oracle, not a claim that every conforming design deadlocks.

## Crypto assessment and compromise matrix

HPKE Base exports a secret, the independent ephemeral DH contribution is concatenated
with that exporter in HKDF-Extract, and the transcript binds named participants,
keys, suite, context and ephemerals. The two fixed 32-byte contributions do not have
a variable-length concatenation ambiguity. Role-labelled expansions separate traffic
directions. These are positive design properties, not a composition theorem.

[RFC 9180 sections 5.3 and 9.8](https://www.rfc-editor.org/rfc/rfc9180.html#section-9.8)
allow exporter-derived material for bidirectional use. Its section 9.7 leaves
application properties such as replay and recipient-compromise forward secrecy
outside HPKE's base guarantees. [RFC 5869 section 2.3](https://www.rfc-editor.org/rfc/rfc5869.html#section-2.3)
expects a pseudorandom expansion key; the use of a derived 32-byte seed is not by
itself an HKDF misuse. Independence/entropy and lifecycle assumptions still need
analysis for this custom construction.

| Attacker capability / event | Expected boundary and evidence |
|---|---|
| Modify transcript, ack, envelope routing or exact approved arguments | Signature/AEAD/transcript checks reject; this is currently normative design, not an executed attack test |
| Reflect traffic in the opposite direction | Directional keys/AAD should reject; test independently with valid and swapped roles |
| Learn responder static KEM key after completed session and erasure | Extra ephemeral DH is intended to preserve past secrecy; not proved by citing HPKE alone |
| Learn retained session seed | All four generations in both directions can be derived; no ratchet or post-compromise recovery claim |
| Compromise signing key during establishment | Trusted-key premise is lost; fresh registry lookup does not detect misuse of an unrevoked key |
| Send first application operation before initiator confirmation | Responder provisional state must prevent effects; CST-05 clarifies exact transition |
| Rotate/revoke a bound key between checks | Re-observe at final gate and close bound session; CST-04 fixes tuple interpretation |
| Replay concurrent request or crash after external commit | Atomic ledgers prevent ordinary redispatch; UNKNOWN requires reconciliation, not exactly-once proof |

CST-A1 remains an assurance task: produce independently derived B/info/exportCtx,
exporter, ssE2E, T/th, prk/seed, ackKey/tag, sid, generation keys and record AAD
fixtures, with valid/rejection cases. Review secrecy/agreement, unknown-key-share,
interleaving and compromise timing using a stated model and assumptions. Such
analysis may occur alongside experimental harness development; it must precede a
strong security approval. No replacement of the construction is justified solely
by its being custom, and no robustness claim follows merely from concatenating DH.

## Trust-boundary assessment

| Trusted asset / boundary | Untrusted actor | Required deployment evidence |
|---|---|---|
| Original capture store and linkage | Plugin/skill/model expansion | Capture precedes expansion; mutation is denied; derived intent is bound to the stored original |
| Policy engine and signing API | Model-selected MCP tool or child process | No generic signing authority; exact call capability and approved policy revision |
| Manifest and loaded instance | Replaced path/dependency/configuration | Approved immutable artifact is the one loaded; environment/interpreter/dependency scope is documented |
| Executor and capabilities | Local tool with attempted shell/network/file escape | All protected credentials/effects remain mediated; process identity alone is insufficient |
| Result consumer | Malicious or substituted tool response | Verify exact intent/peer before model consumption; signed content grants no new authority |
| Resolver and administration | Arbitrary RPC/origin or baseline updater | Configured trust, source readiness, authenticated changes and rollback-resistant state |

The split between untrusted plugins and protected Client/dispatcher is coherent.
DID/Card registration authenticates a registered identity; it does not protect a
compromised signing process. A remotely advertised manifest hash does not demonstrate
runtime integrity. [RFC 9334](https://www.rfc-editor.org/rfc/rfc9334.html) separates
attestation evidence and appraisal. Requiring a popup would not replace capability
isolation. User-request/LLM semantic correctness remains distinct from byte integrity.

CST-A2 is a per-deployment evidence gate: name the OS/runtime privilege boundaries,
credential ownership, every protected effect and deny route, update authority and
failure injection points. A hook-only adapter which can be disabled or fail open
cannot receive Execution Guard PASS, even if every wire signature test succeeds.
Inspect invalid/missing output, timeout, child processes, subagents, retries,
network/file exits, concurrent replicas and verifier replacement. These are
required future observations, not claims that a particular host has been tested.

## Inspector readiness and independent evidence

CST-A3: current `pkg/inspect/vectors.go` imports the Go core's suite definitions and
uses its Produce/Verify functions. This is useful regression checking, but it cannot
alone establish independent expected values for the revised protocol. Pin fixture
origin, version and digest; distinguish the subject under test from the expected
oracle. Two language wrappers over the same core do not provide two independent
implementations. The existing raw-message diagnostics also deliberately omit some
live checks; retain that distinction in reports.

The original 358 planned cases remain unchanged. Finding-specific checks above are
review proposals, not newly counted executable cases. Cases involving an open CST
finding cannot be reported PASS by choosing whichever interpretation the current
core happens to implement. Use NOT_RUN/pending-contract until the normative choice
and exact expected output are recorded.

### Gate for the next implementation decision

1. Close CST-01..05 with a single interpretation in the owning existing chapters.
2. Add exact boundary/state examples and update traceability/line references together.
3. Re-review only the changed contracts and their cross-layer consequences.
4. Start the stable Inspector foundation with independently sourced fixtures; keep
   composition experiments and host-specific evidence separately labelled.
5. Grant full-profile or security approval only after relevant independent evidence,
   not from a green parser test or the absence of known findings.

No Inspector implementation or repository split was performed in this review.

## Observed checks and limits

- `git diff --check` passed on the current draft before this review.
- Temporary Python arithmetic confirmed complete record AAD overhead is **63 bytes**;
  the complete 4096-byte cap leaves **4033 bytes** for callerAAD.
- A synthetic fixed seed/transcript HKDF calculation produced 8 distinct direction/
  generation keys and 2000 distinct key/nonce pairs for the prescribed 1000 records
  in each direction. This checks literal schedule arithmetic only: no HPKE, DH,
  AEAD, entropy, erasure or real concurrency behaviour was executed or proved.
- The current trace catalogue was inspected; its AAD negative example only says
  4097-byte AAD and does not disambiguate the two lengths. Duplicate-pending versus
  eventual-completion is not an explicit lifecycle case in the existing groups.
- No new cryptographic vector files or executable harness were delivered. Temporary
  checks remained outside all repositories. Browser/GUI probes are inapplicable to
  these Markdown/JSON artifacts. No external audit, live exchange, formal model,
  remote-host integrity experiment or current Inspector test run occurred.

This pass is complete as a local review and gate recommendation. External independent
review remains unperformed. Open findings are preserved for correction rather than
silently changing protocol semantics during an audit.
