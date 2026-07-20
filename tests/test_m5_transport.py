import json
import unittest

from fastapi.testclient import TestClient

from api.service import InMemoryReadModel, ReadOnlyApiService
from api.transport import create_app


def armed_record(signal_id="binance-btc", exchange="binance"):
    return {"signal_id": signal_id, "exchange": exchange, "symbol": "BTCUSDT", "market_type": "usdt_perpetual", "state": "armed", "event_time": "2026-07-20T00:01:00Z", "last_confirmed_time": "2026-07-20T00:01:00Z", "freshness_status": "fresh", "data_quality": "normal", "usable_for_signal": True, "reason_codes": ("test",), "reference_entry_price": 100.0, "reference_entry_time": "2026-07-20T00:01:00Z", "invalidation_rule_id": "price_below_entry_buffer_v1", "strategy_version": "provisional-m3-v1"}


class TransportTests(unittest.TestCase):
    def setUp(self):
        model = InMemoryReadModel([armed_record()], {"binance-btc": []}, [], [])
        service = ReadOnlyApiService(model)
        events = lambda: ({"event_type": "new_signal", "signal_id": "binance-btc", "exchange": "binance", "symbol": "BTCUSDT", "occurred_at": "2026-07-20T00:01:00Z", "reason_codes": ("armed",)}, {"event_type": "stale_data", "signal_id": "binance-btc", "exchange": "binance", "symbol": "BTCUSDT", "occurred_at": "2026-07-20T00:02:00Z", "reason_codes": ("delayed",)}, {"event_type": "unsupported", "signal_id": "binance-btc", "exchange": "binance", "symbol": "BTCUSDT", "occurred_at": "2026-07-20T00:03:00Z", "reason_codes": ("ignored",)})
        self.client = TestClient(create_app(service, events))

    def test_all_get_routes(self):
        for path in ("/api/v1/dashboard", "/api/v1/signals/history", "/api/v1/statistics/summary", "/api/v1/health"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get("/api/v1/signals/binance-btc").status_code, 200)
        self.assertEqual(self.client.get("/api/v1/signals/binance-btc/outcomes").status_code, 200)

    def test_not_found_and_invalid_request_envelopes(self):
        not_found = self.client.get("/api/v1/signals/missing")
        self.assertEqual(not_found.status_code, 404)
        self.assertEqual(not_found.json()["error"]["code"], "not_found")
        outcomes_not_found = self.client.get("/api/v1/signals/missing/outcomes")
        self.assertEqual(outcomes_not_found.status_code, 404)
        self.assertEqual(outcomes_not_found.json()["error"]["code"], "not_found")
        invalid = self.client.get("/api/v1/signals/%20")
        self.assertIn(invalid.status_code, (404, 422))
        self.assertIn("error", invalid.json())

    def test_sse_framing_and_allowlist(self):
        response = self.client.get("/api/v1/events")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"].split(";")[0], "text/event-stream")
        self.assertIn("event: new_signal\n", response.text)
        self.assertIn("event: stale_data\n", response.text)
        self.assertNotIn("unsupported", response.text)
        self.assertTrue(response.text.endswith("\n\n"))
        payload = response.text.split("data: ", 1)[1].split("\n", 1)[0]
        self.assertEqual(json.loads(payload)["event_type"], "new_signal")

    def test_request_id_is_preserved_in_error_envelope(self):
        response = self.client.get("/api/v1/signals/missing", headers={"x-request-id": "offline-test-1"})
        self.assertEqual(response.json()["error"]["request_id"], "offline-test-1")

    def test_internal_error_uses_sanitized_envelope(self):
        class BrokenService(ReadOnlyApiService):
            def dashboard(self, generated_at=None):
                raise KeyError("malformed dashboard record should not be exposed")

        broken_client = TestClient(create_app(BrokenService(InMemoryReadModel([], {}, [], []))), raise_server_exceptions=False)
        response = broken_client.get("/api/v1/dashboard")
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["error"]["code"], "internal_error")
        self.assertNotIn("malformed dashboard record", response.text)


if __name__ == "__main__":
    unittest.main()
