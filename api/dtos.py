"""Stable versioned DTOs for the beginner-facing read-only API."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


API_VERSION = "api.v1"


STATE_LABELS = {
    "watch": "暂无信号",
    "potential": "潜在机会，等待确认",
    "armed": "可以考虑开多",
    "active": "信号有效，继续观察",
    "weakening": "信号减弱，注意风险",
    "invalidated": "信号消失",
    "expired": "信号已过期",
}


@dataclass(frozen=True)
class SignalDTO:
    signal_id: str
    exchange: str
    exchange_label: str
    symbol: str
    market_type: str
    state: str
    state_label: str
    group: str
    can_consider_entry: bool
    quality: str
    signal_time: str
    last_confirmed_time: str
    freshness_status: str
    data_quality: str
    usable_for_signal: bool
    reason_codes: tuple[str, ...]
    reference_entry_price: float | None
    reference_entry_time: str | None
    invalidation_rule_id: str
    strategy_version: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DataHealthDTO:
    exchange: str
    exchange_label: str
    symbol: str | None
    status: str
    usable_for_signal: bool
    freshness_status: str
    last_event_time: str | None
    reason_codes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DashboardDTO:
    api_version: str
    generated_at: str
    confirmed: tuple[SignalDTO, ...]
    potential: tuple[SignalDTO, ...]
    no_signal: tuple[SignalDTO, ...]
    recent_invalidations: tuple[SignalDTO, ...]
    health: tuple[DataHealthDTO, ...]
    empty_reason: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SignalDetailDTO:
    api_version: str
    signal: SignalDTO
    state_events: tuple[dict[str, Any], ...]
    outcome_summary: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class OutcomeDTO:
    signal_id: str
    window: str
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

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StatisticsDTO:
    api_version: str
    total_signals: int
    complete_price_observation_windows: int
    incomplete_windows: int
    observed_max_rise_pct: float | None
    observed_max_drawdown_pct: float | None
    strategy_result_status: str
    strategy_result_reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SignalEventDTO:
    event_type: str
    signal_id: str | None
    exchange_label: str | None
    symbol: str | None
    occurred_at: str
    reason_codes: tuple[str, ...]
    message: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
