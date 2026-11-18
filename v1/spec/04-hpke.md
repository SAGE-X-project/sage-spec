# 4. HPKE handshake profile

Version: 0.9.0-draft.1.1. Finalizes 0.9.0-draft.1 with the errata in [../docs/errata-0.9.0-draft.1.md](../docs/errata-0.9.0-draft.1.md).

Vectors: `vectors/hpke.json`. Go sources: `pkg/agent/hpke/` (`types.go`,
`common.go`, `client.go`, `server.go`) and
`pkg/agent/crypto/keys/x25519.go`.

## 1. Suite

| Parameter | Value |
|---|---|
| Mode | HPKE Base (RFC 9180 §5.1), export interface only |
| KEM | DHKEM(X25519, HKDF-SHA256) |
| KDF | HKDF-SHA256 |
| AEAD | ChaCha20-Poly1305 (the HPKE AEAD is never used for payload; sessions use their own keys, `05-session.md`) |
| Suite id string | `hpke-base+x25519+hkdf-sha256` |
| Combiner id string | `e2e-x25519-hkdf-v1` |
| Export length | 32 bytes |

## 2. Info and export context

Both strings are ASCII and fixed in order and delimiters:

```
info      = "sage/hpke-info|v1|suite=" suite "|combiner=" combiner "|ctx=" ctxID "|init=" initDID "|resp=" respDID
exportCtx = "sage/hpke-export|v1|suite=" suite "|combiner=" combiner "|ctx=" ctxID
```

`info` is the HPKE `info` input to `SetupBaseS/R`; `exportCtx` is the HPKE
export context and also the HKDF salt of the combiner.

`ctxID` MUST be 1 to 128 characters of `ALPHA / DIGIT / "-" / "_" / "."`;
a responder MUST reject any other value before any public-key operation.

## 3. Key agreement

1. The initiator encapsulates to the responder's static X25519 KEM key and
   exports `exporterHPKE = Export(exportCtx, 32)`. The encapsulated key is
   `enc` (32 bytes). The responder's KEM key is selected from the registry
   record by `06-did-sage.md` §3.1 (errata E06-11; see also the next
   paragraph). The agent card is not a source of the KEM key.

   An initiator MUST encapsulate only to the KEM key selected by
   `06-did-sage.md` §3.1: the dedicated KEM field when it is non-empty and
   equals the `key_data` of a type-2 entry listed in `keys[]`; otherwise,
   when the dedicated field is empty, the first type-2 entry listed in
   `keys[]`. When the dedicated field is non-empty but not listed, the
   record has no usable KEM key and the handshake MUST NOT start; the
   initiator MUST NOT fall back to another entry. The chain's `verified`
   flag is not consulted.
2. In parallel the initiator generates an ephemeral X25519 key `ephC` and
   the responder an ephemeral key `ephS`; `ssE2E = X25519(ephC, ephS)`.
   An all-zero `ssE2E` MUST be rejected (this also rejects a low-order
   `ephS` at the initiator and a low-order `ephC` at the responder).
3. Session seed:

```
prk  = HKDF-Extract(SHA-256, ikm = exporterHPKE || ssE2E, salt = exportCtx)
seed = HKDF-Expand(SHA-256, prk, "SAGE-HPKE+E2E-Combiner", 32)
```

The exporter alone or `ssE2E` alone never becomes a key.

## 4. Traffic keys and channel binding

No 0.9.0-draft.1.1 message or record uses these outputs; session keys come
from `05-session.md` §2. They are defined because `hpke/traffic-keys` pins
them and because §5 uses the same expansion for `ackKey`.

From `seed`, using the counter-mode expansion
`expand(key, label, n) = HMAC-SHA256(key, label || be32(counter))...`
truncated to `n` bytes (counter starts at 1):

| Output | Label | Length |
|---|---|---|
| C2S key | `SAGE-c2s:key` | 32 |
| C2S IV | `SAGE-c2s:iv` | 12 |
| S2C key | `SAGE-s2c:key` | 32 |
| S2C IV | `SAGE-s2c:iv` | 12 |
| Channel binding | `SAGE-cb-v1` | 32 |

Note that this expansion is HMAC-based and is not RFC 5869 HKDF-Expand
(which would also feed the previous block back in). The session layer
(`05-session.md`) uses standard HKDF; the two must not be confused.

## 5. Acknowledgement tag

Proves to the initiator that the responder derived the same seed and binds
the whole transcript:

```
ackKey = expand(seed, "SAGE-ack-key-v1", 32)
th     = SHA-256(0x00 || info || 0x00 || exportCtx || 0x00 || enc || 0x00 || ephC || 0x00 || ephS || 0x00 || initDID || 0x00 || respDID)
ackTag = HMAC-SHA256(ackKey, "SAGE-ack-msg|v1|" || len16(ctxID) || len16(nonce) || len16(kid) || th)
```

`info`, `exportCtx` and the DIDs are their ASCII bytes; `enc`, `ephC` and
`ephS` are the raw 32-byte keys, not their base64 text. The `0x00`
separators are unambiguous only because the keys have fixed length and the
ASCII fields cannot contain `0x00` (§2; `06-did-sage.md`, errata E06-02).

`binds_order` in the vector fixes the transcript order. Compare with a
constant-time equality.

## 6. Messages

### 6.0 Framing

The init is a `WireMessage` (`08-transport.md` §1) with
`task_id = "hpke/complete@v1"`, `context_id = ctxID`, `did = initDID`,
`recipient = respDID`, `payload` = the UTF-8 bytes of the init JSON object,
and `signature` = the initiator's envelope signature of `08-transport.md` §1
(request label followed by the JCS bytes of the envelope without
`signature`), made with its `06-did-sage.md` §3.1 signing key. `ctxID` is
not a member of the init object; it is the envelope's `context_id`. The
response envelope is the `data` of a `WireResponse` (UTF-8 JSON bytes) that
the responder signs per `08-transport.md` §2; inside it, `sigB64` and
`ackTagB64` remain the handshake's own protection. A responder MUST verify
the envelope signature (`08-transport.md` §1) before any step of §6.

### Init payload (initiator to responder), JSON object

| Member | Type | Content |
|---|---|---|
| `initDid` | string | initiator DID; MUST equal the DID that signed the transport message |
| `respDid` | string | responder DID; MUST equal the receiving agent's DID |
| `info` | string | the `info` bytes of §2 as a JSON string (they are ASCII) |
| `exportCtx` | string | the `exportCtx` bytes of §2 as a JSON string |
| `nonce` | string | UUID, unique per context; replay-checked per the replay store rule below |
| `ts` | string | RFC 3339 with nanoseconds; MUST be within ±2 minutes of the responder's clock |
| `enc` | base64url-raw | 32-byte encapsulated key |
| `ephC` | base64url-raw | 32-byte initiator ephemeral X25519 public key |

The init object MUST have exactly the eight members of the table, each a
JSON string, and is subject to `02-jcs.md` (errata E02-02 to E02-04). `enc`
and `ephC` MUST be canonical base64url without padding and decode to
exactly 32 bytes. `nonce` MUST be a canonical lower-case UUID (36
characters). `ts` MUST be RFC 3339 with an explicit offset. The payload
MUST NOT exceed 4 KiB. The responder checks, in order: payload limits and
syntax; `initDid` equals the envelope `did` whose signature verified;
`respDid` equals its own DID; `ts`; `info` and `exportCtx` recomputed; HPKE
open and the ECDH checks of §3. It marks the nonce as used only after every
one of these checks has succeeded (`00-overview.md` §7.4).

Replay store: the responder MUST retain `(ctxID, nonce)` for at least 600
seconds (more than twice the ±120 s `ts` window). When the store is full it
MUST reject new inits rather than evict unexpired entries. After losing the
store it MUST reject inits whose `ts` precedes the restore time plus 120 s.

The responder recomputes `info` and `exportCtx` from `ctxID` and the two
DIDs and MUST reject the payload when they differ from the received values.
Every rejection, at any step (task, DID resolution, signature, parsing,
cookie, timestamp, replay, `info`, HPKE open, ECDH), returns the same
generic error `authentication failed` to the peer, through the same
transport response.

### Response envelope (responder to initiator), JSON object

| Member | Content |
|---|---|
| `v` | `"v1"`; anything else MUST be rejected |
| `task` | `"hpke/complete@v1"` |
| `ctx` | context id |
| `kid` | session key id issued by the responder (`kid-<uuid>` by default, or from a `KeyIDBinder`) |
| `ephS` | base64url-raw responder ephemeral public key |
| `ackTagB64` | base64url-raw `ackTag` |
| `ts` | RFC 3339 nanoseconds. Informative. The response is bound to the init by `ackTag` and the echoed `enc`/`ephC`, so the initiator need not check `ts`. |
| `did` | responder DID |
| `infoHash`, `exportCtxHash` | base64url-raw SHA-256 of the `info` and `exportCtx` bytes |
| `enc`, `ephC` | echoed from the init payload |
| `sigB64` | base64url without padding of the signature, made with the responder's `06-did-sage.md` §3.1 signing key and the algorithm of that key's type (`01-crypto.md`), over the JCS bytes of the envelope without `sigB64` |

The initiator MUST reject a response unless: it is valid per `02-jcs.md`
(errata E02-02 to E02-06) and has exactly the 13 members; `v` is `v1`;
`task` is `hpke/complete@v1`; `ctx` equals its `ctxID`; `did` equals the
`respDid` it sent; `enc` and `ephC` equal what it sent; `infoHash` and
`exportCtxHash` equal SHA-256 of its own `info` and `exportCtx`; `kid` is 1
to 128 printable ASCII characters; `ephS` decodes to 32 bytes; `sigB64`
verifies under the key resolved for `did`; `ssE2E` is not all-zero (this
also rejects a low-order `ephS`); and `ackTag` matches in constant time.
Only then does it create the session with label `sage/hpke+e2e v1`
(`05-session.md` §1.1).

### Unconfirmed responder session

The responder creates its session when it sends the response, before the
initiator has proved it holds the matching keys. The session is
*unconfirmed* until the responder accepts a valid inbound session record
from the initiator. The responder MUST NOT send application data under an
unconfirmed session, and MUST destroy it, erasing its keys
(`00-overview.md` §7, DP-3), when the idle timeout (`05-session.md` §7)
expires. Because 0.9.0-draft.1.1 defines no carriage of session records
(`08-transport.md`, errata E08-15), a responder session established
under 0.9.0-draft.1.1 alone stays unconfirmed and always ends at the idle
timeout.

## 7. Denial-of-service cookie (optional)

0.9.0-draft.1.1 defines no way to issue a cookie, so a cookie is a local
mechanism: a responder MUST NOT require one from an initiator that has no
out-of-band way to obtain it. When a responder uses cookies, it MUST check
the cookie before DID resolution, signature verification and any HPKE
operation, and a failed cookie check returns the generic error (§6).
`metadata` is signed by the sender but grants nothing by itself
(`08-transport.md` §1); a cookie MUST be
bound by its issuer to `ctxID`, `initDid` and `respDid`.

## 8. Open items

| Id | Item |
|---|---|
| O-7 | The expansion is a single HMAC block per 32-byte output and is a PRF under HMAC's assumptions; it is kept. Replacing it changes `ackTag` and is a breaking change. |

## Known residual risks

- **E04-18 (key binding).** `info` and the transcript hash `th` bind the
  two DIDs but not the keys that resolution returned for them (the
  responder's KEM key and both signing keys), so the DID-to-key binding is
  whatever resolution returned at that moment. Risk if left: low to medium,
  unquantified; no concrete attack is known.

## Changes from 0.9.0-draft.1

- E04-01 (a) Where the KEM key comes from (updated for SN-8)
- E04-02 (b) Only a listed KEM key is used (resolved SN-8)
- E04-03 (a) §4 outputs are not used by any 0.9.0 message (O-7 closed)
- E04-04 (a) Framing of the two messages (resolved SN-1)
- E04-05 (b, b-limit) `ctxID` syntax
- E04-06 (b) Init payload is parsed strictly
- E04-07 (a) One generic error, no exceptions
- E04-08 (a) Response signature: key and encoding
- E04-09 (b) Initiator checks are normative
- E04-10 (a) The zero check is on the shared secret
- E04-11 (a) Cross-reference
- E04-12 (a) The cookie is local, and is checked first (O-6 closed)
- E04-13 (b) Responder session stays unconfirmed (resolved SN-9)
- E04-14 (b) Init replay store
- E04-16 (a) Byte form of the transcript binds
- E04-17 (a) Response `ts` is informative
- E04-15 (a) `hpke.json` description (applied in `vectors/hpke.json`)
