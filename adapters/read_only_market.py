"""Read-only Binance/OKX normalization and data-health boundaries.

This module deliberately has no network client. Adapters receive decoded public
payloads and return records conforming to the M1 contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence


class AdapterValidationError(ValueError):
    """Deterministic validation failure for an exchange payload."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


def _utc_from_milliseconds(value: Any, field: str) -> str:
    try:
        timestamp = float(value) / 1000
        parsed = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    except (TypeError, ValueError, OverflowError, OSError) as exc:
        raise AdapterValidationError("invalid_timestamp", field) from exc
    return parsed.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _number(value: Any, field: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise AdapterValidationError("invalid_number", field) from exc
    if parsed != parsed or parsed in (float("inf"), float("-inf")):
        raise AdapterValidationError("invalid_number", field)
    return parsed


def _required(payload: Mapping[str, Any], field: str) -> Any:
    if field not in payload or payload[field] is None:
        raise AdapterValidationError("missing_required_field", field)
    return payload[field]


def _canonical_symbol(value: str) -> str:
    normalized = value.replace("-", "").replace("_", "").replace("/", "").upper()
    return normalized[:-4] if normalized.endswith("SWAP") else normalized


def _envelope(exchange: str, symbol: str, record_id: str, event_time: str, available_time: str, received_time: str, quality: str) -> dict[str, Any]:
    return {
        "schema_version": "m1.v1",
        "record_id": record_id,
        "exchange": exchange,
        "symbol": symbol,
        "market_type": "usdt_perpetual",
        "event_time": event_time,
        "available_time": available_time,
        "received_time": received_time,
        "data_quality": quality,
    }


def _validate_times(event_time: str, available_time: str, received_time: str) -> None:
    event = datetime.fromisoformat(event_time.replace("Z", "+00:00"))
    available = datetime.fromisoformat(available_time.replace("Z", "+00:00"))
    received = datetime.fromisoformat(received_time.replace("Z", "+00:00"))
    if available < event:
        raise AdapterValidationError("availability_before_event", "available_time")
    if received < available:
        raise AdapterValidationError("receipt_before_availability", "received_time")


def _health_quality(event_time: str, available_time: str, received_time: str, missing_fields: Sequence[str], connected: bool, out_of_order: bool, max_delay_ms: int) -> tuple[str, bool, str]:
    if not connected:
        return "reconnecting", False, "connection_unavailable"
    try:
        event = datetime.fromisoformat(event_time.replace("Z", "+00:00"))
        available = datetime.fromisoformat(available_time.replace("Z", "+00:00"))
        received = datetime.fromisoformat(received_time.replace("Z", "+00:00"))
    except ValueError:
        return "invalid", False, "invalid_timestamp"
    if available < event or received < available:
        return "invalid", False, "timestamp_order_invalid"
    if missing_fields:
        return "missing", False, "required_metric_missing"
    if out_of_order:
        return "out_of_order", True, "arrival_order_requires_replay_sort"
    delay_ms = int((available - event).total_seconds() * 1000)
    if delay_ms > max_delay_ms:
        return "delayed", False, "availability_delay_exceeds_limit"
    return "normal", True, "healthy"


@dataclass
class ConnectionHealth:
    """Fail-closed connection state; it never emits a trading signal."""

    state: str = "disconnected"
    consecutive_errors: int = 0
    last_error_code: str | None = None

    def connected(self) -> None:
        self.state = "connected"
        self.consecutive_errors = 0
        self.last_error_code = None

    def disconnected(self) -> None:
        self.state = "disconnected"

    def reconnecting(self) -> None:
        self.state = "reconnecting"

    def error(self, code: str) -> None:
        self.state = "error"
        self.consecutive_errors += 1
        self.last_error_code = code

    def usable(self) -> bool:
        return self.state == "connected"

    def snapshot(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "usable_for_signal": self.usable(),
            "consecutive_errors": self.consecutive_errors,
            "last_error_code": self.last_error_code,
        }


class ReadOnlyAdapter:
    exchange: str

    def normalize_symbol(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def normalize_candle(self, payload: Sequence[Any], symbol: str, record_id: str, available_time: str, received_time: str) -> dict[str, Any]:
        raise NotImplementedError

    def normalize_metrics(self, payload: Mapping[str, Any], symbol: str, record_id: str, available_time: str, received_time: str) -> dict[str, Any]:
        raise NotImplementedError

    def health(self, event_time: str, available_time: str, received_time: str, missing_fields: Sequence[str] = (), connected: bool = True, out_of_order: bool = False, max_delay_ms: int = 2000) -> dict[str, Any]:
        quality, usable, reason = _health_quality(event_time, available_time, received_time, missing_fields, connected, out_of_order, max_delay_ms)
        return {
            "exchange": self.exchange,
            "event_time": event_time,
            "available_time": available_time,
            "received_time": received_time,
            "data_quality": quality,
            "freshness_ms": max(0, int((datetime.fromisoformat(available_time.replace("Z", "+00:00")) - datetime.fromisoformat(event_time.replace("Z", "+00:00"))).total_seconds() * 1000)) if quality != "invalid" else None,
            "missing_fields": list(missing_fields),
            "out_of_order": out_of_order,
            "usable_for_signal": usable,
            "reason": reason,
        }


class BinanceAdapter(ReadOnlyAdapter):
    exchange = "binance"

    def normalize_symbol(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        raw_symbol = str(_required(payload, "symbol"))
        symbol = _canonical_symbol(raw_symbol)
        event_time = _utc_from_milliseconds(_required(payload, "onboardDate"), "onboardDate")
        available_time = _utc_from_milliseconds(_required(payload, "availableTime"), "availableTime")
        received_time = _utc_from_milliseconds(_required(payload, "receivedTime"), "receivedTime")
        _validate_times(event_time, available_time, received_time)
        result = _envelope(self.exchange, symbol, f"{self.exchange}-{symbol}-symbol", event_time, available_time, received_time, "normal")
        result.update({"record_type": "symbol", "base_asset": _required(payload, "baseAsset"), "quote_asset": _required(payload, "quoteAsset"), "contract_status": _required(payload, "status"), "price_decimals": int(_required(payload, "pricePrecision")), "quantity_decimals": int(_required(payload, "quantityPrecision"))})
        return result

    def normalize_candle(self, payload: Sequence[Any], symbol: str, record_id: str, available_time: str, received_time: str) -> dict[str, Any]:
        if len(payload) < 9:
            raise AdapterValidationError("missing_required_field", "binance_kline")
        event_time = _utc_from_milliseconds(payload[6], "close_time")
        result = _envelope(self.exchange, _canonical_symbol(symbol), record_id, event_time, available_time, received_time, "normal")
        result.update({"record_type": "candle", "interval": "5m", "open_time": _utc_from_milliseconds(payload[0], "open_time"), "close_time": event_time, "open": _number(payload[1], "open"), "high": _number(payload[2], "high"), "low": _number(payload[3], "low"), "close": _number(payload[4], "close"), "base_volume": _number(payload[5], "volume"), "quote_volume": _number(payload[7], "quote_volume"), "trade_count": int(_number(payload[8], "trade_count")), "closed": True})
        _validate_candle(result)
        return result

    def normalize_metrics(self, payload: Mapping[str, Any], symbol: str, record_id: str, available_time: str, received_time: str) -> dict[str, Any]:
        event_time = _utc_from_milliseconds(_required(payload, "time"), "time")
        result = _envelope(self.exchange, _canonical_symbol(symbol), record_id, event_time, available_time, received_time, "normal")
        result.update({"record_type": "metrics", "last_price": _number(_required(payload, "lastPrice"), "lastPrice"), "base_volume": _number(_required(payload, "volume"), "volume"), "quote_volume": _number(_required(payload, "quoteVolume"), "quoteVolume"), "open_interest": _number(_required(payload, "openInterest"), "openInterest"), "open_interest_unit": "contracts", "funding_rate": _number(_required(payload, "fundingRate"), "fundingRate")})
        _validate_nonnegative(result, ("base_volume", "quote_volume", "open_interest"))
        return result


class OkxAdapter(ReadOnlyAdapter):
    exchange = "okx"

    def normalize_symbol(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        raw_symbol = str(_required(payload, "instId"))
        symbol = _canonical_symbol(raw_symbol)
        event_time = _utc_from_milliseconds(_required(payload, "ts"), "ts")
        available_time = _utc_from_milliseconds(_required(payload, "availableTime"), "availableTime")
        received_time = _utc_from_milliseconds(_required(payload, "receivedTime"), "receivedTime")
        _validate_times(event_time, available_time, received_time)
        result = _envelope(self.exchange, symbol, f"{self.exchange}-{symbol}-symbol", event_time, available_time, received_time, "normal")
        result.update({"record_type": "symbol", "base_asset": _required(payload, "baseCcy"), "quote_asset": _required(payload, "quoteCcy"), "contract_status": _required(payload, "state"), "price_decimals": int(_required(payload, "tickSzDecimals")), "quantity_decimals": int(_required(payload, "lotSzDecimals"))})
        return result

    def normalize_candle(self, payload: Sequence[Any], symbol: str, record_id: str, available_time: str, received_time: str) -> dict[str, Any]:
        if len(payload) < 9:
            raise AdapterValidationError("missing_required_field", "okx_candle")
        event_time = _utc_from_milliseconds(payload[0], "timestamp")
        result = _envelope(self.exchange, _canonical_symbol(symbol), record_id, event_time, available_time, received_time, "normal")
        result.update({"record_type": "candle", "interval": "5m", "open_time": event_time, "close_time": event_time, "open": _number(payload[1], "open"), "high": _number(payload[2], "high"), "low": _number(payload[3], "low"), "close": _number(payload[4], "close"), "base_volume": _number(payload[5], "volume"), "quote_volume": _number(payload[7], "quote_volume"), "trade_count": 0, "closed": str(payload[8]) == "1"})
        _validate_candle(result)
        return result

    def normalize_metrics(self, payload: Mapping[str, Any], symbol: str, record_id: str, available_time: str, received_time: str) -> dict[str, Any]:
        event_time = _utc_from_milliseconds(_required(payload, "ts"), "ts")
        result = _envelope(self.exchange, _canonical_symbol(symbol), record_id, event_time, available_time, received_time, "normal")
        result.update({"record_type": "metrics", "last_price": _number(_required(payload, "last"), "last"), "base_volume": _number(_required(payload, "vol24h"), "vol24h"), "quote_volume": _number(_required(payload, "volCcy24h"), "volCcy24h"), "open_interest": _number(_required(payload, "oi"), "oi"), "open_interest_unit": "contracts", "funding_rate": _number(_required(payload, "fundingRate"), "fundingRate")})
        _validate_nonnegative(result, ("base_volume", "quote_volume", "open_interest"))
        return result


def _validate_nonnegative(record: Mapping[str, Any], fields: Sequence[str]) -> None:
    for field in fields:
        if record[field] < 0:
            raise AdapterValidationError("negative_value", field)


def _validate_candle(record: Mapping[str, Any]) -> None:
    if record["low"] < 0 or not (record["low"] <= min(record["open"], record["close"]) <= max(record["open"], record["close"]) <= record["high"]):
        raise AdapterValidationError("invalid_candle_range", record["record_id"])
    _validate_nonnegative(record, ("base_volume", "quote_volume", "trade_count"))
