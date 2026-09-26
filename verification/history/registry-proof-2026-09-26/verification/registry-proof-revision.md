# Registry proof and KEM role correction

Status: **NORMATIVE_CORRECTION_LLM_REREVIEWED** for the unreleased 0.10.0
design. This revision resolves the two textual defects in the
[fixed LLM review](mcp-independent-llm-review.md) without changing the old
review target or its conclusions. The reviewed chapter and plan bytes are
preserved under [history](history/llm-review-target-2026-09-25/). Earlier
adoption and Inspector reports remain pinned to their own revisions.

| Finding | Earlier ambiguity | Current rule | Verification contract |
| --- | --- | --- | --- |
| LLM-01 | Global `len16` included field bytes, while REG-04 appended them again. | Chapter 00 defines only the two-byte length; REG-04 appends each of five fields exactly once. Lengths above 65535 fail. | Two exact PoP challenge-byte fixtures, duplicate-field rejection and new REG-04 cases. |
| LLM-02 | REG-01 rejected unknown `alg`, but chapter 11 omitted a literal for the required X25519 KEM key. | Registry `alg` is exactly `x25519` for a 32-byte X25519 KEM key. TABLE-02 remains signing-only; KEM keys never verify signatures or sign their own endorsement. Raw 32-byte values do not reveal key-generation provenance. | KEM role and selection fixture; exact-case, wrong-length, signature-use and handshake-key-selection cases. |

The [0.10.0 fixture](vectors/registry-proof-0.10.0.json) pins challenge bytes,
hashes and a deterministic KEM key selection. Its local checker parses the
framing independently and checks rejection labels. It does not verify a live
proof, register a real key, complete HPKE, or establish either core's
conformance. Eight new Inspector parents are planned in
[traceability](traceability.json), bringing the plan to 91 rule groups, 479
parents and 26 mandatory children. All eight remain `planned_not_executed`.

An additional fresh-context Codex LLM read-only re-review independently
reconstructed both PoP byte strings and SHA-256 hashes. Its first pass found
that a proposed Ed25519-versus-X25519 raw-byte provenance check was not
observable: both encodings can be 32 bytes and the record has no separate
`key_type` field. The text and negative fixture were corrected to validate
the declared `alg` and an actual 31-byte KEM key. Its second pass found no
further concrete ambiguity within LLM-01/LLM-02 scope. This is a same-service
LLM review, not an organizationally independent audit or runtime proof.

This correction affects accepted proof bytes and registry-key verdicts. It
continues the already approved unreleased 0.10.0 design; it is not a silent
patch to a released 0.10.0. A released protocol would require the versioning
decision in chapter 00 before deployment. The next gate is version-pinned
Go/Rust and Inspector unit and safe runtime evidence. Organizationally
independent audit, Agent-host enforcement and live Registry Source checks
remain open; no release or protocol conformance is claimed.
