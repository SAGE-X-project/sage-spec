# Pinned Go/Rust transport-envelope review

Status: **TRANSPORT-01 through TRANSPORT-06 assessed at bounded source and
existing-test scope; no complete parent-case verdict**. The
[91-rule index](core-gap-index.json) has 76 reviewed and 15 pending.
Normative `sage-spec` is pinned to
`44df132fee5925182018ce089dc82435cb353f8a`, Go `sage` to
`49379baadc6baec9ca8b4bb7d15bf43d65144bd7`, and Rust `rs-sage-core` to
`ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396`. No normative text, core
code or Inspector case verdict changed.

## TRANSPORT-01: common envelope schema

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

## TRANSPORT-02: complete request signature

[TRANSPORT-02](../spec/08-transport.md) requires an unpadded base64url
`payload` of at most 8 MiB decoded and signs the JCS request with only
`signature` removed, prefixed by `sage-wire-request|0.10.0` and a newline.
Sender, recipient, named key, version, context, metadata and payload all
remain within the signature. The algorithm follows the resolved named key;
HTTP method and target additionally need chapter 03 binding. A plain
handshake payload must be the chapter 04 JCS object, and a session payload
the complete chapter 05 binary record. Neither signing arbitrary bytes nor
validating a detached signature alone establishes those payload semantics.

| Boundary | Pinned source observation | Finding |
| --- | --- | --- |
| Go strict request paths | [`sign010` and `verifyWire010`](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/hpke/completion010.go#L180-L245) use the required request domain and remove only `signature` from the parsed object. The [plain receive path](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/hpke/completion010.go#L582-L595) compares the initiation body and selects the current signing key before verification. The [session receive path](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/hpke/record010.go#L214-L245) checks the participant tuple and current key before verifying the wire signature and opening the record. | **PARTIAL SIGNED SUBSET; COVERAGE GAP**. The fixed parser rejects optional signed `metadata` and `task_id`, so these permitted members cannot be authenticated in this path. Plain and session request payloads are capped at 16 KiB decoded, below the 8 MiB profile maximum. These checks do not prove that a host binds every logical tool/resource/executable input to the authenticated payload or selects the protected HTTP route. |
| Rust strict request paths | [`signed` and `verify_wire`](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/completion010.rs#L152-L173) use the same domain and whole parsed unsigned object. The [plain responder](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/completion010.rs#L438-L468) checks the canonical initiation and selected key. The [session opener](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/completion010/record010.rs#L231-L300) checks tuple and current key before signature and AEAD acceptance. | **PARTIAL SIGNED SUBSET; COVERAGE GAP**. The closed field lists omit permitted metadata/task fields, and the decoded payload cap is 16 KiB. The selected source paths do not show a complete application/tool-input binding or all HTTP host uses. |
| Legacy Go transport | The older [`WireMessage`](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/transport/wire.go#L23-L42) carries a signature and payload but lacks the required 0.10.0 identity, key, timing and version fields. | It cannot be treated as a 0.10.0 whole-request signature path merely because an application verifies its signature elsewhere. |

The pinned Inspector [TRANSPORT-02 evidence](https://github.com/SAGE-X-project/sage-inspector/blob/f104c8c3ce072e7a64d5a0092623e45ffb8d287b/docs/current-spec-transport02-evidence.md)
uses older normative revision `5bcf511e604579afa63f434013447f44b6858828`.
Its five fixtures include a valid signed request, changed recipient, changed
payload, removed metadata and a re-signed wrong-owner key URL. All five
complete cases remain `UNSUPPORTED` in both core adapters: neither exposes
`sage.transport.request.verify`. The separate generic signature run rejects
the three changed-byte cases, but accepts the re-signed wrong-owner key; it
does not check key ownership or full request admission. The fixed plain
payload is not a complete handshake. The evidence checker passed here, and
no old case result is transferred to the pinned normative revision.

At the pinned core revisions, selected Go completion, record and HTTP binding
tests passed. Rust's 102 completion tests, including bounded local loopback
runtime cases, passed with local socket access. These are implementation
tests, not complete TRANSPORT-02 cases. A complete verdict needs a
version-matched request verifier with valid optional metadata/task fields,
the specified payload range, independent signature and key-ownership cases,
and host-level evidence that authenticated payload values control protected
tool execution. Cross-layer JCS and HTTP binding findings remain in their
separate reviews.

## TRANSPORT-03: terminal response and request binding

[TRANSPORT-03](../spec/08-transport.md) requires one signed terminal response
for an internally retained exact signed request, with the complete-request
SHA-256, matching IDs/context/task presence, opposite identities and the same
plain or session mode. An application error still uses a signed response and
one of four closed codes; a lost response does not authorize a second result
or automatic redispatch.

| Boundary | Pinned source observation | Finding |
| --- | --- | --- |
| Go strict completion and session | The [plain completion path](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/hpke/completion010.go#L483-L560) retains the initiation, compares `message_id`, the JCS hash, identities, context, fresh ID/nonce and current signing key. The [session response methods](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/hpke/response010.go#L27-L160) retain the request, enforce terminal state, exact hash, four error codes and encrypted response mode. | **PARTIAL RESPONSE BINDING; PROFILE GAP**. These are distinct fixed handshake and session subsets. The plain completion accepts only success; neither subset carries optional `task_id`, and the 16 KiB response limit is below the profile maximum. There is no evidence that every host consumes results only after this verifier or reconciles a lost response without redispatch. |
| Rust strict completion and session | The [plain completion path](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/completion010.rs#L570-L635) checks a retained initiation and complete signed-request hash. The [session response methods](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/completion010/record010.rs#L361-L519) enforce a retained request, terminal state, closed error codes, session record and matching hash before releasing data. | **PARTIAL RESPONSE BINDING; PROFILE GAP**. The fixed subset has the same optional-field and size limitations. No universal host result-consumption or post-loss reconciliation boundary is proven. |

The pinned Inspector [TRANSPORT-03 evidence](https://github.com/SAGE-X-project/sage-inspector/blob/f104c8c3ce072e7a64d5a0092623e45ffb8d287b/docs/current-spec-transport03-evidence.md)
uses normative revision `5bcf511e604579afa63f434013447f44b6858828`.
Its seven complete cases are `UNSUPPORTED` in both primitive adapters. Generic
Ed25519 checks accept even signed responses with wrong request binding; this
does not supersede the strict source checks above or establish a new verdict.

## TRANSPORT-04: receive order and replay transaction

[TRANSPORT-04](../spec/08-transport.md) orders cheap schema/timing checks,
current-key and complete signature/HTTP proof checks, then session AEAD and
atomic id/nonce/sequence reservation before application admission. Rejection
must have no protected effect. An accepted ID remains spent even if an
application later rejects the message; replay state must survive the required
retention and restart boundary across HTTP, WebSocket and local adapters.

Both cores define a [Go `ReserveRecord` contract](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/hpke/record010.go#L10-L24)
and [Rust `reserve_record` contract](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/completion010.rs#L202-L229)
for durable ID/nonce denial with final validation under exclusive session
access. The [Go receiver](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/hpke/record010.go#L187-L265)
and [Rust receiver](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/completion010/record010.rs#L231-L315)
check tuple/current key and signature, then open AEAD with replay publication.
This is **partial source and test evidence**, not proof that every deployed
store is durable, all transports share the same replay namespace, or the
application has zero effects on every failure. The Inspector
[TRANSPORT-04 evidence](https://github.com/SAGE-X-project/sage-inspector/blob/f104c8c3ce072e7a64d5a0092623e45ffb8d287b/docs/current-spec-transport04-evidence.md)
is pinned to the older normative revision and keeps all five complete cases
`UNSUPPORTED`; its fixed failed-tag primitive tests only the AEAD operation.

## TRANSPORT-05: joint HTTP and envelope authentication

[TRANSPORT-05](../spec/08-transport.md) requires inner envelope and RFC 9421
HTTP signatures, equal DID/version and optional body projections, identical
key/time/nonce values, trusted HTTPS target and one acceptance transaction.
Neither a different signing key nor an unsigned fallback may repair a failed
outer binding.

The [Go strict HTTP verifier](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/hpke/http010.go#L310-L350)
and [Rust strict HTTP verifier](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/completion010/record010/http010.rs#L277-L294)
compare signed parameters and body/header projections using the selected
signing key. The [Go](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/hpke/http010.go#L376-L467)
and [Rust](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/completion010/record010/http010.rs#L322-L394)
session HTTP methods compose outer verification with inner signature/record
acceptance. **The strict path is partial**: its outer suite is Ed25519 only
while chapter 03 also permits P-256, its fixed envelope has no `task_id`, and
these core APIs do not prove that a trusted TLS host supplies the actual
method, target and authority or that every protected route uses the path.
The pinned Inspector [TRANSPORT-05 evidence](https://github.com/SAGE-X-project/sage-inspector/blob/f104c8c3ce072e7a64d5a0092623e45ffb8d287b/docs/current-spec-transport05-evidence.md)
is from the older normative revision: four representative complete cases
are `UNSUPPORTED` in both primitive adapters. Valid isolated signatures on
mismatched parameters do not prove joint admission.

## TRANSPORT-06: WebSocket and local carriage

[TRANSPORT-06](../spec/08-transport.md) requires a UTF-8 JSON envelope per
reassembled WebSocket text message over authenticated TLS, rejects binary and
compression, and caps the reassembled message at 16 MiB. Each message must
still pass the same expected-recipient and signature gates; a local adapter
claiming WireTransport must put those checks in an unavoidable trusted path.

The pinned Go [WebSocket server](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/transport/websocket/server.go#L209-L269)
has a 1 MiB default read limit and parses the legacy `WireMessage` before
calling an application handler. This path does not use the strict 0.10.0
envelope verifier or establish per-message current-key/replay checks. The
pinned Rust [completion module](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/COMPLETION010.md#L1-L28)
explicitly describes its carriage as no general WireTransport implementation;
no current WebSocket adapter is established by that source. The distinct MCP
binding does not supply chapter-08 WireTransport conformance. The pinned
Inspector [TRANSPORT-06 evidence](https://github.com/SAGE-X-project/sage-inspector/blob/f104c8c3ce072e7a64d5a0092623e45ffb8d287b/docs/current-spec-transport06-evidence.md)
keeps all five complete cases `UNSUPPORTED`; its event parser and detached
signature checks have no current core/TLS host. **The required host carriage
path remains unestablished.**

The four preserved Inspector evidence checkers passed here, but all use the
older normative revision. Selected Go completion, record, HTTP and legacy
WebSocket tests and Rust completion tests exercise bounded implementation
behavior; none promotes a complete parent case or crosses the host and
deployment boundaries identified above. The next unreviewed rule is `EVIDENCE-01`.
