# Pinned Go/Rust Agent Card schema review

Status: **CARD-01 assessed at bounded source and existing-test scope; no
complete parent-case verdict**. The [91-rule index](core-gap-index.json) has
36 reviewed and 55 pending. Normative `sage-spec` is pinned to
`44df132fee5925182018ce089dc82435cb353f8a`, Go `sage` to
`49379baadc6baec9ca8b4bb7d15bf43d65144bd7`, and Rust `rs-sage-core` to
`ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396`. No normative text, core
code or Inspector case verdict changed.

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
| Registry and proof boundary | The Go legacy proof shape includes `created`, `proofPurpose` and Base58 proof data ([source](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/did/a2a_proof.go#L39-L53)); the Rust legacy proof has the corresponding older fields ([source](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/did/a2a.rs#L36-L53)). Both card types embed public keys. | Neither older proof or embedded key list substitutes for the SAGE proof and current registry comparison. Their exact cryptographic differences belong to the subsequent `CARD-02` and `CARD-03` reviews; they are not inferred as passed here. |

At the pinned core revisions, selected Go `pkg/agent/did` A2A tests passed
and Rust `cargo test --lib did::a2a::` passed **1/1**. These confirm the older
card implementations' tested behavior, not CARD-01. The pinned Inspector
[CARD-01 evidence](https://github.com/SAGE-X-project/sage-inspector/blob/f104c8c3ce072e7a64d5a0092623e45ffb8d287b/docs/current-spec-card01-evidence.md)
uses an older normative revision, `5bcf511e604579afa63f434013447f44b6858828`.
Its source-card and independent-signature controls pass, but both primitive
adapters report all six `CARD-01` cases as `UNSUPPORTED` because neither
exposes `sage.card.verify`. Its evidence checker passed in this review; no
old case result is transferred to the current normative revision.

The next unreviewed rule is `CARD-02`. Before a CARD-01 parent-case verdict,
each core needs an explicit 0.10.0 SAGE card parser and validator, with
exact-member/duplicate/null/byte and time bounds, canonical DID, registry
service equality, and one version-matched Inspector path that observes no
discovery output or protected effect on rejection. A separate A2A transport
adapter may carry the assertion without changing its SAGE wire schema.
