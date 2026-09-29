# Independent standards-clause reference vectors

Status: **OFFLINE_REFERENCE_VECTORS_NOT_IMPLEMENTATION_RESULTS** for SAGE
`0.10.0`. The [fixed JSON fixture](vectors/standards-clauses-0.10.0.json)
has SHA-256 `9498da58d79e227295e623c3d4031c2525e68dfe4f8ddcaf1746631ff19572a5`.
It pins the normative source revision and source-file digests. The
[checker](check_standards_vectors.py) recomputes exact HTTP digest and
signature-base bytes, verifies four synthetic signatures using OpenSSL, and
checks the acceptance boundaries below. Neither the SAGE Go/Rust cores nor
the historical Go-generated vectors supplied the expected values. The
user-designated sibling `rfc9421` repository was consulted for comparison,
but its current builder and parser are not treated as an RFC conformance
oracle.

The HTTP body is the inert UTF-8 JSON `{"probe":"sage-0.10.0"}`, **not** a
valid SAGE transport envelope. Fixed time and nonce values make the bytes
reproducible for an offline unit seam; they do not model live freshness or
entropy. The fixture publishes public keys and signatures only. Ed25519
and P-256 request and request-bound response signatures are independently
checked against the exact RFC 9421 signature bases. The P-256 signatures
also use SAGE's low-S restriction. The response base includes the exact
received request `Signature` field through `"signature";req`.

| Planned Inspector parent | Reference assertion in this fixture | Further evidence needed |
| --- | --- | --- |
| `msca-http-ed25519` | Exact request/response bases and valid Ed25519 signatures | Valid inner envelope, active registry record, full HTTP and replay path |
| `msca-http-p256` | Exact request/response bases and valid low-S P-256 signatures | Optional-suite support or explicit UNSUPPORTED, then full path |
| `msca-http-private-alg` | Private suite named in HTTP `alg` is rejected before crypto or dispatch | Version-matched receiver verdict and generic remote response |
| `msca-http-only-private-key` | No matching HTTP signing key is available | Sender and receiver refusal without fallback |
| `msca-http-no-substitution` | Different inner and outer key URLs are rejected even when both keys are active | Full dual-signature and effect-boundary test |
| `msca-did-prefix-case` | Mixed-case DID scheme or method prefix is malformed | Independent parser and resolver test |
| `msca-did-url-prefix-case` | Mixed-case DID key URL prefix is malformed before key lookup | Independent key-selection test |
| `msca-private-suite-non-http-scope` | HTTP `alg` restriction does not by itself exclude a permitted non-HTTP private suite | Independent secp256k1/Keccak signature and full envelope checks |

An additional secp256k1 `EC` JWK records exact 32-byte `x` and `y`, the
uncompressed point, and an OpenSSL-parsed public key. It tests the key
representation described by RFC 8812 §3.1; it does not infer JOSE `ES256K`,
SAGE's private signing suite, a DID resolution result, or registry authority.

All eight Inspector parents remain **planned_not_executed**. This fixture is
partial source-derived evidence, not PASS for any whole parent, core
implementation conformance, an organizationally external audit, or a release.
The next gate is version-matched Go/Rust and Inspector execution of complete
positive and negative envelopes, HTTP request/response exchange, registry
and replay decisions, and the remaining standard-specific byte boundaries.

Source rules: [RFC 9421 §§2.4–2.5, 3.3.4, 3.3.6](https://www.rfc-editor.org/rfc/rfc9421.html),
the [IANA HTTP Signature Algorithms registry](https://www.iana.org/assignments/http-message-signature),
[RFC 7405 §2.1](https://www.rfc-editor.org/rfc/rfc7405.html#section-2.1), and
[RFC 8812 §3.1](https://www.rfc-editor.org/rfc/rfc8812.html#section-3.1).
