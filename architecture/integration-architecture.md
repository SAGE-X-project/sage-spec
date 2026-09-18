# Integration architecture

Status: **proposed structure** for protocol 0.10.0. No code was moved, no package
created and no API changed by this document. It answers one question: how must the
specification and its implementing libraries be structured so that they can be adopted
by a new agent, by a new MCP server, and by an agent or MCP server that already has its
own message-sending logic.

Companion documents: [repository roles](repository-roles.md) owns who may implement
what; [migration plan](migration-plan.md) owns the order of work; the
[integration guide](../guides/integration.md) owns advice to a developer following the
normative [Execution Guard profile](../profiles/agent-mcp-security.md). This document
owns the shape of the code that sits between them.

## 1. The constraint that shapes everything

Easy adoption and complete mediation cannot be delivered by one artifact.

The specification is explicit about mediation. EXEC-01 states that "a deployment that
cannot enforce this boundary MUST NOT claim the Execution Guard profile". TRANSPORT-06
states that "no reliance on an LLM choosing to call a verification tool constitutes
conformance". EXEC-08 requires each adapter to "demonstrate complete interception and
deny on no verdict, exception, disconnect or timeout".

A library that can be adopted incrementally is, by construction, a library a caller can
forget to call. Pursuing one API that is both effortless to bolt on and impossible to
bypass produces the worst available outcome: something pleasant to adopt that protects
nothing, carrying a name that suggests otherwise.

The resolution is not to choose one side. It is to **stratify the code by the boundary
the integrator can actually enforce, and to make each stratum state honestly what it
delivers.** The charter already defines that stratification in §7 as the conformance
levels Verifier, Peer, Registrar and Execution Guard. The structural claim of this
document is that the code should be organised along those levels, and that today it is
organised along protocol mechanisms instead.

## 2. Observed state

Read from the Go repository and the Rust core during this analysis; §9 records exactly
what was inspected.

**There is no assembly layer in Go.** The repository root contains no Go file. Every
exported constructor under `pkg/agent/` builds one mechanism: a key store, a format
exporter, a transport, a rotator. No constructor produces a configured participant.

**An integrator must supply many collaborators before the first message moves.**
`guard010.OpenDispatchGate(path, create, recipient, Authority, IntentPolicy, Component)`
requires three interfaces and a durable path.
`registry010.NewGate(Config, Source, Clock, Store)` requires three more. Transport,
HTTP signatures, handshake and session records are wired separately. That is six or more
integrator-supplied implementations before anything works.

**Collaborator contracts are defined locally and collide.** `Store` is declared twice
with unrelated meanings, at `pkg/agent/registry010/gate.go:81` and
`pkg/storage/interface.go:103`. `Clock`, `Source`, `Authority`, `IntentPolicy` and
`Component` each exist in exactly one consuming package. An adapter author has no single
contract surface to implement against.

**Layers are mixed inside packages.** `pkg/agent/guard010` contains the pure functions
`OriginalCommitment`, `ManifestCommitment` and `PolicyCommitment` in `commitment.go`
alongside the stateful `DispatchGate` in `dispatch.go`. A caller who needs only a digest
also acquires the ledger.

**One seam has the right shape.**
`rfc9421.ResponseSigner.Wrap(next http.Handler) http.Handler` at
`pkg/agent/core/rfc9421/response_signer.go:53` is a one-line insertion into an existing
server. It is currently the exception rather than the template.

**No example exercises the Execution Guard path.** The smallest integration example,
`examples/mcp-integration/simple-standalone/main.go`, is 294 lines and imports only
`core/rfc9421` and `crypto/keys`. It maintains a hand-written map of trusted agent keys
and says so in a comment. Across the whole `examples/mcp-integration` tree the only SAGE
imports are `core`, `core/rfc9421`, `crypto/keys`, `did` and `did/ethereum`. Nothing
imports `guard010`, `execution010`, `registry010`, `session`, `hpke` or `transport`.
The published integration story therefore demonstrates message signing only, at
approximately Verifier level, and predates the 0.10.0 execution work.

**Rust already has the facade Go lacks.** `rs-sage-core/src/lib.rs` re-exports
`Message`, `MessageBuilder`, `VerificationOptions`, `VerificationResult` and
`VerificationService` at the crate root, above modules that mirror the Go package names
(`guard010`, `execution010`, `registry010`, `rfc9421`, `hpke`, `session`, `jcs`). It
also carries feature-gated `ffi` and `wasm` modules. The two cores are therefore not
symmetric in adoption cost today, and any cross-core integration claim must account for
that.

**A permissive default is already recorded as a hazard.**
[purpose-and-vision](../analysis/purpose-and-vision.md) notes that
`pkg/agent/core/rfc9421/verifier_http.go` "permits nil guard, disabling replay and
optional expected DID", and concludes that "a flexible library API is not itself the
mandatory integration profile".

## 3. Proposed layering

Four layers, with dependencies running in one direction only. Selecting a higher layer
brings the lower ones; a lower layer must never import a higher one.

### IA-01 — L0, pure codec

No I/O, no state, no collaborators. Canonical byte production, signature base
construction, intent and result encoding and decoding, digest and commitment
computation, encoding validation and rejection.

This is the layer the cross-language vectors test, the layer an existing implementation
in any language adopts first, and the only layer that can be exercised without
provisioning anything. It must not transitively pull in a database driver, an HTTP
stack or a clock.

Present material: `crypto/jcs`, the base-construction parts of `core/rfc9421`,
`guard010/commitment.go`, `guard010/json.go`.

### IA-02 — L1, cryptographic verification without policy

Stateful, but decides only cryptographic validity and freshness. Verify a signature
against a supplied key, validate an AEAD record, maintain a replay window, enforce size
and time bounds.

It requires a store and a clock. It requires no policy, no registry and no notion of
authorisation. Its output is the single statement "these bytes are authentic and fresh
under the key I was given", and nothing more.

### IA-03 — L2, trust decisions

Requires external trust inputs that only the deployment can supply: authoritative
registry observation, key selection, pinned session tuples, execution authorisation and
the durable execution ledger.

Present material: `registry010.Gate`, `guard010.DispatchGate`, `execution010.Ledger`.

**No constructor in this layer may produce a working object when a required collaborator
is absent.** A missing policy, ledger or registry source is a construction error, never
a silently permissive default. This rule exists because the recorded `verifier_http.go`
hazard is exactly the shape of defect that a flexible constructor invites.

### IA-04 — L3, deployment assemblies

The layer an integrator actually starts from. One assembly per deployment shape, each a
single constructor over a configuration value, wiring L0 through L2 with production-safe
defaults:

| Assembly | Serves | Refuses to construct without |
|---|---|---|
| Agent node | An agent that signs, verifies and optionally establishes sessions | Own identity, key source, registry source, replay store |
| MCP executor | A server that exposes protected tools behind the intent envelope | The above plus policy, component manifest, execution ledger |
| Gateway | A signing delegate terminating protection at a declared boundary | The above plus an explicit statement of the termination point |

An assembly chooses defaults. It does not own policy content; the deployment still
supplies that, which keeps the boundary that [repository roles](repository-roles.md)
draws between a library and an application.

## 4. Three integration shapes and their seams

One API covering all three degrades all three. Each gets a distinct entry point.

### IA-05 — A new agent

A single L3 agent-node constructor. The configuration names the agent's own identifier,
key source, registry source, policy and durable paths; the result is a participant with
transport, signatures, handshake and sessions already wired. This is the cheapest case
and needs no further mechanism.

### IA-06 — A new MCP server

**The seam is the tool registry, never an individual tool.** Wrapping tools one at a
time means an unwrapped tool is a complete bypass, and EXEC-08 requires that "unsigned
direct calls to a protected tool MUST be rejected at the same executor boundary".
Wrapping the registry makes registering a protected tool without protection impossible
to express.

The executor assembly therefore exposes registration, not decoration: a tool is
registered *into* the guarded registry, which owns `sage_secure_call`, the intent
verification order of EXEC-04 and the result signing of EXEC-07. Structure replaces
developer discipline.

### IA-07 — An existing agent or MCP server

The only realistic seams in software that already exists are the outbound and inbound
transport boundaries.

- **Outbound:** an `http.RoundTripper` that signs and, where a session exists, encrypts.
  No equivalent exists today.
- **Inbound:** an `http.Handler` wrapper that verifies before the application handler
  runs. `ResponseSigner.Wrap` already demonstrates the shape.

**Both must be paired with an installation self-check.** The characteristic failure of
this case is not a wrong call; it is a route that was never wrapped. The assembly must
be able to enumerate the routes it protects, compare that against the server's mux at
startup, and refuse to start rather than serve an unprotected path. Without this, the
inbound wrapper is advisory.

This case must also be told, plainly, what it can claim. An existing application
generally reaches Verifier or Peer, not Execution Guard, because Execution Guard
requires capability isolation the application does not have. See IA-10.

## 5. Structural enforcement

Three rules that move guarantees from documentation into the type system and the
startup path.

### IA-08 — Express the conformance step as a type, not a boolean

[Repository roles](repository-roles.md) already requires this in prose: "SDKs/adapters
must expose the distinction between proposed operation, authorized execution envelope
and verified result rather than return a single ambiguous success boolean."

Make it structural. `VerifiedMessage` (the L1 verdict) and `AuthorizedCall` (the L2
verdict) are distinct types, and the dispatch entry point accepts only `AuthorizedCall`.
"Forgot to authorise" then fails to compile instead of failing silently at runtime.

This is the single mechanism that makes IA-07 safe without trusting the integrator's
discipline, and it is why the layering above is worth the disruption.

### IA-09 — Default to refusal, never to permission

A constructor missing a required collaborator returns an error. A verifier without a
replay guard does not exist as a constructible value. An adapter that cannot enumerate
its protected routes does not start. This restates EXEC-08's deny-on-no-verdict
requirement as a property of the API rather than a rule the caller must remember.

### IA-10 — Let the assembly report its own conformance level

An assembled participant exposes the level it actually achieves, derived from what was
wired rather than from what was configured, together with a startup self-test. The
deployment cannot advertise a level the assembly does not report.

This implements R-45 and EXEC-01 in code, and it is what prevents easy adoption from
turning into false claims. It is the difference between a library that is easy to use
and a library that is easy to misrepresent.

## 6. Cross-cutting structure

### IA-11 — One unversioned contract surface

Collect `Clock`, `Store`, `Source`, `Authority`, `IntentPolicy`, `Component` and
`Resolver` into a single contract package with no protocol version in its path, and
resolve the `Store` name collision recorded in §2. Adapter code written by an integrator
implements the deployment's own concerns; it should not churn because a wire format
changed.

### IA-12 — Keep the version suffix only where the wire lives

The present `guard010`, `execution010` and `registry010` package names put the protocol
version in the import path.

The cost is that every consumer's import lines change on a MINOR bump, and OVERVIEW-03
permits MINOR to change wire formats during 0.x, so this will happen repeatedly. The
benefit is that two protocol versions can coexist in one binary during migration, which
matters precisely because the specification forbids silent fallback and requires exact
version matching.

**Recommendation: keep the suffix on packages that carry wire formats, and remove it
from L0 pure codecs and from the IA-11 contract surface.** Coexistence is preserved
where it has value, and the surfaces an integrator writes against stay stable. Note that
the Rust core uses the same suffixed module names, so this decision should be taken for
both cores together or the asymmetry recorded.

### IA-13 — SDK substrate

Language SDKs wrap a pinned core rather than reimplementing it, as
[repository roles](repository-roles.md) already requires. Add one structural
constraint: the FFI and WASM boundary may expose L0 and L1 fully, but L2 only as opaque
handles. L2 holds signing keys and durable ledger state, and those should not cross a
language boundary as ordinary values.

## 7. Costs and rejected alternatives

Stated so the proposal can be judged rather than merely accepted.

**The assembly layer adds maintenance.** Three deployment shapes means three assemblies
to update whenever a lower layer moves. Assemblies also accumulate defaults, which
brings them close to the policy ownership that [repository roles](repository-roles.md)
places outside the library. The line must be held explicitly: an assembly selects
defaults for mechanism, never content for policy.

**Typed authorisation makes the API heavier.** More intermediate types, and constructing
a fake `AuthorizedCall` in a test becomes deliberately awkward. That awkwardness is the
protection working, and developers will still dislike it.

**IA-07 cannot be made fully safe.** Wrapping the transport boundary does nothing about
a second egress path inside the application. The honest ceiling for this case is to
report the achieved level accurately (IA-10), not to claim protection the structure
cannot deliver.

**This requires moving existing code.** Separating L0 out of `guard010`, collecting the
contract surface and adding assemblies is real work, corresponding to gates 4 and 5 of
the [migration plan](migration-plan.md). It can be done entirely as package layout
inside the existing repository; no repository split is required, and the migration plan
is right to place physical extraction last.

**Rejected: a single universal integration API.** It would have to accept the weakest
caller, which means every guarantee becomes optional, which means the profile cannot be
claimed by anyone. Rejected on the strength of EXEC-01.

**Rejected: model-visible verification tools as the enforcement path.** Already excluded
by TRANSPORT-06 and EXEC-08; recorded here because it is the structure integrators
reach for first.

## 8. Suggested sequence

Ordered so each step is useful on its own and none blocks on unresolved specification
questions.

1. Split L0 out of the mixed packages and collect the IA-11 contract surface. Pure
   refactoring, no behaviour change, immediately reduces what an integrator must import.
2. Introduce the typed verdicts of IA-08 through the existing call paths.
3. Convert permissive constructors to IA-09 refusals, starting with the recorded
   `verifier_http.go` nil-guard hazard.
4. Add the outbound `RoundTripper` so IA-07 has both seams.
5. Build the MCP executor assembly of IA-06 and the guarded tool registry, and publish
   an example that actually exercises `guard010`, `execution010` and `registry010`. The
   absence of such an example is currently the largest gap between the specification and
   an adoptable implementation.
6. Add conformance self-reporting (IA-10) and the route self-check of IA-07.
7. Decide IA-12 for the Go and Rust cores together.

Steps 1 through 4 are prerequisites for gate 4 of the [migration plan](migration-plan.md);
steps 5 and 6 are its content.

## 9. Evidence

Read in the Go repository at the current `main` working tree:

| Observation | Location |
|---|---|
| No Go file at the repository root; no deployment-level constructor under `pkg/agent/` | Directory listing and exported-constructor scan |
| Dispatch gate requires three interfaces and a durable path | `pkg/agent/guard010/dispatch.go:77` |
| Registry gate requires three further collaborators | `pkg/agent/registry010/gate.go:95` |
| `Store` declared twice with unrelated meanings | `pkg/agent/registry010/gate.go:81`, `pkg/storage/interface.go:103` |
| Pure commitments and stateful dispatch share one package | `pkg/agent/guard010/commitment.go`, `pkg/agent/guard010/dispatch.go` |
| Correctly shaped handler seam | `pkg/agent/core/rfc9421/response_signer.go:53` |
| Smallest MCP example is 294 lines and hand-rolls a trusted-key map | `examples/mcp-integration/simple-standalone/main.go` |
| No example imports `guard010`, `execution010`, `registry010`, `session`, `hpke` or `transport` | Import scan across `examples/mcp-integration` |

Read in `rs-sage-core`:

| Observation | Location |
|---|---|
| Crate root re-exports `VerificationService`, `MessageBuilder` and related types | `src/lib.rs` |
| Module names mirror the Go packages, including the `010` suffixes | `src/` listing |
| Feature-gated `ffi` and `wasm` modules exist | `src/lib.rs` |

Specification statements relied upon: EXEC-01, EXEC-04, EXEC-07 and EXEC-08 in the
[Execution Guard profile](../profiles/agent-mcp-security.md); TRANSPORT-06 in
[chapter 08](../spec/08-transport.md); conformance levels in [charter](../charter.md) §7;
R-45; the library-versus-profile note and the `verifier_http.go` nil-guard observation in
[purpose and vision](../analysis/purpose-and-vision.md); ownership boundaries in
[repository roles](repository-roles.md).

## 10. Limits

No code was written, built or run for this document. The Go analysis covers package
layout, exported signatures and example imports, not implementation behaviour. The Rust
analysis covers the crate root and module list only. The four SDK directories were
counted but not reviewed; [repository roles](repository-roles.md) already treats them as
migration inputs rather than compatible implementations. No claim is made that the
proposed structure has been validated by building an integration against it, and the
ergonomic judgements in §4 are design reasoning, not measured adoption cost.
