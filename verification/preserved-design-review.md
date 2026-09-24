# Review of the preserved design branch

Date: 2026-09-24. This review resumes the `docs/design-and-integration-review`
work as an input to the next specification revision. It does not adopt that branch
as a replacement for the current 0.10.0 normative design and does not change a
protocol rule. The reviewed normative `main` revision is
`263cd1a05c145ed19efae6310d22e8b6a5114be6`; the preserved branch was at
`9f6901c29412561e38c14cff7279d3751bcc0885` with an uncommitted working
tree. Its two branch-specific committed documents were:

| Input | SHA-256 of read file | Role |
| --- | --- | --- |
| `architecture/integration-architecture.md` | `50b9a1cb18028fb9a3c098b9bf44a0505b1b821e7afb08a592508cf9073687a5` | Proposed library and integration layering |
| `verification/design-standards-review.md` | `1dac095f909bd83424563f90e183af906a528d1f4a663ef2efba4599ac7fe431` | Dated findings against an earlier draft |

Of 17 modified tracked and 17 untracked working-tree files, 12 in each group
already matched `main` byte for byte. The remaining ten working-tree files
(`CHANGELOG.md`, `PROCESS.md`, `README.md`, `charter.md`, `spec/00-overview.md`,
`guides/integration.md`, `profiles/agent-mcp-security.md`, and three
`verification/` files) predate the adopted non-HTTP MCP profile and its
91-rule/457-parent traceability. They must not be copied over `main`: doing so
would remove adoption and admission clarifications. The preserved branch and
its uncommitted files were read only.

The ten divergent working-tree inputs are pinned below. The tracked working
diff from branch `HEAD` has SHA-256
`47f97ad51e238afcd6badb2316dc7473552577391fc4fe90eec779ab1c2b27f7`
when emitted with `git diff --binary HEAD`; the untracked entries are identified
by their individual file hashes.

| Divergent path | SHA-256 in preserved worktree |
| --- | --- |
| `CHANGELOG.md` | `1053d8a2daab2103fbefbeab07c4c51b47142439cc22fe229dd29479c20d087b` |
| `PROCESS.md` | `584ad61d932ab016387963bc944be08949b10d73f9ccaf0c59094f60de414372` |
| `README.md` | `5cb1f5dd20384049a4986314dfa0517e1f266699e4807b57598b7035c359ea37` |
| `charter.md` | `1cb5ac4c29eb0a536ec9e3fb80c37431c18610f65357d8b52d41933aa2568c60` |
| `spec/00-overview.md` | `3ad861a60bcb21d26eb974109da5f753ad8fefffd04780ed2f2b0f2a10a82227` |
| `guides/integration.md` | `535304348249cc68cb84c1014a9aeaec9c38eceb5beb50a13cc21f4eda838a92` |
| `profiles/agent-mcp-security.md` | `99d5dc57d12d59d6e33102b2fdaa44efb137e48deab65e8012ff5128838d04b1` |
| `verification/inspector-plan.md` | `a5c6ba25e4cd4d1d1a687034c698bcfd0e07d634173582f74827c36fcd83a33e` |
| `verification/review.md` | `fd1a393640fc56890ea11c1ca50d4e03c9e7e8119e3fdc26e36b56423d0b6e56` |
| `verification/traceability.json` | `c4db008e83ad9491559941ce6cb36960eea4fe3ba1ec6c698d7d77ea91ea009c` |

## Integration architecture disposition

The proposed L0 pure encoding, L1 cryptographic verification, L2 trust/admission
decisions, and L3 deployment assemblies are useful **implementation boundaries**.
They fit the intended reusable Go/Rust cores, thin language SDKs and separately
owned Agent/MCP applications. They do not create new protocol conformance levels
or replace the charter's Verifier, Peer, Registrar and Execution Guard levels.

| Proposal | Disposition for the next design pass |
| --- | --- |
| IA-01..04 and IA-05 | Keep the separation of pure bytes, cryptographic validity, trusted authorization and application assembly. Recheck package and dependency claims against pinned current core revisions before moving code. An assembly may choose mechanism defaults but cannot invent authorization policy. |
| IA-06 | Keep guarded tool registration as a useful integration seam. A guarded registry alone cannot prove complete mediation: direct tool effects, subprocesses, file/network paths and the non-HTTP MCP owner must remain within the trusted enforcement boundary. The adopted [owner profile](../profiles/non-http-mcp-security.md) controls its connection and admission sequence. |
| IA-07 | Restrict HTTP `RoundTripper`/`Handler` advice to the HTTP profile. HTTP wrappers do not implement the selected **non-HTTP** MCP binding. Route enumeration helps at startup but cannot establish that every runtime effect path is mediated. Existing-host integration requires a host-specific interception/effect-boundary contract and evidence. |
| IA-08..10 | Distinct `VerifiedMessage` and `AuthorizedCall` types can reduce accidental misuse, provided construction is restricted to the trusted owner and a dispatch capability cannot be forged or serialized. Type checks and an assembly's self-report are not proof against a compromised host or bypassable effects; conformance still needs Inspector and deployment evidence. Missing required collaborators must fail construction. |
| IA-11..12 | A shared collaborator package can reduce duplicate interfaces, but keep wire **and stateful admission semantics** versioned where behavior changes. An unversioned `Store`/`Authority` interface must not silently mean different things to 0.10.0 and a later profile. Decide this with both cores after the revised specification is fixed. |
| IA-13 | Opaque FFI/WASM handles are a useful SDK boundary, not key isolation by themselves. Pin the core version, session lifetime, failure propagation and host custody of keys/ledger state. |

The architecture document's implementation sequence starts with package moves.
The [fixed execution order](https://github.com/SAGE-X-project/sage-inspector/blob/2b278fc23e9a55d1dc90554e1b976bc6104ae791/docs/execution-order.md)
instead puts specification review and a new traceability snapshot before Go/Rust
refactoring. Follow that order. The architecture's Go/Rust observations were
bounded static reads, not full current conformance results; Go
`2fb4755ba38d1c90adea5089402fcc6b8981fd71` and Rust
`40b5a8c6d76d952131013d8a034f819fd31b7ca0` need a fresh, clause-based
gap map at the implementation step.

## Standards and design findings

The older standards review is valuable as a candidate list, but its priority
and proposed fixes are not automatically current decisions. A spot check of the
official [HTTP semantics](https://www.rfc-editor.org/rfc/rfc9110.html),
[HTTP signatures](https://www.rfc-editor.org/rfc/rfc9421.html),
[JWK](https://www.rfc-editor.org/rfc/rfc7517.html),
[BCP 178](https://www.rfc-editor.org/rfc/rfc6648.html) and
[Controlled Identifiers 1.0](https://www.w3.org/TR/controller-document/)
supports the distinctions below; other findings remain candidates for targeted
review, not externally audited conclusions.

| Earlier finding | Current assessment and required decision |
| --- | --- |
| DSR-S01, HTTP content coding | Reclassify from claimed honest-peer interoperability failure to an integration hazard. [MSG-01](../spec/03-rfc9421.md) already requires **senders** to omit `Content-Encoding`, including responders, regardless of a request's `Accept-Encoding`. A conforming responder therefore does not compress. Guidance or a later explicit `Accept-Encoding: identity` requirement can protect users of default HTTP libraries, but the old P1 rationale is too strong. |
| DSR-S02, multiple signatures | Reclassify from RFC contradiction to a deliberate narrow-profile interoperability choice. RFC 9421 permits multiple signatures, but a profile may require one. Relaxing the `sig1` cardinality rule would also affect parsing, request-bound response coverage and multiple-signature confusion; do not apply the proposed “ignore all other labels” fix without a full security and vector review. |
| DSR-S03, optional JWK members | Keep open as a specific profile-versus-R-14 compatibility question. RFC 7517 requires a generic JWK consumer to ignore unknown members; SAGE's exact projection and strict acceptance are narrower. Decide whether SAGE accepts additional public members without using them for authority, or narrows its generic DID-consumer claim. Preserve private-key and contradictory-key rejection. |
| DSR-S04, `X-SAGE-*` | Keep as a naming and migration decision. BCP 178 says new names **SHOULD NOT** use `X-`; it does not make the existing names invalid. A rename changes signed HTTP components and deployments, so it belongs in a versioned compatibility decision. |
| DSR-S05..S07 | Preserve the private-algorithm-name decision; verify Ed25519 implementation agreement and reference coverage separately. |
| DSR-S08 | Keep open as a reference and vocabulary mismatch. Controlled Identifiers 1.0 defines `JsonWebKey`, while `JsonWebKey2020` exists in older DID registries. Choose the target vocabulary and compatibility behavior before editing chapter 10. |
| DSR-D01 | Decide whether 0.10.0 explicitly limits Execution Guard authorization to one hop or adds a verifiable delegation model. An Agent-to-Agent transport path does not itself delegate a user's authorization. Do not add a nested chain field without a trust and replay model. |
| DSR-D02..D03 | Decide the claimed policy floor and whether argument provenance can be generated and enforced by a trusted Client. A signed provenance field cannot prove origin if the host inferred it incorrectly. Keep cryptographic integrity and semantic prompt safety claims separate. |
| DSR-D04..D05 | Specify any per-request work budget and pre-authentication registry-work limits without weakening current authoritative freshness or creating an identity-existence oracle. Treat resolver outages as fail-closed and record their availability cost. |
| DSR-D06 | Add a migration account for changed DID grammar and unsupported Solana profile before release claims; do not silently alias old IDs. |
| DSR-D07 | Replace its historical count of 77 rule groups/386 planned cases with the adopted 91 groups/457 parent cases plus 26 mandatory children **only in a new review**, not by rewriting the historical report. Current Inspector evidence and remaining `NOT_RUN` scopes retain the [integrated verdict](https://github.com/SAGE-X-project/sage-inspector/blob/2b278fc23e9a55d1dc90554e1b976bc6104ae791/docs/ins11-integrated-verdict.md). |

## Next revision boundary

First resolve the two open normative errata in the
[post-adoption review](post-adoption-errata-review.md): protected-call
concurrency/overload and a stable local binding identity with descriptor-digest
checks. In the same design pass, decide the standards and scope questions above
that affect accepted bytes or security claims. Then update the relevant normative
chapters, profile, charter, compatibility notes and traceability **together** in a
new pinned revision. Keep the 0.10.0 adoption snapshot and historical reports
intact. Only after that revision should the Go/Rust layer refactor and Inspector
re-run be planned against concrete clauses. External review remains outstanding.
