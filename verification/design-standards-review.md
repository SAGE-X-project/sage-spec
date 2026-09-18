# Design gap and standards conformance review

Date: **2026-09-18**. Target: **SAGE 0.10.0 working draft** at the current working
tree of `sage-spec` (`main`, uncommitted modifications to chapters 00..11 plus
untracked `analysis/`, `architecture/`, `guides/`, `profiles/`, `seeds/`, `verification/`).

Decision: **REVISE one standards defect before any interoperability attempt; decide
three wire-affecting standards questions before 0.10.0 is frozen; treat the design
findings as scope decisions for the charter rather than editorial fixes.**

This is a third review pass, complementary to [review.md](review.md),
[standards.md](standards.md), [crypto-trust-review.md](crypto-trust-review.md) and
[crypto-trust-closure.md](crypto-trust-closure.md). It does not re-litigate CST-01..05,
which are closed at document level.

## 1. Method and independence

The reviewer is an assistant instance, separate from the drafting and CST sessions but
not organizationally or model-independent. No external audit, formal proof, live
exchange or implementation test is claimed. Every standards finding below was checked
against the official publication text, and every implementation claim against source
read locally in this session; §6 records exactly what was consulted and how.

Scope: all 12 chapters, the charter, the Execution Guard profile, the integration
guide and the traceability data, judged against the project goal of protecting
agent-to-agent and agent-to-MCP message exchange from an attacker. No specification
text, implementation, vector or Seed was changed by this review.

Two classes of finding are separated deliberately:

- **Design findings (DSR-D\*)** concern whether the specified mechanisms achieve the
  stated goal. Several are scope decisions the charter may legitimately decline; the
  finding is then that the decline should be explicit, not silent.
- **Standards findings (DSR-S\*)** concern divergence from a cited or applicable
  standard. These are ranked by whether they break interoperation between two honest
  implementations, because that is the failure mode that costs the most later.

Severity follows the CST convention. **P1** means resolve before the affected contract
is frozen or before interoperability is attempted; it is not a demonstrated exploit.
**P2** means a material cost, ambiguity or internal contradiction.

## 2. Summary

| ID | Severity | Finding | Wire impact |
|---|---|---|---|
| DSR-S01 | P1 | Content coding is banned but `Accept-Encoding` is never constrained, so two honest HTTP implementations fail | One sentence in chapter 03; no format change |
| DSR-D01 | P1 | No delegation model exists for a multi-hop agent chain, although the charter lists Agent-to-Agent as a deployment model | Either a charter exclusion, or a new intent field |
| DSR-D02 | P1 | The profile commits to a policy rigorously but imposes no floor on policy content, so an allow-everything deployment conforms | None; a charter requirement |
| DSR-D03 | P1 | The intent carries no argument provenance, so EXEC-07's "results are data, not policy" rule cannot be enforced by a policy engine | New optional-to-populate intent member |
| DSR-D05 | P1 | Per-message fresh registry observation lets an unauthenticated sender force third-party registry work, and makes the registry an availability single point | Chapter 09 admission rules; no format change |
| DSR-S02 | P2 | Requiring exactly one `Signature-Input` member rejects the intermediary-added signature that RFC 9421 §4.3 is designed for | Chapter 03 wording |
| DSR-S03 | P2 | Rejecting additional JWK members contradicts RFC 7517 §4 and undermines R-14 | Chapter 10 wording |
| DSR-S04 | P2 | `X-SAGE-*` header names contradict BCP 178 | Header rename; cheapest now |
| DSR-S06 | P2 | The Ed25519 profile is stricter than both candidate reference libraries, so R-31 agreement depends on custom code in each | Implementation note |
| DSR-S07 | P2 | The normative reference table omits standards the text depends on | Editorial |
| DSR-S08 | P2 | `JsonWebKey2020` does not exist in the cited Controlled Identifiers 1.0 | Chapter 10 label |
| DSR-D04 | P2 | No aggregate call budget per captured request | Receiver ledger rule only |
| DSR-D06 | P2 | Identifier change and Solana removal have a recorded decision but no costed migration | Documentation |
| DSR-S05 | Accepted | `sage-secp256k1-keccak256` is unregistered, but the mandatory suite is registered | None |
| DSR-D07 | Informational | All 386 planned cases remain unexecuted and CST closure was self-review | None |

## 3. Design findings

### DSR-D01 — P1: no delegation model for a multi-hop agent chain

Sources: `charter.md` §2 (Agent to Agent deployment model),
`profiles/agent-mcp-security.md` §3 (intent fields), §5 line 232.

**Observed.** The Execution Guard binds exactly one `issuer` to one `recipient`.
`parent_call_id` is explicitly powerless: "Parent IDs express causality; they grant no
delegated authority or wider permissions." `original_digest` commits the capture made
by *this* Client. A receiver is told to "trust the configured issuing principal and its
authorisation policy for the permitted operation."

Consider a user request to agent A, which calls agent B, which calls MCP server C.
B signs with its own key, its own `request_id` and its own capture. Nothing in C's
verified input traces to the user's original request through A. C cannot distinguish
a call B makes because A asked from one B originates alone. Trust is therefore pairwise
static configuration, growing with the square of the participant count, and the
authorisation chain is severed at every hop.

This matters precisely because Agent-to-Agent is a listed deployment model and because
a confused-deputy attack becomes available after a single hop: a compromised B issues
calls that C accepts as properly authorised.

**Required resolution, one of two.** Either record in `charter.md` §5 that 0.10.0
protects a single authorisation hop and that transitive delegation is excluded, in the
same explicit style as N-1..N-6; or specify a delegation chain.

If a chain is specified, RFC 8693 §4.1 is the applicable precedent. Its `act` claim
nests actors so that "the outermost `act` claim represents the current actor while
nested `act` claims represent prior actors", with "the least recent actor ... most
deeply nested"; §4.4's `may_act` states that a party is authorised to become the actor.
Borrow those two semantics. **Do not adopt the encoding**: `act` is a JWT claim, JWT
implies JWS, and JWS reintroduces the message-carried `alg` that chapters 01 and 11
deliberately eliminated. A SAGE chain should nest the prior intent digest and its proof
inside the new intent, require the receiver to verify the whole chain, and require
permissions to be monotonically non-increasing along it. Cite RFC 8693 informatively,
as `standards.md` already cites RFC 9396.

**Closure checks (not executed).** Two-hop chain accepted with narrowed permission;
two-hop chain rejected when the second hop widens permission; broken chain link
rejected; chain replay at the wrong recipient rejected; single-hop behaviour unchanged.

### DSR-D02 — P1: the policy has a commitment but no floor

Sources: `profiles/agent-mcp-security.md` §2 line 44 and the policy commitment subsection.

**Observed.** EXEC-02 specifies `policy_digest` with unusual rigour: a domain-separated
SHA-256 over a closed JCS descriptor, a fresh epoch per revision, an artifact manifest
covering the evaluator and its dependencies, serialized retirement, and an explicit
worked byte example in [crypto-trust-closure.md](crypto-trust-closure.md).

The content of that policy has no stated minimum. The only constraint is that it "MUST
resolve to executable allow/deny rules and MUST NOT consist solely of an instruction to
the LLM to call a security tool." Deny-by-default is not required. No relationship
between the policy decision and `original_digest` is required, and EXEC-02 states the
receiver need not see the original text at all.

Consequently a deployment whose engine is `allow-everything/1` satisfies every EXEC
rule and would pass every planned inspector case, because R-38 tests rejection of
*alteration after* authorisation, not the correctness of the authorisation.

Combined with N-3, which excludes semantic prompt injection, the protected interval is
"from the moment the Client decided" to "the moment the tool ran". The attack the
project exists to resist, an attacker influencing what the Client decides, falls
immediately before that interval. The specification is honest about this
(`guides/integration.md` §1), but honesty makes it a stated non-goal rather than a
partial defence, and the charter requires no mitigation at all.

**Required resolution.** Add a charter requirement fixing a policy floor. A universal
policy language remains unnecessary; fix the obligations, not the syntax. At minimum:
default deny; an enumerated set of inputs the evaluator MUST consume; and a statement
that a policy which cannot deny any call does not satisfy the Execution Guard level.

**Closure checks (not executed).** A descriptor whose artifacts cannot express denial
fails profile setup; an evaluator that ignores a required input fails review; a
deny-by-default fixture rejects an unlisted tool.

### DSR-D03 — P1: arguments carry no provenance, so the "results are data" rule is unenforceable

Sources: `profiles/agent-mcp-security.md` §3 (intent field table), §7 (EXEC-07).

**Observed.** EXEC-07 states the correct rule: "Results are data, not policy, new skills
or grants. Following an instruction in a result always requires a new policy-governed
call." The intent schema that carries that new call has `arguments` and
`parent_call_id` and nothing else relevant. There is no member recording which prior
call outputs, or which externally sourced content, the argument values were derived
from.

The policy engine is therefore asked to govern the call while being denied the one
input that distinguishes `path = <what the user typed>` from `path = <what a fetched
web page said>`. The single most effective structural mitigation against injected
content, refusing to let untrusted-derived values reach a high-privilege tool, cannot
be written as a rule against the current schema.

**Required resolution.** Add a provenance member to the intent, for example a
`derived_from` array of prior `call_id` values whose output influenced the arguments,
together with a coarse trust classification per argument. Register it through the
chapter 11 §1 procedure, since it changes signed bytes and therefore requires a MINOR
increment under OVERVIEW-03.

**Do not** adopt W3C PROV for this. It is RDF and JSON-LD based, and chapter 10 has
already decided against JSON-LD processing; importing it would contradict an existing
design decision for no gain at this granularity.

**Known cost.** The Client must track data flow through its own model loop, which is
real implementation work, and the tracking must itself sit inside the trusted boundary
so that a compromised plugin cannot under-report a trust level. The field is worth
little without DSR-D02's policy floor, so the two should land together.

**Closure checks (not executed).** An argument derived from a tool result is marked and
denied for a privileged tool; the same literal value typed by the user is allowed;
a plugin attempting to downgrade a trust marking is rejected; an absent marking is
treated as untrusted rather than trusted.

### DSR-D04 — P2: no aggregate call budget per captured request

Sources: `profiles/agent-mcp-security.md` §3, §4. Verified by search: the specification
contains no occurrence of a rate limit, budget or quota concept.

**Observed.** Replay control guarantees that one intent executes at most once. Nothing
bounds how many distinct intents a single `request_id` may spawn. A compromised
component that cannot forge an intent can still drive the model to emit many
individually permitted calls, which is the ordinary shape of an exfiltration: many
allowed reads followed by one allowed send.

**Required resolution.** Require the receiver to enforce a configured maximum number of
dispatched calls per `(issuer, request_id)`, and to deny beyond it. The identifier is
already present in every intent, and exceeding the budget maps onto the existing
`policy_denied` error, so no schema or error-enum change is needed.

**Known cost.** A legitimate long task will hit the ceiling. Budget increase must
itself be a protected administrative action, not something the caller can request.

### DSR-D05 — P1: the freshness rule creates an unauthenticated amplification vector and an availability single point

Sources: `spec/09-registry.md` REG-05 line 115, `spec/03-rfc9421.md` MSG-04,
`spec/04-hpke.md` HPKE-06, `spec/09-registry.md` REG-08. Verified by search: the
specification contains no negative-caching rule and no rate-limiting requirement.

**Observed.** REG-05 requires a fresh authoritative observation, at most five seconds
old, for "every protected-message decision, session operation and execution decision",
with no cache grace. MSG-04's ordering resolves and validates the key *before*
verifying the signature, which is unavoidable because the key is needed to verify.

An unauthenticated sender can therefore force one registry observation per message by
naming any identifier. Under the eip155 profile that is a finalized-block chain read.
Under the web profile REG-08 requires a fresh `no-store` fetch of a document whose
lifetime is at most five seconds, per operation.

No mitigation is specified. There is no negative-result rule for identifiers that do
not exist, no rate-limiting requirement, and HPKE-06 declines to define a cookie
exchange while making a local admission check a MAY. N-1 disclaims availability, but
the party absorbing the cost here is a third party, the chain RPC provider or the
registry origin, not only the verifier.

The same rule has an availability face. A registry outage stops all protected
communication, which is the intended fail-closed behaviour recorded in `charter.md` §4,
but no degraded mode, no pre-authorised offline window and no operational analysis
exists anywhere in the specification. The predictable result is that implementers
introduce an unspecified cache, which is the worst outcome available.

**Required resolution.** Three additions to chapter 09, none of which weakens R-9.

1. Permit bounded negative admission state. R-9 forbids grace on a *positive*
   observation; remembering that an identifier was absent is the opposite direction and
   can only cause a legitimate newly registered agent to be refused for a bounded
   period. State a maximum lifetime, and state that this state never contributes to an
   authentication decision, only to whether work is performed.
2. Express it as verifier-internal application state, explicitly **not** an HTTP cache
   entry. RFC 9111 §5.2.2.5 constrains a cache storing a response: "The no-store
   response directive indicates that a cache MUST NOT store any part of either the
   immediate request or the response and MUST NOT use the response to satisfy any other
   request." A record of "identifier X was absent at time T" reuses no response and
   satisfies no later request from stored content, so it stays outside that directive,
   but the text must say so or an implementer will read a contradiction with REG-08.
3. Promote the HPKE-06 admission check from MAY to MUST for public endpoints, and bind
   resolution work to a per-source budget. Signal exhaustion with 429 (RFC 6585) and
   `Retry-After` (RFC 9110 §10.2.3). **Constrain 429 to volume per source only.** If it
   can vary with whether an identifier exists, it becomes exactly the authentication
   oracle R-35 exists to prevent.

Additionally, state the availability consequence in `charter.md` §4 next to the
fail-closed property, so that deployments size registry availability deliberately.

**Closure checks (not executed).** Repeated unknown identifiers cause at most one
registry read per negative-state lifetime; a newly registered identifier is accepted
once that state expires; 429 responses do not differ between an existing and a
nonexistent identifier; a registry outage denies rather than degrades.

### DSR-D06 — P2: the identifier change and Solana removal have a decision but no costed migration

Sources: `spec/06-did-sage.md` §7, `spec/09-registry.md` REG-07; implementation read at
`sage/pkg/agent/did/utils.go:110-134` and the directory `sage/pkg/agent/did/solana/`.

**Observed.** The implementation forms `did:sage:ethereum:0x<address>` and
`did:sage:solana:<address>`. The specification requires
`did:sage:eip155:<chain-id>:<registry-address>:<agent-id>`, forbids aliasing and
silent conversion, and REG-07 declares `solana` reserved and unsupported, requiring a
conforming resolver to answer `id.unknown-kind`. The implementation nonetheless ships a
Solana DID package.

Adopting 0.10.0 therefore means re-registering every existing agent and withdrawing the
Solana path. `spec/06-did-sage.md` §7 records the decision; no document records the
cost, the sequencing or the disposition of existing registrations.
`architecture/migration-plan.md` addresses repository boundaries, not identifiers.

**Required resolution.** A short migration document covering identifier transition,
existing-registration disposition and the Solana decision, referenced from the charter
§9 decision table.

### DSR-D07 — Informational: evidence status and the independence of the closure

Verified from `verification/traceability.json`: 45 requirements, 77 rule groups and 386
cases, with every case in `planned_not_executed`. The six historical vector suites carry
26 cases at `1.0.0-draft.1` and, as the specification itself states, certify nothing for
0.10.0. CST-A1, the independent analysis of the custom
`HKDF-Extract(salt=th, IKM=exporterHPKE || ssE2E)` composition, remains open.

`crypto-trust-review.md` states plainly that its reviewer "is the same assistant that
coordinated the draft" and that independence is not claimed. The closure of CST-01..05
is therefore self-closure. It improved the document materially, and the present review
found no reason to reopen any of the five, but it does not substitute for external
review. This review has the same limitation and makes the same disclosure.

## 4. Standards conformance findings

Every citation in this section was read from the official publication during this
review; §6 records the exact source and question.

### DSR-S01 — P1: banning content coding without constraining `Accept-Encoding` breaks honest implementations

Source: `spec/03-rfc9421.md` MSG-01, line 25. Verified by search: the specification
contains no occurrence of `Accept-Encoding`.

**Observed.** MSG-01 requires senders to omit `Content-Encoding` and receivers to
reject it. Nothing tells a sender to request an unencoded response.

An ordinary HTTP client library attaches `Accept-Encoding: gzip` by default. A server
honouring that header compresses its response. The receiving side must then reject that
response under MSG-01. Two honest implementations using stock libraries fail to
communicate, with no attacker involved.

This is the only finding in this review that breaks interoperation between correct
implementations, which is why it is ranked above every design finding.

**Required resolution.** One sentence in chapter 03: a protected request MUST send
`Accept-Encoding: identity`, and a responder MUST NOT apply a content coding. RFC 9110
§12.5.3 defines exactly this mechanism, describing `identity` as "a special case,
representing no encoding" and stating that a client communicates it accepts no encoding
by sending `Accept-Encoding: identity`; §8.4 requires a server to apply only codings the
client accepts.

The digest definition itself is correct and needs no change. MSG-01 computes the digest
over "received HTTP content bytes after transfer framing removal", which is RFC 9530
`Content-Digest` semantics rather than `Repr-Digest`, and the distinction is handled
correctly.

### DSR-S02 — P2: requiring exactly one signature rejects the pattern RFC 9421 §4.3 exists for

Source: `spec/03-rfc9421.md` MSG-01, lines 10-12.

**Observed.** MSG-01 requires "exactly one `Signature-Input` dictionary member and one
matching `Signature` member, both labelled `sig1`."

RFC 9421 §4.3 states that "multiple signatures can be included in a single HTTP message
by using different labels for each signature in the Signature-Input and Signature
fields", and describes the intermediary case directly: "An intermediary or the
application can add additional signatures to a message by computing a new signature
over the message (with all existing signatures present) and adding new Signature-Input
and Signature fields with a different label."

Under MSG-01 as written, any gateway, CDN or service mesh that adds its own signature
causes every SAGE message to be rejected. MSG-02's rule about proxies concerns a proxy
that *changes* a covered component, not one that *adds* a signature, so it does not
cover this case.

**Required resolution.** Restate the rule as a selection rule rather than a cardinality
rule: the `sig1` label MUST be present and MUST be the SAGE signature verified under
this chapter; other labels are ignored and confer nothing. This is what RFC 9421 §3.2
step 1.1 anticipates, requiring a verifier to determine which signature to process
"based on the policy and configuration of the verifier". Security is unchanged, because
an ignored signature grants no authority, and the deployment surface widens materially.

Note for the drafting: RFC 9421 gives no guidance on unrecognised labels, so the
ignore rule must be stated explicitly rather than assumed.

### DSR-S03 — P2: rejecting additional JWK members contradicts RFC 7517 §4 and undermines R-14

Source: `spec/10-resolution.md` line 29.

**Observed.** Chapter 10 requires that JWKs "contain exactly `kty`, `crv`, `x` and, for
EC keys, `y`", and rejects "extra/contradictory members".

RFC 7517 §4 states the opposite obligation for consumers: "Additional members can be
present in the JWK; if not understood by implementations encountering them, they MUST be
ignored." The members most likely to appear are registered, not exotic: `use` (§4.2),
`key_ops` (§4.3), `alg` (§4.4) and `kid` (§4.5). Generic JWK tooling emits them as a
matter of course.

The internal consequence is sharper than the external one. R-14 requires that the
identifier "resolves to a document that generic decentralised-identity software can
consume". Chapter 10 then rejects the documents such software produces. The requirement
and the rule contradict each other.

`standards.md` records that SAGE "intentionally restricts optional JWK members for one
wire form" but does not record the conflict with RFC 7517's ignore obligation.

**Required resolution, one of two.** Either relax consumption to accept the registered
optional members while forbidding them from influencing any verification decision,
keeping production restricted to the four members; or keep the strict rule, record it
explicitly in `standards.md` as a departure from RFC 7517 §4, and narrow R-14's claim so
it no longer promises generic consumability. The first preserves R-14; the second is
cheaper but costs the requirement.

### DSR-S04 — P2: `X-SAGE-*` header names contradict BCP 178

Source: `spec/11-registries.md` TABLE-06, lines 111-112, and the reservation of
`X-SAGE-X-` for private use. Verified by search: RFC 6648 is cited nowhere in the
repository, including `standards.md`.

**Observed.** RFC 6648 is BCP 178. Its §3 recommendation to creators of new parameters
is that they "SHOULD NOT prefix their parameter names with `X-` or similar constructs".
The obligation is SHOULD NOT rather than MUST NOT, and the RFC addresses application
protocol parameters generally with HTTP headers as one example, so this is a
best-practice deviation rather than a violation.

The practical cost is the one BCP 178 describes: if any of these fields is later
standardised, the name must change and both forms must be supported during transition.

**Required resolution.** Rename to `SAGE-Version`, `SAGE-DID`, `SAGE-Message-ID`,
`SAGE-Context-ID`, `SAGE-Task-ID`, and reserve `SAGE-X-` for private use. These names
appear in the signature coverage list of MSG-02, so this is a wire change. Version
0.10.0 promises no compatibility and the chapters are unpublished, which makes this the
cheapest moment the change will ever have. If it is declined, record RFC 6648 in
`standards.md` as a knowing deviation rather than leaving it unmentioned.

### DSR-S05 — Accepted deviation: `sage-secp256k1-keccak256` is unregistered

Source: `spec/11-registries.md` TABLE-02, line 36.

**Observed.** RFC 9421 §6.2.2 establishes the HTTP Signature Algorithms registry with
initial contents `rsa-pss-sha512`, `rsa-pkcs1-v1_5-sha256`, `hmac-sha256`,
`ecdsa-p256-sha256`, `ecdsa-p384-sha384` and `ed25519`. A generic RFC 9421
implementation cannot process an unregistered `alg` value.

**Assessment: this deviation is correctly handled and needs no change.** The
mandatory-to-implement suite is `ed25519`, which is registered, and the optional P-256
suite uses the registered `ecdsa-p256-sha256`. Only the optional secp256k1 suite is
SAGE-private, and chapter 01 states plainly that it "is a SAGE-local identifier, not an
IANA assignment or JOSE ES256K". The mandatory interoperability path is therefore fully
standard.

Recommended follow-up, not a defect: record in the deployment binding that a deployment
using the secp256k1 suite cannot interoperate with stock RFC 9421 tooling, and decide
whether IANA registration is wanted before 1.0.

### DSR-S06 — P2: the Ed25519 profile exceeds both candidate reference libraries

Source: `spec/01-crypto.md` CRYPTO-02, line 35. Verified against library source read
locally in this session; see §6.

**Observed.** CRYPTO-02 requires that "decoded A and R MUST be nonidentity members of
the prime-order subgroup ([L]A and [L]R are identity)", the uncofactored equation, and
explicit rejection of mixed-torsion points.

Go's standard library, read at `crypto/internal/fips140/ed25519/ed25519.go`
(`verifyWithDom`, toolchain go1.26.8), checks the signature length, rejects
`sig[63]&224 != 0`, rejects a non-canonical S via `SetCanonicalBytes`, and uses the
cofactorless equation `[S]B = R + [k]A`. It performs **no** prime-order subgroup check
on A, and it never decodes R at all, comparing the recomputed point's encoding against
`sig[:32]`.

Rust's `ed25519-dalek` 2.2.0, the version pinned in `rs-sage-core/Cargo.lock`, is closer
but still insufficient. `verify_strict` does decompress R and rejects
`signature_R.is_small_order() || self.point.is_small_order()`. In curve25519-dalek 4.1.3
`is_small_order()` is `self.mul_by_cofactor().is_identity()`, that is `[8]P = identity`,
which excludes only the eight torsion points. A mixed-order point `P + T` where `P` has
prime order satisfies `[8](P+T) != identity` and therefore passes. The helper that
matches CRYPTO-02 is `is_torsion_free()`, defined as
`(self * BASEPOINT_ORDER_PRIVATE).is_identity()`, and `ed25519-dalek` never calls it;
the crate contains no occurrence of the name.

**Assessment.** This is not an interoperability break. Honestly generated keys and
signatures lie in the prime-order subgroup, so honest traffic passes; only adversarially
crafted input is rejected, which is the intent. The cost is implementation burden and
the risk to R-31: cross-implementation agreement holds only if both cores implement the
same extra checks, and neither language gets them from its default API.

**Required resolution.** Add an implementation note to chapter 01 stating that the
profile is deliberately stricter than RFC 8032 §5.1.7 permits, that Go requires an
explicit prime-order check plus decoding of R using an external edwards25519 package,
and that Rust requires `verify_strict` **plus** `is_torsion_free` on both A and R. Add a
mixed-torsion negative vector to the planned cases, distinct from the small-order case,
since the two are separated by exactly this boundary.

### DSR-S07 — P2: the normative reference table omits standards the text depends on

Source: `spec/00-overview.md` §7. Verified by extracting every RFC number from the
normative table and comparing against usage across the repository.

**Observed.** The table lists RFC 2119, 4648, 5234, 6979, 7517, 7518, 7748, 8032, 8174,
8439, 8785, 8941, 9180, 9421, 9457 and 9651.

Missing, though relied upon:

| Standard | Where the text depends on it |
|---|---|
| RFC 5869 | Every HKDF extract and expand in chapters 04 and 05; present in `standards.md` but absent from the normative table |
| RFC 9562 | UUIDv4 is required for envelope `id`, `context_id`, `task_id`, handshake `ctx` and `kid`, intent `request_id`, `call_id` and policy `epoch`; no UUID standard is cited anywhere |
| RFC 9110 | Chapters 03 and 08 define HTTP behaviour, status codes and field handling |
| RFC 8446 | TLS server authentication is required in chapters 03, 08, 09 and 10 |
| RFC 3986 | URI syntax underlies DID URLs, service endpoints and `@target-uri` |

**Required resolution.** Add these to the table. The text is not wrong; an independent
implementer simply cannot determine from it which UUID or TLS version to target.

### DSR-S08 — P2: `JsonWebKey2020` does not exist in the cited Controlled Identifiers 1.0

Source: `spec/10-resolution.md` line 11; normative reference to W3C Controlled
Identifiers 1.0 in `spec/00-overview.md` §7.

**Observed.** Chapter 10 sets the verification method type to `JsonWebKey2020`.
Controlled Identifiers v1.0, a W3C Recommendation dated 15 May 2025, defines two
verification method types, `Multikey` (§2.2.2) and `JsonWebKey` (§2.2.3), and does not
mention `JsonWebKey2020` at all. The suffixed name belongs to an earlier generation of
cryptosuite vocabulary.

**Required resolution.** Change the type to `JsonWebKey`, matching the cited
Recommendation. If the older name must be retained for an existing consumer, say which
consumer and cite the document that defines it, because the currently cited one does not.

## 5. Standards impact of the proposed changes

Assessed because a change that breaks a standard cannot be adopted regardless of its
security value.

| Proposed change | Standard touched | Assessment |
|---|---|---|
| Provenance member in the intent (DSR-D03) | None. The intent is a SAGE-private object serialized with RFC 8785, whose only constraint is I-JSON validity, which a list of UUID strings satisfies | Adoptable. Follows chapter 11 §1 and needs a MINOR increment |
| Policy floor (DSR-D02) | None. A charter requirement with no wire effect | Adoptable |
| Per-request call budget (DSR-D04) | None. `request_id` exists; exhaustion maps to the existing `policy_denied` value | Adoptable with no schema change |
| Delegation chain (DSR-D01) | RFC 8693 §4.1 and §4.4 supply the semantics; adopting the encoding would import JWT and JWS | Adoptable only as SAGE-native encoding with RFC 8693 cited informatively. W3C PROV is rejected because chapter 10 has already declined JSON-LD |
| Negative admission state (DSR-D05) | RFC 9111 §5.2.2.5 binds a cache storing a response, not application state recording that a lookup failed; RFC 9111 §2 notes negative results such as 404 are storable in general | Adoptable if the text states it is not an HTTP cache entry, which also avoids an apparent conflict with REG-08's `no-store` |
| Admission budget and 429 (DSR-D05) | 429 is RFC 6585, not RFC 9110; `Retry-After` is RFC 9110 §10.2.3 | Adoptable if 429 depends only on source volume, never on identifier existence, or it becomes the oracle R-35 forbids |
| Migration document (DSR-D06) | None | Adoptable |
| Independent analysis and fixtures (DSR-D07) | None | Adoptable |

No proposed change requires deviating from a standard. Two required a change of
approach, recorded above: the delegation chain must not use JWT, and the negative state
must not be described as an HTTP cache.

## 6. Verification log

Standards text consulted during this review, with the question asked of each:

| Source | Question | Result used in |
|---|---|---|
| RFC 6648 | Exact recommendation on the `X-` prefix, its strength, and BCP status | DSR-S04: BCP 178, §3, SHOULD NOT, general application parameters |
| RFC 7517 | Section 4 treatment of additional members; registered optional members | DSR-S03: MUST-ignore quoted; `use`/`key_ops`/`alg`/`kid` at §4.2-4.5 |
| RFC 9421 | Multiple signatures; algorithm registry initial contents; unrecognised labels | DSR-S02, DSR-S05: §4.3 quoted; six registered algorithms; no label guidance |
| RFC 9110 | `Accept-Encoding` and the `identity` coding; `Content-Encoding` | DSR-S01: §12.5.3 and §8.4 |
| RFC 9111 | Scope of the `no-store` directive; storability of negative results | §5 assessment of the negative-state proposal |
| RFC 8693 | The `act` and `may_act` claims and how nesting expresses a chain | DSR-D01: §4.1 and §4.4 |
| W3C DID Core | DID ABNF; whether `method-specific-id` permits multiple colons | §7 confirmation below |
| W3C Controlled Identifiers 1.0 | Verification method types defined; presence of `JsonWebKey2020` | DSR-S08: Recommendation of 15 May 2025; `Multikey` and `JsonWebKey` only |

Source read locally in this session:

| Source | Observation | Used in |
|---|---|---|
| `crypto/internal/fips140/ed25519/ed25519.go`, Go toolchain 1.26.8 | `verifyWithDom` uses the cofactorless equation and canonical S, performs no subgroup check on A and never decodes R | DSR-S06 |
| `ed25519-dalek` 2.2.0, `src/verifying.rs` | `verify_strict` decompresses R and rejects small-order A and R only; `is_torsion_free` is never called in the crate | DSR-S06 |
| `curve25519-dalek` 4.1.3, `src/edwards.rs` | `is_small_order` is `[8]P = identity`; `is_torsion_free` is `[L]P = identity` | DSR-S06 |
| `sage/pkg/agent/did/utils.go` and `pkg/agent/did/solana/` | Implementation forms two-segment `did:sage:ethereum:` and `did:sage:solana:` identifiers and ships a Solana package | DSR-D06 |
| `verification/traceability.json` | 45 requirements, 77 rules, 386 cases, all `planned_not_executed` | DSR-D07 |
| Repository-wide search | No occurrence of `Accept-Encoding`, RFC 6648, RFC 9562, RFC 9110, RFC 8446, RFC 3986, or any rate-limit, budget, quota, negative-cache, taint or provenance rule | DSR-S01, DSR-S04, DSR-S07, DSR-D03, DSR-D04, DSR-D05 |

## 7. Standards points confirmed correct

Recorded so that a later reader does not re-open them.

- The identifier is a syntactically valid DID. DID Core §3.1 gives
  `method-specific-id = *( *idchar ":" ) 1*idchar` with
  `idchar = ALPHA / DIGIT / "." / "-" / "_" / pct-encoded`. Multiple colon-separated
  segments are permitted, and SAGE's `segment` production is a strict subset of `idchar`
  with percent-encoding removed.
- Omitting `@context` from the resolved document is right for the declared media type.
  `@context` is a representation-specific entry of the JSON-LD representation
  (`application/did+ld+json`); the plain JSON representation carries no such
  requirement. The fetched DID Core §6.2 text did not state this exhaustively, so this
  item is confirmed by the representation-specific-entry definition rather than by a
  direct quotation of §6.2.
- `Content-Digest` is used with the correct semantics, over content as received rather
  than over a representation, and the `sha-256` key is the registered lowercase form.
- RFC 9421 parameter usage is correct: `tag` is an application-specific tag, `expires`
  is the defined parameter, the signer emits a fixed order while the verifier
  reconstructs the received order, and `Signature` uses the Structured Field byte
  sequence with padded standard base64.
- The mandatory signature suite is a registered RFC 9421 algorithm name.

## 8. Limits

No implementation was run, no vector regenerated, no cryptographic composition
analysed, no live exchange attempted. The attack shapes in §3 are derived from the
document text and were not reproduced. The implementation comparison covers DID
identifier formation and the two Ed25519 verification paths only; it is not an
implementation audit. Standards findings rest on the sections quoted in §6; no
exhaustive conformance audit of any cited standard was performed. This review is local
and advisory, by an assistant instance without organizational independence, and is not
an external audit, a formal proof or a security approval.
