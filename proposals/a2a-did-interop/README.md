# A2A 1.0 binding and DID 1.0/1.1 projection proposal

Status: **proposed design, not adopted**. MUST/SHOULD below apply only if this
proposal is adopted. It does not change the 0.10.0 normative chapters, make any
core conformant, or claim interoperability with any external implementation.
Publication of this proposal is not adoption or a protocol release. Every
planned case is `NOT_RUN`.

This proposal serves stage 7 of the
[program sequence](../../architecture/program-sequence.md): it reviews the A2A
and DID standards and versions SAGE should interoperate with, gives an exact
identity, card and resolution mapping, and lists positive and negative cases.
The research behind it compared A2A 0.2.6, 0.3.0 and 1.0, DID Core 1.0, DID 1.1,
DID Resolution, DID methods and the verifiable credential ecosystem as observed on
2026-10-11. The [basis](basis.json) pins the reviewed SAGE revision and the exact
external documents with the SHA-256 of the bytes fetched that day. The
[review record](review.md) lists the counterexample review that revised this
draft.

Decisions recorded with this proposal (2026-10-11):

1. The binding targets A2A protocol version `1.0` only. A2A 0.3 is not accepted
   by an agent that offers SAGE protection.
2. Resolution offers both a DID Core 1.0 projection and a DID 1.1 projection.
3. A separate DID project, not the SAGE cores, owns general DID and credential
   support; this proposal states only the boundary SAGE relies on. That project
   now exists as `SAGE-X-project/did-go`, checked by the independent
   `SAGE-X-project/did-inspector`. The informative boundary section below pins
   the revisions reviewed on 2026-10-12. Neither repository changes, decides or
   adopts any rule of this proposal.

## Sources and their status

- A2A: tag `v1.0.1` of `a2aproject/A2A`, protocol version `1.0`. Agent Card
  signing is A2A §8.4: RFC 8785 canonicalization and an RFC 7515 JWS whose
  protected header carries `alg` and `kid`. A2A does not define how a signing key
  is bound to an agent identity, and defines no request signatures, end-to-end
  encryption or normative replay protection. A2A §5.8 and §12 allow custom
  protocol bindings identified by a URI; a custom binding MUST state how service
  parameters are carried (A2A §3.2.6) and how A2A errors map (A2A §5.4).
- DID Core 1.0 is a W3C Recommendation (2022-07-19). It defines a JSON
  representation (`application/did+json`) and a JSON-LD representation
  (`application/did+ld+json`, first `@context` `https://www.w3.org/ns/did/v1`).
- DID 1.1 is a W3C Candidate Recommendation Snapshot (2026-03-05), not a
  Recommendation. It layers on Controlled Identifiers 1.0, defines a single JSON
  representation with media type `application/did` and context
  `https://www.w3.org/ns/did/v1.1`, and uses the `JsonWebKey` and `Multikey`
  verification method types. It states no compatibility rule for 1.0 documents.
  IANA lists `application/did`; it does not list `application/did+json` or
  `application/did-resolution`.
- DID Resolution v1 is a W3C Candidate Recommendation Draft (2026-10-01). It
  recommends (SHOULD) RFC 9457 problem details whose `type` is a URL under
  `https://www.w3.org/ns/did#`, and still cites DID Core 1.0 normatively.
- RFC 9864 registers the fully specified JOSE algorithm `Ed25519` and marks the
  polymorphic `EdDSA` deprecated.

Because DID 1.1 and DID Resolution are not Recommendations, their text can still
change. Adoption of the DID 1.1 projection MUST record the exact revision it
implements, and a later revision reopens this proposal.

## A2AB-01: The SAGE protocol binding

Protected A2A traffic uses a custom A2A protocol binding, the **SAGE binding**,
identified in `supportedInterfaces[].protocolBinding` by the binding URI chosen
at adoption (OPEN-1). The standard `JSONRPC`, `GRPC` and `HTTP+JSON` bindings are
not protected by this proposal.

On the SAGE binding:

1. Each A2A call is one HTTPS `POST` to the interface `url`. The HTTP body is a
   chapter 08 request envelope, signed under chapter 03 MSG-02 and chapter 08
   TRANSPORT-02 without change to those rules (`Content-Type: application/json`).
2. The envelope `payload` carries the exact UTF-8 bytes of one JSON-RPC 2.0
   request object using the A2A §9 method names. With `session` encoding the
   chapter 05 plaintext is those bytes.
3. The A2A result is one chapter 08 TRANSPORT-03 response envelope whose `data`
   carries the exact UTF-8 bytes of one JSON-RPC 2.0 response object. A2A errors
   are JSON-RPC error objects inside `data` with the A2A §9 error codes; `success`
   is `false` only for the four SAGE transport errors of TRANSPORT-03.
4. A2A service parameters are carried in envelope `metadata`, which the envelope
   signature covers: `a2a_version` and `a2a_extensions`. No A2A service
   parameter is read from an HTTP header or query parameter on this binding.
5. Streaming responses do not exist on this binding, because TRANSPORT-03 allows
   one terminal response per request. `SendStreamingMessage` and
   `SubscribeToTask` are answered with the A2A unsupported-operation error.

## A2AB-02: Version

`a2a_version` MUST be exactly `1.0`. A server MUST reject a request whose
`metadata` lacks `a2a_version` or carries any other value, including `0.3`,
`1.0.1` or an empty string. The A2A patch version is not used on the wire.
Because metadata is a JSON object, there is exactly one value; the rule in A2A
§3.6 that an absent header means 0.3 never applies on this binding.

## A2AB-03: Extension declaration and activation

An agent that offers SAGE protection declares exactly one `AgentExtension` in
`capabilities.extensions` whose `uri` is the SAGE A2A extension URI (OPEN-1),
with `required` set to `true` and `params` an object with exactly these members:

| Member | Type and value |
|---|---|
| `sageVersion` | string, exactly `0.10.0` |
| `did` | string, the agent's canonical `did:sage` identifier (chapter 06) |
| `recordVersion` | string, canonical decimal registry version (chapter 09) |
| `issued`, `expires` | integers, Unix seconds, `0 < expires - issued <= 86400` |

A breaking change to this extension takes a new URI, as A2A §4.6.3 requires.

`a2a_extensions` is a comma-separated list of extension URIs without spaces. It
MUST contain the SAGE extension URI exactly once. A server MUST reject a request
that does not activate the extension.

## A2AB-04: Card shape for a protected agent

A card that declares the SAGE extension MUST also satisfy all of the following;
otherwise it is not eligible for any protected operation:

- every `supportedInterfaces` entry uses the SAGE binding with `protocolVersion`
  `1.0`; no standard binding and no other version is listed;
- `capabilities.streaming`, `capabilities.pushNotifications` and
  `capabilities.extendedAgentCard` are absent or `false`;
- the UTF-8 JSON is at most 262144 bytes, has no duplicate member names, no null
  values, and no member that the `AgentCard` message of the pinned `a2a.proto`
  does not define, except inside `params` of extensions other than SAGE's.

A server whose card declares the SAGE extension MUST NOT accept A2A operations
for that agent on any other binding or version. Push notification
configuration methods and `GetExtendedAgentCard` are answered with the A2A
unsupported-operation error. This removes the downgrade where an attacker calls
the same agent through an interface the binding does not protect.

## A2AB-05: Card identity binding

A2A §8.4 leaves the binding between a card signing key and the agent open. This
binding closes it with SAGE resolution:

1. The card carries exactly one SAGE signature: a `signatures` entry whose
   protected header has exactly the members `alg`, `kid` and `typ`, with no
   duplicate member, and whose unprotected `header` is absent. `typ` is exactly
   `sage-a2a-card+jws`. `kid` is a full canonical `did:sage` DID URL with a
   fragment (chapter 06). A card with two entries of this shape is rejected.
   Entries of another shape are ignored for every protected decision.
2. No alternative key source is used. A SAGE signature whose protected header
   carries `jku`, `jwk`, `x5u`, `x5c`, `crit` or `b64` is rejected, and the
   verifier never fetches a URL from the card to obtain a key.
3. The DID part of `kid`, derived by parsing, MUST equal `params.did`. When the
   client has a configured expected peer, `params.did` MUST equal it.
4. The verifier resolves `params.did` under chapter 09 freshness rules and
   applies chapter 06 ID-03 to `kid`: the key exists, is accepted, unrevoked and
   unexpired, has a signing algorithm, and is the only key tried. A record that
   is `created` or `deactivated` fails this step.
5. `alg` maps exactly to that key's chapter 11 algorithm: `ed25519` uses JOSE
   `Ed25519` (RFC 9864); `ecdsa-p256-sha256` uses JOSE `ES256`. `EdDSA` is not
   accepted. `sage-secp256k1-keccak256` keys cannot sign a card under this
   binding, because no JOSE algorithm defines that suite. Chapter 01 CRYPTO-02
   applies to the signature bytes: Ed25519 is verified strictly and a P-256
   signature with high S is rejected, so signers MUST produce low-S signatures.
6. The verifier canonicalizes the parsed card it will expose, exactly as A2A
   §8.4.1 states (protobuf field presence, `signatures` excluded, RFC 8785), and
   verifies the JWS with that key alone.
7. The current record version MUST equal `params.recordVersion`, and
   `params.issued <= now < params.expires` MUST hold under chapter 03 clock rules
   with no grace. A changed record or an expired card is rejected even if the
   signature verifies; the agent publishes a newly signed card.

The SAGE signed card of chapter 07 is unchanged and remains a separate
assertion. This binding does not rename it as an A2A signature, and an A2A card
signature is not a chapter 07 proof. A verified card is discovery data. It
grants no authorization, and its descriptions and skills are not instructions.

Without a configured expected peer, a verified card proves only that the agent
named in it controls the card; a card host can still serve a different agent's
valid card. A client that relies on discovery alone gets no protection against
that substitution, and a card that omits the extension gives no SAGE protection.

## A2AB-06: Interface eligibility and recipient

An interface of a card that passed A2AB-04 and A2AB-05 is eligible only if the
resolved record has a service whose `type` is `A2AInterface` (OPEN-4) and whose
`uri` equals the interface `url` byte for byte. The comparison does no URL
normalization: a trailing slash, letter case, an explicit default port or
percent-encoding makes the strings different. The client uses eligible
interfaces in card order.

The request envelope `recipient` MUST equal `params.did`. When a JSON-RPC
request carries an A2A `tenant`, the server MUST route it to the agent whose DID
equals `recipient` and reject the request if the tenant routes elsewhere. The
response is signed by `params.did` under TRANSPORT-03; chapter 06 ID-03 and the
expected-peer rule apply to every request and response.

A2A authentication schemes (API key, OAuth 2.0, OpenID Connect, mTLS) may still
be required by the server. They do not replace these checks, and these checks do
not replace them.

## A2AB-07: No downgrade

When trusted configuration requires SAGE for a peer, or the peer's card declares
the SAGE extension, a failure of any check in A2AB-01 to A2AB-06 aborts the
operation. The client MUST NOT retry it on another binding, with another A2A
version, without the extension or with unsigned discovery. A server MUST NOT
execute an operation from a request that failed these checks, and its public
error does not say which check failed (chapter 11 TABLE-07).

## DIDP-01: Two projections

A resolver offers two projections of one validated record:

- **DID Core 1.0 projection**: exactly the chapter 10 RESOLVE-01 document, with no
  `@context`, media type `application/did+json` and verification method type
  `JsonWebKey2020`. It is unchanged by this proposal.
- **DID 1.1 projection**: the same document members with these differences only:
  `@context` is present and is exactly the JSON string
  `https://www.w3.org/ns/did/v1.1`; the media type is `application/did`; each
  verification method `type` is `JsonWebKey` (Controlled Identifiers 1.0).

In both projections `publicKeyJwk` has exactly the members chapter 10 fixes
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

A resolver that cannot validate the record returns an error and no document in
either projection.

## DIDP-02: Projection selection

This rule amends chapter 10 RESOLVE-03 and RESOLVE-05, which today fix
`contentType` to `application/did+json` and claim no `application/did` media
type. The caller selects a projection with the resolution `accept` option or
the HTTP `Accept` header. The value is matched as one media type without
parameters:

| Requested value | Result |
|---|---|
| absent, `*/*` or `application/did+json` | DID Core 1.0 projection |
| `application/json` | the chapter 10 three-member envelope with the DID Core 1.0 projection, unchanged |
| `application/did` | DID 1.1 projection |
| a list, a parameter or q-value, or any other type | rejected with the new code `representation.unsupported` (HTTP 406) |

`application/did+ld+json` and `application/did-resolution` are other types and
are rejected by a SAGE resolver. `didResolutionMetadata.contentType` equals the
media type of the returned document. A resolver MUST NOT return a projection the
caller did not request and MUST NOT fall back from one projection to the other.

## DIDP-03: Projection equivalence

Both projections MUST be produced from the same single authoritative
observation. For any record they MUST agree on the document `id`, the set of
verification method `id` values, each method's `controller` and JWK members, the
contents of `authentication`, `assertionMethod` and `keyAgreement`, the `service`
array and `didDocumentMetadata.versionId`. They differ only in `@context`, media
type and verification method `type`. A resolver that produces the two
projections from different observations, or mixes members of two record
versions in one document, violates this rule.

## DIDP-04: Documents are not key authority

A DID document of either projection is a view for display and for external DID
consumers. A SAGE verifier MUST NOT take signing or key-agreement authority from
a DID document supplied by a peer, a card, a cache or an untrusted resolver; it
uses the authoritative record under chapters 09 and 10.

No projection emits `alsoKnownAs`, `equivalentId` or `canonicalId`. A SAGE
verifier treats such members in any received document as having no effect.
Linking a `did:sage` identifier to an identifier of another DID method, or to an
external agent registry entry, needs an explicit two-sided authenticated linkage
that this proposal does not define; it is never an alias.

## DIDP-05: Errors through the DID Resolution interface

The SAGE resolver and its chapter 10 HTTP binding keep the SAGE problem types
and statuses. A component that presents SAGE resolution through the DID
Resolution v1 interface, such as the separate DID project's `did:sage` driver,
MUST map them as follows. The emitted problem `type` is the DID Resolution URL;
the SAGE code is carried in the problem extension member `sageCode`; the HTTP
status follows DID Resolution §12.1. No document is returned on any error.

| SAGE code | DID Resolution error type |
|---|---|
| `id.malformed`, `size.exceeded` | `INVALID_DID` |
| `id.unknown-kind` | `METHOD_NOT_SUPPORTED` (the method is `sage`; the registry kind is unsupported) |
| `version.unsupported` | `INVALID_OPTIONS` |
| `record.not-found` | `NOT_FOUND` |
| `record.unreachable`, `record.stale`, `record.invalid` | `INTERNAL_ERROR`; never `NOT_FOUND`, because a stale view is not absence |
| `representation.unsupported` | `FEATURE_NOT_SUPPORTED` (DID Resolution §4.4 uses it for an unsupported option) |
| `key.not-in-record` (DID URL dereference) | `NOT_FOUND` |

Through that interface a `deactivated` record is reported as DID Resolution
§4.4 states for a deactivated DID: `didDocument` is null and
`didDocumentMetadata.deactivated` is `true` (HTTP 410 in its binding). The SAGE
interface keeps its chapter 10 projection with empty verification
relationships. Either way the record is never usable for a protected operation
(chapter 10 RESOLVE-03). A `created` record is returned as SAGE projects it, with
empty verification relationships, and is likewise not usable.

## Amendments required at adoption

Adoption changes existing chapters only in these places (PROC-02):

- chapter 06 ID-03: add the A2A card JWS `kid` to the list of key references;
- chapter 10 RESOLVE-03 and RESOLVE-05: the media types and `Accept` matching of
  DIDP-02, and the DID 1.1 projection of DIDP-01;
- chapter 11: the `A2AInterface` service type (OPEN-4), the TABLE-04 entry for
  `typ` `sage-a2a-card+jws`, and the TABLE-07 code `representation.unsupported`.

Chapters 03, 05 and 08 are not amended: the SAGE binding uses their envelopes,
covered components and media type as they are.

## Open decisions

- **OPEN-1, URIs.** The SAGE binding and the SAGE extension each need a stable
  URI owned by the project. A2A treats these URIs as identifiers that need not be
  fetched. The values are chosen at adoption.
- **OPEN-2, default projection.** The absent-`accept` default stays DID Core 1.0
  to keep existing consumers working. Moving it to DID 1.1 is reconsidered when
  DID 1.1 becomes a W3C Recommendation.
- **OPEN-3, `did:sage` registration.** The method is not in the W3C DID
  Extensions list. Registration is a public pull request against
  `w3c/did-extensions` and needs the maintainers' approval after adoption. The
  W3C list currently states DID Core 1.0 method requirements.
- **OPEN-4, service type.** Chapter 09 services carry a free `type`. Reserving
  `A2AInterface` needs a chapter 11 table entry under TABLE-01.
- **OPEN-5, card lifetime.** A2AB-03 caps a card at 86400 seconds so that a
  static card file can be served and cached. Chapter 07 caps the SAGE card at
  300 seconds. The A2A cap is a proposed value to confirm at adoption. Any
  record change, including an operator grant or revocation, also invalidates
  every card of that agent.

## Boundary with the separate DID project (informative)

This section is informative. It records what exists outside this repository and
what was compared; it adds no requirement and changes none. The A2AB and DIDP
rules above are the only proposed rules, and they stay unadopted.

### What exists now

The separate DID project is
[`SAGE-X-project/did-go`](https://github.com/SAGE-X-project/did-go), a Go
library under the Apache License 2.0, reviewed at `main` commit
`bfaee58170b4e90f6099b88e391cc7b35abc664e` (2026-10-12). Its conformance is
checked by a separate repository,
[`SAGE-X-project/did-inspector`](https://github.com/SAGE-X-project/did-inspector),
reviewed at `main` commit `0b0e7628f2844685e6fc8ad9d325ea35cfe73c5b`. The
[basis](basis.json) pins both revisions and the digests of the inspector
reports cited below.

- **Standard core.** did-go implements DID Core 1.0 and DID 1.1 in one superset
  core, Controlled Identifiers 1.0, DID Resolution v1.0 (Candidate
  Recommendation Draft 2026-10-01) with a resolver, a DID URL dereferencer and
  the HTTPS binding, the `did:key` and `did:web` methods, a controller and a
  relying party. Its documents `docs/12-standard-core-and-sage-extension.md`
  and `docs/14-implementation-architecture.md` state the rule that standard
  behavior comes first and that SAGE support is an opt-in extension that can
  only be stricter than the standards.
- **No SAGE dependency.** The root module `go.mod` has no `require` entry, and
  no package in it imports SAGE. Resolution of `did:sage`, freshness, key
  selection and every protected-operation decision stay in the SAGE cores under
  chapters 06, 09 and 10. A SAGE core may use did-go's syntax and data model
  packages to emit the DIDP-01 projections. did-go's `docs/12` section 4 states
  the same trust boundary as DIDP-04: a general-purpose resolver never becomes
  the source of key authority for a SAGE-protected operation.
- **`advanced/sage` waits for adoption.** did-go designs an `advanced/sage`
  module with its own `go.mod`: a `did:sage` driver that wraps a SAGE core for
  external DID consumers, the DIDP-01 projections, a stricter consumption
  profile and the DIDP-05 error mapping. The directory does not exist at the
  reviewed revision, and did-go `docs/12` section 9 says it is not implemented
  before this proposal is adopted. DIDP-05 therefore has no implementation yet;
  it is to be implemented by `advanced/sage`.
- **Inspector evidence.** The did-inspector reports
  `docs/evidence/didgo-did-core-1.0.json` and `docs/evidence/didgo-did-1.1.json`
  inspect did-go `bfaee58`. At requirement level the DID Core 1.0 profile has
  114 PASS and 0 FAIL of 172 statements (1 NOT_APPLICABLE, 57 NOT_RUN), and the
  DID 1.1 profile, which also covers Controlled Identifiers 1.0 and DID
  Resolution, has 307 PASS and 0 FAIL of 436 (3 NOT_APPLICABLE, 126 NOT_RUN).
  Each profile has one recommendation-level FAIL, on the producer writing terms
  that the `@context` does not define; did-go records both as the accepted
  deviation T10 in `docs/08-verification-report.md`. The reports state that
  they are evidence for one run and not a certification. They say nothing about
  `did:sage`, the A2AB rules or any SAGE core.

### Cross-check of DIDP-01, DIDP-02 and DIDP-05 against did-go

On 2026-10-12 the DIDP-01 projections and the DIDP-05 mapping were compared
with did-go `bfaee58`, by reading its source and by a temporary Go program
that is not delivered with this proposal. The program built both projections
of one `did:sage:web` record (an Ed25519 signing key, an X25519 key and one
`A2AInterface` service), consumed them with did-go's consumer in strict mode,
and resolved them through did-go's `DefaultResolver`, dereferencer and HTTPS
handler with a stub `sage` driver. The two inspector reports were regenerated
locally from did-inspector `0b0e762` and matched the committed reports except
for the recorded inspector revision. None of this executes a planned case;
every case stays `NOT_RUN`.

Observations that agree with the proposal:

| Rule | Observation in did-go `bfaee58` |
|---|---|
| DIDP-01 | The DID 1.1 projection (string `@context` `https://www.w3.org/ns/did/v1.1`, `JsonWebKey`, JWK without `alg` or `kid`) labelled `application/did` is accepted as DID 1.1 JSON-LD with no dropped term. `vm/jwk.go` requires only `kty` and, for EC and OKP keys, `crv`. |
| DIDP-01 | The DID Core 1.0 projection (no `@context`, `JsonWebKey2020`) labelled `application/did+json` is accepted as DID Core 1.0 JSON. |
| DIDP-01 | `jsonld/contexts/did-v1.1.jsonld` has SHA-256 `ea216ecc1cb02cd39b693dba2250141e270ba0bf95890be107dd9a9e8e43de85`, the value pinned for `did-1.1-context` in the basis; did-go embeds it and never fetches a context. |
| DIDP-02 | Media types `application/did` and `application/did+json` are the constants in `spec/profile.go`. A DID 1.1 projection labelled `application/did+json`, and a `v1` context under `application/did`, are both rejected in strict mode, so a consumer detects a mislabelled projection. |
| DIDP-05 | Problem `type` URLs are `https://www.w3.org/ns/did#` plus the code (`resolution/errors.go`). The statuses match DID Resolution §12.1 as read in the pinned draft: `INVALID_DID` 400, `INVALID_OPTIONS` 400, `NOT_FOUND` 404, `INTERNAL_ERROR` 500, `METHOD_NOT_SUPPORTED` 501, `FEATURE_NOT_SUPPORTED` 501. |
| DIDP-05 | An unsatisfiable `accept` gives `FEATURE_NOT_SUPPORTED` (501), the same reading of DID Resolution §4.4 that DIDP-05 uses (did-go `docs/12` section 6.2, step 4). |
| DIDP-05 | A deactivated result has no document and `deactivated` `true`; the HTTPS binding answers 410 with `didDocument` null. A missing key fragment dereferences to `NOT_FOUND` (404). A driver's not-found error gives `NOT_FOUND`; any other driver failure gives `INTERNAL_ERROR`, never `NOT_FOUND`. |

### Open items from the cross-check

These items are recorded, not resolved. Neither the proposal nor did-go was
changed because of them. They are for the external review and for adoption.

- **DG-1, empty verification relationships.** Chapter 10 RESOLVE-01, which the
  DID Core 1.0 projection copies exactly, projects a `created` or
  `deactivated` record with empty verification method and relationship arrays,
  and DIDP-01 and DIDP-05 keep that shape. DID Core 1.0 §5.3 and Controlled
  Identifiers 1.0 §2.3 say each relationship property is optional and, if
  present, MUST be a set of one or more verification methods. did-go rejects
  such a document in both projections (`INVALID_CONTROLLED_IDENTIFIER_DOCUMENT`,
  statements `cid10#authentication.2` and `cid10#key-agreement.2`); an empty
  `verificationMethod` array with the relationship members left out is
  accepted. The same applies to any record whose relationship has no member.
  The rule is in the normative chapter, so a fix needs an amendment of
  RESOLVE-01 at adoption. Cases `didp-03-deactivated` and the DIDP-05
  `created` statement are affected.
- **DG-2, the `sageCode` member.** did-go's `resolution.Error` models only
  `type`, `title`, `status`, `detail` and `instance`, and `DefaultResolver`
  replaces a driver error with a new error: the not-found, unsupported,
  invalid-input and invalid-document sentinels map to fixed codes, and any
  other error becomes `INTERNAL_ERROR` with a fixed detail. A `did:sage` driver
  plugged into the standard resolver therefore cannot emit `sageCode`. A
  malformed identifier such as a mixed-case method is refused as `INVALID_DID`
  before any driver runs. Either did-go gains an extension point for problem
  extension members, or `advanced/sage` fronts the standard resolver, or DIDP-05
  drops `sageCode`.
- **DG-3, codes no driver can produce.** DIDP-05 maps `id.unknown-kind` to
  `METHOD_NOT_SUPPORTED` and `version.unsupported` to `INVALID_OPTIONS`. Through
  `DefaultResolver` a driver's unsupported error becomes `FEATURE_NOT_SUPPORTED`
  and any other error `INTERNAL_ERROR`; a driver-returned
  `METHOD_NOT_SUPPORTED` was observed as `INTERNAL_ERROR`. The mapping is
  reachable only if `advanced/sage` does not rely on the standard resolver's
  error mapping, or did-go adds a way for a driver to return a DID Resolution
  error.
- **DG-4, scope of DIDP-02 on the DID Resolution interface.** DIDP-02 amends
  the SAGE resolver and its chapter 10 binding. It does not say whether its
  table also binds the DIDP-05 component. did-go's standard resolver matches
  `accept` with RFC 9110 ranges and q-values and transcodes, so a stub `sage`
  driver was served as `application/did+ld+json` (a JSON-LD document with the
  `v1` context and `JsonWebKey2020`) and a q-value list was accepted. Its HTTPS
  binding answers an absent `Accept`, `*/*` and `application/did-resolution`
  with the complete resolution result, where DIDP-02 returns the bare DID Core
  1.0 projection or rejects. did-go `docs/12` section 6.2 reads DIDP-02 as
  binding `advanced/sage` (exact single type, no q-values, no transcoding), but
  the resolver offers no such profile option today; its producer and consumer
  are injectable. Case `didp-05-unsupported-accept` depends on this answer.
- **DG-5, where the DID 1.1 projection is produced.** DIDP-01 changes the
  verification method type between projections, so the DID 1.1 projection is
  not a re-serialization of the DID Core 1.0 document. A `did:sage` driver must
  offer both media types itself, as the stub driver did; this matches the
  planned `advanced/sage` projection file and needs no rule change.

## Compatibility and planned evidence

Old and new rules (PROC-02): chapter 07's SAGE card and chapter 10's DID Core
1.0 projection are unchanged; existing `application/did+json` and
`application/json` resolution requests return what they return today. New rules
are the SAGE binding, the A2A extension, the card shape and identity binding,
interface eligibility, the DID 1.1 projection, `Accept` matching and the DID
Resolution error mapping. Affected implementations are the Go and Rust cores
(projection and card verification), `sage-adk` (A2A client and server hosts)
and the planned `advanced/sage` module of did-go. No existing vector changes
meaning.

The [case plan](cases.json) lists positive and negative cases for every rule
group, and the [document checker](verify.py) checks traceability only. Inspector
observations, independent A2A and DID consumers and runtime evidence are
`NOT_RUN`.
