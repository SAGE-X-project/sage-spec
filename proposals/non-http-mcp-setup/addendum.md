# Proposed carriage limits and owner verification addendum

Status: **PROPOSAL_NOT_ADOPTED**. This addendum addresses the size-scope, carriage
naming and owner-coverage questions identified by [reconciliation](reconciliation.md)
at revision `48d5f579cbf781143e0bbed89c8771a3b6367544`. It supplements the [setup
proposal](README.md) and [owner contract](owner-contract.md) for review. It does not
silently revise their historical review records or establish normative precedence.
If adopted, the rules below must be integrated into a single normative profile.

The local name **SAGE authenticated non-HTTP MCP binding** means one MCP connection
over one signed, encrypted SAGE session with the proposal's explicit initialization
and fixed discovery. It is not a wire identifier or a new negotiation field. It does
not by itself claim chapter 08 WireTransport, HTTP, general MCP interoperability or
whole-host enforcement. Deployment framing and reliable bounded frame delivery remain
trusted adapter responsibilities; selecting WebSocket requires its separate applicable
transport requirements, not an exemption from them.

## Proposed complete-message limits

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
as in the base proposal. In either case no oversized bytes are sent.

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

## Proposed owner verification coverage

The [supplemental case plan](addendum-cases.json) adds 18 planned checks in a distinct
namespace. It does not alter the original 40 cases or the 386-case normative catalog.
All are NOT_RUN. The following obligations are now explicit review inputs:

- Retain immutable copies or exclusive ownership of asynchronous input/output bytes.
- Synchronous completion must obey the same OUTPUT_PENDING barrier as queued completion.
- Duplicate and old-incarnation completions cannot publish readiness or schedule output.
- Cancellation removes admission rights, and cleanup bounds live workers and buffered
  frames; callbacks have no direct access to protected effects.
- The real 1024-request lifetime bound includes setup IDs and is not a sliding window.
- Close before the serialized Guard admission denies execution. Close after effect
  admission preserves the durable result/reconciliation path and cannot undo effects.

Future tests must use actual Go and Rust APIs once adopted and implemented. Controlled
unit scheduling can exercise races without producing attack-capable code. Bounded
local runtime tests should use inert effects and authenticated peers for four language
pairings. A synthetic model, source inspection or document checker cannot mark these
protocol cases PASS. A host route inventory is separately required to assess mediation.

## Disposition

The three reconciliation questions have proposed textual resolutions, not approval:
complete-message limits above, a descriptive binding name without new wire negotiation,
and separate owner cases. Independent review must still assess their compatibility,
resource behavior and adequacy. Normative integration and explicit adoption are pending.
Historical review hashes, original cases and Inspector evidence remain unchanged.
The combined proposal plans contain **58 NOT_RUN cases** (40 original plus 18 here).
The historical lifecycle remains **37 NOT_RUN**, conformance **NOT_ESTABLISHED**.
No core behavior, wire implementation or actual protocol runtime result changes here.
