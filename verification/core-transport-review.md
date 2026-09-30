# Pinned Go/Rust transport-envelope review

Status: **TRANSPORT-01 assessed at bounded source and existing-test scope; no
complete parent-case verdict**. The [91-rule index](core-gap-index.json) has
39 reviewed and 52 pending. Normative `sage-spec` is pinned to
`44df132fee5925182018ce089dc82435cb353f8a`, Go `sage` to
`49379baadc6baec9ca8b4bb7d15bf43d65144bd7`, and Rust `rs-sage-core` to
`ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396`. No normative text, core
code or Inspector case verdict changed.

[TRANSPORT-01](../spec/08-transport.md) requires a closed JSON envelope with
the named common fields, optional members omitted rather than null, canonical
UUIDv4 and unpadded base64url, and exact metadata key, value, entry-count and
JCS-byte bounds. The same schema permits `context_id`, `task_id`, `role`,
`session_id` and `metadata` when their conditions hold. Request/response body
limits and signature domains are assessed in later transport rules; this pass
checks the common schema without treating a generic signature check as an
envelope verdict.

| Boundary | Pinned source observation | Finding |
| --- | --- | --- |
| Go strict 0.10.0 carriage | [`rawObject010`](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/hpke/completion010.go#L118-L163) rejects duplicate, null, missing and extra top-level members and caps bytes at 32 KiB. The [plain parser](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/hpke/completion010.go#L185-L224) checks exact version, role, UUIDv4, DID/key shape, timing and canonical binary fields. The [session parser](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/hpke/record010.go#L51-L106) also fixes a closed field set. | **PARTIAL STRICT SUBSET; SCHEMA GAP**. Both strict paths require `context_id` and `role` and reject otherwise valid omission. Neither accepts optional `task_id` or `metadata`, so the specified metadata limits and permitted presence cannot be demonstrated. The 32 KiB input and 16 KiB decoded-body caps exclude otherwise valid larger 0.10.0 envelopes. Their closed-member and canonical-binary checks remain useful bounded evidence. |
| Rust strict 0.10.0 carriage | [`raw`](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/completion010.rs#L41-L91) rejects duplicate/null/extra fields and caps input at 32 KiB. The [plain parser](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/completion010.rs#L92-L137) checks version, UUIDv4, DID/key shape, timing and re-encoded base64url equality; the [session parser](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/completion010/record010.rs#L17-L74) uses the same fixed common fields. | **PARTIAL STRICT SUBSET; SCHEMA GAP**. As in Go, `context_id`/`role` are compulsory and `task_id`/`metadata` are absent. The 32 KiB envelope and 16 KiB decoded-record bounds are narrower than the chapter-wide allowance. No complete metadata acceptance/rejection path is established. |
| Go legacy HTTP/WebSocket carriage | [`WireMessage`](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/transport/wire.go#L23-L42) lacks required 0.10.0 `version`, `recipient`, `kid`, times, nonce and encoding. The [HTTP handler](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/transport/http/server.go#L101-L149) uses ordinary `json.Unmarshal` into that struct; the [WebSocket handler](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/transport/websocket/server.go#L229-L255) uses `ReadJSON`. | **SEPARATE LEGACY PATH, NOT A 0.10.0 VERIFIER**. These decoders do not enforce the closed SAGE schema or canonical unpadded base64url. Their body-size and identity-header checks are not substitutes for common-envelope verification. This source review does not assert that every host routes through the legacy path. |

The pinned Inspector [TRANSPORT-01 evidence](https://github.com/SAGE-X-project/sage-inspector/blob/f104c8c3ce072e7a64d5a0092623e45ffb8d287b/docs/current-spec-transport01-evidence.md)
uses older normative revision `5bcf511e604579afa63f434013447f44b6858828`.
Its five independent envelopes cover a valid request, unknown member, invalid
UUID variant, padded payload and 1025-byte metadata value. Both primitive
adapters report all five complete cases `UNSUPPORTED` because neither exposes
`sage.transport.envelope.verify`; generic Ed25519 verification accepts their
signatures but does not check schema. The preserved evidence checker passed in
this review. No earlier result is transferred to the current normative revision.

At the pinned core revisions, selected Go strict completion/record and legacy
HTTP transport tests passed, and the Rust completion scenario passed. These
exercise implementation paths and safe local runtime behavior, not all
TRANSPORT-01 cases. A complete verdict needs an exact-revision verifier that
accepts the permitted optional fields, enforces metadata and all common
limits, selects the intended trusted receive path, and checks independent
positive/negative cases through the host without protected effects on failure.

The next unreviewed rule is `TRANSPORT-02`.
