# Registry operator transaction clarification

Status: **adopted as unreleased 0.10.0 normative design; execution pending**.
The [record](registry-operator-adoption.json) pins the prior chapter and
design graph, the revised chapter and graph, unchanged traceability, and the
[17 planned subconditions](vectors/registry-operator-0.10.0.json). The
[earlier candidate](../proposals/registry-operator-transaction/README.md)
remains a proposal snapshot; [chapter 09](../spec/09-registry.md) is now the
normative source. No implementation, deployed binding, external audit or
conformance verdict is promoted by this document change.

## Rule and compatibility change

The prior REG-03 text named controller-authorized scoped operator changes
without defining their versioned state, public record effect, concurrency or
recovery. A service could therefore authenticate an operator but could not
prove that its grant was in the same committed state as the record write.
The revised chapter keeps the six-member public record and makes each grant
or revoke a management-only mutation that increments its version once. A
grant is an exact `(operator, scope)` pair bound to one Registry, DID and
controller. Only the controller grants or revokes; operators may perform
only the named lifecycle operation. The grant set, record, version, history
and tombstone commit atomically. State transitions retire ineligible grants;
uncertain commits quarantine the source until trusted recovery. The chapter
also states the 128-active-grant bound, restart and public-read obligations,
and the difference between credential authentication and delegation.

This changes previously underspecified accept/reject and persistence
behavior. It is not a wire-format change to protected Agent messages. The
administrative command encoding and deployed storage/credential binding
remain profile-specific and MUST be published before claiming a concrete
Registry conforms. A service that only accepts controllers, including the
current Registry service revision, remains a bounded implementation rather
than evidence of full REG-03/REG-08 conformance. Exact 0.x versions still
require explicit compatibility handling; an implementation cannot silently
claim the amended design from an old revision.

## Historical and verification mapping

The [historical chapter](history/registry-operator-base-2026-10-01/spec/09-registry.md)
and [historical graph](history/registry-operator-base-2026-10-01/analysis/current-design-overlay.json)
retain their original bytes. The earlier REG-08 media correction checks its
own preserved chapter and graph; the new record checks the amended sources.
The 45 requirements, 91 groups, 489 parent cases and 26 existing mandatory
children are unchanged. Existing REG-03 and REG-08 parent IDs own the 17
new subconditions. They are distinct planned observations within those
parents, not 17 extra parent PASS results. A parent cannot pass while an
applicable subcondition is missing or failed. All new subconditions are
`planned_not_executed`; old Inspector reports remain revision-bound.

The subconditions separate successful grant/revoke and exact-scope writes
from duplicate grants, stale versions, unauthorized operators, concurrent
grant/revoke races, uncertain commits, restart history, deactivation and
the public read's old-or-new atomicity. The reference checker verifies
source hashes, old/new clause boundaries, parent mapping and refusal
expectations; it does not execute either core or a Registry deployment.

The next implementation order is Go and Rust transition/storage contracts,
then the Registry service's authenticated command binding and durable grant
state, then Inspector unit and bounded TLS/runtime checks at exact merged
revisions. A deployed REG-08 claim additionally needs its pinned origin,
storage ownership, trusted clock, credential mapping and independent
read/write observer. No such deployment is identified here.

Run the revision controls with:

```sh
python3 -B verification/test_registry_operator_adoption.py
python3 -B verification/check_registry_operator_adoption.py
```
