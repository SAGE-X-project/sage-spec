# 0. Overview

## 1. Scope

SAGE secures messages between AI agents. This specification fixes the parts
that cross an implementation boundary:

1. how an agent's keys are represented and how signatures are encoded
   (`01-crypto.md`);
2. how JSON is canonicalised before it is signed (`02-jcs.md`);
3. how HTTP requests and responses are signed and verified (`03-rfc9421.md`);
4. how two agents establish a shared secret with HPKE (`04-hpke.md`);
5. how that secret becomes session keys and how records are framed
   (`05-session.md`);
6. how agents are named and how their keys are published and proven
   (`06-did-sage.md`, `07-a2a.md`);
7. the transport envelope used by the HTTP and WebSocket transports
   (`08-transport.md`).

Out of scope: on-chain registry contracts (published by
[sage-contracts](https://github.com/SAGE-X-project/sage-contracts)), the
gateway and client integrations, storage, metrics and operational concerns.

## 2. Terminology

The key words MUST, MUST NOT, SHOULD and MAY are to be interpreted as in
RFC 2119. "Initiator" is the agent that starts a handshake; "responder" is
the agent that answers. "Agent A" and "agent B" in the vectors are the
initiator and responder respectively.

Encodings used throughout:

| Term | Meaning |
|---|---|
| `hex` | lower-case hexadecimal, no prefix |
| `base64` | RFC 4648 standard alphabet with padding |
| `base64url-raw` | RFC 4648 URL-safe alphabet, no padding |
| `base58` | Bitcoin alphabet |
| `be64(n)` | 64-bit unsigned big-endian |
| `len16(s)` | 16-bit unsigned big-endian length of `s` followed by `s` |
| `a || b` | byte concatenation |

## 3. Layering

```
transport envelope (08)        WireMessage / WireResponse, X-SAGE-* headers
  HTTP signatures (03)         RFC 9421 over the request and the response
    session records (05)       ChaCha20-Poly1305, seq header, replay window
      HPKE handshake (04)      exporter secret + E2E X25519 -> session seed
        identity (06, 07)      did:sage, key proof of possession, agent card
          primitives (01, 02)  Ed25519 / secp256k1 / P-256 / X25519, JCS
```

Each layer only depends on the layers below it. A conforming implementation
of a layer MUST pass the vectors of that layer and of every layer below it.

## 4. Conformance levels

| Level | Required suites | Typical implementer |
|---|---|---|
| Verifier | `crypto`, `jcs`, `rfc9421`, `did` | a gateway or inspector that only checks signatures and cards |
| Peer | Verifier + `hpke`, `session` | any agent that establishes sessions |
| Reference | all, including verify-only vectors regenerated | the Go and Rust cores |

## 5. Versioning

- The specification version is `MAJOR.MINOR.PATCH[-draft.N]` and is written
  into every vector file as `spec_version`.
- A change that alters bytes on the wire, a derivation label, a covered
  component set or a rejection rule is breaking and increments MAJOR.
- Adding an optional field, a new vector, or clarifying text increments MINOR
  or PATCH.
- Domain-separation labels carry their own version suffix (for example
  `sage/hpke-info|v1`, `sage-session-keys-v1`). A new label version is a
  MAJOR change of this specification.
- Implementations report the specification version they conform to alongside
  their own version.

## 6. Source of truth

Until the Rust core is aligned, the Go core is normative where this text is
silent or ambiguous; each section cites the Go source files it was derived
from. Discrepancies between this text and the Go core are bugs in this text
and are fixed here first, with a vector.
