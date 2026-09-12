# 1. Cryptographic primitives

Vectors: `vectors/crypto.json`. Go sources: `pkg/agent/crypto/keys/`
(`ed25519.go`, `secp256k1.go`, `secp256k1_keccak.go`, `p256.go`,
`ecdsa_encoding.go`, `verify.go`, `keyid.go`).

## 1. Key types

| Type | Curve | Use | Public key encoding |
|---|---|---|---|
| Ed25519 | edwards25519 | signing (default) | 32 bytes (RFC 8032) |
| secp256k1 | secp256k1 | signing, Ethereum identity | 65-byte uncompressed SEC1 (`04 || X || Y`); 33-byte compressed accepted where noted |
| P-256 | NIST P-256 | signing (optional) | 65-byte uncompressed SEC1 |
| X25519 | curve25519 | key agreement (HPKE, E2E) | 32 bytes (RFC 7748) |
| RSA | 2048+ | legacy signing (optional) | PKCS#1 / SPKI DER |

On-chain and in agent cards the registry key type is an integer:
ECDSA (secp256k1) = 0, Ed25519 = 1, X25519 = 2 (`did/types_v4.go`).

## 2. Signature algorithms

### Ed25519

Pure Ed25519 over the message bytes. No pre-hash, no context string.
Signature: 64 bytes `R || S`.

### secp256k1 (Ethereum convention)

This is the single secp256k1 convention on every SAGE path (RFC 9421, HPKE
envelope, A2A proof, CLI):

1. `digest = Keccak-256(message)` (not SHA-256; not the EIP-191 personal
   prefix).
2. ECDSA with RFC 6979 deterministic nonces.
3. `s` MUST be in the lower half of the group order (low-S).
4. Signature: 65 bytes `r || s || v`, `v` in {0, 1} (the recovery id, not 27/28).

Verifiers MUST accept 65-byte `r || s || v` and 64-byte `r || s`, and SHOULD
accept ASN.1 DER. Verifiers MUST normalise a high-S value before checking so
that signatures produced by other libraries remain verifiable
(`secp256k1_keccak.go:55-59`).

A signature under this convention is valid for `ecrecover` on chain and for
any Ethereum wallet that signs the raw Keccak digest, and vice versa.

*Exception.* The key proof of possession in `06-did-sage.md` signs
SHA-256 of its challenge string with the same secp256k1 key. That path is
kept for on-chain compatibility and is listed as open item O-1.

### P-256

1. `digest = SHA-256(message)`.
2. ECDSA. Go's signer is randomised; RFC 6979 is RECOMMENDED and will become
   REQUIRED (open item O-2). Vectors for P-256 are verify-only until then.
3. Low-S normalisation on the signer side.
4. Signature: 64 bytes raw `r || s`. The RFC 9421 verifier accepts raw only;
   the generic verifier also accepts DER.

### RSA

RSASSA-PKCS1-v1_5 with SHA-256 over the message. The RFC 9421 algorithm
identifier the Go core emits for RSA keys is `rsa-pss-sha256`, which does not
match the PKCS#1 v1.5 operation it performs. Open item O-3; RSA is not
covered by vectors and SHOULD NOT be used for new agents.

## 3. RFC 9421 algorithm identifiers

| Key type | `alg` |
|---|---|
| Ed25519 | `ed25519` |
| secp256k1 | `es256k` |
| P-256 | `ecdsa-p256-sha256` |
| RSA | `rsa-pss-sha256` (see O-3) |

Source: `pkg/agent/crypto/algorithm_registry.go`. The `alg` parameter is
informative: verifiers select the algorithm from the resolved key type and
MUST reject a signature whose `alg` contradicts the key.

## 4. Key identifier

`KeyID(pub) = hex(SHA-256(pub)[0:8])` over the raw public key bytes of
section 1 (`keys/keyid.go`). It is used for key selection and logging, not
as a security binding. The Ethereum address of a secp256k1 key is
`0x || hex(Keccak-256(X || Y)[12:32])`, EIP-55 checksummed.

## 5. Open items

| Id | Item |
|---|---|
| O-1 | Key proof of possession uses SHA-256 for secp256k1; unify with the Keccak convention or document it as a distinct algorithm |
| O-2 | Deterministic P-256 signing (RFC 6979) |
| O-3 | RSA identifier `rsa-pss-sha256` vs PKCS#1 v1.5 operation |
