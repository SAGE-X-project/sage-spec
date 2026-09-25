# Preserved design branch disposition

Date: 2026-09-25. This is the post-plan review of the preserved
docs/design-and-integration-review branch against sage-spec main at
5ec68684df4e449a3963724444bfba64a70b825f. The preserved branch was
9f6901c29412561e38c14cff7279d3751bcc0885 plus uncommitted files.
It was read only. This review changes no normative protocol rule and does
not promote historical Inspector evidence to the current 0.10.0 snapshot.

The comparison covers 17 modified tracked files and 17 untracked files.
Eight tracked and ten untracked files match current main byte for byte.
The other nine tracked and seven untracked files diverge. The preserved
tracked working diff, emitted by git diff --binary HEAD, has SHA-256
47f97ad51e238afcd6badb2316dc7473552577391fc4fe90eec779ab1c2b27f7.
The committed design inputs and their hashes are pinned in the
[earlier review](preserved-design-review.md).

| Divergent tracked files | Divergent untracked files |
| --- | --- |
| CHANGELOG.md, PROCESS.md, README.md, charter.md | architecture/migration-plan.md |
| spec/00-overview.md, spec/03-rfc9421.md | guides/integration.md, profiles/agent-mcp-security.md |
| spec/09-registry.md, spec/10-resolution.md, spec/11-registries.md | verification/inspector-plan.md, verification/review.md, verification/standards.md, verification/traceability.json |

These files are review inputs, not a merge set. In particular, copying the
preserved registry and algorithm chapters would undo the current X25519
key-role and proof-of-possession corrections. Copying the older overview,
profile or traceability would also erase later MCP and per-hop decisions.
Matching files need no re-adoption.

## Architecture decisions

| Proposal in the preserved integration architecture | Disposition |
| --- | --- |
| IA-01 through IA-05: separate pure bytes, crypto validity, trust/admission and deployment | Adopt as informative implementation responsibility boundaries. They are not new conformance classes. The [integration boundaries](../architecture/integration-boundaries.md) record the narrowed contract. |
| IA-06: guarded tool registry | Adapt. It helps register protected tools, but only the actual trusted effect boundary can enforce all dispatch paths. Include subprocess, file, network and dynamically loaded paths in the host-specific review. |
| IA-07: HTTP wrappers and route enumeration | Restrict to the HTTP profile. They neither implement the non-HTTP MCP connection owner nor prove coverage of all runtime effects. |
| IA-08 through IA-10: typed verified/authorized values and required collaborators | Adapt. Restrict constructors and dispatch capabilities to the trusted owner; bind decisions to exact operations; refuse protected assembly when required collaborators are absent. A type or self-report is not conformance evidence. |
| IA-11 and IA-12: shared collaborator contracts | Defer package moves until the new spec snapshot and clause gap map. Version stateful admission semantics explicitly; do not share an unversioned interface across different acceptance rules. |
| IA-13: opaque FFI/WASM handles | Adopt as SDK implementation guidance with pinned core versions, lifetime and failure handling. Opaque handles alone do not provide key isolation from a compromised host. |

The original architecture proposed implementation and package moves before
specification closure. The fixed [migration plan](../architecture/migration-plan.md)
and Inspector [execution order](https://github.com/SAGE-X-project/sage-inspector/blob/2b278fc23e9a55d1dc90554e1b976bc6104ae791/docs/execution-order.md)
put the new pinned specification and traceability first. The original branch
remains intact for later implementation-pattern review.

## Standards and trust findings

The preserved standards report was written against an earlier draft.
[Standards revision decisions](standards-revision-decisions.md) already
dispose of DSR-S01 through DSR-S08 and DSR-D01 through DSR-D07 for the
coordinated 0.10.0 design. Reimporting the old report would duplicate or
reverse those decisions. The current overview requires each Client hop to
capture and authorize its own request; no transitive delegation is granted.
The current HTTP integration guidance covers content-coding behavior, and
the registry proof correction fixes X25519 key role and PoP handling.

The prior review's unresolved questions are no longer all open. Policy
semantic safety, authenticated argument provenance and volumetric
availability guarantees remain outside the current conformance claim.
They need separate, versioned design and evidence before any stronger
security claim. The historical INS-11 verdict remains incomplete; this
document supplies no runtime result or independent external audit.

## Next gate

If further review changes accepted bytes, trust semantics or security
claims, update the charter, normative chapters, profiles, compatibility
account and traceability together in a new pinned snapshot. Then produce
clause-based Go and Rust gap maps, implement core changes with appropriate
unit and safe runtime tests, rerun Inspector against that exact snapshot,
and only then assess SDK, service, demo and repository extraction work.
The preserved branch's uncommitted files stay untouched during this gate.
