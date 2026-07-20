"""Availability-time-safe lifecycle replay and price-observation outcomes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Mapping, Sequence

from strategy.lifecycle import LifecycleConfig, SignalLifecycle, Snapshot, StateEvent


WINDOWS: tuple[tuple[str, timedelta], ...] = (
    ("5m", timedelta(minutes=5)),
    ("15m", timedelta(minutes=15)),
    ("1h", timedelta(hours=1)),
    ("4h", timedelta(hours=4)),
    ("1d", timedelta(days=1)),
)


def _time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _pct(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class PriceOutcome:
    signal_id: str
    window: str
    window_start: str
    window_end: str
    as_of_time: str
    entry_price: float
    last_price: float | None
    highest_price: float | None
    lowest_price: float | None
    max_rise_pct: float | None
    max_drawdown_pct: float | None
    peak_time: str | None
    drawdown_time: str | None
    first_extreme_order: str
    complete: bool
    missing_data: tuple[str, ...]
    strategy_result_status: str
    strategy_pnl_pct: None
    strategy_result_reason: str


@dataclass(frozen=True)
class ReplayResult:
    lifecycle_events: tuple[StateEvent, ...]
    outcomes: tuple[PriceOutcome, ...]


class HistoricalReplay:
    """Replay snapshots by availability time and calculate observation only."""

    def __init__(self, lifecycle_config: LifecycleConfig | None = None) -> None:
        self.lifecycle_config = lifecycle_config or LifecycleConfig()

    def run(self, raw_snapshots: Sequence[Mapping[str, Any]]) -> ReplayResult:
        snapshots = tuple(Snapshot.from_mapping(value) for value in raw_snapshots)
        ordered = tuple(sorted(snapshots, key=lambda item: (_time(item.available_time), _time(item.event_time), item.snapshot_id)))
        lifecycle = SignalLifecycle(self.lifecycle_config)
        for snapshot in ordered:
            lifecycle.process(snapshot.__dict__)

        armed_events = tuple(event for event in lifecycle.events if event.to_state == "armed" and event.reference_entry_price is not None and event.reference_entry_time is not None)
        outcomes: list[PriceOutcome] = []
        for event in armed_events:
            signal_snapshots = tuple(snapshot for snapshot in snapshots if snapshot.exchange == event.signal_id.split("-", 1)[0] and snapshot.symbol in event.signal_id and _time(snapshot.event_time) >= _time(event.reference_entry_time))
            outcomes.extend(self._outcomes_for_signal(event, signal_snapshots))
        return ReplayResult(lifecycle.events, tuple(outcomes))

    def _outcomes_for_signal(self, event: StateEvent, snapshots: Sequence[Snapshot]) -> list[PriceOutcome]:
        entry_time = _time(event.reference_entry_time or event.event_time)
        entry_price = Decimal(str(event.reference_entry_price))
        results: list[PriceOutcome] = []
        for window_name, duration in WINDOWS:
            end = entry_time + duration
            eligible = tuple(sorted((snapshot for snapshot in snapshots if _time(snapshot.event_time) <= end and _time(snapshot.available_time) <= end and snapshot.usable_for_signal and snapshot.data_quality in {"normal", "out_of_order"}), key=lambda item: (_time(item.event_time), _time(item.available_time), item.snapshot_id)))
            in_event_window = tuple(snapshot for snapshot in snapshots if entry_time <= _time(snapshot.event_time) <= end)
            excluded_for_availability = any(_time(snapshot.available_time) > end for snapshot in in_event_window)
            missing: list[str] = []
            if not eligible:
                missing.append("no_available_observation")
            if not any(_time(snapshot.event_time) >= end for snapshot in eligible):
                missing.append("window_end_observation_missing")
            if excluded_for_availability:
                missing.append("availability_after_window")
            complete = not missing
            if eligible:
                last = eligible[-1]
                highest = max(eligible, key=lambda item: (item.price, -_time(item.event_time).timestamp(), item.snapshot_id))
                lowest = min(eligible, key=lambda item: (item.price, _time(item.event_time).timestamp(), item.snapshot_id))
                last_price = last.price
                highest_price = highest.price
                lowest_price = lowest.price
                rise = _pct((Decimal(str(highest_price)) - entry_price) / entry_price * Decimal("100"))
                drawdown = _pct((Decimal(str(lowest_price)) - entry_price) / entry_price * Decimal("100"))
                peak_time = highest.event_time
                drawdown_time = lowest.event_time
                if _time(drawdown_time) < _time(peak_time):
                    order = "drawdown_first"
                elif _time(peak_time) < _time(drawdown_time):
                    order = "rise_first"
                else:
                    order = "same_time"
            else:
                last_price = highest_price = lowest_price = None
                rise = drawdown = None
                peak_time = drawdown_time = None
                order = "none"
            results.append(PriceOutcome(event.signal_id, window_name, entry_time.isoformat().replace("+00:00", "Z"), end.isoformat().replace("+00:00", "Z"), end.isoformat().replace("+00:00", "Z"), float(entry_price), last_price, highest_price, lowest_price, float(rise) if rise is not None else None, float(drawdown) if drawdown is not None else None, peak_time, drawdown_time, order, complete, tuple(dict.fromkeys(missing)), "not_evaluated", None, "exit_rules_fees_and_slippage_not_approved"))
        return results
