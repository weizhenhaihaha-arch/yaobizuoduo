# Current AG Task

## Task

- Task ID: `M6-T01`
- Milestone: M6 beginner homepage and detail experience
- Status: dispatched
- Executor: execution AG `Aquinas`
- Reviewer: main AG
- Previous task result: `M5-T03` passed main AG audit; M5 backend/API/storage gate is complete

## Goal

Create the React/TypeScript mobile-first frontend foundation and beginner homepage that lets a user understand the current long-signal state within five seconds.

## Allowed scope

- Scaffold a minimal React/TypeScript frontend using the existing environment and `npm.cmd`
- Define accessible design tokens and reusable homepage components
- Render radar summary plus confirmed, potential, no-signal, and recent-invalidation sections from approved `api.v1` DTO-shaped deterministic fixtures
- Show Binance/OKX text badges, plain-language action state, freshness, quality, entry reference, invalidation, stale/data-health, loading, error, and empty states
- Implement responsive mobile-first layout and deterministic component/browser tests
- Update `DESIGN.md` implementation decisions and `PROJECT_MEMORY.md`

## Forbidden scope

- No signal detail/history/statistics screens in this task
- No live API or exchange calls, WebSocket/SSE connection, database, authentication, trading, leverage, or short logic
- No strategy calculations, threshold changes, profit claims, casino-like animation, or dense terminal indicators
- Deterministic fixtures must be visibly development/test data, never presented as production results

## Acceptance criteria

- Confirmed signals appear first, potential second, no-signal collapsed/lower priority, and invalidations remain visible
- Every card conveys exchange, action, reason, freshness, entry/invalidation context, and disabled stale behavior without relying on color alone
- Loading, empty, delayed, stale, and transport-error states are understandable to beginners
- Keyboard/focus semantics, reduced motion, readable contrast, and mobile/desktop layouts follow `DESIGN.md`
- Frontend tests/build, backend tests, M1 fixture validation, `git diff --check`, scope, and secret checks pass
- Report files, decisions, commands/results, screenshots if available, risks, branch, commit, workspace status, and memory sync

## Required report

Use `AG_WORK_LOOP.md`. Do not proceed to detail/history pages, live API integration, deployment, or trading before main AG approval.
