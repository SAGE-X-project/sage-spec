# Integration boundaries for SAGE implementations

Status: informative implementation guidance for the coordinated, unreleased
0.10.0 design. The normative rules remain in the specification chapters and
security profiles. These boundaries do not define new conformance levels.

## Responsibility layers

| Layer | Responsibility | Output and limit |
| --- | --- | --- |
| L0: bytes | Parse and encode the exact canonical forms, transcript inputs and digests required by the selected profile. | Reproducible bytes or a parsing error. A digest alone confers no authority. |
| L1: cryptographic validity | Verify signatures, HPKE confirmation, session records and replay-sensitive cryptographic state using explicitly supplied keys and inputs. | A cryptographic verdict with evidence of the checked bytes and key. Key-role trust and policy remain outside this layer. |
| L2: trust and admission | Resolve authoritative identity and active key roles, compare the protected capture with the proposed operation, evaluate deployment policy, and admit or deny execution under the selected profile. | An authorization tied to exact target, bytes, role, capture and state. Missing or failed required collaborators deny. |
| L3: deployment assembly | Bind the L2 decision to every actual Agent, MCP, SDK and host effect path, including returned-result consumption. | A protected execution or refusal. The assembly owns interception and key custody in its host. |

L0 and L1 may be reusable library primitives even when a deployment has not
configured L2 or L3. Such a deployment must not claim protected execution.
An assembly may choose mechanisms and adapters but cannot invent an
authorization policy or treat cryptographic validity as authorization.

## Effect boundary

A guarded tool registry is a useful integration point only when it mediates
every effect the protected Client can perform. Registration-time enumeration
does not cover direct tool calls, subprocesses, filesystem or network access,
or newly loaded components by itself. The trusted host must either intercept
those paths or exclude them from the protected profile. An LLM decision to call
a verifier is not a substitute for mandatory enforcement before dispatch and
before consuming a protected result.

HTTP Handler and RoundTripper wrappers apply to HTTP messages. They do not
implement the non-HTTP MCP connection owner, negotiation or execution
admission rules in the selected MCP profile. Each transport integration must
identify its actual effect and result-consumption boundaries. The Client at
each Agent hop captures and authorizes its own outgoing operation; an upstream
authorization does not transitively authorize a downstream call.

Distinct VerifiedMessage and AuthorizedCall types can prevent accidental
misuse if the trusted owner alone constructs them, their evidence remains
bound to the dispatch target, and the dispatch capability cannot be forged or
serialized into the mutable Plugin/MCP/Skill domain. Types, route lists and
an assembly's self-reported security level do not prove complete mediation.
Inspector verdicts and deployment evidence remain separate.

## Interfaces and SDKs

Resolver, key-store, replay-store and admission interfaces may be shared
between reusable cores and adapters. Contracts whose state or acceptance
semantics change must declare the exact specification version and profile;
an unversioned interface must not silently combine different admission
semantics. Go and Rust may use different internal packages while producing
the same externally observable verdicts.

Opaque FFI or WASM handles help a thin SDK preserve object lifetime and
failure propagation. They do not isolate signing keys from a compromised
host by themselves. SDKs must pin the core revision and selected protocol
profile, keep failures visible, and document host custody of keys, policy,
resolver state and execution control.

## Implementation order

Finish the new pinned specification and traceability snapshot before moving
Go or Rust packages. Then map clauses to each core, implement and test the
gaps, rerun Inspector against the exact snapshot, and evaluate SDK, service,
demo and repository extraction work. A package layout is an implementation
choice; the normative profile and its evidence determine compatibility.

See the [repository ownership map](repository-roles.md), the
[normative overview](../spec/00-overview.md), the
[Agent/MCP security profile](../profiles/agent-mcp-security.md), the
[non-HTTP MCP profile](../profiles/non-http-mcp-security.md), and the
[design disposition](../verification/design-branch-disposition-2026-09-25.md).
