# Current AG Task

## Task

- Task ID: `M1-T01`
- Milestone: M1 data contracts and test fixtures
- Status: awaiting_review
- Executor: execution AG `Aquinas`
- Reviewer: main AG
- Previous task result: `M0-T01` passed after targeted repair; M1 is now authorized
- Execution report: M1 artifacts were committed as `e8a8652`; main AG audit is pending

## Goal

Define the first normalized market-data, signal-event, lifecycle, and outcome-record contracts, plus deterministic test fixtures. Do not connect to live exchanges or implement the strategy.

## Allowed scope

- Review `PRODUCT_SPEC.md`, `DESIGN.md`, `DEVELOPMENT_WORKFLOW.md`, `PROJECT_MEMORY.md`, and `M0_BOUNDARY_PROPOSAL.md`
- Define versioned schemas for exchange, symbol, timestamp, candle, volume, OI, funding, data health, signal, signal-state event, and outcome window
- Create small Binance/OKX fixed fixtures covering normal, delayed, missing, out-of-order, and invalid data
- Define event-time versus availability-time fields and deterministic replay expectations
- Update only M1 contract documentation and fixture files

## Forbidden scope

- No frontend or backend application implementation
- No live exchange API integration
- No real-order execution or credential handling
- No short strategy, additional exchange, or automatic trading
- No final strategy thresholds or performance claims

## Acceptance criteria

- Provide versioned contract documentation with required fields, units, timestamp semantics, and invalid-data behavior
- Include deterministic Binance and OKX fixtures and tests or validation scripts that parse them
- Prove the same fixture produces the same normalized result
- Keep confirmed requirements separate from assumptions and unresolved fields
- Run document consistency checks and fixture validation
- Update `PROJECT_MEMORY.md` with durable facts only
- Report changed files, commands, results, risks, branch, commit, and workspace status

## Required report

Use the report structure in `AG_WORK_LOOP.md`. If blocked, report the exact decision needed instead of changing scope.
