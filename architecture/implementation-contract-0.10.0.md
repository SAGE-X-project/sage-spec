# Implementation contract for SAGE 0.10.0

Status: **informative design decision; implementation conformance not established**.
This contract fixes the proposed library and host responsibility boundary for the
next implementation work. It does not amend the normative wire specification,
authorize a release, or certify complete host mediation.

## Inputs and authority

| Input | Revision | Use here |
| --- | --- | --- |
| `sage-spec` | `c0b7f9e61cfb97b9cfabc4e18444f349ef810295` | Current 0.10.0 normative text, including the REG-08 web media correction |
| Go `sage` | `49379baadc6baec9ca8b4bb7d15bf43d65144bd7` | Existing public API and source-path observations |
| Rust `rs-sage-core` | `ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396` | Existing modules, library surfaces and source-path observations |
| `sage-inspector` | `f104c8c3ce072e7a64d5a0092623e45ffb8d287b` | Older pinned implementation evidence; not a verdict on the current spec commit |

The [earlier implementation review](../verification/implementation-pattern-review.md)
records source observations at older revisions. Its SCA-01..03 open-decision
paragraphs are superseded by the [standards clause revision](../verification/standards-clause-revision.md).
The later [REG-08 correction](../verification/web-registry-media-contract.md) is
also part of this contract's input. The 489 planned Inspector parents are a plan,
not 489 passing implementation cases. The [91-group source map](../verification/core-gap-review.md)
is bounded gap evidence pinned to an earlier spec revision, not a blanket pass
transferred to this one.

## Library surface and responsibility

The public protected path should be a **versioned 0.10.0 assembly** over reusable
primitives. Its caller selects a profile and supplies trusted dependencies once;
construction fails when a mandatory dependency is absent. The exact package and
symbol names below are design candidates, not currently exported APIs. No current
Go or Rust primitive result by itself grants dispatch authority.

| Boundary | Core responsibility | Host or adapter responsibility | Existing source candidates |
| --- | --- | --- | --- |
| L0 exact bytes | Closed parsing, canonical encoding, domain separation, transcript and commitment bytes | Supply captured bytes, never pre-normalize them on behalf of the core | Go `crypto/jcs`, `core/rfc9421`, `guard010/{commitment,json}`; Rust `jcs`, `rfc9421`, `guard010` pure functions |
| L1 cryptography and session | Verify selected signature/HPKE/session algorithms, timestamps and replay-sensitive wire state against explicit inputs | Hold private keys and trusted clock/replay backing; choose the declared profile | Go `hpke`, `session`, `core/rfc9421`; Rust `hpke`, `session`, `rfc9421` |
| L2 identity and admission | Select active role-bound keys; verify intent/result; reserve identities; recheck authority and measured instance at final admission | Supply authoritative fresh source, approved policy/baseline, durable stores and pinned executable instance | Go `registry010.Gate`, `guard010.{Client,DispatchGate}`, `execution010.Ledger`; Rust `registry010::Gate`, `guard010::{Client,DispatchGate}`, `execution010::Ledger` |
| L3 assembly | Validate a complete configuration, wire L0–L2 in the required order, expose typed protected operations and explicit failures | Install the boundary at **every** protected effect and result-consumption path; isolate mutable plugins/skills/MCP processes | **Missing as a complete importable deployment constructor** at the inspected commits; partial MCP owners exist in both cores |

Candidate names are Go `pkg/agent/runtime010` for assemblies and
`pkg/agent/ports` for genuinely shared host contracts; Rust `runtime010` and
`ports` can mirror the concepts without forcing identical module layout.
Admission, replay and storage contracts whose semantics depend on 0.10.0 remain
explicitly versioned. The two existing Go `Store` interfaces have different
meanings and must not be mechanically unified. Before choosing final paths,
inspect downstream imports and the preserved, untracked `sage/contracts/` input.

The minimum assembled operations are conceptually:

1. `OpenClient010(config, trusted capture, signer, registry, policy, journal, transport)`
   yields an owner that authorizes and transmits one exact intent and consumes
   only its matching, verified result.
2. `OpenExecutor010(config, registry, approved policy/baseline, durable ledgers,
   pinned component, result signer)` yields a gate whose only dispatch path
   performs final admission and commits the exact invocation.
3. `OpenMCPHost010(config, authenticated connection owner, executor, bounded
   scheduler)` adds the adopted non-HTTP setup/readiness/queue/closure rules.
   HTTP middleware is a separate HTTP transport adapter and does not implement
   this non-HTTP owner.

These signatures describe required inputs and ownership, not a promised source
API or a new wire message. In Go, constructors should return an error for a
missing collaborator and use a caller context for bounded operations. In Rust,
the equivalent constructors should return `Result` and preserve exclusive
ownership or synchronized handles for journal and dispatch state. Construction
must not infer a weaker profile, enable a permissive legacy verifier, or report
Execution Guard coverage from the presence of a type alone.

## Trusted ports and their failure contracts

| Port | Trusted provider and required property | Failure or uncertainty |
| --- | --- | --- |
| Capture and policy | Client host stores exact pre-expansion UTF-8 inputs and evaluates approved, pinned policy over exact recipient, tool, arguments and component baseline; each downstream Agent creates its own capture/decision | No signing or downstream call; model or tool output cannot supply approval |
| Signing custody | Host-controlled key handle signs only an authorized operation with the selected role/algorithm; untrusted code cannot request arbitrary signatures | No alternate key, algorithm, unsigned retry or legacy-profile retry |
| Registry source and clock | Authenticated, operation-scoped fresh observation with configured source/network/registry, proofs, readiness, finality and monotonic time; core gate checks selected active key | Reject on absent, stale, conflicting, unready or unreachable state; peer-provided flags alone are insufficient |
| Registry watermark | Durable monotonic finalized-version/content state, independent from execution history | Reject when advancement cannot be committed or rollback is uncertain |
| Transport replay and session store | Persistent, scoped uniqueness and session sequence/closure state for the selected wire profile | Reject replay, missing backing or state loss; never downgrade to replay-disabled verification |
| Execution ledger and Client journal | Exclusive durable reservation, execution fence, one terminal result, and tracked outstanding invocation, with namespace/lifetime per profile | Unknown after uncertain side effect; no second dispatch or invented success; protected recovery is administrative |
| Component and policy baseline | Trusted administrator approves immutable code/policy descriptors; loader measures and dispatches the **same instance** and blocks uncovered dependencies | Deny changed, retired, missing or re-opened instances; a peer hash cannot approve code |
| Effect owner and scheduler | Trusted host owns all direct, retry, nested, parallel, subprocess, file and network effects; MCP host owns bounded queue/worker/closure ordering | No protected claim when a bypass exists; cancellation/close cannot turn uncertainty into success or free an occupied identity |

An opaque `VerifiedMessage` can carry exact bytes, peer/key evidence and profile,
but is not an execution permit. A non-serializable, owner-bound
`AuthorizedCall`/invocation may be constructed only by the trusted L2/L3 gate
after policy and durable reservation; it is consumed once by the pinned
component. These are proposed API types. Current Go `DispatchReceipt` and Rust
`DispatchReceipt` are local state/commit metadata, not signed tool results or
portable authorization tokens. The dispatch owner still has to prove complete
mediation at deployment time.

## Operation ordering

```text
trusted Client capture -> exact derived-call policy -> role-bound signing
  -> protected transport -> bounded parse and cryptographic verification
  -> fresh authoritative identity/key observation -> receiver policy and baseline
  -> durable identity/nonce reservation -> final recheck and execution fence
  -> pinned effect admission -> durable signed result -> Client result verification
  -> first terminal output consumption
```

The complete order, exact state transitions, duplicate snapshots and MCP queue
semantics remain those of [EXEC-02..08](../profiles/agent-mcp-security.md),
[MSET-01..08 and MOWN-01..06](../profiles/non-http-mcp-security.md). A model-callable
`sage_secure_call` tool or a verification MCP tool can expose functionality, but
the trusted host must invoke its gate before every effect and before consuming
the result, regardless of what the model chooses. A guarded tool registry covers
only routes it actually owns; a host with direct capabilities must intercept
them or leave the Execution Guard profile unclaimed.

For HTTP, select only algorithms registered for the current 0.10.0 HTTP profile:
`ed25519` and, when implemented, `ecdsa-p256-sha256`. The SAGE private
secp256k1/Keccak suite cannot enter HTTP `alg` as an alias. For adopted
non-HTTP MCP outer and handshake signing, require the active Ed25519 key for
the specific role; the X25519 HPKE KEM key is distinct and cannot replace it.
See [the algorithm registry](../spec/11-registries.md),
[HTTP signatures](../spec/03-rfc9421.md), and [MOWN-05](../profiles/non-http-mcp-security.md).
The existing strict HTTP 0.10.0 path is separate from the legacy generic
RFC 9421 verifier at the inspected Go commit; an assembly must make that
selection explicit. The current source map does **not** prove optional P-256
support or every complete role-selection path in either core.

## SDK, compatibility and migration decisions

Native Go callers use the Go core; native Rust callers use `rs-sage-core`.
Python, TypeScript and Java wrappers should use a pinned core library build,
preferably the reviewed Rust C ABI or WASM surface where its host and key-custody
model fit. An available `cdylib`, `ffi` or `wasm` feature is packaging groundwork,
not proof that 0.10.0 L2/L3 can be exposed safely. A wrapper must preserve the
selected profile, exact bytes, structured failures, cancellation, callback
deadline, handle lifetime and journal ownership. It must not recode JCS,
signatures, HPKE or admission. `sage/sdk/rust` is a migration input, not a
second Rust core; keep it only as a documented compatibility facade if a
consumer audit finds users, otherwise archive it after migration notice.

| Existing surface or change | Decision before implementation | Migration evidence |
| --- | --- | --- |
| Permissive general Go/Rust RFC 9421 verifiers | Do not silently select them for 0.10.0. Add an explicit strict assembly first; change generic defaults only with a public compatibility decision | Inventory importers; negative tests for missing nonce, digest, expected peer, replay state and request binding |
| Legacy Go HPKE/transport including `MakeAckTag` | Keep separate and mark exact legacy scope/deprecation; never reinterpret old transcript bytes as 0.10.0 | Exported-use audit, migration mapping and byte/verdict tests |
| Moving Go 0.10.0 HTTP carriage into transport package | Defer physical move until consumers and forwarding aliases are reviewed | Import/build audit; unchanged strict wire corpus |
| Registry, replay and execution stores | Name by distinct purpose and version state schema; do not share an ambiguous `Store` or resume old sessions after rollback | Restart, concurrent writer, partial write, retention and downgrade tests |
| Library version vs protocol version | Publish an explicit release-to-profile matrix; no automatic profile negotiation or fallback | Documentation and tests pin both identifiers |
| `pkg/telemetry/logger` process exit and legacy OIDC/handshake readers | Treat as separate library-adoption and hardening issues, not evidence of 0.10.0 conformance | Consumer/behavior audit and bounded-error tests before refactoring |

No code movement, SDK replacement or repository split is authorized by this
document alone. Preserve old public imports until a migration path is tested.
Safety-relevant generic-default changes should be versioned and announced;
the new strict assembly must fail closed from its first release. The proposed
`ports`/`runtime010` names may change after the import audit without changing
the responsibility boundary.

## Ordered implementation exit gates

This contract fits [the existing migration order](migration-plan.md): the
specification baseline and bounded gap mapping precede Inspector, two cores,
trusted adapters, SDKs, services, demos and physical extraction. It does not
reorder those gates. The next actionable checks are:

1. Pin Inspector's case plan and expected verdicts to this exact normative
   snapshot, including the REG-08 media correction; preserve older reports as
   historical evidence. Distinguish a supported primitive from a complete
   implementation verdict.
2. Audit Go/Rust exported consumers and implement the explicit strict 0.10.0
   assemblies and ports against one versioned corpus. Verify unit boundaries
   and safe live transport/restart behavior in both directions. Keep every
   unsupported profile or host collaborator visibly unsupported.
3. Install the assembly in real Agent/MCP effect and result paths. Demonstrate
   route coverage, key/baseline isolation, durable storage, cancellation and
   failure behavior; then run Inspector against the exact binaries and profile.
4. Migrate SDKs and examples only after core and host evidence. Build the
   registration service and paired security comparison under their separate
   deployment gates. Consider repository extraction after import and release
   ownership audits.

The remaining external independent implementation audit and release decision
are later evidence gates. This design fixes the intended API and trust boundary;
it does not claim that a compromised trusted host or pre-enrolment substitution
is solved by this protocol version.
