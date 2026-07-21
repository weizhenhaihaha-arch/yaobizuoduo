# Design

## Source of truth
- Contract version: beginner-first.v1
- Last refreshed: 2026-07-21
- Primary product surfaces: signal dashboard, signal detail, signal history and outcome statistics
- Evidence reviewed: product discussion, approved `api.v1` DTO boundary, and the reviewed M6 homepage/components

This is one product with one formal signal truth source. Progressive disclosure
changes how much supporting detail is visible; it must never create separate
beginner/expert conclusions or competing signal states.

## Brand
- Personality: calm, clear, practical, and trustworthy
- Trust signals: plain-language reasons, visible signal age, exchange label, invalidation notice, and historical results
- Avoid: casino-like flashing effects, exaggerated profit claims, dense trading-terminal layouts, and unexplained scores

## Product goals
- Goals: let a beginner understand whether there is an actionable long signal within a few seconds; show multiple simultaneous signals in three clear priority groups; clearly show when a signal disappears or becomes invalid; measure what happened after every signal
- Non-goals: showing every abnormal coin, teaching advanced indicators on the main screen, or promising guaranteed profit
- Success signals: users can identify the current action, entry reference, and invalidation condition without opening a chart

## Personas and jobs
- Primary personas: new or less-experienced crypto users who want a simple, actionable radar
- User jobs: find a small number of potential pump-start opportunities, decide whether to enter, and know when to stop following the signal
- Key contexts of use: mobile-first quick checks and desktop monitoring

## Information architecture
- Primary navigation: Signals, Results, Help
- Core routes/screens: active signal dashboard, one signal detail page, historical signal list, outcome statistics summary
- Content hierarchy: group state first, action state second, coin/exchange third, plain-language reason fourth, risk/invalidation fifth, outcome summary sixth, advanced data last

### Default-view contract

Without opening a detail panel, a user must be able to answer whether a confirmed
long signal exists. The summary uses exactly one of these conclusions:
`做多信号已出现`, `暂时没有做多信号`, or `数据延迟，暂不判断`.

Confirmed signals are primary. Recent weakening or invalidation remains visible
and never disappears silently. Potential and no-signal markets show a count and
last scan time; their long lists are collapsed by default.

### Signal-card information budget

The first layer contains no more than six information classes:

1. Symbol and textual exchange name.
2. Current plain-language conclusion.
3. One-sentence reason.
4. Entry reference area.
5. Invalidation condition.
6. Last update time.

Scores, full timelines, experiments and professional metrics cannot enter this
first layer.

### Progressive disclosure

OI, funding, long/short ratio, MA/EMA, raw candles, strategy version, thresholds,
reason codes, internal enums, event/availability timestamps, DTO/SSE terminology,
complete replay windows, drawdown, fees, slippage and experimental parameters are
hidden by default. They may appear only in `了解更多` or `专业数据` sections of the
same product and must support—not replace—the formal conclusion.

Internal states translate to ordinary Chinese:

| Internal state | User-facing text |
| --- | --- |
| `armed` | 做多信号已出现 |
| `active` | 信号仍然有效 |
| `potential` | 正在观察，还不能考虑入场 |
| `weakening` | 信号正在减弱 |
| `invalidated` | 信号已失效，停止按此信号关注 |
| `stale` | 数据有延迟，暂时不要按此页面判断 |
| `not_evaluated` | 还没有足够规则计算模拟结果 |

The default UI never displays internal English states or raw reason codes.
Invalidation is explicitly not a short signal.

## Design principles
- One screen, one decision: every active card answers “can I act now?”
- Fewer, stronger signals: default display is a curated shortlist, not a market dump
- Progressive disclosure: show observation-pool items by group, but collapse low-value no-signal rows
- Explain before exposing: show human-readable reasons before technical indicators
- State changes are prominent: signal disappearance and invalidation must be impossible to miss
- Evidence over impressions: every signal gets a fixed entry reference and follow-up outcome record
- Tradeoff: simplicity wins on the main view; advanced metrics move into the detail view

## Visual language
- Color: dark neutral base with green for confirmed actionable long, amber for potential/waiting, gray for no signal, and red for invalidated; never use color alone to convey state
- Typography: large Chinese action labels, readable numeric hierarchy, short sentences
- Spacing/layout rhythm: generous card spacing and one primary action per card
- Shape/radius/elevation: moderate rounded cards, clear borders, limited shadows
- Motion: subtle state-change highlight only; no flashing or continuous price animation
- Imagery/iconography: simple exchange and state icons; no decorative crypto imagery

## Components
- Existing components to reuse: none
- New/changed components: signal group, signal card, exchange badge, priority sort, signal-state badge, freshness indicator, quality label, entry/invalidation panel, outcome summary, history outcome row, statistics summary
- Variants and states: confirmed, potential, no-signal, active, weakening, invalidated, expired, loading, stale-data, data-delayed
- Token/component ownership: define tokens with the first frontend implementation

## Accessibility
- Target standard: WCAG 2.1 AA intent
- Keyboard/focus behavior: all signal cards and details keyboard reachable
- Contrast/readability: state labels include text, not color alone; minimum readable body size on mobile
- Screen-reader semantics: status changes use meaningful labels and polite announcements
- Reduced motion and sensory considerations: respect reduced-motion preference

## Responsive behavior
- Supported breakpoints/devices: mobile first, then tablet and desktop
- Layout adaptations: one-column active signal feed on mobile; two-column feed plus summary on desktop
- Touch/hover differences: large tap targets; hover only supplements, never replaces, information

## Interaction states
- Loading: show a short explanation that the radar is scanning, not a blank spinner-only screen
- Empty: say “当前没有满足条件的做多信号”，show last scan time and allow viewing history
- Error: identify whether exchange data, network, or signal calculation is unavailable
- Success: new actionable signal gets a restrained “已发现” state and timestamp
- Disabled: stale or incomplete data disables the entry suggestion while explaining why
- Offline/slow network, if applicable: show last update time and mark data as stale

## Content voice
- Tone: direct, calm, non-promotional, beginner-friendly
- Terminology: prefer “可以关注 / 可以考虑入场 / 信号减弱 / 信号消失” over unexplained technical jargon
- Microcopy rules: every signal has a plain-language reason, timestamp, entry reference, and invalidation condition
- Statistics copy must separate “最高涨幅” from “入场后表现”; never label a signal successful solely because price later rose at some point
- Use quality labels `强 / 中 / 弱` only as supporting context; the primary state remains `可以考虑开多 / 等待确认 / 信号减弱 / 信号消失`

## Implementation constraints
- Framework/styling system: React/TypeScript with Vite in an isolated `frontend/` workspace; CSS custom properties provide the first token layer
- Design-token constraints: centralize colors, spacing, typography, and state tokens; action state always has text and is never color-only
- Performance constraints: dashboard should prioritize fast first paint and avoid unnecessary live animation
- Compatibility constraints: modern mobile and desktop browsers
- Test/screenshot expectations: verify responsive dashboard, priority sorting, simultaneous signals, new signal, signal disappearance, stale data, loading/error/empty states, and keyboard focus; M6 uses deterministic `api.v1` DTO-shaped development fixtures only

## M6 implementation decisions
- M6-T01 established the beginner homepage; M6-T02 adds deterministic signal detail, history, observation statistics, and help views. Live HTTP and SSE remain deferred.
- A visible `开发 / 测试数据` badge and footer disclaimer distinguish fixtures from production data; the page makes no strategy calculation or profitability claim.
- The page order is summary, confirmed, potential, collapsed no-signal, and recent invalidations. Each card exposes exchange text, action, reason, freshness, quality, entry reference, and invalidation context.
- Stale or unusable DTOs show a warning and disabled action copy. Loading, empty, and transport-error states use text-first status panels with `role="status"` or `role="alert"`.
- Cards are keyboard focusable, the page has a skip link and semantic headings, and motion is disabled under `prefers-reduced-motion`.
- Primary navigation uses keyboard-operable Signals, Results, and Help controls without adding a routing server. Detail views preserve the Signals navigation context and provide an explicit back action.
- Signal detail remains conclusion-first: current action, plain-language reasons, entry reference, invalidation meaning, data health, state timeline, then fixed-window observations.
- Results show price observations and completeness separately from strategy results. `not_evaluated` is rendered as “策略盈亏：未评估”; null or missing observations are never replaced with inferred values.
- Mobile uses single-column content and horizontally scrollable accessible outcome tables; desktop expands detail/statistics/history layouts with the existing 700px breakpoint.

## Open questions
- [ ] Whether Telegram is included after the first station-notification Paper view / product owner
- [ ] Exact entry and invalidation wording after strategy replay / strategy owner
- [ ] G6 usability-test participant count and passing threshold / product owner
