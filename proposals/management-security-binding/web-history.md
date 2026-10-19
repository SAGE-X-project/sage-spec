# Authenticated read-only management inspection candidate

Status: **UNADOPTED future-version candidate**, draft revision 2. This extends
only the proposed web management binding in [README.md](README.md). It does
not add an endpoint to REG-08 public record retrieval, implement a protocol,
prove durability or change the 0.10.0 inspection contract. The chain binding
needs its own ABI and history observation mapping.

## 1. Authority, channel and bounded requests

Use the same configured future binding identifier, Registry identity, direct
fresh TLS 1.3 mutual authentication and one-request/one-response channel as
the proposed management binding. The binding identifier remains unassigned;
implementations cannot advertise a placeholder as a negotiated standard.
A separate trusted read ACL maps an authenticated actor to permitted Registry
and DID history. Controller status, a write grant, a service URL or possession
of a view identifier does not by itself grant read access. Read permission
never grants mutation. History can contain sensitive operational associations.

Configuration, credential retirement, read-ACL updates, state commits and view
creation/access share one admission serialization order. At its admission
point every request rechecks current configuration generation, leaf pin,
certificate validity, trusted clock and exact read ACL. A provider unable to
serialize these checks refuses the binding; a prior channel snapshot is not
current authority. Configuration change after a completed admission does not
retroactively revoke that completed read. Reads waiting for admission recheck.

Each frame is a four-byte unsigned big-endian payload length followed by
1..69632 UTF-8 bytes. Parse one JCS JSON object under chapter 02 and require
exact received/canonical-byte equality. Bound before allocation and reject
unknown/duplicate/missing fields and invalid text before dispatch. A partial
frame cannot dispatch. At most the first frame dispatches; trailing frames
cannot invoke a second read or a write. Authentication/framing failure closes
the connection and supplies no view. The inspection and mutation dispatchers
are distinct closed schemas; neither interprets an unknown operation as the
other kind or infers an actor from a body.

Every request has exactly `binding`, `registry`, `did`, `operation`, `arguments`.
Context matches trusted endpoint configuration and canonical chapter-06 DID.
`arguments` is selected by exact operation, never a union of optional fields:

| Operation | Exact arguments | Meaning |
|---|---|---|
| `inspect-open` | `version` | Empty string selects current complete state; otherwise canonical decimal 1..18446744073709551615 requests that retained committed version |
| `inspect-read` | `view`, `section`, `index`, `offset` | Read one bounded item chunk from an existing actor-bound immutable view |

These names are candidate design labels, not assigned protocol identifiers.
A history permission can separately restrict historical versions. There is no
wildcard DID, batch, query language, write flag, actor field or automatic fetch.
Malformed requests or denied ACLs supply no existence/history information.

## 2. Immutable views and exact response context

The server bounds concurrent views, per-actor quotas, capture work, snapshot
retention and read deadlines in protected configuration. Exhaustion returns
no view and has no Registry mutation. It never truncates history silently.
An open request captures record, grants, ordered history, tombstone and
version from one complete committed state at one serialization point. A view
is a logical immutable storage snapshot, not a full history copy in one frame.
Incomplete, conflicting or unproved durable state cannot create a view.
Snapshot storage and committed history retention are distinct requirements.

A view identifier is 32 cryptographically random bytes encoded as canonical
unpadded base64url (43 characters). It is bound server-side to actor, Registry,
DID, selected snapshot and current read policy, with an absolute lifetime of
at most 60 seconds on a trusted clock. It is not a bearer authorization token.
Its lifetime is never renewed by reading. Restart discards all views; it does
not discard committed history, pins, finality or rollback high-water marks.
An unknown, expired or mismatched identifier fails without selecting another
snapshot. An expired view can be reopened explicitly at the same retained
version after current authentication; chunks from the two views are never
silently combined.

Every response has exactly `binding`, `registry`, `did`, `requestDigest`,
`operation`, `outcome`, `result`, all within the same 69632-byte frame limit.
`requestDigest` is canonical unpadded base64url SHA-256 of the exact accepted
request payload. The client checks context, operation, digest and the closed
result schema before using any data. Responses use JCS and the authenticated
request's original TLS channel. They are not object signatures, RFC 9457 HTTP
responses or portable proofs against a malicious trusted Registry.

`outcome` is `ok`, `unavailable` or `denied`. An authenticated valid-schema
request without permission gets `denied`; no existence hint is supplied.
An unavailable/quarantined/pruned snapshot, exhausted capacity or expired
view gets `unavailable`. Both failure outcomes have `result` equal to null.
Failure details are local diagnostics, not a fallback source or a claim that
a previous write failed. An invalid response or lost channel is inconclusive.

For successful `inspect-open`, `result` has exactly `view`, `version`,
`present`, `historyCount`, `expires`, `sectionDigests`:

- `version` is the selected canonical committed record version; it is empty
  only for a current proved-absent record. Historical absence is not inferred.
- `present` is a boolean. A deactivated record is present with its tombstone;
  it is never represented as an absent/reusable DID.
- `historyCount` is the exact decimal number of committed mutation entries.
  Creation is entry 1 at record version 1, and one subsequent successful
  mutation produces one following entry/version, including automatic grant
  removals in that same entry. For absence it is `0` and version is empty.
- `expires` is an integer Unix second under chapter 02. At or after that
  instant no further read may be admitted. Capture and expiry are diagnostic
  inspection timing, not REG-05 freshness evidence for a protected operation.
- `sectionDigests` has exactly `record`, `grants`, `tombstone`. Each is the
  canonical base64url SHA-256 of that section's canonical bytes, or null only
  when `present` is false. History/commands have per-item digests below;
  there is no unbounded all-history manifest or Merkle-proof claim.

## 3. Sections, chunking and complete history

`section` is exactly `record`, `grants`, `tombstone`, `history` or `command`.
`index` is a canonical decimal string: `0` for the first three sections,
1..historyCount for history and command. `offset` is a canonical nonnegative
decimal byte offset, at most 262143. No numeric/string coercion is accepted.
Absent views have no readable items; tombstones remain readable for present
terminal records. Missing/unretained items fail rather than becoming empty.

A section item has 1..262144 canonical UTF-8 JSON bytes. `record` is the
complete REG-01 record (its existing 65536-byte bound remains). `grants` is
the complete active grant array sorted by ASCII operator then scope, with
at most 128 exact `{operator,scope}` objects. `tombstone` is exactly
`{deactivated:boolean}`; false does not omit the member. Each history item
has exactly `version`, `previousVersion`, `actor`, `operation`,
`commandDigest`, `target`, `automaticRemovals`, `admitted`, `recordDigest`,
`grantsDigest`. The last three fields bind the trusted admission time and
complete resulting record/grants as specified in
[lifecycle-and-schemas.md](lifecycle-and-schemas.md). `previousVersion` is empty
only for creation. `target` is null except authorize/revoke-operator, where
it is exactly `{operator,scope}`. `automaticRemovals` is a sorted complete
array of removed `{operator,scope}` pairs, never a second mutation/version.
`command` is the exact accepted canonical mutation payload for the same
entry. Its digest equals the history item's `commandDigest`. State/grant
validation must still be reviewed for every command; digest equality alone
is not authorization or semantic correctness.

A successful `inspect-read` result has exactly `view`, `version`, `section`,
`index`, `offset`, `total`, `digest`, `data`, `nextOffset`. Integers other than
chapter-02 timestamps are canonical decimal strings. `total` is 1..262144,
`offset` is less than total, and `data` is canonical unpadded base64url of the
next min(16384,total-offset) raw item bytes. `nextOffset` is offset+decoded
length, or null exactly at total. `digest` covers the complete canonical item,
not only this chunk. A read does not split a logical mutation into separate
versions. Digests and metadata for the same view/item must never change.

Clients follow contiguous offsets from zero, check every returned context,
size, base64 encoding and next offset, then verify complete length/digest,
UTF-8 and canonical JSON before interpreting an item. Interleaved concurrent
views, duplicated/reordered/missing chunks, inconsistent metadata or excess
limits invalidate the assembled evidence. Resource/time limits can leave
inspection incomplete; no partial traversal proves complete history.
Current grants and history-to-command mapping come from the same selected
snapshot. History contains no private credentials, TLS session secrets,
private keys or claims of human intent. Access and retention require a stated
privacy policy. Public-chain history is inherently observable and cannot be
made private by this web read ACL.

## 4. Lost replies, uncertainty and recovery

After a lost mutation response the client opens an authenticated current view
and compares exact accepted command bytes/digest, expected previous version,
actual actor and ordered transition history. A matching uniquely committed
entry proves that command committed at that version in the selected view;
an equal resulting record alone does not. A digest is a comparison aid, not
an authorization capability. A current view must contain a complete history
through its version for a non-commit conclusion at that observation point.

A valid prior request can still be in flight after inspection. Therefore
absence in a complete current history proves only not yet committed as of
that snapshot. It is not an irreversible failed-operation receipt or
permission to send a different payload at a fabricated next version.
An exact retry retains its original expected version and bytes; atomic CAS
can admit at most one mutation at that predecessor. An intervening different
mutation makes that retry stale, even if the original outcome is unknown.
Uncertain/partial storage remains quarantined; the read-only interface cannot
clear quarantine, reconstruct missing history, reauthorize a grant, restore
keys or choose a chain branch. No automatic retry is mandatory.

A separate trusted local recovery procedure proves record/grants/history/
tombstone consistency and rollback resistance before restoring readiness.
Its operator, durable evidence, atomic store mechanism and custody are
operating/implementation choices still unselected. This proposal specifies
observable refusal and inspection, not an implemented recovery backend.
Full integration/Inspector acceptance needs evidence of that backend under
normal, safe restart and unit-only fault scenarios.

Revision 2 applies the closed schema, current-authority, trusted-clock and
complete-history invariants in [lifecycle-and-schemas.md](lifecycle-and-schemas.md).
Draft revision 1 is available at Git revision
`b63b08f81f566ab00d27c89e0cd4c40a4b6f383d`; it is not a deployed wire format.
