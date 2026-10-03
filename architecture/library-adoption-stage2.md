# Stage 2: library adoption and consumer audit

Status: completed source/API and consumer inventory for the ordered program's
second stage. This is **not** a 0.10.0 protocol amendment, a protected-host
integration contract, or an implementation-conformance verdict. Stage 3 defines
the host contract; stage 4 reviews any normative changes before a core refactor.

## Revision and method

| Input | Pinned revision | Role |
| --- | --- | --- |
| Go `sage` | `fbd9b2169c72d62c62dcbaa2336275d08a5735a8` | Module, exported Go AST declarations, package imports and current host seams. |
| Rust `rs-sage-core` | `0a6f1e0356f323d6f0bcca5bd96ad3fdab82297f` | Cargo metadata, `syn`-parsed public declarations, module routing and C header. |
| `sage-spec` stage-1 baseline | `85fee1830b2bc0d2420557df40796ae83073de12` | Ordered program and 0.10.0 design baseline. |
| `sage-inspector` stage-1 baseline | `286f1cc707c819d0c1d589efc4a9fd7c8568273f` | Existing adapter consumers and pending implementation evidence. |

The [machine-readable map](../analysis/library-adoption-stage2/source-consumer-map.json)
records tracked-file Go AST exports/imports, Rust `syn` public declarations and
consumer imports at their own Git revisions. The parsers and map builder are in
the same directory. Go build tags and Rust `cfg` can narrow an AST-listed
declaration; a `pub` item inside a private Rust module also needs a public
module route or re-export. The build probes below test representative reachable
paths. The inventory excludes tests as production consumers and does not infer
runtime behavior from an import.

The Go checkout had an unrelated untracked `contracts/` directory. It was left
untouched and excluded by the map's tracked-file filter. The original
`sage-spec` design branch was also left untouched; this audit was prepared on
an isolated branch from the stage-1 main revision.

## What can be reused now

| Surface | Go source boundary | Rust source boundary | Adoption result |
| --- | --- | --- | --- |
| Canonical bytes, identity and HTTP signatures | `pkg/agent/crypto/jcs`, `did`, `core/rfc9421` | `jcs`, `did`, `rfc9421` | Importable primitives. A signature or parsed DID alone does not admit a tool call. |
| Registry observation | `registry010.NewGate(Config, Source, Clock, Store)`; web validation helpers | `registry010::{Source, Clock, Store, Gate}` and helpers | Gate accepts a **trusted, fully validated** source projection. The deployment still owns origin/chain verification, freshness/finality, storage and source custody. Some bounded web fetch/check helpers exist, but no universal validating registry source. |
| Session and transport | `hpke.NewCompletionEndpoint010`, replay-store interface, `session`, HTTP/MCP carriage helpers | `hpke::completion010::CompletionEndpoint010`, replay-store trait, `session` | Composable handshakes and records. The host owns endpoint identity, durable replay scope, transport-to-session binding and lifecycle across restarts. |
| Signed intent and execution | `guard010` authority/policy interfaces, `OpenClient`, `OpenDispatchGate`, MCP endpoint and result APIs, `execution010` ledger | Corresponding `guard010` traits, `Client`, `DispatchGate`, MCP endpoint and `execution010` ledger | The core enforces bounded transitions around trusted callbacks and journals. It cannot prove that a host captured the real original input or that a loaded plugin is the measured instance. |
| Library and ABI form | One Go module, `github.com/sage-x-project/sage`, with public `pkg/agent/...` packages and substantial transitive dependencies | Crate `sage_crypto_core` 0.3.0 declares `rlib` and `cdylib`; C ABI is gated by `ffi` | Go source imports and Rust native linking are possible. The C header/exported ABI exposes general crypto/HTTP/session functions, not the 0.10.0 Guard, Registry or MCP protected host assembly. |

The exact declarations and source files are in the map. The principal Go
`guard010`, `registry010`, `hpke` and `execution010` directories contain 106,
67, 106 and 9 exported top-level declarations/methods respectively in the
tracked AST scan. The corresponding Rust directories contain 114, 72, 156 and
8 syntactically public declarations/methods. These counts are an inventory,
not a measure of completeness or conformance.

## Trust, lifetime and callback boundary

| Boundary | Existing contract | Still required from an external host |
| --- | --- | --- |
| Original request and final arguments | Guard commitments bind exact original bytes, policy and manifest; `Client` accepts a signed canonical intent. | Capture the actual user/Agent input before model or plugin expansion, protect it from later mutation, associate one operation with one journal, and check final arguments at the same protected execution point. An optional MCP call does not force the Agent client to use this path. |
| Keys and identity | `RegistryAuthority` uses `registry010.Gate`; completion endpoints compare local Ed25519/X25519 material with currently registered keys on use. Go completion copies seed/key bytes; Rust owns a `SigningKey` and zeroizing KEM buffer. | Provision and protect local signing/KEM keys, pin identity and roles, build a validating registry `Source`, control rotation/revocation and quarantine uncertain state. The generic Rust C API permits private-key export/import, so FFI custody policy must be supplied by the embedding product. |
| Durable state | Guard client/dispatch journals, registry store, HPKE replay store and session state have separate scopes. Create and reopen are distinct; failed or uncertain operations can retain locks or `UNKNOWN` outcomes. | Stable identity-to-path mapping, trusted storage ownership, rollback resistance, cross-process exclusivity, replay retention across transports/restarts, crash recovery and a single terminal consumption path. |
| Execution handoff | `Component.Check`/`Commit` and Rust equivalent must use the same pinned instance; dispatch serializes verification, replacement, retirement and bounded commitment. | Immutable loaded plugin/skill/MCP measurement, an atomic exact-argument handoff, bounded callback deadlines, capability isolation and durable administrative updates. Running a tool after an optional check would bypass the intended boundary. |
| Sending and results | `ClientSender.Commit` is a bounded one-request handoff; `ResultSigner` produces a verified signed outcome; MCP wrappers map authenticated results. | Bind the actual outer request ID, nonce/session and recipient to the exact intent, prevent deferred duplicate sends, authenticate negotiated MCP version, protect response routing, and release output only after first durable terminal acceptance. |
| Failure and cancellation | Go Guard uses a uniform `ErrInvalid`; Registry distinguishes rejected, stale and unreachable observations. Sender errors can mean transmission occurred. Rust Guard uses `Invalid`; many Rust trusted callbacks are synchronous traits. | Map local diagnostic categories to protocol-visible failures without leaking sensitive detail; treat uncertain handoff as uncertain, never auto-retry effects; bound synchronous Rust callbacks at the host/process boundary and propagate Go `context` cancellation. |

These host duties are existing source-contract observations, not a newly adopted
normative profile. No package move or compatibility-breaking API change is made
by this audit.

## Existing consumers at the pinned revisions

| Consumer | Observed use | Consequence |
| --- | --- | --- |
| `sage-gateway` (`4e7266857676`) | Imports Go RFC 9421, key and DID packages for HTTP signing/verification middleware. | Demonstrates primitive reuse. Response verification is configured only when a peer resolver is supplied; it is not the complete 0.10.0 Guard/MCP host path. |
| `sage-registry-service` (`baf5570578dd`) | Imports `registry010` for a service-specific web journal and administrative/public handlers. | Demonstrates one concrete Registry consumer; its deployment TLS, credentials and storage choices remain service responsibilities. |
| `sage-adk` (`6037298b4905`) | Imports legacy `sage/core`, `sage/crypto`, `sage/config` and `sage/did` paths. Its `go.mod` replaces `sage` with `../../sage`. | The replacement resolves outside the current `sage-x-project/sage` checkout and the legacy paths are absent at the current Go revision. It is not evidence that today's core is directly usable by this Agent adapter. Do not silently rewrite it in stage 2. |
| `sage-inspector` (`286f1cc707c8`) | Go adapters import Guard, Registry, HPKE, session and primitive packages; four Rust adapter manifests use a path dependency on `sage_crypto_core`. | Useful compile/test consumers, but fixture/adaptor behavior is not a deployed protected Agent or MCP host. Its implementation verdicts remain revision-bound. |
| `sage-a2a-go` (`574e787cb40b`) and `sage-proxy-server` (`eb7e9340d358`) | No tracked production Go import of `github.com/sage-x-project/sage` found. | No adoption claim follows from repository names or proximity. |

The machine map records exact import paths and files. The audited set is the
six nearby repositories above, not every possible external adopter.

## Packaging and build probes

- An isolated external Go module with a local `replace` imported `guard010`,
  `registry010`, `hpke`, `session` and `core/rfc9421`; `go test -mod=mod ./...`
  passed. It proves import/compile at this checkout, not protection of a host.
- `cargo metadata --offline --no-deps` confirms Rust `rlib`/`cdylib`, default
  empty features and optional `ffi`. In an isolated `git archive` copy,
  `cargo check --offline --lib`, `cargo check --offline --lib --features ffi`
  and `cargo build --offline --lib --features ffi` passed. An external Rust
  crate also compiled imports of the public Guard, Registry and HPKE types;
  the completion endpoint's actual path is `hpke::completion010`, not the
  shorter `hpke` re-export. The built macOS
  dynamic library exposes 52 `sage_*` C symbols; neither that symbol set nor
  `include/sage_crypto.h` includes `sage_guard*`, `sage_registry*`,
  `sage_hpke*` or `sage_mcp*` entry points.
- The Rust checks used an offline regenerated lockfile because the tracked
  source revision contains no `Cargo.lock`; they prove current source builds
  against the locally cached compatible dependency resolution, not a pinned
  redistributable binary/ABI. No cross-platform ABI, runtime integration or
  conformance test was inferred from these probes.

## Stage 2 exit and next boundary

The source/AST map, consumer map and representative build probes satisfy the
stage-2 **analysis** exit. Reusable primitives and current host seams are
identified, while the missing protected host assembly is explicit. In stage 3,
define a host-port contract for capture, independent authorization, exact
intent, signing, final dispatch, result verification and fail-closed behavior.
For Agent-client plugins, record which pre-decision and pre-dispatch hooks are
actually enforceable per product; a callable MCP tool alone is insufficient.
Only stage 4 should reconcile that contract into normative `sage-spec` and
`sage-inspector` cases. Stage 5 may then change Go/Rust packaging and APIs
against those adopted contracts. No full Inspector `PASS` or security guarantee
is asserted here.
