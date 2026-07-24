# Current AG Task

- Task ID: `G0-T05`
- Gate: G0
- Risk: `D0`
- Status: `authorized`
- Baseline: `dcb942a80a91312fad12d90b5e362cbdd0611017`

## Authorization-only boundary

This record authorizes only Package A G0-T05 generation 3 governance. G0-T05
implementation has not started.

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

## Exact changed paths

- `PROJECT_STATUS.yaml`
- `CURRENT_TASK.md`
- `PROJECT_MEMORY.md`
- `docs/NEXT_WORKFLOW.md`
- `evidence/g0-t05/package-a-activation.json`
- `scripts/validate_project_status.py`
- `tests/test_g0_project_status.py`

## Stop boundary

The authorization candidate must be the strict direct child of N. During
review, local main and origin/main remain N. A future protected-main merge is
valid only as `[N, accepted-authorization]` with the second-parent tree.
G0-T05 implementation, G1-T01, workflow/ruleset mutation, product code,
network, credentials, trading, deployment, release, and system modification
remain forbidden.
