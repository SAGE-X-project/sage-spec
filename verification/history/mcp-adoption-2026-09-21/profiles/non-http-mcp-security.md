# Authenticated non-HTTP MCP binding for SAGE 0.10.0

Status: **ADOPTED_NORMATIVE_DESIGN**. This profile sets implementation requirements;
full protocol runtime conformance remains **NOT_ESTABLISHED**. It is not a release or
third-party security certification. It applies only to deployments explicitly selecting
this custom non-HTTP binding and MCP 2025-06-18.

The baseline chapters and [Execution Guard](agent-mcp-security.md) continue to apply.
The MSET and MOWN rule groups below own the additional binding requirements. A group's
requirements cover its statements and subheadings until the next identified group;
MSET-08 also owns the state summary, and MOWN-02 owns the owner-operation, publication,
input and closure subsections. The rule/case map and mandatory child assertions are in
[traceability.json](../verification/traceability.json).

## Scope and compatibility

This is a custom non-HTTP MCP transport binding for one initiator/client and one
responder/server. SAGE channel establishment precedes the MCP lifecycle. Both hosts
MUST select this binding through trusted deployment configuration, before parsing
traffic. There is no unprotected probe, fallback, new cipher, transcript field or
portable authorization token. Lack of support aborts setup without a protected call.

The binding supports exactly MCP `2025-06-18` in this binding. That is a binding
support decision, not a claim that the broader SAGE baseline permanently prohibits
later versions. MCP version, SAGE `0.10.0`, cryptographic session ID, JSON-RPC ID and
outer message ID are distinct. HTTP, stdio framing, SSE, multiple MCP connections
multiplexed over one SAGE session, and server-initiated calls are outside this binding.
A new SAGE session requires new MCP setup. Protected Guard ledgers survive separately.

[MCP lifecycle](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle)
defines initialize request/response followed by initialized notification and operation
under negotiated capabilities. This profile adds stricter admission and authenticated
carriage, without changing those MCP message types. Custom transports and HTTP's
separate rules are described in
[MCP transports](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports).
The transport acknowledgement below is not an MCP response to a notification.

## MSET-01 — Channel and ownership

Requirements: R-9, R-21, R-26, R-39, R-43.

The client MUST authenticate the SAGE handshake before sending initialize. The
server may accept that first encrypted initialize record through the existing
provisional responder receive rule: full peer/tuple, signature, freshness, replay and
AEAD checks precede channel confirmation. MCP readiness does not follow from channel
confirmation alone. No plaintext setup or plaintext error fallback is permitted.

A trusted local connection owner retains the exact session object, pinned identity
and key tuple, accepted MCP version, setup request, pending carrier and state. Model
or plugin inputs cannot assert readiness. Readiness is local, unexported state, never
a wire capability, and cannot transfer to another session, peer, role or connection.
Every message still requires current registry checks and normal session validation.
Handshake, registry, lifetime and replay protections are not weakened by this profile.

## MSET-02 — Message carriage and bounds

Requirements: R-17, R-18, R-24, R-30, R-39.

Existing signed session request/response envelopes carry the exact UTF-8 MCP JSON
bytes as encrypted plaintext. The usual outer signature, AEAD callerAAD, request_hash,
message_id and participant correlation remain mandatory. They are not replaced by
parsing inner JSON. Outer and inner request IDs are distinct UUIDv4 strings; an outer
ID collision with the inner ID is rejected. Inner notifications have no ID.

Every control or protected message has at most **16,348 plaintext bytes**,
**16,384 record bytes** and **32,768 wire-envelope bytes**, before and after READY.
The complete-message rules below define counting and failure handling. Reject invalid UTF-8, duplicate JSON members, batches,
trailing JSON, wrong message shape and excess depth (>36) before changing MCP
admission state or causing application effects. An authenticated record may already
have consumed cryptographic sequence/replay state; rejecting its inner JSON MUST NOT
restore that state. An outer validation failure follows the underlying transport
acceptance rules instead of inventing a second replay policy.
Use the versioned MCP schema for initialize fields; optional descriptive fields are
not authority and MUST NOT be forwarded as model instructions. No automatic signing,
policy change, artifact installation or tool execution occurs during setup.

The trusted owner serializes state transitions and output commitment. Preparing an
immutable authenticated output reserves its sequence and invocation but enters a
local OUTPUT_PENDING barrier, not the advertised next state. The bounded local send
must report full success before that next state is published. A partial write,
uncertain completion, cancellation or send failure closes the connection. Send success
is only a local handoff guarantee, never proof of peer receipt or disk persistence.

While OUTPUT_PENDING, no inbound message or callback may dispatch, publish readiness
or reenter the owner. A receiver may defer at most one size-bounded frame until the
barrier clears; it then runs normal authentication and state checks. Overflow closes
the connection. A response arriving before the sender's send callback returns is
subject to the same barrier. Failed or closed output never activates deferred input.
No second output, sequence reuse or duplicate response is created by cleanup.

All control messages consume normal directional sequence and outer replay budgets.
At most one control request is outstanding. The client MUST retain its exact sent
outer envelope until its sole correlated response is authenticated or the connection
closes. Application validation failure never rolls back cryptographic acceptance.
Setup messages never enter the protected tools/call parser or Guard execution ledger.
The connection owner nevertheless retains one client JSON-RPC request-ID history
across initialize, tools/list and all later protected requests. Reserve a syntactically
valid ID of an authenticated request before routing it; repeated IDs close the
connection before dispatch. IDs are never released on response completion or failure.
Sender and receiver both enforce this rule. A newly created Guard endpoint cannot
reset it. The history is bounded to 1024 request attempts including setup; exhaustion
closes the connection, and any tighter record/session limit still applies. Notification
carriers consume outer replay/sequence budgets but have no inner request ID.

## MSET-03 — Initialize and negotiation

Requirements: R-18, R-34, R-39.

Client state CHANNEL_AUTHENTICATED permits exactly one initialize request. It uses a
fresh canonical UUIDv4 JSON-RPC ID, protocolVersion `2025-06-18`, clientInfo and client
capabilities. This narrow binding advertises no optional client capabilities (`{}`).
The immutable request belongs to this session only. Sending moves the client to
WAIT_INITIALIZE; the server expects initialize as its first MCP interaction.

The authenticated reply MUST match both the outer request and the inner JSON-RPC ID.
A successful result selects `2025-06-18`, includes serverInfo and advertises exactly
`capabilities: {"tools": {}}`. Dynamic list changes, sampling, prompts, resources,
logging, experimental features and elicitation are not negotiated in this binding.
A protected JSON-RPC error, unsupported version or capability mismatch aborts setup;
no fallback, retry on the same session or partial readiness is permitted.

A successful initialize or discovery response also requires outer `success: true`
and no outer error. A false/error carrier never becomes setup success even if its
plaintext looks successful.

A successfully validated reply moves the client to INITIALIZE_ACCEPTED. The server
moves to WAIT_INITIALIZED only after the initialization reply for that immutable
invocation clears OUTPUT_PENDING with successful local send and final checks. The client does not dispatch tools in either state.
Duplicate initialize, out-of-order lifecycle messages and mismatched replies close
setup. Failure is locally observable without exposing detailed authentication oracles.

## MSET-04 — Initialized notification and transport acknowledgement

Requirements: R-18, R-26, R-39.

The client then sends exactly the MCP notification
`{"jsonrpc":"2.0","method":"notifications/initialized"}` in a fresh encrypted outer
request. This profile requires the no-params form. It has no JSON-RPC ID and receives
**no JSON-RPC response**. The outer request is only a carrier with normal replay and
request correlation. The client enters WAIT_INITIALIZED_ACK.

In WAIT_INITIALIZED, the server authenticates and validates the exact notification,
confirms the local immutable setup state and prepares its protected endpoint. It
returns one signed, encrypted outer response with `success: true`, no error member,
and plaintext exactly the two UTF-8 bytes `{}`. That fixed marker means only
"this notification was accepted in this connection's initialization state".
It is not a Guard result, execution success, capability or model-visible content.
`data` is the encoded encrypted session record, never literal empty outer data.

The client validates signature, AEAD, session, exact original request_hash/message_id,
outer success and exact `{}` plaintext before entering NEGOTIATED. Any other plaintext,
MCP response object, error, wrong correlation or second response is rejected. The
server enters DISCOVERY_ONLY only after the acknowledgement clears OUTPUT_PENDING
with successful local send and final checks. If sending fails
or its outcome is uncertain, close the connection; do not resend or create a second
acknowledgement. Accepted replay records remain consumed.

Loss of the acknowledgement leaves the client unready. The server may be further
advanced but MUST NOT dispatch without the remaining local admission rules. This
protocol does not promise simultaneous knowledge or exactly-once network delivery.
A new connection may recover by fresh setup; no tool effect occurred in this phase.

## MSET-05 — Protected tool discovery and readiness

Requirements: R-38, R-39, R-40.

NEGOTIATED/DISCOVERY_ONLY permit exactly one authenticated `tools/list` request and
correlated response before protected operations. The request has exactly jsonrpc, a fresh UUIDv4 id and method `tools/list`, with
no params, cursor or extra members. The successful JSON-RPC response has exactly
jsonrpc, that id and result; result has exactly tools. Its one tool object MUST equal
the complete JCS of the [pinned descriptor](non-http-mcp-tool.json), including the exact member
set, not just a projection of name/inputSchema. Reject nextCursor, outputSchema,
annotations, descriptions, titles and unknown metadata in this narrow discovery
binding. Received schema never replaces the trusted baseline.

General MCP permits additional tool description fields, including outputSchema;
this restriction is a deliberate smaller binding, not a statement that those fields
are invalid MCP. See [MCP tool definitions](https://modelcontextprotocol.io/specification/2025-06-18/server/tools).
Extending this descriptor requires an explicit baseline/profile revision.

The client becomes READY only after successful schema and response verification.
The server becomes READY only after its listing response clears OUTPUT_PENDING
with successful local send and final checks, and its local protected endpoint, schema
and mediation are installed. A peer-supplied tools
capability alone cannot establish that local fact. If discovery fails, close setup.
This deliberately restricted one-tool, fixed-schema binding does not advertise full
MCP service interoperability. Broader discovery requires a separate profile revision.

Only READY permits `sage_secure_call` through the Guard boundary, with the existing
exact-intent, policy, manifest, nonce, ledger and result checks. Readiness is necessary
but never sufficient authorization. No direct tool route, recursive secure call,
notification-style protected call or downgrade is introduced. Server/client local
states need not advance simultaneously; each applies its own admission predicate.

## MSET-06 — Deadline, failure and resource ownership

Requirements: R-17, R-39, R-44.

Each side sets a trusted monotonic setup deadline no later than **30 seconds** after
its local SAGE channel key-state creation. The responder starts while provisional;
confirmation does not restart the deadline. Handshake and session expiration may
close earlier. At or after the deadline no new setup transition or transition into READY
is allowed. Local policy may shorten it. Peer timestamps, traffic or progress never
extend it. A missing, untrusted or backward-moving monotonic clock closes setup.
Immediately before publishing every SETUP transition, including after validation, gate
preparation and local I/O, re-read that clock and recheck deadline, session validity,
owner liveness and closure under the serialized owner. A concurrent timeout or close
wins over any later completion callback; CLOSED cannot publish READY. Starting a
callback before the deadline does not allow completing its transition after it.
Every blocking callback is bounded by the remaining deadline, not merely
checked after return. A setup timeout closes the SAGE connection and discards local
readiness and pending response handles without resetting replay state.

Any authentication error, invalid state, unsupported setup, cancellation, uncertain
send outcome, resource exhaustion or failure to prepare the local gate closes this
setup and denies all protected calls. Implementations may report a generic failure;
this binding does not require fabricating a protected MCP error after an invalid
message. No error response is promoted into a signed Guard rejection/completion.
A fail-closed decision cannot be overridden by an LLM option or user-confirmation flag.
Session record and endpoint attempt limits remain applicable; new instances cannot
reset an existing session's counters or deadlines.

## MSET-07 — Closure and reconnect

Requirements: R-9, R-26, R-41, R-42.

Close, key revocation/material change, expiry, owner loss, role/peer/session change
or an interrupted initialization retires readiness. Recovery creates a new authenticated
channel and complete setup. No old initialize response, notification acknowledgement,
listing result or local readiness handle can activate it. Outstanding protected calls
at closure are unresolved until application-level reconciliation; no automatic redispatch.

A fresh connection does not change signed Guard call identity or release intent nonce,
execution reservation, terminal result or durable client consumption. Reconnect must
preserve these independent states. Never recreate a missing ledger as empty merely
to restore readiness. Client-result restart evidence does not certify transport replay
recovery or host-wide exclusive ownership.

## MSET-08 — Design adoption and excluded HTTP behavior

Requirements: R-31, R-32, R-33, R-34, R-45.

This profile adopts the reviewed non-HTTP binding as a 0.10.0 normative design.
It does not define chapter 08 HTTP intent/RPC mapping, HTTP version-header signing,
MCP HTTP session management or OAuth integration. Those require a separate profile;
failure cannot fall back to unspecified HTTP or unprotected transport.

The exact descriptor in [non-http-mcp-tool.json](non-http-mcp-tool.json) is adopted
for this binding. Version-string constructors remain trusted-host inputs until an
unforgeable session-owned readiness path is implemented and tested. Design adoption
is not runtime conformance, third-party audit, stabilisation, tagging or release.
Historical reports and NOT_RUN results are unchanged.

## State summary

| Client | Accepted next event | Next state |
|---|---|---|
| CHANNEL_AUTHENTICATED | emit initialize | WAIT_INITIALIZE |
| WAIT_INITIALIZE | authenticated matching initialize success | INITIALIZE_ACCEPTED |
| INITIALIZE_ACCEPTED | emit initialized carrier | WAIT_INITIALIZED_ACK |
| WAIT_INITIALIZED_ACK | authenticated fixed acknowledgement | NEGOTIATED |
| NEGOTIATED | emit tools/list | WAIT_DISCOVERY |
| WAIT_DISCOVERY | authenticated pinned tool schema | READY |
| setup state, including OUTPUT_PENDING | setup deadline or validation failure | CLOSED |
| any nonclosed state, including READY | session invalidation or explicit close | CLOSED |

Server progression is EXPECT_INITIALIZE → WAIT_INITIALIZED → DISCOVERY_ONLY → READY,
with transitions after authenticated input, successful bounded local output and
final serialized checks as specified above. Each output passes through OUTPUT_PENDING;
the table lists stable states only. All other setup events close the connection. No transition leaves
CLOSED. Once READY, setup timeout is no longer a traffic timer; normal session and
Guard limits apply. Re-initialization on a READY connection is rejected and closes it.

## MOWN-01 — Complete-message limits

Requirements: R-30, R-38, R-42.

Both directions, before and after READY, have these inclusive upper bounds:

| Object | Maximum | Counted bytes |
|---|---|---|
| Decrypted message | 16,348 | Complete exact UTF-8 JSON sent as record plaintext |
| Encrypted record | 16,384 | Sequence, nonce, ciphertext and tag, before outer encoding |
| Wire envelope | 32,768 | Complete serialized signed JSON envelope, including encoded record and signature |

These limits cover initialize, initialized carriage and its acknowledgement,
discovery, protected tools/call requests and all protected responses, including
pending and terminal results. They do not change handshake limits. Each limit is
independent: satisfying the plaintext limit does not waive the record or wire limit.
Transport framing bytes are not envelope bytes; framing must impose its own bounded
reassembly before it returns a complete envelope. No unlimited accumulation is allowed.

The plaintext count includes JSON-RPC members, IDs, intent/proof wrappers, punctuation,
UTF-8 encoding and JSON escapes. For responses it includes both structuredContent and
the canonical-JSON text representation required by EXEC-08, including that string's
escaping. Measuring only intent arguments or one result representation is incorrect.
Depth and member bounds from each applicable schema also remain in force.

A sender checks complete immutable plaintext before encryption, and the exact final
wire envelope before handoff. It must not normalize caller data to make it fit,
truncate, split into multiple records, compress, silently change transport or downgrade.
An oversize protected submission before reservation/signing has no effect and returns
a local size failure. Failure discovered after sequence or request-ID reservation
closes the owner without releasing those reservations. Setup preparation failure closes
as specified for setup. In either case no oversized bytes are sent.

A receiver bounds wire bytes before storing a deferred frame or authenticating it.
Decoded record size is checked before decryption. After outer acceptance, it checks
the complete decrypted message before inner routing. Oversize input closes the owner
and cannot dispatch. If outer acceptance already consumed replay state, inner size
failure does not undo it. These checks do not create a second replay policy.

A response may exceed the carriage limit after an effect has already occurred. That
is a transport delivery failure, not a rejected or unexecuted tool call. Preserve the
original durable outcome, produce no truncated or replacement signed terminal result,
and close the owner on failure to deliver. Notify the trusted caller of an unverified
transport failure; never report authenticated remote success without its evidence.
A fresh connection cannot make the same oversized result fit. Operators need an
explicit application reconciliation or separately authorized delivery mechanism; this
binding defines no automatic alternate transport. Host/tool policy should bound output
in advance where feasible, but output estimates cannot guarantee transport delivery.

## MOWN-02 — Ownership and trusted dependencies

Requirements: R-26, R-39, R-41, R-43, R-44.

One owner exclusively controls one role, authenticated peer/key tuple, SAGE session,
connection incarnation, pending invocation, MCP phase and request-ID history. Neither
session mutation nor a protected endpoint is exposed to untrusted callers. Ownership
cannot be cloned, serialized into a capability or moved to another connection.
A read-only diagnostic phase is not authority to invoke a tool.

Creation accepts trusted deployment configuration, an exclusively owned core session,
its original monotonic key-state creation time, a clock, bounded transport and the
Guard dependencies. The client session is authenticated; the server may still be
provisional only under the authenticated receive rule in MSET-01. The owner
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

## Owner operations

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
is permitted by this binding. Trusted transport callbacks are not accepted from RPC data. Internal
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
   session validity and the active operation under serialization. Use the operation-class deadline defined below: SETUP retains its original
   setup deadline; PROTECTED uses its fixed request/I/O deadline. At or after
   that applicable deadline, or after close/invalidation, discard completion and close.
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
clock validity and Guard checks continue. A SETUP completion observed before its deadline
but published at that deadline fails. PROTECTED completion uses its own deadline. Local READY does not assert remote READY.

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

Preparation, reservation and durable fencing are not final admission. The final dispatch admission
rules below define one shared ordering with owner closure; implementations must
not substitute earlier preparation or storage for protected queue insertion.

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

## MOWN-03 — Final dispatch admission and closure

Requirements: R-9, R-38, R-39, R-40, R-41.

Durable EXECUTING is an execution fence, not final owner admission. Final admission
is the atomic local handoff of the exact invocation into its pinned protected
execution queue after successful fencing and final owner, authority and time checks.
Actual worker effects and durable completion are separately observed events. Owner
closure and queue insertion share one serialization point; the fence alone grants
no execution authority. No new wire field or durable journal state is introduced.
Existing journal rows cannot certify negotiated owner admission.
If expiry precedes queue insertion: zero admissions/effects are permitted. If insertion
already won, expiry closes the failed invocation without proving rollback; preserve
its durable outcome or conservative uncertainty under the post-admission rules.

### Ownership and synchronization

Each owner has an unexported incarnation, liveness flag, READY state, operation ID,
fixed deadline class/value, exact invocation binding and retained request history.
A gate owns the durable execution scope, current approved configuration and pinned
component instances. Multiple owners may share a gate but never share readiness.

Two synchronization domains are required:

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

### Per-invocation sequence

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

### Close, invalidation and cleanup

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
operations and queue slots may survive cancellation. Finite cleanup claims require
a trusted provider with a finite completion/cancellation bound. A provider lacking
that bound is unsupported for this contract. If an unexpected failure prevents
termination, retain its slot and deny new work when exhausted rather than leak workers;
this is fail-closed degradation, not completed cleanup or an availability guarantee.

### Failure and recovery table

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
profile promises neither exactly-once external effects nor guaranteed execution
of every durable fence. Shared/replicated execution still needs the baseline exclusive
ledger ownership; two independent coordinators cannot admit the same reserved call.


## MOWN-04 — Operation deadline classes

Requirements: R-17, R-39, R-41.

Every pending owner operation carries an immutable local class: SETUP or PROTECTED.
This is internal state, not a peer-supplied field. The owner assigns the class from its
validated phase and message kind. A SETUP operation cannot become PROTECTED merely
because another callback observes READY.

SETUP operations use the original key-state creation deadline. Final publication,
including publication of READY, must precede that deadline and still satisfy session
validity. Closing, completing or retiring the setup operation also retires its operation
identity. A later duplicate setup callback has no authority, even after READY.

For a PROTECTED operation started after local READY, the old setup deadline is not
consulted. The owner instead uses a finite, trusted locally configured absolute
request/I/O deadline, fixed when that invocation starts. Configuration is provisioned
before use and is not optional model input. Missing configuration denies submission;
peer traffic and progress cannot extend the bound. Applicable session and Guard time
checks continue independently; passing one clock's limit does not waive another.
A new transport invocation for an existing signed call does not refresh its intent,
terminal result, nonce or execution identity.

If the protected deadline expires before final admission, use the pre-admission deny
path above. Expiry after admission closes the failed invocation/connection and reports
unverified transport failure without claiming rollback. Preserve durable execution and
client consumption state. Loss of the clock, rollback, session invalidation or expired
intent remains a failure under the corresponding baseline checks even after READY.


## MOWN-05 — Signature algorithm compatibility

Requirements: R-8, R-19, R-29.

This binding supports **Ed25519 only** for execution-intent proofs, protected
result proofs, and SAGE outer/handshake message signatures used by this binding. Each
signing role still requires the appropriate active registry key, issuer/recipient
binding, current authorization and full existing signature verification. A valid
signature under an unsupported algorithm is rejected; key presence alone cannot
negotiate algorithm support.

The fixed tool descriptor already expresses the intent restriction and is unchanged.
Result and outer signatures are constrained explicitly here because the input schema
cannot constrain them. Provisioning requires suitable Ed25519 signing keys for the
participating roles before setup. If unavailable, this binding is unsupported; no
silent fallback, key substitution or automatic re-signing of an existing intent is
allowed. Ordinary key selection must still obey the baseline identity rules.

This is a narrower compatibility profile, not removal of secp256k1 or P-256 from the
general SAGE 0.10.0 specification or registry. Registry ownership transactions and
chain-native proofs retain their separately defined algorithms. HPKE's X25519 KEM,
KDF and AEAD are unchanged: X25519 is not an alternative signing algorithm.
Expanding this binding requires an explicit profile/descriptor revision and verifier
and interoperability evidence before advertisement.

## MOWN-06 — Admission clarifications and required schedules

Requirements: R-9, R-30, R-39, R-40, R-41, R-44.

These rules incorporate the separate-agent review and corrections recorded in
[cross-review.md](../proposals/non-http-mcp-setup/cross-review.md). The review is not
a third-party external audit or runtime conformance result.

### Dispatch, worker claim and administrative invalidation

For this binding's EXEC-04/05 mapping, successful protected queue
insertion is dispatch. A queued but unclaimed invocation is already admitted;
ordinary owner closure or intent/session/request expiry after insertion does not
prove that no effect occurred and does not itself undo dispatch. Expiry before
insertion requires zero admissions and effects. The eventual effect may start after
expiry if admission already won and no independently required cancellation applies.
Keep admission, worker claim, actual effect and result persistence separate in traces.

EXEC-06 administrative baseline replacement and approved policy retirement require
additional treatment: under the coordinator, invalidate the old generation and cancel
its queued but unclaimed invocations before a worker may claim them. This implements
pending-call invalidation without silently moving work to the new component. A cancelled
entry retains its historical admission and durable identity but cannot reach effects
or be redispatched. Preserve a conservative unresolved outcome unless existing signed
result rules allow a stronger durable conclusion; cancellation alone cannot fabricate
an authenticated rejection or completion.

Worker claim and administrative invalidation share the coordinator. If invalidation
wins, observe zero worker effects. If claim wins, the running invocation keeps its
original pinned instance and remains subject to the applicable running-tool cancellation
policy; never claim retroactive non-execution or automatically retry. Queue removal,
claim and cancellation must be single-consumer operations. An admitted entry is not a
portable permit. This mapping is part of this profile and its EXEC-04/05/06 integration; it MUST NOT
be inferred from a peer's description of its queue.

### Finite providers and scheduler bounds

Trusted storage, verification and transport providers must have finite completion or
safe-cancellation bounds. The scheduler must also supply a finite enqueue-to-claim OR
safe-cancellation bound; a provider bound alone does not cover an unclaimed queue entry.
At the scheduler bound, claim/cancel races are serialized under the coordinator. No
cancelled entry may later be claimed. If scheduling or cancellation unexpectedly stalls,
retain occupied capacity and pinned dependencies and deny further work when exhausted;
this is fail-closed degradation, not successful cleanup or an availability guarantee.

Worker and outstanding-I/O quotas apply to the shared gate/host pool across owner
replacement and reconnect, not just separately to each connection. Reconnect cannot
abandon an old worker and allocate an unlimited replacement budget. Release capacity
only after the operation actually terminates or a safe cancellation completes. Never
free a pinned dependency merely because owner closure was recorded. Waiting for storage
termination or cleanup must not hold the admission coordinator.

### Final observations and storage uncertainty

The final coordinator clock read is a trusted bounded local sample, never a registry
lookup such as the existing Go RegistryAuthority.Now. Authoritative observation work
occurs outside the coordinator. Its immutable result binds the operation, exact key,
peer, expiries and observed policy/component/session generations. The observation is
acquired after operation start, and its age at final admission is at most 5000 ms:
5000 ms alone is not stale; 5001 ms is. Independent intent, session and request deadlines
still reject at equality. Reject missing/rollback clocks, pre-operation observations,
changed generations and stale observations before queue insertion. A denied attempt
may be re-resolved only through bounded work without extending any fixed deadline.

Closing during a fence write records closure immediately without asserting the write
was cancelled. Test success, explicit failure and uncertain durability separately.
No branch may admit closed work. Failed/uncertain fencing, failed UNKNOWN persistence
and failed recovery conversion keep the affected storage scope unavailable under its
existing integrity rules; no empty-store recreation or queue reconstruction is allowed.
If the fence never became durable, do not fabricate a durable EXECUTING row in evidence.
Whole-scope storage failure is distinct from closing one otherwise healthy owner.

### Distinct record and owner-history limits

The 1024-entry owner history ceiling is an isolated owner-unit bound. It is not a
promise that one authenticated session can reach it. The baseline closes before
sending sequence 1000 and rejects received sequence >=1000 in either direction.
Initialize, initialized notification and discovery consume normal records, while the
notification consumes no inner request ID. Test the owner ceiling in isolation and
separately prove that the tighter record ceiling closes real authenticated traffic
first. Do not alter the session limit, reset counters via a new endpoint, or count
an owner-only result as protocol runtime evidence.

The effective plan's mandatory subscenarios specify generation/freshness boundaries,
storage outcomes, queue failures, shared-owner isolation and bounded cleanup. They
are child assertions of existing cases, not additional top-level protocol cases.
Every applicable child must be observed before its parent can pass. All remain NOT_RUN.



## Evidence and compatibility

All 71 binding parent cases and 26 mandatory child assertions remain NOT_RUN. Children
are obligations within their parents, not additional top-level cases. The 386 existing
baseline planned cases and 37 historical Inspector lifecycle cases are different
catalogs; no prior evidence is promoted by this design adoption. Separate-agent review
is complete at the design/plan level; external audit and full execution remain absent.
See the [adoption record](../verification/mcp-adoption.json) for exact input/output
identities, compatibility decisions and implementation follow-up.
