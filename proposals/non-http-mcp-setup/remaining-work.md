# Remaining delivery work

Assessment after the admission case-impact review, 2026-09-21. Scope: the authenticated
non-HTTP MCP binding in Go/Rust, its Inspector execution evidence and deployment
validation. This is a delivery breakdown, not a completion percentage or a time estimate.

| Remaining work package | Current state | Completion evidence |
|---|---|---|
| 1. Finalize and adopt one normative contract | DESIGN_ADOPTED: reviewed contract, baseline mapping, exact descriptor, compatibility and traceability published; runtime evidence remains absent | One consistent reviewed text, explicit adoption, reconciled profile/descriptor/compatibility/traceability; no conflicting admission definitions |
| 2. Go owner and private gate integration | NOT_IMPLEMENTED for the proposed binding; existing Guard/session primitives already work within their documented scope | Authenticated initialization, one history, output barrier, deadlines, close/admission order and bounded cleanup, with native scenario and race tests |
| 3. Rust implementation of the same contract | NOT_IMPLEMENTED for the proposed binding; existing primitives retained | Equivalent ownership/cancellation/storage semantics and native scenario tests, without assuming Go callback behavior |
| 4. Inspector actual protocol execution | NOT_RUN: all 71 catalog cases; earlier primitive/runtime reports remain valid separately | Go/Go, Go/Rust, Rust/Go, Rust/Rust exchanges; exact bytes, journals, effect and admission observations; evidence for each promoted case |
| 5. Deployment and remaining lifecycle integration | Pending selected registry Source and host enforcement bindings | Fixed deployment/host identities, authoritative observations, complete mediation and recovery evidence; applicable historical lifecycle/INS-11 assertions actually observed |

Packages 2 and 3 can proceed independently after package 1 establishes the contract.
Inspector test design can overlap them, but protocol PASS requires real bindings.
Package 5 needs concrete deployment and host choices; it cannot be completed through
more document checks. Runtime checks that do not create attack-capable reproduction
programs remain in scope. Dangerous host-bypass scenarios use scenario-based units
and retain any resulting limitation in the deployment claim.

The admission review classifies 71 existing cases as 8 assertion changes, 10 stronger
observations and 53 with no direct admission change. Those are design-impact counts,
not 18 completed tests or additional protocol cases. The 37 historical lifecycle cases
are a different catalog: do not sum 71 + 37 into an asserted total of unique tests, or
subtract primitive checks from either. No reliable overall percent complete follows
from these numbers.

## Scope outside these five packages

The broader product plan also includes repository separation, reusable Go/Rust core
library distribution, multi-language SDKs, registration/query MCP services, secure vs
unsecured comparison demos and downstream examples. These are separate deliverables;
they are not completed by closing the MCP protocol catalog. This document does not
assert a current completion percentage for those repositories.

## Why recent work did not reduce the unrun catalog

Signature fixtures, artifact consistency checks and same-author design reviews tested
or clarified narrower boundaries. They did not implement negotiated ownership or run
full protocol cases. The recent iterations therefore improved prerequisites without
reducing 71 NOT_RUN. Future progress should be reported against the five completion
conditions above, not counted by the number of merged documentation/checker PRs.

The [normative profile](../../profiles/non-http-mcp-security.md) adopts the corrected
contract. The next deliverable is the Go/Rust owner-aware gate and authenticated setup
implementation, with the mandatory child schedules and safe runtime evidence. No more
candidate-only checks are needed to claim design adoption. Separate-agent review is
not a third-party external audit, and no test status is promoted by adoption.

Cross-review's 26 mandatory child assertions remain within the 71 binding parents.
The earlier 8/10/53 impact counts describe historical input. Deployment Source and host
choices remain needed for the final package; design adoption does not supply them.
