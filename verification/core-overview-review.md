# Pinned Go/Rust overview-rule review

Status: **four overview rule groups assessed at bounded source, existing-test,
or document-control scope; no full parent-case verdict**. The
[91-rule index](core-gap-index.json) now has 91 reviewed and 0 pending after
the [HTTP message-signature review](core-rfc9421-review.md) and
[HPKE review](core-hpke-review.md) and
[session review](core-session-review.md), [ID-04 review](core-gap-review.md),
and [Agent Card review](core-card-review.md).
This
review does not change normative text, core code, or the latest Inspector
conformance report. `OVERVIEW-01..04` are cross-layer requirements; matching
one parser or passing one test is insufficient to pass any complete group.

The pinned inputs are `sage-spec`
`44df132fee5925182018ce089dc82435cb353f8a`, Go `sage`
`49379baadc6baec9ca8b4bb7d15bf43d65144bd7`, and Rust `rs-sage-core`
`ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396`. The Inspector DID
[positive-control report](https://github.com/SAGE-X-project/sage-inspector/blob/f104c8c3ce072e7a64d5a0092623e45ffb8d287b/docs/did-prefix-observations.md)
is supporting evidence at its own revision, not a new overview verdict.

| Rule | Bounded evidence | Finding and remaining boundary |
| --- | --- | --- |
| [OVERVIEW-01](../spec/00-overview.md), grammar plus prose bounds | Both HTTP parsers require exact `0.10.0` and limit header sizes ([Go](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/hpke/http010.go#L90-L116), [Rust](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/completion010/record010/http010.rs#L77-L112)). The [identity review](core-gap-review.md) demonstrates that both general DID parsers reject a canonical 0.10.0 web DID and accept legacy syntax. | **PARTIAL SOURCE REVIEW WITH GRAMMAR GAP**. One syntactic boundary is demonstrably incompatible. This is not an audit of every ABNF, size, encoding, or semantic bound, nor does it establish how every consumer selects a parser. `OVERVIEW-01-P/N01` remain unexecuted as complete review cases. |
| [OVERVIEW-02](../spec/00-overview.md), dependency and conformance claim | The HTTP session paths combine a signed header, record and endpoint state ([Go](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/hpke/http010.go#L256-L303), [Rust](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/completion010/record010/http010.rs#L269-L304)). Guard APIs have separate authenticated execution acceptance ([Go](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/guard010/mcp.go#L115-L125), [Rust](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/guard010/mcp.rs#L65-L83)). | **PARTIAL SOURCE REVIEW**. Components exist, but no pinned whole-host assembly, dependency-complete version-matched test set, or evidence that historical vectors are excluded from a conformance claim was established. `OVERVIEW-02-P/N01` remain pending. |
| [OVERVIEW-03](../spec/00-overview.md), exact version and cross-layer agreement | Go and Rust HTTP headers require `0.10.0` ([Go](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/hpke/http010.go#L110), [Rust](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/completion010/record010/http010.rs#L104)); plain/session envelopes also require `0.10.0` ([Go plain](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/hpke/completion010.go#L199), [Go session](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/hpke/record010.go#L76), [Rust plain](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/completion010.rs#L102), [Rust session](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/completion010/record010.rs#L37)). Guard intent verifiers require the same version; the MCP **protocol** version is separately fixed at `2025-06-18` ([Go](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/guard010/mcp.go#L9-L18), [Rust](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/guard010/mcp.rs#L4-L10)). The HTTP signature base includes `x-sage-version` ([Go](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/hpke/http010.go#L299-L309), [Rust](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/hpke/completion010/record010/http010.rs#L212-L251)). | **PARTIAL SOURCE AND EXISTING-TEST REVIEW**. Local exact rejection is evidenced; no automatic fallback was seen in these entry points. Entire exchange agreement, every signing domain, negotiated host route and all `OVERVIEW-03-P/N01/N02/N03` cases remain unproven. Do not confuse the independent MCP transport version with the signed SAGE envelope version. |
| [OVERVIEW-04](../spec/00-overview.md), normative precedence | The pinned overview explicitly makes the specification normative and implementation citations informative. The [standards clause revision guard](check_standards_clause_revision.py) tracks normative source bytes; the [index builder](build_core_gap_index.py) pins the same normative revision and merely names core source candidates. The [crypto review](core-crypto-jcs-review.md) and [identity review](core-gap-review.md) report deviations without silently rewriting rules to match code. | **DOCUMENT CONTROL REVIEW**. Repository evidence respects precedence in these reviewed artifacts. It cannot prove that every future implementation decision or conformance claim will do so. `OVERVIEW-04-P/N01` need an independent document/process case review before a complete verdict. |

The existing Go `TestHTTPBinding010`, `TestHTTPAdmission010`,
`TestHTTPSerialization010` and `TestCompletion010Scenarios` exercise normal
exchange and bounded rejection scenarios. Rust has analogous
`http_session_scenarios`, `admission_bounds`, `serialization_vectors` and
`completion_scenarios`. These are implementation tests, not independent
`OVERVIEW` case executions; they must not be promoted to parent-case PASS.
At the pinned core revisions, the four named Go tests passed together with
`go test ./pkg/agent/hpke -run 'TestHTTP(Binding|Admission|Serialization)010|TestCompletion010Scenarios' -count=1`.
The four named Rust tests passed individually under `cargo test --lib` with
their corresponding name filters. The repository's five standards-clause
revision tests and its revision check also passed; that check still reports
`conformance: NOT_ESTABLISHED`.
Before a complete overview verdict, Inspector needs a version-matched
whole-host route through identity, signing, handshake, session, carriage and
execution admission, with explicit evidence of exact-version rejection and
no protected effect on each failed boundary. A separate evidence review must
check the conformance claim and normative precedence.
