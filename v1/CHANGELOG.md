# Changelog (v1)

`v1/` holds one specification version, `0.9.0-draft.1.1`. It stands alone and
uses nothing from 0.9.0-draft.2, 0.10.0 or 0.11. The `spec/` folder at the
repository root and its checks are not changed by it.

## 0.9.0-draft.1.1 (unreleased)

- Chapters 00 to 08 of 0.9.0-draft.1 with all 54 text fixes, all 55 normative
  tightenings and eight wire-changing fixes: strict HTTP signature coverage;
  mandatory nonce, digest and response binding; directional session keys; a
  fixed rekey interval; the registry proof of possession checked by
  verifiers; signed transport requests and responses with domain-separated
  labels. The other eight wire-changing items are deferred and listed in each
  chapter under "Known residual risks". The item list is in
  [docs/errata-0.9.0-draft.1.md](docs/errata-0.9.0-draft.1.md).
- Chapter 00 gains §7, data protection requirements: size limits, parsing
  strictness, key handling, replay, error disclosure and logging.
- `vectors/` carries the 26 vectors of 0.9.0-draft.1 with their input and
  output bytes unchanged and `spec_version` `0.9.0-draft.1.1`. Two vector
  descriptions are corrected. The vector format adds a `reject` mode. The
  new vectors listed in the errata §11 are not yet added.
- Review corrections beyond the errata, where two applied items disagreed or
  the errata wording was too broad: the E03-08 coverage rule names derived
  components only; `@query` of an empty query is `?`; an 08 endpoint answers
  every pre-handler failure, RFC 9421 failures included, with HTTP 200 and the
  unsigned failure object; HPKE responder failures count as pre-handler; a
  check that can only reject (size, cookie) may run before the envelope
  checks; the HPKE init nonce is reserved after every check, HPKE open
  included; `public_kem_key` is the KEM key only under 06 §3.1; `metadata` is
  described as signed; the `rfc9421` vectors are stated to test signatures,
  not resolution.
