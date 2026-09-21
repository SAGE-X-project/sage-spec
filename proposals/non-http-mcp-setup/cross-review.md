# Separate-agent review and correction record

Status: **FINDINGS_RESOLVED_IN_CANDIDATE**. This review was explicitly authorized by the
user and performed by two separate agents on the same machine. It is not a third-party
external audit. Adoption remains PROPOSAL_NOT_ADOPTED; external audit NOT_PERFORMED;
71 parent protocol cases and 37 historical lifecycle cases remain NOT_RUN.

## Reviewed inputs and method

Original candidate revision: `bf9e1b3e44f8d5a7123248fb7cf82b8f9407e739`.
The input bundle contained 62 hash-identified files, including the candidate, effective
plan, selected pinned Go/Rust core code, Inspector review and preserved unpublished
baseline. Its archive SHA-256 was
`ddd4d448f7dc8b4b12b6e31b35532ccb984be0cafc13930dc986a243b01bbe13`.
Reviewers read those inputs independently of the authoring conversation. They did not
edit source files, execute protocol scenarios, or adopt the proposal. Their findings
were reconciled by the author, corrected, then returned to both reviewers.

- `/root/contract_review`: contract logic and trust-boundary review.
- `/root/implementation_review`: Go/Rust feasibility and acceptance coverage review.

Both found the fence-to-queue architecture feasible in principle. Neither reported a
demonstrated new exploitable core vulnerability. This is a bounded design review, not
proof that no other defects exist. Severity below concerns adoption readiness.

## Findings and corrections

| Finding | Severity | Original location | Correction |
|---|---|---|---|
| CR-01: queue insertion needs explicit baseline dispatch mapping | Medium | candidate 444–453, 508–516; EXEC-04/05 | State that insertion is dispatch; distinguish later effect and add before/after-expiry schedules |
| CR-02: finite provider bounds do not bound queue waiting | Medium | candidate 326, 508–516, 550–556 | Require finite scheduler claim-or-safe-cancel bound; retain occupied slots on unexpected failure |
| CR-03: central final-admission checks lack explicit schedules | Medium | candidate 478–525, 547–556; REG-05 | Add generation, freshness, atomic queue failure and shared-owner child assertions |
| IR-01: missing critical generation/freshness/capacity/isolation schedules | High | candidate 478–525; effective plan | Require separate policy/component/session races, 4999/5000/5001-ms observations, pre-operation observation denial and owner isolation |
| IR-02: failed/uncertain storage and recovery outcomes omitted | High | candidate 493–496, 535–568 | Add fence success/failure/uncertainty, failed UNKNOWN and failed recovery persistence; global reconnect-safe occupancy bounds |
| IR-03: 1024-ID authenticated runtime exceeds record ceiling | Medium | madd-history-capacity; SESSION 1000-record limit | Split owner-only 1024-entry unit test from real session exhaustion with control records counted |
| IR-04: administrative replacement of queued work is ambiguous | Medium | candidate 508–516, 542–545; EXEC-06 | Require cancellation of unclaimed old-generation work on approved administrative invalidation; separately order worker claim and retain original instance for running work |

CR and IR entries overlap intentionally: they preserve the two reviewers' findings,
not seven unrelated defects or seven completed protocol scenarios. Original line
references refer to the pinned review input, not regenerated output line numbers.

The [hash-pinned amendment](cross-review-amendment.json) supplies the corrected text,
history-case override and 26 mandatory child assertions. They attach to existing
parents; the catalog still contains 71 top-level cases. Children remain NOT_RUN and
must actually be observed before their parent passes. A document test confirming
that a child is listed is not execution of that child.

The earlier 8/10/53 impact classification is historical to the pre-cross-review input.
It must not be presented as the final number of unchanged assertions after the history
correction and child schedules. The original input manifest and historical case files
are unchanged; generation applies the separately pinned amendment explicitly.

## Re-review and remaining adoption work

Both separate reviewers re-read the corrected outputs. `/root/contract_review` closed
CR-01..03 and `/root/implementation_review` closed IR-01..04 at the candidate-definition
and acceptance-plan level. Neither identified an introduced inconsistency requiring
another correction. This disposition applies to the exact bytes below:

| Artifact | SHA-256 |
|---|---|
| integrated-candidate.md | `ea9a3c15f64cf7a69a246fd634b9efa282fe470b8b2677f0000552ab4c659e5e` |
| integrated-cases.json | `32147552d029306c4c8f041e34899141d0b29817040c4a3f17db0e81f65a1a09` |
| cross-review-amendment.json | `7a90b485205c83b2d2784829ee1c3479c64bf2c43f09a2c7e362f61e50589bdd` |

Even closure of these design findings does not update the unpublished baseline or grant
protocol conformance. Normative profile/compatibility/traceability reconciliation and
explicit adoption remain necessary before the implementation claim.

Validation of this change covers generated-document consistency, complete child/parent
membership and bounded local generator CLI behavior. No new core code, authenticated
runtime case or deployment/host enforcement test is executed by that validation.
