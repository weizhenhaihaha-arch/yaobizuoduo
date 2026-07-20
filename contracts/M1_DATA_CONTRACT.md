# M1 数据契约 v1

## Scope

This contract defines the normalized input and event records for the pump-long signal project. It is an offline contract only: no exchange client, strategy implementation, order execution, credentials, or performance claim is included.

## Contract rules

- JSON encoding is UTF-8; timestamps are RFC 3339 UTC strings with a `Z` suffix.
- Monetary values, quantities, volumes, open interest, and funding rates are JSON numbers, not formatted strings.
- `event_time` is when the exchange says the market event occurred. `available_time` is when the system can safely use the record. A record is never usable before `available_time`.
- `received_time` is local receipt time and is diagnostic only; it must not replace `event_time` during replay.
- `schema_version` is currently `m1.v1` and is required on every top-level record.
- `exchange` is one of `binance` or `okx`; `market_type` is `usdt_perpetual`.
- A record with invalid required fields is rejected, not repaired silently. Missing optional fields are represented as `null` and produce a quality flag.
- Replay sorts accepted records by `(event_time, available_time, record_id)` and produces deterministic output. Records with the same `record_id` are duplicates and are ignored after the first accepted copy.

## Common envelope

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `schema_version` | string | yes | Contract version, `m1.v1` |
| `record_id` | string | yes | Stable unique fixture/event identifier |
| `exchange` | enum | yes | `binance` or `okx` |
| `symbol` | string | yes | Canonical symbol, e.g. `BTCUSDT` |
| `market_type` | enum | yes | `usdt_perpetual` |
| `event_time` | RFC3339 UTC | yes | Exchange event time |
| `available_time` | RFC3339 UTC | yes | Earliest safe-use time |
| `received_time` | RFC3339 UTC | yes | Local receipt diagnostic time |
| `data_quality` | enum | yes | `normal`, `delayed`, `missing`, `out_of_order`, or `invalid` |
| `source_sequence` | integer or null | no | Exchange sequence if available |

`available_time` must not precede `event_time`; `received_time` must not precede `available_time` in accepted normal fixtures. A delayed record has `available_time > event_time`. An out-of-order fixture is valid data whose arrival order differs from event order; it is not rejected solely for arrival order.

## Symbol record

```json
{
  "schema_version": "m1.v1",
  "record_type": "symbol",
  "record_id": "binance-btcusdt-symbol-001",
  "exchange": "binance",
  "symbol": "BTCUSDT",
  "market_type": "usdt_perpetual",
  "base_asset": "BTC",
  "quote_asset": "USDT",
  "contract_status": "trading",
  "price_decimals": 2,
  "quantity_decimals": 3,
  "event_time": "2026-07-20T00:00:00Z",
  "available_time": "2026-07-20T00:00:01Z",
  "received_time": "2026-07-20T00:00:01Z",
  "data_quality": "normal"
}
```

## Candle record

Required fields: `interval`, `open_time`, `close_time`, `open`, `high`, `low`, `close`, `base_volume`, `quote_volume`, `trade_count`, and `closed`. Prices must satisfy `low <= min(open, close) <= max(open, close) <= high`; volumes and trade count cannot be negative.

```json
{
  "schema_version": "m1.v1",
  "record_type": "candle",
  "record_id": "binance-btcusdt-5m-001",
  "exchange": "binance",
  "symbol": "BTCUSDT",
  "market_type": "usdt_perpetual",
  "interval": "5m",
  "open_time": "2026-07-20T00:00:00Z",
  "close_time": "2026-07-20T00:04:59Z",
  "event_time": "2026-07-20T00:04:59Z",
  "available_time": "2026-07-20T00:05:01Z",
  "received_time": "2026-07-20T00:05:01Z",
  "open": 65000.0,
  "high": 65120.0,
  "low": 64980.0,
  "close": 65100.0,
  "base_volume": 120.5,
  "quote_volume": 7830000.0,
  "trade_count": 2400,
  "closed": true,
  "data_quality": "normal"
}
```

## Market metrics record

The optional-but-contractual metrics are `last_price`, `base_volume`, `quote_volume`, `open_interest`, and `funding_rate`. `open_interest` uses the exchange's contract quantity unit and must include `open_interest_unit` (`contracts` or `quote`). `funding_rate` is a decimal rate, not a percentage; `0.0001` means 0.01%.

Missing metrics remain `null`, and the record quality must include `missing` in the fixture's quality explanation. The normalizer must not infer missing OI or funding from price or volume.

## Data health record

```json
{
  "schema_version": "m1.v1",
  "record_type": "data_health",
  "record_id": "okx-btcusdt-health-001",
  "exchange": "okx",
  "symbol": "BTCUSDT",
  "market_type": "usdt_perpetual",
  "event_time": "2026-07-20T00:05:00Z",
  "available_time": "2026-07-20T00:05:01Z",
  "received_time": "2026-07-20T00:05:01Z",
  "data_quality": "delayed",
  "freshness_ms": 1200,
  "missing_fields": [],
  "out_of_order": false,
  "usable_for_signal": false,
  "reason": "availability_delay_exceeds_fixture_limit"
}
```

`usable_for_signal` is false for `delayed`, `missing`, or `invalid` records until a later health record explicitly restores normal quality. Health status never creates a signal by itself.

## Signal record

M1 defines the storage shape only; M1 does not produce signals.

Required fields: `signal_id`, `strategy_version`, `state`, `reason_codes`, `reference_entry_price`, `reference_entry_time`, `invalidation_rule_id`, `cooldown_group`, and `data_snapshot_ids`. `state` is one of `watch`, `potential`, `armed`, `active`, `weakening`, `invalidated`, or `expired`. `reference_entry_price` is `null` unless state is `armed` or later. Strategy thresholds remain unspecified.

## State-event record

Required fields: `signal_id`, `from_state`, `to_state`, `event_time`, `available_time`, `reason_codes`, and `snapshot_id`. State transitions must be append-only and deterministic. An event cannot use a future snapshot: every referenced snapshot must have `available_time <= event_time` in replay time.

## Outcome-window record

The fixed windows are `5m`, `15m`, `1h`, `4h`, and `1d`, measured from the confirmation event's `reference_entry_time`. Required fields are `signal_id`, `window`, `window_start`, `window_end`, `as_of_time`, `last_price`, `highest_price`, `lowest_price`, `max_rise_pct`, `max_drawdown_pct`, `complete`, `missing_data`, `strategy_result_status`, and `strategy_version`. `max_rise_pct` and `max_drawdown_pct` are price observations, not profit claims. A strategy result is `not_evaluated` until a later milestone freezes exit, fee, and slippage rules.

## Invalid-data behavior

1. Reject records missing required envelope fields, invalid timestamps, unsupported exchanges/market types, impossible candle ranges, negative volumes, or non-decimal numeric values.
2. Preserve rejected records in validation output with `accepted: false` and a deterministic error code; never use them for signal or outcome calculation.
3. Accept delayed records for audit but set them unusable until health rules allow them.
4. Accept valid out-of-order records, sort them by event time for replay, and expose the reorder count.
5. Accept missing optional metrics only with explicit `null`, quality metadata, and no inferred replacement.

## Confirmed, assumed, unresolved

Confirmed by M0: Binance/OKX USDT perpetual scope, UTC event and availability semantics, fixed outcome windows, explicit data-health states, and no live execution. Assumed for fixtures: `5m` candle interval, sample timestamps, and a small BTCUSDT sample. Unresolved for M2-M4: exchange-specific field mapping, freshness limits, observation-pool membership rules, strategy thresholds, cooldown duration, fees, and slippage.
