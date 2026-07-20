import json
import unittest
from pathlib import Path

from evaluation.replay import HistoricalReplay


ROOT = Path(__file__).parents[1]


class ReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = json.loads((ROOT / "fixtures" / "m4" / "replay_cases.json").read_text(encoding="utf-8"))["cases"]

    def outcomes_for(self, case):
        result = HistoricalReplay().run(case["snapshots"])
        self.assertTrue(any(event.to_state == "armed" for event in result.lifecycle_events))
        return result, {outcome.window: outcome for outcome in result.outcomes}

    def test_complete_adverse_first_records_both_extremes(self):
        case = self.cases[0]
        result, outcomes = self.outcomes_for(case)
        five = outcomes["5m"]
        self.assertTrue(five.complete)
        self.assertEqual(five.first_extreme_order, "drawdown_first")
        self.assertEqual(five.max_rise_pct, 5.0)
        self.assertEqual(five.max_drawdown_pct, -2.0)
        self.assertEqual(five.strategy_result_status, "not_evaluated")
        self.assertIsNone(five.strategy_pnl_pct)

    def test_late_data_cannot_leak_into_earlier_window(self):
        _, outcomes = self.outcomes_for(self.cases[1])
        five = outcomes["5m"]
        self.assertFalse(five.complete)
        self.assertIn("availability_after_window", five.missing_data)
        self.assertEqual(five.highest_price, 100.0)

    def test_missing_window_is_incomplete_and_not_strategy_pnl(self):
        _, outcomes = self.outcomes_for(self.cases[2])
        five = outcomes["5m"]
        self.assertFalse(five.complete)
        self.assertIn("window_end_observation_missing", five.missing_data)
        self.assertIsNone(five.strategy_pnl_pct)

    def test_replay_is_deterministic(self):
        case = self.cases[0]
        first = HistoricalReplay().run(case["snapshots"])
        second = HistoricalReplay().run(list(reversed(case["snapshots"])))
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
