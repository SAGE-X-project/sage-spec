# Pinned Go/Rust crypto and JCS gap review

Status: **9 additional rule groups assessed at bounded source or primitive
runtime scope**. Together with the [identity review](core-gap-review.md), the
[complete 91-rule index](core-gap-index.json) has 37 reviewed and 54 pending
after the [overview review](core-overview-review.md) and
[HTTP message-signature review](core-rfc9421-review.md) and
[HPKE review](core-hpke-review.md) and
[session review](core-session-review.md) and
[ID-04 review](core-gap-review.md) and [Agent Card review](core-card-review.md).
No normative clause, core implementation or latest 489-parent Inspector
conformance verdict changes here.

The source baseline remains `sage-spec`
`44df132fee5925182018ce089dc82435cb353f8a`, Go `sage`
`49379baadc6baec9ca8b4bb7d15bf43d65144bd7`, and Rust `rs-sage-core`
`ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396`. The
[Inspector 47-case primitive fixture](https://github.com/SAGE-X-project/sage-inspector/blob/f104c8c3ce072e7a64d5a0092623e45ffb8d287b/vectors/0.10.0/jcs-signatures.json)
has SHA-256 `8b7b202db497bb40a65b64f62a4afc0a3bd0a24b624fd76557d69f4b211bdd26`.
It is an earlier independently constructed fixture related to CRYPTO-02 and
JCS-01/03, not a complete test of the later source revision. The
[Go report](evidence/core-jcs-crypto-go.json) and
[Rust report](evidence/core-jcs-crypto-rust.json) were freshly run against the
named current core revisions. The Inspector runner binary SHA-256 was
`d3868cae8777aececeffc87fc2d2d7d1853c335a7a4562b73e1977ef963201ba`;
its source revision was `f104c8c3ce072e7a64d5a0092623e45ffb8d287b`.
The [report checker](check_core_primitive_reports.py)
requires the original case identities, expectations, executable hashes and
unpromoted failures.

| Subject | PASS | FAIL | UNSUPPORTED | Complete rule/case verdict |
| --- | ---: | ---: | ---: | --- |
| Go | 27 | 18 | 2 | Not established |
| Rust | 31 | 16 | 0 | Not established |

## Rule-by-rule findings

| Rule | Bounded finding and source entry points | Status |
| --- | --- | --- |
| CRYPTO-01, supported signing roles and exact encodings | Both cores expose Ed25519. Go's generic [`VerifySignature`](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/crypto/keys/verify.go#L43-L83) converts DER; its secp256k1 verifier also accepts 64-byte signatures. Rust [`PublicKey::from_bytes`](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/crypto/keys.rs#L128-L160) accepts compressed ECDSA points and [`Signature::from_bytes`](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/crypto/signature.rs#L59-L103) accepts DER and 64-byte secp256k1 signatures. These are broader than the 0.10.0 wire encodings. The primitive fixture tags these cases CRYPTO-02; this CRYPTO-01 finding comes from source and related runtime behavior, not a complete CRYPTO-01 case execution. | **GAP**, bounded |
| CRYPTO-02, exact verification and strict points | Both general verifier paths accept identity/mixed-torsion Ed25519 cases and high-S or DER ECDSA inputs in the bounded run. Go [`VerifySecp256k1Keccak`](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/crypto/keys/secp256k1_keccak.go#L43-L68) discards recovery `v` and normalizes high-S. Rust [`PublicKey::verify`](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/crypto/keys.rs#L390-L425) normalizes high-S and its secp256k1 branch does not compare recovered key identity. Exact profile rejection requires new strict paths and an all-message consumer audit. | **GAP**, bounded |
| CRYPTO-03, ECDSA signer nonce and recovery parity | Go P-256 signs with `crypto/rand` and emits low-S; secure randomized signing is permitted. Rust signers normalize low-S and the inspected secp256k1 path adjusts its recovery value. This pass did not execute cross-core signing or prove every signer/FFI/host path chooses these implementations. | **PARTIAL SOURCE REVIEW** |
| CRYPTO-04, full DID key reference | Both legacy key APIs still expose a shortened `hex(SHA-256(pub)[0:8])` ID. Both `registry010` gates select an exact `did#name` signing URL for a configured record. The earlier [identity review](core-gap-review.md) found the public DID parser gap. This pass did not prove that every signer, verifier, resolver and plugin path uses the full URL rather than the legacy ID. | **PARTIAL SOURCE REVIEW** |
| CRYPTO-05, secret custody and domain separation | Inspected Go key generators use `crypto/rand`; Rust Ed25519 generation uses OS randomness. Some selected Go comparisons use `subtle.ConstantTimeCompare`; Guard proof paths apply a versioned signing domain. These source observations cannot establish private-key isolation, no logging, all-domain coverage, constant-time behavior of every secret-derived comparison or prevention of arbitrary plugin signing. | **PARTIAL SOURCE REVIEW** |
| JCS-01, parsing before canonicalization | Fresh primitive execution repeats Go acceptance of duplicate/escaped-duplicate keys and a lone surrogate, and both cores accept negative-zero and negative-underflow tokens. Go [`jcs.Canonicalize`](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/crypto/jcs/jcs.go#L53-L69) decodes into a map before checking duplicates; Rust's parser preserves raw number literals but does not reject negative zero before serialization. Chapter-specific schema, 16 MiB and depth limits remain outside this fixture. | **GAP**, bounded |
| JCS-02, exact protocol integers | The inspected Go and Rust Guard intent paths check bounded `created`/`expires` fields before accepting them. The earlier Inspector signed-Guard fixtures are bound to a different spec revision and cover only that path. This pass did not audit all protocol integer fields, producers or second parsers at the current revision. | **PARTIAL SOURCE REVIEW** |
| JCS-03, RFC 8785 bytes and one parsed meaning | Both cores match seven independent primitive canonical-byte fixtures, including object/array order, Unicode and number formatting. Their complete receive→verify→dispatch paths and every later parser were not part of this run; exact byte matches do not prove no reinterpretation after signature verification. | **PARTIAL RUNTIME REVIEW** |
| JCS-04, exact signature-member exclusion | The 0.10.0 Card rule removes only nested `proof.proofValue`; Go [`a2aCardCanonicalBytes`](https://github.com/SAGE-X-project/sage/blob/49379baadc6baec9ca8b4bb7d15bf43d65144bd7/pkg/agent/did/a2a_proof.go#L73-L89) and Rust [`A2AAgentCard::canonical_bytes`](https://github.com/SAGE-X-project/rs-sage-core/blob/ef63d76b88fe4d6ddbc7ae0fcfdbce7beab4d396/src/did/a2a.rs#L179-L189) remove the entire `proof` object. This is a direct source-level mismatch for that Card entry point. The current Inspector primitive adapters do not expose full 0.10.0 Card verification, so no full JCS-04 case is passed or failed here. | **SOURCE GAP** |

These findings distinguish reusable primitive APIs from the stricter 0.10.0
profile. A general parser's extra acceptance is a profile integration gap,
not evidence that every caller uses that parser. Conversely, a narrower
Guard or registry helper cannot prove that all callers enforce the profile.
The existing Go `crypto/jcs` and `crypto/keys` unit packages passed, as did
Rust's four JCS and 178 crypto library tests. Their success verifies the
existing code's tested behavior; it does not override the independent
0.10.0 rejection mismatches above.
The next unreviewed rule is `CARD-03`, followed by the other 53 pending rule
groups in traceability order. The core owners
must select explicit strict API boundaries with consumer compatibility notes
before changing the general legacy behavior. Inspector must rerun complete
parent cases at the final core and host revisions.

To check this saved evidence with a checkout of Inspector at revision
`f104c8c3ce072e7a64d5a0092623e45ffb8d287b`:

```sh
python3 -B verification/build_core_gap_index.py
python3 -B verification/check_core_primitive_reports.py --inspector-root /path/to/sage-inspector
```
