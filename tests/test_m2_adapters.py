import json
import unittest
from pathlib import Path

from adapters.read_only_market import AdapterValidationError, BinanceAdapter, ConnectionHealth, OkxAdapter


ROOT = Path(__file__).parents[1]


class AdapterNormalizationTests(unittest.TestCase):
    def test_binance_symbol_candle_and_metrics(self):
        adapter = BinanceAdapter()
        symbol = adapter.normalize_symbol({"symbol": "BTCUSDT", "baseAsset": "BTC", "quoteAsset": "USDT", "status": "trading", "pricePrecision": 2, "quantityPrecision": 3, "onboardDate": 1784505600000, "availableTime": 1784505601000, "receivedTime": 1784505601000})
        candle = adapter.normalize_candle([1784505899000, "65000", "65120", "64980", "65100", "120.5", 1784505899000, "7830000", 2400], "BTCUSDT", "b-candle", "2026-07-20T00:05:01Z", "2026-07-20T00:05:01Z")
        metrics = adapter.normalize_metrics({"time": 1784505900000, "lastPrice": "65100", "volume": "120.5", "quoteVolume": "7830000", "openInterest": "125000", "fundingRate": "0.0001"}, "BTCUSDT", "b-metrics", "2026-07-20T00:05:01Z", "2026-07-20T00:05:01Z")
        self.assertEqual(symbol["symbol"], "BTCUSDT")
        self.assertEqual(candle["schema_version"], "m1.v1")
        self.assertEqual(metrics["open_interest_unit"], "contracts")

    def test_okx_mapping_and_symbol_normalization(self):
        adapter = OkxAdapter()
        symbol = adapter.normalize_symbol({"instId": "BTC-USDT-SWAP", "baseCcy": "BTC", "quoteCcy": "USDT", "state": "live", "tickSzDecimals": 2, "lotSzDecimals": 3, "ts": 1784505600000, "availableTime": 1784505601000, "receivedTime": 1784505601000})
        candle = adapter.normalize_candle([1784505899000, "65010", "65130", "64990", "65110", "118", "", "7670000", "1"], "BTC-USDT-SWAP", "o-candle", "2026-07-20T00:05:01Z", "2026-07-20T00:05:01Z")
        metrics = adapter.normalize_metrics({"ts": 1784505900000, "last": "65110", "vol24h": "118", "volCcy24h": "7670000", "oi": "124500", "fundingRate": "0.0001"}, "BTC-USDT-SWAP", "o-metrics", "2026-07-20T00:05:01Z", "2026-07-20T00:05:01Z")
        self.assertEqual(symbol["symbol"], "BTCUSDT")
        self.assertTrue(candle["closed"])
        self.assertEqual(metrics["exchange"], "okx")

    def test_invalid_payloads_fail_closed(self):
        with self.assertRaisesRegex(AdapterValidationError, "invalid_candle_range"):
            BinanceAdapter().normalize_candle([1784505899000, "65000", "64900", "64980", "65050", "10", 1784505899000, "650000", 100], "BTCUSDT", "bad", "2026-07-20T00:05:01Z", "2026-07-20T00:05:01Z")
        with self.assertRaisesRegex(AdapterValidationError, "missing_required_field"):
            OkxAdapter().normalize_metrics({"ts": 1784505900000, "last": "65110"}, "BTC-USDT-SWAP", "missing", "2026-07-20T00:05:01Z", "2026-07-20T00:05:01Z")


class HealthTests(unittest.TestCase):
    def test_health_is_fail_closed_for_delay_missing_and_disconnect(self):
        adapter = BinanceAdapter()
        self.assertTrue(adapter.health("2026-07-20T00:00:00Z", "2026-07-20T00:00:00.500Z", "2026-07-20T00:00:00.500Z")["usable_for_signal"])
        self.assertFalse(adapter.health("2026-07-20T00:00:00Z", "2026-07-20T00:00:03Z", "2026-07-20T00:00:03Z")["usable_for_signal"])
        self.assertFalse(adapter.health("2026-07-20T00:00:00Z", "2026-07-20T00:00:00.500Z", "2026-07-20T00:00:00.500Z", missing_fields=["open_interest"])["usable_for_signal"])
        self.assertFalse(adapter.health("2026-07-20T00:00:00Z", "2026-07-20T00:00:00.500Z", "2026-07-20T00:00:00.500Z", connected=False)["usable_for_signal"])

    def test_out_of_order_is_replay_usable(self):
        health = OkxAdapter().health("2026-07-20T00:00:00Z", "2026-07-20T00:00:00.500Z", "2026-07-20T00:00:00.500Z", out_of_order=True)
        self.assertEqual(health["data_quality"], "out_of_order")
        self.assertTrue(health["usable_for_signal"])

    def test_reconnect_state(self):
        health = ConnectionHealth()
        self.assertFalse(health.usable())
        health.connected()
        self.assertTrue(health.usable())
        health.error("transport_error")
        self.assertFalse(health.usable())
        self.assertEqual(health.snapshot()["consecutive_errors"], 1)
        health.reconnecting()
        self.assertFalse(health.usable())
        health.connected()
        self.assertEqual(health.snapshot()["consecutive_errors"], 0)


class FixtureBoundaryTests(unittest.TestCase):
    def test_existing_m1_fixtures_are_local_and_exchange_scoped(self):
        for name, exchange in (("binance_cases.json", "binance"), ("okx_cases.json", "okx")):
            payload = json.loads((ROOT / "fixtures" / "m1" / name).read_text(encoding="utf-8"))
            self.assertEqual(payload["schema_version"], "m1.v1")
            self.assertEqual(payload["exchange"], exchange)
            self.assertEqual(len(payload["cases"]), 5)


if __name__ == "__main__":
    unittest.main()
