# M5 只读 API Service 与 DTO 边界

## Scope

The M5 service is transport-agnostic. `ReadOnlyApiService` composes approved M1-M4 read-model records into versioned `api.v1` DTOs. Storage is supplied through a `ReadModel` interface. No web framework, live transport, strategy calculation, threshold mutation, frontend, order, or credential handling is included.

## Dashboard contract

The dashboard returns `confirmed`, `potential`, `no_signal`, `recent_invalidations`, and `health` groups. Confirmed states are `armed`, `active`, and `weakening`; potential is `potential`; observation states are `watch`, `invalidated`, and `expired`. Confirmed signals sort before potential and no-signal records. Within groups, actionable state, freshness, exchange, and symbol provide deterministic ordering.

Every signal DTO contains a Binance/OKX text badge, plain-language state, entry permission, freshness, data quality, reason codes, entry reference, invalidation rule, and strategy version. The API exposes state; it does not calculate strategy conditions.

## Safety and outcome semantics

Unusable or stale records remain visibly unusable and cannot be converted into an entry suggestion by the service. Outcome DTOs preserve complete/incomplete and missing-data fields. Price observations remain separate from strategy results; `strategy_result_status` is `not_evaluated` and PnL is `null` until exit, fee, and slippage rules are approved.

Empty dashboard responses include a human-readable reason instead of silently returning an empty list. Invalidation and stale-data messages are read-only event DTOs and do not imply a short signal or an order.

## Transport boundary

Future HTTP/SSE adapters may map these DTOs to routes, but M5 does not define or call live endpoints. Offline tests use `InMemoryReadModel` only.
