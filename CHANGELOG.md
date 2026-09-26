# Changelog

## 0.10.0 — standards scope and resolution error clarification (2026-09-26)

- Record the exact external-standard editions, SAGE restrictions and remaining
  verification gates without claiming standards certification.
- Identify DID Resolution as a Candidate Recommendation Draft informing SAGE's
  own resolution contract. Fix the public RFC 9457 error titles and statuses.
- Add two planned Inspector cases, for 91 groups and 481 parents. Preserve the
  479-case registry-correction snapshot and all earlier evidence separately.
  Refresh the current design graph for the expanded plan.
- No new wire field, core execution result, external audit or conformance claim.

## 0.10.0 — registry proof and KEM role clarification (2026-09-25)

- Define `len16` as length only and pin exact PoP challenge bytes for signing
  keys and endorsed X25519 keys.
- Register exact `x25519` as a KEM-only registry `alg`; reject aliases, role
  mismatches and message-signature use.
- Add eight planned Inspector cases, for 91 groups and 479 parents. Preserve
  the prior 471-case plan and LLM review target as historical snapshots.
- This unreleased design correction changes acceptance decisions. Core and
  Inspector conformance remains unestablished until revision-bound execution.

## 0.10.0 — coordinated trust and standards clarification (2026-09-24)

- Require each trusted Client in a multihop path to capture and independently
  authorize its exact outgoing request; upstream IDs and digests convey no grant.
- Clarify DID/JWK consumer interoperability, one-signature HTTP profile and
  existing signed `X-SAGE-*` naming exception. Record explicit DID migration.
- Add five unexecuted Inspector parent cases, for 91 groups, 471 parents and
  26 mandatory children. Pin the prior 466-case design as historical.
- No wire field, release, audit or conformance claim is added; implementations
  and Inspector need revision-pinned validation.

## 0.10.0 — non-HTTP MCP binding errata adoption (2026-09-24)

- Pin trusted local binding identity, exact descriptor JCS digest, peer expectations
  and construction-time rejection before MCP setup.
- Require one active protected JSON-RPC exchange per owner, including local busy
  refusal, authenticated overlap closure, output-barrier ordering and durable
  outcome preservation.
- Add nine planned parent cases; 91 groups, 466 parent cases and 26 mandatory
  child assertions are now in the current plan. The prior 457-case plan remains
  pinned as historical evidence.
- This is an unreleased 0.10.0 design correction with changed local admission
  verdicts. Earlier Inspector PASS results do not establish conformance to it;
  Go/Rust owners and Inspector require a new revision-pinned implementation and run.
  No wire field, release, external audit or conformance claim is added.

## 0.10.0 — non-HTTP MCP normative design adoption (2026-09-21)

- Publish the preserved 0.10.0 design baseline without changing historical vector metadata.
- Adopt the reviewed non-HTTP MCP 2025-06-18 binding and exact one-tool descriptor.
- Distinguish durable EXECUTING fencing, atomic queue admission, worker claim and effects.
- Reconcile EXEC-04/05/06 dispatch and administrative cancellation; retain all prior identities.
- Add 14 rule groups and 71 parent cases with 26 mandatory child assertions. No execution status is promoted.
- The smaller Ed25519-only binding does not remove baseline signing algorithms or define HTTP mapping.
- Version-string APIs alone cannot advertise support. No release/tag, third-party audit or full core conformance is claimed.

## 0.10.0 — documentation design (2026-09-13)

The existing chapters are updated in place. This version continues the project
history under the approved 0.x policy; it supersedes draft naming without changing
historical vector metadata. No release/tag or implementation conformance is claimed.

- Charter: trusted Client/dispatch boundary, ordinary Plugin/MCP/Skill compromise,
  capture/authorisation, fail-closed enforcement, and deferred pre-enrolment compromise.
- HTTP/envelopes: exact version and coverage, authenticated routing/metadata,
  request-bound responses, strict parsing and atomic replay handling.
- Handshake/session: transcript-bound HPKE combination, one directional schedule,
  deterministic sequence nonce, confirmation and restart/expiry semantics.
- Crypto/identity: unambiguous encodings and private Keccak suite name, honest Card
  proof format, signing possession versus KEM endorsement, authoritative resolution,
  observable revocation and explicit registry profile support.
- New Execution Guard profile and host integration guide define required outcomes
  independently of hook API. They do not equate signature validity with safe intent.
- Current X-bar/AST graphs, purpose/vision and repository boundaries guide future
  library/SDK/MCP/service/demo work. No source repository is split or changed.
- Inspector case/traceability plan records missing execution and proof evidence.
  Existing vector JSON files remain unchanged historical fixtures.

The changes above are potentially byte- and verdict-incompatible. Existing Go,
Rust and inspector implementations must follow the migration plan; they are not
made conformant by updating a version string.

## Historical design work formerly labelled 1.0.0-draft.2

The design stage of `PROCESS.md`. Every change serves a requirement in
`charter.md`, and several change what a conformant implementation signs or
accepts. Breaking changes are expected before `1.0.0`.

### Identity

- Identifiers name the registry that holds the record:
  `did:sage:<kind>:<locator>:<agent-id>`. Previously the network was
  configuration, so two registries could issue the same identifier and a
  proof of possession made for one network was byte-identical for another.
  Every existing identifier changes.
- New `09-registry.md`: one registry model with the record shape, the
  lifecycle and its operations, one proof of possession that binds the
  registry, the agent, the algorithm and the key, the rules that make
  revocation immediate, and three profiles, two of them chains and one not a
  blockchain.
- New `10-resolution.md`: the document a record projects to, the resolution
  contract, its metadata, error reporting and an HTTP binding.
- New `11-registries.md`: signature algorithms, key encodings, domain
  separation labels, registry kinds, headers and diagnostic codes, with the
  procedure for adding an entry.
- `06-did-sage.md` rewritten around the grammar, the uniqueness rules, the
  rule that selects the verifying key, and the method's relationship to the
  identifier standards. Chain aliases are removed; there is one normal form.
- `00-overview.md` gains the requirements language, the extension policy and
  the reference list, and no longer makes any implementation normative.

## 1.0.0-draft.1 (2026-09-12)

First draft. Documents the wire formats of the Go core (`sage` v1.5.2 plus
the 2026-09 refactoring) and publishes 26 vectors in six suites generated by
`sage-vectors`.

### 2026-09-14 — crypto/trust review corrections (unpublished 0.10.0 draft)

- Define pending snapshots, exact-intent status reads and immutable terminal results.
- Bind policy artifacts/issuer/epoch through an explicit domain-separated commitment.
- Fix sender/receiver AAD bounds and enumerate pinned session identity/key checks.
- Define provisional key-confirmation deadlines and atomic cryptographic acceptance.
- Close CST-01..05 at document level; expand the plan to386 unexecuted cases.
  Inspector implementation readiness is distinct from conformance/security approval.
