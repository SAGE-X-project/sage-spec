# Pinned Go/Rust HTTP message-signature review

Status: **six MSG rule groups assessed at bounded source and existing-test
scope; no complete parent-case verdict**. The [91-rule index](core-gap-index.json)
has 28 reviewed and 63 pending after the [HPKE review](core-hpke-review.md).
This review preserves the normative
`sage-spec` revision `44df132fee5925182018ce089dc82435cb353f8a`, Go
`sage` revision `49379baadc6baec9ca8b4bb7d15bf43d65144bd7`, and Rust
`rs-sage-core` revision `ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396`.
It does not change core code, normative text or Inspector case outcomes.

The authoritative mechanism is [RFC 9421](https://www.rfc-editor.org/rfc/rfc9421.html)
with [RFC 9530](https://www.rfc-editor.org/rfc/rfc9530.html) for the digest
field; [SAGE chapter 03](../spec/03-rfc9421.md) fixes a narrower `sig1`,
coverage and freshness profile. The local `rfc9421` project is an informative
comparison, as recorded in the [reference assessment](rfc9421-reference.md).
The generic Go [`rfc9421`](https://github.com/SAGE-X-project/sage/tree/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/core/rfc9421)
and Rust [`rfc9421`](https://github.com/SAGE-X-project/rs-sage-core/tree/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/rfc9421)
modules have configurable, broader behavior. Their capabilities or defaults
cannot be substituted for the strict session HTTP path. Conversely, the strict
path does not prove every host uses it.

| Rule | Pinned source observation | Finding and remaining evidence |
| --- | --- | --- |
| [MSG-01](../spec/03-rfc9421.md), signature fields and suite | Both strict parsers enforce one `sig1`, six named parameters, the `sage-0.10.0` tag and `alg=ed25519` ([Go](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/hpke/http010.go#L189-L254), [Rust](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/completion010/record010/http010.rs#L165-L210)). Go's proof verifier also requires a 32-byte Ed25519 key; both signers emit only Ed25519 ([Go](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/hpke/http010.go#L343-L374), [Rust](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/completion010/record010/http010.rs#L584-L625)). | **SOURCE GAP for P-256 support**: `msca-http-p256` is a positive traceability case, but this path rejects `ecdsa-p256-sha256`. The Ed25519 subset has bounded positive and negative evidence only. Key authorization across all host entry points and complete `MSG-01-P/N01..N04` outcomes remain unproven. |
| [MSG-02](../spec/03-rfc9421.md), signed request components | Both strict paths fix the seven required request components in order, bind to a configured HTTPS target and exact `0.10.0`/digest, and use the trusted message target rather than Forwarded headers ([Go](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/hpke/http010.go#L36-L112), [Rust](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/completion010/record010/http010.rs#L57-L112)). | **PARTIAL SOURCE/TEST REVIEW**. The trusted HTTP transport must supply actual target and authority; merely deserializing caller-provided fields would not satisfy MSG-02. All `MSG-02-P/N01..N05` parent cases need version-matched, host-bound observation. |
| [MSG-03](../spec/03-rfc9421.md), request-bound signed response | The strict response base includes `;req` components and the original request signature. Both sessions retain private request context before verifying a response ([Go](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/hpke/http010.go#L289-L322), [Rust](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/completion010/record010/http010.rs#L212-L294)). Both reject status 204 in this path. | **PARTIAL SOURCE/TEST REVIEW**. Expected-peer and current-key gates need full receive-path and host evidence. Earlier Inspector [MSG-03 evidence](https://github.com/SAGE-X-project/sage-inspector/blob/f104c8c3ce072e7a64d5a0092623e45ffb8d287b/docs/current-spec-msg03-evidence.md) is pinned to an older spec revision and a different generic adapter; its verdicts are not transferred. |
| [MSG-04](../spec/03-rfc9421.md), bounded parsing before effect | The strict HTTP parsers reject duplicate critical fields, unknown/duplicate signature parameters, content coding and oversize fields; the raw HTTP/1.1 codec supplies additional framing checks ([Go](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/hpke/http010.go#L86-L112), [Rust](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/completion010/record010/http010.rs#L70-L112)). The session paths validate before their final replay reservation. | **PARTIAL SOURCE/TEST REVIEW**. These APIs cap content at 32 KiB, deliberately narrower than chapter 03's 16 MiB maximum; interoperability for larger otherwise-valid content is unresolved. A trusted TLS/framing adapter and zero application effects on every failure have not been established by these source checks. |
| [MSG-05](../spec/03-rfc9421.md), freshness and replay | HTTP parameter values are compared to inner envelope values ([Go](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/hpke/http010.go#L325-L341), [Rust](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/completion010/record010/http010.rs#L549-L581)). Both record paths enforce at most 300 seconds and require a replay store. Their inner-envelope check uses `now < expires`, so the HTTP + envelope composition cannot accept through an outer `expires+30` allowance. | **PARTIAL SOURCE/TEST REVIEW**. The stricter inner expiry boundary is documented, not assumed to be a safe or conformant resolution of every timing case. Durable retention through restart, 360-second quarantine, cross-transport nonce identity and concurrent copies require deployed-store evidence; `MSG-05-P/N01..N05` remain unproven as complete cases. |
| [MSG-06](../spec/03-rfc9421.md), error behavior | Strict open methods return internal errors and reject unsigned/204 success; signed session response APIs exist ([Go](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/hpke/http010.go#L428-L467), [Rust](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/completion010/record010/http010.rs#L356-L389)). | **HOST BOUNDARY NOT ESTABLISHED**. These core APIs do not themselves map every authentication/policy/replay failure to a generic HTTP 401 or prove that an unsigned response cannot authorize a retry or result in a host. Signed application-failure behavior and sensitive-log policy need host observation. `MSG-06-P/N01..N03` remain pending. |

At the pinned core revisions, the existing Go HTTP binding, admission,
serialization, handshake and framing unit tests passed as a group. Rust's
session, handshake and framing tests passed individually. These are controlled
implementation tests, not independent executions of all 35 MSG traceability
cases or a conformance claim. The current Inspector evidence is pinned to
earlier normative revisions; it retains its own `FAIL`, `PARTIAL`,
`UNSUPPORTED` and `NOT_RUN` labels.

Next, review the session rules in traceability order. Before promoting any MSG
parent-case verdict, Inspector needs exact-revision positive Ed25519 and P-256
paths, exact-component and request-context checks, bounded framing, a trusted
HTTP/TLS host, durable cross-transport replay and generic error mapping.
Preserve the observed P-256 gap until a core path and independent runtime case
demonstrate support.
