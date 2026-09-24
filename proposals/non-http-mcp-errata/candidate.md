# Candidate: local binding identity and protected-call single-flight

Status: **design candidate**, not an amendment to the adopted SAGE 0.10.0 profile.
Input: adopted `sage-spec` revision `80e3d27f781c062e8d0948d5a5c47370e809390f`,
[ADOPT-02/03 review](../../verification/post-adoption-errata-review.md), and the
[preserved design review](../../verification/preserved-design-review.md). The
[scope decisions](scope-decisions.md) address the other preserved findings. The
next step must integrate accepted text into the normative profile, traceability,
compatibility record and a new pinned revision together. No implementation or
Inspector result becomes conformant by publishing this candidate.

The candidate changes **local admission and deployment configuration**, with no
new wire member, signature construction, cipher, transport, MCP capability or
in-band negotiation. Its chosen per-owner limit is one active protected JSON-RPC
exchange. The shared Guard gate can still have several durable calls from
different owners or from completed transport exchanges, subject to its separate
finite worker, queue and outstanding-I/O quotas.
Parallel protected transport exchanges require separate authenticated owners
and sessions, each with its own complete setup; they still share the configured
gate/host resource ceilings. This choice trades same-connection throughput for
unambiguous correlation, publication and close ordering.

## Local binding identity (ADOPT-03)

The selected binding has the exact local identifier
`sage-mcp-non-http/0.10.0/mcp-2025-06-18`. This is an ASCII configuration value,
**not** a DID, MCP protocolVersion, session ID, signed transcript field or wire
capability. A different SAGE or MCP version requires an explicitly reviewed
binding identifier and descriptor; it is never an alias for this value.

The binding pins the complete object in
[`profiles/non-http-mcp-tool.json`](../../profiles/non-http-mcp-tool.json).
Parse it under the JSON and I-JSON rejection rules in chapter 02, then compute
`SHA-256(JCS(complete descriptor object))` using [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html).
Encode the 32 digest bytes as canonical unpadded base64url and prefix them with
`sha256-jcs:`. The value for the adopted one-tool descriptor is:

```text
sha256-jcs:f40nkKDT3hQs9poaxZxm8Bgw4hUV1f036fGMmIaKPtQ
```

For this exact input, JCS produces 1,141 UTF-8 bytes and SHA-256 hex
`7f8d2790a0d3de142cf69a1ac59c66f01830e21515d5fd37e9f18c98868a3ed4`.
These are calculation cross-checks, not a second digest algorithm. The adoption
record's raw **file** SHA-256
`c3edd622a7c90baa028118f63af42a91f354fe7202070ef91a4bd349e4048204`
pins repository provenance; it is not the JCS object digest and must not be
substituted in deployment configuration.
Changing any descriptor member requires a new pinned digest and an explicit
compatibility decision, even if SAGE and MCP version strings stay the same.

Before an owner can send or accept MCP initialize, the trusted host MUST bind
the following immutable local deployment values to that owner: selected binding
identifier, SAGE version, MCP version, complete descriptor object and its digest,
expected peer identity/key tuple, and expected peer binding identifier/digest.
The two identifiers and two digests MUST match the exact constants above;
versions MUST match `0.10.0` and `2025-06-18`. A missing, malformed, differently
encoded or mismatched value rejects owner construction before MCP setup and
without a protected call. A host MUST NOT substitute a descriptor fetched from
a peer or silently select another profile.

This check compares **trusted local configuration** with the fixed profile. It
cannot prove what software or configuration the remote host actually runs.
Authenticated setup and the client's complete JCS descriptor comparison remain
mandatory. The client MUST compare the discovered complete descriptor with its
pinned object and digest; a digest match alone does not waive the existing exact
member/schema check. The server sends only its pinned descriptor; it does not
infer the client's local digest from the absence of a wire field. A detected
descriptor or trusted configuration change during an owner's lifetime closes
that owner; a revised descriptor needs new approved configuration and a fresh
authenticated setup. No fallback or unchecked retry follows a mismatch.

## One active protected exchange per owner (ADOPT-02)

The limit applies to a **protected JSON-RPC request/response exchange**, not to
the lifetime of a Guard call's durable effect. Define an active exchange on the
client from the serialized acceptance of a local protected submission until
the sole correlated, authenticated response is fully validated and consumed.
Define it on the server from acceptance of the authenticated protected request
until the correlated response clears `OUTPUT_PENDING` with bounded full-send
success. A signed `pending` snapshot ends that transport exchange; it does not
declare the underlying Guard call complete. A later status request is a new
exchange with a fresh JSON-RPC and outer message ID while preserving the
original signed Guard call identity and durable state.

1. A client owner in READY MAY begin one protected exchange only when its slot
   is free, it has no pending output, and all normal session/Guard predicates
   pass. It reserves the exact request ID and cryptographic output only after
   acquiring that slot under owner serialization. A second **local** submission
   while the slot is occupied returns a local busy/denied result before ID,
   sequence, nonce, signature or ledger reservation. It sends no bytes, has no
   tool effect and does not close or disturb the first exchange. This local
   result is not a signed MCP or Guard rejection. Preparation failure before
   any reservation releases the slot with a local error; failure after an ID
   or cryptographic reservation follows the existing close/no-reuse rule.
2. A server owner reserves the syntactically valid ID of every authenticated
   protected request in its one lifetime history before routing, as already
   required. It acquires the free slot atomically under owner serialization
   before Guard verification or durable reservation. If the slot is occupied
   when it routes another such
   request, it MUST close the owner without a second Guard reservation,
   queue insertion, signed replacement response or effect. Consumed outer
   replay/sequence and request-ID history stay consumed. The first call's
   durable outcome is retained under the existing before/after-admission
   rules; closure must not assert that an admitted effect did not occur.
3. The existing one-frame `OUTPUT_PENDING` barrier is unchanged. A frame
   deferred as unauthenticated wire bytes is not a second active request. Once
   the first response's full-send publication releases the server slot, the
   owner authenticates and routes that deferred frame normally; if the first
   send fails or closure wins, the frame is discarded without dispatch. No
   second output or parallel pending send is introduced.
4. The client retains the exact sent outer envelope and both request IDs
   until it authenticates the one matching response or closes. A wrong,
   unsolicited, duplicate or late response closes the owner without releasing
   a result for use. The server publishes only the active exchange's
   correlated response. With one active exchange, no response may overtake
   another on the same owner. Another owner sharing a gate has independent
   response ordering but cannot borrow this owner's readiness or slot.
5. Each accepted protected exchange keeps its fixed PROTECTED deadline from
   MOWN-04, even while it waits for Guard storage, worker, output or response.
   Waiting does not extend the deadline, session lifetime, intent expiry or
   registry freshness. At or after a deadline, or on close/revocation, retire
   the slot and close under the existing failure rules. Before queue insertion
   there is no new effect; after insertion preserve admitted or uncertain
   outcome and prohibit automatic redispatch. A late callback or response
   cannot reopen the owner or release capacity on a replacement owner.

The per-owner slot does not replace the shared gate's worker/queue/I/O limits.
Capacity for an admitted task survives owner closure until it actually
terminates or safe cancellation completes. Another owner may continue only if
its own state and the shared gate remain healthy. Implementations MUST NOT use
the one-slot rule to bypass policy, signing, result verification or durable
execution checks.

## Integration and verification contract

The reusable core can provide pure descriptor canonicalization and digest
calculation, while the connection owner enforces immutable configuration and
single-flight admission. Agent/MCP assemblies must install that owner at the
actual protected boundary. A model-selected MCP security call, an HTTP wrapper
on this non-HTTP binding, a typed verdict or a self-reported conformance level
does not supply complete mediation. Go and Rust may expose different APIs but
must produce the same observable accept/deny and durable outcomes.

| Case family | Required observation | Safe evidence type |
| --- | --- | --- |
| Correct local profile, reordered descriptor JSON | Same JCS digest; construction and authenticated discovery proceed | Pure unit vector and bounded setup exchange |
| Missing/wrong binding identifier, version or digest | Construction rejects before MCP setup; zero protected effects | Unit and bounded runtime setup |
| Descriptor changed after owner creation | Existing owner closes; no silent schema replacement or fallback | Unit plus bounded owner lifecycle |
| Two local protected submissions | First remains active; second is local refusal with no reservations or output | Unit and bounded runtime |
| Authenticated second request on an occupied server owner | Second consumes required history, closes without second admission/effect; first outcome preserved | Unit state-machine scenario |
| Deferred frame at full-send barrier | At most one bounded frame; process only after successful first publication | Unit plus bounded runtime callback ordering |
| `pending` response followed by status retrieval | Slot releases after verified response; fresh transport IDs and unchanged signed Guard identity | Unit plus bounded runtime exchange |
| Wrong/late response, deadline or close | No slot transfer, result consumption, redispatch or false rollback | Unit state-machine scenario |
| Two owners sharing a gate | Independent owner slots; shared worker/queue/I/O quotas remain bounded | Unit and bounded runtime |

These scenarios are specifications for defensive validation, not attack
reproduction code. Inspector must distinguish this candidate from the existing
71-parent historical plan and current 71-parent execution overlay. Adoption
requires new/updated rule-to-case mapping, direct child assertions where needed,
and execution at a pinned new spec/core revision. Earlier PASS results do not
automatically cover the changed local configuration or concurrency boundaries.

This candidate leaves ADOPT-05 evidence provenance and ADOPT-06 external review
open. It does not revise baseline HTTP, DID, registry or policy semantics; the
remaining branch review findings need their own explicit scope and version
decisions before they are folded into a normative snapshot.
