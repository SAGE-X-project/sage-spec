# 6. The did:sage method

Vectors: `vectors/did.json`. Go sources: `pkg/agent/did/` (`manager.go`,
`did.go`, `utils.go`, `types.go`, `types_v4.go`, `key_proof.go`).

## 1. Grammar

```
did-sage   = "did:sage:" chain ":" identifier
chain      = "ethereum" / "solana"          ; after normalisation, see §2
identifier = 1*( unreserved / ":" )         ; everything after the third colon
```

- The identifier MAY contain further colons; parsers split at the first
  three colons only and keep the remainder verbatim
  (`did:sage:ethereum:0x…:42` has identifier `0x…:42`).
- The whole string MUST be at least 10 characters and start with `did:`.
- An empty identifier, a missing chain, an unknown chain or a different
  method are rejected. The `rejected` list in the vector is normative.
- Ethereum identifiers are the lower-case `0x` address; a nonce suffix
  (`:<n>`) distinguishes several agents under one address.

## 2. Chains

`ParseChain` trims whitespace and lower-cases, then accepts:

| Input | Chain |
|---|---|
| `ethereum`, `eth` | `ethereum` |
| `solana`, `sol` | `solana` |

Networks within a chain (`ethereum-mainnet`, `sepolia`, `goerli`,
`solana-mainnet`, `solana-devnet`, `solana-testnet`) are configuration, not
part of the DID.

## 3. Resolution

Resolution returns agent metadata, not a W3C DID Document (open item O-8).
The registry record (`AgentMetadataV4`) carries:

| Member | Content |
|---|---|
| `did` | the DID |
| `name`, `description`, `endpoint` | strings |
| `keys[]` | `{type, key_data, signature, verified, created_at}`; `type` 0 = ECDSA/secp256k1, 1 = Ed25519, 2 = X25519; `key_data` raw public key bytes of `01-crypto.md` §1 |
| `capabilities` | free-form object |
| `owner` | chain address |
| `is_active` | boolean; inactive agents MUST NOT be trusted |
| `public_kem_key` | 32-byte X25519 key used as the HPKE KEM key |
| `created_at`, `updated_at` | timestamps |

## 4. Key proof of possession

Each registered signing key carries a signature proving control of the
private key at registration time:

```
challenge = "SAGE-PoP:" || DID || ":" || hex(key_data)
digest    = SHA-256(challenge)
Ed25519:    signature = Ed25519.Sign(priv, digest)          (64 bytes)
secp256k1:  signature = ECDSA-RFC6979(priv, digest) as r||s||v (65 bytes)
X25519:     no proof (key agreement only)
```

Verifiers recompute the challenge from the DID and `key_data` and verify
`signature`; a key whose proof fails MUST NOT be marked `verified`. Note
that both signature types hash the challenge with SHA-256, and that the
secp256k1 case therefore differs from the Keccak convention used everywhere
else (`01-crypto.md` O-1).

## 5. Open items

| Id | Item |
|---|---|
| O-8 | A DID Document projection of the registry record (verification methods, key agreement, service endpoints) |
