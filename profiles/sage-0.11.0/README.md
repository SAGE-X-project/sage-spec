# SAGE 0.11.0 profile selection

Status: **ADOPTED DESIGN SELECTION**, revision1. This is a separately versioned
selection of V1 protected exchange and R1 registration-reader rules. It is not
an implementation release, complete operating deployment, new runtime verdict,
or an amendment to SAGE0.10.0. The [selection manifest](selection.json) fixes
exact byte labels, body discriminators, source identities and release gates.

## Normative selection and source precedence

The selected values in selection.json govern these0.11.0 version/domain and
reader choices. Its baseline_revision and per-file SHA256 map fix public input
bytes; a moving main or later ERC Draft does not update them automatically.
Rules outside this selection remain at their pinned source and status. Existing
management proposals are still implementation-design inputs; this record does
not certify or implement their ABI, authorization, storage, fork or history.
It does not adopt unlisted private or later candidates by reference. A full
matching management implementation requires a separately published complete
normative binding and qualified code/source/operating manifest before acceptance.
Old proposal documents and0.10.0 norms/reports retain their original meaning.

All selected fields/domains MUST agree for a new operation. A verifier MUST NOT
try the old profile, another key/algorithm, another Registry or an unprotected
path after refusal. A new Registry requires authenticated new enrollment/proofs
and exact Source/instance evidence. No existing address becomes the default.

Domain entries encode actual UTF8 bytes as hex. NUL is00 and LF is0a. Preserve
the stated REG04 length16, REG06 claim, exact Card/transport JCS, HPKE derivation,
session/AAD and Guard framing; only explicitly selected values change. SAGE
Card proof.type becomes SageAgentCardSignature0_11_0 with the selected Card
prefix/body version. This is distinct from unchanged A2A JWS typ. The non-HTTP
MCP binding changes its SAGE version; MCP protocolVersion remains2025-06-18.
Native issuance is a local binding, not an RFC signing-domain assignment.

Record version/recordVersion/expectedVersion, sequence/nonce, schema-format
counters, evaluator and package versions are independent from protocol semver.
A2A protocolVersion remains1.0. RFC internal HPKE-v1, suite identifiers,
JWK curves, algorithm namespaces and native SGS1 framing are not renamed.
Ed25519 is mandatory to implement, not mandatory for every active record or
message. Preserve each binding's optional-suite permission and fail closed
on unsupported suites. A Card's JOSE ES256 support does not qualify another
path's P-256 implementation. X25519 is key agreement only.

## R1 additional reader profile

This is a SAGE reader policy over the pinned ERC8004 Draft, not a claim that all
ERC8004 consumers support it. The manifest carries source revision/hash and
field bounds. The file MUST be bounded strict UTF8 JSON, without duplicate
members or unsafe/nonfinite numeric values. Each registration is a closed object
with exactly agentRegistry and agentId: missing, duplicate or additional members
are rejected. Top-level/service extension retention does not open registration
objects. The matched Registry is the canonical eip155 chain/
lowercase-address identity. Strings are retained without identity normalization.

agentId is an exactly represented integer0..9007199254740991 or a canonical
unsigned decimal string0..2^256-1 (0 or[1-9][0-9]*). The string form is an
explicit SAGE extension. Do not round large identifiers through floating point
or claim universal base-Draft interoperability. R2 numeric-codec work is not
selected. Empty-URI NFT registration remains possible but does not establish
protected readiness. URI grammar uses RFC3986; actual retrieval needs separately
qualified bounded scheme/content/redirect policy, never an arbitrary fetch.

Service.version and top-level active remain optional. active=true is necessary
only for linked protected eligibility and never sufficient. Absent/empty
supportedTrust is discovery-only. Unknown bounded fields and natural-language
descriptions are data, not permissions or configuration. ERC owner/operator,
agentWallet, SAGE controller, scoped grant, signer and KEM roles remain separate;
the thirteen-method SAGE Registry is not an ERC8004/ERC721 implementation.

## Deliberately unselected changes

This V1/R1 selection does not add JWK alg/kid, a new JSON-LD context or DID alias,
enable companion/payment/reputation/validation modules, expand actual crypto
support, change the128 lifetime-key design bound or select a smaller gas cap.
Reviewed optional designs require their own explicit inclusion/adoption and
qualification. A link-dependent capability stays unavailable until its complete
link/source/history conditions are met; it cannot downgrade to independent use.
No W3C/IANA registration or public service endpoint is created by these strings.

## Operating and implementation gates

The instance is UNBOUND and readiness is false. Every applicable field under
operating_requirements needs a concrete approved value and independent evidence
before dependent live use. Optional excluded capabilities must be explicitly
excluded without a support claim. Mandatory accountA support means actual
Registry msg.sender for EOA and contract-wallet calls; tx.origin, body actors,
PoP signers and ERC1271 success do not replace it.7702/AA transaction formats
are separate operating qualifications, not implied support.

R1 pure parsing, discovery reading, on-chain association and optional linked-use
are separate capability claims, all currently unimplemented. Pure parsing does
not fetch or establish authority. An R1 discovery reader needs its own bounded
scheme/content/Source/resource policy even when the companion is excluded;
on-chain association additionally requires exact ERC code/ABI and source/finality
evidence. operating_field_applicability records these distinct conditions.
7702/AA qualification applies only to an explicitly claimed format, without
withdrawing required actual-caller EOA/ordinary-wallet support.

Qualify exact compiler/library/license/code/ABI/source/dependencies, actual
chain/genesis/fork/transaction format, complete-operation numerical budgets,
finality/trust roots/time/durable recovery and real signer/KEM/host ownership.
Research gas caps, source checks, fixtures, booleans or outer receipts are not
that evidence. Preserve authorization/atomicity/history while qualifying costs;
no silent cardinality reduction or partial activation. Deployment and real
transactions require separate approval of concrete artifacts and target values.

Prepare separately versioned APIs and independent new subjects. Preserve old
records/history/tombstones/pins/findings, drain old operations explicitly, use
new transcripts/sessions and commitments, and prevent duplicate effects during
dual support. Volatile profile-aware caches never reset durable monotone or
terminal facts. Unknown source/history/time/custody/commit outcomes refuse or
quarantine; final effect checks and complete mediation remain necessary.

This documentation check executes no Registry, wallet, client, MCP or cryptographic
operation. Matching implementations require unit tests, safe owned normal runtime,
independent review and exact CI/source/subject evidence. A design choice or a
new subject does not relabel historical FAIL/PARTIAL/UNSUPPORTED/NOT_RUN.
