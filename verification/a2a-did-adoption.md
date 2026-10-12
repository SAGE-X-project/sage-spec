# A2A 1.0 binding and DID projection adoption

Status: **adopted as unreleased 0.10.0 normative design; execution pending**.
The [record](a2a-did-adoption.json) pins the base revision, the preserved
pre-adoption files, the adopted files and the reviewed
[proposal](../proposals/a2a-did-interop/README.md), which remains a historical
snapshot with its own status line. The [A2A 1.0 binding](../profiles/a2a-1.0-binding.md)
and [chapter 10](../spec/10-resolution.md) are now the normative sources. No
implementation, Inspector run, external audit or conformance verdict is
promoted by this document change.

## Why the proposal is adopted now

Stage 7 of the program asked for an exact mapping between SAGE identity, cards
and resolution and the A2A and DID standards. The proposal gave that mapping and
planned 92 cases. On 2026-10-12 the project owner answered the five open
decisions and the five items found by checking the proposal against did-go, by
accepting each recommendation, and asked for adoption on the recommended path.
The answers are recorded in the proposal's [review record](../proposals/a2a-did-interop/review.md).
That review is not independent: the owner took part in the design decisions,
and the only other review was the authoring agent's own counterexample pass. An
independent review can still reopen any rule through the normal process.

## Rule and compatibility change

The A2A rules A2AB-01 to A2AB-07 move into a new profile, because no existing
document owned the A2A protocol binding. The binding and extension URIs are
`https://sage-x-project.github.io/sage-spec/a2a/0.10.0/binding` and
`.../extension`, compared as exact strings and never fetched. The card cap
stays 86400 seconds.

The DID rules DIDP-01 to DIDP-05 join chapter 10, which already owned the
document projection. RESOLVE-03 now reports the media type of the returned
projection, and RESOLVE-05 serves `application/did` beside
`application/did+json` and `application/json`, with the new 406 code
`representation.unsupported`. Chapter 06 ID-03 names the A2A card JWS `kid` as a
key reference. Chapter 11 registers the `sage-a2a-card+jws` type, the new
diagnostic code and, in the new TABLE-08, the `A2AInterface` service type.

RESOLVE-01 changes one behaviour: a verification relationship with no member is
now omitted instead of projected as an empty array. DID Core 1.0 §5.3 and
Controlled Identifiers 1.0 §2.3 allow a relationship to be absent but require a
present one to hold one or more verification methods, so the earlier empty
arrays did not conform. A consumer that requires those members to be present is
affected; one that treats them as optional sees the same keys. No vector covers
chapter 10 resolution, so no vector changes meaning. Exact 0.x versions still
require explicit compatibility handling.

## Verification mapping

The plan grows from 91 rule groups and 489 parents to 104 groups and 583
parents: 92 cases come from the proposal case plan unchanged in identity,
input, precondition and expected outcome, and `TABLE-08-P` and `TABLE-08-N01`
cover the service type. All are `planned_not_executed`. Existing requirements,
rules and cases are unchanged apart from rule line anchors in the amended
chapters and the new rule IDs added to requirement mappings. The 26 mandatory
children and the MCP binding adoption are unchanged.

Earlier revision records pinned the old bytes of the files this adoption
changes. Those bytes are preserved under
[history/a2a-did-base-2026-10-12](history/a2a-did-base-2026-10-12), and the
earlier checkers read them from there; the current-source gate also runs this
adoption's checker, so the adopted files are checked on every run.

## Next work

The implementation order is the did-go `advanced/sage` module (the `did:sage`
driver, both projections and the DID Resolution error mapping), then the Go and
Rust cores (projection, `Accept` selection and card verification), then
`sage-adk` A2A hosts, then Inspector runs at exact merged revisions. Registering
`did:sage` and `A2AInterface` in the W3C DID Extensions list follows adoption
and needs the maintainers' approval.

Run the adoption control with:

```sh
python3 -B verification/test_a2a_did_adoption.py
python3 -B verification/check_a2a_did_adoption.py
```
