# M5 FastAPI HTTP/SSE Transport Contract

## Scope

`api/transport.py` is a thin FastAPI transport over the approved `ReadOnlyApiService`. The app is created by `create_app(service, event_source)` so storage and event production remain injected. It has no live exchange client, database, strategy calculation, authentication, credentials, trading, frontend, or deployment behavior.

## GET routes

| Route | Response |
|---|---|
| `GET /api/v1/dashboard` | `api.v1` dashboard groups: confirmed, potential, no-signal, recent invalidations, health |
| `GET /api/v1/signals/{signal_id}` | Signal DTO, state events, and outcome summary |
| `GET /api/v1/signals/history` | Ordered historical signal DTOs |
| `GET /api/v1/signals/{signal_id}/outcomes` | Fixed-window outcome DTOs |
| `GET /api/v1/statistics/summary` | Observation-only aggregate summary and not-evaluated strategy status |
| `GET /api/v1/health` | Read-model health DTOs |
| `GET /api/v1/events` | SSE stream for approved read-only event messages |

## Error envelope

All transport errors use:

```json
{"error":{"code":"not_found|invalid_request|internal_error","message":"...","request_id":"optional"}}
```

404 maps to `not_found`, validation and other client errors map to `invalid_request`, and unexpected failures map to `internal_error` without exposing exception details.

## SSE framing

Only `new_signal`, `weakening`, `invalidation`, and `stale_data` are emitted. Each message is:

```text
event: invalidation
data: {"event_type":"invalidation",...}

```

The event source is injected and may be empty in offline deployments; no transport route calls a live exchange.
