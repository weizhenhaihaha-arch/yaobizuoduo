# M3 做多策略与信号生命周期边界

## Scope

`strategy/lifecycle.py` is a deterministic, explainable state machine over normalized snapshots. It does not fetch data, place orders, render UI, calculate performance, or create short signals.

## Provisional configuration

`LifecycleConfig` contains temporary candidate, confirmation, weakening, invalidation, expiry, cooldown, and freshness values. They are explicitly versioned as `provisional-m3-v1`; they are not production thresholds and make no profitability claim. M4 replay must validate or replace them.

## Input requirements

Each snapshot includes exchange, canonical symbol, `usdt_perpetual`, event/availability time, data quality, `usable_for_signal`, price, price change, volume ratio, OI change, and a `structure_id`. Only `normal` or replay-sorted `out_of_order` data with acceptable availability delay can affect state.

## State transitions

```text
watch -> potential -> armed -> active -> weakening -> invalidated
                                      \-> expired
```

- `watch`: no candidate activity.
- `potential`: at least one provisional candidate condition is present.
- `armed`: all provisional confirmation conditions are present; this is the only transition that records the reference entry price/time.
- `active`: a confirmed signal remains usable on a later snapshot.
- `weakening`: confirmation conditions fade without yet breaching the invalidation buffer.
- `invalidated`: price breaches the reference-entry buffer or weakening persists.
- `expired`: signal age exceeds the provisional maximum age.

Every transition appends an event containing signal ID, snapshot ID, event time, reason codes, entry reference, and invalidation rule ID. Events are never edited or deleted.

## Health veto and deduplication

Stale, missing, invalid, disconnected, or otherwise unusable data returns `data_health_veto` and cannot confirm or invalidate a signal. A terminal opportunity is suppressed during its cooldown and also suppressed when the same `structure_id` reappears. Re-entry requires a different structure ID and an event time after cooldown. Duplicate suppression is an evaluation result, not a new state event.

## Open validation items

The threshold values, structure-ID generation, invalidation buffer, cooldown duration, expiry duration, fee/slippage model, and any final performance interpretation remain unresolved. They require historical replay and product review in later milestones.
