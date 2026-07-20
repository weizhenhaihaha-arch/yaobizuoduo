# Project Memory

## Current state

- This is an independent project for a cryptocurrency pump-radar and long-entry signal website.
- It must not share implementation, roadmap, or Git history with the separate short-reversal project being developed by another agent.
- No application code has been implemented yet; product and strategy discovery is in progress.

## Confirmed requirements

- Initial exchanges: Binance and OKX only.
- Product focus: identify coins entering a potential sharp-upward move and provide actionable long-entry signals.
- A signal should be understandable as an entry opportunity, not merely a large list of abnormal coins.
- Users may use the strategy to open a long position after a signal appears and monitor the position while the signal remains valid.
- When the signal disappears or becomes invalid, the website must clearly notify the user.
- Strategy thresholds and entry rules remain open for discussion and must not be hard-coded from intuition alone.

## Architecture and decisions

- Keep this project in the separate local directory `妖币暴涨做多` and use a separate Git repository from `yaobi-radar`.
- V1 should start as observation, signal history, and paper-evaluation software; real order execution is not part of the current scope.
- The signal lifecycle should distinguish `watch`, `armed`, `entry`, `active`, `weakening`, `invalidated`, and `expired` so users can tell whether a signal is actionable.
- A candidate should be filtered and ranked before display; the goal is a small number of high-quality actionable signals rather than a noisy abnormal-movement list.
- The main experience must be understandable to beginners: group the observation pool into confirmed long signals, potential signals, and no-signal items; lead with the current action and hide advanced metrics behind signal details.
- The dashboard must make four user questions obvious: whether to consider entry now, why the signal appeared, whether it remains valid, and what it means when the signal disappears.
- Every signal must have a complete outcome record from first emission through follow-up windows, including whether price rose, maximum rise, time to peak, and adverse movement.
- Newly actionable long signals are sorted to the top of the dashboard; the list may show multiple simultaneous signals, while stale or weaker states rank below actionable signals.
- Statistics must distinguish simple price movement from strategy results; entry reference, observation windows, and calculation rules must be fixed before evaluation.
- The V1 product is defined as a beginner-facing decision dashboard, not a full trading terminal: the primary answer is whether a confirmed long signal currently exists.
- There is no global five-card cap. The dashboard uses three groups: confirmed signals at the top, potential signals in the middle, and no-signal observation items at the bottom; long lists use collapse, pagination, or load-more behavior.
- Every symbol card must show a textual exchange badge for Binance or OKX before the symbol; exchange color is supplementary, not the only identifier.
- Confirmed UX refinements: separate entry signal from holding/weakening state, show signal freshness, use plain-language quality levels instead of a dominant numeric score, and make data delays visible.
- The signal engine must deduplicate repeated triggers with cooldown and re-entry rules so one opportunity does not repeatedly notify the user.
- Empty states must explain why there is no actionable signal; history must report both price movement and fixed-rule simulated results without equating a later pump with a successful entry.
- The proposed architecture separates exchange collection, normalization, scanning, signal lifecycle, outcome evaluation, API delivery, and later notifications.
- Product and technical details are documented in `PRODUCT_SPEC.md`; strategy thresholds remain open until replay validation.
- M0-T01 boundary proposal is recorded in `M0_BOUNDARY_PROPOSAL.md`: V1 is read-only Binance/OKX USDT perpetual observation, with three dashboard groups, explicit beginner-facing lifecycle states, reproducible confirmation-time entry snapshots, invalidation reasons, deduplicated retriggers, and fixed 5m/15m/1h/4h/1d outcome windows.
- M0 freezes interfaces and evaluation semantics, not final strategy thresholds, cooldown duration, fee/slippage values, or performance claims; those require replay validation in later milestones.
- M1-T01 defines the versioned `m1.v1` normalized-data contract in `contracts/M1_DATA_CONTRACT.md`, including event-time versus availability-time semantics, explicit data-health behavior, append-only signal events, fixed outcome windows, and unresolved strategy fields.
- M1 fixed fixtures are stored under `fixtures/m1/` for both Binance and OKX and cover normal, delayed, missing, out-of-order, and invalid data. `scripts/validate_m1_fixtures.ps1` validates them offline and emits a deterministic replay digest.
- Main AG review passed `M0-T01` after a targeted trailing-whitespace repair; M1 is now authorized and `M1-T01` is the only active task.
- Development must follow the gated M0-M8 workflow in `DEVELOPMENT_WORKFLOW.md`; the current milestone is M0, followed by data contracts before application implementation.
- The AG development-review loop is active after explicit user confirmation; it enforces one task at a time, report-before-review, pass/repair/block outcomes, wake-up checks, and memory synchronization.
- Execution AG `Aquinas` was started for `M0-T01`; it is restricted to the M0 boundary proposal and must report before any next task is dispatched.
- The active loop now requires a three-minute heartbeat while a monitoring session or local monitor is running; each heartbeat checks task status, AG evidence, Git changes, tests, blockers, and wake-up conditions.
- UI/UX decisions are documented in the repository-root `DESIGN.md`, currently a Draft source of truth.
- A future Telegram notification can mirror signal creation and invalidation, but notification timing and deduplication remain to be designed.

## Verification status

- 2026-07-20 Asia/Shanghai: confirmed the existing `妖币雷达做多` directory is linked to `https://github.com/weizhenhaihaha-arch/yaobi-radar.git`, whose current planning is for short-reversal signals; it was left unchanged.
- 2026-07-20 Asia/Shanghai: initialized this directory as a new local Git repository with branch `main`.
- `origin` is now attached to `https://github.com/weizhenhaihaha-arch/yaobizuoduo.git`.
- 2026-07-20 Asia/Shanghai: local remote configuration succeeded, but `git ls-remote` received an empty server response, so remote reachability still needs a later retry.
- 2026-07-20 Asia/Shanghai: secret-pattern scan and staged whitespace check passed; first local documentation commit is `6952aa3`.
- 2026-07-20 Asia/Shanghai: first `git push -u origin main` attempt failed because the GitHub connection was reset; remote publication remains unverified.
- 2026-07-20 Asia/Shanghai: second push attempt failed to connect to `github.com:443`; local commits remain ready to publish when network access is available.
- 2026-07-20 Asia/Shanghai: `DEVELOPMENT_WORKFLOW.md` was added and local commit `dca79e8` was created; push again returned an empty server response.
- 2026-07-20 Asia/Shanghai: `AG_WORK_LOOP.md` was added and local commit `df17cdc` was created; the push attempt again failed to connect to `github.com:443`.

## Open items

- Retry `git ls-remote origin`, then publish the first project commit only after reviewing the staged diff.
- Decide whether the product targets USDT perpetual contracts only or also spot markets.
- Define the exact entry trigger, signal validity window, invalidation condition, and repeat-signal cooldown.
- Decide whether the first release includes Telegram alerts.
- Build a historical replay/evaluation set before presenting a strategy as reliable.
- Decide observation-pool size, pagination behavior, outcome windows, and exact beginner-facing entry/invalidation copy.
- Confirm whether the proposed FastAPI/PostgreSQL/React architecture fits the implementation environment.
- M0 boundary freeze is complete; M1 data contracts and fixtures now await main AG review.
- Main AG must audit the `M1-T01` contract, fixtures, validation output, and scope before dispatching `M1-T02`.
- Main AG must review `M0_BOUNDARY_PROPOSAL.md` and either approve M0 or return specific repairs before M1 begins.
- M0-T01 first review returned `repair_requested` because `git diff --check` found trailing whitespace at `M0_BOUNDARY_PROPOSAL.md:73`; M1 remains blocked until the repair report passes review.
- Establish or keep alive the monitoring session if unattended three-minute checks are required.

## Development log

### 2026-07-20

- Separated the pump-long project from the existing short-reversal project after the user explicitly requested independent work areas.
- Recorded the initial product direction: low-noise actionable long signals for Binance and OKX, with clear signal disappearance/invalidation notifications.
- Confirmed the UX direction: prioritize a small, beginner-readable shortlist over a dense market radar; active, weakening, and disappeared states must be explicit.
- Added the first repository-local design contract in `DESIGN.md`.
- Confirmed that the product needs a signal outcome/statistics system and priority sorting for newly actionable long signals.
- Added the V1 product specification covering beginner-first UI, signal lifecycle, outcome statistics, frontend, backend, APIs, and non-goals.
- Replaced the five-card homepage cap with three grouped sections and added mandatory Binance/OKX exchange badges on every symbol card.
- Confirmed signal freshness, quality labels, repeat-trigger suppression, data-health messaging, and explanatory empty states as product requirements.
- Defined the strict M0-M8 development workflow with milestone gates, non-goals, change control, verification, and the current M0 entry point.
- Activated the AG loop after user confirmation, checked for an active execution AG, found none, and dispatched `M0-T01` as the first wake-up task.
- Started execution AG `Aquinas` for `M0-T01`; the task is now in progress and the main AG will review its report before proceeding.
- Added the three-minute heartbeat requirement and documented the limitation that a closed conversation cannot be represented as an active monitor without a running monitoring process.
- Completed execution AG draft for `M0-T01`: added the boundary decision proposal and recorded the durable M0 decisions and remaining replay-dependent choices.
- Main AG audited the M0-T01 proposal, rejected the first report for a concrete whitespace failure, and issued a narrowly scoped repair request; no M1 work is authorized.
- Execution AG repaired the whitespace issue, main AG re-ran the checks and passed `M0-T01`, then dispatched `M1-T01` for data contracts and deterministic fixtures.
- Completed execution AG work for `M1-T01`: added the versioned data contract, Binance/OKX deterministic fixtures, offline validation script, and deterministic replay check; no live API or application code was added.
