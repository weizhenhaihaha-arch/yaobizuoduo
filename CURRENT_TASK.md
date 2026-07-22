# Current AG Task

## Task identity

- Task ID: `G0-T02`
- Gate: G0 governance baseline and minimal remote CI
- Risk: `D2`
- Status: `closed`
- Finalization mode: completed exact non-self-referential G0-T02 closure
- Candidate generation: `5` detached-HEAD guard repair
- Executor: one bounded developer AG
- Reviewer: main Codex plus independent code/security and architecture lanes
- Authorization: user explicitly authorized the scheduled G0-T02 workflow on 2026-07-22 Asia/Shanghai
- Baseline: `94892d79b8d39ac1726cf657fac0ae76a0e27b37`

## Goal

Establish the smallest real GitHub Actions exact-HEAD CI trust anchor for this
repository. Freeze one stable aggregate check context that later G1 tasks may
expand internally without renaming. This task does not configure branch
protection and does not establish live, Paper, deployment, or release maturity.

## Required deliverables

1. Add one minimal GitHub Actions workflow for pull requests and pushes to
   canonical `main`.
2. For pull requests, checkout and assert the exact
   `github.event.pull_request.head.sha`; never treat a merge-preview ref as the
   candidate. For pushes, assert the subject is `github.sha`.
3. Run a minimal dependency-light governance verification set: canonical status
   validation, repository/Git identity checks, and deterministic checks needed
   to prove the workflow itself. Full cross-platform product verification stays
   in G1.
4. Freeze one aggregate check name. G1 may add internal jobs but may not silently
   rename the aggregate context after it becomes a required check. The frozen
   aggregate job/check name is `G0 / exact-head`.
5. Use read-only repository permissions, require no secrets, disable checkout
   credential persistence, pin every action to a full immutable commit SHA, and
   support fork pull requests without secrets.
6. Record real repository, event, subject SHA, run ID and run URL evidence.
   Cancelled, skipped, neutral, stale, or mismatched runs are not success.
7. Preserve the non-self-referential phase sequence: delivery HEAD -> candidate
   CI -> later review/closure record -> closure CI -> fixed merge -> merged-main
   CI -> finalization record -> finalization D0 CI -> later close record.
8. Update `PROJECT_MEMORY.md` with delivery facts without self-approval.

## Allowed scope

- `.github/workflows/` for the single minimal CI workflow
- focused workflow/governance tests or fixtures required to verify exact subject,
  permissions, immutable action pins, and stable aggregate identity
- `PROJECT_STATUS.yaml`
- `CURRENT_TASK.md`
- `PROJECT_MEMORY.md`
- narrowly necessary governance documentation that describes the fixed check

## Forbidden scope

- No GitHub ruleset or classic branch-protection mutation; that is G0-T03 and
  requires separate product-owner authorization.
- No G1 dependency/runtime freeze or full validation-entry implementation.
- No business logic, strategy threshold, UI feature, database, notification,
  scheduler, deployment, or release change.
- No live/public exchange collection, private API, credential, order, leverage,
  short signal, real trading, profit, or accuracy claim.
- Do not merge `codex/local-preview-01`, copy its changes into this card, start
  G0-T03, or start any G1+ work.
- The consumed G0-T01 no-CI exception is retired and must not be reused.

## Acceptance checks

- Canonical repository-aware status validation passes from the exact task head.
- Local focused checks and the unchanged existing backend/frontend baseline pass.
- Workflow permissions are read-only, checkout credentials are not persisted,
  no secrets are referenced, and all actions are pinned to full commit SHAs.
- PR CI proves checked-out `HEAD` equals the exact PR head SHA; push CI proves
  checked-out `HEAD` equals `github.sha`.
- Fork PR operation requires no secrets.
- The aggregate check context is stable and only strict success is accepted.
- Candidate, closure, merged-main and finalization D0 evidence bind the real
  owner/repository, run ID, URL, event and subject SHA in the required order.
- Main Codex exact-head verification passes; independent code/security returns
  `APPROVE`; independent architecture/route returns `CLEAR`.
- Final closure requires clean `main == origin/main` and successful exact-head
  CI for every required phase.

## Stop conditions

- Stop and report `BLOCKED` if GitHub Actions, repository, PR, push, or runner
  access cannot provide real exact-subject evidence.
- Stop if any run identity or aggregate check name drifts, or any required run
  is not strict success.
- Stop if the workflow needs secrets, write permissions, a private API, or any
  forbidden product capability.
- Any `REQUEST CHANGES`, `WATCH`, or `BLOCK` returns only G0-T02 for repair.
- Do not dispatch G0-T03 without a new explicit user authorization.

## Required delivery report

Report task ID, files changed, exact commands/results, implementation SHA,
delivery/candidate SHA, branch/upstream and PR state, real CI run identities,
aggregate check name, risks/blockers, worktree state, and memory update. Stop
after delivery and wait for main and independent review.

## Resolved generation-1 blocker

The generation-1 local implementation commit was
`5f3a6e93b69947b73e21e51c7e0218c0c283f6de`, but GitHub rejected its push
because the current OAuth App is not authorized with `workflow` scope. No PR or
real exact-HEAD Actions run existed for that commit at that point. The product
owner then explicitly selected a new-generation reauthorization after the
GitHub credential was reauthorized. Generation 1 remains terminal at blocked
record `925fa94c22dfabc8ccd2dbe99fde74ca0c88a12f`; generation 2 starts from the
last canonical close with that blocked record as the immutable second parent.
This does not add a `blocked -> in_progress` transition or rewrite blocked
history.

## Generation 2 review result: returned

- Reviewed exact PR head: `d069c5158c1698f9c496eefe020e153a90d27c1b`.
- Real Actions run: `29882571168` at
  `https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/29882571168`.
- Exact-subject verification succeeded for the pull-request head, canonical
  repository, event, run identity, and read-only checkout.
- The aggregate check `G0 / exact-head` failed because detached exact-head
  checkout did not create local `refs/heads/main`; repository-aware validation
  reported `$.authoritative_main_ref: authoritative main ref does not exist`.
- Verdict: code/security `REQUEST CHANGES`, architecture/route `WATCH`.
- Repair is limited to materializing local `refs/heads/main` from fetched
  `refs/remotes/origin/main` without moving detached `HEAD`, with focused static
  and behavior regression coverage. Return only this G0-T02 generation for
repair; do not start G0-T03 or G1.

## Generation 3 independent review result: returned

- Reviewed exact PR head: `62d7dc485b0d068b83a50d565d869f613248626b`.
- Real strict-success Actions run: `29882992116` at
  `https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/29882992116`.
- Main verification passed 173 Python tests, 10 frontend tests, TypeScript/Vite
  build, repository-aware validation, exact remote identity, and diff checks.
- Architecture/route verdict: `CLEAR`.
- Code/security verdict: `REQUEST CHANGES`. `materialize_authoritative_main`
  unconditionally overwrites an existing divergent local `refs/heads/main`.
  Repair must create local main only when absent, accept it only when already
  equal to fetched origin/main, and otherwise fail closed without moving local
  main or detached HEAD. Add behavior regression coverage. The duplicated
  paragraph in `AG_WORK_LOOP.md` may be removed as a non-blocking cleanup.
- Return only this G0-T02 generation for repair; do not start G0-T03 or G1.

## Generation 5 independent review result: accepted pending merge

- Reviewed exact PR head: `35b90f87ab42843925065e6d0dafdc25797702e0`.
- Real strict-success candidate run: `29884205742`.
- Main verification passed 178 Python tests, 10 frontend tests, TypeScript/Vite
  build, repository-aware validation, exact repository/run identity and diff
  checks.
- Independent code/security verdict: `APPROVE`.
- Independent architecture/route verdict: `CLEAR`.
- The old terminal blocked branch remains fixed at `925fa94`; the capability
  ceiling remains `OFFLINE_EVIDENCE_ACCEPTED`; G0-T03 and G1 remain
  unauthorized. This record is not merge authorization.

## Exact authoritative-main merge recovery

- GitHub merged PR #2 as `608800462fbf9f3b97277484fa906a691b8b8b98`.
- The merge is a canonical two-parent G0 bridge: first parent
  `94892d79b8d39ac1726cf657fac0ae76a0e27b37`, second parent accepted record
  `41868a5eff635d9f83dccaba4ad3e6e38433822c`, and the merge tree/status exactly
  equal that accepted record. The accepted record directly closes reviewed
  candidate `35b90f87ab42843925065e6d0dafdc25797702e0`.
- Authoritative-main `push` run `29884710636` for exact subject `6088004` failed
  in canonical status validation because the merge bridge was restricted to
  G0-T01. URL:
  `https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/29884710636`.
- The task remains `accepted_pending_merge`; the exact accepted candidate,
  successful candidate CI and dual-clear review remain immutable. Closure,
  merged-main success and finalization are still not established. The sole
  blocker is the exact failed-main recovery recorded in `PROJECT_STATUS.yaml`.
- Recovery is limited to generalizing the strict G0 merge bridge and accepting
  this one repository-bound failed-run transition. Ordinary return, a fake or
  successful run, a non-main subject, G0-T03, G1, live data and trading remain
  unauthorized.

## Recovery merge verified; finalization subject pending CI

- PR #3 recovery merged as exact authoritative-main commit
  `c5a488482fffb7183790f36701411d91b2a2bba0`; first parent is failed merge
  `608800462fbf9f3b97277484fa906a691b8b8b98`, second parent is recovery
  acceptance `d501ba25f7fa6945be3f0c4eb415074ad20a51e4`, and its tree equals the
  second parent.
- Closure evidence is accepted record
  `41868a5eff635d9f83dccaba4ad3e6e38433822c` with strict-success exact PR run
  `29884474658`.
- Merged-main evidence is `c5a488482fffb7183790f36701411d91b2a2bba0`
  with strict-success exact `push/main` run `29887948168`.
- The recovery blocker is resolved and cleared. Candidate
  `35b90f87ab42843925065e6d0dafdc25797702e0`, candidate run `29884205742`,
  code/security `APPROVE` and architecture `CLEAR` remain unchanged.
- This record is the `merged_verified` finalization subject. Its own PR run must
  succeed before a later `closed` record may bind it as finalization evidence.
  G0-T03 and G1 remain `not_authorized`.

## Finalization verified and task closed

- Exact `merged_verified` finalization subject:
  `0a8048df7197ece027287c3397783f37630ff0e6`.
- Its strict-success pull-request run is `29888131234` at
  `https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/29888131234`;
  aggregate check `G0 / exact-head` completed successfully.
- This later record transitions `merged_verified -> closed` and binds that
  immutable subject/run as finalization evidence. Candidate, closure,
  merged-main and all CI identities remain unchanged.
- Closing G0-T02 does not authorize or dispatch G0-T03 or G1. The capability
  maturity remains `OFFLINE_EVIDENCE_ACCEPTED`; no live, deployment, release or
  trading readiness is established.

## Exact final-close merge recovery

- GitHub merged PR #4 as `d0dcc837715ea29c7b08f9ef6a7212894e4098bb`.
  It has exact first parent `c5a488482fffb7183790f36701411d91b2a2bba0`,
  exact second parent closed record
  `231d3d0e4756889e8fa3fc5803df6701088556e8`, and a tree/status identical to
  that second parent.
- Exact `push/main` run `29888938625` for subject `d0dcc83` established the
  real event and subject identity, then failed only because direct-first-parent
  validation expected the first parent's `accepted_pending_merge` state rather
  than recognizing the bounded final-close bridge.
- Recovery is restricted to that exact bridge and a status-identical,
  single-parent repair line followed by one exact two-parent repair merge.
  Wrong/swapped parents, tree or status substitution, wrong finalization/run,
  non-main subjects, ordinary closed merges, and forged descendants remain
  fail closed.
- `PROJECT_STATUS.yaml` remains the immutable `closed` record: candidate,
  closure, merged-main, finalization, dual-clear review, capability ceiling and
  `G0-T03 not_authorized` evidence are unchanged. This repair does not start a
  new lifecycle transition or authorize G0-T03/G1.

## Generation 4 independent review result: returned

- Reviewed exact PR head: `66176e228331d77f9404d2976a0227b43ad3d9c4`.
- Real strict-success Actions run: `29883755366`.
- Main verification passed 176 Python tests, 10 frontend tests, TypeScript/Vite
  build, repository-aware validation and exact repository/run checks.
- Architecture/route verdict: `CLEAR`.
- Code/security verdict: `REQUEST CHANGES`. The helper returns early when an
  existing local main already equals origin/main, before confirming that HEAD
  is detached. An attached candidate branch can therefore bypass the intended
  fail-closed guard. Move detached-HEAD verification before every local-main
  branch and add attached plus existing-equal/divergent preservation tests.
- Return only this G0-T02 generation for repair; do not start G0-T03 or G1.
