# Current AG Task

## Task identity

- Task ID: `G0-T01`
- Gate: G0 governance baseline
- Risk: `D0`
- Status: `awaiting_review`
- Executor: one bounded developer AG
- Reviewer: main Codex plus independent code/security and architecture lanes
- Authorization: user explicitly authorized G0 on 2026-07-21 Asia/Shanghai
- Baseline: `7aadae13efd45023d19bf8a280f7680667c930fa`

## Goal

Create the smallest canonical, machine-validatable governance source of truth
for this repository, migrate the approved beginner-first product and G0-G9
route into formal repository documents, and map legacy M0-M7 evidence without
upgrading its maturity.

This card establishes governance only. It does not establish bootstrap CI,
GitHub branch protection, integration, continuous Paper validation, or release
readiness.

## Required deliverables

1. Add root `PROJECT_STATUS.yaml` as the only mutable current-state source.
   It must identify G0, exactly one active task (`G0-T01`), D0 risk, the legal
   task state, evidence SHA fields, reviewer/CI state, capability maturity,
   blockers, and next authorization.
2. Add a versioned status schema and an offline validator with deterministic,
   fail-closed diagnostics. Avoid a new unpinned runtime dependency; a
   JSON-compatible YAML representation plus Python standard library is
   acceptable for this bootstrap card.
3. Validate at least: unknown states, illegal transitions, multiple active
   tasks, missing or malformed SHA fields when required, missing reviewer/CI
   evidence when required, conflicting current-state claims in governed
   documents, and invalid maturity upgrades.
4. Encode the legal lifecycle:
   `planned -> authorized -> in_progress -> awaiting_review -> returned | blocked | accepted_pending_merge -> merged_verified -> closed`.
   `closed` may only follow `merged_verified`; returned candidates invalidate
   prior CI and review identity.
5. Add a legacy M0-M7 evidence map. Historical accepted work may be represented
   only as `OFFLINE_EVIDENCE_ACCEPTED`; L0 remains the documented legacy-local
   exception and must not be rewritten as exact-HEAD remote CI evidence.
6. Replace stale M-era current-route claims in governance documents with the
   approved G0-G9 route and one-card closure loop. `PROJECT_MEMORY.md` remains
   historical facts; `CURRENT_TASK.md` remains the task card; neither may
   compete with `PROJECT_STATUS.yaml` for current machine state.
7. Synchronize the approved beginner-first contract into formal `DESIGN.md`:
   one product and one signal truth source; default view answers whether a
   confirmed long signal exists; professional metrics and internal terms are
   hidden behind progressive disclosure; no beginner/expert split.
8. Add deterministic tests/fixtures for valid and adversarial status examples,
   and update `PROJECT_MEMORY.md` with delivery evidence without self-approval.

## Allowed scope

- `PROJECT_STATUS.yaml`
- `schemas/project_status.schema.json`
- `scripts/validate_project_status.py`
- status-validator tests and fixtures under `tests/` and `fixtures/g0/`
- `docs/LEGACY_EVIDENCE_MAP.md`
- `AGENTS.md`
- `DEVELOPMENT_WORKFLOW.md`
- `AG_WORK_LOOP.md`
- `DESIGN.md`
- `CURRENT_TASK.md`
- `PROJECT_MEMORY.md`

New files equivalent to the named schema, validator, fixture, test, or mapping
paths are allowed only when the developer explains why the exact path differs.

## Forbidden scope

- No `.github/workflows`, GitHub settings, branch-protection mutation, PR merge,
  supervisor/scheduler/heartbeat implementation, deployment, or release work.
- No exchange network request, private API, credential, order, leverage, short
  logic, strategy threshold, signal algorithm, database, notification provider,
  frontend feature, or live/Paper runtime change.
- No claim that G0 is complete, CI is active, branch protection exists, or the
  product is integration/Paper/release ready.
- Do not modify existing business implementation, contracts, M1-M7 fixtures,
  backend tests, frontend source, dependency locks, or automation scripts.
- Do not start `G0-T02` or any G1+ work.

## Acceptance checks

- Validator accepts the canonical repository state and deterministic valid
  fixtures, and rejects every required adversarial fixture with stable,
  sanitized diagnostics and a non-zero exit status.
- Schema and validator agree; unknown keys and ambiguous/coercible field types
  fail closed.
- A repository/document conflict check finds zero stale current-stage claims in
  governed documents while preserving clearly labelled history.
- Legacy mapping contains traceable evidence and never upgrades M0-M7 above
  `OFFLINE_EVIDENCE_ACCEPTED`.
- Beginner-facing design contains the confirmed information hierarchy, six-item
  signal-card budget, plain-language state translations, progressive disclosure,
  and one-truth-source rule.
- Focused G0 tests, all existing backend tests, frontend tests/build, M1 fixture
  validation, Python compilation, `git diff --check`, allowed-scope scan,
  forbidden-feature scan, and tracked-secret scan pass.
- Delivery is on task branch `codex/g0-t01-canonical-status`, with an immutable
  candidate commit pushed to origin and a complete report. The developer must
  set the task/status to `awaiting_review` but must not write `accepted`.

## Required delivery report

Report task ID, files changed, decisions, exact commands/results, candidate SHA,
branch/upstream status, PR status if one exists, risks/blockers, worktree status,
and memory update. Stop after delivery and wait for independent review.

## Independent review result: returned

- Reviewed exact PR head:
  `6be3e708ad019b46685e3a7986a828df7103239d`.
- Code/security verdict: `REQUEST CHANGES`.
- Architecture/route status: `BLOCK`.
- The product route, beginner-first design, allowed scope, legacy maturity cap,
  focused tests, backend tests, frontend tests/build, and local static checks are
  not the reason for return.

### Repair requirements

1. Make candidate identity executable: the delivered PR exact head is the review
   subject. A prior implementation/content commit may be recorded separately,
   but cannot masquerade as the exact delivered candidate. Do not require any
   commit to contain its own SHA.
2. Replace the single CI object with phase-specific evidence for candidate,
   closure, merged-main, finalization/close D0 as required by the formal loop.
   Define which later commit records each already-existing SHA, and validate Git
   object existence, ancestry, phase, and subject identity when repository
   checks are enabled. Fabricated unrelated SHAs must fail.
3. Resolve the bootstrap deadlock explicitly. G0-T01 is forbidden from creating
   CI, while normal acceptance requires CI. Define one narrow, machine-checked,
   non-reusable G0-T01 bootstrap exception bound to this task, authorization
   baseline, independent dual review, local evidence, and offline maturity. It
   must not relax G0-T02 or any later task.
4. A `returned` state must retain a negative review bound to the exact returned
   candidate and reject pending reviewers or unrelated/success CI. Starting a
   repair must atomically clear old candidate/review/CI identities and increment
   generation.
5. Enforce maturity ceilings across G0-G9. G0-G5 cannot exceed offline evidence;
   G6-G7 cannot exceed integration; G8 cannot exceed Paper validated; G9
   `RELEASE_READY` requires explicit product-owner go and complete release
   evidence.
6. Make document conflict validation structural for every permitted current
   mirror; otherwise forbid current-state claims. Include `PROJECT_MEMORY.md` in
   its historical-only rule. A canonical G0 state must reject conflicting G9,
   task, status, or maturity claims.
7. Add architecture `watch` as a faithful, non-mergeable review result. Validate
   `next_authorization.gate` against its task prefix and permitted route.
8. Catch unreadable/non-UTF-8 governed documents and return a stable sanitized
   validation failure without traceback.
9. Add adversarial tests for every defect above, preserve all existing passing
   behavior, rerun the complete original acceptance set, update status/memory,
   push a new immutable delivery head to the same PR, and stop at
   `awaiting_review`. Do not start G0-T02.

## Generation 2 independent review result: returned

- Reviewed exact delivered head:
  `e2d948f5919a02d9db0abc4aefa00ae28ac03b3d`.
- Code/security verdict: `REQUEST CHANGES`.
- Architecture/route status: `BLOCK`.
- Generation 2 repaired self-referential phase identity, distinct phase CI
  slots, bootstrap handling, returned evidence shape, architecture WATCH,
  maturity ceilings, next-gate checks, and document decoding.

### Generation 3 repair requirements

1. In repository-aware mode, read the direct first parent's committed
   `PROJECT_STATUS.yaml`. Require immutable project/task/gate/risk/baseline and
   bootstrap identity continuity; require `transition.from == parent.state`;
   require generation unchanged for ordinary transitions and exactly parent + 1
   for `returned -> in_progress`. Reject jumps, reuse, rollback, or reappearance
   of a consumed bootstrap exception. Repair start must also clear blockers.
2. Bind `merged_main` to an explicit authoritative main ref. A merge commit only
   reachable from a task/fake branch must fail. Add off-main regression coverage.
3. Bind every active CI identity to the canonical repository remote: URL owner
   and repository must match GitHub origin, URL run number must equal `run_id`,
   and phase `subject_sha` must remain exact.
4. Make the canonical governed-document set mandatory and unique. It must
   include `AGENTS.md`, `DEVELOPMENT_WORKFLOW.md`, `AG_WORK_LOOP.md`, `DESIGN.md`,
   `CURRENT_TASK.md`, and `PROJECT_MEMORY.md`; entries may not be removed,
   duplicated, aliased, or replaced to disable conflict validation.
5. Replace G9 owner-go and release-complete booleans with traceable immutable
   approval and release evidence identities. `RELEASE_READY` must not be
   reachable by self-asserting two booleans.
6. Strengthen phase-subject continuity to include project, current gate, risk,
   implementation SHA, and bootstrap identity. Add rewrite regressions.
7. Require same-gate `next_authorization` task sequence to move forward, and
   reject leftover blockers in normal `in_progress` repair state.
8. Preserve all passing checks; update status/memory, deliver a new exact PR
   head on the same branch, and stop at `awaiting_review`. No G0-T02.
