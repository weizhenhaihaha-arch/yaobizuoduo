"""Read-only API service composed behind storage interfaces."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping, Protocol, Sequence

from .dtos import API_VERSION, STATE_LABELS, DashboardDTO, DataHealthDTO, OutcomeDTO, SignalDetailDTO, SignalDTO, SignalEventDTO, StatisticsDTO


EXCHANGE_LABELS = {"binance": "币安", "okx": "欧易"}
CONFIRMED_STATES = {"armed", "active", "weakening"}


class SignalNotFoundError(LookupError):
    """Raised only when a requested signal ID is absent from the read model."""


class ReadModel(Protocol):
    def signals(self) -> Iterable[Mapping[str, Any]]: ...
    def signal_events(self, signal_id: str) -> Iterable[Mapping[str, Any]]: ...
    def outcomes(self, signal_id: str | None = None) -> Iterable[Mapping[str, Any]]: ...
    def health(self) -> Iterable[Mapping[str, Any]]: ...


@dataclass
class InMemoryReadModel:
    signal_records: list[Mapping[str, Any]]
    event_records: dict[str, list[Mapping[str, Any]]]
    outcome_records: list[Mapping[str, Any]]
    health_records: list[Mapping[str, Any]]

    def signals(self) -> Iterable[Mapping[str, Any]]:
        return tuple(self.signal_records)

    def signal_events(self, signal_id: str) -> Iterable[Mapping[str, Any]]:
        return tuple(self.event_records.get(signal_id, ()))

    def outcomes(self, signal_id: str | None = None) -> Iterable[Mapping[str, Any]]:
        return tuple(item for item in self.outcome_records if signal_id is None or item["signal_id"] == signal_id)

    def health(self) -> Iterable[Mapping[str, Any]]:
        return tuple(self.health_records)


class ReadOnlyApiService:
    """DTO composition only; strategy decisions stay in M3."""

    def __init__(self, read_model: ReadModel) -> None:
        self.read_model = read_model

    def dashboard(self, generated_at: str | None = None) -> DashboardDTO:
        signals = tuple(self._signal_dto(record) for record in self.read_model.signals())
        confirmed = tuple(sorted((item for item in signals if item.group == "confirmed"), key=self._sort_key))
        potential = tuple(sorted((item for item in signals if item.group == "potential"), key=self._sort_key))
        no_signal = tuple(sorted((item for item in signals if item.group == "no_signal"), key=self._sort_key))
        invalidations = tuple(sorted((item for item in signals if item.state in {"invalidated", "expired"}), key=self._sort_key))
        health = tuple(self._health_dto(record) for record in self.read_model.health())
        empty_reason = None
        if not confirmed and not potential:
            empty_reason = "当前没有满足确认条件的做多信号；请查看潜在机会、观察池或历史结果。"
        return DashboardDTO(API_VERSION, generated_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), confirmed, potential, no_signal, invalidations, health, empty_reason)

    def signal_detail(self, signal_id: str) -> SignalDetailDTO:
        record = self._find_signal(signal_id)
        signal = self._signal_dto(record)
        outcomes = tuple(self._outcome_dto(item).to_dict() for item in self.read_model.outcomes(signal_id))
        return SignalDetailDTO(API_VERSION, signal, tuple(self.read_model.signal_events(signal_id)), {"outcomes": outcomes, "strategy_result_status": "not_evaluated"})

    def history(self) -> tuple[SignalDTO, ...]:
        return tuple(sorted((self._signal_dto(record) for record in self.read_model.signals()), key=self._sort_key))

    def outcomes(self, signal_id: str) -> tuple[OutcomeDTO, ...]:
        return tuple(self._outcome_dto(item) for item in self.read_model.outcomes(signal_id))

    def statistics(self) -> StatisticsDTO:
        records = tuple(self.read_model.outcomes())
        complete = tuple(item for item in records if bool(item["complete"]))
        rises = [float(item["max_rise_pct"]) for item in complete if item.get("max_rise_pct") is not None]
        drawdowns = [float(item["max_drawdown_pct"]) for item in complete if item.get("max_drawdown_pct") is not None]
        return StatisticsDTO(API_VERSION, len({item["signal_id"] for item in records}), len(complete), len(records) - len(complete), max(rises) if rises else None, min(drawdowns) if drawdowns else None, "not_evaluated", "exit_rules_fees_and_slippage_not_approved")

    def health(self) -> tuple[DataHealthDTO, ...]:
        return tuple(self._health_dto(record) for record in self.read_model.health())

    def event_messages(self, event_records: Iterable[Mapping[str, Any]]) -> tuple[SignalEventDTO, ...]:
        messages: list[SignalEventDTO] = []
        for record in event_records:
            event_type = str(record["event_type"])
            exchange = str(record["exchange"]) if record.get("exchange") else None
            label = EXCHANGE_LABELS.get(exchange) if exchange else None
            symbol = record.get("symbol")
            message = {
                "new_signal": "发现新的做多信号，请查看参考入场和失效条件。",
                "weakening": "做多信号减弱，请注意风险。",
                "invalidation": "做多信号已消失，请停止按原信号继续埋伏。",
                "stale_data": "行情数据延迟，暂不判断信号。",
            }.get(event_type, "信号状态已更新，请查看详情。")
            messages.append(SignalEventDTO(event_type, record.get("signal_id"), label, symbol, str(record["occurred_at"]), tuple(record.get("reason_codes", ())), message))
        return tuple(messages)

    def _find_signal(self, signal_id: str) -> Mapping[str, Any]:
        for record in self.read_model.signals():
            if record["signal_id"] == signal_id:
                return record
        raise SignalNotFoundError(signal_id)

    def _signal_dto(self, record: Mapping[str, Any]) -> SignalDTO:
        state = str(record["state"])
        exchange = str(record["exchange"])
        quality = "强" if state == "armed" else "中" if state in {"active", "potential"} else "弱"
        group = "confirmed" if state in CONFIRMED_STATES else "potential" if state == "potential" else "no_signal"
        freshness_status = str(record.get("freshness_status", "unknown")).lower()
        data_quality = str(record.get("data_quality", "unknown")).lower()
        market_type = str(record.get("market_type", "")).lower()
        usable = bool(record.get("usable_for_signal", False)) and exchange in EXCHANGE_LABELS and market_type == "usdt_perpetual" and freshness_status in {"fresh", "recent"} and data_quality in {"normal", "out_of_order"}
        return SignalDTO(str(record["signal_id"]), exchange, EXCHANGE_LABELS.get(exchange, exchange), str(record["symbol"]), str(record.get("market_type", "usdt_perpetual")), state, STATE_LABELS.get(state, state), group, state == "armed" and usable, quality, str(record["event_time"]), str(record.get("last_confirmed_time", record["event_time"])), str(record.get("freshness_status", "unknown")), str(record.get("data_quality", "unknown")), usable, tuple(record.get("reason_codes", ())), record.get("reference_entry_price"), record.get("reference_entry_time"), str(record.get("invalidation_rule_id", "unknown")), str(record.get("strategy_version", "unknown")))

    def _health_dto(self, record: Mapping[str, Any]) -> DataHealthDTO:
        exchange = str(record["exchange"])
        return DataHealthDTO(exchange, EXCHANGE_LABELS.get(exchange, exchange), record.get("symbol"), str(record["status"]), bool(record.get("usable_for_signal", False)), str(record.get("freshness_status", "unknown")), record.get("last_event_time"), tuple(record.get("reason_codes", ())))

    def _outcome_dto(self, record: Mapping[str, Any]) -> OutcomeDTO:
        return OutcomeDTO(str(record["signal_id"]), str(record["window"]), float(record["entry_price"]), record.get("last_price"), record.get("highest_price"), record.get("lowest_price"), record.get("max_rise_pct"), record.get("max_drawdown_pct"), record.get("peak_time"), record.get("drawdown_time"), str(record.get("first_extreme_order", "none")), bool(record["complete"]), tuple(record.get("missing_data", ())), str(record.get("strategy_result_status", "not_evaluated")), None, str(record.get("strategy_result_reason", "exit_rules_fees_and_slippage_not_approved")))

    @staticmethod
    def _sort_key(item: SignalDTO) -> tuple[int, int, str, str]:
        state_rank = {"armed": 0, "active": 1, "weakening": 2, "potential": 3, "watch": 4, "invalidated": 5, "expired": 6}
        freshness_rank = {"fresh": 0, "recent": 1, "stale": 2, "unknown": 3}
        return (state_rank.get(item.state, 9), freshness_rank.get(item.freshness_status, 9), item.exchange, item.symbol)
