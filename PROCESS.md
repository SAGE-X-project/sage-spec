# How this specification is developed

Status: process definition, 2026-09-13. It applies from `1.0.0-draft.1`
onwards and governs what has to be true before the text is tagged `1.0.0`.

The current draft describes what one implementation did on one day: chapter
00 §6 makes the Go core normative wherever the text is silent. That is the
right way to start and the wrong way to finish, because it freezes
accidental behaviour. The 2026-09 review found four such cases where the
Go core and the written rule disagreed with RFC 9421 or with the
specification's own other chapter
([`sage/docs/refactoring/v2/review/08-implementation-evaluation.md`](https://github.com/SAGE-X-project/sage/blob/main/docs/refactoring/v2/review/08-implementation-evaluation.md)).
From here the text leads and the implementations follow.

## 1. Stages

Five stages, borrowed from how transport and security protocols are
standardised: state the problem, design against it, prove the design is
implementable and interoperable, analyse what it guarantees, then freeze.
A stage is not a calendar phase; a chapter can sit in a different stage
from its neighbours, and section 3 records where each one is.

| Stage | Question it answers | Artefacts | Exit criteria |
|---|---|---|---|
| 1. Charter | What is being standardised, for whom, against which adversary, and what is out of scope | `charter.md`: scope, non-goals, deployment model, adversary model, numbered requirements (`R-n`), conformance levels | Every requirement is testable and traceable to a use case; the adversary model names what is and is not defended; conformance levels fixed |
| 2. Design | What exactly goes on the wire, and why that way | The chapters `spec/00-08`, each with normative rules, a rationale note per non-obvious choice, a security considerations section, and grammars for every field; registries for algorithms, derivation labels and error codes | Every normative statement cites the requirement it serves; no chapter defers to an implementation; every open item is either resolved or explicitly deferred to a later version with a reason |
| 3. Verification | Can two independent implementations produce and accept the same bytes | Vectors covering each rule, positive and rejected; a rule-to-vector coverage matrix; two implementations passing in CI; a live interoperability run; the conformance checker exercising every rule | Coverage matrix complete; the Go and the Rust core pass every vector; a live exchange between them succeeds and the checker detects each seeded violation |
| 4. Analysis | What does the protocol guarantee, and at what cost | Security analysis per adversary capability; a formal model of the handshake and the record layer; a comparison with the published analyses of the mechanisms reused; measured cost (latency, bytes, on-chain fees) against baselines | Every claim in the charter is either proved, measured, or restated as a limitation; the formal model covers the handshake's authentication and secrecy goals; limitations listed in the text |
| 5. Finalisation | Is the text stable enough to be implemented by strangers | A last-call announcement with a fixed window; the resolution of every comment; a frozen tag; an errata file and a maintenance policy | Last call closed with no unresolved objection; no open item left unlabelled; `1.0.0` tagged; errata and extension process written down |

### Draft ladder

Each draft closes one stage, so that implementers know what changed and
what may still move.

| Draft | Closes | Contains |
|---|---|---|
| `1.0.0-draft.1` (released 2026-09-12) | none; snapshot of the Go core | 9 chapters, 6 vector suites, 26 vectors, 8 open items |
| `1.0.0-draft.2` | stages 1 and 2 | charter with numbered requirements; wire-format corrections; registries; security considerations and grammars per chapter; every open item resolved or deferred |
| `1.0.0-draft.3` | stage 3 | rejected-input vectors, coverage matrix, both cores green, live interoperability run, conformance checker complete |
| `1.0.0-draft.4` | stage 4 | security analysis, formal model, measurements, limitations |
| `1.0.0` | stage 5 | last call resolved, text frozen |

## 2. Rules that hold in every stage

1. **The text leads.** A change lands as: text in `spec/`, a vector that
   pins it, the Go core, the Rust core, and the conformance checker. A
   change that cannot be pinned by a vector is not normative; it is a note.
2. **One normative source.** Chapter 00 §6 ("the Go core is normative where
   this text is silent") is deleted when stage 2 closes. Until then every
   use of it is logged as an open item, because it marks a gap in the text.
3. **Nothing is removed for being unused.** A section whose mechanism has
   no caller yet is kept and its role is stated
   ([`sage/docs/refactoring/DECISIONS.md`](https://github.com/SAGE-X-project/sage/blob/main/docs/refactoring/DECISIONS.md)
   decision 8). Removal needs supersession or harm.
4. **Breaking changes are cheap now and expensive later.** Until `1.0.0`,
   a correction that changes bytes is a draft increment. After `1.0.0` it
   is a major version with a parallel vector set, so every known correction
   lands before the freeze.
5. **Two implementations, one of them not the reference.** A rule that only
   the Go core implements is not verified. The Rust core is the independent
   implementation; where it cannot implement a rule, the rule is wrong or
   under-specified.
6. **Every rejection is specified.** For each field, the text says what an
   implementation must reject, and a vector carries the rejected input. A
   verifier that accepts what another rejects is an interoperability
   failure, not a quality difference.

## 3. Where each chapter stands

Assessment of 2026-09-13. "Stage 2 incomplete" means the chapter is
readable and implemented but lacks the artefacts stage 2 requires
(rationale, security considerations, grammar, registry entries).

| Chapter | Stage | Missing for the next stage |
|---|---|---|
| 00 Overview | 1 incomplete | No charter: scope is one paragraph, there is no adversary model and no numbered requirements; §6 defers to the Go core |
| 01 Crypto | 2 incomplete | Open items O-1 (proof-of-possession digest for secp256k1), O-2 (deterministic P-256), O-3 (the RSA identifier names PSS while the operation is PKCS#1 v1.5); no algorithm registry; no security considerations |
| 02 JCS | 2 incomplete | Behaviour on duplicate keys and lone surrogates is unstated and the two cores differ; no rejected-input vector |
| 03 RFC 9421 | 2 incomplete | Wire-format corrections pending (request target without the method; signature parameters verified verbatim; the `X-SAGE-DID` check); O-4 (`tag`), O-5 (a normative default component set); no error registry |
| 04 HPKE | 2 incomplete | O-6 (cookie check before public-key work), O-7 (the counter expansion versus the session key schedule; resolved by scoping each, decision 8); the responder's processing order is a rule, not a note |
| 05 Session | 2 incomplete | The handshake path does not derive the session seed the way this chapter specifies; no rekey or stale-record vector |
| 06 did:sage | 2 incomplete | O-8 (a DID Document projection); how a verifier treats an unverified or revoked key is prose in two places |
| 07 A2A card | 2 incomplete | Key encodings accepted and rejected differ between the cores; no grammar for the proof |
| 08 Transport | 2 incomplete | No vector at all; the header set is not a registry |
| Absent | 1 | MCP binding: named in the strategy and implemented by the gateway, unspecified here |

Verification assets that exist: 6 suites, 26 vectors, both cores running
them in CI, a conformance checker with known gaps
([`review/10-inspector-test-matrix.md`](https://github.com/SAGE-X-project/sage/blob/main/docs/refactoring/v2/review/10-inspector-test-matrix.md)).
Analysis assets that exist: a literature review of the mechanisms reused
([`review/07-literature-review.md`](https://github.com/SAGE-X-project/sage/blob/main/docs/refactoring/v2/review/07-literature-review.md)).
No formal model, no measurements, no security considerations sections.

## 4. Work plan to `1.0.0`

Ordered; each step ends with a merged pull request in this repository and,
where the step changes bytes, in both cores.

### Stage 1, to `draft.2`

1. `charter.md`: scope and non-goals; the deployment model (agent to agent,
   agent to MCP server, through a gateway); the adversary (a network
   attacker who can read, modify, drop, reorder and replay, and a
   registry that may be stale or hostile) and what is explicitly not
   defended (denial of service, prompt injection, a compromised endpoint);
   requirements `R-1..R-n`, each one testable.
2. Rewrite 00 §1-§4 against the charter; delete §6 when stage 2 closes and
   replace it with the rule that ambiguity is a defect in this text.

### Stage 2, to `draft.2`

3. The four wire-format corrections, already prepared as branches in the
   cores: request target without the method; signature parameters verified
   from the received bytes including unknown ones; the responder checks the
   cookie before resolving a DID or verifying a signature; the handshake
   derives the session seed as chapter 05 specifies while chapter 04 keeps
   the counter expansion for channel binding and non-session peers.
4. The `X-SAGE-DID` consistency check becomes a rule with a vector.
5. Registries: signature algorithms, derivation labels, `X-SAGE-*` headers,
   error codes. Each entry names the chapter that defines it and the
   version that added it.
6. Grammars: ABNF for the DID, `keyid`, the headers and the proof value.
7. Per chapter: a rationale note for every non-obvious choice and a
   security considerations section naming what the chapter defends and what
   it assumes the layer below provides.
8. Resolve or defer O-1 to O-8, each with a recorded reason.
9. A chapter for the MCP binding, or a statement that it is out of scope
   and specified by the gateway.

### Stage 3, to `draft.3`

10. Rejected-input vectors for every rejection rule, and the cases the
    conformance matrix lists as missing.
11. A rule-to-vector coverage matrix, generated rather than hand-written,
    failing CI when a normative statement has no vector.
12. A live interoperability run between the two cores through the gateway,
    in CI, and the conformance checker exercising every rule with seeded
    violations.

### Stage 4, to `draft.4`

13. A formal model of the handshake and the record layer (Tamarin or
    ProVerif) covering mutual authentication, secrecy of the session keys,
    and resistance to replay and to key-compromise impersonation; the model
    and its output committed here.
14. Measurements against baselines (TLS 1.3, mutual TLS, a one-round-trip
    Noise pattern) for latency and bytes, and the on-chain cost of
    registration; published as data, not prose.
15. A security analysis mapping each charter requirement to the mechanism
    that meets it, the vector that pins it, and the model or measurement
    that supports it; limitations stated in the text.

### Stage 5, to `1.0.0`

16. Last call: a fixed window announced in the repository, with the draft
    and the analysis linked, inviting review from outside the project.
17. Resolve every comment in the open, then freeze: tag `1.0.0`, pin the
    vector set, add `ERRATA.md` and the extension process (how a new
    chapter or algorithm is added without a major version).

## 5. Change control

- A change starts as an issue stating the requirement it serves and the
  rule it changes. A change with no requirement behind it is a note.
- A change merges as one set: text, vector, Go core, Rust core, checker.
  If the cores cannot land together, the text merges first and the draft
  is not released until both pass.
- Every merged change appears in `CHANGELOG.md` under the draft that
  carries it, saying what moved on the wire.
- Decisions that shape the protocol are recorded in the project decision
  log with the evidence and the alternatives considered.
- After `1.0.0`: errata for clarifications that do not change bytes, minor
  versions for optional additions, major versions for anything that
  changes bytes, a derivation label, a covered-component set or a
  rejection rule (chapter 00 §5).

## 6. Review without a working group

This project has one maintainer, so the usual guard, a working group of
competing implementers, is absent. Its substitutes, in decreasing order of
strength:

1. The independent Rust implementation. It is the closest thing to a
   second implementer and must be written from the text, not from the Go
   code.
2. Adversarial conformance testing. The checker seeds each violation and
   requires both cores to reject it; a rule nobody rejects is not a rule.
3. The published analyses of the reused mechanisms. Where SAGE composes
   HPKE, HTTP Message Signatures and an authenticated record layer, the
   composition is what needs argument, and the literature review lists the
   results that constrain it.
4. Outside review at last call, including the standards bodies that own the
   mechanisms reused, when a profile of their work is being published.

## 7. Cost of this process

It delays `1.0.0` by the length of stages 1 to 4 and it will change bytes
more than once before the freeze, which invalidates vectors and forces both
cores to follow. The alternative, tagging the current draft, costs more:
the four known defects would become a compatibility burden, and a profile
that contradicts RFC 9421 cannot interoperate with anything outside this
project.
