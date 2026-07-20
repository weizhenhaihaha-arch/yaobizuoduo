import json
import unittest
from pathlib import Path

from strategy.lifecycle import LifecycleConfig, SignalLifecycle


ROOT = Path(__file__).parents[1]


class LifecycleTests(unittest.TestCase):
    def load_cases(self):
        return json.loads((ROOT / "fixtures" / "m3" / "lifecycle_cases.json").read_text(encoding="utf-8"))["cases"]

    def test_fixture_replay_states(self):
        for case in self.load_cases():
            with self.subTest(case=case["case_id"]):
                engine = SignalLifecycle()
                actual = [engine.process(snapshot).state for snapshot in case["snapshots"]]
                self.assertEqual(actual, case["expected_states"])

    def test_confirmation_records_entry_and_reasons(self):
        engine = SignalLifecycle()
        snapshots = self.load_cases()[0]["snapshots"]
        engine.process(snapshots[0])
        result = engine.process(snapshots[1])
        self.assertEqual(result.state, "armed")
        self.assertEqual(result.events[0].reference_entry_price, 101.0)
        self.assertIn("provisional_thresholds", result.reason_codes)
        self.assertEqual(result.events[0].invalidation_rule_id, "price_below_entry_buffer_v1")

    def test_stale_data_cannot_create_or_change_signal(self):
        engine = SignalLifecycle()
        stale = self.load_cases()[1]["snapshots"][0]
        result = engine.process(stale)
        self.assertTrue(result.vetoed)
        self.assertEqual(result.state, "watch")
        self.assertEqual(engine.events, ())

    def test_events_are_append_only_and_deterministic(self):
        case = self.load_cases()[0]
        first = SignalLifecycle()
        second = SignalLifecycle()
        for snapshot in case["snapshots"]:
            first.process(snapshot)
            second.process(snapshot)
        self.assertEqual(first.events, second.events)
        self.assertEqual([event.event_id for event in first.events], ["binance-BTCUSDT-structure-a-event-0001", "binance-BTCUSDT-structure-a-event-0002", "binance-BTCUSDT-structure-a-event-0003"])

    def test_custom_thresholds_are_explicitly_configurable(self):
        config = LifecycleConfig(confirm_volume_ratio=3.0, version="test-provisional")
        engine = SignalLifecycle(config)
        snapshot = self.load_cases()[0]["snapshots"][1]
        self.assertEqual(engine.process(snapshot).state, "potential")
        self.assertEqual(engine.config.version, "test-provisional")

    def test_expiry_is_deterministic_and_not_a_short_signal(self):
        config = LifecycleConfig(expiry_minutes=1)
        engine = SignalLifecycle(config)
        first = self.load_cases()[0]["snapshots"][1].copy()
        first["event_time"] = "2026-07-20T00:00:00Z"
        first["available_time"] = "2026-07-20T00:00:00.500Z"
        self.assertEqual(engine.process(first).state, "armed")
        later = first.copy()
        later["snapshot_id"] = "expired"
        later["event_time"] = "2026-07-20T00:01:00Z"
        later["available_time"] = "2026-07-20T00:01:00.500Z"
        result = engine.process(later)
        self.assertEqual(result.state, "expired")
        self.assertIn("signal_age_exceeded", result.reason_codes)
        self.assertNotIn("short", " ".join(result.reason_codes))

    def test_invalid_health_is_a_veto(self):
        engine = SignalLifecycle()
        invalid = self.load_cases()[0]["snapshots"][1].copy()
        invalid["snapshot_id"] = "invalid-health"
        invalid["data_quality"] = "invalid"
        invalid["usable_for_signal"] = False
        result = engine.process(invalid)
        self.assertTrue(result.vetoed)
        self.assertIn("data_health_veto", result.reason_codes)


if __name__ == "__main__":
    unittest.main()
