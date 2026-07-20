# Project Memory

## Current state

- This is an independent project for a cryptocurrency pump-radar and long-entry signal website.
- It must not share implementation, roadmap, or Git history with the separate short-reversal project being developed by another agent.
- Offline application boundaries, the deterministic beginner-facing frontend, and the pure station-notification policy are approved through M7-T01. M7-T02 is `dispatched` for a deterministic offline operational-health assessment boundary; no live notification provider, monitoring infrastructure, exchange transport, or trading execution is implemented.

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
- M5 backend/API/storage, all M6 beginner frontend work, and M7-T01 are approved. `M7-T02` is the only active task and is limited to an offline operational-health assessment boundary; live providers, infrastructure, deployment, automation changes, and trading remain unauthorized.
- M7-T01 adds `notifications/policy.py` over approved `api.v1` `SignalEventDTO` values. Only `new_signal`, `weakening`, and `invalidation` are selectable; exact-event deduplication, signal/event-type cooldown, bounded retry reservation, and restart reconstruction use injected clock and state-store interfaces.
- M7 station copy is traceable to the source signal/event/time/reasons, states that delivery does not execute a trade, and explicitly states that invalidation is not a short signal. Provisional five-minute event age, ten-minute cooldown, 30-second retry delay, and three-attempt values are notification-operation configuration, not strategy thresholds.
- M5-T01 repair makes API entry advice fail closed: `can_consider_entry` now requires supported Binance/OKX exchange, `usdt_perpetual`, usable upstream data, fresh/recent freshness, and normal/out-of-order data quality in addition to `armed` state.
- M4-T01 implements availability-time-safe replay in `evaluation/replay.py`; price observations are separate from strategy results, incomplete windows retain reason codes, and strategy PnL remains `not_evaluated` with no profitability claim.
- M5-T01 implements the transport-agnostic read-only API service and `api.v1` DTOs in `api/`, including confirmed/potential/no-signal grouping, deterministic priority sorting, Binance/OKX badges, freshness/health, invalidation visibility, and not-evaluated outcome semantics.
- M5-T02 adds `api/transport.py`, injected FastAPI GET routes, approved-event SSE framing, sanitized error envelopes, `requirements-api.txt`, and offline interface tests. The transport has no default live client and only accepts injected read-model/service dependencies. `SignalNotFoundError` is raised only for absent IDs; transport maps only that exception to 404, while malformed-record `KeyError` failures use sanitized 500 responses.
- M5-T03 adds the forward-only PostgreSQL schema in `db/migrations/001_m5_read_model.sql` and the injected DB-API `PostgresReadModel` in `persistence/postgres_read_model.py`. The adapter uses parameterized SELECTs only, closes cursors safely, performs no commit/rollback, preserves M1 event/availability timestamps and reason codes, and rejects malformed rows or evaluated strategy results.
- M6-T01 adds an isolated React/TypeScript Vite frontend under `frontend/` with deterministic `api.v1` DTO-shaped fixtures only. The homepage is mobile-first, shows summary/confirmed/potential/collapsed no-signal/recent-invalidations groups, exchange text labels, action/reason/freshness/quality/entry/invalidation fields, stale disabled copy, and accessible loading/empty/error states without live transport or strategy calculation.
- M6-T02 adds keyboard-operable Signals/Results/Help navigation plus deterministic signal detail, state timeline, fixed-window outcome, history, observation-statistics, and help views. Complete/incomplete price observations remain distinct from strategy PnL, which stays visibly `not_evaluated`; missing outcomes fail closed without inferred values.
- Development must follow the gated M0-M8 workflow in `DEVELOPMENT_WORKFLOW.md`; the current milestone is M7 after M6 passed review.
- The AG development-review loop is active after explicit user confirmation; it enforces one task at a time, report-before-review, pass/repair/block outcomes, wake-up checks, and memory synchronization.
- The chat execution AG `Aquinas` completed M6-T01 and was closed before enabling the autonomous CLI supervisor, preventing concurrent runtimes from modifying the repository.
- The active loop now requires a three-minute heartbeat while a monitoring session or local monitor is running; each heartbeat checks task status, AG evidence, Git changes, tests, blockers, and wake-up conditions.
- A local heartbeat runner is defined at `scripts/ag_heartbeat.ps1`; it writes visible `AG_STATUS.md` and local `AG_HEARTBEAT.log` every three minutes. It reports repository evidence and cannot send chat messages after the conversation closes.
- When the user explicitly requests live monitoring, the main AG must keep an active monitoring session and emit a window-visible status every three minutes; each report must include evidence and the next workflow action.
- 2026-07-20 Asia/Shanghai: the local heartbeat runner was syntax-verified and started successfully as PID `17832`; `AG_STATUS.md` was created and showed the current `M1-T01` state.
- The heartbeat is now designed to support a Windows scheduled task `Codex-Yaobizuoduo-Heartbeat`, which runs the script in one-shot mode every three minutes; the task records evidence but never replaces main AG review.
- 2026-07-20 Asia/Shanghai: registered and started Windows task `Codex-Yaobizuoduo-Heartbeat`; state was `Ready`, last result `0`, and the next run was scheduled approximately three minutes later.
- Root-cause finding: the Windows heartbeat recorded repository state but could not invoke main AG review; completed AG commits therefore remained labeled `dispatched` until the conversation resumed.
- The loop uses a per-task Git baseline plus `AG_REVIEW_REQUIRED.md` for completion detection and requires an active `wait_agent` session to return completed work to main AG review. It now also fingerprints changed-file timestamps, raises `AG_WAKE_REQUIRED.md` after three no-progress checks, detects task/baseline mismatch, writes `AG_LOOP_ERROR.md` on failures, writes state atomically, and rotates oversized logs.
- The Windows heartbeat task is configured for a three-minute interval, battery operation, start-when-available behavior, a ten-year repetition window, and a two-minute execution limit. It remains evidence automation only and cannot review code, contact the execution AG, or proactively message a closed chat.
- If main AG commits workflow or memory changes while an execution task is active, it must immediately reset that task's baseline to avoid mistaking the main AG commit for executor completion.
- UI/UX decisions are documented in the repository-root `DESIGN.md`, currently a Draft source of truth.
- A future Telegram notification can mirror signal creation and invalidation, but notification timing and deduplication remain to be designed.

## Verification status

- 2026-07-20 Asia/Shanghai: confirmed the existing `妖币雷达做多` directory is linked to `https://github.com/weizhenhaihaha-arch/yaobi-radar.git`, whose current planning is for short-reversal signals; it was left unchanged.
- 2026-07-20 Asia/Shanghai: initialized this directory as a new local Git repository with branch `main`.
- `origin` is now attached to `https://github.com/weizhenhaihaha-arch/yaobizuoduo.git`.
- 2026-07-21 Asia/Shanghai: local remote configuration remains correct, but direct GitHub HTTPS access still fails. The authenticated GitHub connector returns 404 for `weizhenhaihaha-arch/yaobizuoduo` and lists only `weizhenhaihaha-arch/yaobi-radar` as accessible, so the target repository must be created or granted to the connector before publication.
- 2026-07-20 Asia/Shanghai: secret-pattern scan and staged whitespace check passed; first local documentation commit is `6952aa3`.
- 2026-07-20 Asia/Shanghai: first `git push -u origin main` attempt failed because the GitHub connection was reset; remote publication remains unverified.
- 2026-07-20 Asia/Shanghai: second push attempt failed to connect to `github.com:443`; local commits remain ready to publish when network access is available.
- 2026-07-20 Asia/Shanghai: `DEVELOPMENT_WORKFLOW.md` was added and local commit `dca79e8` was created; push again returned an empty server response.
- 2026-07-20 Asia/Shanghai: `AG_WORK_LOOP.md` was added and local commit `df17cdc` was created; the push attempt again failed to connect to `github.com:443`.
- 2026-07-21 Asia/Shanghai: M7-T01 work verification passed 7 focused notification tests, all 43 backend tests, 10 frontend tests, the TypeScript/Vite build, M1 fixture validation (`c4326c783ba02c0f8414aff7c81fb08bcb6ac1dc0d2a22674055984ea6242785`), whitespace, forbidden-implementation, and secret scans.
- 2026-07-21 Asia/Shanghai: independent M7-T01 review reran 7 focused and all 43 backend tests, 10 frontend tests, the TypeScript/Vite build, M1 fixture validation with the same digest, whitespace, scope, automation-file, and tracked-secret scans successfully. An adversarial malformed DTO probe failed: unhashable `event_type=[]` raises `TypeError` before fail-closed validation. Review requested a validation-order regression repair and did not approve M7-T01.
- 2026-07-21 Asia/Shanghai: bounded M7-T01 repair verification passed 8 focused notification tests, all 44 backend tests, 10 frontend tests, the TypeScript/Vite build, M1 fixture validation (`c4326c783ba02c0f8414aff7c81fb08bcb6ac1dc0d2a22674055984ea6242785`), whitespace, scope/automation allowlists, forbidden-implementation scan, and tracked-secret scan. Non-string container/scalar event types now fail closed without reserving state; unsupported strings retain their distinct result.
- 2026-07-21 Asia/Shanghai: independent M7-T01 repair review passed 8 focused notification tests, all 44 backend tests, 10 frontend tests, the TypeScript/Vite build, M1 fixture validation with the same digest, `git diff --check`, repair scope and automation scans, forbidden-implementation and tracked-secret scans. An adversarial probe confirmed 11 non-string `event_type` shapes plus empty input fail closed without state reservation. M7-T01 is approved.

## Open items

- Create `weizhenhaihaha-arch/yaobizuoduo` or grant the GitHub connector access to it, then publish the clean local `main` branch; do not upload this independent project into `yaobi-radar`.
- V1 targets Binance and OKX USDT perpetual contracts only; spot remains outside V1.
- Define the exact entry trigger, signal validity window, invalidation condition, and repeat-signal cooldown.
- Decide whether the first release includes Telegram alerts.
- Build a historical replay/evaluation set before presenting a strategy as reliable.
- Decide observation-pool size, pagination behavior, outcome windows, and exact beginner-facing entry/invalidation copy.
- FastAPI, PostgreSQL contract/read-model, and React/TypeScript are confirmed for the current implementation path; live infrastructure integration remains later work.
- M0 through M6 and M7-T01 are complete and approved; M7-T02 is dispatched for the next bounded offline operational-health assessment. Telegram evaluation, live delivery/monitoring infrastructure, and continuous paper observation remain later work or unapproved decisions.
- The autonomous supervisor is authorized to execute one repository-state transition per run using Codex CLI; live API/exchange transport, authentication, credentials, deployment, and trading remain unauthorized.
- Establish or keep alive the monitoring session if unattended three-minute checks are required.
- Start and verify the local heartbeat runner when visible unattended repository checks are required.

## Development log

### 2026-07-21

- Completed the M7-T01 worker transition: added the pure station-notification policy, injected restart-safe state/time seams, deterministic fixture and unit coverage, and the bounded M7 contract. The implemented tests cover stale, future, unsupported, common malformed, unknown, and empty inputs, but review found the unhashable event-type gap described below; the module has no live provider, network integration, queue, credentials, exchange connectivity, strategy change, or trading operation.
- Audited GitHub publication after the user requested a full memory backup. The local branch was clean at `c1f341c`, direct GitHub HTTPS remained unavailable, and the GitHub connector confirmed that `yaobizuoduo` is not present or authorized. Publication is blocked until that repository exists or is granted to the connector; `yaobi-radar` was intentionally left untouched.
- Main AG review rejected M7-T01 for one fail-closed defect: `_validate` tests membership in the approved-event set before proving `event_type` is a string, so an unhashable malformed value raises `TypeError`. All required standard suites and repository scans otherwise passed; repair is limited to validation ordering and regression coverage for container/scalar non-string event types.
- Completed the bounded M7-T01 repair: `_validate` now rejects every non-string `event_type` before set membership, regression tests cover an unhashable list and integer without state reservation, and unsupported strings remain distinguishable. All original task checks passed; M7-T01 is awaiting independent review.
- Main AG approved the bounded M7-T01 repair after rerunning every acceptance check and adversarially probing malformed event types. The next smallest workflow-supported task is M7-T02: pure offline operational-health assessment for delay, delivery failure/retry/exhaustion, and recovery evidence, without live infrastructure or paper observation.

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
- Completed M5-T02 targeted repair: removed the global `KeyError` 404 mapping, scoped missing-signal conversion to detail/outcomes routes, and added regression coverage for missing outcomes plus malformed dashboard 500 sanitization.
- Main AG re-review found the first M5-T02 repair incomplete: route-level broad `KeyError` catches still classify malformed existing signal records as missing; a dedicated missing-signal exception and detail/outcomes regression tests are required.
- Completed M5-T02 second targeted repair: added service-layer `SignalNotFoundError`, scoped transport 404 conversion to that exception, and covered missing plus existing malformed detail/outcomes responses with sanitized 500 assertions.
- Main AG approved M5-T02 after 30 tests and four explicit probes confirmed missing detail/outcomes return 404 while malformed existing detail/outcomes return sanitized 500; M5-T03 database migration/read-model work was then dispatched.
- Completed M5-T03: added versioned PostgreSQL tables and indexes for normalized records, signals, append-only events, fixed outcome windows, and health snapshots; added injected read-only DB-API mapping with no writes; added fake connection/cursor tests for all ReadModel methods, malformed/empty data, ordering/query parameters, close behavior, and `not_evaluated` semantics. Full suite passed with 36 tests and no live database call.
- Main AG audited M5-T03: 36 tests, deterministic fixture validation, read-only query checks, append-only migration checks, whitespace, and scope/secret checks passed. M5 was approved and M6-T01 frontend foundation/homepage was dispatched.
- Completed M6-T01 frontend implementation and verification: added Vite/React/TypeScript scaffolding, deterministic development fixture, beginner homepage cards, responsive tokenized CSS, accessibility states, and frontend tests. Clean install used `npm.cmd ci --registry=https://registry.npmmirror.com`; frontend tests passed 3/3 and build passed. Browser screenshot verification was not run because no browser automation dependency was part of the approved frontend scope.
- Main AG audited M6-T01: frontend tests passed 3/3, Vite production build passed, backend tests passed 36/36, M1 fixtures and scope checks passed. M6-T01 was approved and M6-T02 was dispatched.
- Completed autonomous worker implementation for M6-T02: added deterministic DTO-shaped detail/outcome/statistics fixtures, accessible in-app navigation, conclusion-first signal detail and timeline, complete/incomplete fixed-window observations, history rows, observation-only statistics, and help copy. Verification passed with 8 frontend tests, frontend build, 36 backend tests, deterministic M1 fixture validation (`c4326c783ba02c0f8414aff7c81fb08bcb6ac1dc0d2a22674055984ea6242785`), `git diff --check`, and scope/secret scans.
- Main AG review rejected M6-T02 for a contract defect: frontend timeline events require invented `event_type`/`occurred_at` fields, while the approved `api.v1` signal-detail service returns persisted event fields including `event_id`/`event_time`. An adversarial serialized-service probe confirmed both frontend-required fields are absent. The existing 8 frontend tests, frontend build, 36 backend tests, M1 fixture validation, whitespace, scope, and secret checks otherwise passed; repair is limited to aligning frontend types, fixtures, rendering, and regression coverage with the existing backend contract.
- Completed the bounded M6-T02 contract repair: frontend state events now represent `event_id`, `signal_id`, `from_state`, `to_state`, `event_time`, `available_time`, `reason_codes`, and `snapshot_id`; the timeline renders localized text from `event_time` and preserves the exact timestamp in semantic `datetime`. Regression coverage verifies the DTO-shaped fixture and empty-event fail-closed message. Verification passed with 10 frontend tests, frontend build, 36 backend tests, serialized `ReadOnlyApiService.signal_detail(...).to_dict()` event-shape probe, deterministic M1 fixture validation (`c4326c783ba02c0f8414aff7c81fb08bcb6ac1dc0d2a22674055984ea6242785`), `git diff --check`, and scope/secret scans.
- Main AG reviewed and approved M6-T02 after the bounded repair. Independent review passed 10 frontend tests, the TypeScript/Vite build, 36 backend tests, the serialized service event-shape probe, M1 fixture validation (`c4326c783ba02c0f8414aff7c81fb08bcb6ac1dc0d2a22674055984ea6242785`), `git diff --check`, the six-file repair allowlist, forbidden-scope scan, and tracked-secret scan. M6 is approved and M7-T01 is dispatched; no live integration or trading capability was added.
- User explicitly authorized the full autonomous supervisor. Added repo-driven work/review prompts, exclusive locking, one-transition Codex CLI execution, failure backoff/blocking, runtime status/log files, and a reproducible Windows scheduled-task installer. Retired the chat Aquinas runtime before activation.
- First real supervisor work invocation exposed two runtime defects: Windows `workspace-write` could not launch PowerShell and Codex returned exit code 0 despite reporting no transition. Codex CLI was updated from 0.144.5 to 0.144.6, but the sandbox defect persisted; a read-only `danger-full-access` probe succeeded. The supervisor now uses structured JSON output plus required Git/status postconditions so semantic failures cannot be marked successful.
- Deep workflow audit confirmed the scheduled heartbeat was running but lacked stagnation detection, baseline/task mismatch protection, atomic state writes, error signaling, and battery-safe scheduling. These were added and fault-injection verified; the active M6 task baseline was reset after the main AG workflow repair commit.
