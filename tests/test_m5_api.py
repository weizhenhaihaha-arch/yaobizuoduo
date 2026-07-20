import unittest

from api.service import InMemoryReadModel, ReadOnlyApiService


def signal(signal_id, exchange, symbol, state, time, freshness="fresh", usable=True):
    return {"signal_id": signal_id, "exchange": exchange, "symbol": symbol, "market_type": "usdt_perpetual", "state": state, "event_time": time, "last_confirmed_time": time, "freshness_status": freshness, "data_quality": "normal" if usable else "delayed", "usable_for_signal": usable, "reason_codes": ("test_reason",), "reference_entry_price": 100.0 if state in {"armed", "active", "weakening"} else None, "reference_entry_time": time if state in {"armed", "active", "weakening"} else None, "invalidation_rule_id": "price_below_entry_buffer_v1", "strategy_version": "provisional-m3-v1"}


class ApiServiceTests(unittest.TestCase):
    def setUp(self):
        self.records = [
            signal("okx-sol-potential", "okx", "SOLUSDT", "potential", "2026-07-20T00:02:00Z"),
            signal("binance-btc-armed", "binance", "BTCUSDT", "armed", "2026-07-20T00:01:00Z"),
            signal("okx-eth-weak", "okx", "ETHUSDT", "weakening", "2026-07-20T00:03:00Z", "recent"),
            signal("binance-old-invalid", "binance", "DOGEUSDT", "invalidated", "2026-07-20T00:00:00Z", "stale", False),
        ]
        outcomes = [{"signal_id": "binance-btc-armed", "window": "5m", "entry_price": 100.0, "last_price": 102.0, "highest_price": 103.0, "lowest_price": 98.0, "max_rise_pct": 3.0, "max_drawdown_pct": -2.0, "peak_time": "2026-07-20T00:04:00Z", "drawdown_time": "2026-07-20T00:02:00Z", "first_extreme_order": "drawdown_first", "complete": True, "missing_data": (), "strategy_result_status": "not_evaluated", "strategy_result_reason": "exit_rules_fees_and_slippage_not_approved"}, {"signal_id": "binance-btc-armed", "window": "15m", "entry_price": 100.0, "last_price": None, "highest_price": None, "lowest_price": None, "max_rise_pct": None, "max_drawdown_pct": None, "complete": False, "missing_data": ("window_end_observation_missing",), "strategy_result_status": "not_evaluated", "strategy_result_reason": "exit_rules_fees_and_slippage_not_approved"}]
        health = [{"exchange": "binance", "symbol": "BTCUSDT", "status": "healthy", "usable_for_signal": True, "freshness_status": "fresh", "last_event_time": "2026-07-20T00:03:00Z", "reason_codes": ()}, {"exchange": "okx", "symbol": "ETHUSDT", "status": "stale", "usable_for_signal": False, "freshness_status": "stale", "last_event_time": "2026-07-20T00:03:00Z", "reason_codes": ("data_delayed",)}]
        self.service = ReadOnlyApiService(InMemoryReadModel(self.records, {}, outcomes, health))

    def test_dashboard_groups_and_deterministic_priority(self):
        dashboard = self.service.dashboard(generated_at="2026-07-20T00:05:00Z")
        self.assertEqual([item.signal_id for item in dashboard.confirmed], ["binance-btc-armed", "okx-eth-weak"])
        self.assertEqual([item.signal_id for item in dashboard.potential], ["okx-sol-potential"])
        self.assertEqual(dashboard.confirmed[0].exchange_label, "币安")
        self.assertTrue(dashboard.confirmed[0].can_consider_entry)
        self.assertFalse(dashboard.confirmed[1].can_consider_entry)

    def test_invalidation_and_health_are_visible(self):
        dashboard = self.service.dashboard(generated_at="2026-07-20T00:05:00Z")
        self.assertEqual(dashboard.recent_invalidations[0].state_label, "信号消失")
        self.assertFalse(dashboard.recent_invalidations[0].usable_for_signal)
        self.assertEqual(dashboard.health[1].freshness_status, "stale")

    def test_empty_state_explains_no_signal(self):
        empty = ReadOnlyApiService(InMemoryReadModel([signal("watch", "binance", "BTCUSDT", "watch", "2026-07-20T00:00:00Z")], {}, [], [])).dashboard(generated_at="2026-07-20T00:05:00Z")
        self.assertEqual(len(empty.confirmed), 0)
        self.assertIsNotNone(empty.empty_reason)

    def test_outcomes_and_statistics_keep_pnl_not_evaluated(self):
        outcome = self.service.outcomes("binance-btc-armed")[0]
        self.assertEqual(outcome.strategy_result_status, "not_evaluated")
        self.assertIsNone(outcome.strategy_pnl_pct)
        stats = self.service.statistics()
        self.assertEqual(stats.complete_price_observation_windows, 1)
        self.assertEqual(stats.incomplete_windows, 1)
        self.assertEqual(stats.strategy_result_status, "not_evaluated")

    def test_read_only_event_messages_are_plain_language(self):
        events = self.service.event_messages([{"event_type": "invalidation", "signal_id": "binance-btc-armed", "exchange": "binance", "symbol": "BTCUSDT", "occurred_at": "2026-07-20T00:04:00Z", "reason_codes": ("price_below_invalidation",)}])
        self.assertEqual(events[0].exchange_label, "币安")
        self.assertIn("已消失", events[0].message)
        self.assertNotIn("做空", events[0].message)


if __name__ == "__main__":
    unittest.main()
