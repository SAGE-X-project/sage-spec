# Web registry response media contract

Status: **0.10.0 normative design corrected; implementation and Inspector
execution not established**. This change closes the remaining documented
accept/reject ambiguity for `REG-08-N04` without changing the 91 rule groups,
489 planned parent cases, 26 mandatory subscenarios or their execution state.
The pre-correction chapter is preserved at
[the historical source](history/web-registry-media-base-2026-09-30/spec/09-registry.md).

## Decision and compatibility

The prior chapter 09 required a fresh HTTPS web-origin
JSON record but did not state the accepted response `Content-Type`. A `text/plain`
response therefore had no normative accept/reject verdict, even though the
existing `REG-08-N04` plan named an unsupported-media-type case. The corrected
chapter accepts one parameter-free `application/json` media type, compared
case-insensitively under [RFC 9110 §8.3.1](https://www.rfc-editor.org/rfc/rfc9110.html#section-8.3.1).
It rejects absent, repeated, combined, malformed and parameterized values,
and any `Content-Encoding`. No content sniffing or fallback to the public DID
resolution media types is permitted. A media/coding failure is `record.invalid`;
the content-size failure is `size.exceeded`. RFC 8259 registers
`application/json` without defining a `charset` parameter; rejecting all
parameters is an explicit SAGE profile restriction, not a general HTTP rule.

The change narrows previously unspecified acceptance. The 0.10.0 design has
not been released, so the target version remains 0.10.0. An already deployed
implementation claiming an earlier 0.10.0 contract cannot silently adopt a
different verdict: its operator needs an explicit protocol-version transition
under chapter 00 §5, with no unsigned or weaker fallback. A later released
version would need a new exact version if this is a breaking change.

## Traceability and evidence

The existing [REG-08-P and REG-08-N04 plans](traceability.json) already map
the positive configured-origin read and negative unsupported media type to
`REG-08`. Their identities and `planned_not_executed` states are unchanged.
The informative [current design overlay](../analysis/current-design-overlay.json)
now points to the corrected chapter bytes; its prior revision is preserved
alongside the historical chapter so the earlier clause review still checks
its own inputs.
The [bounded media vectors](vectors/web-registry-media-0.10.0.json) pin thirteen
HTTP field decisions under those IDs, including case-insensitive type
matching, missing/duplicate/combined fields, an undefined `charset` parameter,
the distinct DID-document and problem-detail types, content coding and
forbidden trailer metadata. The public resolution envelope uses the same
`application/json` media type but must fail the separate closed body schema.
A reference checker verifies
their expected local decisions and source digests; these are **not** complete
record, TLS, cache, origin, registry-operation or host observations. The
Inspector's earlier 481-case evidence and the latest 489-case inventory are
bound to prior specification revisions and acquire no new verdict here.

The decision was compared with chapter 10's public resolution binding and
the standards application matrix. Chapter 10's `application/did+json` is the
document representation, while its `application/json` result envelope is a
different three-member object. No other in-scope accept/reject ambiguity was
identified by searching current normative chapters and profiles for explicit
undefined or deferred behavior and cross-checking the documented standards
clause findings. This is a bounded document review, not a proof that no future
ambiguity, implementation defect or security flaw exists. Deployment-specific
ABI, host I/O and controller authentication remain their separately declared
bindings; controller transfer and pre-enrolment compromise remain outside 0.10.0.

Run the document and bounded-vector check with:

```sh
python3 -B verification/test_web_registry_media_contract.py
python3 -B verification/check_web_registry_media_contract.py
```

Next, Inspector must pin this new normative source revision, replace the
earlier `REG-08-N04` unsupported/NOT_RUN media decision with a version-matched
case fixture and actual Go/Rust or web-origin observations, and keep the
result NOT_RUN or UNSUPPORTED until such observations exist. No code, deployment,
external audit, release or conformance claim is changed by this correction.
