# Current AG Task

## Task

- Task ID: `M6-T02`
- Milestone: M6 beginner homepage and detail experience
- Status: awaiting_review
- Executor: autonomous Codex CLI worker transition
- Reviewer: autonomous Codex CLI review transition
- Previous task result: `M6-T01` passed main AG audit

## Goal

Add beginner-readable signal detail, history, and observation-statistics views over approved deterministic `api.v1` DTO-shaped development fixtures, while preserving the reviewed homepage.

## Allowed scope

- Add accessible navigation between Signals, Results, Help, and signal detail views
- Implement signal detail with action state, timeline, entry reference, invalidation, data health, and fixed-window outcome observations
- Implement historical signal rows and observation-only statistics that clearly separate maximum price rise from unevaluated strategy PnL
- Reuse approved components/tokens and deterministic development fixtures; keep all development data visibly labeled
- Add responsive component tests and build verification
- Update `DESIGN.md` and `PROJECT_MEMORY.md` with durable decisions

## Forbidden scope

- No live API/SSE/exchange calls, routing server, authentication, database, deployment, or production data
- No strategy calculations, threshold changes, simulated profitability, accuracy claims, real orders, leverage, or short logic
- No notification implementation or M7 observability work
- No redesign of the approved homepage outside changes required for navigation/reuse

## Acceptance criteria

- A beginner can move from a homepage signal to detail and understand current action, why it appeared, whether it remains valid, and what invalidation means
- History and statistics distinguish observed price movement, incomplete windows, and `not_evaluated` strategy results
- Missing, incomplete, stale, empty, and invalidated states remain explicit and fail closed
- Keyboard/focus, text labels, mobile/desktop layout, and reduced-motion behavior follow `DESIGN.md`
- Frontend tests/build, backend tests, M1 fixture validation, `git diff --check`, scope, and secret checks pass
- Report files, decisions, commands/results, risks, branch, commit, workspace status, and memory sync

## Required report

Do not proceed to live API integration, M7 notifications/observability, deployment, or trading before autonomous review passes.
