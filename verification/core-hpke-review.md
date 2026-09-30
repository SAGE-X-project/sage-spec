# Pinned Go/Rust HPKE handshake review

Status: **six HPKE rule groups assessed at bounded source and existing-test
scope; no complete parent-case verdict**. The [91-rule index](core-gap-index.json)
has 34 reviewed and 57 pending after the [session review](core-session-review.md).
Normative `sage-spec` revision
`44df132fee5925182018ce089dc82435cb353f8a` remains fixed; Go `sage` is
`49379baadc6baec9ca8b4bb7d15bf43d65144bd7` and Rust `rs-sage-core` is
`ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396`. No normative text, core code
or Inspector case verdict changed.

The HPKE construction is specified by [RFC 9180](https://www.rfc-editor.org/rfc/rfc9180.html)
and the combiner uses [RFC 5869](https://www.rfc-editor.org/rfc/rfc5869.html).
[SAGE chapter 04](../spec/04-hpke.md) selects one HPKE suite and defines
additional signed-envelope, transcript, E2E, ACK and state obligations. A
matching HPKE exporter alone does not authenticate a peer or establish a
session. The general historical handshake and `vectors/hpke.json` are not
0.10.0 conformance evidence.

| Rule | Pinned source observation | Finding and remaining evidence |
| --- | --- | --- |
| [HPKE-01](../spec/04-hpke.md), suite and authenticated prerequisites | Go's [HPKE helper](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/crypto/keys/x25519.go#L353-L406) selects Base X25519/HKDF-SHA256/ChaCha20-Poly1305. Rust's [KEM helper](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/common.rs#L18-L55) selects the same. Both strict handshake endpoints obtain selected current signing and KEM keys before responding ([Go](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/hpke/completion010.go#L573-L604), [Rust](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/completion010.rs#L449-L477)). | **PARTIAL SOURCE/TEST REVIEW**. Exact suite and key-role selection are visible; trusted registry provenance, fresh context uniqueness across restarts, and every current-key failure need host and durable-state evidence. Base mode itself is not sender authentication. |
| [HPKE-02](../spec/04-hpke.md), initiation and domains | Both [Go](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/hpke/derivation010.go#L133-L190) and [Rust](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/derivation010.rs#L120-L176) require a closed initiation, exact version/suite/combiner and fixed byte lengths, then derive `info` and `exportCtx` from B. Fresh initiation helpers produce HPKE and separate X25519 ephemerals. | **PARTIAL SOURCE/TEST REVIEW**. Primitive domain validation does not establish that all names, nonce and selected keys are authenticated by the outer envelope, nor that every host uses the strict constructor. All five HPKE-02 cases remain unproven as complete receive-path cases. |
| [HPKE-03](../spec/04-hpke.md), transcript and combiner | The [Go schedule](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/hpke/schedule010.go#L19-L71) and [Rust schedule](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/schedule010.rs#L17-L75) use transcript-salted HKDF extract, versioned expansion and HMAC ACK; both reject a zero direct X25519 result. Fresh responder helpers generate an E2E key and UUIDv4 handle. | **PARTIAL SOURCE/TEST REVIEW**. Matching local schedule tests do not prove independence of both ephemeral contributions in every production setup, every HPKE KEM all-zero rejection at the library boundary, or the full five-case transcript/adversarial-state matrix. |
| [HPKE-04](../spec/04-hpke.md), signed completion | Both completion paths demand the closed five-field payload, byte-for-byte initiation echo, current responder key, outer wire signature, versioned completion signature and constant-time ACK check before establishing a session ([Go](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/hpke/completion010.go#L483-L560), [Rust](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/completion010.rs#L595-L654)). | **PARTIAL SOURCE/TEST REVIEW**. The existing synthetic completion scenarios exercise positive and rejection behavior. A version-matched independent Inspector case must still prove both signatures and pending-request ownership at the actual host boundary. |
| [HPKE-05](../spec/04-hpke.md), lifecycle and first-record confirmation | The endpoint and record implementations have provisional responder state, monotonic/UTC deadline checks, final replay reservation and post-reservation expiry recheck ([Go](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/hpke/completion010.go#L352-L469), [Rust](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/completion010.rs#L700-L799)). Existing lifecycle and record tests exercise selected transitions. | **PARTIAL SOURCE/TEST REVIEW**. Complete confirmation, first unseen sequence below 1000, concurrent duplicate behavior, delayed durable commit, restart denial and separate later execution authorization require one stateful, version-matched Inspector assembly. No passed primitive test is promoted to a full 11-case HPKE-05 verdict. |
| [HPKE-06](../spec/04-hpke.md), admission and diagnostics | Both initiation parsers and signed-wire envelope parsers cap decoded handshake content at 16 KiB ([Go](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/hpke/derivation010.go#L43-L55), [Rust](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/derivation010.rs#L20-L41)). Closed schemas and fixed binary lengths are checked before cryptographic derivation. | **PARTIAL SOURCE REVIEW; HOST BOUNDARY PENDING**. The caller still must enforce generic authentication failures, secret-free logs, rate limits without identity assertions and no unsigned cookie path. The five HPKE-06 cases need host/log observations. |

At the pinned revisions, Go's complete `pkg/agent/hpke` package test passed.
Rust's 124 `hpke::` library tests included bounded TCP loopback cases. The
first sandboxed attempt passed 110 and failed 14 because local socket creation
was denied. The same suite passed **124/124** with local loopback access.
These implementation tests and the earlier Inspector
[HPKE evidence](https://github.com/SAGE-X-project/sage-inspector/blob/f104c8c3ce072e7a64d5a0092623e45ffb8d287b/docs/current-spec-hpke03-evidence.md)
are not complete parent-case results at the pinned normative revision.

The session rules are assessed in the linked review; the next unreviewed rule
is `ID-04`. Before promoting HPKE cases,
Inspector needs the exact-revision whole handshake and first-record assembly,
durable replay/clock fault boundaries, current registry binding and independent
schedule vectors, while preserving `FAIL`, `UNSUPPORTED` and `NOT_RUN` where
the required behavior is absent.
