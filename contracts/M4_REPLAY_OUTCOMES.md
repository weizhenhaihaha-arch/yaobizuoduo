# M4 历史回放与结果统计边界

## Availability-time safety

`HistoricalReplay` sorts normalized snapshots by `(available_time, event_time, snapshot_id)` before passing them through the approved M3 lifecycle. Each outcome window is evaluated at its `window_end`; only snapshots with `available_time <= window_end`, `event_time <= window_end`, usable health, and `normal`/replay-sorted `out_of_order` quality are eligible.

A snapshot whose event happened inside a window but became available after that window is excluded and adds `availability_after_window`. It cannot influence an earlier result. This prevents future or late-arriving data from leaking into replay.

## Fixed windows

The reference point is the M3 `armed` event's `reference_entry_time` and `reference_entry_price`. Outcomes are recorded for `5m`, `15m`, `1h`, `4h`, and `1d`. Each record contains last price, highest/lowest price, maximum rise, maximum drawdown, peak time, drawdown time, first-extreme order, completeness, and missing-data reason codes.

`complete` requires an eligible observation at or beyond the window end and no missing-data reason. No interpolation, forward fill, or later correction is used.

## Price observation versus strategy result

Price observations answer what the market did relative to the fixed reference entry. They do not claim that a user obtained that high or avoided the drawdown. Strategy fields remain separate: `strategy_result_status` is always `not_evaluated`, `strategy_pnl_pct` is `null`, and the reason is `exit_rules_fees_and_slippage_not_approved` until a later milestone explicitly defines exits, fees, and slippage.

Incomplete windows are excluded from complete-sample aggregates and retain their reason codes. An adverse-first path is recorded with `first_extreme_order=drawdown_first`; it is not treated as a successful signal merely because a later high exists.

## No claims and unresolved items

This milestone makes no profitability, accuracy, or success-rate claim. Still unresolved are the approved production strategy version, exit rules, fee/slippage model, aggregation policy, and final threshold configuration.
