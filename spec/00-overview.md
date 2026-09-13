# 0. Overview

## 1. Scope

SAGE gives software agents a way to prove who they are and to exchange
messages that cannot be forged, replayed or read in transit. This
specification fixes everything that crosses an implementation boundary.
`charter.md` states the problem, the deployment models, the adversary and
the numbered requirements; every normative statement here serves one of
them and cites it.

| Part | Chapters |
|---|---|
| Primitives: keys, signatures, canonical JSON | `01-crypto.md`, `02-jcs.md` |
| Identity: naming, registration, resolution | `06-did-sage.md`, `09-registry.md`, `10-resolution.md`, `07-a2a.md` |
| Messaging: signed requests and responses | `03-rfc9421.md` |
| Confidentiality: handshake and session records | `04-hpke.md`, `05-session.md` |
| Carriage: envelope and headers | `08-transport.md` |
| Tables and their registration procedure | `11-registries.md` |

Out of scope, as `charter.md` §1 records: the implementation of any
registry, including the contracts published by
[sage-contracts](https://github.com/SAGE-X-project/sage-contracts); proxy
and client integrations; key storage; payment, reputation and staking
signals.

## 2. Conventions

The key words MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD
NOT, RECOMMENDED, NOT RECOMMENDED, MAY and OPTIONAL in this specification
are to be interpreted as described in BCP 14 (RFC 2119 and RFC 8174) when,
and only when, they appear in capitals.

Grammars are written in ABNF (RFC 5234). Where a chapter gives both prose
and a grammar, the grammar governs.

Terminology:

| Term | Meaning |
|---|---|
| Agent | A party that holds keys and sends or receives protected messages |
| Controller | The party authorised to change an agent's registry record |
| Registry | The service that holds records binding identifiers to keys |
| Profile | The part of this specification that says how one kind of registry meets the model of `09-registry.md` |
| Resolver | Software that reads a registry and returns a document (`10-resolution.md`) |
| Verifier | The party that decides whether a message is authentic and fresh |
| Initiator, responder | The agent that starts a handshake, and the one that answers |

Encodings:

| Term | Meaning |
|---|---|
| `hex` | lower-case hexadecimal, no prefix |
| `base64` | RFC 4648 standard alphabet with padding |
| `base64url-raw` | RFC 4648 URL-safe alphabet, no padding |
| `base58` | Bitcoin alphabet |
| `be64(n)` | 64-bit unsigned big-endian |
| `len16(s)` | 16-bit unsigned big-endian length of `s` followed by `s` |
| `a ‖ b` | byte concatenation |

## 3. Layering

```
carriage (08)                envelope, X-SAGE-* headers
  message signatures (03)    RFC 9421 over the request and the response
    session records (05)     AEAD, sequence header, replay window
      handshake (04)         HPKE exporter and ephemeral agreement
        identity (06, 09, 10, 07)  naming, registry, resolution, agent card
          primitives (01, 02)      signatures, key encodings, canonical JSON
```

A layer depends only on the layers below it. An implementation of a layer
MUST pass the vectors of that layer and of every layer below it.

## 4. Conformance levels

A conformance level names a set of requirements from `charter.md` §7. An
implementation states the level it claims and the specification version it
claims (§5).

| Level | Implements | Typical implementer |
|---|---|---|
| Verifier | Reads records and verifies messages and cards | a proxy or conformance checker |
| Peer | Verifier, and establishes sessions | an agent |
| Registrar | Verifier, and creates and maintains records | a registration tool |
| Reference | Every level, and regenerates the vectors | the reference cores |

## 5. Versioning and extension

- The version is `MAJOR.MINOR.PATCH[-draft.N]` and appears in every vector
  file as `spec_version`.
- A change is MAJOR when it alters bytes on the wire, a derivation label, a
  covered component set, a rejection rule, or the meaning of an existing
  registry entry.
- A change is MINOR when it adds an optional field, a registry entry, a
  profile or a vector. A change is PATCH when it only clarifies.
- Domain-separation labels carry their own version suffix. A new label
  version is a MAJOR change.
- Before `1.0.0` the draft number increments instead, and MAJOR changes are
  expected: `PROCESS.md` names what each draft closes.
- An extension adds a registry entry or a profile under the procedure of
  `11-registries.md` §1. An extension that would change an existing entry is
  not an extension but a MAJOR change.
- An implementation MUST refuse a version whose MAJOR differs from one it
  implements, and MAY accept a higher MINOR by ignoring what it does not
  know, provided ignoring it does not weaken a check.

## 6. Normative status of this text

This text is the specification. An ambiguity, a gap or a contradiction is a
defect in this text and is fixed here first, together with a vector that
pins the fix; implementations then follow. No implementation is normative.

Where this text cites a source file, the citation is informative: it records
where a rule came from, not what the rule is.

## 7. References

Normative:

| Reference | Title |
|---|---|
| RFC 2119, RFC 8174 | Key words for use in RFCs |
| RFC 5234 | Augmented BNF for syntax specifications |
| RFC 4648 | Base16, Base32 and Base64 data encodings |
| RFC 8032 | Edwards-curve digital signature algorithm |
| RFC 6979 | Deterministic usage of DSA and ECDSA |
| RFC 7748 | Elliptic curves for security (X25519) |
| RFC 7517, RFC 7518 | JSON Web Key, JSON Web Algorithms |
| RFC 8785 | JSON canonicalisation scheme |
| RFC 8439 | ChaCha20 and Poly1305 |
| RFC 9180 | Hybrid public key encryption |
| RFC 9421 | HTTP message signatures |
| RFC 9530 | Digest fields |
| RFC 8941 | Structured field values for HTTP |
| RFC 9457 | Problem details for HTTP APIs |
| W3C Decentralized Identifiers 1.0 | Identifier syntax, documents, resolution requirements |
| W3C Controlled Identifiers 1.0 | Verification methods, services, verification relationships |
| W3C DID Resolution | Resolution and dereferencing contract |
| CAIP-2 | Chain-agnostic chain identifiers |

Informative: `charter.md`, `PROCESS.md`, and the analyses cited in
individual chapters.
