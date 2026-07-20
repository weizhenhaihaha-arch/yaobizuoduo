# Current AG Task

## Task

- Task ID: `M5-T01`
- Milestone: M5 backend API and real-time event boundary
- Status: repair_requested
- Executor: execution AG `Aquinas`
- Reviewer: main AG
- Previous task result: `M4-T01` passed main AG audit; M5 is now authorized

## Goal

Implement the read-only API service boundary and DTOs that expose dashboard, signal detail, history, outcomes, statistics, and health without moving strategy logic into the API layer.

## Allowed scope

- Compose approved M1-M4 records into stable versioned response models
- Implement confirmed/potential/no-signal grouping and priority sorting
- Include Binance/OKX text badges, freshness, data-health, reason codes, entry reference, invalidation, and outcome completeness
- Define read-only event messages for new signal, weakening, invalidation, and stale data
- Keep storage and web-framework transport behind interfaces; use offline tests
- Update `PROJECT_MEMORY.md` with durable facts only

## Forbidden scope

- No frontend implementation
- No strategy calculations or threshold changes in the API layer
- No live exchange client, real orders, credentials, leverage, or short strategy
- No profitability or accuracy claims
- No fake production data

## Acceptance criteria

- Dashboard groups and sorting match the approved beginner-first product rules
- API DTOs expose all user decisions without requiring frontend strategy calculations
- Data-health and stale states fail closed
- Outcome responses distinguish price observations, incomplete windows, and not-evaluated strategy PnL
- Offline tests cover grouping, ordering, exchange badges, stale data, invalidation, empty state, and outcome semantics
- Unit tests, fixture validation, `git diff --check`, scope, and secret checks pass
- Report changed files, commands, results, risks, branch, commit, workspace status, and memory sync

## Required report

Use the report structure in `AG_WORK_LOOP.md`. Do not proceed to frontend or live transport before main AG approval.

## Main AG review

- Review time: 2026-07-20 14:00 Asia/Shanghai
- Result: repair requested; M5-T02 remains blocked
- Confirmed checks: 23 unit tests passed, M1 fixture validation passed, `git diff --check` passed, and forbidden-scope scan found no trading, credentials, frontend, or live transport implementation
- Blocking defect: an `armed` record with `freshness_status=stale` and `usable_for_signal=true` is returned with `can_consider_entry=true`, violating the fail-closed acceptance criterion
- Required repair: derive entry usability defensively so stale/unusable/unsupported-exchange records can never advise entry, add focused regression tests, and preserve the read-only transport-agnostic boundary
