# Current AG Task

## Task

- Task ID: `M0-T01`
- Milestone: M0 产品和策略边界冻结
- Status: dispatched
- Executor: execution AG (wake-up required; no active execution AG was detected during startup check)
- Reviewer: main AG

## Goal

Produce a concrete M0 boundary decision proposal for the beginner-friendly Binance/OKX pump-long signal product. Do not implement application code.

## Allowed scope

- Review `PRODUCT_SPEC.md`, `DESIGN.md`, `DEVELOPMENT_WORKFLOW.md`, and `PROJECT_MEMORY.md`
- Propose the initial market scope, observation-pool rule, signal lifecycle wording, entry reference, invalidation rule, repeat-trigger cooldown, and outcome windows
- Identify ambiguities, risks, and decisions that require product-owner confirmation
- Update only task documentation if needed; do not change strategy code because no strategy code exists yet

## Forbidden scope

- No frontend or backend implementation
- No exchange API integration
- No real-order execution or credential handling
- No short strategy, additional exchange, or automatic trading
- No final performance claims or hard-coded production thresholds

## Acceptance criteria

- Provide a decision table with current proposal, rationale, open choice, and downstream impact
- Keep confirmed requirements separate from assumptions
- Include a proposed signal state transition and user-facing wording
- Include a proposed fixed evaluation window and explain what remains to validate by replay
- Run document consistency checks and report results
- Update `PROJECT_MEMORY.md` with durable facts only
- Report changed files, commands, results, risks, branch, commit, and workspace status

## Required report

Use the report structure in `AG_WORK_LOOP.md`. If blocked, report the exact decision needed instead of changing scope.
