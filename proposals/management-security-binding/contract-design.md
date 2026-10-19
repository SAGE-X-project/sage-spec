# Typed Registry ABI and storage design candidate

Status: **UNADOPTED future-version candidate**, draft revision 3. The
[ABI JSON](contract-abi.json) and separately authored
[complete method schemas](contract-signatures.json) specify thirteen typed
function candidates: nine write surfaces and four reads. They are not deployed
code or a complete chain binding. No future release/profile/domain identifier,
network, address, finality source or operating custodian has been selected.
The 0.10.0 specification, contracts and all old findings remain unchanged.

## 1. Typed operation mapping

| Candidate function | Semantic operation and exact predecessor |
|---|---|
| commitClaim(bytes32) | Sender/Registry-scoped commitment; no public record mutation or record-version increment |
| revealClaim(string,address,Key[],Service[],bytes32) | Create the prechosen agent ID after matching claim; implicit empty predecessor/absent DID; return version 1 |
| activate(string,uint64) | Activate the named created record at exact positive predecessor |
| addKey(string,uint64,Key) | Append one accepted immutable entry to active record |
| revokeKey(string,uint64,string) | Revoke exact key name under the explicit candidate lifecycle table |
| updateServices(string,uint64,Service[]) | Replace the whole services array |
| authorizeOperator(string,uint64,address,string) | Controller adds one exact operator/scope pair |
| revokeOperator(string,uint64,address,string) | Controller removes one exact active pair |
| deactivate(string,uint64) | Terminal deactivation with atomic grant cleanup |

Each mutator except commit returns the exact uint64 successor. Previous
versions are strictly positive; create's empty predecessor is selected by the
reveal function, never a uint64 zero alias for an existing record. There is no
direct create shortcut, owner-transfer/recovery, blanket approval, relayer,
proxy admin, arbitrary execution, delegatecall or payable entry in this ABI.
The ABI contains no fallback/receive entry. Unsupported selectors/nonzero
value refuse; a typed ABI declaration alone does not enforce that behavior.

Agent ID is 1..64 ASCII characters under chapter 09; full Registry/DID context
comes from the configured chain/this contract and is independently checked by
the client/source binding. The runtime chain ID must remain the configured
chain ID. Controller input at reveal must equal the authenticated sender; it
is in the claim, not a substitute for sender authorization. Operators map to
lowercase address strings for public/management representations and have the
exact scope strings from chapter 09. Do not case-fold or reinterpret arbitrary
web actor identifiers as chain addresses.

Key is (name,alg,key,signer,proof,hasExpiry,expires), with the exact tuple order
in the JSON. Raw public key/signature bytes map to canonical unpadded base64url
in the record. Signer is the full canonical key URL, not a wallet address.
State is implicit accepted for new entries. Expiry absence is hasExpiry=false
and expires=0; present zero is distinct and already expired. Every present
expiry is at most 9007199254740991 even though ABI uint64 is wider. Strings,
key/proof sizes, accepted algorithms and roles remain explicit semantic checks.
Service is (name,serviceType,uri); serviceType maps exactly to record member
type, without renaming it in the canonical public record. Arrays are sorted
by ASCII name; names and raw key material are unique for the record lifetime.

## 2. Canonical encoding and authenticated sender

Use the [Solidity 0.8.20 ABI specification](https://docs.soliditylang.org/en/v0.8.20/abi-spec.html)
for tuple expansion, offsets, padding and selector derivation. This is a pinned
encoding reference, not the future implementation compiler selection. A client
constructs exactly the selected method's canonical encoding. A future contract
checks complete length/canonical re-encoding, unknown selectors, offsets,
lengths, padding and dynamic tails before admission. Solidity's ordinary
decoder alone is not a promise of strict canonical decoding or trailing-byte
rejection. Input allocation/work is bounded before expensive proof work.

The contract's exact `msg.sender` is the actor for both EOA and contract-wallet
calls, as selected in [account-binding.md](account-binding.md). No body, PoP,
callback, log, claimed recovered key or `tx.origin` replaces it. Reveal's
controller equals that caller; current controller/grants and predecessor are
checked at the mutation's serialization point. Commit and reveal are bound to
the same caller even when different outer transactions execute the wallet.
No code-size or transaction-origin EOA restriction is introduced. A wallet's
own upgrade/signature/owner policy is outside Registry authentication; the
address does not attest those properties.

The earlier EOA-only gate is superseded in this future candidate. Accepted
transaction types and the validation source's exact executed-call/state/history
evidence remain unfinished gates: a selector, RPC `from`, outer transaction
signer or receipt alone does not prove the Registry caller or command. Forwarded
identity substitution and wallet-signature callbacks are not added to this ABI.
Transaction nonce, record predecessor and caller-bound claim commitment retain
their distinct replay roles. No ABI selector/tuple changes follow from selecting
this address-based account policy.

## 3. Record, grants and complete history storage

The storage design requires one immutable Registry identity, records keyed by
canonical agent ID, lifetime name/material indexes, immutable key entries with
revocation state, sorted services, current exact scoped grants, every mutation
history/accepted-command pair and permanent terminal identity tombstones.
Commitments are separate sender/Registry-scoped records with commitment block
and consumption state; consuming one and creating the record are atomic.
Reveal is strictly after the commit block and no later than commitBlock+256;
overflow/expiration and duplicate names refuse, with separate activation.

Every successful mutation produces one successor and one complete history
entry under [lifecycle-and-schemas.md](lifecycle-and-schemas.md). Record, grants,
history, automatic removals and tombstone change atomically before success.
A failed/reverted operation publishes none of them as a success. Loss of durable
outcome/readiness is not absence and cannot authorize retries with a fabricated
version. Expiry alone is not a stored mutation. The terminal version cannot be
reused and the uint64 maximum cannot wrap.

The public reads return exact canonical UTF-8/JCS bytes from one selected
finalized block. record returns (false,empty bytes) only for proved absence;
a present record returns (true,complete REG-01 bytes), including deactivated
records. activeGrants is the complete sorted canonical array; historyItem is
one exact canonical history entry and its accepted semantic command at that
version. Missing/unknown history or grants for an absent record refuses rather
than returning fabricated emptiness. registryId returns the immutable identity.
Read methods never themselves prove finality, freshness, trusted origin or
readiness. The selected source must bind all calls to one finalized block,
code/ABI and Registry policy; unproved or conflicting observations fail closed.

On-chain history cannot enforce the private web read ACL and is publicly
observable. History contains no private credentials/session secrets. Mapping
accepted ABI arguments into the complete semantic command, future binding and
PoP/claim domains, exact storage slots/proofs, bounded history reads, event and
revert/error schemas remain design gates. The ABI read return shapes do not
pretend those backend details or privacy costs are solved.

## 4. Crypto and cost gates

Ed25519 verification is mandatory under the eip155 Registry baseline. Every
accepted optional signature algorithm needs its actual strict verifier; reject
unsupported names rather than storing an accepted unverified proof. A signature
length check, wallet recovery or owner approval is not Ed25519 verification.
An X25519 entry is endorsed by an eligible signing key; it does not sign its
own proof and endorsement does not establish KEM private-key possession.
Account transaction authentication is separate from these SAGE key roles.

Before implementation select/review the actual verifier and its exact RFC8032
acceptance policy, dependencies/license and source pin. Measure create/add-key/
revoke/large-record/history work and storage, supported maximum sizes, compiler/
optimizer/runtime code size and worst-case gas against a concrete candidate
execution environment. No precompile availability, gas figure or deployment
budget is assumed here. If a candidate cannot meet the required algorithms or
bounds, report the feasibility gap; do not weaken PoP, remove tombstones, cap a
required case silently or reclassify the deployment conforming.

## 5. Artifact checks and remaining work

The ABI checker resolves the existing Go core module's go-ethereum dependency
in remote CI. Core main and the selected Go toolchain can move; each receipt
records their observed identities and the core go.mod/go.sum hashes. This is
not an immutable pre-pinned environment: actual dependency/module metadata
must be freshly reviewed for each accepted run. The old vector gate is unchanged.
It parses the typed ABI, compares separately authored complete method schemas
including ordered input/output names, types, recursive tuple layouts and mutability,
derives collision-free four-byte selectors and checks ordinary ABI calls against
independent fixed encoding examples. Unit tests exercise artifact/CLI failures.
The signature manifest is authored separately from the ABI, not generated from
it. Each entry has exactly signature, mutability, inputLayout and outputLayout;
layouts are ordered preorder paths (entry.name or keys[].name for children).
Selectors cover input types only, so return layouts require this separate check.
Artifact JSON uses exact case-sensitive keys, required non-null scalar/array
kinds, decoded duplicate rejection and printable ASCII strings. The ASCII bound
is only for these design files, not a restriction on general protocol JCS data.
Escaped unpaired surrogates and replacement/non-ASCII characters are rejected.
Its output/coverage/source receipt is design-artifact evidence, not execution
of these Registry functions, transaction authorization, proof verification,
strict hostile-input decoding, storage correctness or gas measurements.
No exploit client/service or chain transaction is executed by this checker.

Complete transaction/account binding, per-operation semantic command mapping,
exact storage/events/errors, actual algorithm verification and costs, selected
finality source, concrete version/domain/compatibility/adoption and independent
Inspector integration remain. The current four documentary failures and all
old implementation findings stay associated with their existing subjects.
