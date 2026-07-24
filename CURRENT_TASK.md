# Current AG Task

- Task ID: `G0-T05`
- Gate: G0
- Risk: `D0`
- Status: `awaiting_review`
- Baseline: `dcb942a80a91312fad12d90b5e362cbdd0611017`

## Implementation boundary

The product owner has separately started Package A G0-T05 generation 3
implementation after the authorization activation merged as authoritative main
`5f0ee4721bdd5baa89a9711ed740f751dcda00ef`.

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

## Delivery and stop boundary

Implementation `05de8b08529bac32967db2ac0c8342cc005593de` and delivery
must remain a strict single-parent lineage from
the activation main. The cumulative changed paths must stay inside the frozen
seven-path allowlist, while the activation receipt, manifest/schema blobs,
ruleset identity, Package order, capability ceiling, and existing history stay
unchanged.

This delivery stops at `awaiting_review` until exact-head CI and independent
code/security `APPROVE` plus architecture/route `CLEAR`. G1-T01,
workflow/ruleset mutation, product code, network, credentials, trading,
deployment, release, and system modification remain forbidden.
