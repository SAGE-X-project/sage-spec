# Current 0.10.0 design graph overlay

Status: informative responsibility mapping, generated from the coordinated
0.10.0 traceability plan. It does not change the specification or establish
implementation conformance. The machine-readable graph is
[current-design-overlay.json](current-design-overlay.json); regenerate it with
[the builder](build-current-design-overlay.py) and verify it with its
--check option.

## Why this is a separate graph

The [original evidence graph](graphs.md) preserves an X-bar classification
of 161 historical documents and a pinned Go AST extraction. Its normative
overlay describes 45 requirements, 77 rule groups and 386 planned cases at
that earlier snapshot. Rewriting those nodes in place would make the original
AST and document evidence appear current. The present
[traceability plan](../verification/traceability.json) has 45 requirements,
91 rule groups and 481 distinct planned cases. The new graph records that
current authored trace while referring to the earlier AST graph by hash.
No source code was reparsed for this update.

| Evidence | Pinned SHA-256 | Scope |
| --- | --- | --- |
| Current traceability | a83a28338a9e3f15cd7846ce251db2f915d9ffffaf7162bc749b7f38d784aae7 | 45 requirements, 91 rule groups, 481 planned cases |
| Historical AST/document graph | 9ebc83fd13d9abd96f1080e5c95ab8e35f148d94ec81a88e64b8f137d6026f3c | 58 selected Go packages, 1,777 raw symbols, older normative overlay |

The generated overlay has 637 nodes and 887 edges. A requirement links to
its rule groups; a rule links to its source document and planned cases.
Eight cases have an additional MOWN-06 rule reference besides their primary
owner, so 489 rule-to-case edges still describe only 481 distinct cases.
The graph does not convert any planned case into a PASS.

## Layer reading

The 36 document-to-layer edges are **candidate implementation
responsibilities**. A document may address several layers; these edges do
not assign every rule in that document to every listed layer. The later
clause-based Go/Rust gap map must refine them.

| Layer | Meaning | Typical source material |
| --- | --- | --- |
| L0 | Exact parsing, serialization and canonical bytes | JCS, HTTP signature base construction, HPKE transcript bytes, transport framing |
| L1 | Cryptographic validity under supplied inputs | Signatures, HPKE confirmation, authenticated session records, proof checks |
| L2 | Authoritative identity, active key roles, policy and admission | DID/Card/registry resolution, protected capture and Agent/MCP authorization |
| L3 | Host assembly and effect mediation | Mandatory Client hook or equivalent control, MCP connection owner, dispatch and result-consumption barriers |

PROCESS.md and charter.md have traceable rule groups but no runtime layer
edge: they govern process and evidence claims. The protected Client owns
capture and final dispatch, while reusable Go and Rust cores may implement
L0/L1 and selected L2 primitives. A callable MCP signer or verifier cannot
force a host to call it. SDK wrappers must preserve the pinned core's
failure and version semantics. Inspector records independent verdicts; it
is not a production authorization point.

The [integration boundary review](../architecture/integration-boundaries.md)
and [repository roles](../architecture/repository-roles.md) explain these
responsibilities. The [design branch disposition](../verification/design-branch-disposition-2026-09-25.md)
records which proposals were adopted as guidance and which require a later
versioned decision. Neither types nor a tool registry prove full mediation
when a host has direct effect paths outside the protected boundary.

## Next design gate

This graph makes the current document-to-layer relationship inspectable
without changing accepted messages. Before a new specification snapshot,
review any proposed Client/SDK/MCP implementation pattern against the actual
host effect boundary and the selected non-HTTP owner. For each proposed
normative change, record exact accepted bytes, refusal behavior, trust
assumptions, migration impact and planned Inspector cases. Then pin the
changed chapters and traceability together. Only afterward map current Go
and Rust code to clauses and refresh AST evidence at pinned core revisions.
