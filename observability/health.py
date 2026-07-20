"""Pure operational-health assessment over approved read-only snapshots.

The assessor has no logger, monitor, scheduler, provider, network, or storage.
Callers inject the current time and immutable snapshot values.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Any, Protocol

from api.dtos import DataHealthDTO
from notifications.policy import StoredDelivery


SCHEMA_VERSION = "operational-health.v1"
APPROVED_EXCHANGES = frozenset({"binance", "okx"})
APPROVED_EXCHANGE_LABELS = {"binance": "币安", "okx": "欧易"}
UNHEALTHY_STATUSES = frozenset({"delayed", "failed", "retrying", "exhausted", "stale"})


class Clock(Protocol):
    def now(self) -> datetime: ...


@dataclass(frozen=True)
class OperationalHealthConfig:
    """Provisional operational values, separate from strategy thresholds."""

    data_stale_after: timedelta = timedelta(minutes=2)
    notification_pending_after: timedelta = timedelta(seconds=30)
    notification_max_attempts: int = 3

    def __post_init__(self) -> None:
        if self.data_stale_after <= timedelta(0):
            raise ValueError("data_stale_after_must_be_positive")
        if self.notification_pending_after <= timedelta(0):
            raise ValueError("notification_pending_after_must_be_positive")
        if self.notification_max_attempts < 1:
            raise ValueError("notification_max_attempts_must_be_positive")


@dataclass(frozen=True)
class PriorUnhealthyState:
    """Unhealthy evidence explicitly reconstructed by the caller."""

    source_key: str
    assessment_id: str
    status: str
    observed_at: str
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class OperationalSnapshot:
    data_health: tuple[Any, ...] = ()
    notification_deliveries: tuple[Any, ...] = ()
    prior_unhealthy: tuple[PriorUnhealthyState, ...] = ()


@dataclass(frozen=True)
class OperationalAssessment:
    assessment_id: str
    status: str
    severity: str
    source: str
    source_key: str
    observed_at: str
    reason_codes: tuple[str, ...]
    message: str
    action_scope: str = "operational_only"
    prior_assessment_id: str | None = None


class OperationalHealthAssessor:
    def __init__(self, clock: Clock, config: OperationalHealthConfig | None = None) -> None:
        self.clock = clock
        self.config = config or OperationalHealthConfig()

    def assess(self, snapshot: OperationalSnapshot) -> tuple[OperationalAssessment, ...]:
        if not isinstance(snapshot, OperationalSnapshot):
            raise ValueError("snapshot_must_be_operational_snapshot")
        if not isinstance(snapshot.data_health, tuple) or not isinstance(snapshot.notification_deliveries, tuple) or not isinstance(snapshot.prior_unhealthy, tuple):
            raise ValueError("snapshot_collections_must_be_tuples")
        now = self._aware_utc(self.clock.now())
        prior = self._valid_prior(snapshot.prior_unhealthy)
        assessments = [self._assess_data_health(item, now, prior) for item in snapshot.data_health]
        assessments.extend(self._assess_delivery(item, now, prior) for item in snapshot.notification_deliveries)
        if not assessments:
            assessments.append(self._build("empty", "warning", "snapshot", "snapshot:empty", now, ("no_operational_sources",)))
        return tuple(sorted(assessments, key=lambda item: (item.source, item.source_key, item.assessment_id)))

    def _assess_data_health(
        self,
        item: Any,
        now: datetime,
        prior: dict[str, PriorUnhealthyState],
    ) -> OperationalAssessment:
        if not self._valid_data_health(item):
            return self._build("malformed", "critical", "data_health", "data:malformed", now, ("malformed_data_health_snapshot",))
        assert isinstance(item, DataHealthDTO)
        observed = self._parse_time(item.last_event_time)
        if observed is None or observed > now:
            return self._build("malformed", "critical", "data_health", "data:malformed", now, ("invalid_data_health_time",))
        source_key = f"data:{item.exchange}:{item.symbol or '*'}"
        normalized = item.status.lower()
        reasons = item.reason_codes

        if normalized == "healthy":
            if not item.usable_for_signal or item.freshness_status not in {"fresh", "recent"}:
                return self._build("malformed", "critical", "data_health", source_key, observed, ("inconsistent_healthy_state",))
            if now - observed > self.config.data_stale_after:
                return self._build("stale", "warning", "data_health", source_key, observed, reasons + ("last_event_exceeds_operational_limit",))
            return self._healthy_or_recovered("data_health", source_key, observed, reasons, prior)
        if normalized == "stale" or item.freshness_status == "stale":
            return self._build("stale", "warning", "data_health", source_key, observed, reasons or ("data_stale",))
        if normalized == "delayed":
            return self._build("delayed", "warning", "data_health", source_key, observed, reasons or ("data_delayed",))
        if normalized == "failed":
            return self._build("failed", "critical", "data_health", source_key, observed, reasons or ("data_source_failed",))
        return self._build("unknown", "critical", "data_health", source_key, observed, reasons + ("unknown_data_health_state",))

    def _assess_delivery(
        self,
        item: Any,
        now: datetime,
        prior: dict[str, PriorUnhealthyState],
    ) -> OperationalAssessment:
        if not self._valid_delivery(item):
            return self._build("malformed", "critical", "notification_delivery", "notification:malformed", now, ("malformed_notification_snapshot",))
        assert isinstance(item, StoredDelivery)
        source_key = f"notification:{item.deduplication_key}"
        observed = self._aware_utc(item.delivered_at or item.last_attempt_at)
        if observed > now or item.next_retry_at is not None and self._aware_utc(item.next_retry_at) < self._aware_utc(item.last_attempt_at):
            return self._build("malformed", "critical", "notification_delivery", source_key, now, ("invalid_notification_time",))
        normalized = item.status.lower()
        if normalized == "delivered":
            return self._healthy_or_recovered("notification_delivery", source_key, observed, ("notification_delivered",), prior)
        if normalized == "pending":
            if now - self._aware_utc(item.last_attempt_at) > self.config.notification_pending_after:
                return self._build("delayed", "warning", "notification_delivery", source_key, observed, ("notification_pending_exceeds_limit",))
            return self._build("pending", "info", "notification_delivery", source_key, observed, ("notification_attempt_pending",))
        if normalized == "failed":
            if item.attempts >= self.config.notification_max_attempts:
                return self._build("exhausted", "critical", "notification_delivery", source_key, observed, ("notification_retry_exhausted",))
            if item.next_retry_at is not None and now < self._aware_utc(item.next_retry_at):
                return self._build("retrying", "warning", "notification_delivery", source_key, observed, ("notification_retry_scheduled",))
            return self._build("failed", "critical", "notification_delivery", source_key, observed, ("notification_retry_due",))
        return self._build("unknown", "critical", "notification_delivery", source_key, observed, ("unknown_notification_state",))

    def _healthy_or_recovered(
        self,
        source: str,
        source_key: str,
        observed: datetime,
        reasons: tuple[str, ...],
        prior: dict[str, PriorUnhealthyState],
    ) -> OperationalAssessment:
        previous = prior.get(source_key)
        previous_observed = self._parse_time(previous.observed_at) if previous is not None else None
        if previous is None or previous_observed is None or previous_observed > observed:
            return self._build("healthy", "info", source, source_key, observed, reasons or ("source_healthy",))
        recovery_reasons = reasons + (f"recovered_from_{previous.status}",)
        return self._build("recovered", "info", source, source_key, observed, recovery_reasons, previous.assessment_id)

    @staticmethod
    def _valid_data_health(item: Any) -> bool:
        return (
            isinstance(item, DataHealthDTO)
            and item.exchange in APPROVED_EXCHANGES
            and item.exchange_label == APPROVED_EXCHANGE_LABELS[item.exchange]
            and (item.symbol is None or isinstance(item.symbol, str) and bool(item.symbol.strip()))
            and isinstance(item.status, str)
            and bool(item.status.strip())
            and isinstance(item.freshness_status, str)
            and isinstance(item.usable_for_signal, bool)
            and isinstance(item.reason_codes, tuple)
            and all(isinstance(code, str) and bool(code) for code in item.reason_codes)
        )

    @staticmethod
    def _valid_delivery(item: Any) -> bool:
        if not isinstance(item, StoredDelivery):
            return False
        if not all(isinstance(value, str) and bool(value) for value in (item.deduplication_key, item.cooldown_key, item.status)):
            return False
        if not isinstance(item.attempts, int) or isinstance(item.attempts, bool) or item.attempts < 1:
            return False
        if not isinstance(item.last_attempt_at, datetime) or item.last_attempt_at.tzinfo is None:
            return False
        if item.next_retry_at is not None and (not isinstance(item.next_retry_at, datetime) or item.next_retry_at.tzinfo is None):
            return False
        if item.delivered_at is not None and (not isinstance(item.delivered_at, datetime) or item.delivered_at.tzinfo is None):
            return False
        return item.status != "delivered" or item.delivered_at is not None

    @classmethod
    def _valid_prior(cls, items: tuple[PriorUnhealthyState, ...]) -> dict[str, PriorUnhealthyState]:
        valid: dict[str, PriorUnhealthyState] = {}
        for item in items:
            if not isinstance(item, PriorUnhealthyState):
                continue
            if item.status not in UNHEALTHY_STATUSES:
                continue
            if not all(isinstance(value, str) and bool(value) for value in (item.source_key, item.assessment_id, item.observed_at)):
                continue
            if not item.assessment_id.startswith(f"{SCHEMA_VERSION}:"):
                continue
            if not isinstance(item.reason_codes, tuple) or any(not isinstance(code, str) or not code for code in item.reason_codes):
                continue
            if cls._parse_time(item.observed_at) is None:
                continue
            existing = valid.get(item.source_key)
            if existing is None or (item.observed_at, item.assessment_id) > (existing.observed_at, existing.assessment_id):
                valid[item.source_key] = item
        return valid

    @staticmethod
    def _parse_time(value: str | None) -> datetime | None:
        if not isinstance(value, str) or not value:
            return None
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
        if parsed.tzinfo is None:
            return None
        return parsed.astimezone(timezone.utc)

    @staticmethod
    def _aware_utc(value: datetime) -> datetime:
        if not isinstance(value, datetime) or value.tzinfo is None:
            raise ValueError("clock_and_snapshot_times_must_be_timezone_aware")
        return value.astimezone(timezone.utc)

    @classmethod
    def _build(
        cls,
        status: str,
        severity: str,
        source: str,
        source_key: str,
        observed: datetime,
        reasons: tuple[str, ...],
        prior_assessment_id: str | None = None,
    ) -> OperationalAssessment:
        observed_at = cls._timestamp(observed)
        evidence = "|".join((source, source_key, status, observed_at, ",".join(reasons), prior_assessment_id or ""))
        assessment_id = f"{SCHEMA_VERSION}:{sha256(evidence.encode('utf-8')).hexdigest()}"
        messages = {
            "healthy": "Operational source is healthy; this assessment does not perform a trade.",
            "pending": "Notification attempt is pending; this assessment does not perform a trade.",
            "delayed": "Operational source is delayed; this assessment does not perform a trade.",
            "retrying": "Notification retry is scheduled; this assessment does not perform a trade.",
            "failed": "Operational source failed; this assessment does not perform a trade.",
            "exhausted": "Notification retries are exhausted; this assessment does not perform a trade.",
            "recovered": "Operational source recovered from represented unhealthy state; this assessment does not perform a trade.",
            "stale": "Operational source is stale; this assessment does not perform a trade.",
            "empty": "No operational source snapshot was supplied; this assessment does not perform a trade.",
            "malformed": "Operational source snapshot is malformed; details are suppressed and no trade is performed.",
            "unknown": "Operational source state is unknown; this assessment does not perform a trade.",
        }
        return OperationalAssessment(assessment_id, status, severity, source, source_key, observed_at, reasons, messages[status], "operational_only", prior_assessment_id)

    @staticmethod
    def _timestamp(value: datetime) -> str:
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
