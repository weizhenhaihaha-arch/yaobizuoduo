# Current AG Task

## Task

- Task ID: `M4-T01`
- Milestone: M4 historical replay and outcome statistics
- Status: dispatched
- Executor: execution AG `Aquinas`
- Reviewer: main AG
- Previous task result: `M3-T01` passed main AG audit; M4 is now authorized

## Goal

Implement deterministic historical replay and signal-outcome records for the fixed 5m, 15m, 1h, 4h, and 1d windows without claiming profitability.

## Allowed scope

- Replay normalized snapshots through the approved M3 lifecycle using event and availability time
- Record confirmation-time entry reference, window-end change, maximum rise, maximum drawdown, peak time, completeness, missing-data status, and invalidation events
- Keep price-observation outcomes separate from simulated strategy results
- Mark strategy result as not evaluated until fee, slippage, and exit rules are approved
- Add deterministic fixtures and tests for complete, incomplete, delayed, missing, adverse-first, and no-lookahead cases
- Update `PROJECT_MEMORY.md` with durable facts only

## Forbidden scope

- No final thresholds, profitability claims, or public accuracy claims
- No frontend, live exchange integration, real orders, credentials, leverage, or short strategy
- No use of future or unavailable data
- No classifying a signal as successful only because price later reached a favorable high

## Acceptance criteria

- Replay is deterministic and availability-time safe
- Fixed windows are computed from the confirmation reference time
- Maximum rise and drawdown are both recorded, including adverse-first ordering
- Incomplete and missing windows are excluded from complete-sample aggregates with reason codes
- Strategy PnL remains separate and not evaluated unless explicit cost/exit inputs exist
- Unit tests, fixture validation, `git diff --check`, scope, and secret checks pass
- Report changed files, commands, results, risks, branch, commit, workspace status, and memory sync

## Required report

Use the report structure in `AG_WORK_LOOP.md`. Do not proceed to API or frontend work before main AG approval.
