# Charter

Status: stage 1 of `PROCESS.md`, drafted 2026-09-13 for `1.0.0-draft.2`.
This document fixes what is being standardised, against which adversary, and
which requirements the chapters in `spec/` must meet. Every normative
statement written from `draft.2` onwards cites a requirement below, and
every requirement names how it is tested.

## 1. What is being standardised

The wire-level rules that let two software agents, built by different
people on different cores, prove to each other who they are, exchange
messages that cannot be forged, replayed or read in transit, and check each
other's identity against a public registry rather than a private list.

Two halves, both in scope:

1. **Identity**: how an agent is registered and managed as a decentralised
   identifier on a blockchain, which keys that record carries, how the
   record is resolved, and what a verifier must require of it before
   trusting a message.
2. **Messaging**: how a request and its response are signed, how a session
   is established in one round trip, and how session records are
   protected in both directions.

### Out of scope

| Left to | What |
|---|---|
| `sage-contracts` | The Solidity implementation of the registry, its fees, stake amounts, administrative roles and deployment addresses. This specification states what a registry must provide, not how it is written. |
| `sage-gateway` | Proxy behaviour, client configuration, the binding to the Model Context Protocol beyond the message formats defined here. |
| Implementations | Key storage, process management, transport selection, retry policy, logging, metrics. |
| Deliberately unspecified | Payment, reputation and staking signals. Published measurements of comparable on-chain reputation registries show them dominated by unreachable endpoints and self-dealing reviewers, so this version defines no trust decision that depends on them (`sage/docs/refactoring/v2/review/07-literature-review.md` §4). |

## 2. Deployment models

The rules must hold in all three, and a verifier must not need to know
which one it is in.

1. **Agent to agent.** Both endpoints hold their own keys and are
   registered. Requests and responses are signed; a session may be
   established for confidentiality.
2. **Agent to tool server.** One endpoint is an agent, the other exposes
   tools over the Model Context Protocol. The tool server verifies the
   agent's identity; it may itself be unregistered, in which case only one
   direction is authenticated.
3. **Through a gateway.** A proxy signs on behalf of a client that knows
   nothing about this specification, or verifies on behalf of a server.
   The gateway is not a trusted third party: it holds the client's key, so
   a verifier's decision is the same as if the client had signed directly.

## 3. Roles

| Role | Holds | Does |
|---|---|---|
| Agent | one signing key per algorithm, one key-agreement key | signs, verifies, establishes sessions |
| Owner | the chain account that paid for the record | registers, updates, deactivates |
| Operator | an address the owner authorised | the same writes, on the owner's behalf |
| Registry | the chain | stores DID, keys, endpoint, owner, activation state |
| Resolver | nothing | reads the registry, caches, applies the key policy |
| Verifier | the sender's public key, obtained through a resolver | decides whether a message is authentic and fresh |
| Conformance checker | vectors | decides whether an implementation follows this text |

## 4. Assets and properties

| Asset | Property wanted |
|---|---|
| The binding between a DID and its keys | only the owner can create or change it; every observer resolves the same binding |
| A message in flight | authenticity, integrity, freshness; confidentiality once a session exists |
| A session | confidentiality, integrity, ordering, forward secrecy against later compromise of the long-term keys |
| The registry record | availability of reads, authorisation of writes, observable revocation |
| An agent's private keys | never transmitted, never derivable from anything this specification puts on the wire |

## 5. Adversary

Assumed capabilities. The design must defend against each one, and each
defence is traceable to a requirement.

| Id | Capability |
|---|---|
| A-1 | Read every byte on the network, including all headers |
| A-2 | Modify, drop, truncate, reorder and duplicate messages |
| A-3 | Replay a captured message later, to the same or another endpoint |
| A-4 | Present its own valid registered identity and speak to any agent |
| A-5 | Register keys it controls, and attempt to register an identifier another party is in the middle of claiming |
| A-6 | Serve a stale or selectively withheld view of the registry to a resolver |
| A-7 | Obtain a long-term private key after a session has ended |

Explicitly not defended in this version. Each one is stated in the text so
that deployments do not assume otherwise.

| Id | Not defended |
|---|---|
| N-1 | Denial of service by volume. The design limits work per message but sets no availability guarantee |
| N-2 | A compromised endpoint. Anything its keys can sign is authentic by definition |
| N-3 | Instruction injection through message content. Provenance is cryptographic; the meaning of a payload is the application's problem |
| N-4 | Traffic analysis. Message sizes, timing and endpoint identities are visible |
| N-5 | A registry whose consensus is broken, or an owner whose chain account is stolen |

## 6. Requirements

Each requirement is testable. "Vector" means a golden test vector pins it;
"interoperability" means the two cores must agree on it in a live run;
"model" means a formal model must show it; "measurement" means a number
must be published; "review" means it is checked by reading, at last call.

### Identity, registration and management

| Id | Requirement | Tested by |
|---|---|---|
| R-1 | An agent is named by a `did:sage` identifier whose grammar is unambiguous and whose rejection rules are exhaustive | Vector, including rejected inputs |
| R-2 | An identifier names exactly one agent, everywhere. Two registries cannot issue the same identifier, and the identifier itself tells a verifier which registry to consult, so that an agent registered on one chain is never confused with an agent registered on another or with one registered outside any chain | Vector for the namespace component; review |
| R-3 | The specification defines a registry model that is not tied to one chain: the operations a registry must offer (create, read, update, revoke a key, deactivate, authorise an operator) and the properties a record must have. Each concrete registry is a profile of that model and declares its own identifier syntax, key types, signature algorithms and ownership proof, so that cryptographic differences between registries do not reach the other chapters. A registry that is not a blockchain is a profile like any other | Interoperability, one profile per core; review |
| R-4 | A record binds the identifier to its keys, its endpoint, its controller and an activation state. Every reader that sees the same registry state resolves the same binding | Vector for the record encoding; interoperability |
| R-5 | Registration is a claim that binds the identifier, the keys and the controller before it is visible, so that an observer of the claim cannot take the identifier or substitute its own keys. Where a registry cannot hide a claim, the profile states what it offers instead | Vector for the commitment derivation; model |
| R-6 | Each signing key in a record carries a proof that the registrant held the corresponding private key, bound to the identifier and to the key bytes | Vector, positive and tampered |
| R-7 | An agent becomes trustworthy only after activation, and a verifier must reject a message from a record that is not active | Vector for the state machine; interoperability |
| R-8 | A verifier must use only keys the registry marks as proven, must select among several keys by a rule stated in this text, and must reject a message whose key identifier does not name a key in the sender's record | Vector for the selection rule; interoperability |
| R-9 | Revocation takes effect immediately. A verifier must not accept a message authenticated by a key that is revoked, or by any key of a deactivated agent, at the moment it verifies; caching must not extend the life of a revoked key. The text states the point at which a registry's state counts as observed | Vector for the verdict after revocation; measurement of the delay between a revocation becoming observable and the first rejection |
| R-10 | Key rotation does not change the identifier, and a rotated-in key is usable only after its own proof is recorded | Vector |
| R-11 | Writes to a record are authorised to the controller or to a party the controller named; no one else can change a record | Interoperability; review of each profile |
| R-12 | A key-agreement key is published in the record, so that a session can be established with an agent that has never been contacted before | Vector; interoperability |
| R-13 | Registration, resolution and revocation each have a stated cost and latency, published as measurements, so that a deployment can decide what to put on the critical path | Measurement |
| R-14 | The identifier scheme is specified as a decentralised identifier method and resolves to a document that generic decentralised-identity software can consume, so that ownership of an identifier is verified with standard machinery rather than with rules private to this project | Review against the standard; interoperability with an independent resolver |

### Message authentication

| Id | Requirement | Tested by |
|---|---|---|
| R-15 | Every protected message names the identifier of the party that signed it, and the signature covers that name | Vector |
| R-16 | A signature covers the request method, target, authority and, when a body exists, a digest of that body, so that A-2 cannot change what was asked without detection | Vector, including a tampered body |
| R-17 | A message carries a creation time and a unique value, and a verifier rejects one that is outside a stated window or that repeats a value it has already accepted for that key | Vector for the rejection; interoperability |
| R-18 | A response is bound to the request it answers, so a response cannot be moved to another request | Vector |
| R-19 | A verifier rejects a signature whose algorithm does not match the key type it resolved, and rejects encodings this text does not list | Vector, including rejected encodings |
| R-20 | Signature verification is deterministic: the bytes a signer signed are reconstructed by the verifier without re-serialising what it received | Vector produced by an independent signer |

### Confidentiality and sessions

| Id | Requirement | Tested by |
|---|---|---|
| R-21 | A session is established in one round trip, authenticated to both identifiers, with no shared secret configured in advance | Vector; interoperability; model |
| R-22 | Session keys depend on a fresh ephemeral contribution from both sides, so that A-7 cannot decrypt a recorded session | Model; vector for the derivation |
| R-23 | Session keys are not derivable from the key-agreement material alone, nor from the ephemeral material alone | Model; vector |
| R-24 | Session records provide confidentiality and integrity, are ordered, and a receiver rejects a repeated or out-of-window record | Vector, including replayed and reordered records |
| R-25 | Keys are rotated within a session at a stated interval, and the rotation point is unambiguous to both sides | Vector at the rotation boundary |
| R-26 | A session is bound to the handshake that created it, so a record from one session is rejected by another | Vector; model |
| R-27 | The two directions of a session use different keys | Vector |

### Encoding

| Id | Requirement | Tested by |
|---|---|---|
| R-28 | Any structure that is signed has exactly one byte representation, and implementations agree on it including on duplicate members and malformed text | Vector, including rejected documents |
| R-29 | Each key type has one wire encoding for public keys and one for signatures, stated with lengths | Vector |
| R-30 | Every field has a stated maximum size, and a receiver rejects anything larger before doing cryptographic work | Vector; measurement of the work done before rejection |

### Interoperability and process

| Id | Requirement | Tested by |
|---|---|---|
| R-31 | Two implementations written independently of each other pass every vector and complete a live exchange | Interoperability |
| R-32 | After the design stage closes, no implementation is normative: an ambiguity in this text is a defect in this text | Review |
| R-33 | Every normative statement is pinned by a vector or is marked as advice | Generated coverage matrix |
| R-34 | An implementation can state the version it conforms to, and a verifier can refuse a version it does not implement | Vector for the version field |

### Operational

| Id | Requirement | Tested by |
|---|---|---|
| R-35 | An authentication failure returned to a sender does not reveal which check failed | Review; conformance checker |
| R-36 | A responder does public-key or registry work only after the cheap checks it can make first | Measurement; conformance checker |

## 7. Conformance levels

Extends `spec/00-overview.md` §4 with the identity half.

| Level | Must implement | Typical implementer |
|---|---|---|
| Verifier | R-1, R-2, R-4, R-7, R-8, R-9, R-15 to R-20, R-28 to R-30, R-35 | a gateway or checker that verifies messages and cards |
| Peer | Verifier plus R-12, R-21 to R-27 | an agent that establishes sessions |
| Registrar | Verifier plus R-3, R-5, R-6, R-10, R-11 | a tool that registers and manages agents |
| Reference | everything, and regenerates the vectors | the Go and the Rust core |

## 8. What the design stage must produce

Consequences of the requirements above for `spec/`:

1. A chapter on the registry and the agent lifecycle: the registry model of
   R-3, the claim procedure of R-5, the state machine of R-7, the
   authorisation rule of R-11, the immediacy rule of R-9, and one profile
   per registry kind. Today these live only in the Go client and the
   contract (`06-did-sage.md` §3 describes the record, not the lifecycle).
2. Chapter 06 gains the identifier namespace of R-2, the key selection rule
   of R-8, the fragment syntax that names a key inside a record, and the
   method specification and document projection of R-14.
3. The corrections already identified: the request target, verifying the
   received signature parameters, the responder's processing order, the
   session seed derivation, and the identity-header check (R-15, R-16,
   R-20, R-21, R-36).
4. Registries for algorithms, derivation labels, headers and error codes;
   grammars for the identifier, the key identifier, the headers and the
   proof value (R-1, R-29, R-34).
5. A security considerations section per chapter, naming which adversary
   capability the chapter defends and what it assumes from the layer below.
6. Size limits for every field (R-30).

## 9. Decisions

### Taken

| # | Question | Decision (2026-09-13) |
|---|---|---|
| 1 | How quickly revocation must take effect | Immediately, as R-9 states. A verifier must not accept a message authenticated by a revoked key, whatever its cache holds. The design stage defines the point at which a registry's state counts as observed, because a registry that confirms in blocks cannot be read instantaneously; the requirement is that no grace period is granted by the verifier itself |
| 2 | Whether registration is a prerequisite for trust | Yes. A verifier needs the sender's public key, and the record is where it comes from; without a prior registration there is nothing to check a signature against, so a message from an unregistered sender cannot be shown to be untampered. No pre-registration trust path is defined |

### Under design study

| # | Question | Direction given |
|---|---|---|
| 3 | The registry model and its profiles | Not tied to one chain. Different registries use different cryptography, the identifier must say which registry holds the record, and a deployment without any blockchain must be possible. The design must therefore be extensible: adding a registry kind, a key type or a signature algorithm must not disturb the other chapters. R-2 and R-3 state the target; the study settles how profiles are written and what the model requires of each |
| 4 | How far to follow decentralised identity standards | Agents will be numerous, each needs an identifier that cannot collide with any other wherever it was registered, and the owner of an identifier must be verifiable with standard machinery rather than with rules private to this project. R-14 states the target. The study collects what the standards require of a method specification, how existing methods guarantee uniqueness and prove control, and what SAGE must add or change; the shape is not fixed yet |
