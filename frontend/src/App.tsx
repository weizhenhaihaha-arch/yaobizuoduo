import type { DashboardDto, PageState, Signal } from "./types";
import type { ReactNode } from "react";
import { developmentDashboard } from "./fixtures/dashboard";
import "./styles.css";

const reasonLabels: Record<string, string> = {
  volume_expansion: "成交活跃度上升",
  trend_confirmed: "趋势条件已确认",
  momentum_weakened: "动能正在减弱",
  activity_rising: "市场活跃度上升",
  confirmation_pending: "等待进一步确认",
  data_delayed: "行情数据延迟",
  no_confirmed_trigger: "尚未形成确认信号",
  price_below_invalidation: "价格触发失效条件",
};

const freshnessLabels: Record<string, string> = { fresh: "刚刚更新", recent: "近期更新", stale: "数据已过期" };
const qualityLabels: Record<string, string> = { 强: "质量：强", 中: "质量：中", 弱: "质量：弱" };

function reasonText(signal: Signal): string {
  return signal.reason_codes.map((reason) => reasonLabels[reason] ?? reason).join(" · ");
}

function timeText(value: string): string {
  return new Intl.DateTimeFormat("zh-CN", { hour: "2-digit", minute: "2-digit" }).format(new Date(value));
}

function signalAction(signal: Signal): string {
  if (signal.freshness_status === "stale" || !signal.usable_for_signal) return "暂不可判断";
  if (signal.can_consider_entry) return "可以考虑开多";
  return signal.state_label;
}

function SignalCard({ signal, invalidated = false }: { signal: Signal; invalidated?: boolean }) {
  const stale = signal.freshness_status === "stale" || !signal.usable_for_signal;
  const action = signalAction(signal);
  return (
    <article className={`signal-card ${signal.state} ${stale ? "is-stale" : ""}`} tabIndex={0} aria-labelledby={`${signal.signal_id}-title`}>
      <div className="card-heading">
        <div>
          <div className="symbol-line">
            <span className="exchange-badge">{signal.exchange_label}</span>
            <h3 id={`${signal.signal_id}-title`}>{signal.symbol.replace("USDT", " / USDT")}</h3>
          </div>
          <p className="signal-meta">{signal.market_type === "usdt_perpetual" ? "USDT 永续" : signal.market_type}</p>
        </div>
        <span className={`state-badge state-${signal.state}`}>{signal.state_label}</span>
      </div>
      <div className="action-row">
        <span className="action-label">{action}</span>
        <span className="quality-label">{qualityLabels[signal.quality] ?? `质量：${signal.quality}`}</span>
      </div>
      <p className="reason"><strong>为什么：</strong>{reasonText(signal)}</p>
      <dl className="signal-facts">
        <div><dt>数据</dt><dd className={stale ? "warning-text" : ""}>{freshnessLabels[signal.freshness_status] ?? signal.freshness_status} · {signal.data_quality}</dd></div>
        <div><dt>参考入场</dt><dd>{signal.reference_entry_price === null ? "等待确认" : signal.reference_entry_price.toLocaleString("zh-CN")}</dd></div>
        <div><dt>{invalidated ? "失效原因" : "失效条件"}</dt><dd>{signal.invalidation_rule_id === "price_below_entry_buffer_v1" ? "跌破参考入场保护线" : signal.invalidation_rule_id}</dd></div>
      </dl>
      {stale && <p className="disabled-note" role="status">数据不新鲜，已关闭入场建议，请等待数据恢复。</p>}
      <p className="card-time">最近确认 {timeText(signal.last_confirmed_time)}</p>
    </article>
  );
}

function Summary({ dashboard }: { dashboard: DashboardDto }) {
  const actionable = dashboard.confirmed.filter((item) => item.can_consider_entry).length;
  const delayed = dashboard.health.filter((item) => !item.usable_for_signal).length;
  const summary = actionable > 0 ? `现在有 ${actionable} 个信号可以考虑开多` : "当前没有可以考虑开多的信号";
  return (
    <section className="summary-panel" aria-labelledby="summary-title">
      <div className="summary-copy">
        <p className="eyebrow">当前总状态</p>
        <h2 id="summary-title">{summary}</h2>
        <p className="summary-note">{delayed > 0 ? `${delayed} 个数据源需要等待恢复，入场建议已保护性关闭。` : "数据状态正常，优先查看最上方的已确认信号。"}</p>
      </div>
      <div className="summary-stats" aria-label="信号数量">
        <span><strong>{dashboard.confirmed.length}</strong>已确认</span>
        <span><strong>{dashboard.potential.length}</strong>潜在</span>
        <span><strong>{dashboard.recent_invalidations.length}</strong>已失效</span>
      </div>
    </section>
  );
}

function Section({ title, description, signals, kind }: { title: string; description: string; signals: Signal[]; kind: "confirmed" | "potential" | "invalidated" }) {
  return (
    <section className={`signal-section section-${kind}`} aria-labelledby={`${kind}-title`}>
      <div className="section-heading"><div><p className="eyebrow">{kind === "confirmed" ? "优先查看" : kind === "potential" ? "继续观察" : "状态记录"}</p><h2 id={`${kind}-title`}>{title}</h2></div><span className="count-badge">{signals.length}</span></div>
      <p className="section-description">{description}</p>
      {signals.length > 0 ? <div className="card-grid">{signals.map((signal) => <SignalCard key={signal.signal_id} signal={signal} invalidated={kind === "invalidated"} />)}</div> : <div className="section-empty">目前没有记录，雷达会在状态变化时更新。</div>}
    </section>
  );
}

export function DashboardPage({ dashboard = developmentDashboard, state = "ready", errorMessage = "暂时无法读取雷达状态，请稍后重试。" }: { dashboard?: DashboardDto; state?: PageState; errorMessage?: string }) {
  if (state === "loading") return <PageShell><div className="state-panel" role="status" aria-live="polite"><span className="loader" aria-hidden="true" /><h2>雷达正在扫描</h2><p>正在整理最新的信号状态，请稍候。</p></div></PageShell>;
  if (state === "error") return <PageShell><div className="state-panel error-panel" role="alert"><span className="state-icon" aria-hidden="true">!</span><h2>暂时读不到雷达状态</h2><p>{errorMessage}</p></div></PageShell>;
  const isEmpty = state === "empty" || (dashboard.confirmed.length === 0 && dashboard.potential.length === 0 && dashboard.no_signal.length === 0 && dashboard.recent_invalidations.length === 0);
  return <PageShell>
    <Summary dashboard={dashboard} />
    {isEmpty ? <div className="state-panel empty-panel" role="status"><span className="state-icon" aria-hidden="true">—</span><h2>当前没有可考虑的信号</h2><p>{dashboard.empty_reason ?? "当前没有满足确认条件的做多信号，先观察数据变化即可。"}</p></div> : <>
      <Section kind="confirmed" title="已出现信号" description="这些信号已经出现，先看行动和数据新鲜度。" signals={dashboard.confirmed} />
      <Section kind="potential" title="潜在信号" description="正在接近确认条件，但现在不建议直接入场。" signals={dashboard.potential} />
      <details className="collapsed-section"><summary><span>暂无信号</span><span className="count-badge">{dashboard.no_signal.length}</span></summary><p>这些币种暂时没有确认信号；数据延迟时不会提供入场建议。</p><div className="card-grid">{dashboard.no_signal.map((signal) => <SignalCard key={signal.signal_id} signal={signal} />)}</div></details>
      <Section kind="invalidated" title="最近失效" description="信号不会静默消失；这里保留最近的失效原因。" signals={dashboard.recent_invalidations} />
    </>}
  </PageShell>;
}

function PageShell({ children }: { children: ReactNode }) {
  return <div className="app-shell"><a className="skip-link" href="#main-content">跳到主要内容</a><header className="site-header"><div className="brand"><span className="brand-mark" aria-hidden="true">↗</span><div><p className="brand-name">妖币雷达</p><p className="brand-subtitle">做多观察</p></div></div><span className="dev-badge">开发 / 测试数据</span></header><main id="main-content" className="page-content">{children}</main><footer className="site-footer">只读观察工具 · 不连接真实交易所 · 不构成投资建议</footer></div>;
}

export default function App() {
  return <DashboardPage />;
}
