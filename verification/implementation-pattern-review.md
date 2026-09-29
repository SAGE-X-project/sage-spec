# Implementation pattern review after ADOPT-06

Status: **DESIGN_REVIEW_COMPLETE; IMPLEMENTATION_CONFORMANCE_NOT_ESTABLISHED**.
This review makes no normative change, moves no code and does not approve a release.
It turns the preserved architecture proposal and the requested adoption pattern into
an ordered implementation handoff. Full implementation conformance and an
organizationally independent external audit remain later gates.

## Reviewed inputs and limits

| Input | Pinned revision or identity | Treatment |
| --- | --- | --- |
| Current `sage-spec` | `bc0ac3a0a0317cee4abfce75d1c4b7226708d9eb` | Normative baseline and dated review records |
| Preserved `docs/design-and-integration-review` | `9f6901c29412561e38c14cff7279d3751bcc0885` plus uncommitted worktree | Read-only design input; no merge or copy into normative chapters |
| Go `sage` | `49379baadc6baec9ca8b4bb7d15bf43d65144bd7` | Bounded source/API inspection, not execution |
| Rust `rs-sage-core` | `ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396` | Bounded source/API inspection, not execution |
| `sage-inspector` | `e003a22ea6be0fc2207e3f514a844fe458515b3c` | Integration and execution-order context, not a new Inspector verdict |

The two committed branch-only documents have the same SHA-256 values recorded in
the [preserved branch review](preserved-design-review.md):
`50b9a1cb18028fb9a3c098b9bf44a0505b1b821e7afb08a592508cf9073687a5`
for `architecture/integration-architecture.md` and
`1dac095f909bd83424563f90e183af906a528d1f4a663ef2efba4599ac7fe431`
for `verification/design-standards-review.md`. The ten divergent uncommitted
inputs in that review also retain their recorded hashes. Their earlier design
dispositions remain starting points except where a later audit supersedes them;
this pass refreshes the implementation mapping against current core commits.
The handoff notes dated 2026-09-25 are observations and
proposals, not a replacement for adopted 0.10.0 rules. Only selected files and
call sites were inspected; this is not a clause-by-clause code gap matrix.

## What the current code establishes

1. **Legacy HTTP defaults are still permissive.** Go
   `pkg/agent/core/rfc9421/verifier_http.go` defaults to optional nonce,
   content-digest coverage, signer DID and response request binding;
   `DisableReplayCheck` is public. Rust `src/rfc9421/verifier.rs` likewise defaults
   those requirements off and permits a verifier without a replay guard. Their
   strict presets require some coverage but still need a trusted expected peer
   and actual replay storage. They are not safe substitutes for an assembled
   0.10.0 participant merely because signature verification succeeds.
2. **The 0.10.0 HTTP path is separate.** The inspected Go
   `pkg/agent/hpke/{http_handshake010,http010}.go` path owns a fixed HTTP
   signature profile, exact content bytes and handshake binding; no import or
   call of the legacy `HTTPVerifier` occurs within `pkg/agent/hpke`. Thus the
   handoff's *specific* possibility that this path inherits the legacy option
   defaults is not supported by these files. That is a source-path conclusion,
   not a complete runtime or alternate-entry-point audit. Preserve both paths'
   distinct claims and prevent an assembly from accidentally selecting the
   generic verifier for a protected 0.10.0 operation.
3. **Older audit fixes are mixed at the inspected Go commit.** OIDC verification
   checks issuer equality, but the token and JWKS response readers lack an
   explicit byte cap. The legacy handshake peer cache checks the cached DID
   and expiry before reuse, but its save path shows no capacity bound. The
   legacy HTTP server applies a default 1 MiB request-body cap. These are
   scoped source observations, not a claim that the older audit branch was
   merged or that these legacy facilities are 0.10.0-compliant.
4. **A ready-to-import deployment assembly is missing.** Go exposes separate
   `guard010.OpenDispatchGate` and `registry010.NewGate` constructors and two
   unrelated `Store` interfaces. Rust exposes the corresponding modules and a
   crate-root facade, but the inspected facade does not assemble an Agent or
   MCP executor from one profile configuration. Go `README.md` and the
   inspected examples do not demonstrate a `guard010` + `registry010` +
   `execution010` protected flow. This is an adoption gap, not a new wire rule.
5. **The current language SDKs cannot be relabeled as thin 0.10.0 wrappers.**
   `sage/sdk/rust/sage-client` implements Ed25519, X25519, HKDF and AES-GCM
   itself and does not depend on `rs-sage-core`. Python and TypeScript also
   contain native crypto implementations. The Java path requires a separate
   behavior and consumer audit. Rust `rs-sage-core` has `rlib`/`cdylib`, `ffi`
   and `wasm` build surfaces, but build availability alone does not establish
   a safe, complete 0.10.0 language boundary.

## Responsibility mapping

The preserved IA-01..13 layers are useful **code boundaries**, not new protocol
conformance levels. The charter's Verifier, Peer, Registrar and Execution Guard
claims remain separate. In particular, a type or constructor cannot by itself
prove complete host-effect mediation.

| Layer | Go source to assess/refactor | Rust source to assess/refactor | Required boundary |
| --- | --- | --- | --- |
| L0 exact bytes | `crypto/jcs`, pure `core/rfc9421` helpers, `guard010/{commitment,json}.go` | `jcs`, `rfc9421` canonicalization, pure `guard010` functions | No I/O, policy or trusted state; reject noncanonical input before digest/signing |
| L1 cryptographic/session verification | `core/rfc9421`, `hpke`, `session` and 0.10.0 record code | `rfc9421`, `hpke/completion010`, `session` | Authentication/freshness verdict tied to an explicit key, clock and replay context; no authorization claim |
| L2 trust and admission | `registry010.Gate`, `guard010.DispatchGate`, `execution010.Ledger` | `registry010::Gate`, `guard010::DispatchGate`, `execution010::Ledger` | Authoritative observation, exact issuer/key and approved intent, durable reservation and final effect admission |
| L3 deployment assembly | New versioned Agent/MCP/gateway constructors over the above | New versioned constructors above the existing crate facade | Refuse absent collaborators; bind source, signer, replay, policy, transport and effect owner to one declared profile |

The Agent Client captures the original request and authorizes each outgoing
intent before signing. Core code supplies byte rules, cryptographic checks and
admission primitives. The trusted host owns policy content, key custody,
component loading and all protected effect paths. An MCP adapter wraps tool
registration and invocation under that host; an optional model-callable MCP
verification tool is never the mandatory enforcement boundary. A language
SDK exposes a pinned core surface with errors, cancellation and lifetime
semantics; it does not independently redefine the protocol.

`VerifiedMessage` and `AuthorizedCall` are sensible *internal* result types
only if trusted constructors control them and the dispatch capability cannot
be forged, serialized and replayed, or detached from its owner and deadline.
An L3 self-reported profile level is informative until the actual host effect
paths have independent integration evidence. Opaque FFI handles similarly
reduce accidental misuse but do not alone isolate private keys or ledger state.

## Compatibility decisions before code movement

| Change under consideration | Compatibility consequence | Recommended migration |
| --- | --- | --- |
| Make general Go/Rust HTTP verification strict by default | Existing callers accepting absent nonce, coverage, peer binding or replay storage may fail | Introduce explicitly named legacy/archival policy; require a named strict profile in new assemblies; audit consumers and document the breaking API behavior |
| Deprecate old Go `hpke` and transport functions, including `MakeAckTag` | Existing API and old transcript bytes coexist with 0.10.0 | Mark old functions and exact supported scope; retain safe compatibility only with explicit profile selection; never auto-retry a rejected 0.10.0 call through them |
| Move `http_handshake010.go` into transport ownership | Import paths change even if wire bytes do not | Add a temporary forwarding API after import audit, then remove on a declared library-major boundary; keep fixed 0.10.0 parser tests |
| Consolidate `Store`/`Authority` collaborators | Method and state semantics can break adapters | Share only truly stable ports; version replay, registry admission and ledger contracts where behavior changes; do not turn two unrelated `Store` meanings into one interface |
| Resolve [SCA-01](standards-clause-audit.md), [SCA-02](standards-clause-audit.md) and [SCA-03](standards-clause-audit.md) | HTTP accepted algorithms and DID prefix verdicts can change; the JWK source citation is editorial | Decide them in one coordinated normative snapshot with compatibility notes, changed cases and exact-byte vectors before Go/Rust API refactoring |
| Replace existing SDK crypto with core-backed wrappers | Dependency, packaging, key-lifetime and API behavior change | Pin core build/version per language; compare byte/verdict corpus; migrate or archive old SDK entry points only after downstream-consumer review |

The earlier [standards decisions](standards-revision-decisions.md) retained a
private secp256k1 HTTP `alg`. The later [clause audit](standards-clause-audit.md)
found that choice inconsistent with RFC 9421's registered-`alg` requirement.
The latter is an open normative finding, so the earlier acceptance must not be
treated as settled when designing the HTTP API. The preferred correction is
the audit's registered-HTTP-algorithm boundary, keeping any private suite only
where its separate non-HTTP rules actually permit it. This recommendation is
**not** adopted by this review. Do not switch algorithms or keys implicitly.

## Package names and SDK decision

For a later code change, prefer Go `pkg/agent/ports` for stable host-supplied
contracts and `pkg/agent/runtime010` for version-specific assemblies; the Rust
analogues would be `src/ports` and `src/runtime010`. Keep version-sensitive
admission contracts named or nested by profile. These are proposed names,
not directories created here. The untracked `sage/contracts/` input remains
untouched and must be reviewed before selecting a final package path.

Prefer direct `rs-sage-core` use for native Rust applications. Keep
`sage/sdk/rust/sage-client` only as a narrow compatibility facade if an import
audit finds users; otherwise archive it after a migration notice. Python,
TypeScript and Java should target a pinned Rust C ABI or WASM build where the
platform and key-custody model permit it. If a platform cannot safely support
the required callback, persistence or cancellation contracts, mark that
profile unsupported instead of filling gaps with a second crypto stack.

## Ordered handoff

1. Close the open normative standards/scope decisions, including SCA-01..03,
   as one coordinated `sage-spec` revision. Update charter/profile/chapters,
   compatibility guidance and traceability together; preserve old snapshots.
2. Pin a clause-by-clause Go/Rust gap map to that exact revision. Distinguish
   an implementation defect from an unresolved specification question.
3. Design the public strict entry points and host ports with consumer/import
   audit and migration notes. Refactor L0/L1/L2 ownership before introducing
   L3 assemblies; do not move packages simply to mirror the diagram.
4. Implement matched Go and Rust assemblies with unit tests and safe runtime
   tests of real transport and host seams. Do not build reusable attack
   reproduction code. Preserve explicit failure, timeout and no-verdict denial.
5. Run `sage-inspector` against the new pinned revision and both built cores;
   retain earlier 481 planned parents and prior runtime records as historical
   evidence until version-matched results exist.
6. Only then migrate SDKs, add a paired Agent/MCP example and the protected
   versus unprotected comparison, and consider physical repository extraction.
   Runtime Registry Source and selected-host enforcement remain separate
   deployment gates; organizationally independent audit and release judgment
   follow after stable evidence.

This sequence agrees with the [fixed execution order](https://github.com/SAGE-X-project/sage-inspector/blob/e003a22ea6be0fc2207e3f514a844fe458515b3c/docs/execution-order.md)
and the [migration plan](../architecture/migration-plan.md). The current
review establishes a recommended implementation pattern and migration order,
not source conformance, cryptographic security, complete mediation or
production readiness.
