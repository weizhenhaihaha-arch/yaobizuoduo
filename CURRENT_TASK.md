# Current AG Task

- Task ID: `G0-T05`
- Gate: G0
- Risk: `D0`
- Status: `closed`
- Baseline: `dcb942a80a91312fad12d90b5e362cbdd0611017`
- Implementation main: `d3a617ab3081e03276a96142ae2b76349e7b2ef9`

## Implementation boundary

Package A G0-T05 generation 3 implementation is active from exact
implementation main `d3a617ab3081e03276a96142ae2b76349e7b2ef9`. That main
has ordered parents
`[f56c5969051694b35bb77289fbf4868b5e723bef,
ea91b842cc36b77acc77f83b7f189349e8e9ca4a]` and tree
`e08eb6de1c07415316e3ab0895fd58f9c178b322`.

Terminal N has ordered parents
`[1419f7c77ff102fd68eb9583f5ec5c3b196ae4be,
da34fa5094fc945608e0ee570bc66276c9124d2e]`, tree
`dd68a575c89c4e6bf850b3f9e04f83d0f015d272`, and successful push/main run
`30043450574`.

The frozen Package A identities are:

- payload
  `815a40dc1fb47b367e1fe5707c16911862feeb929b0356aff769d0544500ca27`;
- manifest/schema blobs
  `f523c793a58d27e8ffd79da01048c8cd93aaa315` /
  `132656bcda439c20a2ade78d30116c49706de7b3`;
- ruleset `19526291` evidence digest
  `73aa3644a4c571c7101b0ac36547bd1be2edc306846045d2d36ad07ac86c5bb1`;
- historical generations `[1,2]`, making generation `3` the mechanical
  minimum unused integer greater than all history;
- superseded activation blob
  `c061d55218098fd5957ef75d40cb855635371bb6`, which must not be reused.

## Frozen implementation scope

- `PROJECT_STATUS.yaml`
- `CURRENT_TASK.md`
- `PROJECT_MEMORY.md`
- `docs/NEXT_WORKFLOW.md`
- `evidence/g0-t05/package-a-activation.json`
- `scripts/validate_project_status.py`
- `tests/test_g0_project_status.py`

## Stop boundary

The implementation and delivery chain must remain strict single-parent from
exact implementation main. During review, local main and origin/main remain
`d3a617ab3081e03276a96142ae2b76349e7b2ef9`. The cumulative card diff must
contain the required governance mirrors, validator, and tests and must remain
inside the frozen seven-path ceiling.

G1-T01 remains not authorized until G0-T05 is fully closed on authoritative
main. Workflow/ruleset mutation, product code, market API, credentials,
trading, deployment, release, fallback, a second product, and system
modification remain forbidden.

## Delivery verification

- Exact implementation:
  `5862c7b4b7c9080ba20ed40e0a81f157d72a7cc5`
- Canonical validator: passed.
- Package A / G0-T05 focused suite: `60 passed`.
- Non-transport Python suite: `551 passed`.
- Frontend Vitest suite: `10 passed`.
- Frontend production build: passed.
- Python compileall, Git diff, and secret checks: passed.

The exact delivery candidate is
`a29c5f35bbbaada717c69c9d9b4749a07db2c464`. Its exact-head CI run
`30087724361` succeeded. Independent code/security review returned `APPROVE`
and architecture/route/time-causality review returned `CLEAR`, both bound to
that exact candidate. Acceptance
`3f30ac7f2cc6d2196a893b26d922984500429338` passed exact-head CI
`30087824072`, then protected-main merge
`c7ed76914e7728ab0ef95d85699663656dcddf04` preserved ordered parents
`[d3a617ab…, 3f30ac7f…]` and passed main CI `30087883412`. The card is merged
verified. Finalization `27ff7803629e7a9b92ac21ac30a0d5ed661cddca`
passed exact-head CI `30087966580`. This commit is the close record; the exact
terminal merge and its authoritative-main CI remain pending, so no G1
authority is claimed yet.
