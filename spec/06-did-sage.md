# 6. The did:sage method

Vectors: `vectors/did.json`. Requirements: `charter.md` R-1, R-2, R-8, R-14.

An agent is named by an identifier that says which registry holds its
record. The registry model and the operations are in `09-registry.md`; the
document an identifier resolves to is in `10-resolution.md`.

## 1. Syntax

```abnf
did-sage     = "did:sage:" registry-id ":" agent-id
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

## 2. Uniqueness and equality

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

## 3. Which key verifies a message

A signature names its key with the `keyid` parameter, which MUST be a
`did-url` with a fragment. A verifier:

1. parses `keyid` into an identifier and a key name, rejecting a `keyid`
   without a fragment (`sig.malformed`);
2. resolves the identifier (`10-resolution.md`) and rejects if the record is
   unknown, not active, or unreadable (`record.not-found`,
   `record.inactive`, `record.unreachable`);
3. finds the key with that name and rejects if there is none
   (`key.not-in-record`);
4. rejects if that key is not accepted, is revoked, or has expired
   (`key.unproven`, `key.revoked`);
5. rejects if the key's algorithm does not match the `alg` parameter
   (`sig.alg-mismatch`);
6. verifies the signature with that key alone. A verifier MUST NOT try
   other keys in the record.

Where a protocol step needs a key but no `keyid` names one, for example the
key-agreement key used to start a handshake, the record's key for that
purpose is selected by the rule in `09-registry.md` §2.

## 4. Operations

Creating, activating, adding a key, revoking a key and deactivating a
record are defined once, in `09-registry.md` §3, and are the same for every
kind of registry. A profile states how each operation is carried out and
who is authorised.

## 5. Relationship to the identifier standards

`did:sage` is a decentralised identifier method. Its syntax conforms to the
identifier grammar of the W3C specification, its resolution contract is in
`10-resolution.md`, and the document it produces uses the controlled
identifier data model. The method name is to be registered in the W3C
method registry before `1.0.0`.

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

## 7. Change from `1.0.0-draft.1`

The earlier form was `did:sage:<chain>:<identifier>`, where the network was
configuration rather than part of the identifier. Two registries could
therefore issue the same identifier, and a proof of possession made against
one network was byte-identical for another. Every identifier changes; there
is no compatibility rule, because no deployment may rely on the earlier
form.
