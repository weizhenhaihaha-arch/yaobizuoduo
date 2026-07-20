BEGIN;

CREATE TABLE IF NOT EXISTS normalized_records (
    record_id TEXT PRIMARY KEY,
    schema_version TEXT NOT NULL,
    record_type TEXT NOT NULL CHECK (record_type IN ('symbol', 'candle', 'market_metrics', 'data_health')),
    exchange TEXT NOT NULL CHECK (exchange IN ('binance', 'okx')),
    symbol TEXT NOT NULL,
    market_type TEXT NOT NULL CHECK (market_type = 'usdt_perpetual'),
    event_time TIMESTAMPTZ NOT NULL,
    available_time TIMESTAMPTZ NOT NULL,
    received_time TIMESTAMPTZ NOT NULL,
    data_quality TEXT NOT NULL CHECK (data_quality IN ('normal', 'delayed', 'missing', 'out_of_order', 'invalid')),
    source_sequence BIGINT,
    payload JSONB NOT NULL,
    CHECK (available_time >= event_time),
    CHECK (received_time >= available_time)
);

CREATE TABLE IF NOT EXISTS signals (
    signal_id TEXT PRIMARY KEY,
    schema_version TEXT NOT NULL,
    exchange TEXT NOT NULL CHECK (exchange IN ('binance', 'okx')),
    symbol TEXT NOT NULL,
    market_type TEXT NOT NULL CHECK (market_type = 'usdt_perpetual'),
    strategy_version TEXT NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('watch', 'potential', 'armed', 'active', 'weakening', 'invalidated', 'expired')),
    reason_codes TEXT[] NOT NULL DEFAULT '{}',
    reference_entry_price NUMERIC,
    reference_entry_time TIMESTAMPTZ,
    invalidation_rule_id TEXT NOT NULL,
    cooldown_group TEXT NOT NULL,
    data_snapshot_ids TEXT[] NOT NULL DEFAULT '{}',
    event_time TIMESTAMPTZ NOT NULL,
    available_time TIMESTAMPTZ NOT NULL,
    last_confirmed_time TIMESTAMPTZ,
    freshness_status TEXT NOT NULL,
    data_quality TEXT NOT NULL,
    usable_for_signal BOOLEAN NOT NULL,
    CHECK (available_time >= event_time),
    CHECK ((state IN ('armed', 'active', 'weakening') AND reference_entry_price IS NOT NULL AND reference_entry_time IS NOT NULL) OR state NOT IN ('armed', 'active', 'weakening'))
);

CREATE TABLE IF NOT EXISTS signal_events (
    event_id TEXT PRIMARY KEY,
    schema_version TEXT NOT NULL,
    signal_id TEXT NOT NULL REFERENCES signals(signal_id),
    from_state TEXT NOT NULL CHECK (from_state IN ('watch', 'potential', 'armed', 'active', 'weakening', 'invalidated', 'expired')),
    to_state TEXT NOT NULL CHECK (to_state IN ('watch', 'potential', 'armed', 'active', 'weakening', 'invalidated', 'expired')),
    event_time TIMESTAMPTZ NOT NULL,
    available_time TIMESTAMPTZ NOT NULL,
    reason_codes TEXT[] NOT NULL DEFAULT '{}',
    snapshot_id TEXT NOT NULL,
    CHECK (available_time >= event_time)
);

CREATE OR REPLACE FUNCTION reject_signal_event_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'signal_events is append-only';
END;
$$ LANGUAGE plpgsql;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'signal_events_append_only') THEN
        CREATE TRIGGER signal_events_append_only
        BEFORE UPDATE OR DELETE ON signal_events
        FOR EACH ROW EXECUTE FUNCTION reject_signal_event_mutation();
    END IF;
END;
$$;

CREATE TABLE IF NOT EXISTS outcome_windows (
    signal_id TEXT NOT NULL REFERENCES signals(signal_id),
    window TEXT NOT NULL CHECK (window IN ('5m', '15m', '1h', '4h', '1d')),
    strategy_version TEXT NOT NULL,
    window_start TIMESTAMPTZ NOT NULL,
    window_end TIMESTAMPTZ NOT NULL,
    as_of_time TIMESTAMPTZ NOT NULL,
    entry_price NUMERIC NOT NULL,
    last_price NUMERIC,
    highest_price NUMERIC,
    lowest_price NUMERIC,
    max_rise_pct NUMERIC,
    max_drawdown_pct NUMERIC,
    peak_time TIMESTAMPTZ,
    drawdown_time TIMESTAMPTZ,
    first_extreme_order TEXT NOT NULL,
    complete BOOLEAN NOT NULL,
    missing_data TEXT[] NOT NULL DEFAULT '{}',
    strategy_result_status TEXT NOT NULL DEFAULT 'not_evaluated' CHECK (strategy_result_status = 'not_evaluated'),
    strategy_pnl_pct NUMERIC CHECK (strategy_pnl_pct IS NULL),
    strategy_result_reason TEXT NOT NULL,
    PRIMARY KEY (signal_id, window),
    CHECK (window_end >= window_start),
    CHECK (as_of_time >= window_start)
);

CREATE TABLE IF NOT EXISTS health_snapshots (
    health_id TEXT PRIMARY KEY,
    schema_version TEXT NOT NULL,
    exchange TEXT NOT NULL CHECK (exchange IN ('binance', 'okx')),
    symbol TEXT,
    market_type TEXT NOT NULL CHECK (market_type = 'usdt_perpetual'),
    event_time TIMESTAMPTZ NOT NULL,
    available_time TIMESTAMPTZ NOT NULL,
    received_time TIMESTAMPTZ NOT NULL,
    data_quality TEXT NOT NULL CHECK (data_quality IN ('normal', 'delayed', 'missing', 'out_of_order', 'invalid')),
    status TEXT NOT NULL,
    usable_for_signal BOOLEAN NOT NULL,
    freshness_status TEXT NOT NULL,
    last_event_time TIMESTAMPTZ,
    reason_codes TEXT[] NOT NULL DEFAULT '{}',
    missing_fields TEXT[] NOT NULL DEFAULT '{}',
    CHECK (available_time >= event_time),
    CHECK (received_time >= available_time)
);

CREATE INDEX IF NOT EXISTS signals_dashboard_order_idx ON signals (state, freshness_status, exchange, symbol, signal_id);
CREATE INDEX IF NOT EXISTS signal_events_lookup_idx ON signal_events (signal_id, event_time, available_time, event_id);
CREATE INDEX IF NOT EXISTS outcome_windows_order_idx ON outcome_windows (signal_id, window_start, window_end, window);
CREATE INDEX IF NOT EXISTS health_snapshots_order_idx ON health_snapshots (exchange, symbol, event_time DESC, health_id);
CREATE INDEX IF NOT EXISTS normalized_records_lookup_idx ON normalized_records (exchange, symbol, event_time, available_time, record_id);

COMMIT;
