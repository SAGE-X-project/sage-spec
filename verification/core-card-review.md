# Pinned Go/Rust Agent Card review

Status: **CARD-01 through CARD-03 assessed at bounded source and existing-test
scope; no complete parent-case verdict**. The [91-rule index](core-gap-index.json)
has 73 reviewed and 18 pending. Normative `sage-spec` is pinned to
`44df132fee5925182018ce089dc82435cb353f8a`, Go `sage` to
`49379baadc6baec9ca8b4bb7d15bf43d65144bd7`, and Rust `rs-sage-core` to
`ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396`. No normative text, core
code or Inspector case verdict changed.

## CARD-01: closed SAGE card

[CARD-01](../spec/07-a2a.md) specifies a separate SAGE 0.10.0 discovery
assertion, not an external A2A Agent Card schema. Its closed JSON object
requires `version`, canonical DID `id`, `recordVersion`, `name`, registry
`services`, `issued`, `expires` and one SAGE `proof`; only `description` and
`capabilities` are optional. The entire input is at most 65,536 UTF-8 bytes,
and unknown, duplicate or null members fail. The 300-second lifetime and
capability bounds apply before discovery data is exposed. The card cannot
serve as an alternative key source or authorization grant.

| Boundary | Pinned source observation | Finding |
| --- | --- | --- |
| Go card shape and parsing | The existing [`A2AAgentCard`](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/did/types_v4.go#L90-L103) has JSON-LD `@context`, `type`, `publicKey`, `service`, `created` and `updated`, with no 0.10.0 version, record version or integer issue/expiry pair. [`ParseA2AAgentCardWithProof`](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/did/a2a_proof.go#L62-L71) uses ordinary JSON unmarshal without the SAGE input cap or a closed-member check. [`ValidateA2ACard`](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/did/a2a.go#L152-L200) requires an embedded public key and endpoint, which are not CARD-01's field model. | **SOURCE GAP FOR SAGE CARD SCHEMA**. Passing legacy A2A validation cannot imply acceptance of a valid SAGE card or rejection of its unknown, duplicate, null, oversize or stale variants. |
| Rust card shape and parsing | The existing [`A2AAgentCard`](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/did/a2a.rs#L55-L86) has the same older JSON-LD/key-list/timestamp shape. [`from_json`](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/did/a2a.rs#L169-L176) deserializes it without a SAGE size or closed-member bound; [`validate`](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/did/a2a.rs#L220-L258) checks only selected key and proof relationships. | **SOURCE GAP FOR SAGE CARD SCHEMA**. The Rust struct and parser do not implement CARD-01's required fields, timing, or exact service projection. |
| Registry and proof boundary | The Go legacy proof shape includes `created`, `proofPurpose` and Base58 proof data ([source](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/did/a2a_proof.go#L39-L53)); the Rust legacy proof has the corresponding older fields ([source](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/did/a2a.rs#L36-L53)). Both card types embed public keys. | Neither older proof or embedded key list substitutes for the SAGE proof and current registry comparison. The cryptographic differences are assessed under `CARD-02` below; current-registry discovery remains for `CARD-03`. |

At the pinned core revisions, selected Go `pkg/agent/did` A2A tests passed
and Rust `cargo test --lib did::a2a::` passed **1/1**. These confirm the older
card implementations' tested behavior, not CARD-01. The pinned Inspector
[CARD-01 evidence](https://github.com/SAGE-X-project/sage-inspector/blob/f104c8c3ce072e7a64d5a0092623e45ffb8d287b/docs/current-spec-card01-evidence.md)
uses an older normative revision, `5bcf511e604579afa63f434013447f44b6858828`.
Its source-card and independent-signature controls pass, but both primitive
adapters report all six `CARD-01` cases as `UNSUPPORTED` because neither
exposes `sage.card.verify`. Its evidence checker passed in this review; no
old case result is transferred to the current normative revision.

Before a CARD-01 parent-case verdict,
each core needs an explicit 0.10.0 SAGE card parser and validator, with
exact-member/duplicate/null/byte and time bounds, canonical DID, registry
service equality, and one version-matched Inspector path that observes no
discovery output or protected effect on rejection. A separate A2A transport
adapter may carry the assertion without changing its SAGE wire schema.

## CARD-02: signed proof bytes and key binding

[CARD-02](../spec/07-a2a.md) requires exactly `type`, `verificationMethod`,
`alg` and `proofValue` in the proof. The type is
`SageAgentCardSignature0_10_0`; the method is a full key URL belonging to the
card's DID; the signature is canonical unpadded base64url. Only
`proof.proofValue` is omitted from the signed copy. The input to the signing
algorithm is `ASCII("sage-card-0.10.0") || 0x00 || JCS(copy)`, so proof type,
algorithm, key reference and timestamps remain authenticated.

| Boundary | Pinned source observation | Finding |
| --- | --- | --- |
| Go legacy proof | [`A2AProof`](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/did/a2a_proof.go#L39-L53) has no `alg`, has `created`/`proofPurpose`, and uses Base58. The [signer](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/did/a2a_proof.go#L126-L176) signs canonical card bytes before adding the entire proof; the [verifier](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/did/a2a_proof.go#L295-L349) removes the entire proof and has no SAGE domain prefix. Its [DID-assisted path](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/did/a2a_proof.go#L218-L262) compares key bytes from the card with verified resolver metadata, but does not implement a 0.10.0 key URL/profile. | **SOURCE GAP FOR SAGE CARD PROOF**. The old signature leaves proof metadata outside its signed bytes. The older DID-assisted check is a distinct trust boundary; it does not repair the missing SAGE proof shape, domain or exact named-key binding. |
| Rust legacy proof | [`A2AProof`](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/did/a2a.rs#L36-L53) likewise uses older type, time and Base58 fields with no `alg`. [`canonical_bytes`](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/did/a2a.rs#L179-L189) removes the whole proof; [`sign`](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/did/a2a.rs#L191-L217) and [`verify_proof`](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/did/a2a.rs#L261-L295) operate on that unprefixed card and its embedded public key. | **SOURCE GAP FOR SAGE CARD PROOF**. A valid legacy proof is not a CARD-02 proof; no registry-selected key or exact 0.10.0 signature domain is shown in this path. |

Selected Go A2A proof tests and Rust's A2A signing/verification test passed
at the pinned revisions. The pinned Inspector
[CARD-02 evidence](https://github.com/SAGE-X-project/sage-inspector/blob/f104c8c3ce072e7a64d5a0092623e45ffb8d287b/docs/current-spec-card02-evidence.md)
uses the older normative revision `5bcf511e604579afa63f434013447f44b6858828`.
Its five independent fixtures and generic Ed25519 controls demonstrate that
signature verification alone does not check proof type or method. Both core
adapters report all five complete CARD-02 cases as `UNSUPPORTED`; the
malformed base64url input was checked only at fixture level. The evidence
checker passed, but no old verdict is transferred to the current normative
revision. Neither the legacy tests nor generic signature controls prove a
complete CARD-02 case.

Before a CARD-02 parent-case verdict, the cores and Inspector need
version-matched SAGE proof signing and verification over the
exact copy with only `proofValue` removed, exact type/algorithm/URL checks,
canonical signature encoding, registry-selected key binding, and bounded
positive and rejection cases with no discovery output on failure.

## CARD-03: current-registry verification before discovery

[CARD-03](../spec/07-a2a.md) requires size, schema and time checks before
resolution or signature work, then exact expected-peer binding, a fresh
authoritative registry observation, active record and selected signing key,
equal `recordVersion` and complete `services`, and proof verification before
exposing card data. A stale but still correctly signed card is rejected;
failure cannot authorize unsigned discovery or a protected effect.

| Boundary | Pinned source observation | Finding |
| --- | --- | --- |
| Go legacy DID-assisted card path | [`ValidateA2ACardWithProofAndDID`](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/did/a2a_proof.go#L379-L394) combines older field checks, DID-assisted proof verification and endpoint comparison. The [proof step](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/did/a2a_proof.go#L218-L262) uses the legacy DID parser, a string-prefix method check, a resolver read, active status and matching key bytes; the [endpoint step](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/did/a2a.go#L271-L331) performs another resolver read and compares only the first endpoint. | **PARTIAL LEGACY CHECKS; SAGE SOURCE GAP**. There is no SAGE card version, `recordVersion` or issued/expiry check, exact complete service-array comparison, trusted fresh observation contract, or single consistent selected-key/record snapshot in this card path. These two resolver reads cannot be assumed to describe the same record version. The older positive tests are not CARD-03 evidence. |
| Rust legacy card path | [`validate`](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/did/a2a.rs#L220-L258) checks selected relationships within the older card; [`verify_proof`](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/did/a2a.rs#L261-L295) selects its embedded key. The separate [registry gate](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/registry010/mod.rs#L265-L347) can check a trusted snapshot, but this card API does not call it. | **SAGE SOURCE GAP**. No CARD-03 integration with the registry gate, exact named key, record version, services, expected peer, trusted time or discovery-output boundary is shown. The in-memory DID resolver is a test store, not an authoritative source. |

At the pinned core revisions, selected Go DID-assisted A2A tests and Go
`registry010` tests passed; Rust's A2A card test passed **1/1** and registry
gate tests passed **3/3**. These are component tests, not one composed card
receive decision. The pinned Inspector
[CARD-03 evidence](https://github.com/SAGE-X-project/sage-inspector/blob/f104c8c3ce072e7a64d5a0092623e45ffb8d287b/docs/current-spec-card03-evidence.md)
uses the older normative revision `5bcf511e604579afa63f434013447f44b6858828`.
Its five fixtures isolate expiry, changed record version, inactive state and
changed service, but both core adapters return `UNSUPPORTED` for all five
complete cases. That run does not perform authoritative resolution or
card-to-record acceptance. Its evidence checker passed here; no old verdict
is transferred to the current normative revision.

The next unreviewed rule is `PROC-01`. A complete CARD-03 verdict needs
one version-matched receive path that binds the exact peer and proof key to
the same fresh authoritative record snapshot, checks whole services and
version before releasing discovery data, and observes zero protected effects
on each rejected case. Runtime evidence must distinguish unavailable,
inactive, stale and changed registry results from signature-only failures.
