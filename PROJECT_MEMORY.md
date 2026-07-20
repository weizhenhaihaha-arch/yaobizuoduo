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
- UI/UX decisions are documented in the repository-root `DESIGN.md`, currently a Draft source of truth.
- A future Telegram notification can mirror signal creation and invalidation, but notification timing and deduplication remain to be designed.

## Verification status

- 2026-07-20 Asia/Shanghai: confirmed the existing `妖币雷达做多` directory is linked to `https://github.com/weizhenhaihaha-arch/yaobi-radar.git`, whose current planning is for short-reversal signals; it was left unchanged.
- 2026-07-20 Asia/Shanghai: initialized this directory as a new local Git repository with branch `main`.
- `origin` is now attached to `https://github.com/weizhenhaihaha-arch/yaobizuoduo.git`.
- 2026-07-20 Asia/Shanghai: local remote configuration succeeded, but `git ls-remote` received an empty server response, so remote reachability still needs a later retry.
- 2026-07-20 Asia/Shanghai: secret-pattern scan and staged whitespace check passed; first local documentation commit is `6952aa3`.
- 2026-07-20 Asia/Shanghai: first `git push -u origin main` attempt failed because the GitHub connection was reset; remote publication remains unverified.

## Open items

- Retry `git ls-remote origin`, then publish the first project commit only after reviewing the staged diff.
- Decide whether the product targets USDT perpetual contracts only or also spot markets.
- Define the exact entry trigger, signal validity window, invalidation condition, and repeat-signal cooldown.
- Decide whether the first release includes Telegram alerts.
- Build a historical replay/evaluation set before presenting a strategy as reliable.
- Decide observation-pool size, pagination behavior, outcome windows, and exact beginner-facing entry/invalidation copy.
- Confirm whether the proposed FastAPI/PostgreSQL/React architecture fits the implementation environment.

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
