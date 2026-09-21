# Standards applicability and source review

Reviewed 2026-09-13 against official publications. This document records selection
and limitations; it is not a claim of certification, an IETF registration, or a
security proof. The existing protocol mechanisms are retained where sound, with
SAGE-specific profiles made explicit. Reported errata are not silently normative.

## Adopted constructions and boundaries

| Source | Adopted scope | Boundary / SAGE decision |
|---|---|---|
| [RFC 9421](https://www.rfc-editor.org/rfc/rfc9421.html) | HTTP signature-base and request-bound response construction | Chapter 03 fixes coverage, algorithm, version, freshness and rejection; a valid signature is not tool authorisation |
| [RFC 9530](https://www.rfc-editor.org/rfc/rfc9530.html) | Content-Digest over HTTP content | Digest is covered by a signature; no authentication is inferred from an unsigned hash |
| [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html) | JCS for explicitly identified JSON structures | Strict I-JSON rejection; not arbitrary JSON stringify or HTTP-message reserialisation |
| [RFC 9180](https://www.rfc-editor.org/rfc/rfc9180.html) | HPKE Base exporter suite | Transcript/extra ephemeral combiner is SAGE design, not an RFC authentication theorem |
| [RFC 5869](https://www.rfc-editor.org/rfc/rfc5869.html) | HKDF extract/expand | Exact SAGE domain labels and transcript bytes are fixed in chapters 04/05 |
| [RFC 8439](https://www.rfc-editor.org/rfc/rfc8439.html) | ChaCha20-Poly1305 | Sequence nonces, key lifetime and replay state are SAGE responsibilities |
| [RFC 8032](https://www.rfc-editor.org/rfc/rfc8032.html), [RFC 7748](https://www.rfc-editor.org/rfc/rfc7748.html) | Ed25519, X25519 | Validation and intended relationship are explicit; X25519 is not a signature algorithm |
| [RFC 7517](https://www.rfc-editor.org/rfc/rfc7517.html), [RFC 8037](https://www.rfc-editor.org/rfc/rfc8037.html) | JWK representation | No claim of JWE or all JOSE algorithms; SAGE Keccak suite is not JOSE ES256K |
| [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119.html), [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174.html) | Capitalised normative vocabulary | Normative design is distinguished from verification status |
| [RFC 5234](https://www.rfc-editor.org/rfc/rfc5234.html), [RFC 4648](https://www.rfc-editor.org/rfc/rfc4648.html) | Grammar and canonical binary text encodings | Semantic lengths and rejection rules also apply |
| [RFC 8941](https://www.rfc-editor.org/rfc/rfc8941.html), [RFC 9651](https://www.rfc-editor.org/rfc/rfc9651.html) | Structured fields used by RFC 9421 | This profile uses the RFC 9421 integer/string/byte/list subset; later field types do not expand accepted signature parameters |
| [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457.html) | HTTP problem details where specified | Authentication failures remain generic; diagnostics do not expose verification oracles |
| [DID Core](https://www.w3.org/TR/did-core/), [Controlled Identifiers](https://www.w3.org/TR/cid-1.0/) | Method grammar, verification relationships and document representation | SAGE Card proof is explicitly custom; no unsupported W3C suite claim |
| [DID Resolution](https://www.w3.org/TR/did-resolution/) | Resolution concepts and metadata | Concrete SAGE resolution contract is chapter 10; draft evolution does not change it automatically |
| [CAIP-2](https://chainagnostic.org/CAIPs/caip-2) | Chain namespaces | Registry deployment identity is also required to avoid cross-contract collision |

## Informative design references

[RFC 9396](https://www.rfc-editor.org/rfc/rfc9396.html) motivates structured,
fine-grained authorisation data. The Execution Guard intent is a SAGE object; it
is not an OAuth token and does not implement OAuth by analogy.
[RFC 9334](https://www.rfc-editor.org/rfc/rfc9334.html) distinguishes attestation
architecture from a bare measurement. A precomputed component hash is useful as
local baseline evidence but is not remote attestation. Remote hardware appraisal
and initially compromised registration remain outside the current claim.

[MCP tools 2025-06-18](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)
support structured tool results and do not mandate one user-interaction pattern.
SAGE proposes `sage_secure_call` as a version-pinned binding above MCP and does not
redefine its standard. The security best-practice URL for that version redirected
to [2025-11-25 guidance](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices)
during review; it is informative, not silently treated as the older normative version.

## Errata disposition

| RFC | Observed disposition | Applicability |
|---|---|---|
| [9421](https://www.rfc-editor.org/errata/rfc9421) | Verified 8102, 8103 | Correct `@signature-params` spelling applies to signature-base reconstruction |
| [9530](https://www.rfc-editor.org/errata/rfc9530) | Verified 8158, 8273 editorial; Reported 8890 | No new digest construction; reported Brotli example outside the no-content-encoding profile |
| [8785](https://www.rfc-editor.org/errata/rfc8785) | Verified 7920; 6292 editorial | Chapter 02 rejects negative zero as a stricter SAGE rule, including underflow to negative zero |
| [9180](https://www.rfc-editor.org/errata_search.php?rfc=9180) | Verified 6941, 7121, 7790, 7934, 7937, 7932 | KEM suite identifier and private-vector clamping apply; info argument names kept distinct; Auth-mode claim correction is not inherited proof for Base composition |
| 9180 | Held 7251, 7933 | Not automatic normative amendments; HPKE payload sequence is not used by this exporter profile |
| [8037](https://www.rfc-editor.org/errata/rfc8037) | Reported 5329 | JWE/ECDH key-mixing issue, not adopted as a change to this JWK-only usage |
| [7517](https://www.rfc-editor.org/errata/rfc7517) | Reported 6907 | JWE example AAD, outside this profile |
| [9396](https://www.rfc-editor.org/errata/rfc9396) | Errata endpoint did not yield usable records in this review | Informative only; do not infer that there are no errata |
| [9334](https://www.rfc-editor.org/errata/rfc9334) | Listing consulted | Informative architecture; no new attestation mechanism adopted |

This is an applicability review of material consulted, not an exhaustive standards
compliance audit. Remaining implementation work must pin its libraries, apply
relevant verified errata and test exact version-specific constructions. Bibliographic
presence alone is not evidence that an implementation follows a standard.

## User-designated RFC 9421 project

The sibling `rfc9421` project supplies local English text, Korean explanatory
translations and Go implementation context. The [reference assessment](rfc9421-reference.md)
records the actual working-tree snapshot and differences. Translation and code
are informative; neither overrides RFC 9421 or establishes SAGE conformance.
