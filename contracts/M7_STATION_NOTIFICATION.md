# M7 Station Notification Policy Contract

`notifications/policy.py` is a pure, offline boundary over approved `api.v1`
`SignalEventDTO` values. It selects only `new_signal`, `weakening`, and
`invalidation`. Stale, future, unsupported, unknown, malformed, and empty input
fail closed. A station notification is display data only: it cannot deliver to a
provider or execute a trade, and invalidation explicitly is not a short signal.

`station.v1` deduplication keys are deterministic hashes of the source event
type, signal ID, exchange label, symbol, and occurrence time. Cooldown is scoped
to signal ID plus event type, so an invalidation is never hidden by an earlier
weakening reminder. The provisional defaults are a five-minute maximum event
age, ten-minute cooldown, 30-second retry delay, and three total attempts. These
are notification-operation values, not strategy thresholds.

Time and state storage are injected. A selected attempt is saved as `pending`
before it is returned. Success records `delivered` and starts cooldown; failure
records a deterministic next-retry time. Pending attempts recover through the
same retry delay after restart. A state-store implementation must durably
preserve `StoredDelivery` records and cooldown timestamps; the bundled in-memory
store exposes a snapshot only for offline tests and reconstruction.

No Telegram, email, SMS, browser push, webhook, SSE client, queue, scheduler,
database, credentials, exchange connectivity, or trading operation is present.
