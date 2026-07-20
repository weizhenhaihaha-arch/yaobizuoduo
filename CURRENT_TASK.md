# Current AG Task

## Task

- Task ID: `M5-T02`
- Milestone: M5 backend API and real-time event boundary
- Status: dispatched
- Executor: execution AG `Aquinas`
- Reviewer: main AG
- Previous task result: `M5-T01` passed main AG re-audit after targeted fail-closed repair

## Goal

Implement the versioned FastAPI HTTP and SSE transport over the approved read-only M5 service without moving strategy, storage, or trading behavior into routes.

## Allowed scope

- Add a minimal dependency manifest for FastAPI transport and tests
- Implement the approved dashboard, signal detail, history, outcomes, statistics, and health GET routes
- Implement an SSE event route for new signal, weakening, invalidation, and stale-data DTO messages
- Add consistent not-found, invalid-request, and internal error response envelopes
- Keep read-model construction behind dependency injection and use deterministic offline fixtures/tests
- Document route contracts and update `PROJECT_MEMORY.md` with durable facts only

## Forbidden scope

- No frontend implementation or database migration in this task
- No live exchange client, background collector, real orders, credentials, leverage, or short strategy
- No strategy calculations or threshold changes in transport code
- No authentication accounts, profitability claims, fake production data, or deployment work

## Acceptance criteria

- Routes map approved DTOs without frontend-side strategy calculation
- SSE uses valid event framing and exposes only approved read-only event types
- Empty, stale, invalidated, unsupported, and missing-signal cases are explicit and fail closed
- Route handlers do not instantiate live exchange or trading clients
- Offline interface tests cover every GET route, error envelope, and SSE framing
- Full unit tests, M1 fixture validation, `git diff --check`, scope, and secret checks pass
- Report changed files, commands, results, risks, branch, commit, workspace status, and memory sync

## Required report

Use the report structure in `AG_WORK_LOOP.md`. Do not proceed to database migration, frontend, live exchange transport, or trading before main AG approval.
