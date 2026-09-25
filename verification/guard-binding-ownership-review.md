# Execution Guard and MCP responsibility review

Date: 2026-09-26. Status: informative review against sage-spec main
04cec35d8e0eed1cd168a4315f1ca69876271de5. This review does not
change the 0.10.0 normative profile, a test verdict, or an implementation
package boundary. The [current traceability plan](traceability.json) has
SHA-256 ec4cef166a7e1aa6993b8345b9b702fbb218b091426a4eab330dc104657028fd.

This review covers nine EXEC, eight MSET and six MOWN rule groups: 23 groups
with 147 distinct planned cases and 155 rule-to-case links. Eight MOWN-06
links reuse cases whose primary owners are MOWN-02, MOWN-03 or MOWN-04;
they are not eight additional cases. Every case in this current plan remains
planned_not_executed. The separately pinned
[Inspector execution evidence](mcp-evidence-adoption.md) must retain its
own source revisions and incomplete overall verdict.

The layers below identify a functional responsibility, not a required Go or
Rust package. A rule spanning several layers still needs clause-level
implementation mapping after the new specification snapshot.

| Rule | Candidate layers | Functional enforcement owner | Review boundary |
| --- | --- | --- | --- |
| EXEC-01 | L2, L3 | Protected Client host and receiver gate | Key, policy and effect custody must be demonstrated in the selected host. |
| EXEC-02 | L2, L3 | Protected Client capture and policy | Each hop authorizes its own exact outgoing operation; capture cannot be delegated to mutable tools. |
| EXEC-03 | L0, L2 | Client encoder and receiver verifier | Canonical intent bytes are distinct from permission to execute. |
| EXEC-04 | L2, L3 | Receiver authorization and final dispatch gate | Verification, reservation and effect commitment remain separate observations. |
| EXEC-05 | L2, L3 | Durable receiver ledger and trusted retry owner | An uncertain outcome never becomes permission to redispatch. |
| EXEC-06 | L2, L3 | Protected baseline owner and actual component loader | A hash comparison does not prove an unobserved loaded dependency or whole-host integrity. |
| EXEC-07 | L1, L2, L3 | Receiver result signer and protected Client consumer | Only an authenticated, request-bound result may enter protected consumption. |
| EXEC-08 | L2, L3 | Client gate and MCP adapter | A callable MCP verifier cannot force an untrusted host to invoke it. |
| EXEC-09 | Evidence | Specification and Inspector claim owners | Cryptographic validity is not semantic prompt safety or full-host assurance. |
| MSET-01 | L2, L3 | Trusted local connection owner | Session, peer, role and local binding identity stay pinned to one owner. |
| MSET-02 | L0, L3 | Connection owner and transport adapter | Exact bytes, size bounds and output commitment require one serialized owner. |
| MSET-03 | L2, L3 | Client and server setup owners | Negotiation does not confer tool readiness before required state transitions. |
| MSET-04 | L2, L3 | Setup owner and transport acknowledgement adapter | A local send acknowledgement is not an authenticated peer result. |
| MSET-05 | L2, L3 | Discovery owner and protected tool gate | Tool description and readiness are bound to the authenticated connection. |
| MSET-06 | L3 | Owner scheduler and bounded dependencies | Timeout, cancellation and cleanup cannot revive or bypass admission. |
| MSET-07 | L2, L3 | Connection lifecycle owner | Reconnect creates new ownership without erasing durable Guard identity. |
| MSET-08 | Evidence | Profile and Inspector scope owners | HTTP and unrelated MCP transports are outside this binding. |
| MOWN-01 | L0, L3 | Connection owner before inner routing | Complete-message bounds precede application effects. |
| MOWN-02 | L2, L3 | Exclusive owner and trusted dependency providers | Callbacks and output publication cannot mutate a stale or different owner. |
| MOWN-03 | L2, L3 | Receiver admission coordinator and durable gate | Final queue insertion and owner closure share one ordering point. |
| MOWN-04 | L3 | Owner clock and scheduler | Setup and protected deadlines have different admission consequences. |
| MOWN-05 | L1, L2 | Trusted signer and active role-key selector | A compatible active signing key cannot be replaced by a KEM key or another algorithm. |
| MOWN-06 | L2, L3 | Shared gate and owner resource pool | Shared case links cover admission, invalidation and finite providers without double counting. |

## Evidence limit that affects the next design

EXEC-01 and EXEC-06 use deployment_or_document_review for all their
planned cases. Their negative inputs include disabled enforcement, direct
effect paths and a component change after checking. A document review can
reject a proposed architecture, but it cannot establish that a particular
running host mediates its actual effects or loaded components. The
[Inspector plan](inspector-plan.md) makes the same distinction, and the
integrated INS-11 result remains INCOMPLETE. A later pinned host requires
host-specific source/configuration review and safe bounded runtime evidence;
attack-capable bypass reproduction is not required.

The current [design graph](../analysis/current-design-overlay.md) links
documents to candidate layers. This table refines the security-critical
Guard and MCP subset without turning those links into conformance results.
The Go/Rust cores can expose exact-byte and cryptographic operations, and
may offer trusted state-machine building blocks. The selected Client and
receiver hosts still own capture, key custody, final effect mediation,
result consumption and failure behavior. A model-selected tool call alone
cannot satisfy mandatory enforcement.

## Inputs needed before a normative snapshot

The implementation-pattern decision must identify the actual Client host
and its protected capture, policy, key and dispatch boundaries; every
protected effect and result-consumption path; the place where the MCP
connection owner lives; and the Go/Rust public API and SDK custody model.
For each change, classify whether it changes only code organization or
also changes accepted bytes, admission order, refusal behavior or the
claimed threat boundary. Only the latter category changes the normative
profile and planned Inspector cases.

The fixed [execution order](https://github.com/SAGE-X-project/sage-inspector/blob/58cffde89e45096b12d834fb562ea856d46b1c0b/docs/execution-order.md)
places the coordinated specification and traceability snapshot before
Go/Rust package moves and an Inspector rerun. No release or complete
conformance claim follows from this ownership review.
