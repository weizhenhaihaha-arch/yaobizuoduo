import type { Outcome, SignalDetailDto, StatisticsDto } from "../types";
import { developmentDashboard } from "./dashboard";

const observed = (value: Outcome): Outcome => value;

export const developmentOutcomes: Outcome[] = [
  observed({
    signal_id: "binance-btc-armed", window: "5m", entry_price: 65000, last_price: 65325,
    highest_price: 65650, lowest_price: 64870, max_rise_pct: 1, max_drawdown_pct: -0.2,
    peak_time: "2026-07-20T08:05:00Z", drawdown_time: "2026-07-20T08:02:00Z",
    first_extreme_order: "drawdown_first", complete: true, missing_data: [],
    strategy_result_status: "not_evaluated", strategy_pnl_pct: null,
    strategy_result_reason: "exit_rules_fees_and_slippage_not_approved",
  }),
  observed({
    signal_id: "binance-btc-armed", window: "15m", entry_price: 65000, last_price: null,
    highest_price: null, lowest_price: null, max_rise_pct: null, max_drawdown_pct: null,
    peak_time: null, drawdown_time: null, first_extreme_order: "none", complete: false,
    missing_data: ["window_end_observation_missing"], strategy_result_status: "not_evaluated",
    strategy_pnl_pct: null, strategy_result_reason: "exit_rules_fees_and_slippage_not_approved",
  }),
];

export const developmentSignalDetail: SignalDetailDto = {
  api_version: "api.v1",
  signal: developmentDashboard.confirmed[0],
  state_events: [
    { event_id: "event-btc-watch", signal_id: "binance-btc-armed", from_state: null, to_state: "watch", event_time: "2026-07-20T07:58:00Z", available_time: "2026-07-20T07:58:01Z", reason_codes: ["activity_rising"], snapshot_id: "snapshot-btc-watch" },
    { event_id: "event-btc-potential", signal_id: "binance-btc-armed", from_state: "watch", to_state: "potential", event_time: "2026-07-20T07:59:00Z", available_time: "2026-07-20T07:59:01Z", reason_codes: ["volume_expansion"], snapshot_id: "snapshot-btc-potential" },
    { event_id: "event-btc-armed", signal_id: "binance-btc-armed", from_state: "potential", to_state: "armed", event_time: "2026-07-20T08:01:00Z", available_time: "2026-07-20T08:01:01Z", reason_codes: ["trend_confirmed"], snapshot_id: "snapshot-btc-armed" },
  ],
  outcome_summary: { outcomes: developmentOutcomes, strategy_result_status: "not_evaluated" },
};

export const developmentStatistics: StatisticsDto = {
  api_version: "api.v1",
  total_signals: 4,
  complete_price_observation_windows: 3,
  incomplete_windows: 2,
  observed_max_rise_pct: 3.4,
  observed_max_drawdown_pct: -1.7,
  strategy_result_status: "not_evaluated",
  strategy_result_reason: "exit_rules_fees_and_slippage_not_approved",
};

export const developmentHistory = [
  ...developmentDashboard.confirmed,
  ...developmentDashboard.recent_invalidations,
  ...developmentDashboard.potential,
];
