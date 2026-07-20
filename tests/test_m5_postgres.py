import unittest

from persistence.postgres_read_model import PostgresReadModel, ReadModelDataError


class FakeCursor:
    def __init__(self, rows_by_table):
        self.rows_by_table = rows_by_table
        self.description = None
        self.executions = []
        self.closed = False
        self.rows = ()

    def execute(self, query, params):
        self.executions.append((query, params))
        if "FROM signals" in query:
            table = "signals"
        elif "FROM signal_events" in query:
            table = "signal_events"
        elif "FROM outcome_windows" in query:
            table = "outcome_windows"
        elif "FROM health_snapshots" in query:
            table = "health_snapshots"
        else:
            raise AssertionError("unexpected query")
        self.rows = tuple(self.rows_by_table.get(table, ()))

    def fetchall(self):
        return self.rows

    def close(self):
        self.closed = True


class FakeConnection:
    def __init__(self, rows_by_table):
        self.cursor_instance = FakeCursor(rows_by_table)
        self.closed = False
        self.commit_count = 0
        self.rollback_count = 0

    def cursor(self):
        self.cursor_instance.closed = False
        return self.cursor_instance

    def commit(self):
        self.commit_count += 1

    def rollback(self):
        self.rollback_count += 1

    def close(self):
        self.closed = True


def rows():
    return {
        "signals": [{"signal_id": "b-btc", "exchange": "binance", "symbol": "BTCUSDT", "market_type": "usdt_perpetual", "state": "armed", "event_time": "2026-07-20T00:01:00Z", "freshness_status": "fresh", "data_quality": "normal", "usable_for_signal": True, "reason_codes": ["armed"], "strategy_version": "provisional-m3-v1"}],
        "signal_events": [{"event_id": "event-1", "signal_id": "b-btc", "from_state": "potential", "to_state": "armed", "event_time": "2026-07-20T00:01:00Z", "available_time": "2026-07-20T00:01:01Z", "reason_codes": ["confirmed"], "snapshot_id": "snapshot-1"}],
        "outcome_windows": [{"signal_id": "b-btc", "window": "5m", "strategy_version": "provisional-m3-v1", "window_start": "2026-07-20T00:01:00Z", "window_end": "2026-07-20T00:06:00Z", "as_of_time": "2026-07-20T00:06:00Z", "entry_price": 100.0, "last_price": 102.0, "highest_price": 103.0, "lowest_price": 99.0, "max_rise_pct": 3.0, "max_drawdown_pct": -1.0, "complete": True, "missing_data": [], "strategy_result_status": "not_evaluated", "strategy_pnl_pct": None, "strategy_result_reason": "exit_rules_fees_and_slippage_not_approved"}],
        "health_snapshots": [{"health_id": "health-1", "exchange": "binance", "symbol": "BTCUSDT", "market_type": "usdt_perpetual", "event_time": "2026-07-20T00:01:00Z", "available_time": "2026-07-20T00:01:01Z", "received_time": "2026-07-20T00:01:01Z", "data_quality": "normal", "status": "healthy", "usable_for_signal": True, "freshness_status": "fresh", "reason_codes": [], "missing_fields": []}],
    }


class PostgresReadModelTests(unittest.TestCase):
    def setUp(self):
        self.connection = FakeConnection(rows())
        self.model = PostgresReadModel(lambda: self.connection)

    def test_all_read_model_methods_map_contract_rows(self):
        self.assertEqual(tuple(self.model.signals())[0]["signal_id"], "b-btc")
        self.assertEqual(tuple(self.model.signal_events("b-btc"))[0]["snapshot_id"], "snapshot-1")
        outcome = tuple(self.model.outcomes("b-btc"))[0]
        self.assertEqual(outcome["strategy_result_status"], "not_evaluated")
        self.assertIsNone(outcome["strategy_pnl_pct"])
        self.assertEqual(tuple(self.model.health())[0]["freshness_status"], "fresh")

    def test_queries_are_parameterized_selects_and_read_only(self):
        self.model.signals()
        self.model.signal_events("b-btc")
        self.model.outcomes()
        self.model.outcomes("b-btc")
        self.model.health()
        executions = self.connection.cursor_instance.executions
        self.assertEqual(len(executions), 5)
        for query, params in executions:
            self.assertTrue(query.lstrip().upper().startswith("SELECT"))
            self.assertNotIn("b-btc", query)
        self.assertEqual(executions[1][1], ("b-btc",))
        self.assertEqual(executions[3][1], ("b-btc",))
        self.assertEqual(self.connection.commit_count, 0)
        self.assertEqual(self.connection.rollback_count, 0)

    def test_empty_rows_are_safe_and_missing_signal_is_left_to_service(self):
        empty = PostgresReadModel(FakeConnection({}))
        self.assertEqual(tuple(empty.signals()), ())
        self.assertEqual(tuple(empty.signal_events("missing")), ())
        self.assertEqual(tuple(empty.outcomes("missing")), ())
        self.assertEqual(tuple(empty.health()), ())

    def test_malformed_rows_fail_closed_and_close_cursor(self):
        broken_connection = FakeConnection({"signals": [{"signal_id": "broken"}]})
        broken = PostgresReadModel(broken_connection)
        with self.assertRaises(ReadModelDataError):
            broken.signals()
        self.assertTrue(broken_connection.cursor_instance.closed)

    def test_invalid_strategy_result_is_rejected(self):
        invalid = rows()
        invalid["outcome_windows"][0]["strategy_result_status"] = "evaluated"
        broken_connection = FakeConnection(invalid)
        with self.assertRaises(ReadModelDataError):
            tuple(PostgresReadModel(broken_connection).outcomes())

    def test_cursor_and_connection_close_are_safe(self):
        self.model.signals()
        self.model.close()
        self.model.close()
        self.assertTrue(self.connection.closed)
        with self.assertRaises(RuntimeError):
            self.model.health()


if __name__ == "__main__":
    unittest.main()
