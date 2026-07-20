import json
import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

from api.dtos import DataHealthDTO
from notifications.policy import StoredDelivery
from observability.health import (
    OperationalHealthAssessor,
    OperationalHealthConfig,
    OperationalSnapshot,
    PriorUnhealthyState,
)


class FixedClock:
    def __init__(self, now):
        self.value = now

    def now(self):
        return self.value


def data_health(status="healthy", usable=True, freshness="fresh", last_event_time="2026-07-21T00:00:00Z"):
    return DataHealthDTO(
        exchange="binance",
        exchange_label="币安",
        symbol="BTCUSDT",
        status=status,
        usable_for_signal=usable,
        freshness_status=freshness,
        last_event_time=last_event_time,
        reason_codes=("approved_health_source",),
    )


def delivery(status="pending", attempts=1, last_attempt_at=None, next_retry_at=None, delivered_at=None):
    attempted = last_attempt_at or datetime(2026, 7, 21, 0, 0, 45, tzinfo=timezone.utc)
    return StoredDelivery(
        deduplication_key="station.v1:abc",
        cooldown_key="signal-1:new_signal",
        status=status,
        attempts=attempts,
        last_attempt_at=attempted,
        next_retry_at=next_retry_at,
        delivered_at=delivered_at,
    )


class OperationalHealthTests(unittest.TestCase):
    def setUp(self):
        self.clock = FixedClock(datetime(2026, 7, 21, 0, 1, tzinfo=timezone.utc))
        self.assessor = OperationalHealthAssessor(self.clock)

    def assess(self, data=(), deliveries=(), prior=()):
        return self.assessor.assess(OperationalSnapshot(tuple(data), tuple(deliveries), tuple(prior)))

    def test_fixture_data_health_states_are_deterministic_and_traceable(self):
        cases = json.loads(
            (Path(__file__).parents[1] / "fixtures" / "m7" / "operational_health_cases.json").read_text(encoding="utf-8")
        )["data_health_cases"]
        for case in cases:
            with self.subTest(case=case):
                first = self.assess(data=(data_health(case["status"], case["usable"], case["freshness"]),))[0]
                second = self.assess(data=(data_health(case["status"], case["usable"], case["freshness"]),))[0]
                self.assertEqual(first.status, case["expected"])
                self.assertEqual(first, second)
                self.assertTrue(first.assessment_id.startswith("operational-health.v1:"))
                self.assertEqual(first.source, "data_health")
                self.assertEqual(first.observed_at, "2026-07-21T00:00:00Z")
                self.assertIn("approved_health_source", first.reason_codes)
                self.assertEqual(first.action_scope, "operational_only")

    def test_healthy_claim_fails_closed_when_source_is_not_usable(self):
        assessment = self.assess(data=(data_health("healthy", False, "fresh"),))[0]
        self.assertEqual(assessment.status, "malformed")
        self.assertEqual(assessment.reason_codes, ("inconsistent_healthy_state",))

    def test_notification_pending_retry_failed_and_exhausted_states(self):
        pending = self.assess(deliveries=(delivery(),))[0]
        self.assertEqual(pending.status, "pending")

        delayed = self.assess(deliveries=(delivery(last_attempt_at=datetime(2026, 7, 21, 0, 0, 20, tzinfo=timezone.utc)),))[0]
        self.assertEqual(delayed.status, "delayed")

        retrying = self.assess(deliveries=(delivery("failed", next_retry_at=self.clock.now() + timedelta(seconds=10)),))[0]
        self.assertEqual(retrying.status, "retrying")

        failed = self.assess(deliveries=(delivery("failed", next_retry_at=self.clock.now() - timedelta(seconds=1)),))[0]
        self.assertEqual(failed.status, "failed")

        exhausted = self.assess(deliveries=(delivery("failed", attempts=3),))[0]
        self.assertEqual(exhausted.status, "exhausted")

    def test_recovery_requires_matching_prior_unhealthy_snapshot(self):
        current = data_health()
        normal = self.assess(data=(current,))[0]
        self.assertEqual(normal.status, "healthy")

        prior = PriorUnhealthyState(
            source_key=normal.source_key,
            assessment_id="operational-health.v1:prior",
            status="stale",
            observed_at="2026-07-20T23:58:00Z",
            reason_codes=("data_delayed",),
        )
        recovered = self.assess(data=(current,), prior=(prior,))[0]
        self.assertEqual(recovered.status, "recovered")
        self.assertEqual(recovered.prior_assessment_id, prior.assessment_id)
        self.assertIn("recovered_from_stale", recovered.reason_codes)

        mismatched = replace(prior, source_key="data:okx:BTCUSDT")
        future = replace(prior, observed_at="2026-07-21T00:00:01Z")
        invalid_id = replace(prior, assessment_id="not-an-assessment")
        self.assertEqual(self.assess(data=(current,), prior=(mismatched,))[0].status, "healthy")
        self.assertEqual(self.assess(data=(current,), prior=(future,))[0].status, "healthy")
        self.assertEqual(self.assess(data=(current,), prior=(invalid_id,))[0].status, "healthy")

    def test_delivered_notification_recovers_only_from_matching_prior_state(self):
        delivered_at = datetime(2026, 7, 21, 0, 0, 58, tzinfo=timezone.utc)
        current = delivery("delivered", delivered_at=delivered_at)
        healthy = self.assess(deliveries=(current,))[0]
        self.assertEqual(healthy.status, "healthy")
        prior = PriorUnhealthyState(healthy.source_key, "operational-health.v1:failed", "failed", "2026-07-21T00:00:45Z", ("notification_retry_due",))
        self.assertEqual(self.assess(deliveries=(current,), prior=(prior,))[0].status, "recovered")

    def test_empty_malformed_and_unknown_inputs_fail_closed_without_details(self):
        empty = self.assess()[0]
        malformed = self.assessor.assess(OperationalSnapshot(({"status": "healthy"},), (), ()))[0]
        unknown = self.assess(deliveries=(replace(delivery(), status="mystery"),))[0]
        self.assertEqual((empty.status, malformed.status, unknown.status), ("empty", "malformed", "unknown"))
        self.assertEqual(malformed.reason_codes, ("malformed_data_health_snapshot",))
        self.assertNotIn("{", malformed.message)

    def test_unhashable_data_exchange_fails_closed_as_malformed(self):
        malformed = replace(data_health(), exchange=[])
        assessment = self.assess(data=(malformed,))[0]
        self.assertEqual(assessment.status, "malformed")
        self.assertEqual(assessment.reason_codes, ("malformed_data_health_snapshot",))

    def test_unhashable_prior_status_is_ignored_without_enabling_recovery(self):
        current = data_health()
        healthy = self.assess(data=(current,))[0]
        malformed_prior = PriorUnhealthyState(
            source_key=healthy.source_key,
            assessment_id="operational-health.v1:prior",
            status=[],
            observed_at="2026-07-20T23:58:00Z",
            reason_codes=("data_delayed",),
        )
        assessment = self.assess(data=(current,), prior=(malformed_prior,))[0]
        self.assertEqual(assessment.status, "healthy")
        self.assertIsNone(assessment.prior_assessment_id)

    def test_case_variant_delivered_without_delivery_time_is_malformed(self):
        assessment = self.assess(deliveries=(delivery("DELIVERED"),))[0]
        self.assertEqual(assessment.status, "malformed")
        self.assertEqual(assessment.reason_codes, ("malformed_notification_snapshot",))

    def test_stale_is_derived_from_injected_time_and_threshold(self):
        item = data_health(last_event_time="2026-07-20T23:57:59Z")
        assessment = self.assess(data=(item,))[0]
        self.assertEqual(assessment.status, "stale")
        self.assertIn("last_event_exceeds_operational_limit", assessment.reason_codes)

    def test_invalid_configuration_snapshot_and_clock_are_rejected(self):
        with self.assertRaises(ValueError):
            OperationalHealthConfig(data_stale_after=timedelta(0))
        with self.assertRaises(ValueError):
            self.assessor.assess("not-a-snapshot")
        with self.assertRaises(ValueError):
            OperationalHealthAssessor(FixedClock(datetime(2026, 7, 21))).assess(OperationalSnapshot())

    def test_future_notification_times_fail_closed(self):
        future = delivery(last_attempt_at=self.clock.now() + timedelta(seconds=1))
        assessment = self.assess(deliveries=(future,))[0]
        self.assertEqual(assessment.status, "malformed")
        self.assertEqual(assessment.reason_codes, ("invalid_notification_time",))


if __name__ == "__main__":
    unittest.main()
