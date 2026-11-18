# 6. The did:sage method

Version: 0.9.0-draft.1.1. Finalizes 0.9.0-draft.1 with the errata in [../docs/errata-0.9.0-draft.1.md](../docs/errata-0.9.0-draft.1.md).

Vectors: `vectors/did.json`. Go sources: `pkg/agent/did/` (`manager.go`,
`did.go`, `utils.go`, `types.go`, `types_v4.go`, `key_proof.go`).

## 1. Grammar

```
did-sage   = "did:sage:" chain ":" identifier
chain      = "ethereum" / "solana"          ; after normalisation, see §2
identifier = segment *( ":" segment )       ; everything after the third colon
segment    = 1*( ALPHA / DIGIT / "-" / "." / "_" / "~" )
```

- The identifier MAY contain further colons; parsers split at the first
  three colons only and keep the remainder verbatim
  (`did:sage:ethereum:0x…:42` has identifier `0x…:42`).
- A parser MUST reject a DID containing any other character, including
  `%`, `#`, `?`, `/`, `|`, space, control characters and non-ASCII, and an
  empty segment. A DID URL (`DID#fragment`) is not a DID; a parser that is
  given one MUST reject it.
- A DID MUST NOT exceed 256 bytes; a `keyid` (DID plus fragment) MUST NOT
  exceed 289 bytes.
- An empty identifier, a missing chain, an unknown chain or a different
  method are rejected. The `rejected` list in the vector is normative.
- A parser accepts any `identifier` the grammar allows. By convention an
  `ethereum` identifier is the registrant's lower-case `0x` address,
  optionally followed by `:<n>`; neither the parser nor the registry
  enforces it, and a verifier MUST NOT infer the owner address from the
  identifier.

## 2. Chains

`ParseChain` trims whitespace and lower-cases, then accepts:

| Input | Chain |
|---|---|
| `ethereum`, `eth` | `ethereum` |
| `solana`, `sol` | `solana` |

The canonical form of a DID is `did:sage:` followed by `ethereum` or
`solana` (after `ParseChain`), `:`, and the identifier unchanged. Every
comparison of DIDs (`ExpectedDID`, `X-SAGE-DID` against `keyid`, `initDid`
against the envelope `did`, `respDid` against the responder's DID, the card
`id` against the resolved record, authorisation lists, replay scopes) MUST
be made between canonical forms. Signers SHOULD emit the canonical form.
Byte strings that embed a DID (HPKE `info`, `th`, the PoP challenge) use the
DID exactly as sent.

Networks within a chain (`ethereum-mainnet`, `sepolia`, `goerli`,
`solana-mainnet`, `solana-devnet`, `solana-testnet`) are configuration, not
part of the DID.

A verifier MUST be configured with exactly one network and one registry
address per chain, MUST resolve every DID of that chain only there, and
MUST NOT fall back to another network or registry when resolution fails.

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
| `public_kem_key` | 32-byte X25519 key; it is the HPKE KEM key only under §3.1 |
| `created_at`, `updated_at` | timestamps |

- `keys[]` lists the agent's current keys in registry order. Revoking a key
  removes it from this list (the registry keeps the key's own entry for
  audit, outside the list).
- `signature` of a type-0 or type-1 entry is the proof of possession of §4.
  A type-2 entry has no proof (§4).
- `verified` is a flag kept by the registry. A verifier MUST NOT use it to
  decide whether a key may be used: key eligibility is defined in §3.1 from
  the listing and the §4 proof alone.
- Implementations may expose a selected-key view (`public_key`); it is
  derived by §3.1 and is not a registry member.

0.9.0-draft.1.1 specifies resolution only for `ethereum` (the
AgentCardRegistry). `solana` DIDs parse, but their resolution is not
specified and is not covered by conformance.

A verifier MUST reject, or ignore when advisory, a resolved record with
`name` over 256 bytes, `description` over 4 KiB, `endpoint` over 2 KiB,
more than 32 `keys`, or `capabilities` over 16 KiB as JSON. `endpoint`
SHOULD be an `https` URL.

A verifier MUST NOT rely on a resolved positive result (agent active, key
listed) older than 300 seconds (RECOMMENDED 60). It MAY cache negative
results (inactive, revoked, unknown) without limit. If the registry cannot
be read, verification fails; a verifier MUST NOT fall back to an older
positive result.

### 3.1 Key eligibility and selection

- **Eligible key**: a type-0 or type-1 entry is eligible when it is listed
  in `keys[]` and its `signature` is a valid §4 proof for the record's
  `did` and that `key_data`. A type-2 entry is eligible when it is listed.
  The registry's `verified` flag is not consulted.
- **Signing key**: the first eligible type-0 entry in registry order; if
  none, the first eligible type-1 entry. An entry whose proof does not
  verify is not eligible and is skipped. If the selected entry's
  `key_data` does not decode, resolution fails; it does not fall back to
  another key.
- **KEM key**: the dedicated KEM field when it is non-empty and equals the
  `key_data` of an eligible type-2 entry; otherwise, only when the
  dedicated field is empty, the first eligible type-2 entry. A non-empty
  dedicated field that is not listed leaves the record without a KEM key
  (`04-hpke.md`, errata E04-02).
- An inactive agent (`is_active` false) has no usable keys.

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

`hex` is lower-case; `key_data` is used exactly as stored (errata E01-03);
`DID` is the record's `did` member exactly as stored; the signature is 64
bytes for Ed25519 and 65 bytes `r || s || v` (low-S, `v` checked, errata
E01-05) for secp256k1, both over the 32-byte `SHA-256(challenge)`
(`01-crypto.md`, errata E01-07). The registry stores this proof as
`signature` and every verifier checks it (next paragraph).

`keys[].signature` of a type-0 or type-1 key MUST be the §4 proof, with the
challenge unchanged and the DID taken from the record's `did` member exactly
as stored. A registry MUST verify the proof before listing the key and MUST
refuse a key whose proof does not verify. A verifier MUST verify the proof
itself before using the key, independently of the registry, and MUST NOT
rely on the registry's `verified` flag (§3, §3.1).

Note that both signature types hash the challenge with SHA-256, and that the
secp256k1 case therefore differs from the Keccak convention used everywhere
else.

## 5. Open items

O-8 (DID Document projection) is deferred to 0.10.0; 0.9.0-draft.1.1
resolution returns the record of §3 only.

## Known residual risks

- **E06-05**: A DID has more than one accepted spelling, because
  `ParseChain` accepts the aliases `eth` and `sol` and any case variant of
  the chain (§2); §2 requires canonical comparison inside the protocol, but
  stores outside it that key on the raw string are not covered. Risk if
  left: medium.
- **E06-06**: The network is not part of the DID, so the same DID can name
  different agents on different networks of one chain; §2 requires one
  configured network per chain as an interim mitigation. Risk if left:
  medium to high where several networks are in use.

## Changes from 0.9.0-draft.1

- E06-01 (a) The address form is a convention, not a parse rule
- E06-02 (b) Identifier characters are enforced
- E06-03 (b, b-limit) Length
- E06-04 (b) Comparisons use the canonical form
- E06-07 (b) One network per chain, no fallback
- E06-08 (a) What the record really says, and what a verifier reads from it
- E06-09 (c) Key possession is not proven or verifiable
- E06-10 (a) The proof is defined as an off-chain check
- E06-11 (a) Key eligibility and selection
- E06-12 (b) Freshness of resolution, fail closed
- E06-13 (a) Solana resolution is not specified
- E06-14 (b, b-limit) Record member limits
- E06-15 (a) O-8 deferred
