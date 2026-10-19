# Lifecycle and closed-schema refinement

Status: **UNADOPTED future-version candidate**, draft revision 2. This is a
refinement of the earlier proposal at Git `b63b08f81f566ab00d27c89e0cd4c40a4b6f383d`.
It changes no adopted 0.10.0 requirement, frozen report, existing contract or
release. Concrete release/profile/domain selection and adoption remain gates.
The existing four documentary failures and two issuer NOT_RUN remain open.

## 1. Complete lifecycle decision table

At a single admission point obtain the exact authenticated actor, current
credential/config generation, record/version, grants and trusted time. Check
expected predecessor and every argument before any durable change. Success
is one record version plus its complete record/grants/history/tombstone commit.
Failure changes none of those values. All names/material remain immutable
including tombstones; no key or terminal DID is revived.

| Operation | Controller eligibility | Operator eligibility | Complete effect |
|---|---|---|---|
| create | Absent DID; actor equals proposed controller | Never | Version 1, created, initial proven accepted keys and services |
| activate | Created | Current activate grant, created | Active; remove scopes invalid in active |
| add-key | Active | Current add-key grant, active | Append one accepted, proven immutable key; no name/material reuse |
| revoke-key | Created or active | Current revoke-key grant, active only | Revoke one accepted entry; retain it; if no usable signing key remains, deactivate and remove every grant in the same commit |
| update-services | Active | Current update-services grant, active | Replace the whole bounded service array |
| authorize-operator | Created or active | Never | Add one absent eligible pair, at most 128 active grants |
| revoke-operator | Created or active | Never | Remove one present exact pair |
| deactivate | Created or active | Current deactivate grant, same state | Terminal; remove every grant, retain all record/history/key material |

This candidate explicitly permits controller revoke-key in created state.
Chapter 09 does not label that operation active-only, but this proposal does
not retroactively declare an old implementation conforming. A created record
with another usable signing key stays created after revocation; losing its
last usable signing key makes it terminal, without an intervening activation.
Operators cannot acquire a revoke-key scope in created state. An already
revoked key is rejected rather than incrementing version idempotently.

Created permits only activate/deactivate grants. Active permits only add-key,
revoke-key, update-services/deactivate grants. Activation removes activate
grants; deactivation removes all grants. Automatic removals share the triggering
version and history entry. Operators never create, delegate further, transfer
controller or claim a different Registry/DID. A controller cannot grant itself
operator scope as a second authority identity.

All new entries supplied at create/add-key are accepted; callers cannot inject
pre-revoked entries as fabricated history. At create at least one proven,
accepted unexpired signing key is required. KEM keys never satisfy that test.
For revoke-key use the same trusted admission time to evaluate the successor's
usable signing keys. Expiry alone is not a mutation or a version increment:
an active-but-expired record is unusable for protected operations while its
controller can still authorize eligible recovery management under chapter 09.
A terminal record accepts no mutation, including grant operations. At the
maximum uint64 version every mutation is refused; no wrap or special bypass
for deactivation is allowed. Plan deactivation before exhaustion.

## 2. Framing, principal and schemas

Exactly the first declared frame is considered. Invalid length, UTF-8,
canonical JSON, unknown/duplicate/missing members, premature EOF or an invalid
operation closes that session without trying a second frame. A complete
first command can commit even if an invalid extra frame subsequently arrives;
the protocol never promises that a later framing error rolls back a completed
commit. Exactly one dispatch is the enforced boundary.

The configured future binding label is 1..128 visible ASCII bytes (0x21..0x7e),
matched exactly and never negotiated from a body. Web actor identifiers use
1..256 visible ASCII bytes under protected leaf-pin mapping. The future chain
actor mapping is specified separately; neither a certificate nor an actor
string alone supplies a lifecycle grant. DID/key names and service entries
retain chapters 06/09 bounds. Any added future-profile narrowing is explicit.

A create key has exactly name, alg, key, proof, state and optional expires;
state must be accepted. Add-key wraps exactly one such key. A proof has exactly
signer/value with canonical encodings and its declared key role. No body actor,
credential, role, alternate expected version or default grant is accepted.
All scalar types are exact: booleans are not numbers, decimal strings are not
JSON numbers, null is not an empty object/array/string. Reject duplicate fields
before a parser can overwrite them. JCS is serialization, not authorization.

A mutation response has exactly the six members in README section 2.3.
Binding/Registry/DID/digest always refer to the original accepted payload.
For committed, version is exactly the successor (1 at create). For rejected,
version is the proven current version only if that actor may inspect it;
otherwise it is empty. For unknown, version is empty unless a complete current
version is independently proved. Rejected means this admission made no commit,
not that the bytes can never be submitted later. A malformed/unauthenticated
request need not receive an object; it closes without a success claim.

## 3. History that supports semantic inspection

Each history entry additionally carries admitted, recordDigest and grantsDigest.
Admitted is an integer trusted Unix second 0..9007199254740991 at the mutation's
serialization point. Values are nondecreasing within a record; version orders
multiple admissions in one second. A clock rollback or unavailable trusted time
refuses admission rather than inventing a timestamp. The digests are canonical
unpadded base64url SHA-256 of the complete resulting JCS public record and
sorted active grant array. Neither is a message signature or portable proof.

For a present view historyCount equals the canonical version string, and
entries/commands 1..version are all retained in order. Entry 1 has an empty
previousVersion, operation create and no earlier tombstone. Each later entry
names exactly version-1 and one exact accepted command with that predecessor.
Its actor/operation/target/automatic removals must agree with the command,
prior state/current grants and admitted-time expiry evaluation. Replay from
creation checks every invariant and recomputed resulting record/grant digest;
the final reconstructed record/grants/tombstone must equal the selected view.
A hash match alone does not validate a transition or establish principal truth.

This is authenticated evidence from the trusted Registry, not independent
protection against that trusted authority forging its own history or clock.
Missing intermediate commands, a gap/duplicate, unavailable retained version,
wrong digest or incomplete reconstruction prevents a complete-history claim.
No partial traversal proves non-commit. Quarantined durable state cannot create
a complete view or clear itself through read access.

A view's immutable contents may be old; current credential and read ACLs are
still checked for every admitted read. Historical write grants never authorize
current inspection. Before returning each chunk the trusted provider bounds
its size and complete item identity to the selected view; chunks from another
view are not interchangeable even when bytes happen to match.

A view expires at the earlier of its trusted wall-clock expires value and
60 seconds of monotonic elapsed time since creation. Neither timer extends
on read. Missing time, a backward wall-clock discontinuity or lost monotonic
state invalidates views and readiness; restarting discards views and restores
committed history/rollback state through the trusted recovery procedure.
This does not claim to detect every dishonest clock or attest host integrity.

## 4. Remaining implementation and evidence

The shared admission order must actually cover credential retirement, ACL
changes, record/grant state and commit outcome; independent reads followed by
an unrelated write lock are not proof of that property. The concrete store,
clock, recovery backend and authority remain unselected. Unit-only scenarios
cover stale credentials/ACLs, same predecessor, revocation order, bad framing,
clock loss, capacity and uncertain storage; safe owned runtime later verifies
normal admission, complete history and restart. No attack client or service
is provided here. The ABI design and its codec checks are separate from those
future execution tests and cannot close the old documentary/runtime findings.
