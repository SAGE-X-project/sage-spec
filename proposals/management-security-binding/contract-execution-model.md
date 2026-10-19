# Candidate Registry commands, state and outcomes

Status: **UNADOPTED future-version design**, revision 4. This extends the
[typed thirteen-method candidate](contract-design.md) and
[lifecycle table](lifecycle-and-schemas.md). No SAGE 0.10.0 requirement,
existing contract, release, operating chain or deployment changes here.
The function ABI and its two codec examples remain byte-identical.
The separate [outcome ABI](outcomes/abi.json) and
[authored schemas](outcomes/schemas.json) propose twenty-two custom errors and
two events; artifact checks do not execute any of them on a Registry.

## 1. One command from one executed call

Use the selected method and validated arguments to derive the complete accepted
semantic command: configured future binding, immutable registry ID, exact DID,
operation, predecessor, arguments and the exact Registry `msg.sender` actor.
Do not accept a second body, claimed actor, supplied digest or wallet owner as
the authority or replacement command. [Account policy A](account-binding.md)
continues to support both EOA and contract-wallet callers.

| ABI surface | Accepted history command |
|---|---|
| commitClaim | No record command/version; caller-and-Registry-scoped commitment only |
| revealClaim | create; empty predecessor; version 1; controller equals actual caller |
| activate | activate at the exact positive predecessor |
| addKey | add-key with exactly one immutable accepted entry |
| revokeKey | revoke-key with the exact named entry; automatic terminal state/grant cleanup shares this version |
| updateServices | update-services with the complete replacement array |
| authorizeOperator | authorize-operator with exact target address and scope |
| revokeOperator | revoke-operator with the same exact pair |
| deactivate | deactivate and atomic complete grant removal |

Four read methods create no command or mutation version. A successful record
mutation has one successor and one complete retained command/history pair;
commitClaim does not fabricate such a pair. Creation cannot bypass the matching
same-caller claim or its strictly-later, at-most-256-block reveal window.
Registry identity/code/context checks also apply to reads. The concrete future
binding and claim/PoP domain bytes remain unassigned adoption gates.

## 2. Logical state and canonical bytes

| State | Retention and consistency rule |
|---|---|
| Record identity | Exact agent ID/DID and immutable controller, created/active/deactivated state, positive uint64 version |
| Keys | Immutable named entries with retained revoked flags; lifetime name/raw-material uniqueness across roles; no clearing tombstones |
| Services | Current sorted complete array; service names cannot collide with retained key names |
| Grants | Complete current sorted scoped pairs, at most 128; transition-specific removals in the same mutation |
| History | Every version 1..current, accepted semantic command, authenticated actor, admitted time and resulting record/grants digests |
| Terminal identity | Permanent final version and identity tombstone; no revival, reassignment or wrap |
| Claim | Separate exact caller/commitment binding, commit block and consumption; consumption plus creation is atomic |

This is the required logical mapping, **not a compiler storage-slot layout or
proof format**. The exact slot layout, typed-state/canonical-byte storage choice,
implementation and full workload cost are still unfinished. A source must later
bind those exact artifacts to the same finalized block and deployed code.

Build the complete public REG-01 record and active grant array from validated
fields. Serialize under chapter 02 JCS with exact field presence and canonical
unpadded base64url; uint64 versions are decimal strings. `hasExpiry=false` requires
expires=0 and omits expires, while present zero remains an expired value.
Preserve supplied service strings exactly after syntax validation; apply proper
JSON escaping rather than assuming every ASCII byte can be emitted literally.
Never fetch a URI to validate it or derive a grant from service metadata.

Validate signing proofs before KEM endorsements, including when a signing entry
sorts after its KEM entry. A KEM signer is an eligible validated signing key in
the same proposed/current record. This is endorsement, not KEM possession.
Accepted optional algorithms require their own strict verifiers. No algorithm
subset or verifier is adopted by the separate raw-key research experiment.

The admission timestamp has one precise chain meaning, is in the existing safe
integer-second range and is nondecreasing for a record. It is distinct from a
client's clock, observation freshness and finality delay. Expiry alone writes no
history; revoking the last usable signing key commits terminal state and grant
cleanup once. Version exhaustion refuses every mutation, including deactivate.
All checks and state/history effects belong to one atomic execution; a revert
publishes no successful partial mutation. Complete history is public on chain,
not a confidential log or the optional web read ACL.

## 3. Preflight and capacity

Before allocation and expensive proof work, bound whole calldata, array counts,
field lengths and all nested offset/length arithmetic. Then require exact full
canonical ABI re-encoding, padding, tails and length. Compiler decoding by itself
is insufficient evidence of this stricter candidate policy. The actual decoder
implementation and its unit-only malformed-input tests remain NOT_RUN.

The public record's 65536-byte JCS bound is not an ABI calldata bound. For the
current eip155 syntax, a same-record signer URL is at most 189 ASCII bytes.
Using dynamic(n)=32+32*ceil(n/32), one seven-field Key tuple is at most 736 bytes
for raw key32/proof64/algorithm<=7, and one three-field Service tuple is at most
2336 bytes. Including dynamic-array offsets, selector and reveal's five heads:

```
4 + 5*32 + dynamic(64)
  + (32 + 128*(32+736)) + (32 + 16*(32+2336)) = 136516
```

This conditional calculation assumes Ed25519/x25519 only; it does not select
that subset. The current TABLE-02/03 raw-type union (key<=65, proof<=65,
algorithm<=23) adds 96 bytes per Key and gives a conservative upper bound
148804. Record-size, field, algorithm/role and semantic checks still apply;
the simultaneous maxima need not form a valid 65536-byte record. Future table
extensions require a newly reviewed bound. No value here selects an operating
gas limit, makes a narrower caller limit conforming, or proves full 128-key
creation/verification/storage/history affordable. The single-signature research
cap is unrelated to a complete Registry operation's budget.

## 4. Proposed refusal ABI

All twenty-two errors have zero arguments, keeping this diagnostic surface
bounded. The table defines intended guard categories, not proof that compiled
Solidity emits them for every malformed call or EVM failure.

| Error | Intended guard category |
|---|---|
| MalformedCall | Selector/ABI/canonical framing or ambiguous input |
| ValueNotAllowed | Nonzero value on this nonpayable binding |
| WrongRegistryContext | Different configured chain/Registry/code context |
| UnauthorizedCaller | Controller/current exact grant does not authorize caller |
| WrongRecordState | Operation is not permitted in the current lifecycle state |
| PreviousVersionMismatch | Exact expected predecessor is not current |
| VersionExhausted | No uint64 successor exists |
| ClaimUnavailable | Matching caller-scoped unconsumed commitment is absent |
| ClaimWindowInvalid | Reveal is not strictly later or is outside the window |
| ClaimMismatch | Exact recomputed claim does not match |
| IdentifierUnavailable | Agent identity is already reserved, including terminal identity |
| KeyUnavailable | Requested key is absent or not eligible for the named operation |
| KeyNameReused | Lifetime key name would be reused |
| KeyMaterialReused | Lifetime raw key material would be reused |
| InvalidKeyProof | Selected signing proof/endorsement fails strict verification |
| UnsupportedKeyAlgorithm | Declared algorithm is not actually supported |
| InvalidEntry | Field syntax, role, signer context, sort order or other entry invariant fails |
| BoundsExceeded | Calldata/field/array/record/grant capacity bound fails |
| GrantUnavailable | Required exact target grant pair is absent |
| GrantAlreadyPresent | Controller would insert an already active pair |
| HistoryUnavailable | Required complete version/command/history view is unavailable |
| TimeInvalid | Required admission time range/order cannot be established |

Implementations must finish the guard precedence table before contract code;
this inventory does not assign precedence to simultaneous failures. Compiler
ABI rejection, Panic, out-of-gas, empty or unknown revert data remain failures,
never successes, algorithm fallback or permission to invent a new predecessor.
Do not claim every such failure is one of these custom errors.

Decode custom errors only under a verified exact call/code/source context.
Revert bytes alone cannot establish who produced them. A wallet may catch an
inner revert or execute several commands, so outer receipt success and a decoded
error name are insufficient to determine this Registry operation's outcome.
The source must establish its exact executed command and coherent state/history.

## 5. Proposed events and digest meanings

Events are nonanonymous under the pinned
[Solidity ABI 0.8.20](https://docs.soliditylang.org/en/v0.8.20/abi-spec.html).
Their exact indexed flags and ordered arguments are in the separate ABI and
schema manifest. Topic0 uses the normal ABI event signature hash. No custom
signature scheme or HTTP error encoding is substituted.

ClaimCommitted binds actual caller, commitment and commit block; it does not
claim a record exists. RecordChanged binds an indexed SHA-256 of exact canonical
ASCII DID bytes, the actual actor, full DID, predecessor/successor, operation,
command/record/grants digests and admitted seconds. The DID hash is explicitly
SHA-256; it is distinct from the ABI's topic0 derivation. A consumer recomputes it
from the emitted full DID before using it as an index.

Record/grants digests are SHA-256 of complete resulting JCS bytes under the
existing lifecycle candidate. The command digest is SHA-256 of complete accepted
semantic command JCS bytes, not calldata, transaction hash, log bytes or a second
claimed command. Registry/actor/predecessor belong to that command. The future
binding/domain selection is still required before any implementation signs or
accepts a purported future command.

Emit one RecordChanged after the complete atomic mutation/history is formed.
Automatic removals share its version and history item; they create no extra
record version. Reverted execution leaves no successful mutation event. Logs,
indexed hashes and transaction receipts do not replace exact state/history,
Registry code identity, caller execution or finalized source evidence.

## 6. Artifact evidence and unchanged next gates

The separate bounded CLI checks the complete 22-error/2-event inventory,
closed JSON shapes, exact argument layout/indexed flags/nonanonymous events,
ABI-derived selectors/topics and two authored normal event-data examples.
Unit cases are finite local data; there is no chain connection, attack generator,
contract execution or new conformance verdict. The two examples test argument
encoding; their small strings are codec fixtures, not admitted DID records.

Continue with exact storage slots/serialization and guard precedence, full
workload costs, frozen SAGE/A2A/DID/ERC-8004/KYA mappings, selected finality-source
artifact, compatibility and explicit versioned adoption before matching contract,
Go/Rust/ADK and Inspector implementation. Actual account-policy execution,
operating source/custody, deployment and migration remain separate gates.
All old FAIL/PARTIAL/NOT_RUN findings and deferred W3C registration remain intact.
