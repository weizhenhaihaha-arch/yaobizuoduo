"""Deterministic long-signal lifecycle with provisional thresholds.

The engine consumes normalized snapshots only. It has no exchange, network,
order, frontend, or short-strategy responsibilities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping


STATES = ("watch", "potential", "armed", "active", "weakening", "invalidated", "expired")
TERMINAL_STATES = {"invalidated", "expired"}


def _time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


@dataclass(frozen=True)
class LifecycleConfig:
    """All numeric values are provisional and must be replay-validated later."""

    candidate_price_change_pct: float = 0.30
    candidate_volume_ratio: float = 1.50
    candidate_oi_change_pct: float = 0.20
    confirm_price_change_pct: float = 0.80
    confirm_volume_ratio: float = 2.00
    confirm_oi_change_pct: float = 0.50
    max_chase_price_change_pct: float = 4.00
    weakening_volume_ratio: float = 1.20
    weakening_oi_change_pct: float = 0.00
    invalidation_buffer_pct: float = 0.50
    cooldown_minutes: int = 30
    expiry_minutes: int = 60
    max_snapshot_age_ms: int = 2000
    version: str = "provisional-m3-v1"


@dataclass(frozen=True)
class Snapshot:
    snapshot_id: str
    exchange: str
    symbol: str
    market_type: str
    event_time: str
    available_time: str
    data_quality: str
    usable_for_signal: bool
    price: float
    price_change_pct: float
    volume_ratio: float
    oi_change_pct: float
    structure_id: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "Snapshot":
        return cls(
            snapshot_id=str(value["snapshot_id"]),
            exchange=str(value["exchange"]),
            symbol=str(value["symbol"]),
            market_type=str(value["market_type"]),
            event_time=str(value["event_time"]),
            available_time=str(value["available_time"]),
            data_quality=str(value["data_quality"]),
            usable_for_signal=bool(value["usable_for_signal"]),
            price=float(value["price"]),
            price_change_pct=float(value["price_change_pct"]),
            volume_ratio=float(value["volume_ratio"]),
            oi_change_pct=float(value["oi_change_pct"]),
            structure_id=str(value["structure_id"]),
        )


@dataclass(frozen=True)
class StateEvent:
    event_id: str
    signal_id: str
    from_state: str
    to_state: str
    event_time: str
    snapshot_id: str
    reason_codes: tuple[str, ...]
    reference_entry_price: float | None
    reference_entry_time: str | None
    invalidation_rule_id: str


@dataclass(frozen=True)
class Evaluation:
    state: str
    signal_id: str | None
    reason_codes: tuple[str, ...]
    events: tuple[StateEvent, ...]
    vetoed: bool = False


@dataclass
class _TrackedSignal:
    signal_id: str
    exchange: str
    symbol: str
    structure_id: str
    state: str
    created_time: str
    last_event_time: str
    reference_entry_price: float | None = None
    reference_entry_time: str | None = None
    invalidated_time: str | None = None


class SignalLifecycle:
    """Stateful coordinator whose event log is append-only and deterministic."""

    def __init__(self, config: LifecycleConfig | None = None) -> None:
        self.config = config or LifecycleConfig()
        self._signals: dict[tuple[str, str], _TrackedSignal] = {}
        self._events: list[StateEvent] = []

    @property
    def events(self) -> tuple[StateEvent, ...]:
        return tuple(self._events)

    def process(self, raw_snapshot: Mapping[str, Any]) -> Evaluation:
        snapshot = Snapshot.from_mapping(raw_snapshot)
        self._validate_snapshot(snapshot)
        key = (snapshot.exchange, snapshot.symbol)
        tracked = self._signals.get(key)

        if not self._usable(snapshot):
            return Evaluation(tracked.state if tracked else "watch", tracked.signal_id if tracked else None, ("data_health_veto", snapshot.data_quality), (), True)

        if tracked and tracked.state in TERMINAL_STATES:
            if self._cooldown_active(tracked, snapshot) or tracked.structure_id == snapshot.structure_id:
                return Evaluation(tracked.state, tracked.signal_id, ("duplicate_trigger_suppressed", "new_structure_required"), ())
            tracked = None
            self._signals.pop(key, None)

        candidate = self._is_candidate(snapshot)
        confirmed = self._is_confirmed(snapshot)
        if tracked is None:
            if not candidate:
                return Evaluation("watch", None, ("candidate_conditions_not_met",), ())
            signal_id = self._signal_id(snapshot)
            tracked = _TrackedSignal(signal_id, snapshot.exchange, snapshot.symbol, snapshot.structure_id, "watch", snapshot.event_time, snapshot.event_time)
            self._signals[key] = tracked
            events = [self._transition(tracked, snapshot, "potential", ("candidate_activity",))]
            if confirmed:
                events.append(self._transition(tracked, snapshot, "armed", self._confirmation_reasons(snapshot), snapshot))
            return Evaluation(tracked.state, tracked.signal_id, events[-1].reason_codes, tuple(events))

        if self._expired(tracked, snapshot):
            event = self._transition(tracked, snapshot, "expired", ("signal_age_exceeded",))
            return Evaluation(tracked.state, tracked.signal_id, event.reason_codes, (event,))

        if tracked.state in {"armed", "active", "weakening"} and self._invalidation_breached(tracked, snapshot):
            event = self._transition(tracked, snapshot, "invalidated", ("price_below_invalidation",))
            tracked.invalidated_time = snapshot.event_time
            return Evaluation(tracked.state, tracked.signal_id, event.reason_codes, (event,))

        if tracked.state == "potential":
            if confirmed:
                event = self._transition(tracked, snapshot, "armed", self._confirmation_reasons(snapshot), snapshot)
                return Evaluation(tracked.state, tracked.signal_id, event.reason_codes, (event,))
            if not candidate:
                event = self._transition(tracked, snapshot, "weakening", ("candidate_conditions_faded",))
                return Evaluation(tracked.state, tracked.signal_id, event.reason_codes, (event,))
            return Evaluation(tracked.state, tracked.signal_id, ("awaiting_confirmation",), ())

        if tracked.state == "armed":
            if self._is_weakening(snapshot):
                event = self._transition(tracked, snapshot, "weakening", ("confirmation_conditions_faded",))
                return Evaluation(tracked.state, tracked.signal_id, event.reason_codes, (event,))
            event = self._transition(tracked, snapshot, "active", ("confirmation_remains_valid",))
            return Evaluation(tracked.state, tracked.signal_id, event.reason_codes, (event,))

        if tracked.state == "weakening":
            if confirmed:
                event = self._transition(tracked, snapshot, "active", ("conditions_recovered",))
                return Evaluation(tracked.state, tracked.signal_id, event.reason_codes, (event,))
            event = self._transition(tracked, snapshot, "invalidated", ("weakening_persisted",))
            tracked.invalidated_time = snapshot.event_time
            return Evaluation(tracked.state, tracked.signal_id, event.reason_codes, (event,))

        if tracked.state == "active" and self._is_weakening(snapshot):
            event = self._transition(tracked, snapshot, "weakening", ("confirmation_conditions_faded",))
            return Evaluation(tracked.state, tracked.signal_id, event.reason_codes, (event,))

        return Evaluation(tracked.state, tracked.signal_id, ("signal_remains_valid",), ())

    def _transition(self, tracked: _TrackedSignal, snapshot: Snapshot, to_state: str, reasons: tuple[str, ...], entry_snapshot: Snapshot | None = None) -> StateEvent:
        from_state = tracked.state
        if to_state not in STATES:
            raise ValueError(f"unsupported_state: {to_state}")
        if to_state == "armed" and entry_snapshot is not None:
            tracked.reference_entry_price = entry_snapshot.price
            tracked.reference_entry_time = entry_snapshot.event_time
        event_number = len(self._events) + 1
        event = StateEvent(f"{tracked.signal_id}-event-{event_number:04d}", tracked.signal_id, from_state, to_state, snapshot.event_time, snapshot.snapshot_id, tuple(reasons), tracked.reference_entry_price, tracked.reference_entry_time, "price_below_entry_buffer_v1")
        self._events.append(event)
        tracked.state = to_state
        tracked.last_event_time = snapshot.event_time
        return event

    def _validate_snapshot(self, snapshot: Snapshot) -> None:
        if snapshot.exchange not in {"binance", "okx"}:
            raise ValueError("unsupported_exchange")
        if snapshot.market_type != "usdt_perpetual":
            raise ValueError("unsupported_market_type")
        if snapshot.price <= 0 or snapshot.volume_ratio < 0:
            raise ValueError("invalid_snapshot_value")
        if _time(snapshot.available_time) < _time(snapshot.event_time):
            raise ValueError("availability_before_event")

    def _usable(self, snapshot: Snapshot) -> bool:
        if not snapshot.usable_for_signal or snapshot.data_quality not in {"normal", "out_of_order"}:
            return False
        age_ms = (_time(snapshot.available_time) - _time(snapshot.event_time)).total_seconds() * 1000
        return age_ms <= self.config.max_snapshot_age_ms

    def _is_candidate(self, snapshot: Snapshot) -> bool:
        return snapshot.price_change_pct >= self.config.candidate_price_change_pct or snapshot.volume_ratio >= self.config.candidate_volume_ratio or snapshot.oi_change_pct >= self.config.candidate_oi_change_pct

    def _is_confirmed(self, snapshot: Snapshot) -> bool:
        return (snapshot.price_change_pct >= self.config.confirm_price_change_pct and snapshot.volume_ratio >= self.config.confirm_volume_ratio and snapshot.oi_change_pct >= self.config.confirm_oi_change_pct and snapshot.price_change_pct <= self.config.max_chase_price_change_pct)

    def _is_weakening(self, snapshot: Snapshot) -> bool:
        return snapshot.volume_ratio < self.config.weakening_volume_ratio or snapshot.oi_change_pct < self.config.weakening_oi_change_pct

    def _invalidation_breached(self, tracked: _TrackedSignal, snapshot: Snapshot) -> bool:
        if tracked.reference_entry_price is None:
            return False
        floor = tracked.reference_entry_price * (1 - self.config.invalidation_buffer_pct / 100)
        return snapshot.price < floor

    def _expired(self, tracked: _TrackedSignal, snapshot: Snapshot) -> bool:
        return (_time(snapshot.event_time) - _time(tracked.created_time)) >= timedelta(minutes=self.config.expiry_minutes)

    def _cooldown_active(self, tracked: _TrackedSignal, snapshot: Snapshot) -> bool:
        if tracked.invalidated_time is None:
            return False
        return _time(snapshot.event_time) < _time(tracked.invalidated_time) + timedelta(minutes=self.config.cooldown_minutes)

    def _signal_id(self, snapshot: Snapshot) -> str:
        return f"{snapshot.exchange}-{snapshot.symbol}-{snapshot.structure_id}"

    def _confirmation_reasons(self, snapshot: Snapshot) -> tuple[str, ...]:
        return ("price_momentum_confirmed", "volume_expansion_confirmed", "oi_support_confirmed", "provisional_thresholds")
