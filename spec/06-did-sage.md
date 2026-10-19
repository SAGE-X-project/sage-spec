# 6. The did:sage method

Target: **0.10.0**. Existing `vectors/did.json` is legacy evidence, not proof of conformance. Requirements: `charter.md` R-1, R-2, R-8, R-14.

An agent is named by an identifier that says which registry holds its
record. The registry model and the operations are in `09-registry.md`; the
document an identifier resolves to is in `10-resolution.md`.

## 1. Syntax — ID-01 (R-1, R-2, R-30)

```abnf
did-sage     = %s"did:sage:" registry-id ":" agent-id
registry-id  = kind ":" locator
kind         = lowercase *( lowercase / DIGIT / "-" )
locator      = segment *( ":" segment )
agent-id     = segment
segment      = 1*64 ( ALPHA / DIGIT / "." / "-" / "_" )
lowercase    = %x61-7A
```

The number of segments in `locator` is fixed by the kind and is given in
the profile for that kind (`11-registries.md` §5). A parser that does not
implement the kind MUST reject the identifier rather than guess where the
locator ends; it reports `id.unknown-kind`.

A DID MUST be at most 256 ASCII bytes and a DID URL at most 289 bytes.
Only the profile syntax in chapter 09 is accepted. Paths, queries, empty
segments and additional fragments MUST be rejected.
The ASCII `did:sage:` prefix is case-sensitive and MUST appear exactly as
shown in both a DID and a DID URL. A mixed-case scheme or method prefix
MUST be rejected as `id.malformed`; it is not normalized or treated as an
alias. The `%s` syntax is the case-sensitive ABNF form of RFC 7405.

A key inside a record is named by a fragment:

```abnf
did-url      = did-sage "#" key-id
key-id       = 1*32 ( ALPHA / DIGIT / "-" / "_" )
```

Examples, informative:

```
did:sage:eip155:11155111:0xc7ecf7ad6ee71cb0d94f0eb00f46f1ddf432a808:0x1234abcd
did:sage:web:agents.example.com:billing-bot
did:sage:web:agents.example.com:billing-bot#key-1
```

## 2. Uniqueness and equality — ID-02 (R-2)

- `registry-id` identifies one registry instance. Two registries MUST NOT
  share a `registry-id`, and a profile states what makes its locator
  unambiguous: for a chain, the chain reference of CAIP-2 together with the
  address of the registry; for a hosted registry, the domain name.
- `agent-id` is unique within that registry.
- Two identifiers denote the same agent when their strings are equal after
  the normalisation below. There are no aliases: an implementation MUST NOT
  accept an abbreviation of a kind or of a locator.
- Normalisation: `kind` is lower-case; a chain locator's hexadecimal address
  is lower-case; no percent-encoding is permitted anywhere in the
  identifier. An identifier that is not in normal form MUST be rejected
  (`id.malformed`).

Because the identifier names the registry, an agent registered in one
registry can never be confused with an agent registered in another, and a
proof of possession made for one registry is not valid in another
(`09-registry.md` §4).

## 3. Which key verifies a message — ID-03 (R-8, R-9, R-15, R-19)

Each signature binding names a full `did-url` with a fragment: HTTP and execution intents use `keyid`, wire envelopes use `kid`, Cards use `verificationMethod`, A2A card signatures use the JWS protected header `kid` (`../profiles/a2a-1.0-binding.md` A2AB-05), and handshake completion uses `respKid`. In the procedure below, key reference means that binding-specific field. A verifier:

1. parses the key reference into an identifier and a key name, rejecting a reference
   without a fragment (`sig.malformed`);
2. resolves the identifier (`10-resolution.md`) and rejects if the record is
   unknown, not active, or unreadable (`record.not-found`,
   `record.inactive`, `record.unreachable`);
3. finds the key with that name and rejects if there is none
   (`key.not-in-record`);
4. rejects if that key is not accepted, is revoked, or has expired
   (`key.unproven`, `key.revoked`, `key.expired`);
5. uses only the algorithm of that selected key and, when the binding carries `alg`, rejects any mismatch
   (`sig.alg-mismatch`);
6. requires the DID part of the key reference to equal the authenticated sender field
   and the expected peer, when one is configured (`sig.binding`);
7. verifies the signature with that key alone. A verifier MUST NOT try
   other keys in the record.

Where a protocol step needs a key but no `keyid` names one, for example the
key-agreement key used to start a handshake, the record's key for that
purpose is selected by the rule in `09-registry.md` §2.

## 4. Operations — ID-04 (R-3, R-10, R-11)

Creating, activating, adding a key, revoking a key and deactivating a
record are defined once, in `09-registry.md` §3, and are the same for every
kind of registry. A profile states how each operation is carried out and
who is authorised.

## 5. Relationship to the identifier standards

`did:sage` is a decentralised identifier method. Its syntax conforms to the
identifier grammar of the W3C specification, its resolution contract is in
`10-resolution.md`, and the document it produces uses the controlled
identifier data model. This is a proposed method, not a claim of W3C endorsement or registration.
The JSON representation follows [DID Core](https://www.w3.org/TR/did-core/);
SAGE resolution metadata extensions are explicitly identified in chapter 10.

## 6. Security considerations

| Threat | Defence |
|---|---|
| A-5: an attacker registers the identifier a party is claiming | The identifier names the registry and the claim binds the keys (`09-registry.md` §3) |
| A-5: a proof made in a cheap registry is replayed in an expensive one | The proof covers the `registry-id` (`09-registry.md` §4) |
| A-4: a valid agent presents another agent's key | The `keyid` must name a key in the sender's own record, and only that key is tried |
| A-6: a stale view hides a revocation | Resolution states its observation point and grants no grace (`09-registry.md` §5) |
| Confusion between two records | No aliases and a single normal form; equality is byte equality |

This chapter assumes the primitives of `01-crypto.md` and the resolution
contract of `10-resolution.md`.

### 6.1. Assets, participants and trust boundaries

The assets are the unique registry/record binding, immutable key material and
proofs, current lifecycle and operator state, and the freshness of each read.
A controller's management credential and an agent's message-signing key have
different authority. A PoP or KEM endorsement is not management authorization.
Private signing, management and session keys, ephemeral secrets and claim
salts before disclosure require protection; public keys and registry records
do not provide confidentiality. Cryptographic requirements are in chapter 01.

An untrusted caller can supply valid identities as well as malformed input.
Network observers can read public data and modify, replay, reorder or withhold
traffic. A resolver can return stale or conflicting observations. Security
therefore depends on the trusted Registry/source, authenticated command
binding, finality/readiness configuration, protected signing/capture boundary,
and current durable record/grant state. These are distinct from an untrusted
plugin, Card endpoint, model-proposed actor or caller-supplied RPC URL.

The charter's exclusions remain material: a stolen authorized controller,
malicious trusted Registry or broken consensus can authorize false state.
Initially poisoned enrolment cannot be repaired by resolving that same state.
Ordinary component alteration is within Execution Guard scope only with its
protected baseline/capture and complete mediation assumptions. Valid identity
is neither benign intent, user approval nor upstream delegation (charter N-7).
The analysis below does not certify a currently deployed Registry or fill the
missing concrete management/fork binding documented in the review record.

### 6.2. Threats across method operations

The table analyzes each operation, rather than importing application-message
replay rules into the management plane. Existing checks are conditional on the
complete trusted binding required by chapter 09; an unspecified API or source
cannot obtain those guarantees merely by labeling an actor authenticated.

| Attack | Create (including eip155 commit/reveal) | Activate, add/revoke key, update services, authorize/revoke operator, deactivate | Resolve/read |
|---|---|---|---|
| Eavesdropping | Chain transactions and revealed records are public. The salted commitment hides claim contents only before reveal, with random secret salt; it does not hide sender, timing or fees. Web management confidentiality depends on its selected channel. | Public mutations and retained history expose relationships and timing. Signing authenticates bytes without encrypting them. Management channel/log confidentiality requires its binding. | Public records are not secret. Web TLS protects transit content from an ordinary network observer, not the origin or trusted resolver; traffic size/timing/endpoints remain visible. |
| Replay | A creation PoP alone authorizes nothing. The eip155 account/registry-scoped commitment is single-use and its reveal window is bounded; transaction replay protection is a separate binding duty. Web creation still requires authenticated command admission. | Exact expected version and atomic authorization prevent a second commit at the same prior version; immutable revoked key names/material prevent resurrection. Reconnecting or possessing a captured grant is not a fresh authorization. Missing command integrity remains a known gap. | A valid historical record alone is insufficient. A fresh authoritative observation is required per operation, with readiness, finalized version/rollback checks and no positive-cache authorization of a later operation. |
| Insertion | Registry/DID-bound proofs and authorized creation reject substituted ownership only when complete claim and principal binding are established. Independent claim-name racing remains possible. | An untrusted body actor, service URI or PoP cannot grant authority. Complete command authentication and current controller/scoped grants are required; omitted deployment binding cannot be presumed correct. | Untrusted records/keys and unknown fields are rejected under the closed record contract; an approved source is required. A discovered service is not a source of Registry authority. |
| Deletion | Withheld transactions, reveal suppression or lost responses can prevent registration. Commit expiry permits refusal, not a success inference. | Dropped requests do not justify success. A lost reply can hide a committed mutation: inspect authoritative history; uncertain durable outcome quarantines dependent writes/success. Deactivation retains the record/tombstone. | Suppression, unreachable source or missing readiness causes refusal. Freshness checks cannot force delivery or recover a withheld state. |
| Modification | The commitment binds all claim fields; proofs bind DID, key name, algorithm and material. These do not replace the complete authenticated management command. | Registry, DID, operation, prior version and all arguments must reach one authenticated atomic decision. State/grants/history/tombstone commit together. Current abstract rules do not authenticate arbitrary external bytes by themselves. | Selected-key-only verification, PoP validation and coherent authoritative snapshots reject inconsistent substitutions under the trusted source assumptions. A malicious trusted origin/validator can still lie within that trust boundary. |
| Denial of service | Parsing, PoP, admission, consensus and expired commitment handling consume resources. Claim-name races, withheld inclusion and finality loss can block progress. | Proof checks, serialization contention, durable history/grant growth and credentialed flooding consume resources. Revocation cannot become observable sooner than publication/finality. | A small request can force a fresh authoritative read, validation and a bounded document response. Unavailable authority causes refusal even for an otherwise valid message. |
| Amplification | A small commitment or claim can trigger transaction propagation/validation and later retained state. Fees limit some paid writes, not every peer/RPC cost. | One update can induce proof checks, history writes and network replication. Authorized operators can externalize these costs within their scopes; per-record limits do not bound the total number of records. | A short DID may trigger backend requests/cryptography and a larger bounded response. Fixed origins/no Card-endpoint fetch limit destination choice, not work or state amplification. |
| Man in the middle | Claim proofs/commitment protect their specified fields only. End-to-end authenticated management binding and chain/source identity remain necessary; no claim of arbitrary relayer safety is made. | Channel termination, credential-to-actor mapping and exact command binding are part of the management trust boundary. A forwarding header or re-serialized body is not automatically equivalent to the authenticated command. | Authenticated web origin TLS and trusted chain/source/readiness protect their respective paths. DNS/RPC responses alone are not independent authority. Chain ID/address/code alone cannot distinguish every fork. |

Unspecified management authentication and fork disambiguation remain open
method-document findings. This analysis records their consequences rather
than treating the absence as an attack being inapplicable. Controller transfer
and recovery are not 0.10.0 operations; migration uses a new record and explicit
peer configuration. Solana is reserved and is not an executable profile.

### 6.3. Availability, amplification and DLT resource burdens

Record/key/service/JSON limits and cheap checks before cryptographic work bound
one attempt. They do not prevent aggregate floods, connection exhaustion,
CPU contention, storage exhaustion, backend fan-out or many individually valid
requests. Transports must reject ambiguous framing before record consumption;
this does not itself bound aggregate HTTP/TLS connection costs. A reachable
return path makes simple spoofed reflection harder, not authenticated flooding
or computation/state amplification impossible. No measured amplification factor
or universal availability guarantee is asserted.

The chain path imposes transaction signature and execution/proof work on nodes,
propagation bandwidth on peers, and consensus/finality work on validators.
Full nodes retain/synchronize canonical state and, according to their node
policy, historical chain data. The trusted Registry additionally retains
required mutation/grant history and permanent key/record tombstones even when
the current record is bounded. Fees may be paid by a transaction sender or an
explicit sponsor, while other peers/operators still pay validation, read,
network and storage costs. Invalid submissions and fresh RPC reads can consume
resources without a successful paid mutation. Consensus rules, capacity,
pricing, propagation and pruning policies belong to the chosen chain; no
particular transaction fee, throughput or historical-node policy is assumed.

A hosted Registry instead pays for TLS, authentication, proof verification,
serialized writes, durable history and freshly produced read responses. An
attacker can force resource costs with valid-looking reads; a credentialed
operator may submit many otherwise authorized commands. Record bounds do not
cap total registry cardinality or required durable history. Exhaustion cannot
be reported as partial success, and an ambiguous commit outcome requires the
quarantine/recovery rule in REG-03/REG-08.

Fail-closed freshness deliberately trades availability for rejection of stale
keys: once the operation's snapshot is too old or source readiness is lost,
a later operation cannot reuse a previously positive result. An operation's
consistent snapshot is not permission for later cached authorization.
Publication/finality latency can delay observable revocation even when a
verifier adds no grace. A chain partition, trusted-source outage, eclipse of a
node, lost trusted clock or denied synchronization can therefore halt protected
operations. More retries against unavailable authority can increase load.

Deployment admission, concurrency/time budgets, validated destinations and
resource monitoring can reduce these costs. Their values/effectiveness require
separate deployment evidence and cannot weaken mandatory freshness or commit
atomicity. Prevention of all volumetric floods is outside scope because finite
network/compute/storage resources can be saturated by distributed or privileged
senders, including before authenticated application checks. Honest consensus
and network access likewise cannot be guaranteed by a DID method. These limits
explain the charter's availability/consensus exclusions; they do not excuse
avoidable unbounded parsing, arbitrary fan-out or partial durable writes.
Expected costs and publication-to-finality/observation latency require the
measurements in R-13, not invented zero-delay or fee claims.

This method-specific analysis follows [RFC 3552 sections 4.6, 4.7 and
5](https://www.rfc-editor.org/rfc/rfc3552.html#section-5). It distinguishes
object-field protection, channel protection and atomic authorization. It
introduces no new wire encoding, algorithm, acceptance rule or operating root.

### 6.4. Privacy considerations

Software agents may represent people or organizations, so public agent data
can affect their privacy. All nine threat categories in [RFC 6973 section
5](https://www.rfc-editor.org/rfc/rfc6973.html#section-5) are applicable to this
method; the following are method-specific consequences and mitigation limits.

| Reference and threat | did:sage exposure and mitigation limits |
|---|---|
| 5.1.1 Surveillance | Public chain changes, repeated DID lookups and service traffic reveal activity. TLS does not conceal everything from the origin, resolver or traffic observer. Payload encryption does not conceal public registry content or every identifier-bearing header; traffic concealment is outside charter N-4. |
| 5.1.2 Stored data compromise | Required history/tombstones and optional query/admin logs can reveal relationships after compromise. Private keys/secrets must never enter protocol logs under CRYPTO-05. Protect/minimize optional logs with access and retention policies without deleting required integrity history. No encrypted-database or log-retention implementation is presumed. |
| 5.1.3 Intrusion | Discoverable service URIs and recognizable agent names can attract unsolicited calls, notifications or flooding that interrupts the represented user's activity. Discovery confers no permission to call or execute; access controls and service admission remain necessary. Never fetch an endpoint merely to validate registration. |
| 5.1.4 Misattribution | A shared controller, compromised management credential, stale key view or similarly named agent can attribute activity incorrectly. Exact DID/key binding and fresh observation address substitution under their assumptions, not legal identity, benign intent, physical operator identity or correctness of an LLM interpretation. |
| 5.2.1 Correlation | A persistent DID, retained controller account, reused keys, service URIs and transaction relationships can link activities. Independent identifiers/keys may reduce some links, but controller funding/history/endpoints can still correlate them; key rotation/deactivation does not erase the old linkage. No unlinkability guarantee is offered. |
| 5.2.2 Identification | Names, domains, controller accounts or combined external information can identify an individual behind an agent. Publish only necessary public metadata and avoid personal data or secrets in identifiers/service fields. Cryptographic verification is not a civil-identity verification service. |
| 5.2.3 Secondary use | A third party can reuse publicly indexed records/history for profiling or other purposes beyond registration. The format carries no enforceable downstream-use restriction; original registration consent cannot make every later use safe. Optional service/query collection needs its own purpose/access policy. |
| 5.2.4 Disclosure | Record/service strings can unintentionally expose confidential paths, account associations or sensitive organizational roles. Public records remain readable after deactivation; signing/encryption of application messages does not redact those records. Keep secrets out of public metadata and restrict disclosure of optional private operational data. |
| 5.2.5 Exclusion | Controllers can perform supported updates/revocations but cannot erase permanent identifiers, revoked-key history or already replicated public observations. A person represented by an agent may not control its controller account. Operator notices/access/correction procedures can help participation; this method provides no general erasure, consent or data-subject access protocol. |

These mitigations are bounded deployment practices, not a new record field or
proof of regulatory compliance. Required public integrity data cannot become
private merely by changing a log policy. A new identity or key may still be
linked through old public observations, and a new observer need not ask the
original controller's permission to copy public data. No new logging obligation
or transitive human approval requirement is introduced here.

## 7. Change in 0.10.0

The earlier form was `did:sage:<chain>:<identifier>`, where the network was
configuration rather than part of the identifier. Two registries could
therefore issue the same identifier, and a proof of possession made against
one network was byte-identical for another. Every identifier changes; legacy identifiers MUST NOT be silently converted or accepted as aliases.
Migration requires an explicit new registration and configuration change;
existing deployments are not assumed absent.
