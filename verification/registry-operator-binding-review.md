# Registry operator and storage binding review

This review uses the adopted 0.10.0 specification at
`dcdd028b5160de5e32eb1f43cf1f71eed3fc4744`, Go core at
`8038e1906f9b7595a0589584fdc707fd3f9e2ce1`, and the Registry service at
`431ad432bd5658f7b4911414426cb6fa4374f52e`. It records the next
REG-03/REG-08 design decision; it does not amend the normative contract or
claim a deployed Registry binding.

## Finding

[REG-03](../spec/09-registry.md)
requires each successful mutation to increment the record version once and
names controller-authorized, scoped `authorize/revoke operator` operations.
The public record has exactly six members and deliberately excludes operator
management data. REG-08 leaves the administrative API to the deployment, but
still requires atomic enforcement of REG-03 and retained tombstones.

The Go core's `WebRegistryAdminAuthority010.Delegated` accepts the controller,
actor, DID, operation, and expected version. `ApplyWebRegistryWrite010` checks
that authority while the local journal's writer lock is held. The journal's
complete persisted state contains the envelope, mutation history, and
tombstone, but no operator grants. Its transition checker accepts `activate`,
`add-key`, `revoke-key`, `update-services`, and `deactivate`; it rejects
`authorize-operator` and `revoke-operator`. The Registry service maps verified
client-certificate fingerprints to actors and deliberately denies all
delegated writes. Inspector's six local service-storage conditions therefore
demonstrate controller writes and public reads, not delegated authority or
deployed storage ownership.

The pinned evidence is the Go
[authority interface and admission check](https://github.com/SAGE-X-project/sage/blob/8038e1906f9b7595a0589584fdc707fd3f9e2ce1/pkg/agent/registry010/web_write_admission010.go),
[transaction state](https://github.com/SAGE-X-project/sage/blob/8038e1906f9b7595a0589584fdc707fd3f9e2ce1/pkg/agent/registry010/web_write_transaction010.go),
[transition checker](https://github.com/SAGE-X-project/sage/blob/8038e1906f9b7595a0589584fdc707fd3f9e2ce1/pkg/agent/registry010/web_transition010.go),
the service's [controller-only binding](https://github.com/SAGE-X-project/sage-registry-service/blob/431ad432bd5658f7b4911414426cb6fa4374f52e/registry/server.go),
and Inspector's [local observation](https://github.com/SAGE-X-project/sage-inspector/blob/633b620eaacbb87d15cbb5e282e1c9ec83ccd0c7/docs/reconciled-spec-inventory.md).

Consequently, putting a mutable grant map beside the journal would not by
itself satisfy the specification: the grant decision, record version, public
envelope, mutation history, and tombstone could disagree after a concurrent
write or restart. Treating the configured certificate-to-actor mapping as a
grant would also let deployment configuration silently replace a
controller-authorized management decision.

## Decision required before implementation

Define a versioned management-plane grant state and its deployment binding.
The normative revision should answer all of these together:

1. Specify the exact controller-authenticated command for grant and revoke,
   including operator identifier, DID, operation scope, expected record
   version, and whether an existing grant may be replaced. State which record
   lifecycle states permit each command. Creation, grant, and revoke must
   never be delegable to an operator.
2. Specify how a successful management-only command increments the public
   record version while leaving its controller, keys, services, and lifecycle
   state unchanged. Define its history entry and distinguish it from an
   ordinary `update-services` mutation that happens to submit identical
   services. The public record need not expose management credentials.
3. Require one linearizable commit for the authenticated command, grant
   state, next version, complete record, mutation history, and tombstone.
   Authority lookup must read the same committed version as the candidate
   compare-and-swap. A failed command or uncertain commit must not authorize
   a subsequent write; recovery must prove which version committed before
   the store resumes.
4. Define exact scope matching, revocation effect, and restart behavior.
   A grant cannot authorize another operation, controller change, further
   delegation, or a stale-version write. Revocation must be effective at the
   next authorization decision; historical evidence must not recreate a
   revoked grant. No credential or public record field may authorize itself.
5. Pin the deployment's trusted storage owner, clock, credential issuer and
   certificate-to-actor binding. For a live REG-08 claim, identify the public
   HTTPS origin and demonstrate that its response comes from the same
   committed state used by authenticated writes. Local test fixtures alone
   cannot establish that ownership.

The first four items are a specification and implementation contract, not
permission to choose a hidden wire format in either core. If the profile
intends operator grant changes to avoid a public version increment, REG-03's
“each successful atomic mutation” rule needs an explicit, reviewed exception
instead. That alternative cannot be assumed by the service or Inspector.

The [operator transaction candidate](../proposals/registry-operator-transaction/README.md)
chooses one versioned, atomic management state and enumerates the decisions
and refusal cases for a later coordinated normative adoption. It is a
proposal, not a current 0.10.0 implementation or conformance result.

## Verification sequence

After the specification fixes the command and transaction model, implement
the same state transition in the Go and Rust cores. Bind it to a durable
Registry service transaction, then add Inspector cases with independent
expected outcomes. At minimum, check controller grant and revoke, one
in-scope operator write, out-of-scope and operator-issued grant refusal,
stale expected version, competing grant/write and revoke/write, restart
recovery, and unchanged public state after every refusal. Use unit scenarios
and bounded TLS runtime tests. Preserve the earlier local service report and
its `NOT_ESTABLISHED` conformance verdict; only a separately pinned deployed
origin and storage observer can close that boundary.
