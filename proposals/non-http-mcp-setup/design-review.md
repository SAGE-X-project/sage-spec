# MCP setup and owner design review

Verdict: **CHANGES_REQUIRED_BEFORE_ADOPTION**. Three open design findings below need
explicit resolution before core implementations use this as their common contract.
They are textual ambiguities and compatibility decisions, not demonstrated deployed
vulnerabilities. No authentication bypass or exploit was established by this review.

Method: a separate reasoning pass by the same authoring agent, requested by the user.
This is not an external independent audit. The [review record](design-review.json)
pins the source revision, reviewed files and original review archive hash. The archive
contains the unpublished local baseline; its identity remains distinct from an adopted
normative release. Findings refer to that frozen input, not future edited documents.

## Open findings

### DREV-01: Define the close-versus-Guard-admission boundary

Priority P2; design severity MEDIUM. [Owner contract](owner-contract.md), lines 127–133,
protects closure before handoff and refuses rollback after crossing the execution
boundary, but delegates the handoff linearization point to implementations. The
included local EXEC-04 separates durable reservation from final authorization and
dispatch (profile lines 161–177). Those are observably different moments.

Consider a trusted implementation that has handed an invocation to Guard and created
a reservation but has not yet authorized final dispatch when the owner closes. The
text does not state whether owner closure invalidates this in-flight reservation or
whether handoff has already made it irrevocably admitted. Either implementation can
point to part of the current prose. The existing pre-handoff and post-effect cases do
not settle this intermediate state. The owner contract acknowledges that ordering
must be documented; it does not yet supply a shared answer.

Required correction: define a common logical admission event, its order relative to
reservation, the final authority check and owner invalidation, and the durable outcome
of a close that wins that order. Implementations may choose their synchronization
mechanism, but not different observable semantics. One possible resolution is to
require live-owner validation at the final serialized dispatch admission; any choice
must preserve the existing rule that committed effects cannot be rolled back.

Required unit evidence: close after handoff/before reservation, after reservation/
before final admission, and after admission/before effect completion. Assert exact
effect count and retained ledger outcome, not merely connection closure. Follow with
bounded inert-effect runtime tests once the API exists. These checks were NOT_RUN.

### DREV-02: Scope the setup deadline in output completion

Priority P2; design severity MEDIUM. Owner contract lines 85–88 says a completion at
or after the setup deadline closes the connection. Lines 101–105 says READY retires
the setup timer. The output section does not explicitly limit that deadline predicate
to setup operations, despite the owner also handling protected calls and responses.
The [addendum](addendum.md) expressly applies carriage to traffic after READY.

An implementation reusing the output-completion routine for a protected response at
31 seconds could close a healthy, already-ready session; one treating the section as
setup-only would continue. The finite model cannot resolve this: its READY state has
no protected send/completion transition. Its successful post-deadline admission check
therefore does not test the ambiguous output path.

Required correction: give setup and protected operations explicit deadline classes.
Only a still-incomplete setup uses the original setup deadline. READY traffic retains
normal session, request and Guard limits with independently bounded I/O. A late setup
callback remains invalid; retiring its timer cannot revive it.

Required unit evidence: complete setup before 30 seconds, then complete a valid
protected request and response after 30 seconds; independently expire the session and
request limits and require failure. Cover a stale setup completion after READY. Real
protected exchange and timer tests remain NOT_RUN.

### DREV-03: Declare the Ed25519-only intent restriction explicitly

Priority P2; design severity MEDIUM. The fixed [tool descriptor](tool.json), at
`inputSchema.properties.envelope.properties.intent.properties.alg`, requires exactly
`ed25519`. Local EXEC-03 instead references chapter 01's algorithms, which include
Ed25519, secp256k1 and P-256. The proposal pins the entire descriptor, so rejecting a
non-Ed25519 intent is deterministic; the issue is an undocumented compatibility
restriction, not a schema-validation ambiguity or broken cryptography.

The reconciliation lists version, capability and size restrictions but omits this
algorithm restriction. An integrator can construct a valid general-profile P-256
intent that this binding necessarily rejects. The contract also leaves it unclear
whether the intended restriction applies only to intent proofs or additionally to
result/transport signatures; the input schema alone cannot constrain those signatures.

Required correction: explicitly choose either a narrower Ed25519 intent profile with
separate result/transport algorithm rules, or a revised descriptor covering supported
baseline algorithms. Record the compatibility decision and update the descriptor hash
and affected review records only if bytes change. Do not silently broaden algorithms
without corresponding verifier support.

Required evidence: table-driven positive/negative cases for each chosen intent,
result and outer-signature algorithm, including an active but unsupported key. This
review inspected schema and normative text; it did not execute cryptographic cases.

## Observations, not additional blocking findings

- The one deferred frame, irreversible replay acceptance and fixed acknowledgement
  are coherent within the stated trusted-host assumptions. No proof for arbitrary
  scheduler behavior, coupled peers or complete cryptographic lifecycle follows.
- Oversized results after an effect now have an explicit non-rollback outcome. This
  is safe failure accounting but an operational availability limitation: reconnect
  alone cannot retrieve a result that still exceeds the same cap.
- The narrower binding omits general MCP behavior. MCP's optional ping utility has
  a required response when used, and its lifecycle allows pings during initialization.
  A generic SDK with automatic ping may therefore not interoperate with the proposed
  strict state sequence. Since generic interoperability is already excluded, this is
  a deployment compatibility note rather than a new security finding. Make SDK settings
  explicit before interoperability testing. Sources: [MCP ping](https://modelcontextprotocol.io/specification/2025-06-18/basic/utilities/ping)
  and [MCP lifecycle](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle),
  consulted 2026-09-21. Optional functionality does not mean all peers must send pings.

## Verification and limits

Re-executed the frozen package: all 15 document/CLI tests passed; source hashes and
requirement references matched; the finite model reproduced 812 states and 19,488
transitions. These passing checks neither settle the three findings nor execute their
required tests. No actual setup adapter, protected effect or attack code was executed.

All 58 protocol cases and 37 historical lifecycle cases remain NOT_RUN. Adoption is
PROPOSAL_NOT_ADOPTED and conformance NOT_ESTABLISHED. The findings remain OPEN; this
review does not modify the design to mark its own findings resolved. Next work is to
resolve the three decisions in text and add the missing scenario plans, then rerun
review against the revised input. External independent scrutiny remains outstanding.
