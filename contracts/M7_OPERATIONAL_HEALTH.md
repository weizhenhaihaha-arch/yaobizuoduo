# M7 Offline Operational-Health Assessment Contract

`observability/health.py` is a pure `operational-health.v1` assessment boundary
over approved `api.v1` `DataHealthDTO` values and M7 `StoredDelivery` values.
The current time and complete read-only snapshot are injected. The module has no
monitor, logger, telemetry backend, provider, scheduler, daemon, queue, network,
database, filesystem watcher, exchange client, credential, or trading action.

Assessments expose a stable hash identifier, structured status, severity,
source key, source-observed UTC time, reason codes, fixed safe message, and
`operational_only` action scope. Identical evidence produces the same identifier.
Malformed and unknown values fail closed with bounded reason codes; exception or
source payload details are not copied into messages.

Data-health inputs can assess as `healthy`, `delayed`, `failed`, `stale`,
`malformed`, or `unknown`. Notification delivery inputs can assess as `healthy`,
`pending`, `delayed`, `retrying`, `failed`, `exhausted`, `malformed`, or
`unknown`. An empty snapshot produces an explicit `empty` assessment. Recovery
is derived only when a healthy current source has a matching, valid
`PriorUnhealthyState` in the same injected snapshot; a caller cannot obtain a
recovery assessment from a healthy value alone.

The provisional operational defaults are a two-minute data-staleness limit, a
30-second pending-delivery limit, and three notification attempts. They are
explicit configuration and are not market-strategy thresholds. This boundary
does not deliver alerts; a later separately approved adapter may consume these
assessment values.
