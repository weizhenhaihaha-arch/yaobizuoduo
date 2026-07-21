# Context: long-radar development workflow optimization

## Task statement

Produce a confirmation-ready, deeply optimized development workflow for the independent `yaobizuoduo` repository. This is planning only; no implementation or task dispatch is authorized.

## Desired outcome

- Preserve the beginner-facing, long-signal-only, Paper-first product boundary.
- Remove conflicting current-state documents and false milestone-completion claims.
- Define one canonical status source and a bounded task/review/acceptance chain.
- Separate offline contract completion, integration completion, Paper validation, and release readiness.
- Provide a macOS-compatible operating model and a remote exact-HEAD CI gate.
- Return a staged plan with explicit acceptance criteria for user confirmation.

## Repository facts

- Current Git HEAD is `101e593`; local `main` matches `origin/main` and was clean before this planning artifact.
- `CURRENT_TASK.md` says `M7-T02` is `awaiting_review` after a bounded validation repair.
- `PROJECT_MEMORY.md` says M0-M6 and M7-T01 are approved, while live exchange transport, live providers, continuous Paper observation, and trading are not implemented.
- `DEVELOPMENT_WORKFLOW.md` still says the project is at M0.
- `AG_WORK_LOOP.md` still reports M0 and M5-T01 in its current-state section.
- M2's approved implementation is an offline payload-mapping boundary, while the milestone definition also requires continuous live public-data collection and operational behavior.
- M4 strategy PnL remains `not_evaluated`; final thresholds, exit rules, fees, and slippage remain unresolved.
- M6 uses deterministic DTO fixtures and has no live backend integration.
- M7 has pure notification-policy and health-assessment boundaries, but no provider, production monitoring, or continuous Paper run.
- No `.github/workflows` directory exists.
- Supervisor scripts are Windows PowerShell/Scheduled Task specific; the current macOS clone has no PowerShell and no ignored `.ag_loop_state.json` runtime baseline.

## Constraints

- Binance and OKX USDT perpetuals only for V1.
- Long signals only; invalidation must never become a short signal.
- No real orders, exchange credentials, leverage management, or profit guarantees.
- One active task slice at a time.
- Developer delivery is not acceptance; Codex independently reviews and returns `ACCEPTED`, `RETURNED`, or `BLOCKED`.
- Each accepted slice must have exact-scope evidence, tests, exact-HEAD CI, durable project-memory closure, and merged-main verification before the next slice.
- Planning approval does not authorize implementation.

## Unknowns requiring user confirmation

- Whether unattended macOS automation is desired at all, or whether the active Codex task should remain the supervisor.
- Whether Telegram belongs in the first observation release.
- The observation-pool construction rule and final strategy/entry/invalidation parameters.
- Minimum Paper observation duration and sample threshold for release review.

## Likely repository planning touchpoints

- `DEVELOPMENT_WORKFLOW.md`
- `AG_WORK_LOOP.md`
- `CURRENT_TASK.md`
- `PROJECT_MEMORY.md`
- `M0_BOUNDARY_PROPOSAL.md`
- `DESIGN.md`
- future CI workflow and canonical verification scripts
