# Current AG Task

## Task identity

- Task ID: `G0-T04`
- Gate: G0 governance anomaly recovery
- Risk: `D0`
- Status: `authorized`
- Candidate generation: `4`
- Baseline: `1671568fd5bb33d1e316f8cbe8e9708d7d4d5d1f`
- Exact terminal-blocked record:
  `a88b4f9e5fa7d498aeb338ec9e8bbbe198241a87`

## Single goal

Close G0-T04 generation 4 without rewriting the exact PR #15 through #23
history. Preserve the anomaly receipt/seal and inactive Package A blobs, add
the newly observed owner authority as future activation input only, and create
the protected-main bridge required for a fresh canonical Package A route.

## Current truth

- Reviews for PR #15, #17, #19, #20, #21, and #22 are all empty.
- Exact reviewed candidate `6541189bbdacc870de5691d07991b9103ee2c763`
  passed PR #23 run `30005396033`, main verification, independent
  code/security `APPROVE`, and architecture/route `CLEAR_FOR_SEAL`.
- Those candidate results authorize only the later Stage-2 seal `S`; they do
  not accept, merge, close, or expand G0-T04.
- The product owner has now explicitly reconfirmed Package A payload
  `815a40dc1fb47b367e1fe5707c16911862feeb929b0356aff769d0544500ca27`
  and separately authorized this generation-4 governance recovery. This
  authorization does not resurrect the deleted activation record.
- Package A payload
  `815a40dc1fb47b367e1fe5707c16911862feeb929b0356aff769d0544500ca27`
  remains byte-frozen but `not_authorized`.
- `G0-T05` is `not_authorized`.
- `G1-T01` and all later work are `not_authorized`.
- Capability remains capped at `OFFLINE_EVIDENCE_ACCEPTED`.

The immutable anomaly receipt is
`evidence/g0-t04/pr15-pr22-review-chain.json`. The false activation assertion
previously stored at `evidence/g0-t05/package-a-activation.json` is absent from
the recovery tree but remains permanently visible in Git history.
The later review seal is
`evidence/g0-t04/pr15-pr22-recovery-seal.json`.

## Exact generation-4 topology

1. This authorization record has ordered parents
   `[1671568fd5bb33d1e316f8cbe8e9708d7d4d5d1f,
   a88b4f9e5fa7d498aeb338ec9e8bbbe198241a87]`, advances generation 3 terminal
   blocked history to generation 4 `authorized`, and clears all prior
   candidate/CI/review/blocker slots.
2. The implementation/start/delivery chain is single-parent from this record
   and may modify only the frozen generation-4 allowlist.
3. Candidate exact-HEAD CI and independent code/security `APPROVE` plus
   architecture/route `CLEAR` precede acceptance.
4. Protected-main integration must use ordered parents
   `[a88b4f9e5fa7d498aeb338ec9e8bbbe198241a87, accepted-generation-4]`
   with a tree exactly equal to the accepted second parent.
5. G0-T04 must complete merged-main and finalization CI before a new activation
   record may bind the reconfirmed Package A payload to the new close.

## Frozen allowlist

- `PROJECT_STATUS.yaml`
- `CURRENT_TASK.md`
- `PROJECT_MEMORY.md`
- `docs/NEXT_WORKFLOW.md`
- `evidence/g0-t04/pr15-pr22-recovery-seal.json`
- `evidence/g0-t04/generation-4-route-seal.json`
- `scripts/validate_project_status.py`
- `tests/test_g0_project_status.py`

## Forbidden scope

- No G0-T05 or G1 implementation before this G0-T04 generation is closed.
- No Package A activation in this generation; owner confirmation is recorded
  only as authority for a future fresh activation bound to the new close.
- No manifest/schema/order/payload mutation.
- No workflow, required-check, ruleset, repository-setting, or remote mutation.
- No business, strategy, adapter, API, persistence, frontend, notification, or
  observability implementation.
- No market network access, credentials, accounts, orders, leverage, shorting,
  trading, paid resources, deployment, release, or `LOCAL-PREVIEW`.

## Verification and stop conditions

- Exact topology, receipt bytes, Package blobs, ruleset identity, activation
  neutralization, status, ledger, and cumulative allowlist must all validate.
- Required commands:
  - `python3 scripts/validate_project_status.py --repo-root . PROJECT_STATUS.yaml`
  - `python3 -m pytest -q tests/test_g0_project_status.py -k 'pr15_pr22 or transition_ledger'`
  - `python3 -m pytest -q --ignore=tests/test_api_transport.py --ignore=tests/test_m5_transport.py`
  - `npm --prefix frontend test -- --run`
  - `npm --prefix frontend run build`
  - `python3 -m compileall -q scripts tests`
  - `git diff --check`
- Any failed test, review, topology, identity, blob, ruleset, allowlist, or
  authority check returns only this G0-T04 card.
- The product owner authorizes automatic push, PR, exact-HEAD CI, independent
  dual review, protected-main merge, merged-main/finalization CI and close for
  this generation only.
- Stop before creating the fresh Package A activation until G0-T04 is closed.
