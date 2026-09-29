# Pinned Go/Rust clause gap review

Status: **28 of 91 rule groups reviewed at a bounded source or document level; 63 pending**.
This began as the first implementation-gap pass after the 0.10.0 standards revision,
not an implementation conformance verdict or a change to normative text. The
[machine-readable index](core-gap-index.json) names **every** rule group in
`traceability.json`, its source and case count, a starting source location in
each core, and its review state. The index is checked against exact
traceability bytes. A source candidate is a place to start reading, not a
claim that the code implements the rule.

The [crypto and JCS review](core-crypto-jcs-review.md) adds nine bounded rule
assessments, the [overview review](core-overview-review.md) assesses four
cross-layer rules, the [HTTP message-signature review](core-rfc9421-review.md)
assesses six MSG rules, and the [HPKE review](core-hpke-review.md) assesses six
handshake rules. The identity findings below remain attached to the same
pinned core revisions.

| Input | Pinned revision |
| --- | --- |
| `sage-spec` | `44df132fee5925182018ce089dc82435cb353f8a` |
| Go `sage` | `49379baadc6baec9ca8b4bb7d15bf43d65144bd7` |
| Rust `rs-sage-core` | `ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396` |

## Reviewed identity rules

| Rule | Go source and observation | Rust source and observation | Finding |
| --- | --- | --- | --- |
| [ID-01](../spec/06-did-sage.md) exact DID and key-URL syntax | [`did.ParseDID`](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/did/manager.go#L324-L341) splits a legacy chain form; `ValidateDID` calls it. [`registry010.Gate.validDID`](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/registry010/gate.go#L132-L139) checks an exact configured registry prefix but is not the public parser. | [`did::parse_did`](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/did/mod.rs#L66-L89) parses the legacy chain form. [`RegistryGate::valid_did`](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/registry010/mod.rs#L189-L201) is a separate configured-prefix admission check. | **GAP** in both public parsers. The canonical `did:sage:web:agents.example.com:alice` is rejected; an old chain form and a fragment presented as a DID are accepted. Neither primitive adapter exposes the new DID URL operation. The gate's scoped positive behavior must not be used to relabel the public parser or complete ID-01 as conformant. |
| [ID-02](../spec/06-did-sage.md) uniqueness and no aliases | [`ParseChain`](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/did/manager.go#L310-L322) accepts `eth`, `sol` and case-insensitive chain strings; `ParseDID` joins extra `:` segments into the identifier. | [`parse_chain`](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/did/mod.rs#L51-L59) has the same aliases and case folding; `parse_did` leaves extra colons in the identifier. | **GAP** in the legacy public parsing surface. The 0.10.0 identity includes a complete kind/locator and forbids alias inference. This finding does not determine whether any separately configured Registry Source prevents cross-registry collisions. |
| [ID-03](../spec/06-did-sage.md) exact key selection | [`registry010.Gate.SelectWithTime`](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/registry010/gate.go#L240-L273) requires an active record and exactly `did#name` for an accepted Ed25519 key; no alternate signing key is tried there. | [`RegistryGate::select_with_time`](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/registry010/mod.rs#L285-L314) has the same scoped exact selection. | **PARTIAL SOURCE REVIEW**. Both gates depend on a trusted validating Source and configured registry; this pass did not establish a full DID URL parser, expected-peer binding, signer role across every message type, final signature verification or live host assembly. |

The [bounded parser observations](identity-parser-observations.json) ran the
existing Inspector Go and Rust adapters against both pinned cores. Each
adapter was built from its named core and is identified by an executable
SHA-256. Six harmless DID inputs were used; per core **five disagree with the
0.10.0 expectation and one agrees**:

| Input | 0.10.0 expected | Both core adapters |
| --- | --- | --- |
| Canonical web DID | ACCEPT | REJECT |
| `did:sage:ETH:0xabc` alias/case | REJECT | ACCEPT |
| `did:sage:ethereum:0xabc` legacy chain form | REJECT | ACCEPT |
| Legacy form with an extra locator segment | REJECT | ACCEPT |
| Legacy form with `#key-1` supplied to the DID-only API | REJECT | ACCEPT |
| Uppercase `DID:` scheme | REJECT | REJECT |

These are **primitive-entry-point** observations, not complete ID-01 or ID-02
case outcomes. The Inspector [positive-control report](https://github.com/SAGE-X-project/sage-inspector/blob/f104c8c3ce072e7a64d5a0092623e45ffb8d287b/docs/did-prefix-observations.md)
independently preserves the canonical DID failure and unsupported DID URL
operation. No success/failure here is transferred to the latest 489-parent
case inventory. No core source was changed in this review.

## Complete review queue and next boundary

The index groups all 91 rules by their authoritative source. Counts are:

| Source | Rules | Review state |
| --- | ---: | --- |
| Overview | 4 | Bounded cross-layer/document review in the linked addendum |
| Crypto and JCS | 9 | Bounded review in the linked addendum |
| RFC 9421, HPKE, session | 18 | Six MSG and six HPKE rules reviewed; six pending |
| DID method | 4 | ID-01 and ID-02 gap; ID-03 partial; ID-04 pending |
| Card, transport, registry, resolution, tables | 29 | Pending |
| Agent/MCP Guard and non-HTTP MCP | 23 | Pending |
| Process and evidence charter | 4 | Pending repository/evidence review |

The next implementation-map pass must cover the remaining 63 rule groups
against actual code and test entry points. For identity, first introduce or
identify one explicit strict 0.10.0 parser shared by DID and key URL uses,
without changing the legacy public API's behavior implicitly. Separate
profile-specific locator validation from generic syntax and keep trusted
Source validation, exact key selection and signature verification distinct.
Then rerun positive, negative, kind, length, fragment, alias and cross-registry
cases in both Inspector adapters and relevant host assemblies. The eventual
complete map must name the consumer/import compatibility consequences before
changing or removing the legacy parser.

Recheck the current index and preserved bounded observations with:

```sh
python3 -B verification/build_core_gap_index.py
python3 -B verification/observe-core-identity.py
```

Locally, `build_core_gap_index.py` also accepts `--go-root` and `--rust-root`
to verify that every starting source location exists at the pinned checkouts.
Refreshing the runtime observations requires freshly built adapters and the
two `--go-adapter`/`--rust-adapter` paths with `--write`.
