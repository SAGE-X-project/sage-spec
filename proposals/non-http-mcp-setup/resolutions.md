# Proposed resolutions of the MCP design review

Status: **PROPOSAL_NOT_ADOPTED**. This text resolves the three ambiguities identified
in [design-review.md](design-review.md) at revision
`05c9069e651c0b0debb699e329a7e9093a466741`, within the proposed design only. It is a
same-author correction and re-review, not an external audit or implementation result.

For the revised proposal, the rules below clarify the [owner contract](owner-contract.md)
and supplement the [carriage addendum](addendum.md). Earlier review documents remain
historical records of their pinned inputs. Their OPEN statuses are not overwritten.
The [resolution record and case plan](resolutions.json) records the new disposition.
Before adoption, integrate this text into one normative contract; implementations must
not choose conflicting interpretations from different historical documents.

## DREV-01: Final dispatch admission orders with closure

Passing an invocation to Guard, validating its signature or creating a durable
reservation is **not** final dispatch admission. Define final admission as the
serialized transition of that invocation's existing reservation to the durable
execution-started state (EXECUTING in EXEC-04), under the trusted final dispatch gate.
No tool effect may begin before this transition commits successfully.

The owner lifecycle invalidation operation and final admission use the same logical
ordering mechanism for that owner/incarnation. Immediately before committing final
admission, the gate checks owner liveness, local READY, the exact retained invocation,
current authority/policy/component validity and applicable session/request/intent
limits. Those checks and admission cannot be separated by a competing owner-close or
policy-retirement operation. Implementations may use different locking or transaction
mechanisms, but must expose this same order. Do not hold an owner lock across an
arbitrary tool effect. Inability to supply this ordering is unsupported, not permission
to use a stale readiness snapshot or caller-supplied permit.

- If close wins before a reservation exists, deny the call with zero effects.
- If close wins after reservation but before final admission, never invoke the tool.
  Preserve the reservation and nonce. The ledger owner may persist a terminal rejected
  outcome only if it can durably prove that no admission occurred and no competing
  invocation owns execution. Otherwise preserve an unresolved/unknown outcome according
  to the existing Guard recovery rules. Never delete or reset the reservation.
- If final admission wins, later connection closure cannot undo that decision or prove
  non-execution. The admitted invocation may complete through its existing execution
  path; no new invocation may be admitted on the closed owner. Preserve the durable
  terminal result or recover as unknown, without automatic redispatch.

A crash after durable admission but before the actual effect is conservatively
unresolved/unknown on recovery, not an excuse to execute again. This is the existing
execution-ledger tradeoff, not an exactly-once external-effect guarantee. Closure does
not grant permission to ignore independently applicable cancellation or tool policy,
but such cancellation cannot fabricate proof that an effect never occurred.

Re-review: this explicitly settles the interval between handoff/reservation and final
admission. The draft no longer leaves the observable close ordering to each language.
The concrete cross-component synchronization and durable failure behavior remain to be
implemented and tested. Disposition: RESOLVED_IN_DRAFT; runtime evidence NOT_RUN.

## DREV-02: Separate setup and protected-operation deadlines

Every pending owner operation carries an immutable local class: SETUP or PROTECTED.
This is internal state, not a peer-supplied field. The owner assigns the class from its
validated phase and message kind. A SETUP operation cannot become PROTECTED merely
because another callback observes READY.

SETUP operations use the original key-state creation deadline. Final publication,
including publication of READY, must precede that deadline and still satisfy session
validity. Closing, completing or retiring the setup operation also retires its operation
identity. A later duplicate setup callback has no authority, even after READY.

For a PROTECTED operation started after local READY, the old setup deadline is not
consulted. The owner instead uses a finite, trusted locally configured absolute
request/I/O deadline, fixed when that invocation starts. Configuration is provisioned
before use and is not optional model input. Missing configuration denies submission;
peer traffic and progress cannot extend the bound. Applicable session and Guard time
checks continue independently; passing one clock's limit does not waive another.
A new transport invocation for an existing signed call does not refresh its intent,
terminal result, nonce or execution identity.

If the protected deadline expires before final admission, use the pre-admission deny
path above. Expiry after admission closes the failed invocation/connection and reports
unverified transport failure without claiming rollback. Preserve durable execution and
client consumption state. Loss of the clock, rollback, session invalidation or expired
intent remains a failure under the corresponding baseline checks even after READY.

Re-review: output-completion step 4 in the historical owner contract applies its setup
deadline predicate only to SETUP. The equivalent protected completion uses its own
fixed deadline and session checks. This allows healthy protected traffic after the
30-second setup interval without reviving old setup callbacks. Disposition:
RESOLVED_IN_DRAFT; runtime evidence NOT_RUN.

## DREV-03: Explicit Ed25519 signature subset

This proposed binding supports **Ed25519 only** for execution-intent proofs, protected
result proofs, and SAGE outer/handshake message signatures used by this binding. Each
signing role still requires the appropriate active registry key, issuer/recipient
binding, current authorization and full existing signature verification. A valid
signature under an unsupported algorithm is rejected; key presence alone cannot
negotiate algorithm support.

The fixed tool descriptor already expresses the intent restriction and is unchanged.
Result and outer signatures are constrained explicitly here because the input schema
cannot constrain them. Provisioning requires suitable Ed25519 signing keys for the
participating roles before setup. If unavailable, this binding is unsupported; no
silent fallback, key substitution or automatic re-signing of an existing intent is
allowed. Ordinary key selection must still obey the baseline identity rules.

This is a narrower compatibility profile, not removal of secp256k1 or P-256 from the
general SAGE 0.10.0 specification or registry. Registry ownership transactions and
chain-native proofs retain their separately defined algorithms. HPKE's X25519 KEM,
KDF and AEAD are unchanged: X25519 is not an alternative signing algorithm.
Expanding this binding requires an explicit profile/descriptor revision and verifier
and interoperability evidence before advertisement.

Re-review: the accepted algorithm set is explicit for all relevant message-signing
roles without confusing it with registry or HPKE operations. Descriptor bytes and its
historical hash remain unchanged. Disposition: RESOLVED_IN_DRAFT; cryptographic
execution and cross-language support for this full binding remain NOT_RUN.

## Evidence and adoption state

Thirteen additional scenarios in resolutions.json cover the intermediate reservation
state, deadline classes and three distinct signature roles. They supplement the
original 40 and addendum 18 cases: **71 planned protocol cases, all NOT_RUN**. Existing
case identifiers, tests and historical reports are unchanged. The original finite
model does not implement these new admission, deadline or algorithm distinctions.

The resolution checker verifies hashes, finding-to-case membership and status labels;
it cannot establish the truth of the re-review arguments. Its unit and CLI tests are
document checks, not execution of the 13 protocol scenarios. The historical lifecycle
remains 37 NOT_RUN, conformance NOT_ESTABLISHED and external review NOT_PERFORMED.
Before normative adoption, obtain independent scrutiny of these corrections and merge
the proposed rules and traceability into a single reviewed normative baseline.
