# 2. JSON canonicalisation

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

| Object | Signed by | Section |
|---|---|---|
| HPKE response envelope (`v, task, ctx, kid, ephS, ackTagB64, ts, did, infoHash, exportCtxHash, enc, ephC`) | responder, detached `sigB64` | `04-hpke.md` §6 |
| A2A agent card with the `proof` member removed | card owner | `07-a2a.md` §3 |

RFC 9421 signature bases and session records are byte strings and do not use
JCS. The transport envelope (`08-transport.md`) is not signed as JSON; its
`payload` is signed as raw bytes.

Verifiers MUST canonicalise the received JSON themselves rather than trust
the sender's serialisation, and MUST remove exactly the members listed above
before canonicalising.
