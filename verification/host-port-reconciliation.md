# Protected host-port reconciliation for 0.10.0

Status: informative clause-to-inspection decision for the [ordered program](../architecture/program-sequence.md).
This review reconciles the [protected host-port contract](../architecture/host-port-contract.md)
with the reviewed 0.10.0 design baseline. It does not change accepted protocol
bytes, admission order, refusal behavior, threat scope, version, or normative
case identifiers. It does not claim implementation conformance.

The authoritative normative source remains commit
`1820ab5eafb843e1c13f4c46c34aeeb28d934ac9`, bound by the
[first-stage baseline](first-stage-baseline.json). Its Agent/MCP profile has
SHA-256 `0538acbdcfc143d93fb7d99a2a2c09c068fc354388c4e37c7489204305b1913f`;
the [traceability plan](traceability.json) has SHA-256
`410b1ffb7e6da0462d8c3b3ecae4ba6ed2a9c1f0bc14583fe4d17fa4d7ef5ba7`.
The Inspector must retain its older revision-bound observations rather than
transferring their verdicts to a host or a new source snapshot.

## Clause and inspection decision

| Host port | Existing normative owner | Existing case anchors | Required host observation and decision |
| --- | --- | --- | --- |
| Exact capture | EXEC-02 | `EXEC-02-P`, `EXEC-02-N01` | Compare the submitted ordered UTF-8 bytes and protected commitment with what the host actually captured before mutable expansion. A prompt string reported by a hook is insufficient without this boundary evidence. No new normative clause. |
| Independent authorization | EXEC-02; EXEC-08 | `EXEC-02-N02`, `EXEC-08-N01` | Show an approved local policy decision on the exact target and arguments; model choice or a skipped diagnostic MCP call cannot confer authority. No new normative clause. |
| Identity and signing role | EXEC-03/04; MOWN-05; chapter 10 | `EXEC-03-P`, `mres-missing-signing-key` | Resolve current issuer/recipient and the active signing key for its precise role. Missing Ed25519 for the non-HTTP binding denies; X25519 KEM does not substitute. No new algorithm or registry value. |
| Measured component | EXEC-06 | `EXEC-06-N03`, `EXEC-06-N04` | Compare the approved dependency closure with the same immutable loaded instance; path hashing followed by reopening or uncovered code fails. No new manifest encoding. |
| Protected signing | EXEC-02/03/08 | `EXEC-02-N02`, `EXEC-08-N02` | Observe that only a trusted exact decision reaches the signer and no model/plugin route signs arbitrary bytes. No new proof format. |
| Transport handoff | EXEC-03/05/08; MSET-01..08 | `EXEC-05-N04`, `mset-04-lost-ack` | Pin exact envelope, peer, transport identity, setup readiness and uncertain-send state. Retry keeps the signed intent identity. No new carriage or MCP lifecycle rule. |
| Durable admission | EXEC-04/05; MOWN-03/04/06 | `EXEC-04-N04`, `mres-close-before-reservation` | Observe exclusive reservation, final recheck, closure ordering and zero effects before dispatch. No new state transition. |
| Effect ownership | EXEC-01/04/08 | `EXEC-01-N03`, `EXEC-01-N04`, `EXEC-08-N03` | Inventory all direct and nested effect routes and independent effect counters; disabled or timed-out hooks cannot silently preserve a protected claim. No universal hook name is specified. |
| Result consumption | EXEC-07/08 | `EXEC-07-N02`, `EXEC-07-N05`, `EXEC-08-N01` | Match an authenticated result to the tracked call before user/model/downstream release, and consume the first terminal outcome once. No new result field. |

The 489 parent cases, 26 original children and 17 Registry operator
conditions remain the reviewed baseline. The anchors above are existing case
IDs, not extra requirements or a declaration that their broad parent cases
have passed. Inspector may add more precise *inspection controls* linked to
these IDs. A control that sees only a fixture or subject-reported fact remains
partial; a host-dependent case without a selected host and independent
observer remains `NOT_RUN` or `UNSUPPORTED` as its contract dictates.

## Product and standards disposition

Claude Code and Codex hooks are adapter capabilities, not protocol events.
Their documented coverage and failure behavior are recorded in the
[host-port contract](../architecture/host-port-contract.md). Because documented
hook calls may be absent or fail without blocking, a plugin-only installation
cannot supply complete EXEC-01/08 evidence. A different client may use a
different interception mechanism if it meets the same host-owned boundary.
The Inspector's route inventory must include effects and result consumers
outside the chosen hook path; a sample tool-call trace cannot prove coverage.

This reconciliation adds no HTTP signature component, `Content-Digest` field,
HPKE operation, DID/registry value or MCP wire message. The applicability and
independent restrictions already recorded for RFC 9421, RFC 9530, RFC 9180,
the DID sources and MCP 2025-06-18 in the
[standards application matrix](standards-application-matrix.md) therefore stay
unchanged. In particular, HTTP message authentication does not authorize an
EXEC tool, HPKE Base does not authorize its sender, and an MCP tool result does
not bypass EXEC-07 verification. This is a local host-inspection refinement;
it requires no 0.10.0 version or compatibility change.

## Inspector handoff and completion limit

The companion Inspector host-port inventory links the nine ports above to
existing case IDs and specifies independent observation fields for safe,
bounded host checks. It must validate the unchanged profile and traceability
hashes, reject missing or invented anchors, and report every new control as
unobserved until a versioned subject and independent observer are present.
Unit tests and a local CLI run can validate that inventory and reporting rule;
they are not execution evidence from a deployed Agent, MCP server, Claude Code
or Codex. Complete host mediation, Registry Source observation and INS-11
remain later implementation/deployment gates in the program order.
