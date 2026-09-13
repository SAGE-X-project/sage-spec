# 11. Registries

The tables this specification maintains, and how an entry is added. A
registry exists so that a new algorithm, label, header, profile or
diagnostic code can be introduced without editing the chapters that use it
(`00-overview.md` §5).

## 1. Registration procedure

1. A proposal is an issue in this repository naming the registry, the value
   requested, the chapter that will use it, and the requirement from
   `charter.md` it serves.
2. An entry is added by a pull request that changes this chapter, the
   chapter that defines the behaviour, and at least one vector.
3. Values are assigned in the order accepted. A value is never reused, and
   an entry is never changed in meaning; a superseded entry is marked
   obsolete and stays in the table.
4. Adding an entry is a MINOR change. Changing or removing one is MAJOR.
5. Ranges reserved for private use are marked in each table; values outside
   them are assigned only by the procedure above.

## 2. Signature algorithms

Names as they appear in the `alg` parameter of a message signature
(`03-rfc9421.md`) and in a verification method (`10-resolution.md`).

| Name | Key type | Digest | Signature encoding | Chapter | Status |
|---|---|---|---|---|---|
| `ed25519` | Ed25519 | none (pure) | 64 bytes, RFC 8032 | `01-crypto.md` | current |
| `es256k` | secp256k1 | Keccak-256 | 65 bytes, `r ‖ s ‖ v`, low-S | `01-crypto.md` | current |
| `ecdsa-p256-sha256` | P-256 | SHA-256 | 64 bytes, `r ‖ s`, low-S | `01-crypto.md` | current |

Names beginning `x-` are for private use and MUST NOT appear in a record or
a message that leaves a deployment.

## 3. Key types and encodings

How a public key appears in a registry record and in a resolved document.

| Key type | Use | Wire encoding in a record | Document encoding |
|---|---|---|---|
| Ed25519 | signing | 32 bytes | JSON Web Key, `OKP`, curve `Ed25519` |
| secp256k1 | signing | 65 bytes, uncompressed, `0x04` prefix | JSON Web Key, `EC`, curve `secp256k1` |
| P-256 | signing | 65 bytes, uncompressed, `0x04` prefix | JSON Web Key, `EC`, curve `P-256` |
| X25519 | key agreement | 32 bytes | JSON Web Key, `OKP`, curve `X25519` |

A registry profile MAY accept a subset of these types and MUST reject a key
whose type it cannot verify (`09-registry.md` §4).

## 4. Domain separation labels

Every label is versioned; a new version is a MAJOR change of this
specification (`00-overview.md` §5).

| Label | Used for | Chapter |
|---|---|---|
| `sage/hpke-info|v1` | HPKE `info` | `04-hpke.md` |
| `sage/hpke-export|v1` | HPKE export context | `04-hpke.md` |
| `SAGE-HPKE+E2E-Combiner` | combining the exporter and the ephemeral secret | `04-hpke.md` |
| `SAGE-c2s:key`, `SAGE-c2s:iv`, `SAGE-s2c:key`, `SAGE-s2c:iv`, `SAGE-cb-v1` | counter expansion outputs | `04-hpke.md` |
| `sage/hpke+e2e v1` | session seed and identifier derivation after a handshake | `05-session.md` |
| `sage-session-keys-v1` | session key schedule | `05-session.md` |
| `sage-directional-keys-v1` | per-direction keys | `05-session.md` |
| `sage-session-rekey-v1` | key rotation within a session | `05-session.md` |
| `sage-pop-v1` | proof of possession of a key | `09-registry.md` |

## 5. Registry kinds

The first component of an identifier's locator (`06-did-sage.md` §1) names
the kind of registry that holds the record. A kind is added by the
procedure of §1 together with its profile.

| Kind | Locator syntax | Profile |
|---|---|---|
| `eip155` | CAIP-2 chain reference, then the registry contract address | `09-registry.md` §6 |
| `solana` | CAIP-2 chain reference, then the program address | `09-registry.md` §7 |
| `web` | a domain name serving the registry document | `09-registry.md` §8 |

## 6. Transport headers

| Header | Direction | Meaning | Chapter |
|---|---|---|---|
| `X-SAGE-DID` | request and response | the sender's identifier; MUST agree with the `keyid` of the signature | `08-transport.md`, `03-rfc9421.md` |
| `Signature-Input`, `Signature` | request and response | RFC 9421 fields | `03-rfc9421.md` |
| `Content-Digest` | where a body exists | RFC 9530 field | `03-rfc9421.md` |

Headers beginning `X-SAGE-X-` are for private use.

## 7. Diagnostic codes

These codes are for logs, conformance reports and resolution errors. A
verifier MUST NOT tell a sender which check failed (`charter.md` R-35); it
returns a single authentication failure and records the code locally.

| Code | Meaning |
|---|---|
| `sig.missing` | no signature field present |
| `sig.malformed` | a signature field could not be parsed |
| `sig.unknown-label` | the requested label is absent |
| `sig.base-mismatch` | the signature base could not be reconstructed |
| `sig.bad` | the signature did not verify |
| `sig.alg-mismatch` | the algorithm does not match the resolved key |
| `sig.stale` | outside the freshness window |
| `sig.replay` | the nonce or sequence has been seen |
| `sig.coverage` | a required component is not covered |
| `sig.binding` | a response is not bound to its request |
| `digest.missing`, `digest.mismatch` | body digest absent or wrong |
| `size.exceeded` | a field or body exceeds its maximum |
| `id.malformed` | the identifier does not parse |
| `id.unknown-kind` | the registry kind is not implemented |
| `record.not-found` | the registry has no record for the identifier |
| `record.inactive` | the record is not active |
| `record.unreachable` | the registry could not be read |
| `key.not-in-record` | the key identifier names no key in the record |
| `key.unproven` | the record does not carry an accepted proof for the key |
| `key.revoked` | the key is revoked |
| `pop.bad` | a proof of possession did not verify |
| `session.unknown`, `session.replay`, `session.window`, `session.aead` | session record failures |

Resolution errors are reported as problem details (RFC 9457) whose type is
the code above, as `10-resolution.md` §5 defines.
