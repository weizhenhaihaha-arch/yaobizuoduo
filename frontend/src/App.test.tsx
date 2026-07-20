import { act } from "react";
import type { ReactElement } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterEach, describe, expect, it } from "vitest";
import App, { DashboardPage } from "./App";
import { developmentDashboard } from "./fixtures/dashboard";

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
