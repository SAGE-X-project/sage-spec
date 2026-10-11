# External review guide: A2A 1.0 binding and DID 1.0/1.1 projections

Status of the reviewed text: **proposed design, not adopted**. Every planned case
is `NOT_RUN`. This guide adds no rule. Where it gives a recommendation, the
recommendation is the authors' suggestion for the reviewers to accept or reject;
it is not a decision.

## 1. Why this guide exists

The [proposal](README.md) defines how SAGE would protect A2A 1.0 traffic and how
a SAGE resolver would present a record as a DID Core 1.0 document and as a DID
1.1 document. Before adoption it needs a review by people who did not write it.
The only review so far was a counterexample pass by the authoring agent itself
([review.md](review.md)), which is not independent. This guide tells an external
reviewer what to review, which exact texts the proposal was written against, how
to run the document checker, what evidence exists, and which decisions are still
open.

## 2. What is under review and what is not

Under review are the proposed rules and their reasoning:

- **A2AB-01 to A2AB-07**: the SAGE protocol binding for A2A 1.0, the version and
  extension rules, the card shape, the binding between a card signature and a
  `did:sage` record, interface eligibility and the no-downgrade rule;
- **DIDP-01 to DIDP-05**: the two DID projections, how a caller selects one,
  their equivalence, the rule that a DID document is never key authority, and
  the error mapping through the DID Resolution interface;
- the "Amendments required at adoption" list, which names every place in the
  normative chapters that adoption would change;
- the five open decisions (OPEN-1 to OPEN-5) and the cross-check items DG-1 to
  DG-5 recorded in the README.

Not under review, and not requested from reviewers:

- **Adoption.** A review finding does not adopt the proposal, and a clean review
  does not either. Adoption is a separate project decision that also amends
  chapters 06, 10 and 11 and is recorded under PROCESS.md.
- **Implementation.** No SAGE core, `sage-adk` or did-go `advanced/sage` code
  implements these rules. Do not report "not implemented" as a finding.
- **The current normative chapters** (`spec/`, `profiles/`, `charter.md`) as a
  whole. They are cited, and a finding may show that a chapter rule conflicts
  with a standard (DG-1 is such a case), but changing them is outside this
  proposal. A CI step fails if those paths differ from the pinned normative
  revision.
- **Security proofs and interoperability claims.** The proposal claims neither.

## 3. The pinned basis

[basis.json](basis.json) pins everything the text depends on.

- SAGE normative revision `1820ab5eafb843e1c13f4c46c34aeeb28d934ac9` and branch
  base `f97378cde7f29006520299c4246d2a50a429545f`.
- External documents with the SHA-256 of the bytes served on 2026-10-11: A2A
  `v1.0.1` (`specification.md` and `a2a.proto`), DID Core 1.0 (W3C
  Recommendation), DID 1.1 (Candidate Recommendation Snapshot 2026-03-05) and
  its `v1.1` context, DID Resolution v1.0 (Candidate Recommendation Draft
  2026-10-01), Controlled Identifiers 1.0, RFC 8785, RFC 7515, RFC 9864 and RFC
  9457. A W3C page can gain a status banner later; a changed hash means the
  citation must be checked again, not that the text changed.
- Related projects, informative only: did-go at
  `bfaee58170b4e90f6099b88e391cc7b35abc664e` and did-inspector at
  `0b0e7628f2844685e6fc8ad9d325ea35cfe73c5b`, with the digests and totals of
  the two inspector reports.

Please cite these exact revisions in findings. A finding against a newer draft
of DID 1.1 or DID Resolution is welcome, but say which revision you read,
because the proposal reopens when the pinned revision changes.

## 4. Running the document checker

From the repository root, with Python 3 and no extra packages:

```sh
python3 -B proposals/a2a-did-interop/verify.py --self-test
python3 -B proposals/a2a-did-interop/verify.py
base="$(python3 -c "import json; print(json.load(open('proposals/a2a-did-interop/basis.json'))['sage_baseline']['normative_source_revision'])")"
git diff --quiet "$base" HEAD -- spec/ profiles/ charter.md && echo unchanged
```

The second command prints `{"status": "PROPOSAL_NOT_ADOPTED", "cases": 90,
"execution": "NOT_RUN"}`. The checker reads the README, the case plan, the basis
and this guide. It checks that the status is still a proposal, that every source
and related project is pinned, that every rule group has at least three planned
cases including a positive and a negative one, that this guide marks its
recommendations and cites the pinned revisions, and that no em dash appears. It
runs no A2A exchange, no DID resolution and no cryptography. A passing checker
means the documents are consistent with each other, not that the rules are
right.

## 5. Review already done

[review.md](review.md) records thirteen findings from the authoring agent's own
adversarial pass on 2026-10-11 (three HIGH, nine MEDIUM, one group of LOW
items) and where each is resolved. The largest changes were the custom A2A
binding that carries JSON-RPC inside the chapter 08 envelope, the rule that a
card with the SAGE extension lists only SAGE-binding interfaces, and the
explicit amendment of chapter 10 media types. Reviewers should check whether
those resolutions actually close the problems, not only read the table.

## 6. Evidence available

There is no evidence that any planned case passes. What exists is evidence
about the separate DID library, and a cross-check of three DIDP rules against it.

- **did-go** (`bfaee58`, Apache-2.0) implements DID Core 1.0 and DID 1.1 in one
  superset core, Controlled Identifiers 1.0, DID Resolution with a resolver,
  dereferencer and HTTPS binding, `did:key`, `did:web`, a controller and a
  relying party. Its root module has no dependency on SAGE. The `advanced/sage`
  module that would carry the `did:sage` driver and the DIDP-05 mapping is
  designed in its `docs/12` and not implemented until this proposal is adopted.
- **did-inspector** (`0b0e762`) is a separate conformance inspector. Its
  reports `docs/evidence/didgo-did-core-1.0.json` and
  `docs/evidence/didgo-did-1.1.json` inspect did-go `bfaee58`: at requirement
  level 114 PASS and 0 FAIL of 172 statements for DID Core 1.0, and 307 PASS
  and 0 FAIL of 436 for DID 1.1 with Controlled Identifiers and DID Resolution.
  57 and 126 requirement statements are `NOT_RUN`. Each profile has one
  recommendation-level FAIL that did-go accepts as deviation T10 (it writes
  terms the `@context` does not define, because DID Core also says a producer
  MUST serialize every entry). To regenerate:

  ```sh
  cd adapters/didgo   # inside a did-inspector checkout at 0b0e762
  go run ./cmd/did-inspector-didgo --profile did-core-1.0 --deterministic --out core.json
  go run ./cmd/did-inspector-didgo --profile did-1.1 --deterministic --out did11.json
  ```

  A local run on 2026-10-12 matched the committed statements and totals; only
  the recorded inspector revision differed.
- **Cross-check.** The README's boundary section lists what was compared:
  DIDP-01 projections consumed by did-go, the DID 1.1 context digest, media
  types, DID Resolution error type URLs and HTTP statuses, deactivation and key
  dereferencing. Most observations agree with the proposal. The disagreements
  are recorded as DG-1 to DG-5. The program used was temporary and is not
  delivered; a reviewer who wants to repeat it can follow the description in
  the README.

None of this is evidence about `did:sage`, the A2AB rules, the SAGE cores or
interoperability with any A2A implementation.

## 7. Open decisions and recommended answers

Each decision lists the options the authors considered, their advantages and
disadvantages, and a recommendation. Reviewers are asked to accept or reject
each recommendation and to say why.

### OPEN-1: binding and extension URIs

A2AB-01 and A2AB-03 need two stable URIs owned by the project. A2A treats them as
identifiers, and A2A §4.6.3 requires a new URI for a breaking change.

| Option | Advantages | Disadvantages |
|---|---|---|
| (a) HTTPS URIs under `https://sage-x-project.github.io/sage-spec/`, with the exact SAGE version in the path, for example `.../a2a/0.10.0/binding` and `.../a2a/0.10.0/extension` | The project already uses this host for the chapter 10 problem types; the version in the path matches the exact-version rule of PROC-02 and the `/0.10.0/` path of RESOLVE-05; it can serve human-readable guidance | Depends on GitHub Pages and the organisation name; every SAGE version changes both URIs; the version is also in `params.sageVersion`, so the two must be checked to agree |
| (b) A URN such as `urn:sage:a2a:binding` | Never fetched, independent of hosting | `sage` is not a registered URN namespace; A2A examples use HTTPS URIs; nowhere to publish guidance |
| (c) A future project-owned domain | Most stable in the long term | No such domain exists today; adoption would wait for it |

**Recommendation to the reviewers:** option (a), with the exact version in the
path, and a rule that the URI is compared as an exact string and never fetched
while deciding whether a request is protected. Please check whether duplicating
the version in the URI and in `params.sageVersion` creates a case the rules do
not cover.

### OPEN-2: default projection

DIDP-02 returns the DID Core 1.0 projection when `accept` is absent or `*/*`.

| Option | Advantages | Disadvantages |
|---|---|---|
| (a) Keep DID Core 1.0 as the default until DID 1.1 is a W3C Recommendation | Existing `application/did+json` callers see no change; DID Core 1.0 is the only Recommendation | DID 1.1 consumers must ask with `accept`; the default uses `JsonWebKey2020`, a DID extensions type that Controlled Identifiers does not define |
| (b) Make DID 1.1 the default now | Aligns with the newer data model and `JsonWebKey` | Changes the answer existing callers get, which PROC-02 treats as incompatible; DID 1.1 can still change |
| (c) No default: require an explicit media type | No silent choice | Breaks every caller that sends no `Accept` today |

**Recommendation to the reviewers:** option (a), as proposed, and reopen the
question when DID 1.1 becomes a Recommendation and the pinned DID Resolution
revision changes. did-go `docs/12` section 6.5 takes the same position on
re-pinning DID 1.1.

### OPEN-3: registering `did:sage`

The method is not in the W3C DID Extensions list, which applies the DID Core 1.0
method requirements.

| Option | Advantages | Disadvantages |
|---|---|---|
| (a) Submit a registration pull request to `w3c/did-extensions` after adoption | Makes the method discoverable to generic resolvers; registration is not needed for adoption | Needs maintainer approval the project does not control; the method specification must then be kept public and current |
| (b) Wait until DID 1.1 is a Recommendation | Avoids registering against requirements that may change | Delays discovery with no clear gain, because the list applies DID Core 1.0 requirements today |
| (c) Do not register | No external dependency | Generic DID tooling and reviewers will treat the method as unknown |

**Recommendation to the reviewers:** option (a), without making registration a
condition of adoption, and only after DG-1 is resolved. A method whose
documents carry empty verification relationship arrays violates DID Core 1.0
§5.3 and would be hard to defend in the registration review.

### OPEN-4: the `A2AInterface` service type

A2AB-06 requires a registry service of type `A2AInterface` whose URI equals the
card interface URL. Chapter 09 service types are free strings.

| Option | Advantages | Disadvantages |
|---|---|---|
| (a) Reserve the exact string `A2AInterface` in chapter 11 under TABLE-01, as proposed | Short and readable, in the style of other DID service types | A short name can collide with another ecosystem's use; the DID 1.1 `v1.1` context does not define it, so a consumer that performs JSON-LD processing cannot expand it to a defined IRI |
| (b) Use an HTTPS URI as the type, under the OPEN-1 host | No collision; expands as an IRI in JSON-LD | Verbose; unusual among DID service types; one more URI to keep stable |
| (c) Adopt an existing registered service type for A2A, if one exists | Reuses community work | The authors did not find or check one; its semantics would have to match A2AB-06 exactly |

**Recommendation to the reviewers:** option (a), and register the type in the
DID Extensions list together with the method (OPEN-3). Reviewers who know of an
existing A2A service type (option c) are asked to name it with a citation.

### OPEN-5: card lifetime

A2AB-03 caps `expires - issued` at 86400 seconds; chapter 07 caps the SAGE card
at 300 seconds.

| Option | Advantages | Disadvantages |
|---|---|---|
| (a) 86400 seconds, as proposed | A static card file can be served and cached; the signing key need not be online at the card host. Revocation and key changes are still caught, because A2AB-05 resolves the record freshly and requires `recordVersion` to match | Differs from chapter 07; a card stays valid for a day if the record does not change; every record change forces a re-signed card |
| (b) 300 seconds, matching chapter 07 | One lifetime across SAGE | The card must be re-signed every five minutes, which puts a signing key on or near the card host |
| (c) 3600 seconds | A middle ground | Still needs frequent signing, with no protection that the `recordVersion` check does not already give |

**Recommendation to the reviewers:** option (a). The protection against a
revoked or changed key comes from fresh resolution and the `recordVersion`
check, not from the card lifetime. Please test that claim: look for a case in
which a card that is up to one day old, for an unchanged record, lets an
attacker do something a five-minute card would prevent.

## 8. Items from the did-go cross-check

The README records five items found by comparing the proposal with did-go. They
are not decided. Reviewers are asked for an answer to each question.

- **DG-1.** Chapter 10 RESOLVE-01 and DIDP-01 project a `created` or
  `deactivated` record with empty relationship arrays, which DID Core 1.0 §5.3
  and Controlled Identifiers 1.0 §2.3 forbid. Should adoption amend RESOLVE-01
  to omit empty relationship members (did-go accepts that form), and should the
  same apply to any record whose relationship has no member?
- **DG-2.** DIDP-05 carries the SAGE code in a `sageCode` problem member. Is
  that member needed? If it is, should did-go's standard core gain a way to
  carry problem extension members, or should `advanced/sage` front the standard
  resolver?
- **DG-3.** `METHOD_NOT_SUPPORTED` for an unknown registry kind and
  `INVALID_OPTIONS` for `version.unsupported` cannot be produced by a driver
  behind did-go's standard resolver today. Is the mapping right, and if so
  where should it be produced?
- **DG-4.** Does the DIDP-02 table, including the rejection of
  `application/did+ld+json`, q-values and `application/did-resolution`, bind
  the DID Resolution interface of DIDP-05, or only the SAGE interface? The
  answer decides whether a DID Resolution client asking `did:sage` with no
  `Accept` gets the complete resolution result, as the DID Resolution HTTPS
  binding does in did-go, or the bare DID Core 1.0 projection.
- **DG-5.** Needs no rule change; confirm that the DID 1.1 projection must be
  produced by the `did:sage` driver and not by re-serializing the DID Core 1.0
  document.

## 9. Checklist of questions per rule group

**A2AB-01, binding.** Does carrying one JSON-RPC object as the envelope payload
lose any A2A semantics (batch, notifications, `id` handling)? Are the four SAGE
transport errors and the A2A JSON-RPC errors cleanly separated? Is refusing
streaming acceptable for real agents, and is the refusal error the right A2A
code?

**A2AB-02, version.** Is exact `1.0` right when A2A releases `1.0.x` patches and
later `1.1`? Can any path reintroduce the A2A §3.6 rule that an absent version
means 0.3?

**A2AB-03, extension.** Is the closed `params` member set complete? Is the
comma-separated `a2a_extensions` format exactly what A2A specifies, including
spaces and duplicates? Is `required: true` handled by A2A clients as the rule
expects?

**A2AB-04, card shape.** Is any downgrade left when a server also exposes the
agent on a standard binding? Are the size bound and the rejection of unknown
members compatible with A2A clients that add fields? Is the exception for other
extensions' `params` safe?

**A2AB-05, card identity.** Is the JWS profile (closed protected header, `typ`,
no `jku`, `jwk`, `x5u`, `x5c`, `crit` or `b64`) complete? Does canonicalization
per A2A §8.4.1 (protobuf field presence, RFC 8785) give one byte string for
every parser? Is the algorithm mapping (`Ed25519` per RFC 9864, `ES256`, no
`EdDSA`, low-S) correct? Is the residual substitution risk without an expected
peer stated clearly enough?

**A2AB-06, interfaces and recipient.** Is byte-for-byte URL comparison with no
normalization workable for operators? Does the tenant routing rule close
cross-tenant confusion? Do A2A authentication schemes interact with these checks
in any way the rule misses?

**A2AB-07, no downgrade.** Can a client be made to retry on another binding,
version or without the extension by any error, timeout or redirect? Does the
public error leak which check failed?

**DIDP-01, projections.** Are the DID 1.1 differences (string `@context`,
`application/did`, `JsonWebKey`) the only ones needed? Is leaving `alg` out of
the JWK, against the Controlled Identifiers SHOULD, justified? Does DG-1 change
your view of the projection shape?

**DIDP-02, selection.** Is exact media type matching without parameters or
q-values acceptable to generic DID clients? Is the 406 status in the SAGE
binding right? See DG-4 for the DID Resolution interface.

**DIDP-03, equivalence.** Is the list of members that must agree complete? Can a
resolver serve the two projections from different observations through caching?

**DIDP-04, key authority.** Is there any path in which a DID document from a
peer, card, cache or general resolver influences a protected decision? Is
treating `alsoKnownAs`, `equivalentId` and `canonicalId` as having no effect
enough?

**DIDP-05, errors.** Is each SAGE code mapped to the right DID Resolution error
type, and are the statuses the ones in DID Resolution §12.1? Is reporting
`record.stale` as `INTERNAL_ERROR` rather than `NOT_FOUND` correct? Is the
deactivated behavior (null document, `deactivated` true, 410) right? See DG-2
and DG-3.

**Amendments and compatibility.** Is the amendment list complete? Does any
existing vector or caller change meaning?

## 10. How to submit findings

Open an issue or a pull request review on `SAGE-X-project/sage-spec`, with a
title that starts with `a2a-did-interop:`. One finding per issue is easiest to
track. For each finding give:

1. the rule ID (for example `A2AB-05` item 2, or `DIDP-05` table row) or the
   open item (`OPEN-3`, `DG-4`);
2. a severity (HIGH: the rule permits an attack or contradicts a pinned
   standard's MUST; MEDIUM: an ambiguity two implementers could read
   differently; LOW: wording or a missing case);
3. the exact source you rely on: document, revision from the basis, section and
   the quoted sentence;
4. a concrete counterexample: the input, what the proposal says happens, and
   what should happen;
5. a suggested change, if you have one, and its disadvantages.

For each open decision, answer "accept" or "reject" to the recommendation, with
your reason. Findings are recorded in the review record before any adoption
decision, and the proposal text is revised in place under PROC-02 and PROC-03.
Please do not send private keys, credentials or non-public deployment details.
