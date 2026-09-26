# sage-spec

**SAGE protocol 0.10.0 — documentation design, not an implementation release.**

This repository defines identity, authenticated messaging and Agent/MCP execution
protection for independent implementations. It updates existing documents in place,
based on the Go `sage` code and design documents, Rust core and inspector evidence.
Implementations are evidence, never authority where the text is silent.

## Specification

| Document | Responsibility |
|---|---|
| [Charter](charter.md) | Purpose, trust boundaries, adversary, R-1..R-45 |
| [00 Overview](spec/00-overview.md) | Conventions, layering, versioning, conformance |
| [01 Crypto](spec/01-crypto.md) | Keys, signatures, encodings |
| [02 JCS](spec/02-jcs.md) | Canonical JSON and rejection |
| [03 HTTP signatures](spec/03-rfc9421.md) | RFC 9421/9530 profile and request-bound responses |
| [04 HPKE](spec/04-hpke.md) | Authenticated transcript, combiner, confirmation |
| [05 Sessions](spec/05-session.md) | Keys, records, sequence, replay, closure |
| [06 DID](spec/06-did-sage.md) | Grammar and key selection |
| [07 Agent Card](spec/07-a2a.md) | Card proof and registry binding |
| [08 Transport](spec/08-transport.md) | Authenticated wire envelopes |
| [09 Registry](spec/09-registry.md) | Lifecycle, profiles, authoritative state |
| [10 Resolution](spec/10-resolution.md) | DID document projection and reads |
| [11 Registries](spec/11-registries.md) | Algorithms, labels, headers, diagnostics |
| [Execution Guard](profiles/agent-mcp-security.md) | Mandatory verification and fail-closed execution |
| [Non-HTTP MCP binding](profiles/non-http-mcp-security.md) | Adopted connection ownership, negotiation and execution admission design |
| [Integration guide](guides/integration.md) | Agent/SDK/hook/MCP integration |

## Evidence and follow-up design

- [Document/code graph](analysis/graphs.md), [JSON graph](analysis/graphs.json),
  [purpose and vision](analysis/purpose-and-vision.md).
- [Inspector plan](verification/inspector-plan.md), [traceability](verification/traceability.json),
  [standards review](verification/standards.md), [review evidence](verification/review.md).
- [Repository roles](architecture/repository-roles.md), [migration](architecture/migration-plan.md).
- [Preserved design branch review](verification/preserved-design-review.md) records which
  architecture and standards proposals need revision before a new specification snapshot.
- [MCP binding errata candidate](proposals/non-http-mcp-errata/candidate.md) preserves
  the reviewed input for the adopted local binding identity and exchange ordering.
- [Next-revision scope decisions](proposals/non-http-mcp-errata/scope-decisions.md)
  distinguish changes to carry forward from claims left outside 0.10.0.
- [Process](PROCESS.md), [changelog](CHANGELOG.md), [approved Seed](seeds/sage-spec-0.10.0.yaml).

## Status and limits

The former `1.0.0-draft.1` was a Go snapshot. Continuing as `0.10.0` is an explicit
version-policy reset, not a downgrade or promise of byte compatibility. Security
corrections may change wire formats. Exact 0.x versions are matched.

The six JSON suites in [vectors/](vectors/README.md) remain historical and retain
their embedded version. They do not certify 0.10.0. No Core, SDK, MCP, inspector
or demo code is implemented here. Full binding interoperability and formal security
proof are not established. Earlier partial Inspector/core runtime evidence retains its
original scope and is not promoted by this documentation update.

Execution Guard assumes protected Client capture, keys, policy, verifier, baselines
and final dispatch. It covers compromised ordinary Plugin/MCP/Skill components
under that boundary, not semantic safety or a fully compromised trusted host.

## Licence

Apache-2.0; see [LICENSE](LICENSE). This is RFC-style specification work, not an
IETF RFC. Examples describe proposed behaviour rather than deployed services.

## Adopted MCP design and historical proposals

The [original adoption record](verification/mcp-adoption.json) fixes the reviewed
non-HTTP MCP 2025-06-18 design and its 457-case historical plan. The
[errata adoption record](verification/mcp-errata-adoption.json) pins the preserved
466-case amendment. The [earlier revision record](verification/spec-revision-adoption.json)
pins 91 rule groups and 471 top-level planned cases. The
[registry proof correction](verification/registry-proof-revision.md) adds eight
planned parents, for 479 total: 386 baseline cases, 71 original MCP binding
parents, nine errata parents, five earlier revision parents and eight registry cases.
The plan also has 26 mandatory child assertions.
All are planned/unexecuted in this normative plan; historical runtime reports remain
separate and must be mapped by exact case evidence. This is design adoption, not a tag,
release, third-party audit or a claim that either core supports the whole binding.

The [cross-review](proposals/non-http-mcp-setup/cross-review.md) records two separate
agents and their re-review. Proposal files remain frozen with their historical statuses;
current normative requirements live in profiles/ and spec/. Do not select an earlier
proposal's different admission definition instead of the adopted profile.
The [remaining work](proposals/non-http-mcp-setup/remaining-work.md) tracks implementation
and deployment follow-up.

Graphs and dated review records describe their pinned source inputs; they are not
live indexes of the current core repositories or new execution evidence.
