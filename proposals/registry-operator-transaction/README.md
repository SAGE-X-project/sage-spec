# Registry operator transaction candidate

Status: **proposed 0.10.0 REG-03/REG-08 correction, not adopted**. The
starting normative revision is `1e63a2d9a52c3d4c694c0404a319f9eff050a209`. This
candidate resolves the questions in the
[operator and storage binding review](../../verification/registry-operator-binding-review.md).
It does not change the current [chapter 09](../../spec/09-registry.md), the
489-case plan, either core, the Registry service, or an Inspector verdict.
The current deployed REG-08 conformance verdict remains `NOT_ESTABLISHED`.

## Scope and state

The Registry has one serialized state per record identifier: the public
six-member record, its monotonically increasing version, lifecycle state,
complete mutation history, terminal tombstone, and a management-plane set of
active grants. A grant is the exact pair `(operator, scope)` under that
record's immutable `(registry, DID, controller)` identity. The operator and
controller are authenticated authorization identifiers of 1–256 ASCII bytes.
They are compared byte for byte; neither case folding nor Unicode
normalization is allowed. A deployment MAY use a narrower identifier syntax
but MUST reject an identifier it cannot map uniquely to one authenticated
principal. An operator MUST differ from the controller.

`scope` is exactly one of `activate`, `add-key`, `revoke-key`,
`update-services`, or `deactivate`. A grant never covers `create`,
`authorize-operator`, `revoke-operator`, controller change, or another
record. Each active grant has one scope; a controller needs a separate
versioned grant command for each additional scope. At most 128 grants may be
active for a record. The complete grant history is retained even when a grant
is revoked or the record is deactivated. A grant is not a DID key, a Card
service, a transport credential, or a transitive authorization token.

## Proposed command semantics

Every accepted command names the target Registry and DID, its exact
operation, and the expected previous record version. A management command
also names the target operator and one scope. The deployment authenticates
the **actor** from its trusted credential binding before the transaction;
actor identity cannot come from the command body, public record, Card, or
claimed operator field. Each deployment binding MUST publish an unambiguous,
bounded command encoding and exact mapping to these semantic fields. REG-08's
administrative HTTP format remains deployment-specific; an unreviewed format
cannot be inferred from this proposal.
The expected version is the canonical decimal string in the current public
record, with no leading zero; creation alone uses an empty expected version.
No alternate encoding, whitespace normalization or missing value is a match.

| Operation | Actor and precondition | Committed effect |
|---|---|---|
| `create` | authenticated controller; identifier unused; expected version empty | version `1`, created record, no active grants |
| `authorize-operator` | authenticated current controller; record `created` or `active`; target grant absent; capacity available | add exactly `(operator, scope)` |
| `revoke-operator` | authenticated current controller; record `created` or `active`; target grant present | remove exactly `(operator, scope)` |
| scoped lifecycle mutation | controller, or operator with the exact active `(actor, operation)` grant; record state permits the operation | apply only the named chapter-09 transition |

In `created`, only `activate` and `deactivate` are valid grant scopes. In
`active`, only `add-key`, `revoke-key`, `update-services`, and `deactivate`
are valid grant scopes. A lifecycle transition that changes the record state
removes grants whose scopes are not valid in the new state in the same commit;
deactivation removes every active grant, including when `revoke-key`
deactivates automatically. The history records those automatic removals
under the triggering mutation without an extra version increment. A
controller may revoke a
grant while it is active; regranting the same pair after revocation requires
a new authenticated command and record version. Granting an already active
pair or revoking an absent pair is invalid and does not increment the version.
The maximum record version cannot be incremented by any command.

Grant and revoke are **management-only record mutations**. On success, the
public record's `version` increments exactly once, while `id`, `controller`,
`keys`, `services`, and `state` remain byte-equivalent after canonical
parsing. The committed history entry identifies the management operation,
target operator and scope; it MUST NOT be indistinguishable from an ordinary
`update-services` operation. The public record does not expose the grant
set or administrative credentials. The web-origin envelope's issuance time
is refreshed from the trusted service clock when serving the committed
record; it does not become a grant timestamp or an alternate authority.

An expired signing key can leave an `active` record unusable for protected
messages. A controller may still revoke an operator or authorize a recovery
operator under the same authenticated management transaction; doing so does
not make the expired record usable. An operator may add a valid proven key
only if its exact `add-key` grant is active and chapter 09 permits that
transition. The next public resolution and protected-message decision must
still enforce key validity. This prevents a management command from silently
turning record version progress into message authority.

## Atomic decision and publication

For each command, the trusted Registry deployment MUST perform these steps
under one linearizable, durable transaction for the identifier:

1. Read the current record, version, grant set, history and tombstone from
   the same committed state. Reject an absent, deactivated or inconsistent
   state except for valid creation. Compare the exact expected version before
   authority or mutation effects.
2. Authenticate the actor and, for a non-controller lifecycle mutation,
   check the exact current grant for that actor and operation. Only the
   controller may authorize or revoke grants. Validate the proposed record,
   lifecycle and key proofs against the current state.
3. Commit the next version, record, grants, history and tombstone together.
   Publish a successful administrative response only after the complete
   state is durable. A public read observes either the complete old state or
   complete new state, never a mixture. A failed decision changes none of
   these committed values.

Two commands with the same expected version cannot both commit. A revoke
that linearizes before an operator write removes its authority; an operator
write that linearizes first may finish, and revocation does not undo that
already committed effect. If the commit outcome is uncertain, the store
MUST quarantine writes and public claims requiring that state until trusted
recovery proves one complete committed version. Restart MUST replay complete
grant history and record history together. If storage ownership, completeness
or monotonicity cannot be established, resume MUST fail closed. This does not
claim protection from a malicious trusted storage administrator or arbitrary
disk rollback; deployed ownership and anti-rollback evidence remain separate
REG-08 gates.
If a caller loses the commit response, it MUST NOT assume the command failed
or replay it with a fabricated newer version; it must inspect the trusted
committed version and history. Exhausted durable capacity refuses further
commands without publishing a partial state. The deployment binding must
provide an authenticated read-only way for an authorized inspector to verify
the version, grant state and ordered command history without
granting that observer write authority.

The actor-to-credential mapping only establishes authentication. Installing
an additional certificate mapping does not create a grant. Revoking a grant
does not itself revoke a transport certificate, and revoking a certificate
cannot substitute for a controller-authorized grant mutation. A deployment
MUST check both credential validity and the current grant at every write.

## Planned Inspector decisions

These are **planned expectations**, not executed results. They would be
mapped into REG-03 and REG-08 traceability in one normative adoption revision.
Every refusal preserves the committed version, grants, record, history and
tombstone; diagnostic responses may be recorded separately.

| Scenario | Expected decision |
|---|---|
| Controller grants one valid scope; operator performs that exact operation | Both commits succeed at consecutive versions; one intended record transition |
| Operator requests another scope, record or controller | Reject; no mutation |
| Operator attempts grant or revoke | Reject; no mutation |
| Controller grants an existing pair, revokes an absent pair, or exceeds 128 active grants | Reject; no mutation |
| Controller revokes one scope while another remains | Only the named scope loses authority |
| Activation retires an `activate` grant; deactivation clears all grants | Removal and record transition share one versioned commit |
| Revoked operator retries; controller later regrants with a fresh version | Retry rejects; new explicit grant can authorize future operations |
| Grant races a write at the same expected version | One commit; the other is stale |
| Revoke races an operator write | Result follows the observed linearization order; never a mixed state |
| Stale, malformed, or ambiguous command | Reject before any committed effect |
| Management command at maximum version or after deactivation | Reject; tombstone persists |
| Active record has expired signing keys | Management alone does not make it usable; proven key recovery remains a separate transition |
| Restart after committed grant or revoke | Exact grant set and record version are recovered together |
| Uncertain write or incomplete history after restart | Quarantine; no public or delegated success claim |
| Public read concurrent with a management commit | Complete old or new version; never a mixed record/grant transaction |

The implementation sequence is normative adoption with an immutable prior
snapshot and case map, then Go and Rust transition and storage contracts,
Registry service binding, and Inspector unit plus bounded TLS/runtime
observations. A live deployment still needs its own pinned origin, storage
owner, clock, credential mapping and independent read/write observer.
