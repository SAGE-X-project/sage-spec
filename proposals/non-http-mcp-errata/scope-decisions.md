# Scope decisions for the next SAGE specification revision

Status: design decisions and explicit open work, **not** an adopted profile.
This register uses the [preserved design review](../../verification/preserved-design-review.md)
and the [post-adoption errata review](../../verification/post-adoption-errata-review.md).
It keeps message integrity, delegated authority, semantic safety and service
availability as distinct claims. The current adopted rules and Inspector
verdict remain unchanged until a single new normative snapshot is pinned.

| Input | Decision for the next revision | Boundary retained |
| --- | --- | --- |
| ADOPT-02/03 | Carry the [single-flight and local binding candidate](candidate.md) into normative review with explicit case changes. | No in-band negotiation, parallel protected exchange on one owner, or raw-file hash as a peer-config digest. |
| DSR-S01 | Retain the prohibition on `Content-Encoding` in both directions. Add integration guidance that clients request `Accept-Encoding: identity` and disable automatic compression/decompression at the protected byte boundary. | An unmodified stock HTTP library is not evidence of SAGE profile conformance. No new signed component is introduced merely for guidance. |
| DSR-S02 | Retain exactly one `sig1` signature in 0.10.0. [RFC 9421](https://www.rfc-editor.org/rfc/rfc9421.html) permits more, but this profile deliberately selects a subset. | Multiple-signature support requires a separate review of signature selection, request-bound response coverage and confusion handling. |
| DSR-S03 | Retain SAGE's exact canonical *produced* DID-document JWK form and strict validation of authoritative projection. Clarify that R-14 is an outbound document-consumption goal to be demonstrated with an independent DID consumer, not a promise to accept arbitrary JWK documents as authority. | Private keys, contradictory key metadata and untrusted resolver fields cannot become authorized through [RFC 7517](https://www.rfc-editor.org/rfc/rfc7517.html)'s optional-member rule. |
| DSR-S04 | Keep existing signed `X-SAGE-*` names for 0.10.0 and record the [BCP 178](https://www.rfc-editor.org/rfc/rfc6648.html) naming exception. | Renaming signed fields needs a new wire version, migration and vectors; no silent alias. |
| DSR-S05..S07 | Keep the private algorithm-name decision. Add missing informative references and require Go/Rust agreement on the strict Ed25519 profile before a compatibility claim. | A library accepting a wider set of encodings is not itself the protocol acceptance rule. |
| DSR-S08 | Keep `JsonWebKey2020` only if chapter 10 cites its [DID extension definition](https://www.w3.org/TR/did-extensions-properties/) and states that [Controlled Identifiers 1.0](https://www.w3.org/TR/controller-document/) defines `JsonWebKey` instead. Correct the standards table and narrow any untested general interoperability claim. | A change to `JsonWebKey` would change document bytes and requires a separate versioned decision; no automatic type alias. |
| DSR-D01 | **Pending user scope decision:** either each hop has a new trusted capture/authorization, or the protocol defines transitive delegation. | Agent-to-Agent message protection alone proves neither delegation nor original-user intent at later hops. |
| DSR-D02 | Keep policy content under trusted deployment control; explicitly deny on missing/error policy verdict. Do not claim that protocol conformance proves a policy is semantically safe or sufficiently restrictive. | An explicit permissive deployment policy can authorize broad actions; cryptographic integrity does not make it safe. |
| DSR-D03 | Defer a signed argument-provenance field until a trusted Client can define and test how provenance is captured through the model/tool loop. | An unverified provenance label would be another attacker-controlled claim, not a defense. |
| DSR-D04/05 | Record per-capture call budgets and pre-authentication registry-work limits as separate availability-profile work. Keep fresh authoritative positive observations and fail-closed outage behavior. | No positive-cache grace, identity-existence oracle or claim of volumetric denial-of-service resistance is introduced. |
| DSR-D06 | Require migration notes for changed DID grammar and unsupported Solana paths before release. | Do not interpret old identifiers as new canonical identities. |
| DSR-D07 | Retain historical 77-rule/386-case evidence in its dated report; the current adopted map has 91 rule groups, 457 parents and 26 mandatory children. | The later Inspector overlay does not retroactively execute historical plans or establish full conformance. |

The next normative snapshot must decide its exact compatibility version and
update the affected profile/chapter text, charter, traceability, expected cases,
changelog and verification controls together. In particular, the ADOPT-02/03
candidate changes local acceptance behavior even though it adds no wire field.
Spec and implementation revisions must be pinned separately; the historical
adoption record is not rewritten to pretend the new rules were present earlier.

The implementation layering from the preserved branch is guidance for the later
Go/Rust refactor: canonical bytes and digests belong in a pure layer; cryptographic
validity does not equal Guard authorization; a trusted owner enforces the
single-flight slot; deployment assemblies fail construction when required
configuration is absent. SDK wrappers, MCP adapters and model-visible tools
cannot manufacture readiness or bypass that owner. These are observable
requirements for the eventual integration tests, not package-name mandates.
