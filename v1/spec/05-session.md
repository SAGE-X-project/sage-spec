# 5. Session layer

Version: 0.9.0-draft.1.1. Finalizes 0.9.0-draft.1 with the errata in [../docs/errata-0.9.0-draft.1.md](../docs/errata-0.9.0-draft.1.md).

Vectors: `vectors/session.json`. Go source: `pkg/agent/session/session.go`,
`manager.go`, `types.go`.

## 1. Seed and session id

### 1.1 Sessions established by the handshake

For a session established by `04-hpke.md`, the session seed is the 32-byte
`seed` of `04-hpke.md` §3 itself, with no further extraction, and
`sid = base64url-raw(SHA-256("sage/hpke+e2e v1" || seed)[0:16])`.
The initiator takes the `c2s` direction.

### 1.2 Seed from an external secret (local use)

Inputs: an external 32-byte shared secret, the context id, two ephemeral
public keys and a label.

```
(lo, hi) = the two ephemeral public keys sorted as byte strings
salt     = SHA-256(label || ctxID || lo || hi)
seed     = HKDF-Extract(SHA-256, sharedSecret, salt)
sid      = base64url-raw(SHA-256(label || seed)[0:16])
```

This path is pinned by the `seed-and-id` vector. No 0.9.0-draft.1.1
protocol uses this path between peers.

The only label used between peers is `sage/hpke+e2e v1`. An empty label
MUST be rejected; there is no default. `sage/hpke v1` and
`a2a/handshake v1` are not part of 0.9.0-draft.1.1. The label is part of
the derivation, so peers MUST agree on it.

## 2. Key schedule

All expansions are RFC 5869 HKDF-SHA256 with `ikm = seed` and
`salt = sid`. `salt` is the 22 ASCII bytes of the base64url-raw `sid`
string, not the 16 decoded bytes.

| Info | Output |
|---|---|
| `sage-session-keys-v1` | 64 bytes: `encryptKey[32] || signingKey[32]` (shared, non-directional) |
| `sage-directional-keys-v1` | 128 bytes: `c2sEnc[32] || c2sSign[32] || s2cEnc[32] || s2cSign[32]` |
| `sage-session-rekey-v1` `|| direction || be64(generation)` | 32 bytes: rotated AEAD key for that direction and generation |

`direction` is `c2s` or `s2c` for directional keys, and the ASCII string
`single` for the shared keys.
A session established by `04-hpke.md` MUST use only the directional keys,
for every record in both directions, and a receiver on such a session MUST
NOT attempt to open a record with the shared keys. The shared keys are
defined for single-party use and for the `encrypt-decrypt` vector; they
MUST NOT be used between two peers.

## 3. Record format

```
record = be64(seq) || nonce[12] || ChaCha20-Poly1305(key, nonce, plaintext, aad = be64(seq) || callerAAD)
```

- `seq` starts at 0 per sender and increments by one per record, shared by
  every encrypt entry point of the session.
- `nonce` is 12 random bytes from a CSPRNG. It is not derived from `seq`.
- The 8-byte sequence header is authenticated as AAD; the caller's AAD, if
  any, follows it.
- Records shorter than 36 bytes (8-byte `seq`, 12-byte nonce, 16-byte tag)
  MUST be rejected before any AEAD operation.
- A receiver MUST reject a record longer than 16 MiB + 36 bytes and caller
  AAD longer than 4 KiB.
- A sender MUST NOT encrypt more than 2^32 records under one generation key
  and MUST end the session before `seq` reaches 2^64 - 1. A receiver MUST
  reject `seq = 2^64 - 1`.

## 4. Replay window

The window is per session and per receive direction. Let `top` be the
highest accepted `seq`. A record with `seq <= top - 1024` is stale; a
record with `seq` already marked is a replay; the window moves only after
the AEAD opens.

## 5. Key rotation

With `RekeyInterval = R`, record `seq` uses generation `g = seq / R`. `R`
is 256 for every session between peers. Other values exist only for
single-party use. Generation 0 uses the base key; generation
`g > 0` uses the key derived with info `sage-session-rekey-v1 || direction ||
be64(g)` of §2. Receivers derive on demand from `seq`, so out-of-order
delivery across a boundary still decrypts. The vector `encrypt-decrypt`
holds one record at `seq 0` and one at `seq 256` (generation 1).

## 6. MAC path (informative)

No 0.9.0-draft.1.1 message carries `mac`. An implementation that offers
this local API MUST use the sender's outbound directional signing key.

`EncryptAndSign(plaintext, covered)` additionally returns
`mac = HMAC-SHA256(signingKey, covered)` using the signing key of the same
direction; `DecryptAndVerify` checks it with a constant-time compare before
opening the record.

## 7. Lifetime

Sessions expire on absolute age (`MaxAge`, default 1 h), idle time
(`IdleTimeout`, default 10 min) or message count (`MaxMessages`, default
1000). These are local policy and not on the wire. Whatever values are
configured, an implementation MUST enforce them on every encrypt and
decrypt operation and MUST destroy an expired session, erasing its seed and
keys (`00-overview.md` §7, DP-3). `MaxAge` MUST NOT exceed 24 hours.

## Changes from 0.9.0-draft.1

- E05-01 (a, see note) The handshake's session seed and id
- E05-02 (b) One label, no default
- E05-03 (a) Rekey direction string for shared keys
- E05-04 (c) Shared keys allow reflection; peers use directional keys only
- E05-05 (a) The MAC path is not part of interoperability
- E05-06 (c) Rekey interval is fixed
- E05-07 (b) Minimum record length
- E05-08 (b, b-limit) Maximum record length
- E05-09 (b) Limits on one key
- E05-10 (b) Lifetime is enforced on every path
- E05-11 (a) Replay window details
- E05-12 (a) The salt is the ASCII session id
