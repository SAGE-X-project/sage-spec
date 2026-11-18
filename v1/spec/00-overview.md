# 0. Overview

Version: 0.9.0-draft.1.1. Finalizes 0.9.0-draft.1 with the errata in [../docs/errata-0.9.0-draft.1.md](../docs/errata-0.9.0-draft.1.md).

## 1. Scope

SAGE secures messages between AI agents. This specification fixes the parts
that cross an implementation boundary:

1. how an agent's keys are represented and how signatures are encoded
   (`01-crypto.md`);
2. how JSON is canonicalised before it is signed (`02-jcs.md`);
3. how HTTP requests and responses are signed and verified (`03-rfc9421.md`);
4. how two agents establish a shared secret with HPKE (`04-hpke.md`);
5. how that secret becomes session keys and how records are framed
   (`05-session.md`);
6. how agents are named and how their keys are published and proven
   (`06-did-sage.md`, `07-a2a.md`);
7. the transport envelope used by the HTTP and WebSocket transports
   (`08-transport.md`).

Out of scope: on-chain registry contracts (published by
[sage-contracts](https://github.com/SAGE-X-project/sage-contracts)), the
gateway and client integrations, storage, metrics and operational concerns,
and the carriage of session records (05) between peers, which this version
does not define (`08-transport.md` §5).

## 2. Terminology

The key words MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT,
RECOMMENDED, NOT RECOMMENDED, MAY and OPTIONAL are to be interpreted as
described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in
all capitals. "Initiator" is the agent that starts a handshake; "responder"
is the agent that answers. "Agent A" and "agent B" in the vectors are the
initiator and responder respectively.

Encodings used throughout:

| Term | Meaning |
|---|---|
| `hex` | lower-case hexadecimal, no prefix |
| `base64` | RFC 4648 standard alphabet with padding |
| `base64url-raw` | RFC 4648 URL-safe alphabet, no padding |
| `base58` | Bitcoin alphabet |
| `be16(n)` | 16-bit unsigned big-endian |
| `be32(n)` | 32-bit unsigned big-endian |
| `be64(n)` | 64-bit unsigned big-endian |
| `len16(s)` | `be16(len(s)) || s`: the 16-bit unsigned big-endian byte length of `s`, followed by `s` itself. `s` appears once. A value longer than 65 535 bytes cannot be encoded and MUST be rejected before any derivation that uses it. |
| `a || b` | byte concatenation |

## 3. Layering

```
transport envelope (08)        WireMessage / WireResponse, X-SAGE-* headers
  HTTP signatures (03)         RFC 9421 over the request and the response
    session records (05)       ChaCha20-Poly1305, seq header, replay window
      HPKE handshake (04)      exporter secret + E2E X25519 -> session seed
        identity (06, 07)      did:sage, key proof of possession, agent card
          primitives (01, 02)  Ed25519 / secp256k1 / P-256 / X25519, JCS
```

The diagram shows protection layers, not a strict dependency order. In
particular: the handshake (04) is carried in a transport envelope (08) and
uses its `context_id`, `did` and envelope signature; HTTP signatures (03)
resolve their `keyid` through 06 and compare it with the 08 header
`X-SAGE-DID`. A conforming implementation of a layer MUST pass the vectors of
that layer and of every chapter it uses.

## 4. Conformance levels

| Level | Chapters | Vector suites | Typical implementer |
|---|---|---|---|
| Verifier | 01, 02, 03, 06, 07 | `crypto`, `jcs`, `rfc9421`, `did` (including the card vector) | a gateway or inspector |
| Peer | Verifier + 04, 05, 08 | Verifier + `hpke`, `session`, `transport` | an agent |
| Reference | all | all, and it can regenerate them | a reference generator |

Passing a suite means: every `deterministic` vector reproduces byte for byte,
every `verify` vector verifies, and every `reject` vector is rejected
(`vectors/README.md`). The `transport` suite is listed in errata §11 and is
not yet published; until it is, chapter 08 has no vector. Naming an
implementation as "reference" is informative.

## 5. Versioning

- The specification version is `MAJOR.MINOR.PATCH[-PRERELEASE]` (SemVer 2.0.0, for example
  `0.9.0-draft.1.1`) and is written
  into every vector file as `spec_version`.
- Before `1.0.0`, a breaking change increments MINOR (0.9.x to 0.10.0) and a
  compatible change increments PATCH. From `1.0.0`, breaking changes
  increment MAJOR.
- Breaking means: it alters bytes on the wire, a derivation label, a covered
  component set, a key or signature encoding, or makes a rejection rule
  accept something it rejected before.
- Adding an optional field, a new vector, or clarifying text is a compatible
  change.
- Domain-separation labels carry their own version suffix (for example
  `sage/hpke-info|v1`, `sage-session-keys-v1`). A new label version is a
  breaking change of this specification.
- This version carries no version on the wire. Implementations report the
  version they conform to out of band (documentation, `--version` output,
  conformance reports). A 0.9.0-draft.1.1 peer and a 0.10.0 peer fail each
  other's checks because their labels differ (`sage/hpke-info|v1` versus the
  0.10.0 labels); they do not misinterpret each other.

## 6. Normative status

This text and the vectors in `vectors/` are the specification. Where the
text and a vector disagree, the disagreement is a defect of this
specification; until it is corrected, an implementation MUST reproduce the
vector. No implementation is normative. Where this text cites a source file
("Go sources: ..."), the citation is informative: it records where a rule
came from, not what the rule is.

An ambiguity, a gap or a contradiction is fixed in this text, together with
a vector that pins the fix where the fix is testable; implementations then
follow.

Behaviour that 0.9.0-draft.1 inherited from the Go core because the text was
silent is written out in this version (errata E00-E08). An implementation
MUST NOT rely on any behaviour of a particular core that this text does not
state.

## 7. Data protection requirements

These requirements collect, for every chapter, the rules that keep keys,
payloads and identities from leaking or being misused. They are normative.
Each cites the chapter rule it summarises, by chapter and errata item; where
the two differ, the chapter governs.

### 7.1 Input size limits (DP-1)

A receiver MUST check sizes before parsing, decoding or any cryptographic
operation, and MUST reject (not truncate) an oversized input.

| Input | Maximum | Rule |
|---|---|---|
| HTTP request body, WebSocket message | 1 MiB | 08, E08-10 |
| Body buffered for `Content-Digest` | 16 MiB (only where 08 does not apply) | 03, E03-13 |
| `Signature-Input`, `Signature` field value | 8 KiB each; 32 covered components | 03, E03-21 |
| HTTP header section | 64 KiB | 03, E03-21 |
| RFC 9421 `nonce` | 16-64 characters | 03, E03-12 |
| DID; `keyid` | 256 bytes; 289 bytes | 06, E06-03 |
| HPKE `ctxID`; init payload; `kid` | 128 characters; 4 KiB; 128 characters | 04, E04-05, E04-06, E04-09 |
| Any value passed to `len16` | 65 535 bytes | 00 §2 |
| Signed JSON: HPKE envelopes, card | 64 KiB, depth 16, 256 members or elements, 32 card keys and services | 02, E02-06 |
| Signed JSON: `WireMessage`, `WireResponse` | 1 MiB (transport limit), depth 16, 256 members or elements | 02, E02-06; 08, E08-10 |
| Session record; caller AAD | 16 MiB + 36 bytes; 4 KiB | 05, E05-08 |
| Envelope `id`, `context_id`, `task_id`; `role`; `metadata` | 128 B; 32 B; 32 entries, 64 B keys, 1 KiB values | 08, E08-11 |
| Registry record fields | name 256 B, description 4 KiB, endpoint 2 KiB, 32 keys, capabilities 16 KiB | 06, E06-14 |

### 7.2 Parsing strictness (DP-2)

1. Every encoded value has one accepted form. Base64 and base64url values
   MUST be canonical (correct alphabet, padding as specified, no trailing
   bits, no whitespace). Hex is lower-case. Signatures: 64 bytes Ed25519 and
   P-256, 65 bytes secp256k1, low-S, `v` checked (01, E01-04 to E01-06).
2. JSON that is signed or verified: no duplicate or case-variant member
   names, no unpaired surrogates, valid UTF-8, no trailing data, no numbers,
   exact member sets (02, E02-02 to E02-05; 04, E04-06, E04-09).
3. HTTP signatures: one label, one field line per signature-relevant header,
   canonical `Signature-Input`, no unknown parameters, no component
   parameters other than `;req`, a fixed set of derived components (03,
   E03-03, E03-05 to E03-09).
4. Identifiers: the did:sage grammar with its character set; comparisons on
   the canonical form (06, E06-02, E06-04).
5. A value the receiver acts on MUST come from the same parse that was
   verified (02, E02-01, E02-03).

### 7.3 Key handling and lifetime (DP-3)

1. Private keys never leave the agent that owns them and MUST NOT appear in
   any message, log, error or vector other than the label-derived test keys
   of `vectors/README.md`.
2. A key is used for one purpose: X25519 keys only for key agreement;
   Ed25519 and secp256k1 keys only for signing. Every signature an agent
   makes is over a context-specific input (`08-transport.md` labels for the
   envelopes; JCS objects with fixed member sets for the card and HPKE
   response; the 32-byte PoP digest; the RFC 9421 base), so application
   bytes carried in `payload` cannot be turned into another context's
   signature (08, E08-03). An agent MUST NOT sign bytes in any non-envelope
   context on behalf of another party.
3. Ephemeral private keys (`ephC`, `ephS`, the HPKE encapsulation key) are
   generated per handshake from a CSPRNG, used once, and erased as soon as
   `seed` is computed. `exporterHPKE`, `ssE2E` and `ackKey` are erased after
   `ackTag` is computed or checked. `seed` and all session keys are erased
   when the session ends or expires (05, E05-10).
4. A session ends at the earliest of `MaxAge` (at most 24 h), `IdleTimeout`,
   `MaxMessages`, 2^32 records under one generation key, or the revocation
   of either peer's key being observed (05, E05-09, E05-10). This version has
   no forward secrecy inside a session: compromise of `seed` exposes every
   record of that session.
5. A key is usable only while it is listed in the agent's `keys[]` and, for
   a signing key, carries a valid proof of possession (`06-did-sage.md`)
   that the verifier checked itself; the registry's `verified` flag is not
   used (06, E06-08, E06-11). A KEM key that is not listed is never used
   (04, E04-02). Revocation removes a key from the list and reaches
   verifiers only through resolution, which MUST be at most 300 s old and
   MUST fail closed (06, E06-12).
6. Implementations SHOULD keep long-term private keys in an encrypted store
   or hardware token, and SHOULD compare secrets, MACs and tags in constant
   time (`ackTag` MUST, `04-hpke.md`).

### 7.4 Replay and freshness (DP-4)

| Object | Freshness | Replay store | Rule |
|---|---|---|---|
| RFC 9421 request | `created` within `MaxAge` (≤ 300 s) and skew (≤ 300 s); `expires` if present | `(signer DID, nonce)` kept ≥ `created + MaxAge + skew` | 03, E03-02, E03-11, E03-12 |
| RFC 9421 response | as above | bound to the request by `"signature";req` | 03, E03-10 |
| HPKE init | `ts` within ±120 s | `(ctxID, nonce)` kept ≥ 600 s | 04, E04-14 |
| HPKE response | bound to the init by `ackTag`, `enc`, `ephC` | none needed | 04, E04-09, E04-17 |
| Session record | session lifetime | 1024-entry window per direction | 05, E05-11 |
| Transport request envelope | `created` (`YYYY-MM-DDThh:mm:ssZ`) within 300 s and skew | `(did, nonce)` kept ≥ `created + 300 s + skew` | 08, E08-01 |
| Transport response envelope | `created` within the same window | bound to the request by `request_hash` | 08, E08-02 |
| Resolution result | ≤ 300 s for positive results | n/a | 06, E06-12 |

In every store: an entry is checked and reserved only after the signature or
AEAD and every other check have succeeded, so a rejected message never
consumes a nonce (03, E03-18); a full store rejects new input rather than
evicting live entries; a store that was lost rejects input dated before its
restoration plus the skew. Freshness checks cannot be disabled outside test
harnesses, which fix the clock instead.

### 7.5 Error disclosure (DP-5)

1. Every failure of an inbound message before it reaches the application
   handler (size, syntax, parsing, envelope, freshness, resolution,
   signature, digest, replay, cookie) produces one externally visible result
   per transport: HTTP 401 with body `authentication failed` and a constant
   `WWW-Authenticate` value for RFC 9421; HTTP 200 with the unsigned
   `{"success":false,"error":"authentication failed"}` for 08, which the HPKE
   responder also uses. No header, status, body or error string may depend on
   which check failed (03, E03-17; 04, E04-07; 08, E08-08, E08-09).
2. `internal error` is returned only when the application handler fails
   after the message was accepted, in a signed 08 response. No `bad request`
   or other value exists.
3. There is no distinct error for a disallowed suite, unknown agent,
   inactive agent, revoked key, stale timestamp or replay.
4. Libraries may return detailed errors to their caller; the component that
   answers the peer MUST map them.
5. Cheap checks (sizes, syntax, cookie) come before resolution and signature
   verification; this is for cost, not secrecy, and does not permit distinct
   errors.

### 7.6 Logging (DP-6)

1. MUST NOT log: private keys, seeds, `exporterHPKE`, `ssE2E`, `ackKey`,
   session keys, session plaintext, decrypted payloads, request or response
   bodies, or cookies.
2. SHOULD NOT log full signatures or nonces; log their SHA-256 prefix if
   correlation is needed.
3. MAY log: DIDs, KeyIDs (`01-crypto.md`), message ids, the diagnostic
   reason for a rejection, and timestamps.
4. Values taken from unverified input (for example the `keyid` DID before
   the signature verifies) MUST be marked as unverified, truncated to 256
   bytes, and escaped so that control characters cannot forge log lines.
5. Logs of rejected inputs MUST NOT include more of the input than item 4
   allows.

## Known residual risks

- No protocol version on the wire (errata E00-07, deferred). Envelopes and
  headers carry no version member. Risk: low. Cross-version traffic fails
  closed because the HPKE and session labels differ, but a peer cannot tell
  "wrong version" from "forged".

## Changes from 0.9.0-draft.1

- E00-01 (a) The text and the vectors are normative; no implementation is
- E00-02 (a) BCP 14 key words
- E00-03 (a) `len16` definition and bound
- E00-04 (a) Layer dependencies stated as they are
- E00-05 (a) Conformance levels name chapters, include 07/08, and include negative vectors
- E00-06 (a) Versioning before 1.0 and how the version is reported
- E00-08 (a) Vector file format: version value, `reject` mode, generator constant (in `vectors/README.md`)
- E00-09 (a) New §7 "Data protection requirements" and the scope note
- E00-10 (b) Disclosure and logging rules (cross-chapter), as §7.5 and §7.6
- E00-11 (b) Private key and secret handling, as §7.3
