# Independent review of unadopted method-security candidates

Decision: ACCEPT — scoped documentary-analysis candidate and separately scoped incomplete binding proposal only.

No important unresolved defect was found that blocks retaining these artifacts as unadopted proposals. This decision adopts no specification, version, operating root, implementation, or new conformance verdict. All seven historical documentary FAILs remain unchanged. In particular, the composite `security-requirements.1` is **not an overall PASS**; all-command authentication and fork binding remain incomplete.

## Reviewed artifacts and provenance

- `06-did-sage.md`: SHA256 `995f99299abc0ebd02651bfda75a5d30145968add464e1f93b2e9d656ea8184b`.
- `binding-proposal.md`: SHA256 `94ddba93442850e80ce7097b145b792dbed0e21e6ee868941956fbee3670a0b7`.
- Current `manifest.json`, including the later-added binding-proposal entry: SHA256 `cbd9bdfbf0fd15072aa389939903b01733e014d1dd7eb6634d70ee9b721c090e`.
- Adopted baseline: Git commit `06b50e177ccd22bce7d70fd80c2d7f822ae3fd3b`. Baseline `spec/06-did-sage.md`: SHA256 `fa7e180a37971ec382968d826857a3c4735f2a5f476c939d7aaf48349cea5691`.
- Frozen seven-finding inventory: SHA256 `b14d0166821457e7b09ad48c73145433eafb773cbecfa4cb975df9cab5e860d5`.
- Local RFC3552 snapshot: SHA256 `ba07e18bdffd18893e8607398bef42dbdb5f1c5aa0c7dd6891d43ca8a0b19e4f`.
- Local RFC6973 snapshot: SHA256 `94bb6027b22603c58728431ec4606a0f2a7aad569234322c55d6a91e22ffa06e`.

The baseline was read from its fixed Git blob, not from the user's dirty specification checkout. I compared the candidate against that blob: removing exactly the 134 inserted lines comprising sections 6.1–6.4 restores the baseline bytes exactly. Existing chapter text and obligations are therefore preserved. Manifest source hashes for chapters 00/01/06/09/10, charter and standards-application matrix were checked against fixed source material. I read the seven exact IDs and their review bases; this review does not modify that inventory.

## A. Chapter 06 analysis candidate

**ACCEPT as a substantive partial documentary repair candidate.** The new text supplies analysis rather than merely headings or references:

1. `did11-cr20260305#privacy-requirements.1`: section 6.4 discusses all nine RFC6973 section 5 categories. It connects public controller/key/service data, lookup traffic, retained history, compromise, naming, unsolicited interaction and represented people to surveillance, stored-data compromise, intrusion, misattribution, correlation, identification, secondary use, disclosure and exclusion. It also states mitigation limits: encryption does not redact public records, rotation/deactivation does not erase links, retention policy cannot erase required integrity history, and no general consent/erasure or regulatory-compliance protocol is supplied. These address the identified substantive omission without claiming runtime privacy protection.
2. `did11-cr20260305#security-requirements.2`: section 6.2 covers all eight listed attacks across create, lifecycle/key/service/operator mutations and resolution. Amplification is concretely described for propagation/proof work, retained state, replication, backend reads and response size. Integrity and replay explanations distinguish management commands from application-message replay and distinguish PoP from authorization. The text explicitly conditions incomplete management and fork guarantees instead of inventing their availability.
3. `did11-cr20260305#security-requirements.13`: section 6.3 relates transaction/proof validation, propagation, consensus/finality, state/history/tombstone retention and fresh reads to peer/operator resource burdens. It separates paid mutation fees from costs externalized to peers/RPC operators, and per-record bounds from registry-wide growth. It does not demand fabricated fee benchmarks or present future measurements as completed.
4. Composite `security-requirements.1`: sections 6.1–6.3 improve its specific residual-DoS/exclusion analysis. Finite resources, privileged/distributed flooding, pre-authentication cost, source outages, finality and fail-closed freshness explain residual susceptibility. However this is not an audit of every RFC3552 obligation, and does not close the composite finding while complete authentication/fork contracts remain missing.

I found no removal or weakening of an adopted obligation, closed record schema, atomic grant/history rule, algorithm policy or freshness boundary. The added lower-case requirements about framing, protected secrets and atomic decisions restate cited existing duties; absence of new uppercase BCP14 words was checked but was not treated as sufficient proof by itself. No accepted-byte change, runtime verdict, new operating authority, endpoint-fetch permission, logging obligation, transitive human approval or change to the approved 0.10.0 alg/kid/JSON-LD policy is introduced by this analysis. The availability exclusions are explained rather than used to excuse avoidable unbounded parsing or partial writes.

A future adopted documentary revision still needs its own exact-source author review. This candidate review is not that new revision's formal PASS assignment and does not overwrite frozen results.

## B. Management/fork binding proposal

**ACCEPT as a concrete but deliberately incomplete UNADOPTED design proposal; not acceptance as a finished or implementable conformance binding.** Its separate status is essential.

The proposal materially improves specificity: an authenticated leaf-to-actor mapping, same non-transferable TLS stream, current credential-generation/pin/validity check at serialization, bounded canonical command frame, complete command context, all eight operation schemas, current grant checks, atomic record/version/grant/history/tombstone publication, context/digest-bound response, and uncertain-outcome quarantine are described. Actor authentication is explicitly separate from lifecycle permission. The reference controller-only/delegated=false session is not misrepresented as operator support. Fresh TLS alone is not presented as mutation replay protection; exact prior version, state and tombstones supply that separate function.

The chain proposal distinguishes authenticated transaction sender from PoP and body claims, transaction nonce from record version, and EIP1559 typed transaction signing from legacy EIP155 and SAGE signatures. It does not fabricate ABI selectors or claim the legacy deployed contract implements the proposed eight-operation mapping. The retained commitment/reveal properties are consistent with adopted REG-06.

The fork proposal correctly rejects chain ID/address/code or genesis alone as sufficient. It calls for validated ancestry, selected consensus/finality or authenticated resolver-attestation rules, durable accepted policy/anchor/version state, conflict refusal and explicit trusted reconfiguration. It acknowledges that a common prior anchor cannot by itself distinguish later divergent branches and that a hostile trusted source is not automatically detected.

The following remain adoption blockers, explicitly disclosed by the proposal, rather than findings that have been closed by this review:

- Authenticated read-only history/recovery framing and permission rules are not yet defined. The proposed response and command identity are not a complete recovery protocol.
- Actual chain ABI/selectors/encoding, transaction-type acceptance, direct-sender enforcement, output/revert/event rules and code/upgrade policy remain to be bound and reviewed. No EOA/account-abstraction or relayer interoperability has been established.
- The concrete consensus verifier or resolver attestation artifact, validation rules, persistence/reconfiguration integration and branch-conflict tests remain absent. Protected operational roots/anchors/providers are not selected.
- A final operation/state matrix must be checked against REG-03/REG-09 and each concrete binding. For example, the proposed active-only `revoke-key` row must remain an explicit proposed binding restriction if retained, rather than being silently described as a verbatim statement of every baseline controller permission.
- Current-credential checking and durable registry publication need a real common serialization contract; separate unsynchronized check and commit would not implement the stated design.

The phrase “one-to-one map” should be read as unique credential-to-actor mapping with explicitly allowed multiple rotation credentials for one actor; it is not mathematically injective in that direction. The adjacent text makes the security rule unambiguous, so this is non-blocking terminology cleanup for a later revision.

TLS1.3-only, full-handshake/no-resumption, direct-EOA scope, new framing and fork refusal policies are new acceptance/rejection choices. The proposal correctly excludes treating them as 0.10.0 PATCH clarifications under OVERVIEW-03 and requires an explicit version/profile compatibility decision. It changes no adopted contract now. The initial proposal's new exact framing must not be substituted for existing public REG-08 HTTP retrieval, nor inferred from the existing TLS1.2+ reference APIs.

Consequently `security-requirements.5`, `.6`, and `res10-crd20261001#vdr-forks.1` remain open, and composite `security-requirements.1` remains not complete. Concrete proposals do not themselves establish all-operation implementation correctness or deployed authority.

## Limits and preserved scope

This was read-only semantic review of source text, fixed Git blobs, local frozen standards and hashes. No Go/Rust build, test, parser, formatter, network/API, transaction, Registry operation or new runtime evidence was executed. Only this TMP report was written. No repository source or frozen result was changed.

The old seven FAILs, three approved 0.10.0 recommendation causes, issuer obligations, operating-history and deferred-registration items, outstanding Registry/new-contract decision, stages 7/8 and the original fourteen-stage order remain unchanged. Neither candidate establishes all standards compliance, production readiness, operational custody, successful fork handling or completion of the project.
