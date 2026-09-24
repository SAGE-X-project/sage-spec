# ADOPT-06 external review package

Status: **READY_FOR_EXTERNAL_REVIEW**, not reviewed. No reviewer or review report
is assigned. The external audit remains `NOT_PERFORMED`; protocol conformance
remains `NOT_ESTABLISHED`. This package makes the requested independent review
reproducible. It neither changes the 0.10.0 rules nor certifies an implementation.

Review the `SAGE-X-project/sage-spec` normative and evidence inputs at
[commit `d86ca1a4d326d6090e50d100b834d38ec204a2c2`](https://github.com/SAGE-X-project/sage-spec/tree/d86ca1a4d326d6090e50d100b834d38ec204a2c2). This
request package is a later wrapper around that unchanged target. The [manifest](mcp-external-review-package.json)
pins every required file by SHA-256. Do not substitute the earlier 2026-09-21
adoption snapshot or the uncommitted `docs/design-and-integration-review` work
for this target. The latest Inspector evidence linked here is at commit
`58cffde89e45096b12d834fb562ea856d46b1c0b`; its older binding overlay
is explicitly tied to still earlier Go and Rust revisions in the
[evidence addendum](mcp-evidence-adoption.md).

An independent reviewer should evaluate whether the specification gives an
unambiguous acceptance or rejection decision for each of these boundaries:

1. Separate Ed25519 signing roles from X25519 HPKE keys; check active-key,
   participant-role and downgrade rules in the handshake and outer carriage.
2. Follow exact MCP plaintext bytes through the signed session envelope, AEAD,
   `request_hash`, message IDs, sequence/replay rules and bounded parsing.
3. Reconstruct both sides of initialize, the initialized notification, its
   fixed transport acknowledgement and tool discovery. Check what each side
   knows after a lost reply or local send success without peer receipt.
4. Model `OUTPUT_PENDING`, the single deferred frame, synchronous/duplicate
   completion, publication, close and deadline-equality races. Only the exact
   active send completion may advance its owner.
5. Examine one active protected exchange per owner, second-attempt rejection,
   request-ID history, response correlation, Guard admission, `pending`,
   recovery and close ordering. Include independent authorization at each
   Agent Client hop and the trusted original-input capture boundary.
6. Check registry freshness, signing-key isolation, component manifest and
   actual dispatch boundaries. Identify any property that needs an Agent host
   or live Registry Source and cannot follow from core-local tests.
7. Check scope exclusions and compatibility: MCP `2025-06-18`, selected custom
   non-HTTP binding, no in-band negotiation or fallback, and excluded HTTP,
   stdio, SSE, multiplexing and server-initiated calls.

The reviewer may use the [traceability map](traceability.json) and
[Inspector plan](inspector-plan.md) to locate cases, but should derive expected
decisions from the normative text and applicable standards independently of
the implementation and Inspector reports. The 71-parent binding overlay is
evidence for its pinned old revision. The nine MCP errata cases and five later
specification cases are still `NOT_RUN`; deployed Agent host and live Registry
Source checks are also `NOT_RUN`. Passing unit or local runtime tests cannot
resolve those deployment questions.

The review response should record the reviewer's identity, affiliation and
conflicts of interest; the exact target revision and files examined; methods
and assumptions; each finding's rule anchor, triggering state/input,
accept/reject ambiguity or security consequence, severity and proposed
correction; and any scope not examined. A no-finding conclusion needs the same
scope and independence record. Findings and their dispositions must be
reviewed before ADOPT-06 can be marked complete. Publication or conformance
requires separate evidence and decisions.

Local source and evidence identity checks:

```sh
python3 -B verification/test_mcp_external_review_package.py
python3 -B verification/check_mcp_external_review_package.py \
  --inspector-root /path/to/sage-inspector
```

The checker validates the package and pinned local inputs. It does not perform
the external review or retrieve the expiring Inspector CI artifact.
