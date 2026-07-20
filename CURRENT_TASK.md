# Current AG Task

## Task

- Task ID: `M2-T01`
- Milestone: M2 read-only market collection and data health
- Status: dispatched
- Executor: execution AG `Aquinas`
- Reviewer: main AG
- Previous task result: `M1-T01` passed main AG audit; M2 is now authorized

## Goal

Design and implement only the read-only Binance and OKX market-data adapter boundary and health behavior. Do not implement signal strategy or real trading.

## Allowed scope

- Review the M1 contract and fixtures before coding
- Define exchange adapter interfaces and symbol mapping rules
- Implement safe read-only probes or adapter stubs that can be tested without credentials
- Implement normalization, freshness, delay, missing-data, and reconnect state handling
- Add offline tests using the existing fixtures; live probes are optional and must not be required for tests
- Update `PROJECT_MEMORY.md` with durable facts only

## Forbidden scope

- No signal scoring or final strategy thresholds
- No frontend implementation
- No real-order execution or exchange credentials
- No short strategy or additional exchange
- No fake live data presented as verified production data

## Acceptance criteria

- Binance and OKX adapter boundaries map into `m1.v1` fields
- Tests cover normal, delayed, missing, out-of-order, invalid, and reconnect/error states
- Data-health status fails closed and cannot create a signal
- Offline tests pass without network access
- Live endpoint behavior, if probed, is recorded separately from offline verification
- `git diff --check`, targeted tests, and scope/secret checks pass
- Report changed files, commands, results, risks, branch, commit, workspace status, and memory sync

## Required report

Use the report structure in `AG_WORK_LOOP.md`. If blocked by endpoint access or missing product decisions, report the exact blocker instead of expanding scope.
