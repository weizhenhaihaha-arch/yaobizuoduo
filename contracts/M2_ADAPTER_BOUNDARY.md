# M2 只读适配器与数据健康边界

## Scope

`adapters/read_only_market.py` only accepts decoded public payloads and maps Binance or OKX data to the `m1.v1` contract. It contains no HTTP client, URL caller, credentials, websocket loop, signal calculation, frontend, or order operation.

## Exchange mapping

| Source | Normalized field | Rule |
|---|---|---|
| Binance `symbol` | `symbol` | Remove separators and uppercase; `BTCUSDT` remains `BTCUSDT` |
| OKX `instId` | `symbol` | `BTC-USDT-SWAP` becomes `BTCUSDT` |
| Binance kline array | candle | Map open/high/low/close, base/quote volume, trade count and close time |
| OKX candle array | candle | Map timestamp, OHLC, base/quote volume and confirmation flag; trade count is `0` because it is not present in this boundary |
| Binance `lastPrice`/`openInterest`/`fundingRate` | metrics | Numeric conversion; OI unit is `contracts` |
| OKX `last`/`oi`/`fundingRate` | metrics | Numeric conversion; OI unit is `contracts` |

The adapters reject malformed timestamps, non-numeric values, impossible candle ranges, negative quantities, missing required fields, and timestamps in the wrong order. They do not infer missing metrics.

## Health behavior

The health result is fail-closed:

- `normal`: connected, complete, and within the configured delay; usable for a later strategy layer.
- `delayed`: accepted for audit but not usable for a signal.
- `missing`: not usable; missing fields remain explicit.
- `out_of_order`: valid and usable only after deterministic replay sorting.
- `invalid`: rejected and never usable.
- `reconnecting`/`disconnected`/`error`: connection is not usable and cannot create a signal.

`ConnectionHealth.usable()` returns true only for `connected`. A connection state never emits a signal and is independent from strategy code.

## Reconnect behavior

The state machine starts `disconnected`, moves to `connected` after a successful public-data connection, moves to `reconnecting` after a disconnect, and moves to `error` after a transport or decode error. Errors retain a deterministic code and count. Recovery clears the error count only after an explicit `connected()` transition.

## Verification boundary

Tests use only local dictionaries and the existing offline fixture files. No live endpoint is required or claimed as verified. Future M2 integration may add a transport implementation only after this boundary is reviewed.
