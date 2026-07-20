export type SignalState =
  | "watch"
  | "potential"
  | "armed"
  | "active"
  | "weakening"
  | "invalidated"
  | "expired";

export type Signal = {
  signal_id: string;
  exchange: "binance" | "okx";
  exchange_label: string;
  symbol: string;
  market_type: string;
  state: SignalState;
  state_label: string;
  group: "confirmed" | "potential" | "no_signal";
  can_consider_entry: boolean;
  quality: string;
  signal_time: string;
  last_confirmed_time: string;
  freshness_status: string;
  data_quality: string;
  usable_for_signal: boolean;
  reason_codes: string[];
  reference_entry_price: number | null;
  reference_entry_time: string | null;
  invalidation_rule_id: string;
  strategy_version: string;
};

export type DataHealth = {
  exchange: "binance" | "okx";
  exchange_label: string;
  symbol: string | null;
  status: string;
  usable_for_signal: boolean;
  freshness_status: string;
  last_event_time: string | null;
  reason_codes: string[];
};

export type DashboardDto = {
  api_version: "api.v1";
  generated_at: string;
  confirmed: Signal[];
  potential: Signal[];
  no_signal: Signal[];
  recent_invalidations: Signal[];
  health: DataHealth[];
  empty_reason: string | null;
};

export type PageState = "ready" | "loading" | "empty" | "error";

export type StateEvent = {
  event_id: string;
  signal_id: string;
  from_state: SignalState | null;
  to_state: SignalState;
  event_time: string;
  available_time: string;
  reason_codes: string[];
  snapshot_id: string;
};

export type Outcome = {
  signal_id: string;
  window: "5m" | "15m" | "1h" | "4h" | "1d";
  entry_price: number;
  last_price: number | null;
  highest_price: number | null;
  lowest_price: number | null;
  max_rise_pct: number | null;
  max_drawdown_pct: number | null;
  peak_time: string | null;
  drawdown_time: string | null;
  first_extreme_order: string;
  complete: boolean;
  missing_data: string[];
  strategy_result_status: "not_evaluated";
  strategy_pnl_pct: null;
  strategy_result_reason: string;
};

export type SignalDetailDto = {
  api_version: "api.v1";
  signal: Signal;
  state_events: StateEvent[];
  outcome_summary: {
    outcomes: Outcome[];
    strategy_result_status: "not_evaluated";
  };
};

export type StatisticsDto = {
  api_version: "api.v1";
  total_signals: number;
  complete_price_observation_windows: number;
  incomplete_windows: number;
  observed_max_rise_pct: number | null;
  observed_max_drawdown_pct: number | null;
  strategy_result_status: "not_evaluated";
  strategy_result_reason: string;
};
