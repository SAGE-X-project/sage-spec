# Wire envelope and HTTP binding reference bytes

Status: **OFFLINE_REFERENCE_NOT_PROTOCOL_CONFORMANCE** for SAGE `0.10.0`.
The [fixed fixture](vectors/wire-http-binding-0.10.0.json) has SHA-256
`17de2b6ca0eaf71cb7e1ad4c569b2a7b0e235f1ba9992c05fcacde86fbcf6a63`.
It records the exact normative source-file digests. The
[checker](check_wire_http_vectors.py) recomputes the wire signature inputs,
RFC 9421 request and request-bound response bases, HTTP Content-Digests,
header/body identity, time and nonce equality, and the response's hash of the
complete signed request. OpenSSL independently verifies four Ed25519
signatures. The fixture contains public keys, not private keys.

The request is a complete `plain` SAGE wire envelope carrying a
chapter 04 initiation-shaped payload. Its HTTP signature covers the required
request components. The response is a distinct complete `plain` wire envelope
with `success=false`, `error=unavailable`, and empty data; its outer signature
also covers the exact request `Signature` field. Both bodies are actual UTF-8
JSON bytes, so the digests cover received content rather than an inert probe.
All fixture strings use a restricted printable ASCII subset for which the
checker's sorted, compact JSON serialization equals RFC 8785 JCS. This checker
does not claim general RFC 8785 parser conformance.

The [mutation tests](test_wire_http_vectors.py) cover changed initiation
content, invalid inner signature, altered HTTP target, outer key substitution,
changed request hash, request signature field substitution, context mismatch,
duplicate JSON members, source drift, and evidence-status promotion. They
test local reference verification; they do not send traffic or exercise
attack tooling.

No HPKE SetupBase or chapter 05 schedule was performed. The initiation's
`enc` and `ephC` are correctly sized X25519 public values, but this package
does not establish that `enc` is a valid encapsulation to a registered
recipient KEM key. The signed error response does not establish a session.
Registry resolution, current proven-key status, live clock and replay state,
application dispatch, Go/Rust implementation behavior, and the Inspector
parent verdicts remain untested. In particular, the earlier
[standards-clause vectors](standards-vectors.md) and these bytes together do
not promote any Inspector case to PASS.

The next implementation gate is Inspector consumption of these fixed bytes
against version-matched Go/Rust APIs with explicit PASS, FAIL, UNSUPPORTED,
and NOT_RUN outcomes. Full positive HPKE completion and authenticated session
exchange need their own independent schedule vectors and state tests.
