"""Injected DB-API PostgreSQL read model with no write operations."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Any


class ReadModelDataError(ValueError):
    """Raised when a database row cannot satisfy the approved read contract."""


class PostgresReadModel:
    """Read-only M1-M5 model backed by an injected DB-API connection."""

    def __init__(self, connection_or_factory: Any | Callable[[], Any]) -> None:
        self._connection_or_factory = connection_or_factory
        self._connection: Any | None = None
        self._closed = False

    def signals(self) -> Iterable[Mapping[str, Any]]:
        rows = self._fetch(
            """
            SELECT signal_id, schema_version, exchange, symbol, market_type,
                   strategy_version, state, reason_codes,
                   reference_entry_price, reference_entry_time,
                   invalidation_rule_id, cooldown_group, data_snapshot_ids,
                   event_time, available_time, last_confirmed_time,
                   freshness_status, data_quality, usable_for_signal
            FROM signals
            ORDER BY state, freshness_status, exchange, symbol, signal_id
            """,
            (),
        )
        return tuple(self._signal_row(row) for row in rows)

    def signal_events(self, signal_id: str) -> Iterable[Mapping[str, Any]]:
        rows = self._fetch(
            """
            SELECT event_id, schema_version, signal_id, from_state, to_state,
                   event_time, available_time, reason_codes, snapshot_id
            FROM signal_events
            WHERE signal_id = %s
            ORDER BY event_time, available_time, event_id
            """,
            (signal_id,),
        )
        return tuple(self._event_row(row) for row in rows)

    def outcomes(self, signal_id: str | None = None) -> Iterable[Mapping[str, Any]]:
        if signal_id is None:
            query = """
                SELECT signal_id, window, strategy_version, window_start,
                       window_end, as_of_time, entry_price, last_price, highest_price,
                       lowest_price, max_rise_pct, max_drawdown_pct,
                       peak_time, drawdown_time, first_extreme_order, complete,
                       missing_data, strategy_result_status, strategy_pnl_pct,
                       strategy_result_reason
                FROM outcome_windows
                ORDER BY signal_id,
                         CASE window WHEN '5m' THEN 1 WHEN '15m' THEN 2
                                     WHEN '1h' THEN 3 WHEN '4h' THEN 4
                                     WHEN '1d' THEN 5 ELSE 6 END,
                         window_start, window
            """
            params: tuple[Any, ...] = ()
        else:
            query = """
                SELECT signal_id, window, strategy_version, window_start,
                       window_end, as_of_time, entry_price, last_price, highest_price,
                       lowest_price, max_rise_pct, max_drawdown_pct,
                       peak_time, drawdown_time, first_extreme_order, complete,
                       missing_data, strategy_result_status, strategy_pnl_pct,
                       strategy_result_reason
                FROM outcome_windows
                WHERE signal_id = %s
                ORDER BY signal_id,
                         CASE window WHEN '5m' THEN 1 WHEN '15m' THEN 2
                                     WHEN '1h' THEN 3 WHEN '4h' THEN 4
                                     WHEN '1d' THEN 5 ELSE 6 END,
                         window_start, window
            """
            params = (signal_id,)
        return tuple(self._outcome_row(row) for row in self._fetch(query, params))

    def health(self) -> Iterable[Mapping[str, Any]]:
        rows = self._fetch(
            """
            SELECT health_id, schema_version, exchange, symbol, market_type,
                   event_time, available_time, received_time, data_quality,
                   status, usable_for_signal, freshness_status,
                   last_event_time, reason_codes, missing_fields
            FROM health_snapshots
            ORDER BY exchange, symbol, event_time DESC, health_id
            """,
            (),
        )
        return tuple(self._health_row(row) for row in rows)

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._connection is not None:
            self._connection.close()

    def _fetch(self, query: str, params: tuple[Any, ...]) -> tuple[Mapping[str, Any], ...]:
        if self._closed:
            raise RuntimeError("read model is closed")
        connection = self._get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return tuple(self._row_mapping(cursor, row) for row in rows)
        finally:
            cursor.close()

    def _get_connection(self) -> Any:
        if self._connection is None:
            if callable(self._connection_or_factory):
                self._connection = self._connection_or_factory()
            else:
                self._connection = self._connection_or_factory
        return self._connection

    @staticmethod
    def _row_mapping(cursor: Any, row: Any) -> Mapping[str, Any]:
        if isinstance(row, Mapping):
            return row
        description = getattr(cursor, "description", None)
        if not description or len(description) != len(row):
            raise ReadModelDataError("database row has no valid column description")
        return {str(column[0]): value for column, value in zip(description, row)}

    @staticmethod
    def _required(row: Mapping[str, Any], *fields: str) -> None:
        missing = [field for field in fields if field not in row]
        if missing:
            raise ReadModelDataError("database row is missing required fields")

    @staticmethod
    def _tuple_value(value: Any) -> tuple[Any, ...]:
        if value is None:
            return ()
        if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
            raise ReadModelDataError("database array field is malformed")
        return tuple(value)

    @classmethod
    def _signal_row(cls, row: Mapping[str, Any]) -> Mapping[str, Any]:
        cls._required(row, "signal_id", "exchange", "symbol", "market_type", "state", "event_time", "freshness_status", "data_quality", "usable_for_signal")
        return {
            "signal_id": row["signal_id"], "schema_version": row.get("schema_version", "m1.v1"),
            "exchange": row["exchange"], "symbol": row["symbol"], "market_type": row["market_type"],
            "strategy_version": row.get("strategy_version", "unknown"), "state": row["state"],
            "reason_codes": cls._tuple_value(row.get("reason_codes", ())),
            "reference_entry_price": row.get("reference_entry_price"), "reference_entry_time": row.get("reference_entry_time"),
            "invalidation_rule_id": row.get("invalidation_rule_id", "unknown"), "cooldown_group": row.get("cooldown_group", "unknown"),
            "data_snapshot_ids": cls._tuple_value(row.get("data_snapshot_ids", ())), "event_time": row["event_time"],
            "available_time": row.get("available_time"), "last_confirmed_time": row.get("last_confirmed_time"),
            "freshness_status": row["freshness_status"], "data_quality": row["data_quality"],
            "usable_for_signal": row["usable_for_signal"],
        }

    @classmethod
    def _event_row(cls, row: Mapping[str, Any]) -> Mapping[str, Any]:
        cls._required(row, "event_id", "signal_id", "from_state", "to_state", "event_time", "available_time", "reason_codes", "snapshot_id")
        return {"event_id": row["event_id"], "schema_version": row.get("schema_version", "m1.v1"), "signal_id": row["signal_id"], "from_state": row["from_state"], "to_state": row["to_state"], "event_time": row["event_time"], "available_time": row["available_time"], "reason_codes": cls._tuple_value(row["reason_codes"]), "snapshot_id": row["snapshot_id"]}

    @classmethod
    def _outcome_row(cls, row: Mapping[str, Any]) -> Mapping[str, Any]:
        cls._required(row, "signal_id", "window", "strategy_version", "window_start", "window_end", "as_of_time", "complete", "missing_data", "strategy_result_status", "strategy_pnl_pct", "strategy_result_reason")
        if row["strategy_result_status"] != "not_evaluated" or row["strategy_pnl_pct"] is not None:
            raise ReadModelDataError("outcome strategy result is outside the approved boundary")
        cls._required(row, "entry_price")
        return {"signal_id": row["signal_id"], "window": row["window"], "strategy_version": row["strategy_version"], "window_start": row["window_start"], "window_end": row["window_end"], "as_of_time": row["as_of_time"], "entry_price": row["entry_price"], "last_price": row.get("last_price"), "highest_price": row.get("highest_price"), "lowest_price": row.get("lowest_price"), "max_rise_pct": row.get("max_rise_pct"), "max_drawdown_pct": row.get("max_drawdown_pct"), "peak_time": row.get("peak_time"), "drawdown_time": row.get("drawdown_time"), "first_extreme_order": row.get("first_extreme_order", "none"), "complete": row["complete"], "missing_data": cls._tuple_value(row["missing_data"]), "strategy_result_status": row["strategy_result_status"], "strategy_pnl_pct": row["strategy_pnl_pct"], "strategy_result_reason": row["strategy_result_reason"]}

    @classmethod
    def _health_row(cls, row: Mapping[str, Any]) -> Mapping[str, Any]:
        cls._required(row, "health_id", "exchange", "market_type", "event_time", "available_time", "received_time", "data_quality", "status", "usable_for_signal", "freshness_status", "reason_codes", "missing_fields")
        return {"health_id": row["health_id"], "schema_version": row.get("schema_version", "m1.v1"), "exchange": row["exchange"], "symbol": row.get("symbol"), "market_type": row["market_type"], "event_time": row["event_time"], "available_time": row["available_time"], "received_time": row["received_time"], "data_quality": row["data_quality"], "status": row["status"], "usable_for_signal": row["usable_for_signal"], "freshness_status": row["freshness_status"], "last_event_time": row.get("last_event_time"), "reason_codes": cls._tuple_value(row["reason_codes"]), "missing_fields": cls._tuple_value(row["missing_fields"])}
