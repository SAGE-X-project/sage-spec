# Future binding verification and contract design plan

Status: **UNADOPTED design and evidence plan**, draft revision 4. This plan
implements the selected design direction, not an adopted wire standard,
finished ABI, release, contract implementation or deployment approval.

## 1. Compatibility and adoption gates

Freeze the existing 0.10.0 normative files, history, vectors and Inspector
subjects. Proposed behavior uses a separately identified future profile and
release; its final identifier and number are not assigned here. No automatic
upgrade, fallback from failed candidate authentication to the old binding,
or reinterpretation of a 0.10.0 Card/record selects this candidate. A caller
explicitly configures the supported profile and rejects mismatches. Any shared
format reuse is reviewed field by field, not inferred from equal key lengths.

Before implementation, inventory Client/server, Go/Rust core, ADK, SDK/MCP,
Registry read/write adapters and Inspector callers; publish an old/new
compatibility table, selected identifier/domain separators and independent
review. 0.10.0 PoP/claim strings in the candidate are inherited baseline
references, not newly assigned future-version domains. Whether a future
binding deliberately reuses them needs explicit scope/replay review. Publishing
this proposal cannot select those bytes for an interoperable implementation.

The 0.10.0 alg/kid/JSON-LD recommendation decision remains unchanged.
All old FAIL/PARTIAL/UNSUPPORTED/NOT_RUN results stay associated with their
old subjects. A future review uses exact new normative revision, source,
observer and runtime evidence; it cannot relabel an old gate by editing an
expected outcome. Four remaining documentary failures stay open.

## 2. New Registry contract design, preserving existing deployments

Design a new contract alongside the current one. Do not upgrade a deployed
proxy, reuse an old address as equivalent, alter ownership, deploy or send a
transaction under this design authorization. Evaluate the old deployment's
actual code/ABI/semantics separately; its historical operation is preserved.
Existing deployments are not declared conforming or unusable without evidence.

The next design artifact is a pinned ABI plus state/storage mapping for a
new non-proxy EVM Registry candidate. This describes a review candidate,
not a selected operating network. The contract artifact must settle:

| Surface | Required exact design/evidence before implementation |
|---|---|
| Commit/reveal and create | Canonical selector/type definitions; sender-scoped claim; exact commitment fields/domain; reveal strictly after commit block and within 256 blocks; atomic one-time consume/create; minimum proven signing key and separate activation |
| Lifecycle operations | Selectors and argument maps for activate, add-key, revoke-key, update-services, authorize-operator, revoke-operator and deactivate; apply the explicit candidate created-state controller revoke-key rule; overflow/expiry/terminal-state rules |
| Canonical decoding | Exact selector, argument types and order, dynamic offsets/lengths, text encoding, duplicates/sorting, lengths before work, trailing bytes and value rules. Prove encode/decode round trips; reject ambiguous alternate encodings without executing adversarial payloads |
| Actor and grants | Exact Registry msg.sender-to-controller/operator mapping for both EOA and contract-wallet callers under [account-binding.md](account-binding.md); caller-bound commit/reveal, registry/chain binding, eligible states/scopes, current grant at serialization and atomic revoke-before-write. No tx.origin/body/recovered signer replacement, PoP authorization, implicit forwarder or operator delegation |
| Records and proofs | Exact record-to-storage mapping and independent re-encoding, lifetime key count/name/material uniqueness, algorithm/role separation, Ed25519 support and all accepted algorithm verification; KEM endorsement distinguished from possession |
| Version/history | One uint64-range record increment, exact predecessor, history entries for all successful mutations/grant changes/automatic removals, retained tombstones, atomic public reads, restart/reorg treatment and complete authenticated inspection mapping |
| Returns/errors/events | Exact outputs and revert/error semantics with no state/event success on failure; typed events distinguish management operations; logs alone are not authoritative full storage/history or finalized execution |
| Code and costs | Pinned compiler/optimizer/dependencies, artifact and deployed runtime code policy, no unreviewed upgrade path, bounded gas/storage/verification work, capacity and latency measurements. Do not presume native Ed25519 verification availability or affordable gas |
| Read/finality mapping | Record, grants and history at one finalized block; exact storage/proof or trusted-node observation mapping; chain/address/code/ABI identity and readiness. Arbitrary RPC data is not proof |

A plain ABI JSON file is insufficient without this semantics map. Conversely,
a table of required selectors is not the ABI. The typed ABI and normal codec artifact now begin that work, as explained in
[contract-design.md](contract-design.md). Remaining semantics, contract code,
proof verification, costs and deployment data are not supplied by ABI checks.
The account policy is selected: both EOA and contract-wallet addresses may be
actual callers. Its unit/normal-runtime evidence remains NOT_RUN. No library
qualification or ABI codec check substitutes for that evidence. Any future
change to caller interpretation or Registry upgrade model needs a separately
reviewed candidate rather than silently widening identity substitution.

Migration preparation includes deterministic export/import comparison of
public records, historical key tombstones, grants, history and authority;
explicit old/new identities and re-enrollment rules; incompatible proof/domain
re-issuance; independently checked transition observations and user-owned
private keys remaining under their existing custody. Copying data does not
prove controller ownership or continuity. Never silently redirect old DIDs,
reuse immutable names or let two new registries share an identity. Actual
migration requires a separately approved procedure after artifact validation.

## 3. Finality-source and fork artifact

Finish one concrete source binding before code: either a self-validated node
with its precisely selected consensus/finality and validated ancestry interface,
or an explicitly trusted resolver with authenticated attestation encoding,
identity, context/expiry, version and anti-replay rules. These are alternative
trust models, not interchangeable proofs. No source is selected here.

Publish protected policy fields for chain/genesis, registry/address/code,
accepted anchor hash/height, source identity and generation, finality method,
monotonic persistent record versions and authenticated reconfiguration.
Explain the same-chain-ID, same-genesis and post-anchor divergence limits.
For each observation bind one finalized block to record/grants/history/code;
missing proof, conflict or rollback refuses instead of choosing the largest
height or version. Test restart with durable anchors and a safe data fixture;
actual hostile-fork generators/services are excluded.

The final source artifact must also state the linearization point, clock and
readiness ownership, permitted publication-to-finality delay, five-second
per-operation freshness enforcement and persisted tombstone behavior.
Finalized does not mean zero latency or immunity from trusted-source compromise.
Operational chain/RPC/address/anchor/root/custody/host and cost decisions are
asked with concrete alternatives after design review. Deployment, signing and
paid execution require separate authorization.

## 4. Evidence groups and completion criteria

| Group | Unit/data-only obligations | Safe owned-runtime obligations after implementation |
|---|---|---|
| Auth/command | Closed schemas, canonical bytes, actor-context matching, all operations/states, malformed/duplicate/truncated/extra-frame refusal and stale credentials as data | Trusted local Client/server handshake, normal reads/writes, exact command delivered once to owned atomic admission; no external target |
| Atomic storage | Same predecessor, concurrent revoke/write order, exhausted capacity, uncertain commit and rollback as modeled outcomes | Owned store normal persistence and safe restart, complete old/new snapshots; no claim from a mock alone |
| Read/history | Every response schema, chunks/length/digest/context, ACL/current generation, expiry, denied/unknown/pruned view, lost response with in-flight commit | Owned history traversal with normal multi-chunk records/commands, read-only permission and new authenticated sessions; observed view identity and source receipts |
| Contract | Independent ABI expected bytes, every operation/key role/state/proof/version and negative modeled cases | Local normal deployment/registration/read/grant lifecycle with an owned EOA and wallet after implementation and authorization; exact inner caller/command/state/history observations, compiler/artifact/runtime code/gas evidence; no public-chain transaction implied |
| Finality/fork | Pre/post-anchor conflicts, stale sources, missing ancestry, restart high-water marks as fixed data and unit scenarios | Normal owned node/source observation only where safe and available; otherwise explicit NOT_RUN |
| Integration/Inspector | Independent catalogs/oracles, old subjects unchanged, bad/missing evidence yields ERROR/NOT_RUN rather than fabricated PASS | Go/Rust/ADK selected consumers and Inspector capture the same pinned source/ABI/observer and real evidence; full PR/main CI and artifact review |

Code changes use meaningful units plus safe runtime where available. Cases
that would require reusable attack tooling remain modeled/data-only tests,
with that limit reported. Changed code needs at least 90% coverage under the
existing project rule. Independent LLM design/code/artifact review is distinct
from a later organizationally independent external audit.

Each implementation group ends with full PR CI, exact artifact checks,
independent review, squash merge, own branch deletion, fresh main CI/evidence
and original local main synchronization preserving user changes. No SAGE Core
Team manual or automatic review request is permitted. This proposal's existing
CI checks document/baseline consistency only; it is not future-protocol runtime
coverage or an additional conformance verdict.

## 5. Work order and preserved work

1. Review the refined web management/history lifecycle and closed schemas; keep current normative files unchanged.
2. Finish the new-contract ABI/storage/algorithm-cost design against pinned
   current SAGE/A2A/DID and an explicitly frozen ERC-8004 revision; record gaps
   and the KYA boundary. ERC-8004 remains changeable, not an unpinned latest input.
3. Complete the selected finality-source artifact and compatibility inventory;
   prepare operating alternatives and request only decisions needed for them.
4. Review/adopt an explicitly versioned complete scope, then implement and
   independently inspect matching code under the original plan. Do not skip
   an old pending verification because this future proposal exists.

This proposal does not complete stages 7/8, remaining DID obligations,
actual issuer uniqueness, IdentityAndReadiness/MeasuredComponent, deployment
controls, production ingress, current runtime inventories, maintenance/legacy
work or dependencies. Existing implementation gaps and deferred W3C registration
remain in the project handoff. Later demo, facilitator, discovery, settlement,
governance and testnet work retain their original order; no operational network
or future stage is started by publishing this candidate.

The [candidate command, state and outcome model](contract-execution-model.md)
adds a separate 22-error/2-event artifact with normal data-codec checks.
It does not change the thirteen-function ABI or complete storage slots, guard
precedence, contract execution, costs, finality or version adoption.

## Candidate chain-command and storage refinement

Check all 13 ABI method classifications and 51 ordered input paths (including
structural tuple/array nodes) against chain-command-map.json and the existing
signature manifest. Preserve the six-member web input/no actor, the separately
derived chain actor, complete reveal salt and reserved ClaimMismatch. Unit-only
metadata cases cover omitted/duplicate paths, redirected actor/salt/proof/expiry
fields, changed scalar types and limits; these are not live protocol requests.

The checker emits no protocol PASS and runs no contract. Require fresh source
hashes, eight unit results, at least90% checker statement coverage and actual
artifact evidence before accepting this design-tool change. Subsequently close
per-operation guard priorities, serializer byte equality and actual slot/type
layout, then full maximum-valid workload/account/finality/compatibility and
explicit adoption. No design-tool success closes the old four documentary
FAILs, operating/issuer holds or actual Registry/Go/Rust/ADK inspection gates.
