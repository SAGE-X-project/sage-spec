# 10. Resolution and the resolved document

Vectors: `vectors/did.json`. Requirements: `charter.md` R-4, R-14.

A registry record (`09-registry.md` §1) is projected into one document
shape, whatever kind of registry holds it. The document is what a verifier
reads and what ordinary identifier software can consume; it is also what
makes a registry that is not a blockchain a profile rather than a second
design.

## 1. The document

```json
{
  "@context": ["https://www.w3.org/ns/did/v1"],
  "id": "did:sage:web:agents.example.com:billing-bot",
  "controller": "did:sage:web:agents.example.com:billing-bot",
  "verificationMethod": [
    {
      "id": "did:sage:web:agents.example.com:billing-bot#key-1",
      "type": "JsonWebKey",
      "controller": "did:sage:web:agents.example.com:billing-bot",
      "publicKeyJwk": { "kty": "OKP", "crv": "Ed25519", "x": "…" }
    },
    {
      "id": "did:sage:web:agents.example.com:billing-bot#kem-1",
      "type": "JsonWebKey",
      "controller": "did:sage:web:agents.example.com:billing-bot",
      "publicKeyJwk": { "kty": "OKP", "crv": "X25519", "x": "…" }
    }
  ],
  "authentication": ["…#key-1"],
  "assertionMethod": ["…#key-1"],
  "keyAgreement": ["…#kem-1"],
  "service": [
    { "id": "…#agent", "type": "SageAgent", "serviceEndpoint": "https://…" }
  ]
}
```

Projection from the record:

| Record member | Document |
|---|---|
| `id` | `id` |
| `controller` | `controller`, expressed as an identifier where the profile has one, otherwise omitted |
| key entry with a signing `alg`, `state` `accepted` | a `verificationMethod` entry, referenced from `authentication` and `assertionMethod` |
| key entry with `alg` `x25519`, `state` `accepted` | a `verificationMethod` entry, referenced from `keyAgreement` |
| key entry with `state` `revoked`, or past `expires` | omitted from the document; its absence is what a verifier sees (§3) |
| `services` | `service` |
| `state` | resolution metadata, not the document (§3) |
| `version` | resolution metadata `versionId` |

Key material is a JSON Web Key, because the controlled identifier data model
defines no compact encoding for secp256k1 or X25519. The mapping from key
type to JSON Web Key members is in `11-registries.md` §3.

## 2. Resolving

```
resolve(identifier, options) -> (document, documentMetadata, resolutionMetadata)
```

1. Parse the identifier (`06-did-sage.md` §1). On failure return the error
   `id.malformed`.
2. Select the profile from the kind. If it is not implemented, return
   `id.unknown-kind`.
3. Observe the registry as the profile requires (`09-registry.md` §5). If it
   cannot be observed, return `record.unreachable`.
4. If there is no record, return `record.not-found`.
5. Project the record (§1) and return it with the metadata of §3.

A resolver MUST NOT return a document assembled from more than one
observation, and MUST NOT return a cached document except as
`09-registry.md` §5 permits.

## 3. Metadata

| Member | Meaning |
|---|---|
| `deactivated` | `true` when the record's `state` is `deactivated`. The resolution succeeds and the document is returned with no verification method |
| `created`, `updated` | times of the first and latest change, where the profile can supply them |
| `versionId` | the record's `version` |
| `canonicalId` | the identifier in normal form, when the caller used another form that this specification still accepts |
| `equivalentId` | other identifiers that denote the same agent, when a profile defines any |
| `observedAt` | the observation point the profile used, so that a caller can see what "now" meant |

A record that is `created` but not yet `active` resolves successfully with
metadata that says so; a verifier treats it as unusable
(`06-did-sage.md` §3).

## 4. Dereferencing a key

`dereference(did-url)` returns the verification method whose `id` equals the
URL, or `key.not-in-record`. A key that is revoked or expired is not in the
document, so dereferencing it fails, which is the behaviour a verifier
relies on.

## 5. Errors

Errors are problem details (RFC 9457). `type` is the diagnostic code of
`11-registries.md` §7 in the namespace
`https://sage-x-project.github.io/sage-spec/errors/`, `title` is a short
description, and `status` is the HTTP status when the resolver is reached
over HTTP:

| Code | Status |
|---|---|
| `id.malformed`, `id.unknown-kind` | 400 |
| `record.not-found` | 404 |
| `record.unreachable` | 502 |
| `key.not-in-record` | 404 |

A deactivated record is not an error: it is a successful resolution with
`deactivated` set.

## 6. HTTP binding

A resolver MAY be exposed over HTTP as
`GET /1.0/identifiers/{identifier}` over TLS, returning the document with
media type `application/did`, or the document and both metadata objects with
media type `application/did-resolution`. This binding is what lets a
registry that is not a blockchain be read by software that knows nothing
about SAGE.

## 7. Security considerations

| Threat | Defence |
|---|---|
| A-6: a resolver serves an old view | §2 forbids assembling from several observations and returns `observedAt`; caching rules are in `09-registry.md` §5 |
| A-2: a document is altered in transit | The transport is TLS, and the `web` profile additionally signs the record (`09-registry.md` §8) |
| A revoked key is still usable | Revoked keys are absent from the document, so dereferencing fails |
| Confusion between identifier forms | `canonicalId` names the normal form; there are no aliases (`06-did-sage.md` §2) |
