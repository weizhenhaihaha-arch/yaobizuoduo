# M5 Read-Model Migration

`001_m5_read_model.sql` is a forward-only, transaction-wrapped schema migration for the approved M1-M5 read model. It is intentionally not executed by the application or tests.

The migration is rerunnable for tables, indexes, and the append-only trigger. There is no destructive down migration. Rollback means restoring the database snapshot or applying a separately reviewed future migration; the read adapter never runs migration SQL.
