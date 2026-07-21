# Current AG Task

## Task identity

- Task ID: `G0-T01`
- Gate: G0 governance baseline
- Risk: `D0`
- Status: `authorized`
- Executor: one bounded developer AG
- Reviewer: main Codex plus independent code/security and architecture lanes
- Authorization: user explicitly authorized G0 on 2026-07-21 Asia/Shanghai
- Baseline: `e2e0b489e1fbf555c4405f58ec1ab8d20f77199f`

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
