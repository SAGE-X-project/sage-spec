# Candidate management authentication and fork bindings

Status: **UNADOPTED future-version candidate**, draft revision 1.
Baseline sage-spec main `6d611b19764cfae50936ab4c63dbe4e1f9f78487`,
SAGE 0.10.0. On 2026-10-19 the project direction was selected: preserve
0.10.0, design new security rules as a separate version candidate, preserve
existing Registry contracts, and design/verify a new contract before any
separate deployment decision. No release number, operating network, ABI,
trust root, key custodian or address is selected by this direction.

This directory does not change the adopted specification or certify an
implementation/deployment. The separate documentary baseline remains
26 PASS / 19 NOT_APPLICABLE / 4 FAIL / 2 NOT_RUN. Earlier documentary and
runtime reports keep their original subjects and results. No new conformance
verdict follows from publishing or checking these proposal files.

The [read-only history candidate](web-history.md) supplies the missing web
inspection/recovery exchange. The [verification and adoption plan](verification-plan.md)
identifies the still incomplete chain ABI, finality-source artifact and tests.
There is no protocol implementation or executable attack demonstration here.

## 1. Selected design direction and compatibility boundary

Keep the descriptive threat/privacy/resource analysis separate from new
management or source restrictions. The former explains current behavior;
wire bytes, accepted inputs, authentication choices and versions remain
unchanged. It can receive a separate documentary review without claiming
all seven findings closed.

For the management gap, propose two explicitly selected bindings: a direct
mutually authenticated web management channel with complete command framing,
and a direct authenticated chain-transaction binding with a published ABI.
Neither changes application-message RFC 9421, HPKE, DID projection or the
approved 0.10.0 alg/kid/JSON-LD recommendation policy. A deployment cannot claim
the proposed binding merely because its existing generic transport is TLS.

The concrete web framing below, restriction to direct full handshakes and
new fork acceptance conditions create new acceptance/rejection rules. They
must not be merged into 0.10.0 as PATCH clarifications under OVERVIEW-03.
No release number is selected here. The selected direction permits a separately versioned design; adoption still
needs a concrete release/profile identifier, compatibility inventory and review
before implementation. The old profile and old evidence remain identifiable. The chain ABI
is still a design dependency below, not a fabricated finished binding.

## 2. Proposed web management binding: exact command on its authenticated channel

This is an optional proposed management channel, separate from REG-08 public
HTTP record retrieval. It does not make mTLS mandatory for every SAGE client,
message, deployment or Registry profile.

### 2.1. Trusted configuration and channel

A management endpoint configuration identifies the binding revision, exact
registry ID, permitted DNS server name/address/port, trusted server roots,
client CA roots, and a single-valued map from SHA-256 of a complete client leaf
certificate's DER bytes to an ASCII actor identifier. Actor identifiers obey
chapter 09 section 9 bounds and exact equality. More than one credential may deliberately
represent one actor during configured rotation, but one credential cannot map
to different actors. A certificate never grants a lifecycle scope by itself.
All trusted configuration is protected, versioned and checked for rollback.
No actor, root, registry ID or target endpoint is learned from a Card or body.

The client validates the server certificate chain, validity, DNS identity and
configured endpoint, with no insecure fallback or redirect. The server checks
the client certificate chain, validity, intended client authentication usage
and exact leaf pin. Both endpoints use their trusted clocks. This proposed
binding selects TLS 1.3, a fresh full mutual handshake, no resumption/early
application data, no renegotiation/post-handshake identity changes, and no
terminating forwarding proxy. A TCP load balancer that preserves the end-to-end
TLS bytes does not derive authority. A later proxy/resumption alternative would
need its own complete principal/command-binding rules, not forwarded identity
headers. These are proposed restrictions, not facts about the existing TLS1.2+
reference APIs.

One channel carries exactly one command frame and one response frame, then
closes. Actor and byte stream remain attached in a non-transferable trusted
session object; a body or second connection cannot replace either. A bounded
handshake plus read/write deadlines and deployment resource budgets apply.
At the final serialization point, the server checks the current trusted
credential configuration generation and leaf pin/validity again. A changed or
revoked pin, expired certificate, lost configuration/clock, stale authority or
closed session causes refusal. A channel snapshot cannot authorize a later
command after credential retirement. CA or actor-key compromise remains a
trust-boundary failure until trusted credential/pin replacement; a valid stolen
key can authenticate an adversary. This mechanism does not attest program
integrity or human intent and does not automatically check external revocation
services. Credential retirement here is enforced by current explicit pins.

### 2.2. Proposed framing and complete command schema

A frame is an unsigned four-byte big-endian length followed by exactly that
many bytes, with content length 1 through 69632 inclusive. Read limits apply
before allocation/JSON parsing. The payload is one strict UTF-8 JSON object
under chapter 02, serialized as JCS; received bytes must equal that object's
JCS bytes. Invalid UTF-8, duplicate/unknown/missing fields, noncanonical bytes,
extra bytes inside the declared payload and unknown operations are refused
before authorization. The session dispatches at most its first valid frame;
trailing frames can never dispatch a second operation. EOF before the complete
first frame refuses without mutation. Frame length is not an HTTP content
length and cannot be silently accepted on the public read endpoint.

The object has exactly `binding`, `registry`, `did`, `operation`,
`expectedVersion`, and `arguments`. `binding` is the exact selected future
binding identifier and revision; it is not an automatic alias for 0.10.0.
`registry` must equal protected endpoint configuration. `did` is a canonical
full DID in that registry and is the same DID used for authorization and state
lookup. No body `actor`, authorization claim or alternative version is accepted.
`expectedVersion` is the canonical current decimal string, except create uses
exactly the empty string. It is checked at the atomic admission point.

| Operation | Exact arguments members and existing semantic source | Actor and prior state |
|---|---|---|
| create | `controller`, `keys`, `services`; REG-01 encodings/bounds, proposed DID and all proofs; candidate starts at version1/state created | Actor equals proposed controller; DID/tombstone absent; no operator creation |
| activate | Empty object | Controller or current `activate` grant; created |
| add-key | `key` containing exactly one REG-01 key | Controller or current `add-key` grant; active |
| revoke-key | `name` using key-id grammar | Controller or current `revoke-key` grant in active state; controller-only revocation in created state remains an explicit unresolved lifecycle interpretation of REG-03. Retain the immutable entry; atomically deactivate if no usable signing key remains. Adoption is blocked until that interpretation is resolved without silently changing 0.10.0. |
| update-services | `services`, the complete REG-01 array | Controller or current `update-services` grant; active |
| authorize-operator | `operator`, `scope` as chapter 09 section 9 | Controller only; created/active, exact state-eligible scope |
| revoke-operator | `operator`, `scope` as chapter 09 section 9 | Controller only; created/active, exact active pair |
| deactivate | Empty object | Controller or current `deactivate` grant; created/active |

The authenticated stream is parsed once into an immutable bounded command.
Registry/DID/operation/version/arguments passed to the durable transaction are
those exact parsed fields, not values recreated from model content, a mutable
caller object or a route after admission. This binding does not authorize
recovery/controller transfer, new fields or operators delegating further.
REG-01 immutable material and chapter 09 section 9 state/grant/atomicity rules still apply.
Encoding and state validation must be shared or independently tested to avoid
a second parser authorizing a different command from the channel's bytes.

### 2.3. Atomic authorization, replies and retries

In one serialization transaction, obtain current credential configuration,
record/version, grants, ordered history and tombstone. Check the current pin
and exact actor, expected version, operation eligibility, scope, all arguments,
proofs and successor invariants. For an operator, inspect the exact current
controller-authorized grant for this DID/registry/operation. Never accept the
existing reference session's delegated=false as evidence of operator support;
this proposal requires a new complete admission integration. A revoke that
linearizes first denies the later operator write.

Commit next record/version/grants/history/tombstone durably together before a
success response. Preserve each command's normalized fields and authenticated
actor in access-controlled management history; never retain private credentials.
Required integrity history is distinct from optional traffic logs. On failure,
none of those committed values change. Loss/ambiguity of durable commit
quarantines dependent writes and public success until trusted recovery proves
one complete state; a lost response is not proof of non-commit.

A proposed response is a single frame on the same TLS session containing an
exact bounded JSON object: `binding`, `registry`, `did`, `commandDigest`,
`outcome`, `version`. The digest is canonical unpadded base64url SHA-256 of the
exact accepted command payload bytes. `outcome` is `committed` only after
complete commit, `rejected` only for proven non-commit, or `unknown` while
quarantined; `version` is the proven committed/current decimal version, or the
empty string for absent/unproven state. A decoder checks binding/context/digest
before using the response. This is authenticated channel evidence, not a
transferable object signature or public non-repudiation proof. It is not an
RFC 9457 HTTP response. The separately framed, authenticated read-only exchange in
[web-history.md](web-history.md) is the candidate inspection/recovery interface.
It has no write authority and has not been implemented or runtime-validated.

TLS protects this connection, while expected version/state/tombstone protect
repeated commands on another connection. A retry of create cannot reuse a DID;
a repeated mutation cannot commit twice at the same version. After response
loss, inspect trusted state/history and the exact command identity before any
new command; never fabricate a higher version or assume a different payload
with the next version is a retry. Do not promise an arbitrary retry is safe
merely because the channel is fresh.

## 3. Proposed chain binding scope and exact remaining ABI dependency

Select direct externally owned account transactions on the configured chain
as the initial candidate; no meta-transactions, trusted forwarders, proxy
upgrades, account abstraction, multisig-contract caller or relayer substitution
is silently supported. Those alternatives need their own complete binding.
This restriction changes which deployments/actors can claim the new binding;
it cannot be retroactively inferred from REG-06's current account-address rule.

A selected transaction format must authenticate chain domain, nonce,
destination, value and complete calldata. For example, EIP-1559 type2
signatures cover the type byte and their listed chain/nonce/destination/data
fields; EIP-155 describes a different legacy transaction construction.
One does not reinterpret the chain transaction signature as a SAGE
RFC9421 signature, PoP, EIP-191 message or a trial of multiple algorithms.
Exact legacy/type acceptance must be stated in the adopted binding, not guessed.

The trusted node validates the transaction and chain; the contract authenticates
the actual transaction sender, its own configured registry/chain and executed
code. Client expected registry destination/code/chain/finality must all agree.
The public controller is that exact sender for create; every subsequent actor
is the actual authenticated sender, checked against current controller/grants.
Body controller fields and recovered PoPs never replace it. A proof does not
authorize arbitrary creation. Nonzero-value calls, unsupported selectors and
ambiguous decoding need explicit binding rules rather than implied support.

The ABI must be published as a pinned artifact with a per-selector mapping of
all eight operations above plus commit/reveal. Each entry needs canonical
argument types, dynamic offsets/lengths/trailing bytes, DID/registry mapping,
expected empty/create versus exact previous version, all key/proof/expiry and
service fields, output/revert semantics, events and atomic state/history/grant
storage rules. Its actual selectors, byte encoding and code hash are NOT defined
by this proposal and therefore the chain binding is NOT complete. Merely writing
that mapping must exist does not close security.5/.6 for eip155. The selected new-contract design direction keeps the legacy deployment intact.
The ABI acceptance checklist in [verification-plan.md](verification-plan.md)
precedes implementation and deployment; existing code is not certified.

The existing claim commitment remains SHA-256/JCS over its exact REG-06 fields
including secret random salt. Associate the commitment with authenticated sender
and registry. Reveal by that sender occurs after commit block and within256
blocks, consumes the matching commitment and creates the record atomically.
Activation remains separate. Transaction nonce and expected record version have
different replay roles; both are required by their own layer. Chain-ID replay
protection does not distinguish forks that retain that ID.

A successful RPC submission or pending receipt is not finalized registration.
A reverted transaction publishes no registry mutation. The client associates
exact transaction hash, selected canonical inclusion block, successful execution,
expected version/history and finalized ancestry before claiming that change
observed. On uncertain receipt/inclusion, inspect trusted state/history and
quarantine dependent success; never resubmit a changed command with an invented
version. Operational costs/finality/provider custody remain unselected.

## 4. Proposed fork disambiguation contract

A trusted branch policy contains protected chain ID, genesis identity,
registry address/code policy, a specific finalized anchor block hash/height,
authenticated validation-source identity and a precise consensus/finality rule.
A genesis value alone is insufficient for later forks, and an anchor cannot
distinguish two branches that diverge after it. A returned hash is not proof
that the returned branch is the configured authority.

For an observation, establish that its finalized block descends from the
accepted anchor through validated ancestry under the selected consensus rule,
with one coherent state proof/source observation for the exact Registry code
and record. A validated local node can supply consensus/ancestry checks; a
trusted resolver alternative explicitly trusts its authenticated attestations
and configured identity, not an arbitrary RPC's word `finalized`. The exact
chosen consensus verifier or resolver attestation format/policy still needs a
binding artifact and tests; none is selected by this proposal.

Persist accepted finalized anchors, source/policy generation and highest record
versions durably. A restart cannot reset these to accept an older branch.
Conflicting finality at an accepted height, non-descendant observation, missing
ancestry, unavailable validation or unproved rollback makes readiness false and
causes refusal. If two branches both descend from the old anchor but have
incompatible newly finalized blocks, quarantine instead of choosing by highest
height/version, first response, majority of untrusted endpoints or cheapest
RPC. A hostile trusted authority remains a stated assumption, not detected by
this policy without independent evidence.

Only explicit authenticated reconfiguration can resolve a quarantined branch.
Record old/new policy and anchors, reason and authorizer; stop dependent
operations while new readiness and necessary record/grant/history continuity
are established. Never silently transfer irreversible tombstones/identity claims
to a conflicting Registry state or use reconfiguration to resurrect a key.
Concrete anchor values, validator trust, provider selection, persistence/custody
and an actual fork incident require operating decisions/evidence. This proposal
is a candidate means and remaining evidence contract, not a completed fork test.

## 5. Planned verification and decisions

| Group | Required positive evidence | Refusal/unit-only scenarios; no exploit tooling |
|---|---|---|
| Command framing/principal | Exact immutable payload from owned mutually authenticated channel reaches one atomic admission; all operations with controller and permitted operators | Duplicate/unknown/malformed/truncated/second frame, wrong context/version/body actor, different stream, stale credential configuration or expired leaf: no unauthorized dispatch |
| Atomic grants/replay | Current permitted scope succeeds; one version/complete durable history change; separate read-only inspection | Concurrent same version, revoke-before-write, operator creating/delegating, stale grant, capacity/uncertain/restart state; no partial success |
| Authentication | Correct root/name/leaf and protected-current generation; explicit new binding revision | Unknown certificate, retired pin, invalid clock, forwarder identity substitution, closed session; existing controller-only code is not all-operation evidence |
| Chain | Published ABI artifact and exact selectors/argument round trip; trusted sender, chain and code; correct finalized inclusion | Calldata/context/nonce/version substitution, wrong sender, unbound relayer/proxy, wrong code/branch, uncertain receipt. Fixed simulator/unit only for attack-capable cases |
| Fork | Authenticated configured anchor/source, validated descent/finality, restart persistence and explicit trusted reconfiguration | Same-genesis post-anchor divergence, conflict/rollback, unavailable ancestry, stale source generation: fail closed, no automatic selection |

Before adoption: independently review the read-only history candidate and finish the exact chain ABI;
review all operations and binding schemas; finish profile/version compatibility under OVERVIEW-03 and review the selected
new-contract migration direction without deploying it. Afterwards: version-matched independent documentary review,
implementation, unit and safe owned-runtime tests, Inspector subject/evidence,
full CI and separate main execution. No old frozen verdict is overwritten.
The issuer two obligations, operating-history ten, deferred registration fifteen,
0.10.0 three recommendation causes and all other stage7/8 items remain separate.


## 6. Standards application and unresolved adoption gates

[TLS 1.3, RFC 8446](https://www.rfc-editor.org/rfc/rfc8446.html), sections
4.4, 4.6 and 8, supplies channel authentication and the resumption/early-data
context. Fresh mutual handshakes and one request per connection are this
candidate's application restrictions; TLS itself also supports other modes.
Certificate-to-actor authorization, read ACLs and durable command atomicity
are application responsibilities. A channel does not attest a compromised
endpoint or produce a transferable signature over its history.

[JCS, RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html), section 3,
supplies canonical JSON serialization. Chapter 02 and this candidate supply
closed schemas, bounds and duplicate rejection before member loss. Decimal
versions and offsets are strings, avoiding conversion to inexact JSON numbers.

[EIP-1559](https://eips.ethereum.org/EIPS/eip-1559) defines type-2 transaction
signing fields. It is an example under consideration, not automatic support
for every transaction type or account model. The eventual ABI uses the
[Solidity ABI specification](https://docs.soliditylang.org/en/latest/abi-spec.html)
with a pinned compiler/tool specification and exact artifact; that reference
alone does not define SAGE selectors, authorization, strict decoding or costs.

RFC 9421 application-message signatures, HPKE KEM key roles, public record
reads, DID projection and A2A requests retain their adopted contracts. This
management candidate neither replaces nor silently widens those profiles.
The remaining four documentary findings stay open until a versioned subject,
complete web/chain/fork contracts and independent evidence support a new
finding. The two actual issuer obligations and all existing runtime gaps
remain separate.
