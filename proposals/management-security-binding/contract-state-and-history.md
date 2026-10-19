# Exact Registry state, commands and admission candidate

Status: **UNADOPTED future-version design**, revision 5, following spec main309609e.
This is a grouped design closure, not Registry implementation, source adoption,
proof of conformance or a change to SAGE0.10.0. Account A remains selected:
EOAs and contract wallets are supported through exact Registry msg.sender.
The eight record mutations, commitClaim and four reads keep their existing ABI.
[chain-command-map.json](chain-command-map.json) retains all 51 ordered input
layout paths, including structural tuple/array nodes. Its target descriptions
are authored for this mapping; ABI types/paths were copied from the existing
signature manifest and are compared back to that separately maintained source.
The existing Go gate also checks that manifest against the ABI. These are
artifact consistency checks, not independent semantic or Registry verdicts.
Concrete future binding, PoP/claim domain, operating chain, code/compiler/source,
algorithm manifest and full cost approval remain adoption gates.

## 1. Two input sources, one retained command per successful record mutation

The web payload remains exactly the six members binding, registry, did,
operation, expectedVersion, arguments. It accepts no actor field and create
arguments have no salt. Do not route the chain representation into that parser.

The **derived chain history command** has exactly seven members: binding,
registry, did, operation, expectedVersion, arguments, actor. The Registry
constructs binding and registry from its fixed adopted configuration, did from
its canonical Registry/agent ID, actor from its actual msg.sender, operation
from the exact function and expectedVersion from its predecessor argument.
A source authenticates that executed call; a JSON actor is never input authority.
Creation alone has expectedVersion="". Other mutations use canonical positive
uint64 decimal strings, not JSON numbers. Chain addresses are 0x plus forty
lowercase hex digits. No outer wallet owner, transaction signer, tx.origin,
claimed body, PoP or supplied digest can substitute for msg.sender.

| ABI method | operation | Exact derived arguments |
|---|---|---|
| revealClaim | create | controller, keys, services, salt |
| activate | activate | empty object |
| addKey | add-key | key |
| revokeKey | revoke-key | name |
| updateServices | update-services | services |
| authorizeOperator | authorize-operator | operator, scope |
| revokeOperator | revoke-operator | operator, scope |
| deactivate | deactivate | empty object |

controller/operator come from their exact ABI address. keys/one key map tuple
name/alg/key/signer/proof/hasExpiry/expires to the REG-01 closed accepted entry:
name/alg/key/proof/state and optional expires. Raw key/proof bytes become
canonical unpadded base64url; proof is exactly signer/value; state="accepted".
hasExpiry=false requires expires=0 and omits expires, while true includes its
exact safe integer (including zero). Services map name/serviceType/uri to
name/type/uri without other normalization. reveal salt is exactly its ABI
bytes32, base64url encoded. It is public after reveal and cannot be omitted
from retained accepted call identity. No unrevealed salt or private key is
retained or made available by a history read.

The history entry retains the existing ten members: version, previousVersion,
actor, operation, commandDigest, target, automaticRemovals, admitted,
recordDigest, grantsDigest. Its command is the derived chain object above,
not the different web six-member payload. target is null except for the exact
operator/scope object on grant/revoke. automaticRemovals contains only implicit
cleanup, not an explicitly requested revoke-operator pair. Version is the exact
successor and previousVersion agrees with the command. commandDigest is SHA256
of complete command JCS; recordDigest/grantsDigest cover complete resulting
JCS objects. All three digest strings are canonical unpadded base64url.
Neither command digest, calldata hash, transaction hash nor event topic0
substitutes for another or for an authorization/consensus proof.

Complete command and history each have 1..262144 canonical JSON bytes. The
complete REG-01 record remains at most 65536, grants at most128 pairs. These
chain history item bounds do not expand the web69632-byte input frame. A read
returns one exact version item; it never replays unbounded history or returns
all versions at once. Four reads and commitClaim create no command/version.
All accepted create/add-key/service argument collections are retained without
truncation. Any implementation must prove these item bounds cover every
otherwise admissible record/operation; until then full serializer/capacity is
NOT_RUN, not a license to reject a required case silently.

## 2. Caller-scoped multi-claim representation

Use mapping(actualCaller => mapping(recomputedCommitment => Claim)), scoped
also by this configured Registry identity and its adopted claim domain.
Claim contains commitBlock:uint256, consumed:bool, present:bool. Block zero
is valid data; present, not a nonzero block sentinel, distinguishes absence.

commitClaim inserts a previously absent exact key at the current block;
present duplicates refuse ClaimUnavailable whether pending, consumed or
expired. No refresh, deletion, replacement or renewal of that same key occurs.
A controller can commit several distinct keys; selecting one never consumes
another. Different callers' entries have no shared authority. This is a
candidate storage policy, not an assertion that it prevents independent name
competition or proves an identifier unique across Registries.

reveal derives the complete claim from Registry/agent/controller/keys/services/
salt using the future adopted domain and exact chapter09 claim schema. It
looks up actual caller + that digest and requires present && !consumed. First
require currentBlock>commitBlock; then currentBlock-commitBlock<=256. This
subtraction after comparison avoids uint256 addition overflow. A failed reveal
does not consume anything; success consumes the matching claim atomically with
creation/version1/history. Identifier/tombstone must still be absent.

There is no independently supplied commitment in revealClaim. With this
multi-claim representation, a recomputed missing key is ClaimUnavailable;
there is no stored alternative selected by the input to compare for a
ClaimMismatch branch. Keep ClaimMismatch in the existing22-error artifact as
**reserved, not emitted by this candidate**. Do not add an accepted digest,
change the function ABI or fabricate a test branch merely to emit it. Removing
the reserved diagnostic later requires an explicit simultaneous ABI/manifest/
checker/compatibility review. No current ABI change is proposed here.

## 3. Typed storage design, not finalized Source evidence

Use the locally inspected, separately reviewed abstract declaration as the
declaration candidate: typed current state plus immutable per-version command/history.
There is no duplicated cached current JSON. Public read serialization must
reproduce the exact bytes whose digest was committed at mutation admission.
Those invariants require actual code and tests later; declarations alone do
not enforce them.

Top-level roots are configuredChainId:uint256 at slot0, registryId:string at
slot1, records:mapping(string=>Record) at slot2, and caller/bytes32 claims at
slot3. The chain ID is positive, <=32 decimal digits and equals block.chainid;
registryId is exactly eip155:<chain>:<this-address>, with canonical address.
They are constructor-set storage, not Solidity immutable variables omitted
from storageLayout; no update/proxy/delegatecall setter is admitted. The
selected runtime code hash and exact initialized configuration must be bound
by the selected Source, not guessed from these root numbers.

Record uses controller:address/version:uint64/state:uint8 packed in relative
slot0 offsets0/20/28, admitted:uint64 slot1, keys slot2, services slot3, grants
slot4, usedNames slot5, usedMaterial slot6, history slot7. State0 means absent
and is used only with version0; created1/active2/deactivated3 require positive
version and controller. Controller is a principal address, not a proof of its
wallet policy. Terminal state/version and all entries/history persist. A
failed partial initialization must never leave state0 with retained data as
an admissible record. No public erase/reassignment path exists.

Key has name/alg/material/signer/proof in relative slots0..4 and hasExpiry:bool,
expires:uint64, revoked:bool packed in slot5 offsets0/1/9; stride6 slots.
Service has name/serviceType/uri (three slots). Grant address operator and
uint8 scope share one slot offsets0/20. Scope codes are internal: activate1,
add-key2, revoke-key3, update-services4, deactivate5;0 and other codes are
invalid. Public scopes remain exact strings. Sorting follows public ASCII
operator then scope, never numeric scope order. History has bytes command and
bytes entry; Claim uses uint256 block slot0 and bool consumed/present slot1
at offsets0/1. These are the six structs and28fields of the layout-only probe.

Current keys remain ASCII-name sorted including revoked entries; insertions
can move typed array slots without changing entry identity/content. usedNames
and usedMaterial are lifetime indexes keyed by exact name/raw bytes, not alg,
role, key hash aliases or just current accepted entries. Service names cannot
collide with retained keys. A new key also cannot collide with a current
service name; removing a service does not tombstone its name as a former key.
Service and active grant arrays are complete sorted bounded replacements.
Removal may shift elements but cannot fabricate grant history. The history
mapping is indexed by positive uint64 version and every1..current exists.
No read or mutation needs unbounded history traversal; a complete inspector
walk still establishes every version under an independently authenticated
selected finalized view and cannot be inferred from count alone.

Solidity string/bytes short/long encodings, mapping hashing and dynamic array
slot arithmetic follow the version-pinned Solidity0.8.20 rules. The exact
compiler/settings/source/type/layout artifacts must be retained before source
proofs. The local Paris/Shanghai layout equality is only evidence about that
probe, not operating-fork selection or actual contract storage reads.

## 4. Deterministic reached-body admission order

Compiler nonpayable/selector/ABI failures, gas exhaustion and backend faults
may precede the body. No custom diagnostic or priority is promised for those
paths; empty/unknown/panic revert remains failure. A decoded error never proves
its producer or outer-wallet/Registry outcome. The table below orders only
checks actually reached in a selected Registry execution. Implementations
must bound raw reads/copy/offset arithmetic before decoding nested values.
No allocation by an unchecked ABI length and no URL fetch/callback is allowed.

| Rank | Exact check, in written suborder | Refusal category |
|---|---|---|
| 1 | Actual length above the current-table global cap148804; then length<4; then bounded four-byte selector lookup and unknown-selector refusal; then known-operation cap/static head checks; then safe offset/length/declared nested bound checks and strict ABI padding/tail/re-encoding | BoundsExceeded; MalformedCall |
| 2 | Attached value, then configured chain ID/Registry identity | ValueNotAllowed; WrongRegistryContext |
| 3 | Agent ID/field syntax and scalar ranges, then array/count/field length caps in ABI field order; read numeric version must be positive; mutation expectedVersion must be positive | InvalidEntry; BoundsExceeded |
| 4 | Operation-specific identity/claim lookup as below | IdentifierUnavailable; WrongRecordState; ClaimUnavailable |
| 5 | Actual caller/controller or exact current grant; reveal controller must equal caller; grant changes controller-only | UnauthorizedCaller |
| 6 | Allowed lifecycle, then exact predecessor, then successor capacity | WrongRecordState; PreviousVersionMismatch; VersionExhausted |
| 7 | Reveal block comparison/window, then safe admission time, then nondecreasing time against predecessor | ClaimWindowInvalid; TimeInvalid |
| 8 | Operation targets/duplicate grants/eligible scopes; then ordered key/service name and raw material uniqueness and role/algorithm/signer/expiry syntax, then exact provisional record byte bound | KeyUnavailable; GrantUnavailable; GrantAlreadyPresent; InvalidEntry; KeyNameReused; KeyMaterialReused; UnsupportedKeyAlgorithm; BoundsExceeded |
| 9 | All signing proofs in ASCII key order, then all KEM endorsements in ASCII key order; exact eligible signer only | InvalidKeyProof |
| 10 | Complete successor, operation-specific usable-signer rule below, automatic removals, canonical command/record/grants/history construction and byte bounds | InvalidEntry; BoundsExceeded; HistoryUnavailable |
| 11 | Atomically store complete state/indexes/history/claim consumption, emit successful event, return exact successor | No partial-success category |

This fixes the global-cap/selector order without requiring an unknown
selector to supply a per-method cap. A future wider algorithm table requires
a newly reviewed cap, not an alias. Section7 specifies per-method caps and the within-row priority candidate.
Actual decoder and guard execution remain a pre-implementation evidence gate.

The operation-specific table and diagnostic rules in section7 refine this
summary; only their checked categories are mapped to a named custom error.
At rank8, a duplicate name is checked before duplicate material; duplicate
name with both current-service collision and prior-key reuse chooses
KeyNameReused first. Unsupported algorithm is checked before decoding its
raw representation/proof so there is no fallback to another algorithm.
Proof loops do not confuse lexicographic KEM-before-signer with validation
order. New signing proof verifies its original challenge/key; KEM endorsement
uses a validated eligible signing key in the same proposed/current record.
Historical revoked/expired signers retained for old proof checks do not gain
current admission authority.

For commitClaim, after ranks1..2 and fixed field framing, rank4 rejects an
already-present caller/hash; then inserts the new claim and emits ClaimCommitted.
It does not read a record, require a record clock, increment a version or
publish a record command/history. The hash is opaque bytes32 (including zero);
its actual content becomes meaningful only through a matching reveal.

For reveal, rank4 checks permanent identifier absence then matching claim
presence/unconsumed, rank5 checks controller equality, rank6 is absent/create
only (no caller-supplied predecessor), rank7 checks block window/time. Failed
proofs/oversize output still leave the claim unconsumed. Create requires at
least one proven accepted unexpired signing key at this admission time.

Other record mutations rank4 require a present record; rank5 checks authority
against that exact state/grants. Rank6 enforces the existing lifecycle table,
then exact predecessor/capacity. rank7 uses that operation's block.timestamp
in0..9007199254740991 and >=record.admitted. A record can be active but have
expired keys: controller management remains available as allowed; protected
message use does not. activate requires a usable signer, add-key can restore
one, revoke-key with none remaining atomically deactivates/clears grants. This is not a
universal usable-signer postcondition on every mutation. Create and activate
require at least one usable signing key. revoke-key evaluates remaining keys
at this admission time and, if none remain, commits terminal state/grant
cleanup in the same version. Other permitted controller management, including
authorize-operator/revoke-operator and update-services, does not become invalid
merely because time has expired every signing key. A deactivation also need
not restore a usable key. No such operation grants protected-message use to
an expired key or revives a terminal record. add-key obeys its entry/proof
rules; it does not silently gain a new whole-record signer requirement from
this summary. KEM endorsement still needs its eligible current signing key.

record returns false/empty only for proved absent identity; present terminal
records return complete bytes. activeGrants/historyItem require present
identity; absent is WrongRecordState. historyItem version>current or missing
positive retained bytes is HistoryUnavailable, not an empty entry; missing
current grants is also unavailable, never synthesized successful emptiness.
registryId reads the configured canonical ID. Reads perform bounds/context and
field checks but no controller/read ACL, mutation predecessor, time, proofs,
claim consumption or event. Public chain history cannot enforce the web ACL.

## 5. Serialization, resource and feasibility gates

Use chapter02 JCS, proper escaping and exact field presence. All public strings
here are accepted ASCII; reject invalid UTF-8/control/syntax only according
to their actual field grammar, never invent a generic unescaped-ASCII shortcut.
The serializer must escape quotes/backslash/controls correctly and reproduce
integer safe seconds, positive uint64 decimal strings, boolean fields and
canonical base64url without number/string coercion. Store both complete
command and entry only after their digests and resulting bytes are ready.
Read and write use the same explicitly reviewed serialization contract; an
independent normal oracle must check byte equality (not just hash equality).

The chain command bound covers the otherwise admissible record data without
truncation: create's keys/services/controller occur unchanged in the resulting
record; add-key's new entry and update-services' full replacement also occur
unchanged there. All other argument sets are bounded small scalar objects.
Beyond these common components, binding contributes at most256 escaped content
bytes (128 visible ASCII bytes), Registry 82, DID 156, actor 42, predecessor 20,
operation 18 and reveal salt 43, plus fixed member names/punctuation. A
conservative 2048 bytes covers all wrapper/scalar overhead; thus command size
is at most 65536+2048=67584, below262144. This is not permission to use the
chain shape as the web input. Actual serializer byte equality remains NOT_RUN.

One canonical address/scope grant pair is at most83 bytes;128 distinct sorted
pairs require at most2+128*83+127=10753 bytes. A history entry adds only bounded
scalars, three 43-byte digests, optional target and fixed member names; even a
conservative 2048-byte allowance beyond automaticRemovals keeps it at most 12801
bytes and therefore below262144. This is a byte-capacity argument, not gas,
actual storage execution or source evidence.

Full workload cost remains NOT_RUN. Published isolated strict Ed25519 and
conditional storage calculations are not a complete Registry cost, max-valid
record proof or permitted budget. Preserve required128 lifetime keys,16services,
128grants, history/tombstones and strict algorithm policy. If a selected
execution environment cannot admit a required valid case, report that
feasibility gap and obtain an explicit profile/design decision. Do not lower
limits, erase retained evidence or silently call a partial profile conforming.

Next: implement and verify the actual bounded decoder/guard behavior after
adoption; before that, finish typed layout qualification, serializer byte
examples and full valid workload design/cost;
then fixed standards/Source/version/compatibility and explicit adoption before
matching actual Registry/Go/Rust/ADK/Inspector implementation. Existing reports,
Core1.0 observations, issuer/operating/registration holds and stages9..14 remain.

## 6. Mapping artifact checks and limits

`check_chain_map.py` checks the closed metadata format, exact 13 methods,
8 record-mutation/4 read/1 claim classification, complete ordered ABI input
paths/types, field destinations, explicit web/chain actor distinction, salt,
reserved diagnostic and integer bounds. Eight finite artifact-mutation units
cover omission, destination/type/actor substitution, duplicates, bool-vs-int
limits and non-JSON/non-ASCII metadata. They do not submit these as protocol
requests, generate signatures or execute a Registry.

CI preserves actual unit/statement-coverage/result logs in the existing
candidate ABI artifact, bound to exact source hashes and Python identity.
A successful checker result means only this fixed design metadata agrees with
its stated cross-file relationships. It cannot establish serializer output,
guard runtime precedence, authority truth, source finality, full costs or any
new conformance verdict. The section7 guard design, full type/layout qualification and actual
code remain distinct from this metadata gate. The gate recomputes all13
method head/cap pairs but does not execute those decoding/guard paths.

## 7. Per-operation framing and reached-body priorities

The metadata gate also recomputes minimum static-head and conservative maximum
calldata bytes from the ordered input layouts and current bounded tuple fields.
These are byte-size bounds, not the minimum complete canonical encoding or a
promise that simultaneous maxima form an admissible REG-01 record.

| Method | Selector plus static head | Maximum complete calldata |
|---|---:|---:|
| commitClaim | 36 | 36 |
| revealClaim | 164 | 148804 |
| activate | 68 | 164 |
| addKey | 100 | 1028 |
| revokeKey | 100 | 260 |
| updateServices | 100 | 38116 |
| authorizeOperator | 132 | 292 |
| revokeOperator | 132 | 292 |
| deactivate | 68 | 164 |
| registryId | 4 | 4 |
| record | 36 | 132 |
| activeGrants | 36 | 132 |
| historyItem | 68 | 164 |

For dynamic bytes of maximum n, length plus padded content is
32+32*ceil(n/32). The current raw TABLE union uses key<=65, proof<=65, alg<=23,
name<=32, signer<=189, serviceType<=64 and uri<=2048. Key tuple maximum is
7*32+64+64+128+224+128=832. Service maximum is3*32+64+96+2080=2336.
A dynamic tuple array has a32-byte length, one32-byte offset per element and
the bounded tuple payloads; keys have at most128 entries, services at most16.
A root agentId is at most64, name32, scope15. ABI integers, addresses, bools
and bytes32 occupy32-byte words. Every table value includes the4-byte selector.
No minimum-head number authorizes padding/trailing bytes, missing dynamic
length words or any noncanonical complete input. Optional/future algorithms
cannot enlarge these bounds without a newly reviewed mapping and profile.

### 7.1 Deterministic raw preflight

After any compiler/backend preemption described above, reached-body order is:

1. Refuse actual length>148804 (BoundsExceeded), then length<4 (MalformedCall).
2. Read only the available4-byte selector. Unknown selector is MalformedCall.
3. Apply the known method's maximum cap (BoundsExceeded), then its static-head
   minimum (MalformedCall). This does not allocate by a supplied length.
4. Walk dynamic fields in ABI declaration order, arrays in index order and
   tuple members in declaration order. At each node, a missing offset/length
   word is MalformedCall. A declared count/field length above its reviewed cap
   is BoundsExceeded. Unsafe offset/length arithmetic, an out-of-input slice,
   overlap/alias/gap, noncanonical offset/padding or trailing bytes is
   MalformedCall. Check each condition in that written order. Before copying
   or decoding content, prove that node's complete range and all nested bounds.
   Finish exact canonical ABI equality after those bounded checks. No unchecked
   allocation, external URI fetch or fallback-selector scan occurs.

This is a deterministic decoder design contract; its actual code and unit-only
malformed-input scenarios remain NOT_RUN. Native nonpayable or ABI compiler
refusal may precede it and need not emit these names. Out-of-gas/empty/panic/
unknown revert is never normalized into success or a fabricated new version.

### 7.2 Shared semantic suborder and diagnostics

After framing, rank2 checks value then configured context. Rank3 walks admitted
fields in ABI order: exact ASCII/identifier/address/service-URI/scalar grammar,
then their semantic ranges (including safe seconds and positive predecessors).
Raw length/count caps have already been checked before any content parse.
Known-algorithm/role/same-record signer eligibility is rank8 rather than an
alternate parser that chooses an algorithm from raw key bytes.

Rank4 selects the authoritative current identity. For reveal, identifier absent
(including no terminal tombstone) precedes matching caller/hash presence and
unconsumed state. For other record mutations it requires a present record;
absence is WrongRecordState. A present record's missing/incoherent current
history needed for the operation is HistoryUnavailable. This does not require
unbounded replay of all old versions inside a mutation: complete retained
history is an invariant preserved by atomic code and later checked by complete
inspection. A claim commit only checks caller/hash duplication.

Rank5 checks exact principal. Grant mutations require the controller. For
other eligible mutations an exact existing operation grant can authorize the
actual caller; a PoP or wallet owner cannot. Reveal separately requires its
controller to equal caller. Failure is UnauthorizedCaller. Rank6 checks the
operation/state table, then predecessor equality, then uint64 successor
capacity. Their errors are respectively WrongRecordState,
PreviousVersionMismatch and VersionExhausted. The counter never wraps, including
for deactivate. Rank7 checks reveal's strict-later/window rule first, then safe
block.timestamp and nondecreasing admitted time. commit/read do not add a
record time or mutation-version check.

Rank8 performs the following operation-specific rules in the written order;
a rule that does not apply to that operation is skipped, never replaced by a
default permission:

| Operation | Target and entry checks after ranks1..7 |
|---|---|
| create | New key names ASCII sorted: equality gives KeyNameReused, a distinct inversion InvalidEntry. New raw-material duplicate gives KeyMaterialReused. Service names sorted/unique, collision with any retained/proposed key name gives InvalidEntry. Validate new key entries in their supplied order as below. |
| activate | No supplied key/proof or target; usable-signing rule is rank10. |
| add-key | Lifetime count at capacity gives BoundsExceeded. Prior key-name reuse gives KeyNameReused; raw-material reuse across any role/algorithm gives KeyMaterialReused; collision with a current service name gives InvalidEntry. Then validate the one new key entry. |
| revoke-key | Missing or already-revoked target gives KeyUnavailable. No newly supplied proof; the final usable-signer/terminal decision is rechecked at rank10. |
| update-services | Sorted/unique service names and retained-key-name noncollision, otherwise InvalidEntry. No grant or proof inferred from metadata. |
| authorize-operator | Target equals controller or scope ineligible for current state gives InvalidEntry; already active exact pair gives GrantAlreadyPresent; active grant count at128 gives BoundsExceeded. |
| revoke-operator | Target equals controller gives InvalidEntry; absent exact active pair gives GrantUnavailable. |
| deactivate | No new target/proof. |

The exact permitted scope strings are checked as field grammar at rank3; their
current-state eligibility is checked at rank8 for grant insertion. Created
allows only activate/deactivate grants; active allows add-key/revoke-key/
update-services/deactivate. No other target address is implicitly an authority.
There is no new zero-address principal reservation introduced by this table;
actual msg.sender and existing exact principal policy continue to apply.

For each new key, unknown or configured-unsupported algorithm gives
UnsupportedKeyAlgorithm before algorithm-specific representation decoding.
Wrong raw/proof length, role, signer reference, expiry-presence/value or other
structural entry condition gives InvalidEntry. A signing entry names its own
canonical key URL. A KEM entry names a distinct same-record eligible accepted
unexpired signing entry, with no alternate-key trial. A mathematical verification
failure under the selected strict verifier at rank9 is InvalidKeyProof. Verify
only the newly supplied proofs (all creation entries or the single add-key
entry); unchanged previously admitted entries do not create a new general
proof loop for grant/service/deactivate operations. At creation verify all new
signing proofs before any new KEM endorsement even if its name sorts earlier.

After every applicable rank8 entry/target check, construct a bounded,
noncommitting prospective record and count its exact chapter02 JCS bytes.
Reject size>65536 as BoundsExceeded before rank9 proof work. For a nonterminal
prospective successor, also apply the explicitly future-profile headroom check
in section8, after its actual-byte check and before any proof. This is a new
admission narrowing proposed here, not an added0.10.0 consumer rule. The global raw
ABI cap alone does not imply the record bound. New keys are only provisionally
represented as accepted for byte counting; this is not proof validity, signer
admission, durable state, a digest authority or a success event. For byte counting, a revoke-key/deactivate prospective record may project the
exact terminal state from its already admitted retained keys and the same
admission time; this is not an early committed lifecycle decision. Rank10
rechecks the final operation-specific state and grant cleanup after all proofs.
Do not publish or store it before all remaining guards succeed. The exact serializer remains
an implementation/test gate; an estimate must not silently reject an otherwise
valid record. Retain rank10's complete final-state/digest/byte-bound recheck.

Rank10 constructs the full successor and applies the explicitly operation-specific
usable-signing rules: create/activate require one; revoke-key with none remaining
commits terminal state and all grant removals; other permitted management is not
refused merely because keys expired. Apply activation cleanup of activate grants,
deactivation cleanup of all grants, then encode the complete record, grants,
command and history in that order. Encoded bound failure is BoundsExceeded;
a violated successor invariant is InvalidEntry; missing required retained data
is HistoryUnavailable. No arbitrary local exception is relabeled as one of these
without its checked cause. At rank11 commit all effects and one event atomically.
Explicit revoke-operator target is not duplicated in automaticRemovals.

### 7.3 Operation applicability, reads and reserved diagnostic

| Surface | Applicable reached-body ranks |
|---|---|
| commitClaim |1..3; rank4 duplicate caller/hash, then atomic claim insert/event. No record/version/time/key proof/history command |
| revealClaim |1..11; rank6 create-absence semantics only, not a supplied predecessor |
| other seven record mutators |1..11 with only their operation-specific targets/proofs/successor rules |
| registryId |1..3/context, then exact configured ID; no record lookup or event |
| record |1..4/context; proved absence returns false/empty; otherwise complete terminal/current record |
| activeGrants |1..4/context; absent identity is WrongRecordState; missing complete grants is HistoryUnavailable |
| historyItem |1..4/context; absent identity is WrongRecordState; requested version>current or missing retained positive item is HistoryUnavailable |

Reads impose no controller/web read ACL, mutation predecessor/time/key proof or
claim consumption. A syntactically invalid requested version fails at rank3
before lookup; positive but unavailable version fails at the history step.
Source/finality/readiness is an external authenticated evidence requirement,
not established by these Solidity return bytes or a custom error selector.
ClaimMismatch remains reserved/not emitted in this multi-claim candidate.

This is a candidate diagnostic priority definition, not observed runtime
coverage or a guarantee that a later compiler body is reached. New implementation
must apply fixed unit scenarios for simultaneous failures and safe owned normal
EOA/wallet lifecycle/history runs before it can claim this behavior.

## 8. Proposed terminal/version byte headroom — explicit future narrowing

The existing record ceiling alone does not reserve bytes for a later root
state/version change. For unchanged content, active→deactivated adds5 JSON
content bytes; a version digit boundary can also add bytes. A record at the
ceiling could therefore prevent a required terminal successor even without
adding a key/service. No packet, signing or runtime reproduction is needed to
state this byte-capacity issue.

This **unadopted future-profile proposal adds an admission restriction**. For
every nonterminal prospective successor, after checking its actual complete
JCS length<=65536, make a temporary size-counting copy with only root version
replaced by the string "18446744073709551615" and root state by "deactivated".
Require this copy's exact JCS length<=65536, otherwise BoundsExceeded before
proof work. Apply this at create and every later nonterminal successor,
including add-key and update-services; no alternate enrollment/update path
skips it. Never revive a revoked key to count space or drop retained fields.

This is at most24 additional bytes for an active record with a one-digit
version (5 for state and19 for version). Created needs at most23 (4+19).
The exact temporary encoding decides the check; an unconditional24-byte
subtraction is not an equivalent implementation. Terminal successors require
the actual record bound but no future headroom, since they cannot mutate.

The temporary object is never an admitted record, accepted command, stored
history entry, event, PoP/claim input, signature or recordDigest. Only the
actual successor is stored and hashed. This invariant prevents size growth
from these two metadata fields alone when key/service/controller/id values
are retained. It does not guarantee future arbitrary additions, gas funds,
clock/source/authority readiness or counter availability. In particular the
maximum uint64 version still refuses every mutation, including deactivate;
this reservation introduces no version-exhaustion bypass or liveness claim.

This restriction excludes some boundary records that the0.10.0 byte ceiling
alone would admit. Do not silently call the admission sets identical, apply
the new check when reading old0.10.0 records, reclassify existing frozen results
or change an existing deployment. Explicit future profile/version/domain and
new Registry/identity, compatibility/migration policy and adoption must account
for it. Existing retained records must not be truncated or rewritten as a
migration shortcut. Actual reservation serializer/transition tests and matching
Registry/Go/Rust/ADK/Inspector support remain NOT_RUN until implementation.
