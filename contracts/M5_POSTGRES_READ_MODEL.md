# M5 PostgreSQL Read Model Boundary

`db/migrations/001_m5_read_model.sql` defines the versioned PostgreSQL shape for normalized records, signals, append-only signal events, fixed outcome windows, and health snapshots. It is forward-only and is not executed by the application or offline tests.

`persistence.postgres_read_model.PostgresReadModel` implements the approved `ReadModel` using an injected DB-API connection or factory. It issues only parameterized `SELECT` statements, closes each cursor in `finally`, and does not call `commit`, `rollback`, migrations, or connection setup commands. `close()` closes the injected connection once; ownership is explicit at the injection boundary.

The adapter preserves `event_time` and `available_time`, reason-code arrays, strategy versions, fixed windows (`5m`, `15m`, `1h`, `4h`, `1d`), and `not_evaluated` with null strategy PnL. Empty result sets remain empty so the service layer owns missing-signal semantics. Missing columns, malformed arrays, and evaluated strategy results raise `ReadModelDataError` instead of being silently repaired.

Offline tests use fake DB-API connections only. No live database, credentials, ORM, Docker, Redis, exchange transport, frontend, strategy, or trading code is included.
