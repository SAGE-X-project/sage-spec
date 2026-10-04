# SAGE program sequence

Status: program plan, not a normative protocol amendment or a claim of
implementation conformance. The numbered order below records the intended
dependencies. An unfinished stage is not silently replaced by work from a
later stage. Protocol 0.10.0 remains the current design target; later features
need their own reviewed scope and exact version decision.

## First completion target: specification and Inspector

Stage 1 completes the **design and verification contract** before the core
refactor. `sage-spec` owns the normative rules and independent expected
results; `sage-inspector` owns the case inventory, executable inspection
contracts and evidence states. The Inspector can be ready to assess an
implementation before that implementation exists. In that situation its
implementation verdict is `NOT_RUN` or `UNSUPPORTED`, never `PASS`.

Stage 1 exits only when:

1. The 0.10.0 charter, chapters 00–11, Agent/MCP profiles, registries,
   terminology, compatibility, error behavior, vectors, traceability and
   changelog describe one reviewed revision. Every behavior-affecting
   standards choice has an explicit scope and accept/reject consequence.
2. Each normative requirement maps to independently defined Inspector cases,
   including positive controls, rejection boundaries, lifecycle and failure
   behavior. The current 489-parent/26-child catalog is a starting inventory,
   not a fixed target if the reviewed specification changes.
3. Inspector can enumerate and report every case against the frozen revision,
   bind source and fixture hashes, and distinguish `PASS`, `FAIL`, `PARTIAL`,
   `UNSUPPORTED` and `NOT_RUN`. All implementation-dependent and deployed-host
   cases without a real subject retain their honest pending verdicts.
4. The standards application matrix has a recorded disposition for each
   referenced RFC or other standard and flags any unresolved contradiction.
   A local review closes the design baseline; organizationally independent
   external audit remains a later release gate.
5. The two repositories record the same spec revision and an explicit change
   map. Existing historical evidence and the separate design branch are
   preserved. This exit is **tooling and design readiness**, not full protocol
   conformance or a security guarantee.

The current [specification process](../PROCESS.md),
[Inspector plan](../verification/inspector-plan.md),
[standards application matrix](../verification/standards-application-matrix.md)
and [migration plan](migration-plan.md) provide the detailed work contracts.
The [Inspector remaining-work register](https://github.com/SAGE-X-project/sage-inspector/blob/main/docs/remaining-work.md)
retains revision-bound implementation and deployment obligations.

The [stage-2 library adoption audit](library-adoption-stage2.md) records the
pinned source/API and consumer map. The [stage-3 protected host-port
contract](host-port-contract.md) defines the ordered integration and current
product-hook boundaries without changing normative 0.10.0 text. Stage 4
[reconciliation](../verification/host-port-reconciliation.md) maps its host
ports to existing normative owners and Inspector cases without changing the
reviewed wire or trust rules. The Inspector's companion inventory records
the still-unobserved host evidence; core refactoring remains stage 5.

## Ordered delivery stages

| Stage | Work | Exit evidence and dependency |
| --- | --- | --- |
| 1 | Complete `sage-spec` and `sage-inspector` as described above. | One frozen 0.10.0 design revision, full clause-to-case coverage, and truthful Inspector reports. Core or deployment cases need not pass yet. |
| 2 | Analyze how external Agent and MCP projects can import Go `sage` or link built Go/Rust libraries. Inventory public APIs, packaging, lifecycle, key custody, callback and error boundaries, plus existing consumers. | A pinned source/AST and consumer map that distinguishes reusable primitives from missing protected host assembly. Do not move packages before this map. |
| 3 | Define mandatory protection integration for Agent/MCP implementations and product-specific Agent-client plugins, including clients such as Claude Code and Codex where supported. | A host-port contract for pre-model capture, independent authorization, exact intent, protected signing, final dispatch, result verification and fail-closed behavior. Document each client's enforceable interception capability; an optional MCP call alone cannot guarantee mediation. |
| 4 | Reconcile the stage 2–3 integration contract into `sage-spec` and `sage-inspector`. | Review any normative change against the applicable RFC and MCP standards, version and compatibility rules; add independent cases before implementation. Product hook names remain adapter choices unless an enforceable common contract exists. |
| 5 | Analyze, plan and refactor Go `sage` and Rust `rs-sage-core` against the frozen rules and Inspector contracts. | Importable/library-buildable protected entry points, cross-language byte/verdict parity, unit and safe runtime checks, explicit unsupported boundaries, and version-pinned Inspector results. |
| 6 | Build a runnable demo Agent using the completed cores. | Comparable SAGE-enabled and baseline workflows with the same workload, measured defended behavior and residual risks; no universal security claim from a demo. |
| 7 | Extend the specification and Inspector for the intended A2A and DID standard interoperability. | A separate standards and version review, exact identity/card/resolution mapping, independent consumers, and positive/negative cases. Preserve the validated 0.10.0 baseline until the change is adopted. |
| 8 | Update `sage`, `rs-sage-core` and the existing `sage-contracts` repository for the adopted stage 7 revision. | Pinned API/ABI and registry transition evidence, cross-core checks, and Inspector verdicts for the new revision. |
| 9 | Update the stage 6 demo to the stage 7–8 identity and contract model. | Repeated comparable measurements with exact revisions and the same stated limitations. |
| 10 | Design and implement a facilitator for Agent/MCP key creation, registration and lookup using the proven cores and contract lifecycle. | Clear custody and operator authorization, registration/rotation/revocation recovery, trusted source freshness, and user-facing failure behavior. |
| 11 | Design a distinct service-discovery protocol for finding SAGE-enabled Agents and MCP services, considering both Web2 and Web3 authority models at this stage. | Explicit trust anchors, identifier/card/service relationships, freshness, privacy, downgrade behavior, versioning and Inspector cases. Discovery metadata alone never grants execution authority. |
| 12 | Design non-repudiation evidence and debugging records for Agent/MCP interactions and evaluate a WBFT-based Agent settlement infrastructure chain. | Signed event provenance, time/finality and retention rules, privacy-preserving evidence commitments, reproducible verification and a separation between protocol acceptance and actual off-chain outcome. |
| 13 | Specify governance and validator checks for an Agent using another Agent or MCP service, then implement only deterministic, reviewable checks. | Validators distinguish valid/invalid protocol evidence, policy admission, execution result and unresolved outcome. Consensus cannot by itself decide arbitrary malicious intent or guarantee semantic safety. Sensitive prompts, credentials and private outputs do not become public chain data. |
| 14 | Launch a testnet for the approved settlement/governance revision and evaluate it as an Agent/MCP network layer. | Versioned protocol and contract deployments, independent validators, measured failure/recovery behavior, privacy and performance evidence, migration policy, and clearly bounded security claims. |

The future discovery, settlement, governance and testnet stages are research
and design commitments, not implicit 0.10.0 requirements. Their protocol
versions, Web2/Web3 split, WBFT deployment model and economic or governance
parameters are determined in their respective stages. Initial identity/Card
registration already controlled by an adversary remains a separately scoped
future design problem; later runtime protection does not repair that origin.
