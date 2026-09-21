# Documentation-first migration plan

Status: proposed future implementation sequence from the approved protocol **0.10.0** Seed. This change performs no code movement, repository creation, package removal, new executable vectors or inspector implementation. Existing source changes, including untracked `sage/contracts/`, remain untouched.

## Baseline and constraints

Baseline commits: `sage c7709b7486e0da94336edc0931fddd87f6a45343`, `rs-sage-core 206bbbb5a66667ae2feb3b0e9991ed1ca4622bb2`, `sage-inspector 05b890d973cf3b62a82ba412462af746aa5c266d`, source `sage-spec f4a4e7fbf71a665785984eef7609b2e8fabe833d`. [Graphs](../analysis/graphs.md) record the current tracked-doc inventory and static Go graph; [purpose and vision](../analysis/purpose-and-vision.md) distinguishes observations from interpretations.

Earlier `sage/docs/refactoring/v2/review/11-repository-split-and-research-plan.md` is lineage, not this plan's release commitment. Old v1.6/v1.7/v1.8 deletion dates and the prior 1.0.0-draft protocol target are not imported automatically. Security-motivated incompatibilities are allowed by the Seed, but every wire change still needs explicit migration behavior and compatibility evidence.

## Ordered gates

| Gate | Future work and accountable role | Exit evidence | If gate fails |
|---|---|---|---|
| 0 — Specification baseline | Spec owner reconciles wire chapters, profile, RFC choices, rejection behavior and version history. Record every implementation-affecting change from previous draft. | Reviewed 0.10.0 text; requirement-to-test plan links; no unresolved ambiguity that changes accept/reject or bytes. This delivery is documentation evidence only. | Keep draft status; do not label implementations compliant. |
| 1 — Implementation gap mapping | Go/Rust owners map each normative requirement to source and current behavior; compare accepted/rejected encodings, limits, transcript binding and state transitions. | Clause-by-clause gap matrix with pinned commits; every deliberate incompatibility named. | Fix specification contradiction first, or assign implementation defect; do not treat existing defaults as normative. |
| 2 — Inspector and test corpus | Inspector owner implements the separate [verification plan](../verification/inspector-plan.md), trusted expected-identity inputs, replay/context handling and errors. | Positive/negative cases including boundary, replay, restart, concurrency, revocation and timeout; distinguish old assets from new cases. | Incomplete categories remain unverified; no blanket pass from existing vectors. |
| 3 — Go and Rust cores | Core owners implement 0.10.0 profiles with explicit strict configurations and persistent/stateful replay where required. | Shared corpus agreement plus live Go→Rust and Rust→Go request/response and session exchange; failures agree, not just successful bytes. | Keep incompatible versions isolated; never silently retry protected traffic unsigned or on an older profile. |
| 4 — Trusted Agent/MCP adapters | Adapter owner binds Client-authorized operation to actual execution, validates responses before use, and connects protected component hash/manifests to executable instance. | Bypass tests for direct, nested, parallel and retry paths; changed args; unavailable verifier; missing hook; altered component after check; no side effects on rejection. | Disable the protected feature/claim. A product without enforceable interception does not claim this integration profile. |
| 5 — Language SDKs | SDK owners wrap proven Go/Rust surfaces; select ABI/WASM/native packaging per language, document key custody, memory/error and cancellation semantics. | Core version pinned; byte/verdict corpus plus lifecycle and callback tests; transport and tool wrapper enforce the same profile. | Do not port experimental SDK cryptography or publish inferred compatibility. |
| 6 — Registration/query services | Service/contract owners expose verified card/key lifecycle and discovery using spec-defined state/freshness policy; component manifests stay distinct from identity registration. | Registration/activation, key update/revocation, stale cache, resolver outage and reorganization-policy tests against pinned ABI/network context. | Deny requests that cannot establish required trusted state; do not fall back to unverified metadata. |
| 7 — Demos and physical extraction | Application owners build matched SAGE/no-SAGE examples, then consider splitting CLI, wrappers, services and demonstrations according to [roles](repository-roles.md). | Same workload/attacker baseline; exact commits/platform; both defended and residual cases. Consumer import audit and independently buildable packages precede any move. | Keep directories in existing repositories; repository count is not a delivery metric. |

Gates 4–6 can proceed independently only after their required core and profile contracts are stable. Physical extraction is deliberately last: moving code before correctness evidence distributes existing gaps across repositories.

## Existing-to-target responsibility mapping

| Existing sage responsibility | Target role | Migration treatment |
|---|---|---|
| `pkg/agent/core/rfc9421`, `crypto/{jcs,keys,formats}`, `hpke`, `session` | Go library | Keep reusable primitives; add conformance without copying code into SDKs. Review nil/optional policy defaults and make adapter requirements explicit. |
| `pkg/agent/did`, `did/ethereum`, `did/solana`, generated AgentCard binding | Core interfaces + registry adapter/service | Separate pure identity/card validation from remote resolution and operations where useful; pin ABI, preserve verified source provenance. No binding regeneration in this change. |
| `pkg/agent/transport/{http,websocket}` | Core-compatible transport integration | Keep wire-independent interfaces; ensure strict signing/verification and body/target equivalence at real transport boundaries. |
| `pkg/agent/handshake`, `core/message`, `core/message/nonce`, `crypto/vault` | Compatibility assessment | Historical analyses identify deprecations. Re-read current exported-use evidence before removal; do not assume old deletion timetable or zero external consumers. |
| `cmd/*`, `internal/{app,cli,config}` | CLI/application | Extract only after library release and import audit; keep behavior/error contract and backwards migration instructions. |
| `sdk/{python,typescript,java,rust}` | Thin SDK wrapper projects (proposed) | Audit current behavior; replace divergent crypto paths with proven core use, or archive explicitly. Never relabel current stubs as compliant. |
| `examples/mcp-integration/*` | Adapter examples and security comparison demos | Preserve educational lineage; add real mandatory enforcement and negative cases before security claims. |
| `pkg/storage`, `pkg/oidc`, `pkg/health`, `pkg/telemetry` | Context-dependent service/application support | Use import evidence and external-consumer review to decide retention/move. Static in-module zero use is not sufficient to delete public API. |
| `tools/codegraph`, prior review documents | Analysis tooling and evidence lineage | Reuse existing tool with documented limitations; no new generator or product dependency. |

## Version transition and rollback

Protocol 0.10.0 is a newly defined pre-1.0 target, not a statement that old 1.0.0-draft messages automatically interoperate. Deployment must explicitly select supported profile/version and trusted peers; negotiation must be authenticated where the normative protocol requires it. Separate old-draft compatibility endpoints/configuration from protected 0.10.0 claims. A rejected message must not trigger unsigned, replay-disabled or weaker-profile retry.

A library/SDK release identifies its supported protocol/profile separately from API semver. If a canary fails, stop or route only to a previously approved compatible deployment; rollback cannot bypass freshness/replay/key-revocation requirements. Replay state and key/session migration require an explicit procedure and tests before restart/rollback. Do not resume an old session simply because a binary was downgraded.

Before any package deletion or repository move, inventory downstream importers, publish a migration mapping, retain permitted compatibility aliases where safe, and establish license/release ownership using the project's policies. That audit is future work; this document does not authorize destructive operations.

## Completion evidence and remaining work

This delivery provides design, graphs and inspection contracts. Future completion requires executed adversarial tests, independent core comparisons, real Agent/MCP integration coverage, and deployment-specific verification of protected key/reference storage. Formal modelling may assess handshake/session properties under explicit assumptions; it cannot prove arbitrary LLM intent correctness. Security comparisons must report false acceptance, false rejection and residual attacks instead of claiming that every hacker-modified workflow is prevented.
