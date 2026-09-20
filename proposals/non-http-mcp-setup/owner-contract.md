# Trusted connection-owner API proposal

Status: **PROPOSAL_NOT_ADOPTED**. This is a language-neutral implementation contract
for the non-HTTP setup proposal, not a new wire requirement or an implemented API.
The input is [the revised proposal](README.md) at sage-spec
`a70784d6c3415b08d344bc7705f738df977ad3f9`. Its [review](review.md) still requires
independent external scrutiny and reconciliation with the uncommitted normative
baseline. This contract does not fulfill either requirement.

The terms below describe a proposed future API. Go and Rust signatures, error types
and scheduling mechanisms remain implementation choices. The guarantees and ordering
must agree before either core claims this binding. No version-string constructor,
boolean from an LLM, plugin result or caller-supplied identity establishes readiness.

## Ownership and trusted dependencies

One owner exclusively controls one role, authenticated peer/key tuple, SAGE session,
connection incarnation, pending invocation, MCP phase and request-ID history. Neither
session mutation nor a protected endpoint is exposed to untrusted callers. Ownership
cannot be cloned, serialized into a capability or moved to another connection.
A read-only diagnostic phase is not authority to invoke a tool.

Creation accepts trusted deployment configuration, an exclusively owned core session,
its original monotonic key-state creation time, a clock, bounded transport and the
Guard dependencies. The client session is authenticated; the server may still be
provisional only under the proposal's existing authenticated receive rule. The owner
cannot reset the creation time, accept an arbitrary READY flag or replace the pinned
schema with one received from the peer. Failure to establish exclusive ownership,
clock provenance or required mediation rejects construction without sending setup.

| Dependency | Required contract | Failure boundary |
|---|---|---|
| Session | Existing signature, AEAD, correlation, freshness, replay and registry checks; immutable accepted input bytes | Reject/close under the existing session rules; do not invent rollback |
| Clock and scheduler | Trusted monotonic time, bounded callbacks and timely cancellation | Close on failure or rollback; stalled work cannot retain admission rights |
| Transport | One complete bounded frame per receive; bounded full-send completion | Partial, uncertain or failed send closes; success is only local handoff |
| Gate preparation | Install trusted schema, policy and mediation without invoking tools | Failure closes before READY; preparation is not authorization |
| Guard | Existing exact-intent and current authority checks, durable execution and client-consumption state | No setup shortcut; preserve reservations after connection failure |

These are trusted implementation dependencies, not guarantees supplied by the wire.
A compromised component able to forge the clock, mutate owner memory or falsely
report send completion defeats these local assumptions. DID registration and message
signatures do not themselves establish those host properties. The contract must be
integrated into an enforced host boundary; optional model-selected MCP use is not
sufficient. Hook names and programming frameworks are deliberately unspecified.

## Proposed operations

The operations are conceptual, not exported function signatures. Each accepted event
is processed under the same serialized ownership discipline. Caller-owned byte arrays
are copied or exclusively transferred before asynchronous work can observe them.

| Operation | Caller and inputs | Result and restrictions |
|---|---|---|
| Create | Trusted host supplies the dependencies above | Private owner in CHANNEL_AUTHENTICATED or EXPECT_INITIALIZE; no usable protected endpoint |
| Start setup | Trusted client owner, once | Prepare immutable initialize; reserve history/sequence and enter OUTPUT_PENDING |
| Receive | Trusted transport supplies one bounded wire frame | Process immediately in a stable state, or retain at most one deferred frame during output; overflow closes |
| Complete work | Trusted adapter supplies its private operation identity and outcome | Commit only if incarnation, operation, state, time and session still match; callers cannot assert target phase |
| Submit protected call | Client host supplies exact RPC bytes and existing Guard inputs | Only local READY may enter normal signing/policy/session checks; the owner does not approve a prompt |
| Dispatch accepted call | Private server path after authenticated receive | Validate readiness, retained ID and exact RPC/Guard binding; invoke the existing Guard boundary |
| Close or invalidate | Trusted host, timeout or session validation | Idempotently retire admission, pending work and deferred input; preserve consumed history and durable state |
| Inspect | Diagnostics only | Non-authoritative phase and generic error category; no keys, mutable endpoint or readiness handle |

No public SetReady, ResetHistory, arbitrary CompleteSuccess or ImportReady operation
is proposed. Trusted transport callbacks are not accepted from RPC data. Internal
operation identities are local process state, never wire tokens or proof of authority.
Existing lower-level core APIs may remain available for other profiles; a deployment
claiming this binding must prevent its untrusted routes from bypassing the owner.
Language visibility alone does not prove whole-host mediation.

## Output, callbacks and publication

1. Under serialization, validate the expected phase and session, reserve the request
   ID where applicable, and prepare exact immutable output. Reserve cryptographic
   sequence state through the existing core. Install OUTPUT_PENDING with an internal
   operation identity, target phase, incarnation and bounded deadline before handing
   bytes to transport. Preparation failure closes; no reservation is released for reuse.
2. Perform bounded work without permitting reentrant owner mutation. A completion
   delivered synchronously is queued like an asynchronous completion. The owner must
   remain able to record closure and timeout; holding a lock across blocking I/O is
   not sufficient. There is at most one pending output and one bounded deferred frame.
3. A full-send completion is eligible only for that exact active operation. Duplicate
   or stale completions cannot publish a phase or prepare another output. Completions
   for a retired incarnation are ignored with diagnostics; uncertain completion of
   the active send closes the connection. There is no resend of prepared setup output.
4. Immediately before publication, re-read the trusted clock and recheck closure,
   session validity and the active operation under serialization. At or after the
   setup deadline, or after close/invalidation, discard the completion and close.
   The winner is the serialized publication point, not callback start time.
5. Publish the target phase only on success. Then process any deferred frame through
   normal authentication and phase checks before accepting another input. The frame
   was deferred as wire bytes, not accepted as an authenticated message. Send failure
   clears it without parsing or dispatching it.

Validation or gate-preparation work that runs outside serialization uses the same
incarnation/operation checks and final time/session checks. Late work has no authority
to reopen CLOSED or mutate a replacement owner. Cancellation must revoke its admission
rights even if the underlying host callback cannot be forcibly stopped; such callbacks
must have no direct access to tool effects. Implementations must demonstrate bounded
resource cleanup, not merely abandon an unlimited number of workers.

The 30-second setup bound starts at original local key-state creation, including the
server's provisional interval. It is not restarted by construction, progress or
confirmation. READY retires only the setup timer. Normal session expiry, revocation,
clock validity and Guard checks continue. A completion observed before the deadline
but published at the deadline fails. Local READY does not assert remote READY.

## Authenticated input and protected effects

Wire-size checks precede deferred storage or authentication. Stable-state receive
uses the existing outer session verification and acceptance semantics. Only then does
it validate bounded UTF-8 JSON, duplicate members, message shape, phase and exact
correlation. Inner rejection closes without undoing cryptographic acceptance.

All syntactically valid authenticated request IDs are reserved in the same lifetime
history before routing. Initialize and tools/list consume entries; the initialized
notification has no inner ID. Responses correlate existing IDs rather than reserve
new request IDs. Duplicate IDs or exhaustion at 1024 attempts close before dispatch.
Client submission enforces the same history before sending. Replacing an endpoint
cannot replenish this budget; tighter session limits still apply.

READY is a prerequisite, not an authorization decision. The private handoff retains
exact RPC bytes, invocation identity, authenticated peer/session binding and current
Guard checks. It cannot return a reusable permit that the caller can apply to changed
bytes or another session. The server uses the ordinary durable Guard reservation and
result path; the client uses the ordinary authenticated terminal consumption path.

Closure before the protected handoff wins and prevents admission. Once an authorized
effect has crossed the Guard execution boundary, a connection close cannot roll it
back or certify that it did not happen. The durable reservation/result remains the
source for reconciliation. Do not hold the setup owner lock across arbitrary effects,
automatically redispatch, or report a setup error as a signed terminal Guard result.
The implementation must document that handoff's linearization point and prove its
ordering with close and current authority checks using the actual Guard API.

## Closure, reconnect and error observability

Closure first irrevocably removes admission rights, then cancels bounded transport
and setup work, clears deferred input and releases resources when no longer in use.
Consumed replay and request history are never restored. Cryptographic destruction
follows the core's safe lifetime rules; memory erasure is not claimed by this document.

Recovery constructs a fresh authenticated session and owner with a distinct local
incarnation and full setup. No old callback, response or diagnostic phase may attach
to it. Guard nonce/reservation/result/consumption storage survives independently;
missing durable state is not recreated as empty to make reconnect succeed.

Local diagnostics may distinguish invalid input, timeout, transport failure, invalid
session, exhausted resources and unavailable dependency. They must not contain keys,
raw secrets or detailed authentication failure data exposed to the peer. No plaintext
fallback, automatic retry or wire error extension is introduced. Hosts can notify the
user of rejection without asking the LLM whether rejection should be enforced.

## Evidence required before implementation claims

The existing [40-case plan](cases.json) remains NOT_RUN. The following contract
obligations supplement it; they are planned checks, not additional executed cases.

| Obligation | Required future evidence |
|---|---|
| Encapsulation and mediation | Go and Rust API review plus chosen host route inventory; no mutable/forgeable readiness path |
| Immutable inputs and operation identity | Unit tests for caller-buffer changes, synchronous completion, duplicate completion and old-incarnation completion |
| Barrier and bounded resources | Controlled send/receive unit schedules, partial/uncertain sends, deferred overflow and cancellation cleanup |
| Deadline publication | Unit clock boundaries and callback races; safe runtime timeout/close with bounded local adapters |
| History and replay | Unit checks at the actual 1024 bound, setup/protected reuse and retained outer acceptance on inner failure |
| Guard handoff | Real API unit ordering and bounded runtime inert effects; close before admission denies, close after admission preserves reconciliation |
| Cross-language setup | Safe local Go/Go, Go/Rust, Rust/Go and Rust/Rust exchanges using authenticated setup and pinned discovery |
| Recovery | Old completions cannot affect new owners; durable result consumption survives restart without redispatch |

All obligations are **NOT_RUN** for this contract. Inspector's finite symbolic model
covers selected ordering invariants only; it does not implement this API, prove these
host assumptions or replace the tests above. Historical lifecycle 37 NOT_RUN and
conformance NOT_ESTABLISHED remain unchanged. No attack-capable reproduction is
required for this evidence; controlled unit schedules and inert local runtime peers
are the intended methods.

Next decisions are independent external review, normative baseline/traceability
reconciliation and explicit proposal adoption. Reviewers must assess the trust placed
in send completion, bounded cancellation, the deferred slot, late completions and
Guard handoff. This document is an input to that review, not its approval. Core API
implementation and Inspector protocol execution follow those decisions.
