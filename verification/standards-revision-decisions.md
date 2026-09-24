# Standards and integration decisions for the next specification revision

Status: reviewed decisions reflected in the coordinated, unreleased 0.10.0
normative design; this file remains an informative rationale. Reviewed against `sage-spec` revision
`82466f488dcdd17f6ec8b6723d394eaf1fb67b5d` and the
[preserved branch review](preserved-design-review.md). The existing
[MCP errata adoption](mcp-errata-adoption.json) remains a preserved historical
snapshot. The [current revision record](spec-revision-adoption.json) pins the
coordinated chapter, charter, traceability and compatibility update.

| Finding | Decision for the coordinated revision | Verification boundary |
| --- | --- | --- |
| DSR-S01, HTTP content coding | Keep MSG-01's omission/rejection of `Content-Encoding` in both directions. HTTP client assemblies request `Accept-Encoding: identity`, disable automatic request compression and response decompression at the protected byte boundary, and compare the received content bytes before parsing. This is integration guidance, not a new signed component or a change to the accepted wire profile. | A conforming SAGE responder omits content coding regardless of what the request advertises. A stock library's transformed body is not evidence that the signed bytes were verified. |
| DSR-S02, multiple signatures | Keep exactly one `sig1` member in each signature dictionary. [RFC 9421 §4.3](https://www.rfc-editor.org/rfc/rfc9421.html#section-4.3) permits multiple labels; SAGE deliberately selects a smaller profile. Do not ignore an extra label or select one by order. | Test an extra label and mismatched dictionaries as rejection. Later multi-signature support needs new selection, request-bound response and confusion rules. |
| DSR-S03, JWK members | Keep the exact canonical JWK **produced** from an authoritative SAGE record and reject unapproved extra or contradictory members as a SAGE authority input. Narrow R-14's general software claim to an output-consumption interoperability goal, demonstrated with an independent DID consumer. [RFC 7517 §4](https://www.rfc-editor.org/rfc/rfc7517.html#section-4) tells generic JWK consumers to ignore unknown extra members; it does not require SAGE to treat an arbitrary third-party document as authoritative registry state. | Independent consumer acceptance of the produced document and SAGE rejection of private/contradictory/extra authority input are separate tests. No private key is projected. |
| DSR-S04, `X-SAGE-*` | Keep the existing signed field names for 0.10.0. Record this as a naming exception to [BCP 178 §3](https://www.rfc-editor.org/rfc/rfc6648.html#section-3), which recommends against new `X-` names but does not invalidate deployed names. | No unsigned alias or automatic fallback. A rename changes covered components and needs a separately versioned migration and vectors. |
| DSR-S05–S07, algorithms | Retain SAGE's private secp256k1/Keccak name and the strict Ed25519 acceptance profile in chapter 01. Add informative reference coverage where absent; do not infer that a general-purpose library's broader acceptance is conformant. | Independent Go/Rust positive and negative byte/verdict cases must agree before a compatibility claim. This decision does not add an algorithm or silently loosen decoding. |
| DSR-S08, verification-method vocabulary | Keep `JsonWebKey2020` for the produced 0.10.0 document, cite its [DID property extension](https://www.w3.org/TR/did-extensions-properties/#jsonwebkey2020), and state that [Controlled Identifiers 1.0](https://www.w3.org/TR/cid/) uses `JsonWebKey`. | Do not silently alias the two types. Changing emitted type changes document bytes and needs versioned vectors and consumer tests. |

The HTTP choices follow [RFC 9110 §12.5.3](https://www.rfc-editor.org/rfc/rfc9110.html#section-12.5.3):
`identity` expresses no content coding, while a request without `Accept-Encoding`
can accept any coding. The requested preference does not override MSG-01's
mandatory sender/receiver rules. A response with `Content-Encoding` is rejected,
even if a library could transparently decode it.

## Trust and availability decisions

| Finding | Decision | Limit |
| --- | --- | --- |
| DSR-D01, multihop authority | At every trusted Client hop, capture incoming authenticated input and independently authorize the exact outgoing request under that Client's authority. B→C therefore needs B's own capture and policy decision; no transitive delegation credential is defined in 0.10.0. | Agent-to-Agent authentication, parent/call IDs and upstream digests record identity or causality but do not grant downstream authority. No mandatory human popup is implied. Missing B authorization denies. |
| DSR-D02, policy | Keep policy and evaluator under trusted deployment control. Missing, errored, retired or mismatched verdicts deny. A configured permissive policy may explicitly allow broad operations; conformance does not prove policy semantics are safe. | Signature and policy-digest validity alone do not establish a restrictive policy. |
| DSR-D03, argument provenance | Defer a signed provenance field until the trusted Client can capture and validate its origin through the model/tool loop. | A label derived from untrusted text or code is not origin evidence. |
| DSR-D04–D05, availability | Specify per-capture work budgets and pre-authentication registry-work limits in a separate availability profile, with bounded resource tests. Keep authoritative positive observations and fail-closed resolver outages. | No positive-cache grace, identity-existence oracle or volumetric denial-of-service guarantee is introduced in this revision. |
| DSR-D06, DID migration | The migration plan records old/new grammar, unsupported Solana paths, explicit re-enrollment eligibility and rejection of ambiguous aliases. | Old identifiers are never guessed into new canonical identities. |
| DSR-D07, evidence counts | Preserve the 77-group/386-case original baseline, 91-group/457-case first MCP adoption and 91-group/466-case MCP errata amendment as dated evidence. The coordinated revision has 91 groups, 471 planned parents and 26 mandatory children. | Existing 71-parent Inspector PASS evidence remains pinned to the earlier revision and does not execute the five new cases. |

## Implementation boundaries after the normative revision

The preserved architecture's L0–L3 separation is a responsibility model, not
four new protocol conformance levels. L0 computes canonical bytes and digests;
L1 verifies signatures, sessions and authenticated records; L2 evaluates trusted
identity, policy, execution admission and one-owner exchange ordering; L3 binds
the actual Agent, SDK, MCP and host effect paths to those controls. `VerifiedMessage`
and `AuthorizedCall` types can reduce accidental misuse only when their constructors
and effect path remain under the trusted owner. A model-selected check or a
self-reported level is not complete mediation. Go and Rust may use different
packages and locks while producing the same externally observable verdicts.

The coordinated normative change updates the affected chapters, charter, guide,
traceability and compatibility account while retaining the unreleased 0.10.0
version. Earlier hash-pinned snapshots and Inspector results remain historical.
Go/Rust implementation changes and a new Inspector run follow this fixed snapshot;
neither may inherit coverage of the revised clauses. External review and full
conformance remain open.
