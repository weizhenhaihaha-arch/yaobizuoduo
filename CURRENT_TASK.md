# Current AG Task

- Task ID: `G0-T06`
- Gate: G0
- Risk: `D0`
- Status: `merged_verified`
- Baseline: `af25e573b6a1a8b38d8eaf9a60bcf4988be6ed32`

## Implementation boundary

G0-T06 generation 1 is a D0 governance-only card. It admits the product
owner-approved standards proposal from PR #35 while preserving its exact head
`31c5cbdc89c940fa7c911f5ac1c5beb4fb2fb1e1` and failed CI run
`30105873742` as immutable history.

The authorization record must have ordered parents
`[af25e573b6a1a8b38d8eaf9a60bcf4988be6ed32,
31c5cbdc89c940fa7c911f5ac1c5beb4fb2fb1e1]`. Its first parent is the
authoritative G0-T05 terminal main; its second parent is only the approved
standards proposal. The card may not reinterpret PR #35 as a successful
candidate.

## Frozen implementation scope

- `PROJECT_STATUS.yaml`
- `CURRENT_TASK.md`
- `PROJECT_MEMORY.md`
- `README.md`
- `docs/OPTIMIZED_PRODUCT_WORKFLOW.md`
- `evidence/g0-t06/workflow-standards-authorization.json`
- `scripts/validate_project_status.py`
- `tests/test_g0_project_status.py`

## Stop boundary

Only the approved standards document, its links, exact authorization receipt,
canonical state/task mirrors, validator regression and durable memory may
change. G1-T01 remains `not_authorized`.

P0/G1 implementation, product code, public or private market access,
credentials, orders, trading, ruleset changes, deployment, release and
LOCAL-PREVIEW expansion remain forbidden.

## Delivery verification

Authorization topology, exact eight-path scope, receipt bytes, approved
standards digest, canonical status validation, focused adversarial regressions,
Python compilation and whitespace checks passed. Delivery identity remains
the implicit exact HEAD; implementation is
`36146c77e8c0f7e977d2003fa7ee12349375a945`. Candidate CI and both independent
reviews were evaluated on candidate
`6277839f6b21b9ce6ee0becbe8bbf2074ae7fc92`. Architecture returned `CLEAR`;
candidate CI run `30106788285` failed because a legacy G0-T04 route guard
reinterpreted the new G0-T06 lifecycle. Code/security is therefore
`REQUEST_CHANGES`. Generation 2 atomically cleared all candidate, CI, review
and blocker identities. The bounded repair implementation is
`7497a1986679096805df5c6b3751e9a72fe857bb`; it scopes G0-T06 lifecycle
continuity before legacy route guards and adds hostile regressions. The
generation-2 delivery candidate
`4e24be5e7bcba3be10e252ed7c126a57315aec1c` was returned before push:
code/security found that cumulative allowlist, immutable receipt/document,
next-authorization and complete PR #35 failure identity were not yet enforced
across every lifecycle state. Architecture is `WATCH` until those exact
mechanical boundaries are present. Generation 3 is now the sole active repair
and may change only those exact fail-closed governance boundaries. The bounded
generation-3 implementation is
`d295a00dd34470c4f0bf0ded638f28cc92a8e935`: it carries the cumulative
eight-path allowlist, exact standards and receipt bytes, the unchanged
`G1-T01 not_authorized` boundary, and full PR #35/failed-CI identity through
the lifecycle. Canonical validation, 113 non-governance Python tests, 13
focused adversarial governance tests, 10 frontend tests, and the frontend
production build passed. The delivery candidate is the implicit next committed
HEAD pending exact PR CI and independent reviews.

The exact generation-3 candidate
`1b1380774afcd030d2c8841b20fe9c8c6c71827f` passed PR CI run
`30108655236` and architecture review was `CLEAR`, but code/security returned
it because the direct-parent validator did not explicitly preserve pending
review identity during the `in_progress -> awaiting_review` delivery
transition. The three earlier security blockers remain closed. A next
generation may repair only this exact transition invariant and its regression.
Generation 4 is now the sole active repair; all generation-3 evidence was
cleared atomically from current state and remains preserved in Git history.
The exact generation-4 implementation
`015945aa821913b1c66a9436ed244eeca7cbcfdf` preserves pending review and
blocker identity through delivery and anchors its regression to the exact
generation-3 candidate. Canonical validation, 113 non-governance Python
tests, 13 focused adversarial governance tests, 10 frontend tests, and the
frontend production build passed. The candidate is the implicit next commit.
The exact candidate `cab654c8650ab80333ab0f417c01421d54928a33`
passed PR CI run `30109149237`, independent code/security `APPROVE`, and
independent architecture `CLEAR`. It is accepted pending the exact closure
HEAD CI and final no-drift merge gate.
Closure `5c6055bf8ff807d383d2c543016bad9560ee2e45` passed exact CI run
`30126218254` and PR #36 merged as
`a68662eb0d46514953f6e6888d3f3f7a4d9eeee3`, ordered parents
`[af25e573b6a1a8b38d8eaf9a60bcf4988be6ed32,
5c6055bf8ff807d383d2c543016bad9560ee2e45]`, with a second-parent-equal
tree. Authoritative-main push CI run `30126273246` succeeded. The card is
merged-verified pending this implicit finalization HEAD and its D0 CI.
