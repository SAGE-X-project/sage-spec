# 8. Transport envelope

Version: 0.9.0-draft.1.1. Finalizes 0.9.0-draft.1 with the errata in [../docs/errata-0.9.0-draft.1.md](../docs/errata-0.9.0-draft.1.md).

Go sources: `pkg/agent/transport/wire.go`, `transport/http/client.go`,
`transport/http/server.go`. No dedicated vector; the envelope is covered
through the RFC 9421 vectors (headers) and JSON field names below.

An HTTP request body and a WebSocket message MUST NOT exceed 1 MiB; a
receiver rejects larger ones.

HTTP and WebSocket transports MUST use TLS (`https`, `wss`), except to a
loopback address.

## 1. WireMessage

```json
{
  "id": "<message id>",
  "context_id": "<optional>",
  "task_id": "<optional>",
  "payload": "<base64 bytes>",
  "did": "<sender DID>",
  "recipient": "<receiver DID>",
  "created": "<YYYY-MM-DDThh:mm:ssZ>",
  "nonce": "<16-64 characters>",
  "metadata": { "<key>": "<value>" },
  "role": "<optional>",
  "signature": "<base64 bytes>"
}
```

- `created` is a JSON string: an RFC 3339 `date-time` in UTC, written
  exactly as `YYYY-MM-DDThh:mm:ssZ` (upper-case `T` and `Z`, no fractional
  seconds, no numeric offset). Any other form MUST be rejected. It is a
  string, not a number, because signed SAGE objects contain no numbers
  (`02-jcs.md`, errata E02-05).
- `nonce` has the syntax of `03-rfc9421.md` §5 (errata E03-12);
  `recipient` is the DID the sender addresses.
- Optional members that are absent are omitted, not sent as `null` or `""`.
  Every member is a string except `metadata`, an object whose values are
  strings.
- Signing input: `REQUEST_LABEL || JCS(envelope without signature)`, with
  `REQUEST_LABEL` from §6.
- `payload` is a JSON string holding canonical standard base64 (RFC 4648
  alphabet, with padding) of the raw payload bytes (`00-overview.md` §7.2).
- A receiver MUST, in this order: check sizes and syntax (the size limit at
  the start of this chapter, the field limits of this section, and
  `02-jcs.md`, errata E02-02 to E02-06); require `recipient` to equal its
  own DID and `did` to name an active agent (canonical comparison,
  `06-did-sage.md` §2); require `now - 300 s <= created <= now +
  MaxClockSkew` (skew as in `03-rfc9421.md`, errata E03-11); verify
  `signature`; and, last, check and reserve `(did, nonce)` in a replay
  store retained at least until `created + 300 s + MaxClockSkew`, with the
  store rules of `03-rfc9421.md` (errata E03-12).

`signature` is standard base64 of the signature made with the sender's
`06-did-sage.md` §3.1 key: 64 bytes for Ed25519, 65 bytes for secp256k1
(`01-crypto.md`).

`id`, `context_id` and `task_id` MUST be at most 128 bytes of printable
ASCII; `role` at most 32; `metadata` at most 32 entries, keys at most 64
bytes of `ALPHA / DIGIT / "-" / "_"`, values at most 1 KiB.

A receiver MUST NOT act on any member of a `WireMessage`, nor decode or
dispatch its `payload`, before every check of §1 has passed. A check that
can only reject (the size limit, and the cookie of `04-hpke.md` §7) MAY
run earlier. `metadata` and
`role` are signed assertions of the sender, not facts: they MUST NOT by
themselves grant authority. A payload that names a DID (as the HPKE init
names `initDid`) MUST name the same DID as `did`.

## 2. WireResponse

```json
{ "success": true, "message_id": "<id>", "task_id": "<optional>", "data": "<base64>", "error": "<optional>",
  "did": "<responder DID>", "created": "<YYYY-MM-DDThh:mm:ssZ>", "request_hash": "<base64url>", "signature": "<base64 bytes>" }
```

- `request_hash` is base64url without padding of
  `SHA-256(REQUEST_LABEL || JCS(request envelope without signature))`: the
  exact signing input of the request as the responder rebuilt and verified
  it (§1). `message_id` equals the request `id`.
- `created` has the form of §1. Signing input:
  `RESPONSE_LABEL || JCS(response without signature)`, with
  `RESPONSE_LABEL` from §6, signed by the responder's `06-did-sage.md` §3.1
  key.
- A response to a request whose verification failed cannot carry a
  `request_hash` of a verified request; it is the fixed unsigned object
  `{"success":false,"error":"authentication failed"}` (see the `error`
  rule below). Once the request has been accepted (every check of §1 and,
  for the HPKE responder, every step of `04-hpke.md` §6 passed), every
  response, including `success: false` from the handler, is signed.
- The requester MUST reject a response unless the signature verifies under
  the key of `did`, `did` equals the `recipient` of its request (canonical
  comparison), `request_hash` equals the hash of the signing input it sent,
  `message_id` equals its `id`, and `created` is within the window of §1.
  An unsigned response, or one that fails any check, is a failure and none
  of its members may be used (as `03-rfc9421.md`, errata E03-20).

`data` is standard base64 of the response bytes. Every response of the
`/messages` endpoint is HTTP 200 with a `WireResponse` body, including
`success: false` and including requests rejected before the handler for
method, content type or size (see the `error` rule below).

`error` takes exactly two values. Every failure of an inbound message
before it reaches the application handler (size, parsing, envelope syntax,
recipient, freshness, resolution, signature, replay, and for the HPKE
responder every step of `04-hpke.md` §6) MUST produce `success: false`,
`error: "authentication failed"`. `internal error` is used only when the
application handler itself fails after the message was accepted. No other
value, and no text from verification, parsing or handlers, may appear.

## 3. HTTP headers

| Header | Content |
|---|---|
| `X-SAGE-DID` | sender DID; MUST equal `did` in the body |
| `X-SAGE-Message-ID` | MUST equal `id` |
| `X-SAGE-Context-ID` | MUST equal `context_id` when present |
| `X-SAGE-Task-ID` | MUST equal `task_id` when present |
| `X-SAGE-Meta-<key>` | one header per `metadata` entry |

The HTTP transport accepts only `POST /messages` with
`Content-Type: application/json`.

The HTTP server rejects a request whose headers disagree with the body.
`X-SAGE-DID` and `X-SAGE-Message-ID` MUST be present; `X-SAGE-Context-ID`
and `X-SAGE-Task-ID` MUST be present when the body has the member. A
missing or different header MUST be rejected.

The body's `metadata` is authoritative. A receiver MUST reject a request
with an `X-SAGE-Meta-<key>` header whose value differs from
`metadata[<key>]` or for which the body has no such key, and MUST NOT copy
header values into `metadata`.

Over HTTP, the sender MUST sign the request per `03-rfc9421.md`, covering
`x-sage-did`, and the server MUST sign its response; each receiver MUST
verify per `03-rfc9421.md` and MUST reject an unsigned or failing message;
`x-sage-did` is a covered component there, so the DID cannot be changed
without invalidating the signature.

## 4. WebSocket

The same `WireMessage` / `WireResponse` JSON objects are sent as text
frames; the `X-SAGE-*` headers are not used. There is no RFC 9421
signature on WebSocket. A WebSocket message is protected by the envelope
signatures of §1 and §2 and the connection's own TLS.

## 5. Session record carriage

0.9.0-draft.1.1 defines no message that carries a `05-session.md` record
or the `kid` of `04-hpke.md` §6. Two peers can derive matching session
keys but cannot exchange protected records interoperably; application data
relies on TLS (the TLS rule at the start of this chapter). Defining the
carriage is a future, additive change.

## 6. Signing labels

| Constant | Exact bytes (ASCII) | Hex | Length |
|---|---|---|---|
| `REQUEST_LABEL` | `sage-wire-request|0.9` followed by one LF (0x0A) | `736167652d776972652d726571756573747c302e390a` | 22 |
| `RESPONSE_LABEL` | `sage-wire-response|0.9` followed by one LF (0x0A) | `736167652d776972652d726573706f6e73657c302e390a` | 23 |

No other bytes (no length prefix, no terminator) precede the JCS bytes. A
signature made under one label MUST NOT verify under the other.

## Known residual risks

- No protocol version on the wire (errata E00-07, deferred). `WireMessage`
  and `WireResponse` carry no `version` member and there is no
  `X-SAGE-Version` header. Risk: low.
- Domain separation only for the transport envelopes (errata E08-03,
  deferred beyond this chapter). The card JCS, the HPKE response JCS, the
  PoP digest and the RFC 9421 base keep their draft.1 signing inputs
  without a context label. Risk: medium.

## Changes from 0.9.0-draft.1

- E08-01 (c) The envelope is not signed
- E08-02 (c) Responses are unsigned and unbound
- E08-03 (c) No domain separation between signing contexts (applied to the chapter 08 labels only)
- E08-04 (b) What a receiver may act on
- E08-05 (b) HTTP requests and responses are signed per 03
- E08-06 (b) Identity headers are required
- E08-07 (b) `X-SAGE-Meta-*` cannot add metadata
- E08-08 (a) WireResponse encoding and status
- E08-09 (b) `error` carries no internal detail
- E08-10 (a) Transport size limits
- E08-11 (b, b-limit) Field limits
- E08-12 (a) Endpoint
- E08-13 (a) WebSocket has no RFC 9421 signature
- E08-14 (b) TLS is required
- E08-15 (a) Session records have no carriage in 0.9.0
- E08-16 (a) Payload signature encoding
