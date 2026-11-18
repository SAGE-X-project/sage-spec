# 2. JSON canonicalisation

Version: 0.9.0-draft.1.1. Finalizes 0.9.0-draft.1 with the errata in [../docs/errata-0.9.0-draft.1.md](../docs/errata-0.9.0-draft.1.md).

Vectors: `vectors/jcs.json`. Go source: `pkg/agent/crypto/jcs/jcs.go`.

## 1. Algorithm

SAGE uses the JSON Canonicalization Scheme of RFC 8785 without deviation:

- object members sorted by their UTF-16 code units;
- strings escaped as ECMAScript `JSON.stringify` does (`\"`, `\\`, `\b`,
  `\f`, `\n`, `\r`, `\t`, other control characters as `\u00XX` lower-case
  hex, everything else literal UTF-8);
- numbers serialised as ECMAScript `Number::toString` (so `4.50` becomes
  `4.5`, `1E30` becomes `1e+30`, `-0` becomes `0`, integers above 2^53 lose
  precision exactly as in JavaScript);
- no whitespace;
- literals `null`, `true`, `false`.

The first two vectors are the RFC's own examples; their outputs equal the
RFC's expected text.

## 2. Where canonicalisation is required

| Object | Signed by | Member removed before JCS | Section |
|---|---|---|---|
| HPKE response envelope | responder | `sigB64` | `04-hpke.md` §6 |
| A2A agent card | card owner | `proof` | `07-a2a.md` §3 |
| `WireMessage` | sender | `signature` | `08-transport.md` §1 |
| `WireResponse` | responder | `signature` | `08-transport.md` §2 |

RFC 9421 signature bases and session records are byte strings and do not use
JCS. The transport envelopes `WireMessage` and `WireResponse` are signed as
JSON: the signing input is a label of `08-transport.md` §6 followed by the JCS
bytes of the envelope without `signature` (errata E08-01 to E08-03).

Verifiers MUST canonicalise the received JSON object themselves, after
removing exactly the one top-level member named for that object. No nested
member is removed. The values the verifier acts on MUST come from the same
parsed object it canonicalised.

A JSON text that is verified against a signature (HPKE init and response,
agent card, `WireMessage`, `WireResponse`) MUST be rejected if any object in
it, at any depth, has two members with the same name (compared as sequences of
Unicode code points after unescaping).

Member names are matched exactly (case-sensitive). An object that contains two
names equal under ASCII case folding, or a name that differs from a defined
member name only in case, MUST be rejected.

Signed JSON MUST be well-formed RFC 8259 UTF-8 without a byte order mark, with
one top-level value and nothing after it except insignificant whitespace. An
escape that produces an unpaired surrogate (`\ud800` not followed by a low
surrogate, or a lone low surrogate) MUST be rejected; it MUST NOT be replaced
with U+FFFD.

The SAGE signed objects (HPKE envelopes, agent card, `WireMessage`,
`WireResponse`) contain no JSON numbers in 0.9.0-draft.1.1; times are
RFC 3339 strings (the transport `created` member is defined in
`08-transport.md` §1). A verifier MUST reject a signed object that contains a
number.

A verifier MUST reject a signed JSON text nested deeper than 16 levels, with
an object of more than 256 members or an array of more than 256 elements, or
larger than 64 KiB for the HPKE envelopes and the agent card. `WireMessage`
and `WireResponse` are bounded by the 1 MiB transport limit
(`08-transport.md`, errata E08-10) instead, because their `payload` or `data`
carries application bytes. An agent card MUST NOT have more than 32
`publicKey` or 32 `service` entries.

## Changes from 0.9.0-draft.1

- E02-01 (a) Which members are removed before verifying (resolved SN-3)
- E02-02 (b) Duplicate member names are rejected
- E02-03 (b) One parse, exact names
- E02-04 (b) Strict text: UTF-8, escapes, trailing data
- E02-05 (b) Numbers in signed SAGE objects (updated for SN-2)
- E02-06 (b, b-limit) Size and depth of signed JSON
- E02-07 (a) What the transport signature covers (updated for SN-3)
