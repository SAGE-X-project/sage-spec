# Standards clause revision for SAGE 0.10.0

Status: **AMENDED_NORMATIVE_DESIGN_PENDING_EXECUTION**. This revision closes
the three text findings in the [independent clause audit](standards-clause-audit.md)
against the unreleased 0.10.0 design. The earlier 481-case snapshot and its
review records remain pinned under
`history/standards-clauses-base-2026-09-29/`; the current plan has 489
distinct parents. The [machine-readable record](standards-clause-revision.json)
pins both sets of bytes. Neither set is evidence that a core or Inspector
executed the new cases.

## Decisions and compatibility

**SCA-01:** RFC 9421 `alg` values in SAGE HTTP messages are limited to the
registered `ed25519` and, if implemented, `ecdsa-p256-sha256` algorithms.
The SAGE private `sage-secp256k1-keccak256` identifier remains available in
the explicitly defined non-HTTP SAGE bindings, but is forbidden as HTTP
`alg`. The outer HTTP signature uses the exact active signing key named by
the inner envelope. A record whose only signing key uses the private suite
cannot use this protected HTTP binding. Sender and verifier fail closed;
there is no automatic key substitution, algorithm downgrade, unsigned retry
or separate HTTP identity. These rules narrow previously accepted messages.
They are a correction to the approved unreleased 0.10.0 design, not an
assertion that an already released 0.10.0 deployment can change its verdicts
without a version transition. A deployed version would require the versioned
change procedure in `spec/00-overview.md` §5.

**SCA-02:** the literal `did:sage:` prefix is case-sensitive in both DIDs and
DID URLs. The grammar uses RFC 7405 `%s` notation and the parser rejects a
different case as `id.malformed` before any normalization or resolution.

**SCA-03:** the secp256k1 JWK key representation now cites RFC 8812 §3.1.
Its ES256K signature algorithm uses SHA-256; SAGE's private Keccak suite
does not inherit JOSE or HTTP algorithm identity from that JWK representation.
This reference correction changes no JWK bytes.

The Inspector plan adds eight positive/negative parents covering the two
permitted HTTP algorithms, a private HTTP `alg`, a private-only key record,
key substitution, DID and DID-URL prefix case, and non-HTTP private-suite
scope. P-256 support is optional and receives UNSUPPORTED when absent; it
cannot be satisfied by fallback. All eight cases remain
`planned_not_executed`. Historical Inspector reports cannot be promoted to
their results. The current graph is an informative mapping of the 489-case
plan, not an implementation finding.

Implementation conformance: **NOT_ESTABLISHED**. Core and Inspector execution:
**NOT_RUN** for this revision. Organizationally external audit:
**NOT_PERFORMED**. No release or tag is created by this review.

The protocol sources are [RFC 9421 §3.3](https://www.rfc-editor.org/rfc/rfc9421.html#section-3.3),
the [IANA HTTP Signature Algorithms registry](https://www.iana.org/assignments/http-message-signature),
[RFC 7405 §2.1](https://www.rfc-editor.org/rfc/rfc7405.html#section-2.1), and
[RFC 8812 §3.1](https://www.rfc-editor.org/rfc/rfc8812.html#section-3.1).
