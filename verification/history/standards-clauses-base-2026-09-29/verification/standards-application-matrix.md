# Standards application matrix for SAGE 0.10.0

Status: informative, document-level applicability review as of 2026-09-26.
Reviewed against `sage-spec` base revision
`bdbe5598c2cf63dada68c6939cfdeb28073cf71f` and the official publications
linked below. This matrix does not certify an implementation, an IETF or W3C
endorsement, or the security of SAGE's composition. The owning SAGE chapters
remain normative. A later edition or erratum does not silently change 0.10.0.

`DESIGNED` means the cited SAGE rule defines how a construction is used; it
does not mean that Go, Rust, Inspector or a third-party consumer has passed a
version-matched test. `REFERENCE` means the source informs a local decision
without a general conformance claim.

| Source and edition | SAGE owner and adopted part | SAGE restriction or independent rule | Evidence still required |
| --- | --- | --- | --- |
| [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119.html), [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174.html) | `spec/00-overview.md` §2; capitalized requirement words; DESIGNED | Lower-case prose is not an additional RFC-style mandate. | Review every normative statement against a rule ID and planned case. |
| [RFC 5234](https://www.rfc-editor.org/rfc/rfc5234.html) | `spec/06-did-sage.md` §1; ABNF; DESIGNED | Prose length, canonical-form and supported-kind checks apply in addition to syntax. | Independent positive and rejected-identifier parsers. |
| [RFC 4648](https://www.rfc-editor.org/rfc/rfc4648.html) | `spec/00-overview.md` §2 and `spec/08-transport.md` §1; binary text; DESIGNED | Raw URL-safe base64 is canonical where stated; RFC 9421 and RFC 9530 fields use standard padded base64. | Exact-byte and malformed-padding vectors at each field boundary. |
| [RFC 8032](https://www.rfc-editor.org/rfc/rfc8032.html) | `spec/01-crypto.md` §2; pure Ed25519; DESIGNED | SAGE additionally requires prime-order, nonidentity decoded points and the uncofactored verification equation. This is a narrower acceptance profile, not a claim that every RFC 8032 verifier makes those checks. | Independent Go/Rust signature and rejection vectors. |
| [RFC 7748](https://www.rfc-editor.org/rfc/rfc7748.html) | `spec/04-hpke.md` §§1–3; X25519; DESIGNED | X25519 is a KEM/agreement key, never a signing algorithm; all-zero shared results fail. | Independent DH and role-selection vectors. |
| [RFC 6979](https://www.rfc-editor.org/rfc/rfc6979.html) | `spec/01-crypto.md` §2; deterministic ECDSA nonce guidance; REFERENCE | Deterministic signing is recommended, while secure randomized signing is permitted. SAGE verification and low-S rules remain mandatory for supported suites. | ECDSA positive/negative byte and verdict tests; no identical-signature claim. |
| [RFC 7517](https://www.rfc-editor.org/rfc/rfc7517.html), [RFC 7518](https://www.rfc-editor.org/rfc/rfc7518.html), [RFC 8037](https://www.rfc-editor.org/rfc/rfc8037.html) | `spec/10-resolution.md` §1 and `spec/11-registries.md` §§2–3; public JWK/OKP projection; DESIGNED | SAGE accepts only its authoritative record projection as a key source. Its secp256k1/Keccak suite is not JOSE ES256K. Generic JWK consumers may accept additional members; SAGE's closed authority-input schema is a local rule. | Independent DID/JWK consumer acceptance and SAGE rejection cases for contradictory/private/extra authority input. |
| [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html) | `spec/02-jcs.md` §§1–2; exact canonical bytes; DESIGNED | Signed SAGE input rejects negative-zero tokens and malformed/duplicate JSON before JCS; HTTP content is never reserialized for its digest. The token rejection is a SAGE input restriction, not a different JCS serialization algorithm. | Independent canonical-byte, Unicode, number and duplicate-member vectors. |
| [RFC 9180](https://www.rfc-editor.org/rfc/rfc9180.html) | `spec/04-hpke.md` §§1–3; Base mode exporter; DESIGNED | Sender authentication, the second ephemeral X25519 contribution, transcript binding and acknowledgement are SAGE composition. HPKE Base alone does not authenticate a sender or guarantee forward secrecy after recipient static-key compromise. | HPKE known-answer and cross-core schedule tests; independent composition analysis. |
| [RFC 5869](https://www.rfc-editor.org/rfc/rfc5869.html) | `spec/04-hpke.md` §3 and `spec/05-session.md`; HKDF extract/expand; DESIGNED | Exact salt, IKM, info, labels and transcript bytes are SAGE-defined. | Independent derivation vectors at every schedule boundary. |
| [RFC 8439](https://www.rfc-editor.org/rfc/rfc8439.html) | `spec/05-session.md`; ChaCha20-Poly1305; DESIGNED | Direction, nonce construction, sequence/replay state and key lifetime are SAGE-defined. | Cross-core record, key-rotation and replay tests. |
| [RFC 9421](https://www.rfc-editor.org/rfc/rfc9421.html) | `spec/03-rfc9421.md` §§1–4; HTTP signature base and response `;req` components; DESIGNED | Exactly one `sig1`, exact ordered coverage, algorithm, key role and freshness are a deliberately narrower application profile. HTTP verification does not itself authorize a tool call. | Independent signature-base vectors, HTTP round trips, duplicate-header and transformed-proxy rejection. |
| [RFC 9530](https://www.rfc-editor.org/rfc/rfc9530.html) | `spec/03-rfc9421.md` §§1–3; `Content-Digest`; DESIGNED | The digest covers received HTTP content bytes and is itself signed. Content coding is excluded by the SAGE HTTP profile; an unsigned digest grants no authenticity. | Received-byte tests, including whitespace, framing, and forbidden content coding. |
| [RFC 8941](https://www.rfc-editor.org/rfc/rfc8941.html), [RFC 9651](https://www.rfc-editor.org/rfc/rfc9651.html) | `spec/03-rfc9421.md` §1; Structured Field parsing and serialization; DESIGNED | RFC 9651 obsoletes RFC 8941, while RFC 9421 cites RFC 8941. SAGE pins the RFC 9421 signature-field subset; newer Structured Field types do not expand accepted signature parameters. | Cross-parser exact-byte and malformed-field tests against the selected subset. |
| [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html), [RFC 9111](https://www.rfc-editor.org/rfc/rfc9111.html) | `spec/03-rfc9421.md` and `spec/09-registry.md` §8; HTTP content and cache semantics; DESIGNED | `Accept-Encoding: identity` is integration guidance; protected HTTP messages must omit content coding. Web registry responses cannot become authority merely through cache freshness. | Proxy/automatic-decompression checks and registry cache-control integration tests. |
| [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457.html) | `spec/10-resolution.md` §5; optional HTTP problem details; DESIGNED | Exact SAGE type URI, title and status are fixed per public resolution code. Authentication failures remain generic; clients never fetch a type URI to decide trust. | Publish and dereference each stable type URI; test an independent problem-details consumer and HTTP/status equality. Publication is not established by this repository review. |
| [RFC 6648 / BCP 178](https://www.rfc-editor.org/rfc/rfc6648.html) | `spec/11-registries.md` §6; field-name practice; REFERENCE | Existing signed `X-SAGE-*` names are an explicit naming exception, not an assertion that `X-` means private or standardized. | Future rename requires a separately versioned wire migration and vectors. |
| [W3C DID Core 1.0](https://www.w3.org/TR/did-core/), [Controlled Identifiers 1.0](https://www.w3.org/TR/cid-1.0/) | `spec/06-did-sage.md` and `spec/10-resolution.md`; DID grammar, JSON document and verification relationships; DESIGNED | `did:sage` is a proposed method, not a W3C endorsement. Registry authority is method-specific; the SAGE Card proof is not a W3C Data Integrity suite. | Independent DID document consumer and method-resolution tests. |
| [W3C DID property extensions, 11 December 2025](https://www.w3.org/TR/2025/NOTE-did-extensions-properties-20251211/) | `spec/10-resolution.md` §1; `JsonWebKey2020` vocabulary; REFERENCE | This is a W3C Group Note; `JsonWebKey2020` is not silently aliased to Controlled Identifiers' `JsonWebKey`. | Independent consumer test of the exact projected method type. |
| [W3C DID Resolution Candidate Recommendation Draft, 28 August 2026](https://www.w3.org/TR/2026/CRD-did-resolution-1.0-20260828/) | `spec/10-resolution.md` §§2–5; resolution concepts/result structure; REFERENCE | The source is a mutable work in progress, not a completed Recommendation. Chapter 10 owns the 0.10.0 acceptance contract; SAGE does not claim general draft conformance or inherit later changes. | Version-specific independent resolver/consumer tests; reassess if the W3C draft advances. |
| [CAIP-2](https://chainagnostic.org/CAIPs/caip-2) | `spec/06-did-sage.md` §2; chain namespace; DESIGNED | SAGE also binds the registry contract address to prevent cross-deployment identity collision. | Namespace and canonical-identifier tests for each supported deployment. |
| [MCP 2025-06-18 lifecycle](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle), [transports](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports), [tools](https://modelcontextprotocol.io/specification/2025-06-18/server/tools) | `profiles/non-http-mcp-security.md`; one pinned custom non-HTTP binding; DESIGNED | Custom transport acknowledgement is not an MCP notification response. HTTP, stdio framing, other MCP versions and general MCP service interoperability are not claimed. | Exact-version Client/Server interoperability, negotiation, discovery, protected call and closure tests. |

## Open evidence and publication gates

1. Preserve the earlier 479-case snapshot and the current 481-case Inspector
   plan as planned evidence; do not
   infer standards conformance from the historical vectors or selected PASS runs.
2. Derive independent positive and negative byte/verdict vectors from each source
   standard and its SAGE profile. Cross-check both cores and an external
   consumer where the profile claims generic interoperability.
3. Validate the optional RFC 9457 binding's problem type documentation and
   actual HTTP responses. The fixed type URI is a wire identifier; changing it
   later requires explicit compatibility analysis.
4. Review SAGE's HPKE/exporter/ephemeral composition separately from primitive
   RFC conformance. Preserve the current `NOT_ESTABLISHED` overall verdict until
   the core, Inspector, host and Registry Source evidence gates pass.

The prior [standards review](standards.md), [standards decisions](standards-revision-decisions.md),
[traceability plan](traceability.json) and [Inspector execution order](https://github.com/SAGE-X-project/sage-inspector/blob/main/docs/execution-order.md)
have different purposes. This matrix records source applicability, not a new
conformance level or a substitute for the fixed project order.
