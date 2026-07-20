# Project Memory

## Current state

- This is an independent project for a cryptocurrency pump-radar and long-entry signal website.
- It must not share implementation, roadmap, or Git history with the separate short-reversal project being developed by another agent.
- Offline application boundaries now exist through M5: normalized adapters, deterministic lifecycle, replay/outcome evaluation, and a transport-agnostic read-only API service. No live exchange transport, frontend, or trading execution is implemented.

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
- Main AG review passed `M0-T01` after a targeted trailing-whitespace repair; M1 through M4 are approved.
- Main AG audited `M1-T01`: offline fixture validation passed with 10 cases, 12 accepted, 2 rejected, and a deterministic replay digest; scope and whitespace checks passed. M1-T01 is approved.
- M2-T01 was the only active task for read-only Binance/OKX adapter boundaries; it passed review and M3 is now authorized.
- Main AG audited `M2-T01`: 7 adapter tests, M1 fixture validation, whitespace, and scope checks passed. M2-T01 is approved.
- M3-T01 was the only active task for deterministic signal lifecycle and explainable strategy boundaries; it passed review and M4 is now authorized.
- M2-T01 implements pure offline-testable Binance/OKX payload mapping and fail-closed health handling in `adapters/read_only_market.py`; it has no network client, credentials, signal strategy, frontend, or trading operation.
- M3-T01 implements the deterministic `SignalLifecycle` boundary in `strategy/lifecycle.py`: candidate-to-potential-to-armed-to-active progression, weakening/invalidation/expiry, append-only explainable events, health vetoes, duplicate suppression, cooldown, and new-structure re-entry guards.
- M3 numeric values are versioned provisional configuration (`provisional-m3-v1`) only; no final thresholds, profitability claims, short logic, frontend, live exchange integration, or trading operation were added.
- Main AG audited `M3-T01`: 14 tests, deterministic fixture validation, whitespace, and scope checks passed. M3-T01 is approved.
- M4-T01 was the only active task for availability-safe replay and outcome statistics; it passed review and M5 is now authorized.
- Main AG audited `M4-T01`: 18 tests, M1 fixture validation, availability-time safety, whitespace, and scope checks passed. M4-T01 is approved.
- `M5-T01` passed main AG re-audit after its targeted fail-closed repair. `M5-T02` remains active in targeted error-classification repair; database migration, frontend, live exchange transport, and trading remain unauthorized.
- M5-T01 repair makes API entry advice fail closed: `can_consider_entry` now requires supported Binance/OKX exchange, `usdt_perpetual`, usable upstream data, fresh/recent freshness, and normal/out-of-order data quality in addition to `armed` state.
- M4-T01 implements availability-time-safe replay in `evaluation/replay.py`; price observations are separate from strategy results, incomplete windows retain reason codes, and strategy PnL remains `not_evaluated` with no profitability claim.
- M5-T01 implements the transport-agnostic read-only API service and `api.v1` DTOs in `api/`, including confirmed/potential/no-signal grouping, deterministic priority sorting, Binance/OKX badges, freshness/health, invalidation visibility, and not-evaluated outcome semantics.
- M5-T02 adds `api/transport.py`, injected FastAPI GET routes, approved-event SSE framing, sanitized error envelopes, `requirements-api.txt`, and offline interface tests. The transport has no default live client and only accepts injected read-model/service dependencies.
- Development must follow the gated M0-M8 workflow in `DEVELOPMENT_WORKFLOW.md`; the current milestone is M5, followed by frontend work only after API review.
- The AG development-review loop is active after explicit user confirmation; it enforces one task at a time, report-before-review, pass/repair/block outcomes, wake-up checks, and memory synchronization.
- Execution AG `Aquinas` was started for `M0-T01`; it is restricted to the M0 boundary proposal and must report before any next task is dispatched.
- The active loop now requires a three-minute heartbeat while a monitoring session or local monitor is running; each heartbeat checks task status, AG evidence, Git changes, tests, blockers, and wake-up conditions.
- A local heartbeat runner is defined at `scripts/ag_heartbeat.ps1`; it writes visible `AG_STATUS.md` and local `AG_HEARTBEAT.log` every three minutes. It reports repository evidence and cannot send chat messages after the conversation closes.
- When the user explicitly requests live monitoring, the main AG must keep an active monitoring session and emit a window-visible status every three minutes; each report must include evidence and the next workflow action.
- 2026-07-20 Asia/Shanghai: the local heartbeat runner was syntax-verified and started successfully as PID `17832`; `AG_STATUS.md` was created and showed the current `M1-T01` state.
- The heartbeat is now designed to support a Windows scheduled task `Codex-Yaobizuoduo-Heartbeat`, which runs the script in one-shot mode every three minutes; the task records evidence but never replaces main AG review.
- 2026-07-20 Asia/Shanghai: registered and started Windows task `Codex-Yaobizuoduo-Heartbeat`; state was `Ready`, last result `0`, and the next run was scheduled approximately three minutes later.
- Root-cause finding: the Windows heartbeat recorded repository state but could not invoke main AG review; completed AG commits therefore remained labeled `dispatched` until the conversation resumed.
- The loop now uses a dispatch Git baseline plus `AG_REVIEW_REQUIRED.md` for visible completion detection, and requires an active `wait_agent` session to return completed work to main AG review.
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
- V1 targets Binance and OKX USDT perpetual contracts only; spot remains outside V1.
- Define the exact entry trigger, signal validity window, invalidation condition, and repeat-signal cooldown.
- Decide whether the first release includes Telegram alerts.
- Build a historical replay/evaluation set before presenting a strategy as reliable.
- Decide observation-pool size, pagination behavior, outcome windows, and exact beginner-facing entry/invalidation copy.
- Confirm whether the proposed FastAPI/PostgreSQL/React architecture fits the implementation environment.
- M0 through M4 and M5-T01 are complete and approved; M5-T02 requires a targeted repair so internal read-model `KeyError` failures return sanitized 500 errors rather than false 404 responses.
- No database migration, frontend, live exchange transport, authentication, credentials, or deployment work is authorized before later approvals.
- Establish or keep alive the monitoring session if unattended three-minute checks are required.
- Start and verify the local heartbeat runner when visible unattended repository checks are required.

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
- Completed execution AG work for `M2-T01`: added read-only Binance/OKX normalizers, symbol mapping, fail-closed health/reconnect state, offline tests, and adapter boundary documentation; no live endpoint was called.
- Completed execution AG work for `M3-T01`: added provisional lifecycle configuration, deterministic state events, offline replay fixtures, lifecycle tests, and strategy-boundary documentation; no final performance claim or trading capability was added.
- Completed execution AG work for `M4-T01`: added availability-safe replay, fixed outcome windows, price observation records, incomplete/missing reason codes, deterministic fixtures/tests, and explicit `not_evaluated` strategy results; no future-data lookahead or profitability claim was added.
- Completed execution AG work for `M5-T01`: added read-only service interfaces, versioned DTOs, dashboard grouping/sorting, health and invalidation visibility, event messages, offline tests, and API-boundary documentation; no transport, frontend, live data, strategy change, or trading capability was added.
- Main AG audited M3 lifecycle behavior, passed `M3-T01`, and dispatched `M4-T01` for availability-safe historical replay and outcome statistics.
- Main AG audited M4 replay and outcomes, passed `M4-T01`, and dispatched `M5-T01` for the read-only API service and DTO boundary.
- Main AG audited the M1 contract and fixtures, confirmed deterministic validation, passed `M1-T01`, and dispatched `M2-T01` for read-only collection boundaries and health handling.
- Main AG audited M2 adapters and health behavior, passed `M2-T01`, and dispatched `M3-T01` for the deterministic signal lifecycle and provisional strategy boundary.
- Added the visible local heartbeat runner and ignored runtime status files so three-minute repository checks can be inspected without polluting Git history.
- Fixed the heartbeat PowerShell quoting issue, verified one foreground cycle, and started the hidden three-minute local monitor.
- Refined the loop to distinguish the local persistent heartbeat from an active chat monitoring session; the latter is required for visible three-minute window reports and is not claimed after the session ends.
- Reworked the heartbeat script with `-Once` mode so it can run safely under a Windows scheduled task instead of relying only on a long-lived PowerShell process.
- Replaced the temporary resident heartbeat process with the verified Windows scheduled task; visible status remains in `AG_STATUS.md` and history in `AG_HEARTBEAT.log`.
- Added baseline-aware completion detection and documented the split between persistent OS evidence collection and active-session AG completion monitoring.
- Main AG reviewed M5-T01: all 23 tests and standard checks passed, but an adversarial probe found stale armed data could still expose `can_consider_entry=true`; a targeted repair was requested and M5-T02 remains blocked.
- Execution AG completed the targeted M5-T01 repair: added defensive entry-usability gating and stale/unsupported regression coverage; full 24-test suite, M1 fixture validation, diff, and scope/secret checks passed. Awaiting main AG re-review.
- Main AG re-audited M5-T01 with 24 tests and adversarial stale, unusable, unsupported-exchange, spot, and delayed-quality probes; all passed, so M5-T01 was approved and M5-T02 FastAPI HTTP/SSE transport was dispatched.
- Fixed the heartbeat completion detector so new commits in `repair_requested` state also generate `AG_REVIEW_REQUIRED.md`; a one-shot verification correctly marked the M5 repair commit for review.
- Completed execution AG work for `M5-T02`: added FastAPI GET routes, SSE allowlist/framing, unified errors, dependency injection, minimum API dependencies, transport contract documentation, and offline tests; 29 tests passed without live exchange calls.
- Main AG reviewed M5-T02: 29 tests and standard checks passed, but an adversarial malformed-record probe showed the global `KeyError` handler misclassified an internal dashboard failure as 404; a focused repair was requested and later milestones remain blocked.
