# 5. Session layer

Vectors: `vectors/session.json`. Go source: `pkg/agent/session/session.go`,
`manager.go`, `types.go`.

## 1. Seed and session id

Inputs: a shared secret (the HPKE seed of `04-hpke.md` §3, or another
32-byte secret), the context id, both ephemeral public keys and a label.

```
(lo, hi) = the two ephemeral public keys sorted as byte strings
salt     = SHA-256(label || ctxID || lo || hi)
seed     = HKDF-Extract(SHA-256, sharedSecret, salt)
sid      = base64url-raw(SHA-256(label || seed)[0:16])
```

Labels in use: `sage/hpke+e2e v1` (HPKE handshake), `sage/hpke v1`
(manager path), `a2a/handshake v1` (default when empty; legacy). The label
is part of the derivation, so peers MUST agree on it.

## 2. Key schedule

All expansions are RFC 5869 HKDF-SHA256 with `ikm = seed` and
`salt = sid` (the session id string bytes):

| Info | Output |
|---|---|
| `sage-session-keys-v1` | 64 bytes: `encryptKey[32] || signingKey[32]` (shared, non-directional) |
| `sage-directional-keys-v1` | 128 bytes: `c2sEnc[32] || c2sSign[32] || s2cEnc[32] || s2cSign[32]` |
| `sage-session-rekey-v1` `|| direction || be64(generation)` | 32 bytes: rotated AEAD key for that direction and generation |

`direction` is the ASCII string `c2s` or `s2c`; the initiator sends on `c2s`.
The shared keys exist for `Encrypt`/`Decrypt` callers that do not use roles;
role-aware sessions use the directional keys and MUST NOT mix the two on one
record stream.

## 3. Record format

```
record = be64(seq) || nonce[12] || ChaCha20-Poly1305(key, nonce, plaintext, aad = be64(seq) || callerAAD)
```

- `seq` starts at 0 per sender and increments by one per record, shared by
  every encrypt entry point of the session.
- `nonce` is 12 random bytes from a CSPRNG. It is not derived from `seq`.
- The 8-byte sequence header is authenticated as AAD; the caller's AAD, if
  any, follows it.
- Records shorter than 20 bytes are rejected (`ErrDataTooShort`).

## 4. Replay window

Receivers keep a sliding window of 1024 sequence numbers per session
(bitmap). A record whose `seq` was already accepted is a replay
(`ErrReplayedMessage`); a record older than the window is stale
(`ErrStaleMessage`). The window is updated only after the AEAD opens
successfully.

## 5. Key rotation

With `RekeyInterval = R` (default 256; 0 disables rotation), record `seq`
uses generation `g = seq / R`. Generation 0 uses the base key; generation
`g > 0` uses the key derived with info `sage-session-rekey-v1 || direction ||
be64(g)` of §2. Receivers derive on demand from `seq`, so out-of-order
delivery across a boundary still decrypts. The vector `encrypt-decrypt`
holds one record at `seq 0` and one at `seq 256` (generation 1).

## 6. MAC path

`EncryptAndSign(plaintext, covered)` additionally returns
`mac = HMAC-SHA256(signingKey, covered)` using the signing key of the same
direction; `DecryptAndVerify` checks it with a constant-time compare before
opening the record.

## 7. Lifetime

Sessions expire on absolute age (`MaxAge`, default 1 h), idle time
(`IdleTimeout`, default 10 min) or message count (`MaxMessages`, default
1000). These are local policy and not on the wire.
