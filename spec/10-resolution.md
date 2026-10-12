# 10. Resolution and the resolved document

Target: **0.10.0**. Requirements: R-4, R-8, R-9, R-14, R-28 to R-30, R-34, R-35.
Legacy `vectors/did.json` is not current conformance evidence.

## 1. The document — RESOLVE-01 (R-4, R-14, R-29)

The JSON DID document has `id`, `verificationMethod`, `service` and, when
they have members, `authentication`, `assertionMethod` and `keyAgreement`.
This is the DID Core 1.0 projection of DIDP-01. No `@context` is included:
this is the JSON representation with media type `application/did+json` in
[DID Core](https://www.w3.org/TR/did-core/). Key type is `JsonWebKey2020`,
as documented in the [DID property extensions](https://www.w3.org/TR/did-extensions-properties/#jsonwebkey2020).
[Controlled Identifiers 1.0](https://www.w3.org/TR/cid/) uses the distinct
`JsonWebKey` type. This projection does not silently alias or emit that type;
the DID 1.1 projection of DIDP-01 uses it.
This projection does not claim JSON-LD processing or fetch remote contexts.
The registry's account/controller representation is management data, not
a fabricated self-controller DID; it remains in SAGE metadata.

| Source | Projection |
|---|---|
| record ID | document `id`, exact canonical DID |
| accepted/unexpired signing key | verification method and references in `authentication`, `assertionMethod` |
| accepted/unexpired X25519 key | verification method and reference in `keyAgreement` |
| revoked/expired key | no verification method; retained in authoritative record |
| created/deactivated record | empty `verificationMethod` array and no relationship member |
| registry service | `{ "id": DID + "#" + name, "type": type, "serviceEndpoint": uri }` |

A verification relationship (`authentication`, `assertionMethod`,
`keyAgreement`) with no member is omitted, never projected as an empty array:
DID Core 1.0 §5.3 and Controlled Identifiers 1.0 §2.3 require a present
relationship to hold one or more verification methods.

Each verification method has exactly `id` (DID plus immutable key name),
`type`, `controller` (the subject DID), `publicKeyJwk`. Keys and services
are sorted by ASCII name; a service name MUST NOT collide with a key name.

JWKs contain exactly `kty`, `crv`, `x` and, for EC keys, `y`. The types/curves
are chapter 11. `x`/`y` are unpadded canonical base64url, 32 decoded bytes
each; EC coordinates come from the validated uncompressed point. Reject
private `d`, wrong curves, invalid points, extra/contradictory members and
noncanonical encodings. Algorithm is determined from the authenticated
registry entry; accepting a JWK does not authorize arbitrary algorithms.
See [RFC 7517](https://www.rfc-editor.org/rfc/rfc7517.html) and
[RFC 8037](https://www.rfc-editor.org/rfc/rfc8037.html) for JWK and OKP;
[RFC 8812 §3.1](https://www.rfc-editor.org/rfc/rfc8812.html#section-3.1)
defines the `EC`/`secp256k1` public-key representation. RFC 8812's JOSE
`ES256K` uses SHA-256 and does not define SAGE's Keccak signing suite.
RFC 7517 permits a generic JWK consumer to ignore unknown additional members.
The exact member set above is SAGE's authoritative projection and validation
profile, not a claim that arbitrary third-party JWK documents become registry
authority. An independent DID consumer must be tested against the produced
document before generic interoperability is claimed; that test does not replace
the verifier's current registry observation and key checks.

## 2. Resolving — RESOLVE-02 (R-4, R-8, R-9, R-36)

`resolve(identifier)` returns `didDocument`, `didDocumentMetadata`,
`didResolutionMetadata`. An implementation MUST:

1. Check syntax/size and select an explicitly supported registry kind.
2. Acquire an authorized fresh observation under chapter 09, never follow
   a resolver URL supplied by the unverified sender.
3. Validate complete record structure, ID equality, algorithm encodings,
   proofs, version monotonicity and state from that single observation.
4. Project the validated record and metadata. No missing proof or missing
   state is defaulted to accepted/active.

An arbitrary third-party resolver response over TLS is not a blockchain
proof. A verifier must either validate registry evidence itself or explicitly
trust the resolver's authenticated identity and observation policy. This
trust choice is deployment configuration, not peer-supplied input.
Historical resolution may be provided as a separate administrative API but
MUST NOT authorize present messages or bypass current revocation checks.

## 3. Metadata — RESOLVE-03 (R-4, R-9, R-14)

`didDocumentMetadata` contains `deactivated` (boolean), `versionId` (record
version), and `sage` object with `state`, `controller`, `observedAt`,
`source`, `observedTime`. `observedAt` is the finalized block hash for eip155
or the `issued` integer for web. `source` is the configured source identity
(ASCII string <= 2048 bytes), not evidence by itself; `observedTime` is the
local integer Unix second when observation completed. State is always
explicit, including `created`. No `canonicalId`/`equivalentId` aliases are
emitted. `didResolutionMetadata` contains `contentType` equal to the media
type of the returned projection (DIDP-02) on success.

A deactivated/created record resolves successfully for inspection but MUST
NOT authenticate a protected operation. Successful resolution is not a
successful authorization decision. Maximum complete resolution response is
262144 UTF-8 bytes, with at most 128 keys and 16 services inherited from the
record; JCS chapter 02 bounds apply.

## 4. Dereferencing a key — RESOLVE-04 (R-8, R-9)

Dereference only canonical full DID URLs. Resolve afresh, then use exact
ID equality. Absent keys fail with `key.not-in-record`; a retained revoked
or expired record entry can produce `key.revoked` or `key.expired` locally.
No alternate-key search is permitted. Public authentication responses
collapse these details under chapter 08; administrative resolution is not
an authentication oracle for signature validity.

## 5. Errors and HTTP binding — RESOLVE-05 (R-14, R-34, R-35)

Optional read-only binding: authenticated TLS
`GET /0.10.0/identifiers/{identifier}`; path transport percent-encoding is
decoded exactly once and the resulting DID must obey chapter 06 (which
forbids percent-encoding within the DID). Reject queries and extra path
segments. A request MUST include `X-SAGE-Version: 0.10.0`; other versions
are rejected without fallback. Respond with that header and `Cache-Control:
no-store`. The `Accept` header selects the response under DIDP-02:
`application/did+json` or `application/did` for the document only, or
`application/json` for the three-member resolution envelope above with the DID
Core 1.0 projection. This binding does not serve `application/did-resolution`.
An authentication caller needs the metadata and authoritative
record validation, not only the bare document.

Errors use [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457.html)
`application/problem+json`, with `type` equal to
`https://sage-x-project.github.io/sage-spec/errors/` plus the local code,
`title` and `status` as specified below. The HTTP response status MUST equal
the problem `status`. The `type` URI is an identifier, never a URL to fetch
while deciding whether a resolution response is trustworthy. Publishers of
this binding MUST document the exact type URI, title and status for every
emitted code and SHOULD make the type URI resolve to human-readable guidance.
Until the listed URI endpoints and an independent RFC 9457 consumer have been
checked, this document does not claim the optional HTTP binding interoperates
with generic problem-detail clients.

| Code | Title | HTTP/problem status |
|---|---|---|
| `id.malformed` | Malformed identifier | 400 |
| `id.unknown-kind` | Unsupported registry kind | 400 |
| `version.unsupported` | Unsupported protocol version | 400 |
| `record.not-found` | Record not found | 404 |
| `key.not-in-record` | Key not found | 404 |
| `record.unreachable` | Registry unavailable | 502 |
| `record.stale` | Registry observation stale | 502 |
| `record.invalid` | Registry record invalid | 502 |
| `size.exceeded` | Input too large | 413 |
| `representation.unsupported` | Unsupported representation | 406 |

No partial document is returned on failure. These diagnostics describe
public resolution, not the check that failed on a signed application
message. Unauthenticated error bodies never authorize retry with weaker
settings; detailed internal endpoints require deployment access controls.

## 6. Two projections — DIDP-01 (R-14, R-29)

A resolver offers two projections of one validated record:

- **DID Core 1.0 projection**: exactly the RESOLVE-01 document, with no
  `@context`, media type `application/did+json` and verification method type
  `JsonWebKey2020`.
- **DID 1.1 projection**: the same document members with these differences only:
  `@context` is present and is exactly the JSON string
  `https://www.w3.org/ns/did/v1.1`; the media type is `application/did`; each
  verification method `type` is `JsonWebKey` (Controlled Identifiers 1.0).

In both projections a verification relationship (`authentication`,
`assertionMethod`, `keyAgreement`) that would have no member is omitted. DID Core
1.0 §5.3 and Controlled Identifiers 1.0 §2.3 make each relationship optional and
require a present one to hold one or more verification methods, so an empty
array is not conforming. This applies to `created` and `deactivated` records and
to any record that has, for example, no accepted X25519 key. `verificationMethod`
stays an array and is empty when no key is projected.

In both projections `publicKeyJwk` has exactly the members RESOLVE-01 fixes
(`kty`, `crv`, `x` and, for EC keys, `y`). The DID 1.1 projection does not add
`alg` to the JWK even though Controlled Identifiers says it SHOULD be included:
the algorithm comes from the authenticated registry entry, and a second source
of algorithm information could disagree with it. `kid` is optional in
Controlled Identifiers and is not added. The `Multikey` type is not emitted, so
one key has exactly one encoding. DID 1.1 §6.2.3 also allows an array
`@context`; this projection always uses the single string.

The DID 1.1 projection always carries `@context`, because DID 1.1 does not say
whether a consumer will perform JSON-LD processing. The context is a local
constant whose SHA-256 DID 1.1 §6.2.4 gives for
`https://www.w3.org/ns/did/v1.1`; a DID 1.1 erratum can change that digest. It
is never fetched.

Because the verification method `type` differs, the DID 1.1 projection is not a
re-serialization of the DID Core 1.0 document. The component that projects the
record, a SAGE resolver or a `did:sage` driver, produces each projection from
the record itself.

A resolver that cannot validate the record returns an error and no document in
either projection.

## 7. Projection selection — DIDP-02 (R-14, R-34)

This rule sets the RESOLVE-03 `contentType` and the RESOLVE-05 `Accept`
handling. The caller selects a projection with the resolution `accept` option or
the HTTP `Accept` header. The value is matched as one media type without
parameters:

| Requested value | Result |
|---|---|
| absent, `*/*` or `application/did+json` | DID Core 1.0 projection |
| `application/json` | the RESOLVE-05 three-member envelope with the DID Core 1.0 projection, unchanged |
| `application/did` | DID 1.1 projection |
| a list, a parameter or q-value, or any other type | rejected with the new code `representation.unsupported` (HTTP 406) |

`application/did+ld+json` and `application/did-resolution` are other types and
are rejected by a SAGE resolver. `didResolutionMetadata.contentType` equals the
media type of the returned document. A resolver MUST NOT return a projection the
caller did not request and MUST NOT fall back from one projection to the other.

The table binds the SAGE resolver and its RESOLVE-05 HTTP binding only. A
component that presents SAGE resolution through the DID Resolution v1 interface
(DIDP-05) follows DID Resolution for `accept` matching and for its HTTPS
binding, including the complete resolution result it returns when `Accept` is
absent. Every DID document such a component returns is a DIDP-01 projection:
the DID 1.1 projection when the returned media type is `application/did`, and
the DID Core 1.0 projection for any other DID media type it supports. DIDP-03
applies to all of them.

## 8. Projection equivalence — DIDP-03 (R-4, R-14)

Both projections MUST be produced from the same single authoritative
observation. For any record they MUST agree on the document `id`, the set of
verification method `id` values, each method's `controller` and JWK members, the
contents of `authentication`, `assertionMethod` and `keyAgreement`, the `service`
array and `didDocumentMetadata.versionId`. They differ only in `@context`, media
type and verification method `type`. A resolver that produces the two
projections from different observations, or mixes members of two record
versions in one document, violates this rule.

## 9. Documents are not key authority — DIDP-04 (R-8, R-9, R-14)

A DID document of either projection is a view for display and for external DID
consumers. A SAGE verifier MUST NOT take signing or key-agreement authority from
a DID document supplied by a peer, a card, a cache or an untrusted resolver; it
uses the authoritative record under chapters 09 and 10.

No projection emits `alsoKnownAs`, `equivalentId` or `canonicalId`. A SAGE
verifier treats such members in any received document as having no effect.
Linking a `did:sage` identifier to an identifier of another DID method, or to an
external agent registry entry, needs an explicit two-sided authenticated linkage
that this version does not define; it is never an alias.

## 10. Errors through the DID Resolution interface — DIDP-05 (R-14, R-34, R-35)

The SAGE resolver and its RESOLVE-05 HTTP binding keep the SAGE problem types
and statuses. A component that presents SAGE resolution through the DID
Resolution v1 interface, such as the separate DID project's `did:sage` driver,
MUST map them as follows. The emitted problem `type` is the DID Resolution URL;
the SAGE code is carried in the problem extension member `sageCode`; the HTTP
status follows DID Resolution §12.1. No document is returned on any error. The
component produces these codes and `sageCode` itself. When it is built on a
general DID resolver whose error mapping would replace a driver error, the
component stands in front of that resolver and answers SAGE errors before the
general mapping applies.

| SAGE code | DID Resolution error type |
|---|---|
| `id.malformed`, `size.exceeded` | `INVALID_DID` |
| `id.unknown-kind` | `METHOD_NOT_SUPPORTED` (the method is `sage`; the registry kind is unsupported) |
| `version.unsupported` | `INVALID_OPTIONS` |
| `record.not-found` | `NOT_FOUND` |
| `record.unreachable`, `record.stale`, `record.invalid` | `INTERNAL_ERROR`; never `NOT_FOUND`, because a stale view is not absence |
| `representation.unsupported` | `FEATURE_NOT_SUPPORTED` (DID Resolution §4.4 uses it for an unsupported option); through this interface it applies only to an `accept` value the component cannot serve under DID Resolution, not to the DIDP-02 table |
| `key.not-in-record` (DID URL dereference) | `NOT_FOUND` |

Through that interface a `deactivated` record is reported as DID Resolution
§4.4 states for a deactivated DID: `didDocument` is null and
`didDocumentMetadata.deactivated` is `true` (HTTP 410 in its binding). The SAGE
interface keeps its RESOLVE-01 projection, with the verification relationships
omitted (DIDP-01). Either way the record is never usable for a protected operation
(RESOLVE-03). A `created` record is returned as SAGE projects it, with
no verification relationships, and is likewise not usable.

## 11. Security and evidence

DID Core defines a data model rather than a guarantee that a resolver is
honest or fresh. Source trust, fail-closed observation and record proof
validation address A-2/A-4/A-6 within the declared boundary. Endpoint fetches
remain controlled to prevent SSRF. RFC 7517/8037 encoding rules are adopted;
SAGE intentionally restricts optional JWK members for one wire form.
Independent DID-consumer interoperability and hostile-resolver tests remain
future inspector work, not evidence claimed by this documentation update.
