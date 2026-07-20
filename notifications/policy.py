"""Deterministic selection, deduplication, cooldown, and retry policy.

This module has no delivery provider.  Callers may persist the injected state
store and report an attempted station delivery back through ``record_result``.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Any, Iterable, Protocol

from api.dtos import SignalEventDTO


APPROVED_EVENT_TYPES = frozenset({"new_signal", "weakening", "invalidation"})
APPROVED_EXCHANGE_LABELS = frozenset({"币安", "欧易"})


class Clock(Protocol):
    def now(self) -> datetime: ...


@dataclass(frozen=True)
class NotificationPolicyConfig:
    """Provisional M7 policy values; these are not strategy thresholds."""

    max_event_age: timedelta = timedelta(minutes=5)
    cooldown: timedelta = timedelta(minutes=10)
    retry_delay: timedelta = timedelta(seconds=30)
    max_attempts: int = 3

    def __post_init__(self) -> None:
        if self.max_event_age <= timedelta(0):
            raise ValueError("max_event_age_must_be_positive")
        if self.cooldown < timedelta(0):
            raise ValueError("cooldown_must_not_be_negative")
        if self.retry_delay <= timedelta(0):
            raise ValueError("retry_delay_must_be_positive")
        if self.max_attempts < 1:
            raise ValueError("max_attempts_must_be_positive")


@dataclass(frozen=True)
class StoredDelivery:
    deduplication_key: str
    cooldown_key: str
    status: str
    attempts: int
    last_attempt_at: datetime
    next_retry_at: datetime | None
    delivered_at: datetime | None


class NotificationStateStore(Protocol):
    """Injected persistence seam; implementations may reconstruct after restart."""

    def get_delivery(self, deduplication_key: str) -> StoredDelivery | None: ...
    def save_delivery(self, delivery: StoredDelivery) -> None: ...
    def get_cooldown(self, cooldown_key: str) -> datetime | None: ...
    def save_cooldown(self, cooldown_key: str, delivered_at: datetime) -> None: ...


class InMemoryNotificationStateStore:
    """Offline store that can be rebuilt from an exported deterministic snapshot."""

    def __init__(
        self,
        deliveries: Iterable[StoredDelivery] = (),
        cooldowns: Iterable[tuple[str, datetime]] = (),
    ) -> None:
        self._deliveries = {item.deduplication_key: item for item in deliveries}
        self._cooldowns = dict(cooldowns)

    def get_delivery(self, deduplication_key: str) -> StoredDelivery | None:
        return self._deliveries.get(deduplication_key)

    def save_delivery(self, delivery: StoredDelivery) -> None:
        self._deliveries[delivery.deduplication_key] = delivery

    def get_cooldown(self, cooldown_key: str) -> datetime | None:
        return self._cooldowns.get(cooldown_key)

    def save_cooldown(self, cooldown_key: str, delivered_at: datetime) -> None:
        self._cooldowns[cooldown_key] = delivered_at

    def snapshot(self) -> tuple[tuple[StoredDelivery, ...], tuple[tuple[str, datetime], ...]]:
        deliveries = tuple(sorted(self._deliveries.values(), key=lambda item: item.deduplication_key))
        cooldowns = tuple(sorted(self._cooldowns.items()))
        return deliveries, cooldowns


@dataclass(frozen=True)
class StationNotification:
    notification_id: str
    deduplication_key: str
    source_event_type: str
    source_signal_id: str
    source_occurred_at: str
    exchange_label: str
    symbol: str
    reason_codes: tuple[str, ...]
    title: str
    body: str
    source_message: str


@dataclass(frozen=True)
class NotificationDecision:
    should_deliver: bool
    reason: str
    attempt: int | None = None
    notification: StationNotification | None = None


class NotificationPolicy:
    def __init__(self, store: NotificationStateStore, clock: Clock, config: NotificationPolicyConfig | None = None) -> None:
        self.store = store
        self.clock = clock
        self.config = config or NotificationPolicyConfig()

    def select(self, events: Iterable[Any]) -> tuple[NotificationDecision, ...]:
        return tuple(self.decide(event) for event in events)

    def decide(self, event: Any) -> NotificationDecision:
        validated = self._validate(event)
        if isinstance(validated, str):
            return NotificationDecision(False, validated)
        occurred_at = validated
        assert isinstance(event, SignalEventDTO)
        now = self._aware_utc(self.clock.now())
        if occurred_at > now:
            return NotificationDecision(False, "future_event")
        if now - occurred_at > self.config.max_event_age:
            return NotificationDecision(False, "stale_event")

        deduplication_key = self._deduplication_key(event)
        cooldown_key = f"{event.signal_id}:{event.event_type}"
        existing = self.store.get_delivery(deduplication_key)
        if existing is not None:
            if existing.status == "delivered":
                return NotificationDecision(False, "duplicate_delivered")
            if existing.attempts >= self.config.max_attempts:
                return NotificationDecision(False, "retry_exhausted")
            if existing.next_retry_at is not None and now < existing.next_retry_at:
                return NotificationDecision(False, "retry_not_due")
            return self._reserve(event, deduplication_key, cooldown_key, now, existing.attempts + 1, "retry")

        last_delivered = self.store.get_cooldown(cooldown_key)
        if last_delivered is not None and now - self._aware_utc(last_delivered) < self.config.cooldown:
            return NotificationDecision(False, "cooldown_active")
        return self._reserve(event, deduplication_key, cooldown_key, now, 1, "selected")

    def record_result(self, decision: NotificationDecision, delivered: bool) -> None:
        if not decision.should_deliver or decision.notification is None or decision.attempt is None:
            raise ValueError("decision_is_not_deliverable")
        now = self._aware_utc(self.clock.now())
        notification = decision.notification
        current = self.store.get_delivery(notification.deduplication_key)
        if current is None or current.attempts != decision.attempt:
            raise ValueError("delivery_state_mismatch")
        if delivered:
            updated = StoredDelivery(current.deduplication_key, current.cooldown_key, "delivered", current.attempts, current.last_attempt_at, None, now)
            self.store.save_delivery(updated)
            self.store.save_cooldown(current.cooldown_key, now)
        else:
            updated = StoredDelivery(current.deduplication_key, current.cooldown_key, "failed", current.attempts, current.last_attempt_at, now + self.config.retry_delay, None)
            self.store.save_delivery(updated)

    def _reserve(self, event: SignalEventDTO, deduplication_key: str, cooldown_key: str, now: datetime, attempt: int, reason: str) -> NotificationDecision:
        self.store.save_delivery(StoredDelivery(deduplication_key, cooldown_key, "pending", attempt, now, now + self.config.retry_delay, None))
        notification = self._notification(event, deduplication_key)
        return NotificationDecision(True, reason, attempt, notification)

    @staticmethod
    def _validate(event: Any) -> datetime | str:
        if not isinstance(event, SignalEventDTO):
            return "malformed_event"
        if event.event_type not in APPROVED_EVENT_TYPES:
            return "unsupported_event_type"
        required_strings = (event.signal_id, event.exchange_label, event.symbol, event.occurred_at, event.message)
        if any(not isinstance(value, str) or not value.strip() for value in required_strings):
            return "malformed_event"
        if event.exchange_label not in APPROVED_EXCHANGE_LABELS:
            return "malformed_event"
        if not isinstance(event.reason_codes, tuple) or any(not isinstance(code, str) or not code for code in event.reason_codes):
            return "malformed_event"
        try:
            parsed = datetime.fromisoformat(event.occurred_at.replace("Z", "+00:00"))
        except ValueError:
            return "malformed_event"
        if parsed.tzinfo is None:
            return "malformed_event"
        return parsed.astimezone(timezone.utc)

    @staticmethod
    def _aware_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("clock_must_be_timezone_aware")
        return value.astimezone(timezone.utc)

    @staticmethod
    def _deduplication_key(event: SignalEventDTO) -> str:
        source = "|".join((event.event_type, event.signal_id or "", event.exchange_label or "", event.symbol or "", event.occurred_at))
        return f"station.v1:{sha256(source.encode('utf-8')).hexdigest()}"

    @staticmethod
    def _notification(event: SignalEventDTO, deduplication_key: str) -> StationNotification:
        copy = {
            "new_signal": ("发现新的做多信号", "请查看参考入场和失效条件；本提醒不会执行交易。"),
            "weakening": ("做多信号减弱", "请注意风险并查看信号详情；本提醒不会执行交易。"),
            "invalidation": ("做多信号已消失", "原做多信号已失效；这不是做空信号，也不会执行交易。"),
        }
        heading, body = copy[event.event_type]
        return StationNotification(
            notification_id=deduplication_key.replace("station.v1:", "station-notification-v1-"),
            deduplication_key=deduplication_key,
            source_event_type=event.event_type,
            source_signal_id=event.signal_id or "",
            source_occurred_at=event.occurred_at,
            exchange_label=event.exchange_label or "",
            symbol=event.symbol or "",
            reason_codes=event.reason_codes,
            title=f"{event.exchange_label} {event.symbol}：{heading}",
            body=body,
            source_message=event.message,
        )
