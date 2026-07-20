import { act } from "react";
import type { ReactElement } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, describe, expect, it } from "vitest";
import App, { DashboardPage, RadarApp, ResultsPage, SignalDetailPage } from "./App";
import { developmentDashboard } from "./fixtures/dashboard";
import { developmentSignalDetail, developmentStatistics } from "./fixtures/results";

let root: Root | undefined;

function render(element: ReactElement) {
  const container = document.createElement("div");
  document.body.appendChild(container);
  root = createRoot(container);
  act(() => root?.render(element));
  return container;
}

function text(container: HTMLElement, value: string) {
  expect(container.textContent).toContain(value);
}

afterEach(() => {
  act(() => root?.unmount());
  document.body.innerHTML = "";
  root = undefined;
});

describe("beginner radar homepage", () => {
  it("renders deterministic development data in priority groups", () => {
    const container = render(<App />);
    text(container, "开发 / 测试数据");
    text(container, "现在有 1 个信号可以考虑开多");
    text(container, "已出现信号");
    text(container, "潜在信号");
    text(container, "币安");
    text(container, "欧易");
    text(container, "成交活跃度上升 · 趋势条件已确认");
    text(container, "数据不新鲜，已关闭入场建议，请等待数据恢复。");
    text(container, "最近失效");
    text(container, "价格触发失效条件");
  });

  it("keeps signal cards keyboard reachable without transport calls", () => {
    const container = render(<App />);
    const card = container.querySelector("article[aria-labelledby='binance-btc-armed-title']");
    expect(card?.getAttribute("tabindex")).toBe("0");
    expect(container.querySelector("a[href*='api']")).toBeNull();
  });

  it("explains loading, error, and empty states", () => {
    let container = render(<DashboardPage state="loading" />);
    text(container, "雷达正在扫描");
    act(() => root?.render(<DashboardPage state="error" errorMessage="开发数据暂时不可用" />));
    text(container, "开发数据暂时不可用");
    act(() => root?.render(<DashboardPage state="empty" dashboard={{ ...developmentDashboard, confirmed: [], potential: [], no_signal: [], recent_invalidations: [], empty_reason: "当前没有满足确认条件的做多信号。" }} />));
    text(container, "当前没有可考虑的信号");
    text(container, "当前没有满足确认条件的做多信号。");
  });
});

describe("detail, history, and observation statistics", () => {
  it("navigates from a homepage signal to an explainable detail view", () => {
    const container = render(<RadarApp />);
    const detailButton = Array.from(container.querySelectorAll("button")).find((button) => button.textContent?.includes("查看详情"));
    act(() => detailButton?.click());
    text(container, "先看结论");
    text(container, "为什么出现：成交活跃度上升 · 趋势条件已确认");
    text(container, "跌破参考入场保护线后，停止按此信号继续观察入场");
    text(container, "状态时间线");
    expect(container.querySelector("button[aria-current='page']")?.textContent).toBe("信号");
  });

  it("keeps complete, incomplete, and unevaluated outcomes separate", () => {
    const container = render(<SignalDetailPage detail={developmentSignalDetail} />);
    text(container, "5 分钟");
    text(container, "完整");
    text(container, "不完整：窗口结束价格缺失");
    text(container, "策略盈亏为“未评估”");
    expect(container.textContent).not.toContain("胜率");
  });

  it("renders the approved api.v1 persisted event shape using event_time", () => {
    const event = developmentSignalDetail.state_events[2];
    expect(event).toEqual({
      event_id: "event-btc-armed",
      signal_id: "binance-btc-armed",
      from_state: "potential",
      to_state: "armed",
      event_time: "2026-07-20T08:01:00Z",
      available_time: "2026-07-20T08:01:01Z",
      reason_codes: ["trend_confirmed"],
      snapshot_id: "snapshot-btc-armed",
    });
    const container = render(<SignalDetailPage detail={{ ...developmentSignalDetail, state_events: [event] }} />);
    expect(container.querySelector("time")?.getAttribute("datetime")).toBe(event.event_time);
    text(container, "可以考虑开多");
  });

  it("fails closed when the approved detail payload has no events", () => {
    const container = render(<SignalDetailPage detail={{ ...developmentSignalDetail, state_events: [] }} />);
    text(container, "状态事件缺失，无法还原信号过程。");
  });

  it("shows observation-only statistics and explicit empty history", () => {
    const container = render(<ResultsPage history={[]} statistics={developmentStatistics} />);
    text(container, "观察到的最高涨幅");
    text(container, "策略盈亏：未评估");
    text(container, "还没有历史信号记录；不会用虚构结果填充。");
  });

  it("labels history price observations, incomplete windows, and strategy status", () => {
    const container = render(<ResultsPage statistics={developmentStatistics} />);
    text(container, "价格观察：最高涨幅 +1.00% · 含不完整窗口 · 策略盈亏未评估");
    text(container, "价格观察：暂无完整窗口 · 策略盈亏未评估");
  });

  it("provides keyboard buttons for all primary views and responsive structures", () => {
    const container = render(<RadarApp initialView="results" />);
    const nav = container.querySelector("nav[aria-label='主导航']");
    expect(nav?.querySelectorAll("button")).toHaveLength(3);
    expect(container.querySelector(".stats-grid")).not.toBeNull();
    expect(container.querySelector(".history-list")).not.toBeNull();
    const helpButton = Array.from(nav?.querySelectorAll("button") ?? []).find((button) => button.textContent === "帮助");
    act(() => helpButton?.click());
    text(container, "信号消失是什么意思？");
    text(container, "它不是做空建议");
  });
});
