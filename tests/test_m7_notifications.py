import json
import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

from api.dtos import SignalEventDTO
from notifications.policy import InMemoryNotificationStateStore, NotificationPolicy, NotificationPolicyConfig


class FixedClock:
    def __init__(self, now):
        self.value = now

    def now(self):
        return self.value


def event(event_type="new_signal", occurred_at="2026-07-21T00:00:00Z", signal_id="binance-btc"):
    return SignalEventDTO(event_type, signal_id, "币安", "BTCUSDT", occurred_at, ("approved_source",), "源事件文案")


class NotificationPolicyTests(unittest.TestCase):
    def setUp(self):
        self.clock = FixedClock(datetime(2026, 7, 21, 0, 1, tzinfo=timezone.utc))
        self.store = InMemoryNotificationStateStore()
        self.policy = NotificationPolicy(self.store, self.clock)

    def test_fixture_approved_types_only(self):
        cases = json.loads((Path(__file__).parents[1] / "fixtures" / "m7" / "notification_cases.json").read_text(encoding="utf-8"))["cases"]
        for index, case in enumerate(cases):
            decision = NotificationPolicy(InMemoryNotificationStateStore(), self.clock).decide(event(case["event_type"], signal_id=f"signal-{index}"))
            self.assertEqual(decision.reason, case["expected"])
            self.assertEqual(decision.should_deliver, case["expected"] == "selected")

    def test_notification_is_traceable_and_invalidation_is_not_short(self):
        decision = self.policy.decide(event("invalidation"))
        self.assertTrue(decision.should_deliver)
        self.assertEqual(decision.notification.source_signal_id, "binance-btc")
        self.assertEqual(decision.notification.source_event_type, "invalidation")
        self.assertEqual(decision.notification.source_message, "源事件文案")
        self.assertIn("不是做空信号", decision.notification.body)
        self.assertIn("不会执行交易", decision.notification.body)

    def test_duplicate_delivery_and_same_type_cooldown_fail_closed(self):
        first = self.policy.decide(event())
        self.policy.record_result(first, delivered=True)
        self.assertEqual(self.policy.decide(event()).reason, "duplicate_delivered")
        distinct = event(occurred_at="2026-07-21T00:00:30Z")
        self.assertEqual(self.policy.decide(distinct).reason, "cooldown_active")
        invalidation = self.policy.decide(event("invalidation", "2026-07-21T00:00:30Z"))
        self.assertTrue(invalidation.should_deliver)

    def test_failed_attempt_retries_only_when_due_and_stops_at_limit(self):
        first = self.policy.decide(event())
        self.policy.record_result(first, delivered=False)
        self.assertEqual(self.policy.decide(event()).reason, "retry_not_due")
        self.clock.value += timedelta(seconds=30)
        second = self.policy.decide(event())
        self.assertEqual((second.reason, second.attempt), ("retry", 2))
        self.policy.record_result(second, delivered=False)
        self.clock.value += timedelta(seconds=30)
        third = self.policy.decide(event())
        self.policy.record_result(third, delivered=False)
        self.clock.value += timedelta(seconds=30)
        self.assertEqual(self.policy.decide(event()).reason, "retry_exhausted")

    def test_pending_state_and_cooldown_reconstruct_after_restart(self):
        first = self.policy.decide(event())
        deliveries, cooldowns = self.store.snapshot()
        restarted_store = InMemoryNotificationStateStore(deliveries, cooldowns)
        restarted = NotificationPolicy(restarted_store, self.clock)
        self.assertEqual(restarted.decide(event()).reason, "retry_not_due")
        self.clock.value += timedelta(seconds=30)
        retry = restarted.decide(event())
        self.assertEqual(retry.attempt, 2)
        restarted.record_result(retry, delivered=True)
        deliveries, cooldowns = restarted_store.snapshot()
        reconstructed = NotificationPolicy(InMemoryNotificationStateStore(deliveries, cooldowns), self.clock)
        self.assertEqual(reconstructed.decide(event()).reason, "duplicate_delivered")

    def test_stale_future_malformed_unknown_and_empty_input_fail_closed(self):
        stale = self.policy.decide(event(occurred_at="2026-07-20T23:55:59Z"))
        future = self.policy.decide(event(occurred_at="2026-07-21T00:02:00Z"))
        malformed = self.policy.decide(replace(event(), occurred_at="not-a-time"))
        missing = self.policy.decide(replace(event(), signal_id=None))
        unknown = self.policy.decide({"event_type": "new_signal"})
        unsupported = self.policy.decide(event("stale_data"))
        self.assertEqual([item.reason for item in (stale, future, malformed, missing, unknown, unsupported)], ["stale_event", "future_event", "malformed_event", "malformed_event", "malformed_event", "unsupported_event_type"])
        self.assertEqual(self.policy.select(()), ())

    def test_configuration_and_clock_validation_fail_closed(self):
        with self.assertRaises(ValueError):
            NotificationPolicyConfig(max_attempts=0)
        naive_clock = FixedClock(datetime(2026, 7, 21, 0, 1))
        with self.assertRaises(ValueError):
            NotificationPolicy(InMemoryNotificationStateStore(), naive_clock).decide(event())


if __name__ == "__main__":
    unittest.main()
