# 1. Cryptographic primitives

Version: 0.9.0-draft.1.1. Finalizes 0.9.0-draft.1 with the errata in [../docs/errata-0.9.0-draft.1.md](../docs/errata-0.9.0-draft.1.md).

Vectors: `vectors/crypto.json`. Go sources: `pkg/agent/crypto/keys/`
(`ed25519.go`, `secp256k1.go`, `secp256k1_keccak.go`, `p256.go`,
`ecdsa_encoding.go`, `verify.go`, `keyid.go`).

## 1. Key types

| Type | Curve | Use | Public key encoding |
|---|---|---|---|
| Ed25519 | edwards25519 | signing (default) | 32 bytes (RFC 8032) |
| secp256k1 | secp256k1 | signing, Ethereum identity | 65-byte uncompressed SEC1 (`04 || X || Y`) |
| P-256 | NIST P-256 | signing (optional) | 65-byte uncompressed SEC1 |
| X25519 | curve25519 | key agreement (HPKE, E2E) | 32 bytes (RFC 7748) |

The canonical encoding of a secp256k1 public key is 65-byte uncompressed
SEC1. A registry record's `key_data` for type 0 MAY be 33-byte compressed,
64-byte `X || Y` or 65-byte uncompressed; a verifier MUST decode all three to
the same point and MUST reject any other length. KeyID (§4), the Ethereum
address and the agent card (`07-a2a.md`) use the 65-byte form. The proof of
possession (`06-did-sage.md` §4) uses `key_data` exactly as stored.

A verifier MUST reject a secp256k1 or P-256 public key that is not a valid
point on the curve or is the point at infinity, an Ed25519 key per §2
(Ed25519), and an X25519 key that is not 32 bytes. X25519 public keys from a
peer (`enc`, `ephC`, `ephS`) are checked by the all-zero shared-secret rule of
`04-hpke.md` §3.

On-chain and in agent cards the registry key type is an integer:
ECDSA (secp256k1) = 0, Ed25519 = 1, X25519 = 2 (`did/types_v4.go`).
A 0.9.0-draft.1.1 registry record can only carry types 0, 1 and 2. P-256 is
defined for signatures (vectors `crypto/p256-sha256-sign`,
`rfc9421/request-ecdsa-p256-sha256`) but no 0.9.0-draft.1.1 did:sage record
can publish a P-256 key, so a P-256 signature is verifiable only with a key
obtained by a means outside this specification. The integer is a registry
storage code, not an algorithm identifier.

## 2. Signature algorithms

### Ed25519

Pure Ed25519 over the message bytes. No pre-hash, no context string.
Signature: 64 bytes `R || S`.

Verifiers MUST implement RFC 8032 §5.1.7 with the cofactorless equation
`[S]B = R + [k]A`, and MUST reject: a signature that is not 64 bytes;
`S >= L`; a non-canonical encoding of `A` or `R` (y >= p); a public key `A`
of small order (the eight torsion points). Registries and verifiers MUST
reject a small-order public key.

### secp256k1 (Ethereum convention)

This is the single secp256k1 convention on every SAGE path (RFC 9421, HPKE
envelope, A2A proof, CLI):

1. `digest = Keccak-256(message)` (not SHA-256; not the EIP-191 personal
   prefix).
2. ECDSA with RFC 6979 deterministic nonces.
3. `s` MUST be in the lower half of the group order (low-S).
4. Signature: 65 bytes `r || s || v`, `v` in {0, 1} (the recovery id, not 27/28).

Verifiers MUST accept only a 65-byte `r || s || v` with `1 <= r, s < n`,
`s <= n/2` (low-S) and `v` in {0, 1}, and MUST check that the public key
recovered with `v` equals the resolved key. A 64-byte signature, a DER
signature, a high-S signature and `v` in {27, 28} MUST be rejected.

A signature under this convention is valid for `ecrecover` on chain and for
any Ethereum wallet that signs the raw Keccak digest, and vice versa for a
wallet that signs the raw Keccak digest and returns `v` in {0, 1}.

The proof of possession of `06-did-sage.md` §4 is a separate algorithm: for
both Ed25519 and secp256k1 the signed message is `SHA-256(challenge)`
(32 bytes), and for secp256k1 the 32-byte digest is signed directly (no
Keccak). It is valid only as a proof of possession and MUST NOT be accepted on
any other path.

### P-256

1. `digest = SHA-256(message)`.
2. ECDSA. Go's signer is randomised; RFC 6979 is RECOMMENDED. Randomised
   signing is permitted; verification is deterministic, so P-256 vectors are
   verify-only.
3. Low-S normalisation on the signer side.
4. Signature: 64 bytes raw `r || s`. Verifiers MUST accept only the 64-byte
   raw `r || s` with `s <= n/2`; DER and high-S MUST be rejected on every
   path.

### RSA

RSA is not part of this specification. Signers MUST NOT use RSA keys.
Verifiers MUST reject a signature whose `alg` is `rsa-pss-sha256` or any RSA
algorithm, and MUST reject an RSA public key.

## 3. RFC 9421 algorithm identifiers

| Key type | `alg` |
|---|---|
| Ed25519 | `ed25519` |
| secp256k1 | `es256k` |
| P-256 | `ecdsa-p256-sha256` |

`es256k` in this specification is SAGE's name for secp256k1 over Keccak-256
with 65-byte `r || s || v`. It is not JOSE `ES256K` (SHA-256, 64 bytes) and is
not registered in the IANA HTTP Signature Algorithms registry; generic RFC 9421
or JOSE libraries will not verify it.

Source: `pkg/agent/crypto/algorithm_registry.go`. The `alg` parameter is
informative: verifiers select the algorithm from the resolved key type and
MUST reject a signature whose `alg` contradicts the key. `alg` MAY be absent.
A verifier MUST select exactly one algorithm from the resolved key's type
(Ed25519 → `ed25519`, secp256k1 → `es256k`, P-256 → `ecdsa-p256-sha256`),
MUST NOT try another, and MUST NOT infer the algorithm from the DID's chain or
any other part of the identifier.

## 4. Key identifier

`KeyID(pub) = hex(SHA-256(pub)[0:8])` over the canonical encoding of §1
(65-byte uncompressed for secp256k1 and P-256, 32 bytes for Ed25519 and
X25519) (`keys/keyid.go`). It is used for logging and diagnostics only. It
MUST NOT be used to select a key, to look up a session, or to make an
authorisation decision. The Ethereum address of a secp256k1 key is
`0x || hex(Keccak-256(X || Y)[12:32])` in lower-case hex (the form used in
`did:sage:ethereum` identifiers and by the `crypto` vector); EIP-55
checksumming is a display convention and is not applied on the wire.

## 5. Open items

None. O-1, O-2 and O-3 of 0.9.0-draft.1 are closed.

## Known residual risks

- **E01-10, `es256k` name.** The identifier `es256k` is easily confused with
  JOSE `ES256K`, which uses SHA-256 and 64-byte signatures; renaming it is
  deferred. Risk if left: low, because the digest mismatch makes
  cross-interpretation fail verification and no forgery follows.

## Changes from 0.9.0-draft.1

- E01-01 (a) Which key types a did:sage record can carry
- E01-02 (b) RSA is not part of 0.9.0
- E01-03 (a) secp256k1 public key encodings
- E01-04 (b) Ed25519 verification is strict
- E01-05 (b) secp256k1 verification accepts exactly one encoding
- E01-06 (b) P-256 verification accepts exactly one encoding
- E01-07 (a) O-1 closed: the PoP digest is a distinct, documented algorithm
- E01-08 (a) O-2 closed: P-256 signing stays randomised
- E01-09 (a) What `es256k` means
- E01-11 (b) Algorithm comes from the key, never from the DID's chain
- E01-12 (a) KeyID input for secp256k1
- E01-13 (b) KeyID is for logs only
- E01-14 (b) Public key validation
