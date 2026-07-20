# Current AG Task

## Task

- Task ID: `M3-T01`
- Milestone: M3 pump-long strategy and signal lifecycle
- Status: dispatched
- Executor: execution AG `Aquinas`
- Reviewer: main AG
- Previous task result: `M2-T01` passed main AG audit; M3 is now authorized

## Goal

Implement the deterministic, explainable signal lifecycle and strategy boundary without claiming final thresholds or profitability.

## Allowed scope

- Review M1 contracts, M2 adapters, product specs, and M0 boundary proposal
- Define pure strategy input/output types and candidate-to-potential-to-confirmed state transitions
- Implement append-only state events, reason codes, freshness/data-health vetoes, deduplication, cooldown, and re-entry guards
- Keep numeric thresholds configurable and explicitly marked as provisional
- Add unit tests and fixture-driven replay tests for normal, delayed, missing, invalid, weakening, invalidation, duplicate, and re-entry cases
- Update `PROJECT_MEMORY.md` with durable facts only

## Forbidden scope

- No final production thresholds or performance claims
- No frontend implementation
- No live exchange integration beyond existing offline boundaries
- No real-order execution, API keys, leverage, or short strategy
- No treating signal disappearance as a short signal

## Acceptance criteria

- State transitions are deterministic, append-only, and explainable
- Data health fails closed and cannot confirm a signal
- Duplicate triggers are suppressed and re-entry requires a new valid structure
- Every confirmed signal has reason codes, input snapshot references, confirmation time, reference entry, and invalidation rule
- Tests cover normal, potential, confirmed, active, weakening, invalidated, expired, stale, duplicate, and re-entry paths
- `python -m unittest`, fixture validation, `git diff --check`, scope, and secret checks pass
- Report changed files, commands, results, risks, branch, commit, workspace status, and memory sync

## Required report

Use the report structure in `AG_WORK_LOOP.md`. If final threshold choices are needed, mark them unresolved instead of inventing production values.
