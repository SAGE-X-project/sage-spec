# Proposed concrete admission and closure contract

Status: **CANDIDATE_AMENDMENT_NOT_ADOPTED**. SAGE **0.10.0**; the MCP binding remains
**PROPOSAL_NOT_ADOPTED**. External independent review: **NOT_PERFORMED**.
This is a same-author design response to the
[Inspector integration review](https://github.com/SAGE-X-project/sage-inspector/blob/1c1ea45888752f2860ed92f68a367f1e29e7095f/docs/mcp-owner-core-review.md).
It is not a core API implementation or protocol execution report.

The input is the [consolidated proposal](consolidated.md) at sage-spec
`70abcda876879697cae91f1182ce5c9148211e8d`, Go
`be621819d8e4f3a51895ccf469617a0aa70ee81c` and Rust
`ad30c6ade287765ac96a500699469599b9696fcd`. Those cores write EXECUTING before
post-storage verification and bounded component commitment. This document proposes
how to keep that conservative storage behavior while adding owner cancellation.

## Decision requiring normative reconciliation

The consolidated draft equates final admission with durable EXECUTING. This candidate
**changes that definition**; it is not an interpretation that already satisfies it.
Do not claim conformance to both definitions. The generated draft, historical
resolutions, case counts and Inspector model remain unchanged pending review and
explicit integration. Existing EXECUTING rows must never be recertified as evidence
of negotiated owner admission.

Separate three events:

1. **Durable execution fence:** the existing ledger records EXECUTING successfully,
   prohibiting another execution attempt even if this process later crashes.
2. **Final admission:** after fresh post-storage checks, a short serialized operation
   places one immutable invocation into a protected, bounded, process-local execution
   queue. This is the only handoff that can enable the worker. It is not a returned
   permission that a caller may reuse.
3. **Actual effect:** the trusted worker performs the admitted invocation. Admission
   does not prove that the effect happened or that its result became durable.

The candidate replacement for the admission definition is:

> Final admission is the atomic local handoff of the exact invocation into its pinned
> protected execution boundary, after successful durable execution fencing and final
> owner, authorization and time checks. Owner closure and this handoff share one
> serialization point. A durable execution fence alone does not authorize an effect.

This introduces no wire field or durable journal state. It does change the meaning of
admission in DREV-01 and its crash/close assertions. Adoption must reconcile EXEC-04/05,
the owner contract, consolidated text, model and traceability together. An integration
unable to supply the bounded atomic handoff is unsupported. A blocking arbitrary
Component.Commit callback is not automatically such a handoff.

## Ownership and synchronization

Each owner has an unexported incarnation, liveness flag, READY state, operation ID,
fixed deadline class/value, exact invocation binding and retained request history.
A gate owns the durable execution scope, current approved configuration and pinned
component instances. Multiple owners may share a gate but never share readiness.

Two synchronization domains are proposed:

- **Execution mutex:** serializes existing ledger transactions and per-call work.
  Storage and bounded trusted verification may wait here. It grants no admission.
- **Admission coordinator:** a short critical section covering owner liveness,
  operation identity, local policy/component/session generations, queue insertion
  and publication. It performs no storage, network, blocking callbacks or tool work.

The only nesting order is execution mutex, then coordinator. Close takes only the
coordinator and must never wait for the execution mutex. Cleanup is scheduled after
releasing the coordinator. No path holding the coordinator acquires the execution
mutex. Existing endpoint code that holds its session mutex across Dispatch must be
refactored for this binding; simply adding a second close lock is insufficient.
Trusted callbacks must not reenter either domain. Go and Rust must enforce the same
order, despite differences in mutex and cancellation interfaces.

Local policy retirement, component replacement and session invalidation publish a
changed generation under the coordinator. They may prepare outside it but cannot
change effective local authorization behind it. A failed later administrative write
must not restore a retired generation. Durable rollout across processes remains a
separate deployment responsibility; this process-local coordinator cannot supply it.

## Per-invocation sequence

1. The owner authenticates and bounds the message, reserves its ID in the single
   lifetime history and binds the immutable bytes to the private operation identity.
   Only READY can initiate protected work. Limit outstanding work and queue capacity
   before spawning or retaining it; overload denies, it does not create more workers.
2. Under the execution mutex, perform ordinary Guard verification and durable call/
   nonce reservation. Duplicates use the existing authenticated snapshot path and
   cannot create a new queue entry. Failure or close never deletes a reservation.
3. Record the durable execution fence. The coordinator is not held during this I/O.
   Close can retire admission while the write is blocked. If storage returns failure
   or uncertain durability, no handoff occurs; preserve/poison storage under its
   existing failure contract. There is no effect while a write's outcome is unknown.
4. After successful persistence, reverify authority, policy, exact intent, pinned
   component and clocks. This retains the existing protection against storage delay.
   Verification callbacks run outside the coordinator and within finite host bounds.
   Their result is private immutable data for this operation, never a wire token.
5. Acquire the coordinator while still owning the execution mutex. Match incarnation,
   live READY owner, operation ID, exact bytes and all observed local generations.
   Read the trusted local clocks and reject missing/rollback samples, expired session,
   intent or protected deadline, stale registry observation and exhausted capacity.
   At a deadline equality is failure. No remote lookup or extensible policy callback
   runs inside this critical section. A changed generation denies; do not keep an
   unbounded retry loop under an old request deadline.
6. Atomically insert the immutable invocation into the pinned private queue and mark
   its operation admitted. Insert either succeeds once or makes no work visible.
   The worker claims it through the same coordinator and starts effects only after
   releasing it. No effect occurs inline under either lock. A public receipt or
   diagnostic flag has no execution authority.
7. Release the locks. The admitted worker may finish after transport closure, subject
   to independently applicable tool cancellation/policy. Store the original result
   through the existing completion path. Delivery needs a live owner and its normal
   output barrier; durable completion is not permission to send on a closed owner.

The private observation in steps 4–5 must include trusted monotonic observation time,
exact key/peer binding, relevant expiries and the local generations it validated.
Existing byte-only Authority callbacks do not supply this contract by themselves.
A trusted adapter must provide and check it; a peer's `validated` flag is not evidence.
Use the baseline freshness bound (including observation after the operation starts),
not a new positive-cache lifetime. Remote chain revocation cannot be instantaneously
serialized with a local queue: the guarantee remains the baseline authoritative
observation/finality contract, not knowledge of unobserved remote changes.

## Close, invalidation and cleanup

Close atomically sets the owner's liveness false under the coordinator, retires its
pending operation identities and clears deferred input. This is the close ordering
point, independent of when storage or transport callbacks return. Record local
invalidation and deadline events the same way. Admission also rereads time so a
scheduler that delivers a timeout late cannot admit an expired operation.

If close wins before queue insertion, no worker can claim that invocation. This
includes a close during EXECUTING persistence or post-storage verification. Preserve
the fence and settle conservatively as UNKNOWN through the ledger owner when safe.
Do not create a signed rejection solely from local knowledge that this owner did not
admit; other invocation ownership and the existing signed-result rules still apply.
If UNKNOWN persistence fails, keep the storage unavailable rather than recreate it.

If insertion wins, close cannot revoke that historical admission or prove that no
effect occurred. It blocks new admissions and response publication for that owner.
An admitted task may be cancelled under a separate tool policy, but cancellation
never grants redispatch or permits overwriting the first durable terminal result.

Closing owner A must not retire the shared gate merely to stop A. Owner B retains its
own eligibility if the gate and storage remain healthy. A storage-integrity failure
may separately deny the whole affected storage scope. This is not per-owner closure.
Cleanup waits for workers outside the coordinator; pinned dependencies remain alive
until their last operation has finished. At most the configured finite number of
operations and queue slots may survive cancellation. An uncancellable provider must
occupy its slot until safe release and deny new work when exhausted, not leak workers.

## Failure and recovery table

| Boundary at failure | Permitted effect | Durable treatment and retry |
|---|---|---|
| Before reservation | None | No invented terminal; consumed transport history remains consumed |
| Reserved, not fenced | None | Preserve reservation/nonce; resolve only through existing ledger rules |
| Fence write pending, failed or uncertain | None | No admission; retain conservative storage state/unavailability |
| Fence durable, final verification fails or close wins | None | UNKNOWN or unavailable storage; no new execution attempt |
| Queue insertion fails | None | Same conservative treatment; no partially visible work |
| Admitted, worker not yet started, then crash | Not known to recovery | Durable EXECUTING recovers UNKNOWN; do not reconstruct the queue |
| Effect started, then close/crash | May have occurred | Retain durable terminal if present, otherwise UNKNOWN; never redispatch |
| Durable terminal, response cannot be published | Already determined separately | Preserve exact terminal; use authorized reconciliation, not replacement success |

The queue is deliberately not recovered as a durable job queue. A restart cannot
infer whether a pre-crash EXECUTING record was fenced-only, admitted or effected.
All such unresolved records follow the conservative existing recovery rule. Thus the
candidate promises neither exactly-once external effects nor guaranteed execution
of every durable fence. Shared/replicated execution still needs the baseline exclusive
ledger ownership; two independent coordinators cannot admit the same reserved call.

## Required evidence before implementation claims

The following are acceptance scenarios, **all NOT_RUN for this candidate**. They are
not new executed cases or an automatic expansion of the pinned 71-case catalog.

| Controlled schedule | Required observation |
|---|---|
| Pause fence write; close; release successful write | Close recorded before release, zero admissions/effects, retained fence/UNKNOWN |
| Pause post-storage key/policy check; invalidate; release | Generation or authority rejection, no queue entry |
| Persist while crossing intent/session/request expiry | Post-storage time rejection, no effect at or after the applicable boundary |
| Queue insertion and close in both explicit orders | Close-first denies; insertion-first records exactly one admission |
| Durable write failure, uncertain result or queue exhaustion | No visible work; no reservation deletion or successful delivery |
| Duplicate completion or stale owner incarnation | No second queue entry, no reopened owner or response publication |
| Crash before fence, after fence, after admission and after effect | Correct retained identities; no recovered queue or automatic effect retry |
| Two owners share a gate; close only A | A denied; eligible B remains usable absent an independent storage failure |
| Retire/replace local policy during verification | Old generation cannot enter the queue; already admitted instance stays pinned |
| Saturate cancelled worker slots | Bounded workers/memory and explicit denial until safe cleanup |

Start with deterministic in-process seams and inert counters. Then use bounded local
runtime processes with the real Go/Rust gate, storage and authenticated owners in all
four language pairings. Include journals, raw message bytes, admission order and
handoff counters. A unit model or successful mutex test alone cannot establish the
core integration. Do not create attack-capable plugins or host-bypass programs.

## Review disposition and next steps

The concrete choice is durable fencing followed by atomic protected-queue admission.
It resolves the proposed implementation strategy, not normative acceptance. Before
adoption, independent review must assess the changed admission definition, observation
freshness contract, queue trust boundary, persistence uncertainty and bounded cleanup.
Then integrate the replacement text and case assertions into one reviewed draft and
update profile/traceability together. Do not silently rewrite historical resolution
hashes or treat their previous review as covering this amendment.

No core changes are made here. The existing 71 protocol cases and 37 historical
lifecycle cases remain NOT_RUN; conformance remains NOT_ESTABLISHED. Next work is
review/reconciliation of this explicit amendment and its affected case assertions,
followed by the owner-aware gate implementation after adoption.
