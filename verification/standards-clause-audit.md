# Standards-to-clause audit for SAGE 0.10.0

Status: **DESIGN_AUDIT_WITH_OPEN_FINDINGS**. Reviewed on 2026-09-27 against
`sage-spec` revision `01fc7632168da1e2855097896f3ce28ae2894aa1` and the
linked, dated standards. This is a clause-focused review of the constructions
SAGE actually uses, not a certification of every clause of every publication.
It changes no normative text, traceability case, accepted byte or verdict.
The [application matrix](standards-application-matrix.md) identifies scope;
this report checks selected source requirements against the corresponding
SAGE rules and records the corrections required before a new pinned snapshot.
The 481 parent cases remain planned, not executed. Overall conformance remains
`NOT_ESTABLISHED`.

## Confirmed normative mismatch

**SCA-01 — unregistered HTTP signature `alg` (high).**
[RFC 9421 §3.3](https://www.rfc-editor.org/rfc/rfc9421.html#section-3.3)
requires an algorithm selected using the `alg` signature parameter to use a
value from the [HTTP Signature Algorithms registry](https://www.iana.org/assignments/http-message-signature).
The IANA registry inspected on 2026-09-27 lists `ed25519` and
`ecdsa-p256-sha256`, but not `sage-secp256k1-keccak256`. Its
[registration rules](https://www.rfc-editor.org/rfc/rfc9421.html#section-6.2)
also say an algorithm name should be at most 20 characters; SAGE's private
name exceeds that recommendation. [MSG-01](../spec/03-rfc9421.md) requires
`alg` and admits the selected chapter-01 suite. [TABLE-02](../spec/11-registries.md)
describes that private name as an HTTP `alg` value. Hence an optional
secp256k1 HTTP message currently permitted by SAGE conflicts with the RFC's
registered-`alg` requirement. Calling the value “private” does not create a
private-use exception to that requirement. This is a specification finding,
not evidence of an exploit or of current core behavior.

**Recommended disposition for the coordinated normative revision:** retain
`sage-secp256k1-keccak256` for SAGE's non-HTTP proofs/envelopes where applicable,
but limit HTTP `alg` and its selected signing key to registered, SAGE-supported
`ed25519` or `ecdsa-p256-sha256` until an explicitly reviewed registration or
versioned alternative exists. Because [TRANSPORT-05](../spec/08-transport.md)
requires the HTTP outer key reference to equal the inner envelope `kid`, a
record with only a secp256k1 signing key would have no conforming protected
HTTP path. Do not silently replace its key or algorithm. Update MSG-01,
CRYPTO-01, TABLE-02, TRANSPORT-05, compatibility guidance and traceability
together. Plan independent positive cases for each allowed HTTP suite and
negative cases for the private `alg`, an only-private-key record, and fallback.
If registration is chosen instead, confirm the live IANA assignment and
exact `HTTP_SIGN`/`HTTP_VERIFY` definition before allowing it on the wire.

## Additional text and reference decisions

**SCA-02 — canonical DID prefix versus ABNF (medium, text precision).**
[RFC 5234 §2.3](https://www.rfc-editor.org/rfc/rfc5234.html#section-2.3)
treats bare quoted ABNF strings as case-insensitive.
[ID-01](../spec/06-did-sage.md) uses `"did:sage:"`, while ID-02 explicitly
lowercases the *kind* and chain address but does not state an exact-byte
scheme/method-prefix acceptance rule. The intended canonical spelling is
clear from examples and the DID method name, but a grammar-only parser can
accept a mixed-case prefix. In the coordinated revision, state whether only
the exact ASCII prefix is accepted and, if so, use numeric case-sensitive
ABNF octets or cite [RFC 7405](https://www.rfc-editor.org/rfc/rfc7405.html)
for `%s"did:sage:"`. Add mixed-case prefix acceptance/rejection vectors.
This is an ambiguity in SAGE's own canonical input contract, not a claim
that DID Core is nonconformant.

**SCA-03 — missing secp256k1 JWK source (low, reference accuracy).**
[RFC 7518 §6.2.1.1](https://www.rfc-editor.org/rfc/rfc7518.html#section-6.2.1.1)
names P-256, P-384 and P-521 and permits other registered curves.
[RFC 8812 §3.1](https://www.rfc-editor.org/rfc/rfc8812.html#section-3.1)
defines the `EC`/`secp256k1` JWK projection that
[RESOLVE-01](../spec/10-resolution.md) emits. Cite RFC 8812 for the *key
representation* in the next standards/reference revision. Its `ES256K`
signature algorithm uses SHA-256 and must remain distinct from SAGE's
Keccak suite. No JWK or signing-byte change follows from this citation.

## Clause-to-rule review

“Text aligned” means the examined SAGE text states the selected source
construction or its deliberate restriction; it is not a runtime result or a
complete external-standard conformance opinion. “Reference only” is not a
claim of source conformance. All rows still need the evidence listed in the
[application matrix](standards-application-matrix.md).

| Source clause or dated publication | SAGE rule(s) checked | Text result / remaining boundary |
| --- | --- | --- |
| [RFC 2119 §2](https://www.rfc-editor.org/rfc/rfc2119.html#section-2), [RFC 8174 §2](https://www.rfc-editor.org/rfc/rfc8174.html#section-2) | OVERVIEW-01 and chapter 00 §2 | Text aligned for capitalized requirement words; a complete MUST/SHOULD-to-case inventory is still required. |
| [RFC 5234 §2.3](https://www.rfc-editor.org/rfc/rfc5234.html#section-2.3), [RFC 7405 §2.1](https://www.rfc-editor.org/rfc/rfc7405.html#section-2.1) | ID-01/02 | **SCA-02:** exact scheme/method-prefix case behavior needs a canonical text decision. |
| [RFC 4648 §§3.2, 3.5, 4–5](https://www.rfc-editor.org/rfc/rfc4648.html#section-3) | OVERVIEW-01, TRANSPORT-01, REG-01, MSG-01 | Text distinguishes unpadded base64url from padded Structured Field base64; independent pad-bit and alternate-encoding rejection remains. |
| [RFC 8032 §5.1.7](https://www.rfc-editor.org/rfc/rfc8032.html#section-5.1.7), [RFC 7748 §6.1](https://www.rfc-editor.org/rfc/rfc7748.html#section-6.1) | CRYPTO-01/02, HPKE-01/03, TABLE-03 | Text states a narrower Ed25519 verifier profile and all-zero X25519 refusal; cross-library and role vectors remain. |
| [RFC 6979 §3](https://www.rfc-editor.org/rfc/rfc6979.html#section-3) | CRYPTO-03 | Recommendation only; secure randomized ECDSA remains permitted. No deterministic-signature equality claim. |
| [RFC 7517 §4](https://www.rfc-editor.org/rfc/rfc7517.html#section-4), [RFC 7518 §6.2](https://www.rfc-editor.org/rfc/rfc7518.html#section-6.2), [RFC 8037 §2](https://www.rfc-editor.org/rfc/rfc8037.html#section-2), [RFC 8812 §3.1](https://www.rfc-editor.org/rfc/rfc8812.html#section-3.1) | RESOLVE-01, TABLE-03 | Exact authority-input projection is a deliberate SAGE restriction, while generic JWK consumers may accept optional fields; **SCA-03** corrects the missing secp256k1 representation reference. Independent consumer evidence remains. |
| [RFC 8785 §§3.1–3.2](https://www.rfc-editor.org/rfc/rfc8785.html#section-3) | JCS-01..04 | Text uses JCS serialization and adds pre-JCS negative-zero rejection. Duplicate names, Unicode and number behavior need independent byte vectors. |
| [RFC 9180 §§5.1.1, 5.3, 7.1, 9](https://www.rfc-editor.org/rfc/rfc9180.html#section-5) | HPKE-01..06 | HPKE Base exporter is identified; sender authentication, extra X25519 and acknowledgement are SAGE composition. Primitive alignment does not prove the composition's security or forward secrecy. |
| [RFC 5869 §§2.2–2.3](https://www.rfc-editor.org/rfc/rfc5869.html#section-2) | HPKE-03, SESSION-02 | Extract/Expand inputs are stated; exact cross-core derivation vectors remain. |
| [RFC 8439 §2.8](https://www.rfc-editor.org/rfc/rfc8439.html#section-2.8) | SESSION-02..05 | 32-byte key, 12-byte sequence nonce and AEAD AAD are stated; atomic nonce allocation and replay tests remain. |
| [RFC 9421 §§2.3–2.5, 3.3, 4](https://www.rfc-editor.org/rfc/rfc9421.html#section-2) | MSG-01..06, TRANSPORT-05, TABLE-02 | Exact one-`sig1` coverage is a deliberate narrower profile. **SCA-01 blocks a blanket RFC 9421 conformance claim for the optional secp256k1 HTTP path.** Independent signature-base and proxy tests remain. |
| [RFC 9530 §§2, 6](https://www.rfc-editor.org/rfc/rfc9530.html#section-2) | MSG-01/04, JCS-04 | Text hashes received HTTP content and signs the digest field; no authentication is inferred from digest alone. Received-byte and content-coding tests remain. |
| [RFC 8941 §3.3.5](https://www.rfc-editor.org/rfc/rfc8941.html#section-3.3.5), [RFC 9651 §1](https://www.rfc-editor.org/rfc/rfc9651.html#section-1) | MSG-01/04 | Selected signature-field subset is fixed to RFC 9421 behavior; cross-parser rejection tests remain. |
| [RFC 9110 §§6.4, 8.4, 12.5.3](https://www.rfc-editor.org/rfc/rfc9110.html#section-6.4), [RFC 9111 §5.2](https://www.rfc-editor.org/rfc/rfc9111.html#section-5.2) | MSG-01/04, REG-08 | No protected content coding and no cached registry authority are SAGE restrictions; proxy/decompression and cache tests remain. |
| [RFC 9457 §§3.1, 4](https://www.rfc-editor.org/rfc/rfc9457.html#section-3.1) | RESOLVE-05 | Type/title/status mapping and HTTP status equality are stated. Type-URI publication, actual responses and an independent consumer are **not verified**. |
| [RFC 6648 §3](https://www.rfc-editor.org/rfc/rfc6648.html#section-3) | TABLE-06 | `X-SAGE-*` names are an explicit naming exception and migration issue, not evidence of standard registration. |
| [W3C DID Core §5](https://www.w3.org/TR/did-core/#core-properties), [Controlled Identifiers 1.0](https://www.w3.org/TR/cid-1.0/) | ID-01..04, RESOLVE-01..05 | DID document and verification relationships are mapped; independent generic-consumer behavior and method resolution are untested. SAGE registry freshness is method-specific. |
| [W3C DID Property Extensions, 11 Dec 2025](https://www.w3.org/TR/2025/NOTE-did-extensions-properties-20251211/) | RESOLVE-01 | `JsonWebKey2020` is Note vocabulary, not an alias for Controlled Identifiers' `JsonWebKey` or a W3C Recommendation claim. Consumer evidence remains. |
| [W3C DID Resolution CR Draft, 28 Aug 2026](https://www.w3.org/TR/2026/CRD-did-resolution-1.0-20260828/) | RESOLVE-02..05 | Reference only. Chapter 10 owns the pinned 0.10.0 contract; later draft changes do not silently apply. |
| [CAIP-2](https://chainagnostic.org/CAIPs/caip-2) | ID-02, REG-06 | Chain namespace and contract address jointly select the registry; per-deployment identity tests remain. |
| [MCP 2025-06-18 lifecycle](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle), [transport](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports), [tools](https://modelcontextprotocol.io/specification/2025-06-18/server/tools) | MSET-01..08, MOWN-01..06 | One pinned custom non-HTTP binding is claimed, not general MCP transport interoperability. Version-matched Client/Server and effect-boundary evidence remains. |

## Gate to the next pinned specification

1. Decide and integrate SCA-01 with the already planned implementation-pattern
   review. Do not publish an HTTP conformance claim while the private `alg`
   remains allowed. Resolve SCA-02 and SCA-03 in the same coordinated review.
2. Pin the changed chapters, compatibility statement and new Inspector cases
   as one successor snapshot. Preserve the current 481-case snapshot and its
   checker as historical evidence; do not relabel old Inspector results.
3. Produce independent positive and negative exact-byte/verdict vectors for
   each selected source construction. Run version-matched Go/Rust, external
   consumer, Agent-host and Registry Source checks at their respective gates.
4. Analyze the HPKE exporter/ephemeral composition separately from primitive
   RFC 9180 compatibility. Keep external audit and release status explicit.
