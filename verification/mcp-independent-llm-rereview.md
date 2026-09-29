# ADOPT-06 independent LLM re-review of the current MCP design

Status: **SCOPED_LLM_REREVIEW_COMPLETE** for the non-HTTP MCP design at
[`5bcf511e604579afa63f434013447f44b6858828`](https://github.com/SAGE-X-project/sage-spec/tree/5bcf511e604579afa63f434013447f44b6858828).
A Codex LLM reviewer in a separate fresh context read that commit through
`git show`, without using the uncommitted design branch or editing source.
The [machine-readable record](mcp-independent-llm-rereview.json) pins the
reviewed files and the [earlier LLM result](mcp-independent-llm-review.md).
The reviewer shares the authoring agent's service and workspace, so this is
**not an organizationally independent third-party audit**. That audit remains
`NOT_PERFORMED`; implementation conformance remains `NOT_ESTABLISHED`.

| Earlier finding | Re-review disposition | Evidence and limit |
| --- | --- | --- |
| `LLM-01` — inconsistent PoP length framing | `RESOLVED_IN_NORMATIVE_TEXT` | Chapter 00 defines `len16` as two length bytes only; REG-04 appends each of the five fields once. The reviewer independently reconstructed both fixed PoP challenge strings and SHA-256 values. This does not execute a live proof or registry mutation. |
| `LLM-02` — missing X25519 registry algorithm | `RESOLVED_IN_NORMATIVE_TEXT` | REG-01/02/04 and TABLE-03 define exact lowercase `x25519`, 32-byte KEM key validation, signing-key endorsement, signature-role exclusion and deterministic eligible-key selection. The local fixture does not establish key registration, HPKE possession or a handshake. |

The reviewer also examined the seven trust boundaries in the
[ADOPT-06 request package](mcp-external-review-package.md): key roles and
handshake, authenticated carriage, MCP setup and acknowledgement, owner
output and deadline transitions, protected exchange admission and durable
state, registry and host boundaries, and excluded transports. No additional
concrete normative contradiction was confirmed **within that non-HTTP MCP
scope**. A no-finding result is limited to the examined revision and is not
proof that the design has no other defects. The MCP request package and the
original review remain historical records of their older target; this report
does not rewrite them or turn their Inspector evidence into current evidence.
The reviewer also read the JCS, Card and DID resolution chapters and
reconstructed the pinned descriptor's 1,141-byte canonical serialization and
`sha256-jcs:f40nkKDT3hQs9poaxZxm8Bgw4hUV1f036fGMmIaKPtQ` digest. This
checks that fixed descriptor's bytes, not general JCS implementation behavior
or a live DID consumer.

The [standards clause audit](standards-clause-audit.md) already records separate
open questions: `SCA-01` (unregistered private HTTP signature `alg`), `SCA-02`
(case-sensitive DID prefix versus ABNF), and `SCA-03` (secp256k1 JWK citation).
They are neither residual `LLM-01/02` defects nor new non-HTTP MCP findings.
Resolve them with the planned, coordinated specification revision, not by
silently changing this frozen review target.

PoP byte fixtures establish internal specification-byte consistency only.
Neither this review nor its checker verifies Go/Rust, Inspector against the
reviewed revision, Agent-host mediation, live Registry Source behavior,
cryptographic composition, or a deployed service. No release or protocol
conformance claim follows. The next planned work is review of the preserved
design branch and implementation pattern, followed by one coherent normative
revision and revision-bound execution evidence.
