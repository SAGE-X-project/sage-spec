# 9. The registry and the agent lifecycle

Vectors: `vectors/did.json`, `vectors/registry.json`. Requirements:
`charter.md` R-3 to R-13.

A registry holds records that bind an identifier to keys. This chapter
states what every registry must offer, what a verifier may conclude from a
record, and how each kind of registry meets the model. Nothing here assumes
a blockchain; §6 to §8 are the profiles that say how three kinds do it.

## 1. The record

| Member | Content |
|---|---|
| `id` | the identifier (`06-did-sage.md`) |
| `controller` | the party authorised to change the record, in a form the profile defines |
| `keys` | one or more key entries, below |
| `services` | zero or more endpoints, each with a type and a URL |
| `state` | `created`, `active` or `deactivated` |
| `version` | a value that increases on every change, used as the version identifier in resolution |

A key entry:

| Member | Content |
|---|---|
| `name` | the fragment that names this key within the record, unique in the record |
| `alg` | a signature algorithm name, or `x25519` for a key-agreement key (`11-registries.md` §2, §3) |
| `key` | the public key bytes in the encoding of `11-registries.md` §3 |
| `proof` | the proof of possession (§4) |
| `state` | `accepted` or `revoked` |
| `expires` | optional; after this time the key MUST NOT be used |

A registry MUST NOT report a key as `accepted` unless it has verified the
proof for that key. A registry that cannot verify proofs for an algorithm
MUST refuse keys of that algorithm rather than record them unverified.

## 2. What a verifier reads

A verifier needs exactly this, and a profile MUST be able to answer it:

1. given an identifier, the key entries with `name`, `alg`, `key` and
   `state`;
2. the record's `state`;
3. for a handshake, the key-agreement key: the accepted, unexpired entry
   whose `alg` is `x25519`. Where a record has several, the one whose
   `name` sorts first is used.

`services` and other members are advisory: a verifier MUST NOT make an
authentication decision from them.

## 3. Operations and lifecycle

```
            create                 activate
   (none) ──────────► created ───────────────► active
                         │                       │
                         │ deactivate            │ deactivate
                         ▼                       ▼
                    deactivated ◄────────────────┘

   while active: add key, revoke key, authorise
```

| Operation | Rule |
|---|---|
| create | Binds the identifier to an initial key set and a controller. The registry MUST refuse an identifier that already has a record. The claim MUST bind the identifier, the keys and the controller before it is visible to others; a profile that cannot hide a claim states what it offers instead (§6 to §8). The record enters `created` |
| activate | Moves `created` to `active`. A profile MAY require a delay or a second authorisation. Only an `active` record is usable |
| add key | Adds a key entry with its own proof (§4) to an `active` record |
| revoke key | Sets a key entry to `revoked`. The entry MUST be kept, so that a verifier can tell a revoked key from one that was never present. A registry MUST refuse to revoke the last accepted signing key of an `active` record; deactivate the record instead |
| deactivate | Moves the record to `deactivated`. The record MUST remain readable |
| authorise | Names another party who may perform the operations above |

A `deactivated` record is never reactivated. The identifier is never
reassigned.

## 4. Proof of possession

One proof, for every registry and every key type. The challenge binds the
registry, the agent, the algorithm and the key, so that a proof is valid in
exactly one place:

```
challenge = "sage-pop-v1"
          ‖ len16(registry-id) ‖ registry-id
          ‖ len16(agent-id)    ‖ agent-id
          ‖ len16(alg)         ‖ alg
          ‖ len16(key)         ‖ key
```

`registry-id` and `agent-id` are the components of `06-did-sage.md` §1 as
ASCII; `alg` is the name from `11-registries.md` §2 or §3 as ASCII; `key`
is the public key bytes.

- For a signing key, `proof` is a signature over `challenge` made with that
  key, using the digest and encoding its algorithm prescribes
  (`01-crypto.md`).
- For a key-agreement key, which cannot sign, `proof` is a signature over
  the same `challenge` made with an accepted signing key of the same
  record, and the entry records which key made it.

A verifier of a record, and the registry itself, recompute `challenge` and
check `proof`. A failed proof means the key is not accepted (`pop.bad`).

## 5. Observation, caching and immediacy

`charter.md` R-9 requires that revocation take effect immediately.

1. A verifier MUST decide a key's `state` and the record's `state` from the
   registry state observed at the time of verification, as the profile
   defines observation.
2. A verifier MAY remember, without limit, that a key is `revoked` or that a
   record is `deactivated`. A verifier MUST NOT remember that a key is
   `accepted` or that a record is `active` beyond the observation point;
   caching MUST NOT extend the usable life of a key. Negative caching only.
3. If the registry cannot be observed, verification fails
   (`record.unreachable`). A verifier MUST NOT fall back to an earlier
   positive result.
4. A profile states the observation point, the cost of an observation, and
   the delay between a change being submitted and becoming observable. That
   delay is a property of the registry, not of this specification; the
   requirement binds the verifier, which grants no grace of its own.

## 6. Profile: `eip155`

Locator: two segments, the CAIP-2 chain reference and the address of the
registry contract, both lower-case.

| Aspect | Rule |
|---|---|
| Identifier | `agent-id` is assigned by the registry when the record is created, and is stable for the life of the record |
| Controller | an account address on the same chain |
| Key algorithms | `ed25519`, `es256k`, `ecdsa-p256-sha256`, `x25519`, subject to what the contract can verify; a contract that cannot verify an algorithm MUST refuse it (§1) |
| Claim | two steps: a commitment to the identifier, the key set and the controller, then the revealing transaction. The commitment MUST include the chain reference and the registry address, so it cannot be replayed elsewhere |
| Activation | a delay set by the registry, after which the controller activates |
| Authorisation | the controller, or an operator the controller named |
| Observation | the record's `state` and each key's `state` are read at the most recent block; key material and a newly created record are read at the most recent finalised block. A reorganisation then withdraws a revocation only in the safe direction: the verifier over-rejects rather than accepts a revoked key |
| Cost and latency | published as measurements per deployed registry (`charter.md` R-13) |

## 7. Profile: `solana`

Locator: two segments, the CAIP-2 chain reference and the program address.
The rules of §6 apply with these differences: the controller is an account
on that chain; the claim is a single instruction, because the ordering
guarantees the chain offers make a separate commitment unnecessary, and the
profile states this explicitly; observation uses the confirmed and finalised
commitments in place of the most recent and finalised blocks.

This profile is not yet implemented by any core and is marked provisional
until it passes the vectors (`PROCESS.md` stage 3).

## 8. Profile: `web`

A registry that is not a blockchain. Locator: one segment, a domain name.

| Aspect | Rule |
|---|---|
| Record location | `https://<domain>/.well-known/sage/agents/<agent-id>`, retrieved over TLS |
| Record encoding | the resolved document of `10-resolution.md`, with the additional members `issued` and `expires` |
| Controller | control of the domain, demonstrated by serving the record at that location under a certificate valid for it |
| Claim | publication. A profile of this kind cannot hide a claim before it is visible, so an operator that needs protection against a racing claim MUST use a registry kind that can |
| Activation | a record is `active` when it is served with `state` equal to `active` |
| Revocation | serving a record in which the key entry is `revoked`, or serving `state` equal to `deactivated` |
| Observation | the verifier retrieves the record for the verification it is performing. `expires` MUST NOT be more than 300 seconds after `issued`, and a verifier MUST reject a record whose `expires` has passed. A verifier MUST NOT reuse a retrieved record for a later verification |
| Cost and latency | one retrieval per verification; publication takes effect as soon as the new record is served |

The record MUST be signed by an accepted signing key of the record itself,
over the canonical form of `02-jcs.md` with the signature member removed, so
that a retrieval that is intercepted cannot substitute keys. The first
record for an identifier is therefore self-asserted: this profile binds the
identifier to the domain, and the domain to the keys, but it cannot prove
that the domain holder is anyone in particular. A deployment that needs
more MUST use a registry kind that records a controller independently.

## 9. Security considerations

| Threat | Defence |
|---|---|
| A-5: racing a claim | The two-step claim of §6; `web` cannot offer this and says so |
| A-4: registering another party's key | The proof of §4, checked by the registry, and refused algorithms rather than unverified ones |
| A-6: a stale view | The observation rules of §5, negative caching only, and rejection when unreachable |
| A-7: a key that outlives its use | Revocation with the entry kept, and optional expiry per key |
| Loss of control of a registry | Out of scope (`charter.md` N-5); a deployment that distrusts a registry must not use identifiers from it |

An operator that revokes a key SHOULD also rotate any session established
with it; this specification does not end live sessions on revocation, and
`05-session.md` bounds their lifetime instead.
