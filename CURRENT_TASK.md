# Current AG Task

## Task identity

- Task ID: `G0-T02`
- Gate: G0 governance baseline and minimal remote CI
- Risk: `D2`
- Status: `awaiting_review`
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
