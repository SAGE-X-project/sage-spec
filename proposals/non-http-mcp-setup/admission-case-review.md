# Admission amendment case review

Status: **CANDIDATE_AMENDMENT_NOT_ADOPTED**. Same-author review of the candidate at
`37027c7e91b817e437d197b73b7332bb889ffd66`; external review remains NOT_PERFORMED.
This review completes the admission-definition impact assessment, not independent
security approval, normative adoption or implementation.

The [impact matrix](admission-case-impact.json) accounts for every existing case once:
**8 admission assertions to redefine, 10 observations to strengthen, 53 cases with no
direct change identified in this narrow review**. All 71 remain NOT_RUN. The three
original case files are preserved, and no supplemental prose is counted as an executed
case. Input hashes identify the exact reviewed candidate and historical plans.

## Assessment

The durable-fence/queue-admission distinction is a coherent candidate for the existing
cores: it preserves conservative restart behavior while allowing owner close to win
during storage or verification. It explicitly supersedes the proposed interpretation
that EXECUTING is admission; it cannot be layered on top of that interpretation as if
nothing changed. The existing finite owner model is not evidence for this candidate.

Eight affected assertions are the four DREV-01 close/crash cases, two protected timeout
cases and the two addendum handoff-order cases. Each needs observable queue insertion,
not merely an EXECUTING journal row. The crash case must distinguish fence-only from
admitted-but-not-effected traces even though both recover conservatively as UNKNOWN.
For a fence-write/close race, record close before releasing the paused write and verify
zero queue admissions, rather than infer order from eventual function return times.

The ten observation changes in the matrix cover retained bytes, callback identity,
queue recovery, bounded cancellation, expiry and cross-language execution. The other
53 assertions remain relevant to the historical proposal, but this review does not
claim that their implementation or broader semantics have been verified.

## Two clarifications applied to the candidate

1. **Pre-admission expiry is distinct from post-admission expiry.** The candidate's
   acceptance-table phrase “no effect at or after the applicable boundary” is too broad
   if read to forbid completion of a previously admitted task. Its persistence-crossing
   scenario must say: when the deadline is reached before queue insertion, observe zero
   admissions and zero effects. For an insertion that already won, apply post-admission
   closure/cancellation semantics and never claim rollback. This also affects the old
   bounded-cancellation assertion, whose unqualified “no effects” must be split by order.
2. **Bounded occupancy is not bounded termination.** The candidate's occupied-slot rule
   prevents unbounded accumulation when cancellation cannot stop a provider. It does not
   prove finite cleanup time or availability. Adoption must require a trusted provider
   with a finite completion/cancellation bound for any bounded-cleanup claim. A provider
   unable to meet that contract is unsupported; retaining a slot and denying new work
   is fail-closed degradation, not proof that resource cleanup completed.

Both clarifications are applied to admission-close-contract.md in this change. The
matrix hashes identify the prior reviewed inputs at the pinned revision, not the
subsequently corrected candidate file. Historical plans and the consolidated draft
remain unchanged. The corrected candidate is still unadopted.

## Evidence and adoption gate

Actual implementation tests must observe durable fence success, owner-close ordering,
private queue admission, worker claim/effect and durable terminal as separate events.
A synthetic timestamp supplied by the adapter is insufficient evidence of lock order.
Use deterministic trusted pause/release seams with bounded timeouts, plus safe local
runtime processes. Authority observations must be fresh and bound to the exact operation;
queue insertion must not call arbitrary extension code under the coordinator.

Before adoption, integrate the corrected candidate and have an independent reviewer
assess the changed definition and trust boundary. Record exact
inputs, reviewer identity, findings and disposition. Reconcile the unpublished normative
baseline and update the profile, compatibility record and traceability together. This
same-author review is not that independent decision.

After adoption, implement the same owner/gate contract in Go and Rust, then execute the
71 protocol scenarios in Inspector. Promote individual cases only on complete evidence;
37 historical lifecycle NOT_RUN and conformance NOT_ESTABLISHED remain separate.
