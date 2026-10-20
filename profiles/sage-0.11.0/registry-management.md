# SAGE 0.11.0 chain Registry management binding

Status: **PROPOSED CHAIN BINDING**, revision 1, for explicit adoption before
matching implementation acceptance. This document completes the chain-side
management rules for the selected V1 exchange. It does not make the existing
management proposals normative, amend SAGE 0.10.0, certify an implementation,
select a live instance or authorize deployment. The companion, payment-wallet,
reputation, validation and optional web-management proposals are excluded.

The [machine-readable contract](registry-management.json) identifies the exact
public inputs, schemas, function mapping and limits. The words MUST, MUST NOT,
SHOULD and MAY have the BCP 14 meaning used by chapter 00. The selection in
[selection.json](selection.json) already fixes the version and domain bytes;
this proposal adds the following explicit chain admission and evidence rules.
If adopted, a matching implementation MUST satisfy this document in full and
qualify its exact compiler, dependencies, runtime code, ABI and operating
manifest. Publication or passing the documentary checker alone is not adoption.

## 1. Source precedence and instance identity — CM-01

The manifest's input hashes refer only to public repository files at the
fixed `040436d0239330e3f5fc760489cf2a63729fa4a4` revision. Moving branches,
later ERC drafts and private design notes cannot change this binding.
The selected V1 values plus this document govern new chain management. The
explicitly restated rules below replace the candidate status only for this
binding after adoption; other proposal sections remain proposals. General
cryptographic/JCS/identifier rules come from the pinned chapters 01, 02, 06,
09 and 11 with only the selected 0.11.0 domain/version substitutions.
Implementation details not prescribed here require their own qualified source
artifact; they do not permit an alternate accepted command or authority.

The instance has a positive execution chain ID with at most 32 decimal digits
and an immutable identity `eip155:<chain-id>:<lowercase-contract-address>`.
Constructor initialization MUST bind the exact runtime `block.chainid` and
the contract's own address. Reads and writes MUST reject execution after a
chain-ID mismatch. No setter, upgrade/delegatecall route, controller transfer,
recovery, direct-create shortcut, trusted-forwarder mode or erase path is
introduced. A new instance needs new authenticated enrollment; an old Registry
address is never its default or alias. The Source independently binds genesis,
chain ID, address, initialized identity, code and ABI; equal strings alone do
not authenticate an instance or distinguish a fork.

## 2. Call surface and complete canonical input — CM-02

The thirteen functions and ordered argument/return types are exactly the
manifest-pinned `contract-abi.json` and `contract-signatures.json`. The eight
record mutators are revealClaim, activate, addKey, revokeKey, updateServices,
authorizeOperator, revokeOperator and deactivate. commitClaim has separate
claim state; registryId, record, activeGrants and historyItem are reads.
No additional accepted selector, payable operation or generic execution entry
is permitted. A rejection-only Solidity fallback is not an additional accepted
management operation. ABI implementation artifacts MUST demonstrate the exact
effective thirteen-function surface and constructor behavior.

Before application allocation or proof work, bound the whole calldata and
nested ranges. Native nonpayable/ABI compiler checks may preempt the reached
body and produce ordinary failure; they never supply success or license an
unbounded allocation from an unchecked count. Qualified source/decoder evidence
MUST establish that boundary. After native preemption, reached-body framing is:

1. Length above 148804: BoundsExceeded; length below 4: MalformedCall.
2. Read the available selector. Unknown: MalformedCall.
3. Apply that method's maximum size, then its static-head minimum, from the
   manifest. The minimum is not a complete canonical dynamic encoding.
4. Walk fields in ABI order, arrays in index order and tuple fields in
   declaration order. At each node require its offset/length words, then its
   bounded count/length, then safe arithmetic and complete in-input range.
   Reject missing words as MalformedCall, excessive reviewed counts/lengths
   as BoundsExceeded, and unsafe arithmetic/range, overlap, alias, gap,
   noncanonical offset/padding or trailing bytes as MalformedCall, in that order.
5. After bounded traversal require equality with complete canonical ABI
   re-encoding, including all selector, padding and tails, before admission.

This does not require every compiler panic/out-of-gas/unknown revert to use a
custom error. Every such outcome remains failure or unavailable evidence.
No alternate decoder, selector scan or interpretation is tried after refusal.

## 3. Scalar, role and representation rules — CM-03

Agent IDs use 1..64 ASCII letters, digits, dot, underscore or hyphen, excluding
`.` and `..`. Key/service names use 1..32 ASCII letters, digits, underscore or
hyphen; dots are not key-name characters. Construct exact DIDs and full key
URLs from this Registry and agent ID, with the bounds of chapter 06.
Address JSON text is `0x` and exactly forty lowercase hex digits. Chain account
authorization identifiers are addresses, not a recovered SAGE signing key.

Records have exactly id, controller, keys, services, state and version. Keys
have exactly name, alg, key, proof, state and optional expires; proof has
exactly signer/value. Services have exactly name/type/uri. Creation/addition
supplies accepted entries only. Algorithm, key material, proof, expiry and name
are immutable after admission. Raw bytes become canonical unpadded base64url.
ABI hasExpiry=false requires expires=0 and omission from JSON; true includes
the exact safe integer, including zero. Present expiry is at most 2^53-1 and
is unusable at trusted admission time greater than or equal to that value.

Keys are sorted by ASCII name, including revoked entries; there are 1..128
lifetime entries. A name or exact raw material cannot be reused across any
role or algorithm, including tombstones. Services are a sorted complete array
of 0..16 entries with unique names disjoint from all retained key names. A new
key also cannot collide with a current service name. Removed service names
are not key tombstones. Service type is 1..64 ASCII bytes; its permitted ASCII
controls MUST be JSON-escaped canonically rather than emitted literally.
URI is an absolute HTTPS URI of at most 2048 ASCII bytes under [RFC 3986](https://www.rfc-editor.org/rfc/rfc3986.html),
without userinfo or fragment. Test the parsed components; an `@` in the path
or query is not userinfo. Scheme matching follows [RFC 3986 section 3.1](https://www.rfc-editor.org/rfc/rfc3986.html#section-3.1);
preserve supplied URI bytes after validation, without fetching or silently
normalizing them. Empty/invalid authority, malformed percent escapes, control
bytes or a fragment marker refuse. An endpoint never grants a management scope.

Use the exact TABLE-02 names, including lowercase `ed25519`; `Ed25519` is a
JOSE namespace value and not that record algorithm. Every conforming instance
MUST implement strict Ed25519 under CRYPTO-02. Optional suites require their
own qualified strict verifier. Unsupported optional names refuse rather than
becoming accepted or selecting another key. X25519 is KEM only. Retain its
exact 32-byte public value under the declared algorithm without silently
normalizing it. The pinned Registry rules do not add a new curve-point
canonicalization or low-order admission blacklist. RFC7748 decoding and
HPKE/direct-DH all-zero-result rejection belong to the actual KEM operation;
endorsement alone establishes neither private-key possession nor a successful
handshake. Any additional Registry admission restriction needs its own explicit
profile decision and matching RFC compatibility analysis.

All newly supplied signing proofs are validated before KEM endorsements, even
if a KEM name sorts first. A signing key names its own full key URL. A KEM key
names a distinct, accepted, unexpired signing key in the same proposed/current
record. Use only that exact signer and its algorithm; do not try alternatives.
For later unchanged records retain the original endorsement and historical
signer even if it is later revoked/expired; it acquires no message authority.
Proof lengths follow the selected signer's algorithm, not a signature role
inferred from KEM bytes. Unchanged admitted entries are not re-proven on every
grant/service/deactivation operation. Historical proof checks and current
message/handshake eligibility remain separate.

PoP input is exactly ASCII `sage-pop-0.11.0`, then each REG-04 len16 and its
single field in order: registry-id, agent-id, name, alg, raw key bytes.
The two-byte lengths are unsigned big-endian lengths only. No extra delimiter,
prehash, old prefix or duplicated key bytes is accepted. Strict signing rules
from the pinned crypto chapter apply; account authorization remains separate.

The longest existing TABLE-02 name, `sage-secp256k1-keccak256`, is24 ASCII
bytes. The earlier candidate calculation's23-byte algorithm ceiling was
incorrect. This binding explicitly uses24, preserving that existing optional
suite rather than narrowing it. Both23 and24 occupy the same32-byte ABI
padding block, so the pinned method byte caps remain unchanged. Optional
support still needs a qualified verifier; a string-length mistake cannot be
used to report that suite implemented or to reject it after advertising it.

## 4. Actual caller and claim admission — CM-04

The principal is exactly Registry `msg.sender`, for EOAs and contract wallets.
No `tx.origin`, code-size/EOA test, outer transaction signer, RPC from field,
relay, wallet owner, body actor, PoP signer or ERC-1271 result replaces it.
Operators themselves may be EOAs or wallets. An authorized wallet address
does not attest its owners, implementation, code-upgrade policy or user intent.
Transaction-format and wallet-product qualification are separate requirements.

commitClaim stores the exact caller/commitment pair at the current block.
Presence is an explicit bit; block zero is valid. A present duplicate refuses
ClaimUnavailable even if consumed or expired; it is never refreshed/deleted.
Different commitments and callers remain independent. The claim is SHA-256 of
ASCII `sage-claim-0.11.0`, one NUL byte and complete claim JCS with exactly
registryId, agentId, controller, keys, services and salt. Salt is exactly the
ABI bytes32, represented as canonical unpadded base64url. Key/service arrays
have the above canonical representation and accepted initial entries.

Reveal derives this digest from its exact arguments and configured Registry.
It requires unused identity, proposed controller equal to actual caller,
present unconsumed caller-scoped claim, currentBlock>commitBlock and then
currentBlock-commitBlock<=256. Success consumes only that claim atomically
with created/version1/history. Failure consumes nothing. Reveal has no supplied
digest to compare to an alternative stored commitment; ClaimMismatch remains
reserved and is not emitted. This process prevents cross-caller consumption,
not independent competition for a human-chosen identifier.

## 5. Lifecycle, grants and time — CM-05

An absent record has state0/version0 only. Created, active and deactivated have
positive uint64 versions. Controller is immutable. Deactivated identity and
all key tombstones are permanent; no terminal mutation or reassignment exists.
Every successful record mutation advances exactly once; uint64 maximum rejects
all mutations, including deactivate. Expiry alone does not write history.

| Operation | Current state | Allowed actual principal | Complete effect |
|---|---|---|---|
| create | absent | proposed controller only | created/version1, all initial proofs, at least one usable signer |
| activate | created | controller or exact activate grant | active with usable signer; remove activate grants |
| add-key | active | controller or exact add-key grant | one new immutable proven entry, lifetime indexes retained |
| revoke-key | created/active | controller; exact revoke-key grant only in active | revoke accepted target; terminal plus all-grant cleanup if no usable signer remains |
| update-services | active | controller or exact update-services grant | complete replacement, no new authority |
| authorize-operator | created/active | controller only | insert one absent operator/scope pair, maximum128 |
| revoke-operator | created/active | controller only | remove one present exact pair |
| deactivate | created/active | controller or exact deactivate grant | terminal plus complete grant cleanup |

Created-state grants are exactly activate/deactivate. Active-state grants are
exactly add-key/revoke-key/update-services/deactivate. A controller cannot grant
itself a second operator identity. No extra zero-address reservation is added
to the principal rule. Grant ordering is lowercase operator text then ASCII
scope text; internal enum numbering does not determine that ordering.
Operators cannot create, grant further authority or change the controller.
Explicit revoke-operator is not duplicated in automaticRemovals. All implicit
removals share the same successor, history item and event as their trigger.

Admission uses `block.timestamp` in 0..2^53-1, nondecreasing per record. The
client's trusted now, freshness and finality policy remain different inputs.
Equality is allowed; unavailable/rollback admission time refuses. At create
and activate a usable accepted unexpired signing key is required. Revoking
the last usable signing key is terminal. Other permitted recovery management
is not refused merely because all current keys have expired.

## 6. Exact command, serializer and retained history — CM-06

The accepted derived chain command has exactly binding, registry, did,
operation, expectedVersion, arguments and actor. Binding is
`sage-registry-chain-0.11.0`; actor comes from actual caller, not a JSON input.
ExpectedVersion is empty only for create, otherwise its exact positive decimal
uint64 predecessor. Operation comes from the function. Argument member sets
are in the manifest; create retains controller/keys/services/salt, add-key
wraps key, service replacement wraps services, grant operations retain the
exact operator/scope, revoke-key retains name, and activate/deactivate use `{}`.
No chain command is accepted by the optional six-member web-command parser.

Each history entry has exactly version, previousVersion, actor, operation,
commandDigest, target, automaticRemovals, admitted, recordDigest and grantsDigest.
Version is the successor; previousVersion matches the command. Target is null
except the exact operator/scope object on explicit grant insertion/removal.
AutomaticRemovals is the complete sorted list of implicit removals only.
Command, record and grants digests are SHA-256 of their complete resulting JCS
bytes, represented as canonical unpadded base64url; none is calldata hash,
transaction hash, event topic0, a signature or a substitute for source authority.

Record JCS is at most65536 bytes. Command and history JCS are each1..262144
bytes. These bounds do not increase optional web frames. Keys, grants and
record strings in this chain schema are ASCII with properly escaped controls;
the serializer need not claim to be a general Unicode JSON parser. It MUST
produce chapter02/[RFC8785](https://www.rfc-editor.org/rfc/rfc8785.html) bytes exactly: stable field ordering, shortest valid
JSON escapes, exact safe integer seconds, string versions, no whitespace and
canonical binary strings. Independent golden bytes MUST include control chars,
quotes/backslashes, key/service name punctuation differences, absent versus
zero expiry, decimal boundaries, empty services/grants and all transition
types. Counts or approximate byte estimates cannot replace actual serialization.

This proposal explicitly adopts the future headroom restriction from the
pinned revision5 candidate. For every nonterminal prospective successor,
check its actual complete record length first, then re-encode a temporary
size-only copy with state=deactivated and version="18446744073709551615" and
require it to fit65536. This applies to creation and every nonterminal mutation
before proof work. An unconditional24-byte subtraction is not equivalent.
Terminal successors need only their actual bound. The temporary bytes are
never stored, hashed, signed, emitted or treated as an admitted record.
This is an additional acceptance restriction, not an interpretation that the
0.10.0 sets were identical. Do not apply it to old reads or rewrite old records.
It reserves root state/version growth, not arbitrary additions, gas, authority
readiness or an exhaustion bypass; max-version deactivation still refuses.

Retain every successful version1..current with its command, history, original
salt after reveal and resulting public state/grants digests. No missing item,
fabricated empty value or count alone proves completeness. Typed storage MUST
preserve exact logical state, lifetime indexes and atomic history. Actual
compiler layout/source proofs bind logical fields to slots. Probe variable
labels are not Solidity interface requirements: internal Registry identity
storage must not collide with the `registryId()` function name. No public
initializer or test setup/control entry may exist in accepted runtime code.

For these exact bounded schemas, complete create/update-services command content
is already bounded by a prospective65536-byte record; fixed surrounding fields
fit within4096 additional bytes. Other command arguments are smaller bounded
subsets. A conservative command upper bound is therefore69632, below262144.
A grant pair is at most83 JSON bytes and a128-pair removal array at most10753;
the other fixed history fields fit within1024, also below262144. These are
capacity arguments, not tighter accepted caps or gas bounds; implementations
MUST still verify exact serialized bytes and test every boundary workload.
The longest REG-04 input under the stated eip155/type union is292 bytes:
15 prefix bytes, ten length bytes and82+64+32+24+65 field bytes. Optional
signature/backend limits cannot silently reject any required valid input.

## 7. Reached-body semantic ordering and diagnostics — CM-07

After framing, rank2 checks nonzero value then Registry context. Rank3 checks
scalar/content grammar in ABI field order and semantic ranges. Rank4 resolves
current identity/coherent required history: reveal requires absent identity
then present unconsumed caller/hash; other mutations require existing record.
Rank5 checks exact current caller/controller or grant. Rank6 checks lifecycle,
then exact predecessor, then successor capacity. Reveal has no supplied
predecessor. Rank7 checks reveal window first, then admission time/range/order.

Rank8 checks operation targets and entry structure in the pinned revision5
table's written order, explicitly restated in the manifest. Unsupported
algorithm precedes its raw representation decoding. Complete all applicable
target/entry checks, then the prospective exact record-byte/headroom checks.
Rank9 verifies newly supplied proofs, all signing proofs before endorsements.
Rank10 constructs final state, applies usable-signer and implicit grant cleanup,
then serializes full record, grants, command and history in that order and
rechecks exact bounds/invariants/digests. Rank11 commits all effects and one
RecordChanged atomically. No prospective state is externally published early.

commitClaim applies ranks1..3 then duplicate caller/hash and atomic claim insert;
no record time or history. registryId applies1..3/context. Other reads apply
1..4/context, no write ACL, admission time, proof loop or mutation predecessor.
historyItem's requested version must be positive at scalar checks. Structural
rank3 does not silently perform rank8 algorithm/role eligibility checks.

The exact22 zero-argument errors and2 nonanonymous events use the pinned
outcome ABI and schema. ClaimMismatch is reserved. Error categories and
operation-specific rank8 ordering are fixed in the manifest. A zero-argument
custom error alone does not authenticate its producer; compiler/resource/
unrecognized errors remain failure/unavailable, not another accepted variant.

The categories below also fix diagnostics when these reached guards detect
the cause; they do not rename earlier native/compiler/resource failures.

| Error | Reached cause |
|---|---|
| MalformedCall | Noncanonical/ambiguous selector, ABI offsets, padding, tails or unsafe ranges |
| ValueNotAllowed | Nonzero value at the reached value guard |
| WrongRegistryContext | Execution chain/configured Registry context mismatch |
| UnauthorizedCaller | Exact current principal fails controller/grant authorization |
| WrongRecordState | Required identity absent or operation disallowed in lifecycle |
| PreviousVersionMismatch | Positive supplied predecessor differs from current version |
| VersionExhausted | Current uint64 has no successor |
| ClaimUnavailable | Caller/digest absent, consumed, or duplicate commit |
| ClaimWindowInvalid | Reveal not strictly later or more than256blocks later |
| ClaimMismatch | Reserved; not emitted by this binding |
| IdentifierUnavailable | Creation identity already exists, including terminal tombstone |
| KeyUnavailable | Revoke target missing or already revoked |
| KeyNameReused | Lifetime name reused or equal initial names |
| KeyMaterialReused | Lifetime exact raw material reused in any role/algorithm |
| InvalidKeyProof | Mathematical verification fails under the exact qualified signer |
| UnsupportedKeyAlgorithm | Unknown or unimplemented selected algorithm before raw decoding |
| InvalidEntry | Invalid scalar/content grammar or entry/target/successor invariant |
| BoundsExceeded | An actual reviewed count/length or exact serialized size bound fails |
| GrantUnavailable | Exact requested active operator/scope pair absent at removal |
| GrantAlreadyPresent | Exact pair already active at insertion |
| HistoryUnavailable | Required coherent current/retained history or grants missing |
| TimeInvalid | Admission clock range or per-record monotonicity fails |

## 8. Reads, execution evidence and events — CM-08

record returns false/empty only for absent identity, otherwise true and complete
current REG-01 bytes, including terminal records. activeGrants on absent
identity refuses WrongRecordState; existing empty grants returns exact `[]`.
historyItem returns exactly the retained entry/command at the positive requested
version; absent identity is WrongRecordState, future/missing retained version
is HistoryUnavailable. registryId returns the configured immutable identity.
Every read still applies syntax/context/canonical ABI guards. Reads do not
establish freshness/finality, custody, enrollment uniqueness or protected use.

ClaimCommitted binds actual caller, exact commitment and commit block and
claims no record version. RecordChanged is emitted once after complete atomic
mutation/history, using the exact pinned event arguments/indexed flags. Its
DID index is SHA-256 of exact full ASCII DID, not ABI topic0's Keccak hash.
Reverted execution publishes no successful partial record/grant/history/event.

A Source MUST establish the exact accepted call/caller at the intended code
and one coherent finalized state with complete applicable grants/history.
Outer wallet receipt success, destination, matching event/payload hash or RPC
from do not establish inner Registry success; a wallet may catch an inner
failure. Missing/ambiguous actual execution or outcome is unavailable evidence,
not authenticated absence, success or permission to replay at a guessed version.

## 9. Finality, recovery and qualification — CM-09

The selected Source binds chain ID, genesis, Registry/code/ABI/configuration,
trusted resolver/node identity and policy generation, finalized anchor and
validated descendant ancestry, maximum observation age and trusted clock.
Every multi-read observation is at one selected finalized block. Persist
highest versions, finalized anchors and irreversible tombstones durably.
Restart/cache eviction/generation change cannot reset them. Same-genesis
conflict, incompatible finalized branches, rollback, stale/unavailable ancestry,
unknown policy or clock makes readiness false and quarantines dependent use.
Never choose by height alone, first response or majority of untrusted RPCs.
Only authenticated explicit reconfiguration can resolve quarantine, retaining
old/new policies, anchors, authority and reason and establishing continuity;
it cannot revive terminal identities or keys.

The actual source/attestation/consensus-verifier format and operating values
MUST be separately qualified before live connection; this does not invent an
RPC method or select a service provider. Proof of contract behavior alone is
not a deployed finalized Source. No trusted-registry/node compromise detection
or compromised-wallet intent guarantee is claimed beyond the stated boundary.

Qualification requires the full13-function code/ABI, exact compiler/settings/
linked libraries, complete serializer/decoder and strict crypto artifacts,
unit refusal schedules without attack producers, owned normal EOA/wallet
lifecycle runtime, full valid boundary128keys/16services/128grants costs and
runtime/initcode/storage/history/read budgets. Preserve authorization,
atomicity and all lifetime/history bounds. If a real candidate cannot admit a
required valid case, record the feasibility gap and obtain an explicit design
decision; do not lower limits or promote an incomplete experiment to conformance.
No license/source, runtime verifier, operating chain/fork/transaction format,
gas budget, RPC, deployed address/code or custody/host configuration is selected
by this normative proposal. No actual transaction is authorized.

Old0.10.0 subjects and all FAIL/PARTIAL/UNSUPPORTED/NOT_RUN findings remain
identifiable. Use separate new enrollment/proofs/API entry points and new
subjects; do not translate signed objects or duplicate effects during dual
support. This document does not complete Inspector, Go/Rust/ADK integration,
the optional web-management binding, external registration, independent
organizational audit or the overall7/8 work.
