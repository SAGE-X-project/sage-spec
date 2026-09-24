# ADOPT-06 independent LLM review result

Status: **REVIEWED_WITH_OPEN_FINDINGS**. Two Codex LLM reviewers examined the
[fixed review target](https://github.com/SAGE-X-project/sage-spec/tree/d86ca1a4d326d6090e50d100b834d38ec204a2c2)
in separate fresh contexts, without editing it or receiving prior review
conclusions. The [machine-readable record](mcp-independent-llm-review.json)
identifies their methods, scope, findings, and limits. They share the authoring
agent's service and workspace, so this is a separate-context LLM review, **not
an organizationally independent third-party audit**. The user selected an LLM
for this review. The external audit remains `NOT_PERFORMED`, implementation
conformance remains `NOT_ESTABLISHED`, and no release claim follows.
The record adds hashes for chapters 00 and 11, which the original package did
not list but which the reported findings necessarily examine.

The MCP reviewer hash-checked the nine profile and normative paths listed in
the record against the [review package](mcp-external-review-package.json), read
the relevant clauses and official MCP `2025-06-18` lifecycle, transport, and
tools documents, and reported no additional concrete normative finding within
that scope. The reviewer did not complete an RFC 9180 or RFC 8032 audit or any
runtime, Agent-host, or live-registry test. A no-finding result for that scope
does not establish global completeness.

The cryptography and trust-boundary reviewer independently checked the pinned
descriptor's 1,141-byte canonical encoding and SHA-256 digest and reported two
normative findings. Both were reproduced against the pinned source text:

| ID | Severity | Trigger and conflicting clauses | Consequence | Disposition |
| --- | --- | --- | --- | --- |
| LLM-01 | Medium | For a nonempty REG-04 PoP field, [the global `len16(s)` definition](../spec/00-overview.md) includes the field, while [REG-04](../spec/09-registry.md) appends the field after `len16` and explicitly defines `len16` as length only. | A registrar, signer, and resolver can calculate different signed challenge bytes. | `OPEN_NORMATIVE`: define the length operation once and add exact challenge-byte vectors. |
| LLM-02 | High | [REG-01 and REG-02](../spec/09-registry.md) require a chapter-11 `alg` value yet select an X25519 KEM key; [chapter 11](../spec/11-registries.md) registers signing algorithm names and X25519 as a key type, with no KEM `alg` literal. | A strict parser can reject the key required for the responder handshake. | `OPEN_NORMATIVE`: define its exact registry literal and validation rule, keep signature roles separate, and add registration and handshake vectors. |

The first is an exact-byte contradiction; the second blocks unambiguous KEM-key
registration. These are specification findings, not demonstrated exploits or
runtime failures. The previous adoption and evidence snapshots remain
historical. A separately pinned normative correction and repeat review must
precede claims about this target's complete design. Go/Rust and Inspector runs
must be tied to that later revision; the existing 71-parent Inspector overlay
does not test these corrections. Agent-host enforcement and live Registry Source
behavior remain untested.
