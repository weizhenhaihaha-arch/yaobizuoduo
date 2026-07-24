# Current AG Task

- Task ID: `G0-T06`
- Gate: G0
- Risk: `D0`
- Status: `authorized`
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

Pending authorized-card implementation and exact-head validation.
