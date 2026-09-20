# sage-spec

Protocol specification and golden test vectors for SAGE (Secure Agent
Guarantee Engine): the wire-level rules that every SAGE implementation must
follow so that agents built on different cores interoperate.

This repository contains no implementation. The reference implementation is
the Go core, [`sage`](https://github.com/SAGE-X-project/sage); the Rust core,
[`rs-sage-core`](https://github.com/SAGE-X-project/rs-sage-core), is being
aligned to this specification. Both prove conformance by running the vectors
under `vectors/` in CI.

## Contents

| Path | What |
|---|---|
| `spec/00-overview.md` | Scope, terminology, layering, versioning, conformance levels |
| `spec/01-crypto.md` | Key types, signature algorithms and encodings, key identifiers |
| `spec/02-jcs.md` | JSON canonicalisation (RFC 8785) and where it is required |
| `spec/03-rfc9421.md` | HTTP Message Signatures profile (RFC 9421): components, parameters, headers, verification rules |
| `spec/04-hpke.md` | HPKE handshake profile (RFC 9180): suite, info and export context, E2E combiner, acknowledgement tag, init payload and response envelope |
| `spec/05-session.md` | Session layer: seed and id derivation, key schedule, record format, replay window, key rotation |
| `spec/06-did-sage.md` | The `did:sage` method: grammar, chains, key material, proof of possession |
| `spec/07-a2a.md` | A2A agent card and its proof |
| `spec/08-transport.md` | Transport envelope (`WireMessage`, `WireResponse`) and the `X-SAGE-*` headers |
| `spec/09-registry.md` | The registry model, the agent lifecycle, the proof of possession and one section per registry kind |
| `spec/10-resolution.md` | The document a registry record projects to, and the resolution contract |
| `spec/11-registries.md` | Signature algorithms, key encodings, labels, registry kinds, headers and diagnostic codes, with the procedure for adding an entry |
| `vectors/` | Golden test vectors, one JSON file per suite (see `vectors/README.md`) |
| `charter.md` | What is being standardised, the deployment models, the adversary, and the numbered requirements every chapter must meet |
| `PROCESS.md` | How this specification is developed: the five stages from charter to frozen text, the draft ladder, where each chapter stands, and the work plan to `1.0.0` |

## Status

Version `1.0.0-draft.1`. The text describes what the Go core implements on
2026-09-12 (`sage` v1.5.2 with the refactoring merged up to that date). Every
normative statement is backed by a vector or by a cited source file in the Go
core. Items marked *open* are known gaps that a later draft resolves.

This draft is a snapshot of one implementation, which is how to start and not
how to finish. `PROCESS.md` defines the five stages that take the text from
here to a frozen `1.0.0` (charter, design, verification, analysis,
finalisation), what each draft closes, and the work each stage needs. Until
`1.0.0`, corrections that change bytes are expected and arrive as draft
increments.

## How to check an implementation

1. Load every file in `vectors/`.
2. For each vector with `"mode": "deterministic"`, recompute `output` from
   `input` and compare byte for byte.
3. For each vector with `"mode": "verify"`, run your verification path on
   `output` (decrypt, verify signature, verify proof) and require success.
4. Reject any input marked `rejected` (DID grammar) and any tampered record.

The Go core does exactly this with `sage-vectors check -dir vectors`. The
workflow in `.github/workflows/check.yml` runs it against the Go core's main
branch on every push.

## Versioning

The specification and the vectors are versioned together (`spec_version` in
every vector file). A breaking change to any wire format increments the major
version and gets a new vector set; implementations state which specification
version they conform to. See `spec/00-overview.md` §5.

## Licence

Apache-2.0 (see `LICENSE`). The text, schemas and vectors are meant to be
copied into implementations and their test suites.

### Proposed MCP connection ownership

The [trusted connection-owner API proposal](proposals/non-http-mcp-setup/owner-contract.md)
describes local ownership, bounded callbacks and Guard handoff for the unadopted
non-HTTP setup design. It is review input, not a protocol release or conformance claim.

The [adoption reconciliation](proposals/non-http-mcp-setup/reconciliation.md) maps
that proposal to the preserved local 0.10.0 design and records unresolved adoption
conditions. Its mappings are review input, not evidence of protocol execution.
