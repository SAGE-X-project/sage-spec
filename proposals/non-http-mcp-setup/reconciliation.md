# MCP setup adoption reconciliation

Status: **PROPOSAL_NOT_ADOPTED**. This is a comparison by the authoring agent, not
independent external review, normative adoption or proof of implementation support.
It compares proposal revision `55949a6b7b0de33f94992db595540ae58c92d13f`, including
the [owner contract](owner-contract.md), with the pre-existing uncommitted 0.10.0
design identified in [basis.json](basis.json). The original working tree is preserved.

The [machine-readable mapping](reconciliation.json) pins the four compared baseline
files and the local traceability catalog by SHA-256. That local catalog has 77 rule
groups and 386 planned cases. Its unpublished contents are not supplied by a Git
revision in this proposal. A reviewer needs those exact source files, or a reviewed
published snapshot with updated provenance, to reproduce the comparison. Hashes
identify inputs; they do not make absent inputs independently reviewable.

## Comparison and proposed disposition

References in the baseline column are local rule identifiers, not newly adopted rules.
A mapping means related obligations, not semantic equivalence or test coverage.

| Proposed rule | Baseline relationship | Action required before adoption |
|---|---|---|
| MSET-01 channel ownership | HPKE-05 supplies provisional acceptance; SESSION-06 closes invalid sessions; EXEC-01/08 require trusted mediation | Add explicit session-owned readiness and distinguish authenticated channel from MCP readiness; retain provisional receive and registry requirements |
| MSET-02 carriage and limits | SESSION-03/04/05 and TRANSPORT-04 define record bounds, sequence allocation and atomic replay; EXEC-08 defines the protected call | Adopt the smaller binding limits explicitly; retain cryptographic acceptance on inner rejection; specify the separate 1024-request history and output barrier |
| MSET-03 initialize | EXEC-08 requires structured results with a 2025-06-18 baseline, but does not define this exact setup exchange | Decide and document exact-version selection, empty client capabilities and tools-only server capabilities as this binding's narrower compatibility policy |
| MSET-04 initialized acknowledgement | EXEC-08 does not specify notification carriage; TRANSPORT-04 supplies authenticated correlation | Adopt the encrypted outer acknowledgement and exact two-byte marker explicitly; never present it as a JSON-RPC notification response or Guard result |
| MSET-05 discovery | EXEC-08 pins call input/result semantics; EXEC-01/04 supply mediation and authorization | Adopt exact full descriptor comparison and discovery completion as local readiness conditions; readiness never replaces per-call authorization |
| MSET-06 deadline | HPKE-05 and SESSION-06 govern provisional/session lifetime; EXEC-01/08 require fail-closed mediation | Add the independent 30-second setup deadline, original key-state start and serialized final checks; keep earlier session limits and retire only the setup timer on READY |
| MSET-07 recovery | SESSION-06 requires a fresh handshake; EXEC-04/05/07 retain execution and result identity | Specify new owner/incarnation and fresh setup without clearing durable Guard state; preserve unresolved effects rather than redispatch |
| MSET-08 scope | TRANSPORT-05/06 define HTTP and other carriage; EXEC-08 distinguishes direct local MCP; EXEC-09 limits security claims | Name the custom non-HTTP binding precisely and keep HTTP mapping and host conformance separate; no fallback or inferred full MCP interoperability |

## Differences that must not be silently merged

**Three unrelated 1024 bounds.** SESSION-05's sliding replay window is not the
proposal's lifetime JSON-RPC request history. EXEC-02 also bounds captured input
count to 1024, which is unrelated to either. The request history is not a replay
window: accepted IDs are not evicted to permit more requests. The proposed 1024
request-attempt limit includes initialize and tools/list; notifications have no
inner request ID. The Inspector symbolic capacities of two and three do not test
the production bound.

**Payload limits are profile limits, not universal replacements.** SESSION-03 permits
an 8 MiB record; TRANSPORT-04 permits a 16 MiB envelope; EXEC-03 permits a 1 MiB
intent envelope. The proposal permits only 16,348 decrypted bytes and 32,768 wire
bytes in this binding. A valid general intent can therefore be too large for this
binding. The smaller applicable limit governs; SDKs must reject before sending and
must not truncate, chunk or silently use another transport. Adoption must state the
scope of these limits for protected traffic as well as control traffic and confirm
actual core carriage behavior with boundary tests. The proposal's control-message
wording alone is insufficient to claim a complete protected-call size contract.

**Retry allowances do not imply setup retransmission.** SESSION-04 permits only
identical stored ciphertext if retransmission is attempted, subject to replay
rejection. The setup proposal is stricter: partial or uncertain send closes, and no
second acknowledgement is created. Keep the narrower rule explicit; do not treat the
session allowance as a setup recovery mechanism.

**Version baseline is not exact negotiation.** EXEC-08 requires support for structured
results and names a baseline. Exact 2025-06-18 selection and reduced capabilities are
new restrictions in this binding. They must not become a silent prohibition on other
versions in every SAGE profile. No change to the SAGE 0.10.0 version follows from this
MCP selection.

**Direct MCP and WireTransport remain different claims.** The local profile explicitly
distinguishes direct MCP from chapter 08 carriage conformance. Reusing signed session
envelopes does not establish HTTP signing, WebSocket/TLS framing or host isolation.
The final profile must name which carriage it adopts and preserve all applicable
checks. HTTP intent-versus-RPC payload mapping remains open.

**Owner operations add implementation obligations.** Incarnation checks, bounded
callbacks and the Guard handoff are defined in the owner contract. The 40 proposal
cases predate that contract and do not exhaust its obligations. New cases are needed
for buffer ownership, synchronous/duplicate/stale callbacks, worker cleanup and close
ordering at the actual Guard boundary. Do not relabel those as already covered by the
finite model or inflate the existing catalog by counting prose as executed tests.

## Review and adoption gates

1. Publish or otherwise provide the exact local normative inputs for independent
   review. Reconcile their 0.10.0 version and status with the repository's existing
   older release/process documents; do not infer approval from their presence in a
   working tree. Preserve original edits until an intentional normative update.
2. Obtain independent review of the state machine, fixed acknowledgement, owner
   contract and the differences above. Record reviewer identity, input revisions,
   findings and disposition. The authoring agent's comparison and Inspector model
   are not a substitute for this gate.
3. Resolve protected-call size scope, exact carriage/profile naming and the owner
   obligations. Amend the proposal and case plan as needed, with new input hashes and
   a review record. Existing reviewed artifact hashes must not be silently rewritten
   to imply that an earlier review covered new text.
4. On explicit adoption, update normative text, requirement mappings, compatibility
   record, descriptor baseline and traceability together. MSET identifiers remain
   proposal-local until that decision. The JSON mapping here is not an automatic
   migration into the 386-case catalog, and existing IDs must not be renumbered.
5. Implement both cores and add separate unit and safe runtime evidence for the
   adopted contract, including cross-language exchanges and actual resource bounds.
   Conformance changes only on the applicable evidence; older reports stay intact.

All 40 proposal cases and 37 historical lifecycle cases remain NOT_RUN; conformance
remains NOT_ESTABLISHED. This comparison found adoption work to resolve, not an
exploitable implementation vulnerability. No external message or review request has
been sent, and no core implementation has been changed.
