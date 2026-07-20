# Current AG Task

## Task

- Task ID: `M7-T01`
- Milestone: M7 notification, observation, and stability
- Status: repair_requested
- Executor: autonomous Codex CLI worker repair transition
- Reviewer: autonomous Codex CLI review transition
- Previous task result: `M6-T02` passed autonomous review

## Goal

Define and implement the smallest deterministic, offline-testable station-notification policy boundary over approved `api.v1` event messages, so confirmed signals, important weakening, and invalidations can be selected without duplicate notification spam.

## Allowed scope

- Add a pure notification-policy module that accepts approved read-only event DTOs and returns deterministic station-notification decisions
- Allow only `new_signal`, `weakening`, and `invalidation`; fail closed for stale, unknown, malformed, or unsupported events
- Add explicit deduplication keys, configurable provisional cooldown, retry state, and restart-safe injected state-store interfaces
- Keep user copy consistent with approved webpage lifecycle meanings, including that invalidation is not a short signal
- Add deterministic fixtures/unit tests and a bounded notification contract or runbook section
- Update `PROJECT_MEMORY.md` with durable decisions and verification evidence

## Forbidden scope

- No Telegram, email, SMS, push provider, webhook, browser notification, or live SSE/network integration
- No production queue, Redis, scheduler, deployment, authentication, credentials, or exchange connectivity
- No real orders, leverage, short logic, strategy calculations, threshold changes, or profit/accuracy claims
- No frontend redesign, M8 release work, or unrelated observability infrastructure

## Acceptance criteria

- Only the three approved user-facing lifecycle event types can produce a station-notification decision
- Duplicate delivery, cooldown, retry, restart reconstruction, stale input, malformed input, empty input, and unknown event behavior are deterministic and fail closed
- Notification text and identifiers remain traceable to the approved source event and do not imply trading execution or a short signal
- State storage and time are injected; tests require no network, credentials, database, or wall-clock timing
- Narrow tests, all backend tests, frontend tests/build, M1 fixture validation, `git diff --check`, scope scan, and secret scan pass
- Report files, decisions, commands/results, risks, branch, commit, workspace status, and memory sync

## Review blocking defect

- `notifications/policy.py::_validate` performs approved-type membership before
  validating that `event_type` is a string. A malformed `SignalEventDTO` with
  an unhashable value such as `event_type=[]` raises `TypeError` instead of
  returning a fail-closed `NotificationDecision`.

## Repair acceptance checks

- Validate malformed `event_type` values before set membership so every
  non-string value, including unhashable containers, returns
  `should_deliver=False` with `reason="malformed_event"` and never reserves
  delivery state.
- Add regression coverage for at least an unhashable container and a scalar
  non-string `event_type`; retain the existing unsupported-string behavior.
- Keep the repair limited to notification validation/tests and required task or
  memory reporting, then rerun every original M7-T01 acceptance check.

## Required report

Do not proceed to Telegram evaluation, live delivery, monitoring infrastructure, continuous paper observation, deployment, or M8 during this task.
