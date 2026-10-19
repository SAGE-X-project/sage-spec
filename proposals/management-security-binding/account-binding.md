# Registry caller and contract-wallet binding

Status: **UNADOPTED future-version candidate**, draft revision 3. On
2026-10-19 the project selected actual-call address authorization for both
EOAs and contract wallets. This supersedes only the EOA-only restriction in
previous candidate drafts. SAGE 0.10.0 and existing deployments are unchanged.
It does not select an operating chain, transaction format, finality source,
wallet product, custody, release identifier or deployment.

## 1. One principal rule

For every write, the principal is the Registry's exact `msg.sender` during
execution at the configured Registry on the configured chain. Solidity defines
this as the sender of the current call, distinct from the full transaction's
origin ([Solidity 0.8.20 global variables](https://docs.soliditylang.org/en/v0.8.20/units-and-global-variables.html#block-and-transaction-properties)).
An EOA calling the Registry is its own principal. When a wallet calls the
Registry, the wallet address is the principal, even if an EOA submitted the
outer transaction or paid its gas. Registry controller/operator equality is
exact address equality; neither code size nor equality with `tx.origin` is
an eligibility test.

`revealClaim` requires its proposed controller to equal this principal. The
commitment is scoped to that same principal and Registry; only the same caller
can consume it, after its commit block and within the defined window. Later
writes require that exact current controller or an exact currently permitted
operator/DID/operation grant at serialization. A permitted operator may itself
be an EOA or wallet, but cannot create, grant another operator or substitute
its wallet owner as controller. State/version/grant rules and complete atomic
history remain those in [contract-design.md](contract-design.md) and
[lifecycle-and-schemas.md](lifecycle-and-schemas.md).

No input actor, RPC `from`, forwarded suffix/header, outer signer, sponsor,
wallet-reported owner, recovered SAGE proof key or `tx.origin` replaces the
actual caller. A relay that directly calls the Registry acts as its own address
and needs its own authority. Relaying an outer wallet transaction does not make
the relay the Registry principal. There is no new trusted-forwarder identity
mode, wallet-signature callback, controller recovery/transfer, or arbitrary
execution/delegatecall entry point in the Registry ABI. SAGE key proof checks
and chain-account authorization remain separate.

## 2. Wallet and observation boundaries

The Registry authorizes a wallet address; it does not attest the wallet's
signers, threshold, implementation, owner intent or resistance to compromise.
The wallet may have its own upgrade/owner policy. Changing that policy does
not change the stored Registry controller or automatically revoke its grants;
compromise of an authorized wallet can yield authorized Registry calls until
its applicable authority is removed. This candidate does not add recovery or
promise detection of such valid calls. The non-proxy restriction applies to
the Registry contract, not to every caller's implementation. Supporting wallet
addresses does not certify a particular account-abstraction, wallet-signature
standard or transaction-envelope scheme.

A successful outer transaction receipt is insufficient, especially when a
wallet can catch an inner call failure. Before reporting a management change,
the Client/observer must establish successful execution of the exact command
at the intended Registry and one coherent resulting record/grant/history state
at the selected finalized block. It must bind the actual Registry caller and
canonical calldata to that accepted command. Existing expected-version,
commitment, nonce and finalized-ancestry obligations keep their own roles.

The specific proof/trusted-node mechanism for observing inner calls and
complete authenticated history is still an adoption gate. Do not infer it
from a transaction destination, a wallet event, RPC claim, matching payload
hash or successful outer status. Missing/ambiguous execution or failed inner
mutation supplies no success evidence. No trace API or wallet event format is
implicitly selected here. Gas/call-depth exhaustion and unknown results use
the existing refusal/uncertain-outcome rules, not fallback authorization.

## 3. Evidence to implement after complete candidate adoption

The following are design obligations, all **NOT_RUN** for a new Registry.
Current ABI codec tests do not execute or authorize contract calls.

| Related group | Unit/data-only checks | Safe owned-runtime evidence |
|---|---|---|
| Creation and caller scope | Exact controller equality, caller/Registry-scoped commitment, same-caller reveal, state/window/version bounds | Normal commit/reveal/activate once from an EOA and once from an owned wallet; inspect Registry caller, canonical accepted command and complete resulting state/history |
| Current grants | EOA/wallet controller and operator combinations, exact operation scope, no operator creation/delegation, revoke-before-write ordering | Normal authorize/use/revoke lifecycle for permitted EOA and wallet addresses; observe each accepted successor and grant history |
| Principal substitution | Fixed mismatched actor/origin/signer/relay/PoP data are rejected or cannot substitute authority; no exploit generator | Normal wallet call shows wallet as Registry principal while outer submitter differs; no hostile forwarding runtime |
| Outcome and compatibility | Model inner failure with outer success, unknown receipt, stale predecessor and no partial mutation; preserve old subject IDs | Normal successful wallet lifecycle plus isolated ordinary failure observations where safe; exact pinned artifacts and finalized-source evidence, otherwise NOT_RUN |

Only actual observations may change those statuses. Independent review,
unit tests, safe runtime, full PR/main CI artifacts and explicit versioned
adoption remain required by [verification-plan.md](verification-plan.md).
This selection resolves the account-policy decision; it does not complete
the chain binding, cryptographic feasibility, source/fork contract or stages7/8.
