# Protected host-port contract for Agent and MCP integration

Status: informative stage-3 integration design for the coordinated, unreleased
0.10.0 profile. It operationalizes [EXEC-01..09](../profiles/agent-mcp-security.md),
the [non-HTTP MCP profile](../profiles/non-http-mcp-security.md), and the
[integration layers](integration-boundaries.md). It changes no normative rule,
wire format, Inspector verdict, core API or program order. Proposed port names
are concepts, not existing Go/Rust exports or new conformance levels.

This design uses the [stage-2 pinned source and consumer audit](library-adoption-stage2.md):
Go `sage` at `fbd9b2169c72d62c62dcbaa2336275d08a5735a8`, Rust
`rs-sage-core` at `0a6f1e0356f323d6f0bcca5bd96ad3fdab82297f`, and
Inspector at `286f1cc707c819d0c1d589efc4a9fd7c8568273f`. Product-hook
observations below are from official documentation checked on 2026-10-04;
they require rechecking against the exact deployed client build.

## Claim boundary

The host is the mandatory owner of both effect admission and protected-result
consumption. A model-selected security tool, optional MCP call, ordinary plugin
hook or valid signature cannot establish complete mediation on its own.
The trusted host protects captured originals, approved policy and manifests,
private-key use, authoritative observations, durable journals and ledgers,
verification, dispatch and output release from the mutable model, plugin, skill
and MCP domain. An MCP server under attacker control is not its own trusted
verifier. A compromised trusted gate or keys and an already corrupted initial
Agent/DID/Card enrolment remain outside the 0.10.0 protection claim.

There are three useful *evidence descriptions*, not protocol conformance tiers:

| Evidence | Defensible statement |
| --- | --- |
| Primitive import/build | The selected parser, signer, registry or Guard function can be called. No protected host claim follows. |
| Guarded route | A named effect/result route uses the gate under stated configuration. Other routes remain unassessed. |
| Complete protected-host deployment | Route inventory, capability isolation and live failure evidence show every in-scope effect and protected result passes its gate. Only this supports a deployment-specific Execution Guard claim, subject to the normative profile and Inspector verdicts. |

## Ports and ownership

These ports describe the trusted-host obligations around reusable core logic;
they do not require identical Go and Rust source layout. The host constructs a
version/profile-bound assembly with all required collaborators. Missing ports,
unavailable backing state or an unproved effect route fail construction or
admission; they never select a legacy or weaker profile.

| Port | Trusted input and output | Failure behavior |
| --- | --- | --- |
| `CaptureStore` | At the disclosed typed-prompt, API-submission or trusted-workflow boundary, retain the ordered, exact submitted UTF-8 bytes before untrusted expansion, an unpredictable request ID and the EXEC-02 commitment. A downstream Agent creates a fresh local capture from its authenticated inbound input. | No protected derived call if exact original bytes or protected persistence are unavailable. A hook's reconstructed prompt string is not automatically the exact captured byte sequence. |
| `PolicyAuthorizer` | Evaluate the pinned, approved policy/epoch against that capture and the fully resolved recipient, tool, arguments and approved component baseline. Produce a one-use decision bound to those values. Human confirmation, when any, is a policy choice. | Deny missing, stale, self-asserted or ambiguous authority; an LLM's choice or earlier hop's approval does not substitute. |
| `IdentityAndReadiness` | Obtain authoritative, fresh registry observations and active role-bound signing keys; enforce configured source, finality, clock, revocation and recipient identity at the applicable boundaries. | Deny absent, conflicting, stale or unready observations; never switch key role, algorithm or registry source to keep a call running. |
| `MeasuredComponent` | Bind approved policy and executable manifest to the *same immutable loaded instance* and its loadable dependencies, including plugin, skill and MCP code when used. | Deny changed, missing, reloaded or uncovered executable inputs before signing/admission. A stored hash alone is insufficient if execution can reopen different bytes. |
| `IntentSigner` | Accept only an internal, authorized exact intent and use the selected role-bound key to sign the EXEC-03 canonical bytes. The resulting envelope and call identity enter a protected Client journal. | No arbitrary-sign operation exposed to model/MCP/plugin code; no substitute signer, unsigned retry or altered-intent retry. |
| `TransportOwner` | Bind issuer, recipient and exact signed intent to the selected HTTP or non-HTTP MCP carriage, including outer replay/session identity and setup readiness. Retain original envelope for identity-preserving retrieval. | Treat uncertain send as uncertain; do not mint a new call ID or downgrade transport. Close/setup races follow the selected MCP profile. |
| `AdmissionLedger` | On the receiver, bound and authenticate the exact envelope, check current policy and baseline, atomically reserve identity/freshness, and keep durable dispatch/result state. | Reject before any protected effect on pre-dispatch failure; duplicate and unknown states follow EXEC-04/05 rather than redispatch. |
| `EffectOwner` | Recheck authority, expiry and the measured instance at the final fence, then consume a one-use admission and dispatch the exact verified arguments to the pinned component. Own every nested, direct, retry, concurrent, subprocess, file and network route in scope. | No untrusted code holds bypass credentials or equivalent capabilities. If a route cannot be mediated or isolated, the host cannot claim that scope. |
| `ResultConsumer` | Verify the signed result, issuer/recipient, call binding, status and freshness before returning it to the user, model or downstream Agent; durably consume the first terminal outcome once. | Do not expose unverified results as authoritative output; pending is not success, and uncertain outcomes require reconciliation. |

`AuthorizedCall` and `VerifiedResult` can be opaque, owner-bound handles to make
illegal call order harder, but their type names are only design candidates.
They cannot be serialized into the untrusted domain as bearer permission.
Private keys may reside behind a trusted signing service; that service then
shares the principal's trust boundary and must enforce authorization context.
An FFI/WASM handle alone does not isolate the key or complete the host gate.

## Protected operation sequence

| Step | Decision and durable state | Gate that must still hold |
| --- | --- | --- |
| 1. Capture | Preserve the ordered submitted bytes and request ID before the model or mutable expansion. | Later rewritten text cannot replace the original commitment. |
| 2. Propose | The model, plugin or tool proposes a call; all proposed fields are untrusted. | Proposal has no execution or signing capability. |
| 3. Authorize | The trusted policy evaluates the exact resolved target, tool, arguments, policy epoch and loaded-component baseline under local authority. | New Agent hops authorize independently; optional human approval is never the only verifier. |
| 4. Sign and send | Sign only that authorized intent, journal its exact envelope, then bind it into the selected authenticated transport. | A changed argument, recipient, key role or manifest needs a new decision; a transport retry reuses the original signed intent. |
| 5. Receive and reserve | Peer bounds and authenticates, resolves current role-bound identity, applies its own approved mapping, then durably reserves call/freshness identities. | Failure before final dispatch yields zero protected effects. A duplicate is a snapshot path. |
| 6. Final dispatch | Peer rechecks authority, time and the measured loaded instance, fences execution and passes exact arguments to the one permitted effect owner. | No direct subprocess, network, filesystem, worker or other route bypasses admission. |
| 7. Return and consume | Peer records/signs a result snapshot; Client verifies it and releases the first terminal result once. | Pending is not terminal; unknown/lost result does not authorize another execution. |

Timeout, cancellation, process restart and transport loss do not themselves
prove non-execution. While a call is pending, the Client can retrieve a later
snapshot with the same signed intent and fresh outer transport identity, within
EXEC-05's bounds. `UNKNOWN`, lost ledger or expired retrieval require the
profile's protected reconciliation and must not trigger automatic new-call
dispatch. Policy retirement, key revocation, changed manifests and connection
close are rechecked at their normative boundaries; an already committed
external effect cannot be rolled back by a later denial.

The receiver's final gate and signed-result path are required even if the
sender's plugin performed every available hook check. A route inventory must
include result delivery to the model, SDK callbacks, streaming, tool outputs,
subagents and error handling as well as outbound effects. Post-execution hooks
can withhold a result, but cannot undo an effect that already ran.

## Product adapter capability at the documentation snapshot

This matrix describes *documented interception*, not a claim that an
unmodified third-party Agent client satisfies EXEC-01. Hooks may help collect
evidence or deny supported calls. Exact pre-expansion capture, fail-closed
execution, key isolation and all effect/result routes still need a host-owned
integration or an independently enforced gateway and capability boundary.

| Client | Documented pre-model and pre-tool points | Material limits for a protected claim | Integration decision |
| --- | --- | --- | --- |
| Claude Code | `UserPromptSubmit` runs before model processing and can block; `PreToolUse` runs before agentic tool calls and can block built-in and MCP tools. Its Agent SDK callback hooks can block on the cited prompt/tool timeouts. [Official hooks reference](https://code.claude.com/docs/en/hooks) | Command, HTTP and MCP-tool hook timeout/error paths can continue; matchers and hook installation are conditional. A hook-supplied prompt string does not by itself prove the exact pre-expansion byte capture, and `PreToolUse` does not cover effects outside its tool path. A post-tool hook is too late to stop the effect. | Treat plugin/ordinary hooks as useful adapter points only. Claim the full profile only if a trusted host or independently enforced effect/result boundary proves all routes, exact capture, protected state and fail-closed behavior for the deployed build. |
| Codex | `UserPromptSubmit` exposes a prompt before model submission; `PreToolUse` can deny shell, `apply_patch`, MCP and most local function tools. Managed configuration can pin hooks on supported deployments. [Official hooks reference](https://learn.chatgpt.com/docs/hooks) | Hosted tools do not traverse the local function-tool hook path, specialized paths may opt out, and hook errors, timeouts or malformed output can continue the action. Plugin hooks are skipped until trusted; managed cloud and local modes differ. The documentation itself calls tool hooks a guardrail, not a complete enforcement boundary. | Use hooks for supported routes and diagnostics, then require a host-owned execution/output gate or independent gateway that prevents all bypass paths. A plugin-only installation cannot assert complete 0.10.0 protection from these hooks alone. |
| Agent/MCP host we control | We can insert capture, authorization, signing, admission, dispatch and result release into the actual host control flow. | Completeness still depends on enumerated effect routes, isolation, durable state, tested failure modes and exact source/runtime revisions. | Prefer a mandatory host assembly around every effect and output route; expose MCP security tools only as interfaces to that assembly, never as optional enforcement. |

The named hooks above are product adapter facts, not portable protocol event
names. Their API semantics and availability may change. Neither a user approval
prompt nor a model instruction to invoke `sage_secure_call` is mandatory
mediation. The deployment must check the actual version, hook configuration,
failure behavior and execution routes before assigning a protected-host claim.

## Evidence needed before implementation conformance

For each host/build/profile combination, record:

1. An exhaustive map from prompt/API inputs through every model and tool path to
   effects and result consumers, including direct APIs, shell, filesystem,
   network, background work, retries, parallel work, subagents and transport
   callbacks. State which paths are blocked or excluded by enforceable
   capability isolation, not merely absent from a sample trace.
2. The exact capture boundary and byte framing, key custody, approved policy
   epoch, authoritative registry source, manifest of code/configuration and
   dependencies, and proof that the measured bytes are the running instance.
3. Durable, version/profile-bound Client journal and receiver ledgers, with
   restart, concurrent reservation, close and unknown-outcome handling.
4. Safe unit and runtime checks for changed proposed arguments, denied or
   missing collaborator, disabled or timed-out hook, changed loaded component,
   direct route, duplicate intent, interrupted dispatch and unverified result.
   These checks assert denial and state transitions without publishing an
   attack-capable reproduction program.
5. Exact binary, host configuration, source revision and Inspector revision
   used for each outcome. Unexercised, unsupported or deployment-dependent
   cases stay `NOT_RUN`, `UNSUPPORTED` or `PARTIAL` as appropriate, never `PASS`.

## Stage-4 handoff

Before changing a normative clause, classify each port obligation against
existing EXEC, MSET/MOWN, wire, identity and registry text. Most of the sequence
above already follows EXEC-01..09 and is explanatory, not an invitation to
duplicate it. Stage 4 should review any genuine gap for RFC/MCP compatibility,
version and migration effect, then define independent Inspector cases before
core or adapter changes. The main candidate case families are exact host
capture versus hook text, incomplete hook coverage, hook failure/disablement,
capability bypass, same-instance manifest binding, final admission under
revocation or closure, and verified result release. Product hook names stay in
informative adapters unless a portable, enforceable common contract exists.
