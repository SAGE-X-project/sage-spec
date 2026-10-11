# Counterexample review record

The first draft of this proposal was reviewed on 2026-10-11 in a separate pass
by the same authoring agent, acting as an adversarial reviewer with access to
the SAGE chapters and the pinned external texts. This is not an independent
external review. The review checked every external claim against the
downloaded sources, looked for downgrade and bypass paths, and checked the case
plan and checker. The draft was then revised; the table records each finding
and where it is resolved. External review remains required before adoption.

| Finding | Severity | Resolution in this revision |
|---|---|---|
| Carrying A2A traffic on chapters 03, 05 and 08 "without change" was impossible: MSG-02 fixes the covered list and media type, assumes a JSON body, and TRANSPORT-03 allows no streaming | HIGH | A2AB-01 defines a custom A2A binding that carries one JSON-RPC message inside the chapter 08 envelope and the A2A service parameters in signed `metadata`; streaming methods are refused. Chapters 03, 05 and 08 are not amended. |
| A server could run the same agent's operations on an unprotected interface or as A2A 0.3 | HIGH | A2AB-04 requires a card with the SAGE extension to list only SAGE-binding interfaces and the server to refuse every other binding and version. |
| DIDP-02 contradicted chapter 10 media types and broke `application/json` callers | HIGH | DIDP-02 now amends RESOLVE-03 and RESOLVE-05 explicitly, keeps `application/json` and defines `Accept` matching for wildcards, lists and q-values. |
| Card parsing left duplicate, unknown and null members and size open | MEDIUM | A2AB-04 bounds size and rejects them; A2AB-05 canonicalizes the parsed object that is exposed. |
| Unprotected JWS header and multiple signatures were unconstrained | MEDIUM | A2AB-05 requires exactly one SAGE signature with no unprotected header and a fixed protected member set. |
| Expected peer, card lifetime and services matching were weaker than chapter 07 | MEDIUM | A2AB-05 makes the expected-peer comparison a MUST and adds `issued`/`expires`; A2AB-06 binds interfaces to registry services; the residual substitution risk without configuration is stated. |
| Extended card could replace the verified card | MEDIUM | A2AB-04 requires `extendedAgentCard` absent or false and refuses `GetExtendedAgentCard`. |
| Extension cardinality and `params` types were open | MEDIUM | A2AB-03 requires exactly one entry and fixes member types and `sageVersion`. |
| JOSE verification profile was unstated (high-S P-256) | MEDIUM | A2AB-05 applies chapter 01 CRYPTO-02 and requires low-S signing. |
| DIDP-05 mapping was incomplete and its problem type ambiguous | MEDIUM | DIDP-05 adds `key.not-in-record`, emits the DID Resolution type with `sageCode`, uses DID Resolution statuses, and uses `FEATURE_NOT_SUPPORTED` for an unsupported `accept`. |
| The checker counted only negative cases, exempted DIDP-03 and accepted duplicate headings | MEDIUM | `verify.py` requires a positive and a negative case for every rule and unique headings; CI checks that `spec/` matches the reviewed revision. |
| Missing negative cases for JWS headers, kids, card bodies, URL variants, versions, recipient, tenant, response signer, downgrade and `Accept` matching | MEDIUM | Added to `cases.json` (90 planned cases). |
| Context digest wording, CID wording, DID Resolution RFC 9457 strength, untestable DIDP-01 case, conditional response coverage, tenant routing, `typ` domain separation, card churn, ID-03 list, version header details | LOW | Each is corrected in the text or recorded under "Amendments required at adoption" and OPEN-5. |
