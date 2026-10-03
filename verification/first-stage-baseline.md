# Reviewed SAGE 0.10.0 design baseline

The unreleased 0.10.0 normative design is frozen at source commit
`1820ab5eafb843e1c13f4c46c34aeeb28d934ac9`. The machine-readable
[baseline](first-stage-baseline.json) pins exact bytes of the charter, process,
changelog, all twelve chapters, both MCP profiles, protocol tables, six
public vector suites, the 489-case traceability plan, the 22-source standards
matrix, and the later Registry media/operator subcondition suites. Run
`python3 -B verification/freeze_first_stage.py` to verify these bytes and
the 45 requirement, 91 rule, 489 parent, 26 traceability-child and 17
operator-subcondition counts. The 17 operator conditions have stable IDs and
parent cases in the adopted Registry clarification; they are required
assertions for those parents, not extra parent PASS results.

The preserved `docs/design-and-integration-review` worktree was reread. Its
tracked working diff and ten divergent-file digests still match the
[prior disposition](preserved-design-review.md). That disposition retains the
useful L0–L3 implementation boundaries but rejects copying its older chapters,
profiles or case plan over the later normative adoption. This baseline does
not modify that branch or its uncommitted files.

The [standards application matrix](standards-application-matrix.md) records
the design disposition and narrower SAGE profile for every referenced source.
The [standards clause revision](standards-clause-revision.md),
[Web Registry media correction](web-registry-media-contract.md), and
[operator clarification](registry-operator-adoption.md) record their exact
accept/reject and compatibility changes. Existing historical revisions stay
bound to their original bytes. This local design review does not establish
core or deployed conformance, prove security of the composition, or replace
organizationally independent external audit.

`sage-inspector` must bind this exact baseline and all required assertions
before the program's first tooling stage can close. Its old 489-case inventory
at `44df132fee5925182018ce089dc82435cb353f8a` and its Registry-media
inventory at `dcdd028b5160de5e32eb1f43cf1f71eed3fc4744` retain their
separate revision-bound evidence states. Neither can inherit a complete-case
PASS for this source revision.
