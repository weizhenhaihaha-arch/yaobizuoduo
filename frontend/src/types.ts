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
