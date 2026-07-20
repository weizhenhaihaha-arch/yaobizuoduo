# Current AG Task

## Task

- Task ID: `M7-T02`
- Milestone: M7 notification, observation, and stability
- Status: repair_requested
- Executor: autonomous Codex CLI worker repair transition
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

## Review blocking defects

- `observability/health.py::_valid_data_health` performs approved-exchange set
  membership before proving `exchange` is a string. A malformed
  `DataHealthDTO(exchange=[])` raises `TypeError` instead of producing a
  fail-closed `malformed` assessment.
- `observability/health.py::_valid_prior` performs unhealthy-status set
  membership before proving `status` is a string. A malformed
  `PriorUnhealthyState(status=[])` raises `TypeError` and aborts assessment of
  otherwise valid current sources instead of ignoring invalid prior evidence.
- Delivery validation checks the literal `"delivered"` before the assessment
  path normalizes status casing. Consequently `status="DELIVERED"` with no
  `delivered_at` is accepted and reported `healthy` from `last_attempt_at`
  instead of failing closed as malformed.

## Repair acceptance checks

- Validate malformed data-health and prior-state field types before set or map
  operations so unhashable containers cannot escape as exceptions; malformed
  current sources produce a sanitized `malformed` assessment and malformed
  prior evidence is ignored without enabling recovery.
- Apply one consistent delivery-status normalization/validation rule so every
  delivered state requires a valid `delivered_at`; retain deterministic
  `unknown` behavior for unsupported string statuses.
- Add regression coverage for at least unhashable `exchange`, unhashable prior
  `status`, and case-variant delivered status without `delivered_at`.
- Keep the repair limited to operational-health validation/tests and required
  contract, task, fixture, or memory reporting, then rerun every original
  M7-T02 acceptance check and the adversarial probes above.

## Required report

Do not proceed to live monitoring infrastructure, provider delivery, continuous
paper observation, deployment, automation changes, or M8 during this task.
