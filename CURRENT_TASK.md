# Current AG Task

## Task

- Task ID: `M7-T02`
- Milestone: M7 notification, observation, and stability
- Status: dispatched
- Executor: autonomous Codex CLI worker transition
- Reviewer: autonomous Codex CLI review transition
- Previous task result: `M7-T01` passed autonomous review

## Goal

Define and implement the smallest deterministic, offline-testable operational
health assessment boundary so existing data-health and notification-delivery
state can produce traceable delay, failure, retry, and recovery alerts without
adding live monitoring infrastructure.

## Allowed scope

- Add a pure operational-health module over approved existing health DTO/state
  values, using injected time and read-only snapshots
- Produce deterministic structured health assessments for data delay,
  notification pending/retry/exhaustion, malformed input, and recovery
- Keep alert identifiers, severity, source, observed time, and reason codes
  traceable to the approved source state
- Define provisional operational thresholds as explicit configuration, separate
  from strategy thresholds
- Add deterministic fixtures/unit tests and a bounded observability contract or
  runbook section
- Update `PROJECT_MEMORY.md` with durable decisions and verification evidence

## Forbidden scope

- No live monitoring service, telemetry backend, production logger, pager,
  scheduler, daemon, queue, Redis, database migration, deployment, or automation
  file changes
- No Telegram, email, SMS, push provider, webhook, browser notification, or live
  SSE/network integration
- No exchange connectivity, credentials, real orders, leverage, short logic,
  strategy calculations, threshold changes, or profit/accuracy claims
- No frontend redesign, continuous paper observation, M8 release work, or
  unrelated infrastructure

## Acceptance criteria

- Approved healthy, delayed, failed, retrying, exhausted, recovered, stale,
  empty, malformed, and unknown states are deterministic and fail closed
- Duplicate identical assessments have stable identifiers and recovery cannot be
  emitted without a prior unhealthy state represented in the injected snapshot
- Assessments expose structured severity/source/time/reason evidence without
  leaking exception details or implying a trade action
- State and time are injected; tests require no network, credentials, database,
  filesystem watcher, or wall-clock timing
- Narrow tests, all backend tests, frontend tests/build, M1 fixture validation,
  `git diff --check`, scope scan, and secret scan pass
- Report files, decisions, commands/results, risks, branch, commit, workspace
  status, and memory sync

## Required report

Do not proceed to live monitoring infrastructure, provider delivery, continuous
paper observation, deployment, automation changes, or M8 during this task.
