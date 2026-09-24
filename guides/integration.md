# Agent, SDK and MCP integration guide

This is implementation guidance for the normative [Execution Guard profile](../profiles/agent-mcp-security.md),
not an implementation or a promise that existing clients already conform. Where
this guide and the profile differ, the profile governs. Version: 0.10.0.

## 1. Developer integration points

| Boundary | Responsibility | Failure action |
|---|---|---|
| Original input capture | Trusted Client stores original bytes before plugin expansion; later derived calls reference its commitment | Stop if capture is unavailable or overwritten |
| Context/tool loading | Verify approved descriptions, skills, schemas and executable baseline; distinguish external data from policy | Reject changed/uncovered material |
| Model proposal | Treat generated tool/arguments as a proposal requiring trusted Client policy evaluation | No general-purpose signing oracle |
| Final dispatch | Authorise/sign exact call; trusted receiver verifies identity, policy, manifest, time and durable replay state | No effects without success |
| Result consumption | Match signed result to pending intent, verify source/time and representation | Do not inject unverified output into model/context |
| Retry/subagent/restart | Apply the same gates with durable identities and causal binding | Do not bypass a failed call through another path |

The protected original and final intent are different objects. For "weather in Seoul",
the Client can approve an exact `get_weather` call with an explicit city under local
policy, without forcing a user popup. If an intermediary changes the city after
approval, verification rejects it. If the Client itself approves the wrong city,
cryptography cannot infer the user's intended city; this is a policy/model-quality
failure, not a false guarantee of semantic integrity.

## 2. SDK versus MCP deployment

A library binding can keep capture, authorisation and signing inside the trusted
Client, with a narrow dispatch capability. A protected MCP service may perform those
operations for an authenticated Client, but the ordinary model/plugin interface must
not grant arbitrary signing. Verification exposed as a model-visible tool is useful
for diagnostics and education, not for compulsory enforcement.

The proposed `sage_secure_call` binding and exact envelope are in the profile.
A remote executor validates before invoking the inner tool. A local implementation
needs isolation too: a compromised tool with the same keys or unrestricted file/network
access can avoid the protocol entirely. Running an MCP executable locally does not by
itself establish the required boundary.

Go `sage` and Rust `rs-sage-core` will provide library builds in follow-up work.
Language SDKs should wrap versioned core contracts rather than reimplement crypto.
ABI ownership, handle lifetimes, error types, thread safety and key ownership belong
to the [repository design](../architecture/repository-roles.md), not to the wire grammar.

### HTTP content at the protected byte boundary

An HTTP Client using the chapter 03 profile should request
`Accept-Encoding: identity`, disable automatic request compression and response
decompression, and retain the exact received HTTP content octets after transfer
framing removal until signature and `Content-Digest` checks complete. It must
verify those octets, not
the body supplied by a library after a hidden transform. `Accept-Encoding` is
only a preference: chapter 03 independently requires every SAGE sender to omit
`Content-Encoding` and every receiver to reject it, even when a response could
be decoded. Do not send `Content-Encoding: identity`; the field is omitted.
Configure proxies and HTTP libraries so they cannot transform covered fields or
content behind the verification boundary. A generic `RoundTripper`/`Handler`
wrapper applies only to this HTTP profile; it does not implement the selected
non-HTTP MCP binding.

### Shared implementation boundaries

Separate pure canonicalization and digest calculation (L0), cryptographic
verification and authenticated sessions (L1), trusted identity/policy/execution
admission (L2), and deployment-specific Client/MCP/SDK/effect integration (L3).
These are implementation responsibilities, not additional conformance levels or
prescribed package names. Keep version-specific wire and stateful admission
contracts explicit at every boundary. A verified message is not an authorized
call; an authorized call must be bound to the exact bytes, owner, policy and
effect path that were checked. Missing collaborators fail construction rather
than defaulting to a permissive path. Opaque handles and typed verdicts reduce
accidental misuse but do not prove key isolation or complete host mediation.

## 3. Hook capabilities are not uniform

Official documentation inspected 2026-09-13; this is a capability review, not a
runtime compatibility certification. Pin and test exact client versions before
claiming an adapter conforms.

| Host | Documented mechanism | Gap to assess |
|---|---|---|
| Claude Code | `UserPromptSubmit`, blocking `PreToolUse`, command/HTTP/MCP hooks | Missing server, malformed output and some timeout paths continue execution; managed policy and native enforcement may be needed |
| Gemini CLI | `BeforeModel`, `BeforeToolSelection`, `BeforeTool` | Some non-blocking failures warn and continue; verify each gate/error route |
| VS Code agent | `UserPromptSubmit`, blocking `PreToolUse` | Preview feature with disableable configuration and host-specific schemas |

Sources: [Claude hooks](https://code.claude.com/docs/en/hooks),
[Gemini hooks](https://geminicli.com/docs/hooks/reference/),
[VS Code hooks](https://code.visualstudio.com/docs/agent-customization/hooks).
No claim is made about every Agent Client or untested versions.

A before-model hook can validate incoming context, but it cannot authenticate the
not-yet-generated final call. A pre-execution gate is also required. A post-tool hook
cannot undo effects that already occurred. A verification service timeout mapped to
"no decision" fails the profile even if normal negative verdicts work. Wrapping a
script to convert errors to denial is insufficient if the host never starts the
script or ignores its timeout: the final dispatcher must itself require success.

## 4. Setup and lifecycle

1. Establish the protected Client/receiver, keys, policy and baseline through a trusted
   provisioning process. The protocol does not solve an already poisoned registration.
2. Record supported exact protocol/profile versions and trusted issuer policies;
   DID registration alone is not a tool permission grant.
3. Pin the complete tool artifact, schema and configuration, including dynamic dependencies.
4. Demonstrate no unsigned route to the same capability. Include shell/network exits,
   nested calls, subagents, retries and parallel branches in this inventory.
5. Test disconnect, no output, malformed verdict, verifier termination and timeout.
   All must stop before effects, without needing a popup or an LLM response.
6. On approved updates, replace the baseline under protected administration and
   invalidate pending calls to the old instance. Never learn a changed hash automatically.
7. Recover durable execution state before resuming. Report UNKNOWN crash outcomes;
   a new request ID is not a cure for a possible already-committed operation.

## 5. Registration and developer services

A later registration/lookup MCP service may help create/read Agent and Card records.
Its convenience API does not waive controller authorisation, canonical DID namespaces,
proof requirements, current resolution or revocation rules. It must not turn private
keys into ordinary model-visible tool outputs. Registration, discovery, protected
execution and conformance inspection are separate responsibilities even when one UI
makes them accessible together.

## 6. Comparative demo plan

Future examples should use the same synthetic operation, policy and attacker action
with and without SAGE. Show original input, approved call digest, changed bytes or
manifest, gate verdict, dispatch counter and side-effect evidence. Include a negative
control where the Client willingly approves an unsafe but valid request: neither
signature verification nor a file hash promises to detect that semantic error.

Compare latency and failure modes only from measured runs. Do not attribute sandbox
protection to SAGE when the baseline lacked the same sandbox. No demo or benchmark is
implemented in this delivery; [inspector plan](../verification/inspector-plan.md)
identifies the required future evidence.

## 7. Pending results and policy revisions

A verified pending result closes only its MCP/HTTP invocation. It contains no tool
output and leaves the operation unresolved. Retrieve its later state using the exact
stored intent/proof with a fresh outer request identity, at least one second apart
and only before intent expiry. Never generate a new call ID to turn a retrieval
into another execution. Stop at a terminal result; late pending results cannot
reopen it. If the retrieval window closes, use protected reconciliation rather than
inferring failure or redispatch. See EXEC-05/07 for immutable terminal results.

Provision the EXEC-02 policy descriptor and its commitment through trusted
administration. A changed policy, evaluator or recovery epoch requires a fresh
commitment and synchronized receiver mappings. Updating a hash in a model prompt
is not policy installation. The issuer evaluates its pinned policy; the receiver
checks the approved issuer/commitment/operation mapping and its own access policy.

Resubmitting the original is not a read-only query if no ledger entry exists:
with an intact ledger it can perform the original authorized execution once.
When strict read-only reconciliation is required, use protected administration.
A receiver with lost ledger state cannot treat that state as an empty ledger.

## Authenticated non-HTTP MCP integration

For explicitly selected MCP 2025-06-18 non-HTTP deployments, implement the
[adopted owner profile](../profiles/non-http-mcp-security.md). Version checks alone
are insufficient. Pin the trusted local binding identifier, complete descriptor
JCS digest and expected peer tuple before MCP setup; a discovered descriptor
cannot replace that configuration. The owner admits one active protected
request/response exchange at a time. A local second submission is refused
without reservation, while an authenticated overlapping server request follows
the profile's consumed-history and close rule. A `pending` response ends that
transport exchange but not the original durable Guard call. Preserve the
distinction between durable fencing, queue admission, worker claim and actual
effects, and follow EXEC-06 queued-work invalidation. Go/Rust owner changes and
revision-pinned Inspector checks remain follow-up work.
