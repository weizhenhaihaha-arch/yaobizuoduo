# Current AG Task

## Task

- Task ID: `M5-T03`
- Milestone: M5 backend API and real-time event boundary
- Status: dispatched
- Executor: execution AG `Aquinas`
- Reviewer: main AG
- Previous task result: `M5-T02` passed main AG re-audit after dedicated missing-signal error repair

## Goal

Add the PostgreSQL schema migration and injected read-only persistence adapter required by the approved M1-M5 contracts, without connecting to a live database or changing product/strategy behavior.

## Allowed scope

- Add versioned PostgreSQL migration SQL for normalized market records, signals, append-only state events, outcomes, and health snapshots
- Preserve event-time/availability-time, strategy version, reason codes, data health, fixed outcome windows, and not-evaluated strategy result semantics
- Implement a parameterized read-only `ReadModel` adapter behind an injected DB-API-compatible connection/factory
- Add deterministic offline tests using fakes; test query mapping, ordering, missing data, transaction safety, and no writes from the read adapter
- Document migration/rollback assumptions and update `PROJECT_MEMORY.md`

## Forbidden scope

- No live PostgreSQL connection, credentials, Docker/deployment, or production data
- No frontend, live exchange collection, strategy changes, trading, leverage, or short logic
- No ORM or Redis expansion unless separately approved
- No destructive runtime migration execution

## Acceptance criteria

- Migration is forward-only, versioned, rerunnable where appropriate, and preserves append-only signal events
- Required constraints/indexes support dashboard ordering, detail/history, outcomes, and health reads
- Adapter uses parameterized SQL and implements the approved `ReadModel` without write operations
- Offline tests cover every adapter method and malformed/missing rows fail safely
- Full tests, M1 fixture validation, `git diff --check`, SQL/scope/secret checks pass
- Report files, decisions, commands/results, risks, branch, commit, workspace status, and memory sync

## Required report

Use `AG_WORK_LOOP.md`. Do not proceed to M6 frontend, live database setup, collection, deployment, or trading before main AG approval.
