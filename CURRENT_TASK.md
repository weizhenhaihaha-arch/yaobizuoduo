# Current AG Task

## Task identity

- Task ID: `G0-T04`
- Gate: G0 governance anomaly recovery
- Risk: `D0`
- Status: `in_progress`
- Candidate generation: `4`
- Baseline: `1671568fd5bb33d1e316f8cbe8e9708d7d4d5d1f`
- Exact terminal-blocked main:
  `414fa392026c71b01378c64cbf62cb6b304b2eed`
- Exact premature generation-4 main:
  `8a7b8aca2b59a5598f0e721f557c06a008f362e0`

## Single goal

Close G0-T04 generation 4 without rewriting PR #15 through #24 or the
abandoned off-main generation-4 chain. Preserve every anomaly receipt/seal and
inactive Package A blob, bind the newly observed owner authority as future
activation input only, and create the protected-main bridge required for a
fresh canonical Package A route.

## Current truth

- Reviews for PR #15, #17, #19, #20, #21, #22, and #24 are all empty.
- Exact reviewed candidate `6541189bbdacc870de5691d07991b9103ee2c763`
  passed PR #23 run `30005396033`, main verification, independent
  code/security `APPROVE`, and architecture/route `CLEAR_FOR_SEAL`.
- PR #24 head `db507f75f46196a03a9d87725be5946e6f05575c` passed exact-head
  run `30014856791` and merged as `414fa392026c71b01378c64cbf62cb6b304b2eed`
  with ordered parents `[a88b4f9e5fa7d498aeb338ec9e8bbbe198241a87,
  db507f75f46196a03a9d87725be5946e6f05575c]`, but its GitHub review
  list is empty. It is immutable main-drift history, not reviewed acceptance.
- The prior off-main generation-4 route
  `de070276e53ec75f0cfd864a02d6d05236784eb8 -> 45e714f9e099774ac0c4885f77523fb73c2d313d`
  is preserved but abandoned. It cannot be merged, reused, or treated as
  current candidate evidence.
- The product owner reconfirmed Package A payload
  `815a40dc1fb47b367e1fe5707c16911862feeb929b0356aff769d0544500ca27`
  and explicitly authorized this main-drift reconciliation. This does not
  resurrect the deleted activation record.
- Package A remains byte-frozen and `not_authorized`; `G0-T05` and `G1-T01`
  remain `not_authorized` until this generation fully closes.
- Capability remains capped at `OFFLINE_EVIDENCE_ACCEPTED`; G2 remains
  forbidden.
- PR #26 merged the still-`in_progress` repair head
  `c22bc286b2ee30a0cdaf40a82223bc6f15133af5` prematurely as
  `8a7b8aca2b59a5598f0e721f557c06a008f362e0`, with ordered parents
  `[414fa392026c71b01378c64cbf62cb6b304b2eed,
  c22bc286b2ee30a0cdaf40a82223bc6f15133af5]` and tree
  `930c41200f0f94fb64e40aa19d3adc4323f8276c`. PR run `30028693653`
  is anomaly history only; push/main run `30028739788` failed canonical
  validation. Neither fact is acceptance.

## Exact generation-4 topology

1. This authorization record has ordered parents
   `[1671568fd5bb33d1e316f8cbe8e9708d7d4d5d1f,
   414fa392026c71b01378c64cbf62cb6b304b2eed]`, advances the generation-3
   terminal blocked state to generation 4 `authorized`, and clears candidate,
   CI, review, and blocker slots.
2. The implementation/start/delivery chain is single-parent from this record
   and may modify only the frozen generation-4 allowlist.
3. Candidate exact-HEAD CI and independent code/security `APPROVE` plus
   architecture/route `CLEAR` precede acceptance.
4. Protected-main integration must use ordered parents
   `[414fa392026c71b01378c64cbf62cb6b304b2eed, accepted-generation-4]`
   with a tree exactly equal to the accepted second parent.
5. G0-T04 must complete merged-main and finalization CI before a fresh
   activation may bind the reconfirmed Package A payload to the new close.

## Premature-main recovery route

1. The immutable recovery receipt freezes exact F
   `8a7b8aca2b59a5598f0e721f557c06a008f362e0`, its parents/tree, PR #26
   head/run, and failed push/main run.
2. Only a strict single-parent recovery lineage may follow F. The ordinary
   `in_progress` merge F is anomaly history and never merge authority.
3. Recovery delivery remains `awaiting_review`, with candidate identity
   implicit in the delivery HEAD, CI `not_run`, both reviewers pending, and
   the exact failed-main blocker retained.
4. A future protected-main bridge is valid only as
   `[F, accepted-generation-4-recovery]` with tree equal to its second parent.
   This card does not create that acceptance or bridge.

## Frozen allowlist

- `PROJECT_STATUS.yaml`
- `CURRENT_TASK.md`
- `PROJECT_MEMORY.md`
- `docs/NEXT_WORKFLOW.md`
- `evidence/g0-t04/generation-4-premature-merge-recovery.json`
- `scripts/validate_project_status.py`
- `tests/test_g0_project_status.py`

## Forbidden scope

- No G0-T05 or G1 implementation before this G0-T04 generation is closed.
- No Package A activation in this generation and no old activation reuse.
- No manifest/schema/order/payload mutation.
- No workflow, required-check, ruleset, repository-setting, or unrelated
  remote mutation.
- No business, strategy, adapter, API, persistence, frontend, notification, or
  observability implementation.
- No market API, credentials, accounts, orders, leverage, trading, paid
  resources, deployment, release, local-system change, or `LOCAL-PREVIEW`.

## Verification and stop conditions

- Exact topology, PR #24 identity, abandoned-chain identity, Package blobs,
  activation absence, ledger, and cumulative allowlist must all validate.
- Required commands:
  - `python3 scripts/validate_project_status.py --repo-root . PROJECT_STATUS.yaml`
  - `python3 -m pytest -q tests/test_g0_project_status.py -k 'pr15_pr22 or transition_ledger or generation4'`
  - `python3 -m pytest -q --ignore=tests/test_api_transport.py --ignore=tests/test_m5_transport.py`
  - `npm --prefix frontend test -- --run`
  - `npm --prefix frontend run build`
  - `python3 -m compileall -q scripts tests`
  - `git diff --check`
- Any failed test, review, topology, identity, blob, allowlist, or authority
  check returns only this G0-T04 card.
- The product owner authorizes automatic push, PR, exact-HEAD CI, independent
  dual review, protected-main merge, merged-main/finalization CI, fresh Package
  A activation, G0-T05 rerun, and G1-T01 generation-2 reconciliation within
  the previously frozen boundaries.
