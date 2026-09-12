# 4. HPKE handshake profile

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

## 3. Key agreement

1. The initiator encapsulates to the responder's static X25519 KEM key
   (published in the agent card / registry as `public_kem_key`) and exports
   `exporterHPKE = Export(exportCtx, 32)`. The encapsulated key is `enc`
   (32 bytes).
2. In parallel the initiator generates an ephemeral X25519 key `ephC` and
   the responder an ephemeral key `ephS`; `ssE2E = X25519(ephC, ephS)`.
   An all-zero `ssE2E` MUST be rejected.
3. Session seed:

```
prk  = HKDF-Extract(SHA-256, ikm = exporterHPKE || ssE2E, salt = exportCtx)
seed = HKDF-Expand(SHA-256, prk, "SAGE-HPKE+E2E-Combiner", 32)
```

The exporter alone or `ssE2E` alone never becomes a key.

## 4. Traffic keys and channel binding

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

`binds_order` in the vector fixes the transcript order. Compare with a
constant-time equality.

## 6. Messages

### Init payload (initiator to responder), JSON object

| Member | Type | Content |
|---|---|---|
| `initDid` | string | initiator DID; MUST equal the DID that signed the transport message |
| `respDid` | string | responder DID; MUST equal the receiving agent's DID |
| `info` | base64url-raw | the `info` bytes of §2 |
| `exportCtx` | base64url-raw | the `exportCtx` bytes of §2 |
| `nonce` | string | UUID, unique per context; replay-checked per `ctxID` for 10 minutes |
| `ts` | string | RFC 3339 with nanoseconds; MUST be within ±2 minutes of the responder's clock |
| `enc` | base64url-raw | 32-byte encapsulated key |
| `ephC` | base64url-raw | 32-byte initiator ephemeral X25519 public key |

The responder recomputes `info` and `exportCtx` from `ctxID` and the two
DIDs and MUST reject the payload when they differ from the received values.
All rejections return one generic error (`authentication failed`); the
reason is logged locally only. A suite the responder does not allow is the
one distinct error.

### Response envelope (responder to initiator), JSON object

| Member | Content |
|---|---|
| `v` | `"v1"`; anything else MUST be rejected |
| `task` | `"hpke/complete@v1"` |
| `ctx` | context id |
| `kid` | session key id issued by the responder (`kid-<uuid>` by default, or from a `KeyIDBinder`) |
| `ephS` | base64url-raw responder ephemeral public key |
| `ackTagB64` | base64url-raw `ackTag` |
| `ts` | RFC 3339 nanoseconds |
| `did` | responder DID |
| `infoHash`, `exportCtxHash` | base64url-raw SHA-256 of the `info` and `exportCtx` bytes |
| `enc`, `ephC` | echoed from the init payload |
| `sigB64` | detached: signature over the JCS form of the envelope without `sigB64`, with the responder's signing key (`01-crypto.md`) |

The initiator verifies `sigB64` against the responder's resolved public key,
checks `ephS` is not all-zero, recomputes the seed and `ackTag`, and only
then creates the session with label `sage/hpke+e2e v1` (`05-session.md` §2).

## 7. Denial-of-service cookie (optional)

A responder MAY require a cookie in the transport metadata (`metadata.cookie`)
before doing any public-key work; the cookie check happens before DID
resolution (open item O-6 tracks the ordering in the Go core).

## 8. Open items

| Id | Item |
|---|---|
| O-6 | Cookie check before DID resolution in the Go responder |
| O-7 | The HMAC counter expansion of §4 differs from HKDF-Expand; decide whether v2 aligns it |
