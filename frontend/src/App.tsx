import { useState, type ReactNode } from "react";
import type { DashboardDto, Outcome, PageState, Signal, SignalDetailDto, StatisticsDto } from "./types";
import { developmentDashboard } from "./fixtures/dashboard";
import { developmentHistory, developmentOutcomes, developmentSignalDetail, developmentStatistics } from "./fixtures/results";
import "./styles.css";

type View = "signals" | "results" | "help" | "detail";

const reasonLabels: Record<string, string> = {
  volume_expansion: "成交活跃度上升", trend_confirmed: "趋势条件已确认",
  momentum_weakened: "动能正在减弱", activity_rising: "市场活跃度上升",
  confirmation_pending: "等待进一步确认", data_delayed: "行情数据延迟",
  no_confirmed_trigger: "尚未形成确认信号", price_below_invalidation: "价格触发失效条件",
  window_end_observation_missing: "窗口结束价格缺失",
};
const stateLabels: Record<string, string> = {
  watch: "开始观察", potential: "潜在信号", armed: "可以考虑开多", active: "信号有效",
  weakening: "信号减弱", invalidated: "信号消失", expired: "信号过期",
};
const windowLabels: Record<string, string> = { "5m": "5 分钟", "15m": "15 分钟", "1h": "1 小时", "4h": "4 小时", "1d": "1 天" };
const freshnessLabels: Record<string, string> = { fresh: "刚刚更新", recent: "近期更新", stale: "数据已过期" };
const qualityLabels: Record<string, string> = { 强: "质量：强", 中: "质量：中", 弱: "质量：弱" };

function reasonText(signal: Signal): string {
  return signal.reason_codes.map((reason) => reasonLabels[reason] ?? reason).join(" · ");
}

function timeText(value: string | null): string {
  if (!value) return "暂无";
  return new Intl.DateTimeFormat("zh-CN", { month: "numeric", day: "numeric", hour: "2-digit", minute: "2-digit" }).format(new Date(value));
}

function priceText(value: number | null): string {
  return value === null ? "暂无" : value.toLocaleString("zh-CN");
}

function percentText(value: number | null): string {
  return value === null ? "暂无" : `${value > 0 ? "+" : ""}${value.toFixed(2)}%`;
}

function signalAction(signal: Signal): string {
  if (signal.freshness_status === "stale" || !signal.usable_for_signal) return "暂不可判断";
  if (signal.can_consider_entry) return "可以考虑开多";
  return signal.state_label;
}

function SignalCard({ signal, invalidated = false, onOpenDetail }: { signal: Signal; invalidated?: boolean; onOpenDetail?: (signal: Signal) => void }) {
  const stale = signal.freshness_status === "stale" || !signal.usable_for_signal;
  return (
    <article className={`signal-card ${signal.state} ${stale ? "is-stale" : ""}`} tabIndex={0} aria-labelledby={`${signal.signal_id}-title`}>
      <div className="card-heading"><div><div className="symbol-line"><span className="exchange-badge">{signal.exchange_label}</span><h3 id={`${signal.signal_id}-title`}>{signal.symbol.replace("USDT", " / USDT")}</h3></div><p className="signal-meta">USDT 永续</p></div><span className={`state-badge state-${signal.state}`}>{signal.state_label}</span></div>
      <div className="action-row"><span className="action-label">{signalAction(signal)}</span><span className="quality-label">{qualityLabels[signal.quality] ?? `质量：${signal.quality}`}</span></div>
      <p className="reason"><strong>为什么：</strong>{reasonText(signal)}</p>
      <dl className="signal-facts">
        <div><dt>数据</dt><dd className={stale ? "warning-text" : ""}>{freshnessLabels[signal.freshness_status] ?? signal.freshness_status} · {signal.data_quality}</dd></div>
        <div><dt>参考入场</dt><dd>{signal.reference_entry_price === null ? "等待确认" : priceText(signal.reference_entry_price)}</dd></div>
        <div><dt>{invalidated ? "失效原因" : "失效条件"}</dt><dd>{signal.invalidation_rule_id === "price_below_entry_buffer_v1" ? "跌破参考入场保护线" : signal.invalidation_rule_id}</dd></div>
      </dl>
      {stale && <p className="disabled-note" role="status">数据不新鲜，已关闭入场建议，请等待数据恢复。</p>}
      <div className="card-footer"><p className="card-time">最近确认 {timeText(signal.last_confirmed_time)}</p>{onOpenDetail && <button className="text-button" type="button" onClick={() => onOpenDetail(signal)} aria-label={`查看 ${signal.exchange_label} ${signal.symbol} 信号详情`}>查看详情 →</button>}</div>
    </article>
  );
}

function Summary({ dashboard }: { dashboard: DashboardDto }) {
  const actionable = dashboard.confirmed.filter((item) => item.can_consider_entry).length;
  const delayed = dashboard.health.filter((item) => !item.usable_for_signal).length;
  return <section className="summary-panel" aria-labelledby="summary-title"><div className="summary-copy"><p className="eyebrow">当前总状态</p><h2 id="summary-title">{actionable > 0 ? `现在有 ${actionable} 个信号可以考虑开多` : "当前没有可以考虑开多的信号"}</h2><p className="summary-note">{delayed > 0 ? `${delayed} 个数据源需要等待恢复，入场建议已保护性关闭。` : "数据状态正常，优先查看最上方的已确认信号。"}</p></div><div className="summary-stats" aria-label="信号数量"><span><strong>{dashboard.confirmed.length}</strong>已确认</span><span><strong>{dashboard.potential.length}</strong>潜在</span><span><strong>{dashboard.recent_invalidations.length}</strong>已失效</span></div></section>;
}

function Section({ title, description, signals, kind, onOpenDetail }: { title: string; description: string; signals: Signal[]; kind: "confirmed" | "potential" | "invalidated"; onOpenDetail: (signal: Signal) => void }) {
  return <section className={`signal-section section-${kind}`} aria-labelledby={`${kind}-title`}><div className="section-heading"><div><p className="eyebrow">{kind === "confirmed" ? "优先查看" : kind === "potential" ? "继续观察" : "状态记录"}</p><h2 id={`${kind}-title`}>{title}</h2></div><span className="count-badge">{signals.length}</span></div><p className="section-description">{description}</p>{signals.length > 0 ? <div className="card-grid">{signals.map((signal) => <SignalCard key={signal.signal_id} signal={signal} invalidated={kind === "invalidated"} onOpenDetail={onOpenDetail} />)}</div> : <div className="section-empty">目前没有记录，雷达会在状态变化时更新。</div>}</section>;
}

export function DashboardPage({ dashboard = developmentDashboard, state = "ready", errorMessage = "暂时无法读取雷达状态，请稍后重试。", onOpenDetail = () => undefined }: { dashboard?: DashboardDto; state?: PageState; errorMessage?: string; onOpenDetail?: (signal: Signal) => void }) {
  if (state === "loading") return <div className="state-panel" role="status" aria-live="polite"><span className="loader" aria-hidden="true" /><h2>雷达正在扫描</h2><p>正在整理最新的信号状态，请稍候。</p></div>;
  if (state === "error") return <div className="state-panel error-panel" role="alert"><span className="state-icon" aria-hidden="true">!</span><h2>暂时读不到雷达状态</h2><p>{errorMessage}</p></div>;
  const isEmpty = state === "empty" || [dashboard.confirmed, dashboard.potential, dashboard.no_signal, dashboard.recent_invalidations].every((items) => items.length === 0);
  return <><Summary dashboard={dashboard} />{isEmpty ? <div className="state-panel empty-panel" role="status"><span className="state-icon" aria-hidden="true">—</span><h2>当前没有可考虑的信号</h2><p>{dashboard.empty_reason ?? "当前没有满足确认条件的做多信号，先观察数据变化即可。"}</p></div> : <><Section kind="confirmed" title="已出现信号" description="这些信号已经出现，先看行动和数据新鲜度。" signals={dashboard.confirmed} onOpenDetail={onOpenDetail} /><Section kind="potential" title="潜在信号" description="正在接近确认条件，但现在不建议直接入场。" signals={dashboard.potential} onOpenDetail={onOpenDetail} /><details className="collapsed-section"><summary><span>暂无信号</span><span className="count-badge">{dashboard.no_signal.length}</span></summary><p>这些币种暂时没有确认信号；数据延迟时不会提供入场建议。</p><div className="card-grid">{dashboard.no_signal.map((signal) => <SignalCard key={signal.signal_id} signal={signal} onOpenDetail={onOpenDetail} />)}</div></details><Section kind="invalidated" title="最近失效" description="信号不会静默消失；这里保留最近的失效原因。" signals={dashboard.recent_invalidations} onOpenDetail={onOpenDetail} /></>}</>;
}

function OutcomeTable({ outcomes }: { outcomes: Outcome[] }) {
  if (outcomes.length === 0) return <div className="section-empty" role="status">还没有可用的固定窗口观察记录。策略结果仍未评估。</div>;
  return <div className="table-scroll" tabIndex={0} aria-label="固定窗口价格观察"><table><thead><tr><th>窗口</th><th>完整性</th><th>最高涨幅</th><th>最大回撤</th><th>窗口末价格</th><th>策略结果</th></tr></thead><tbody>{outcomes.map((outcome) => <tr key={outcome.window}><th>{windowLabels[outcome.window]}</th><td>{outcome.complete ? "完整" : <span className="warning-text">不完整：{outcome.missing_data.map((item) => reasonLabels[item] ?? item).join("、")}</span>}</td><td>{percentText(outcome.max_rise_pct)}</td><td>{percentText(outcome.max_drawdown_pct)}</td><td>{priceText(outcome.last_price)}</td><td>未评估</td></tr>)}</tbody></table></div>;
}

export function SignalDetailPage({ detail = developmentSignalDetail, onBack = () => undefined }: { detail?: SignalDetailDto; onBack?: () => void }) {
  const signal = detail.signal;
  const stale = signal.freshness_status === "stale" || !signal.usable_for_signal;
  return <><button className="back-button" type="button" onClick={onBack}>← 返回信号列表</button><section className="detail-hero" aria-labelledby="detail-title"><p className="eyebrow">信号详情 · {signal.exchange_label} · USDT 永续</p><h1 id="detail-title">{signal.symbol.replace("USDT", " / USDT")}</h1><span className={`state-badge state-${signal.state}`}>{signalAction(signal)}</span><p className="detail-lead">{stale ? "数据不可用时不要按此信号考虑入场。" : signal.can_consider_entry ? "当前条件仍有效；请先理解失效条件，再自行判断风险。" : "当前不是新的入场提示，请按状态继续观察。"}</p>{signal.state === "invalidated" && <p className="invalidation-alert" role="status"><strong>停止按此信号继续埋伏。</strong> 信号消失只表示原做多条件不再成立，不代表可以做空。</p>}</section><div className="detail-layout"><section className="content-panel" aria-labelledby="decision-title"><h2 id="decision-title">先看结论</h2><p><strong>为什么出现：</strong>{reasonText(signal)}</p><dl className="detail-facts"><div><dt>参考入场价</dt><dd>{priceText(signal.reference_entry_price)}</dd></div><div><dt>参考时间</dt><dd>{timeText(signal.reference_entry_time)}</dd></div><div><dt>失效含义</dt><dd>跌破参考入场保护线后，停止按此信号继续观察入场</dd></div><div><dt>数据健康</dt><dd className={stale ? "warning-text" : ""}>{freshnessLabels[signal.freshness_status]} · {signal.data_quality}</dd></div></dl></section><section className="content-panel" aria-labelledby="timeline-title"><h2 id="timeline-title">状态时间线</h2>{detail.state_events.length ? <ol className="timeline">{detail.state_events.map((event) => <li key={event.event_id}><time dateTime={event.event_time}>{timeText(event.event_time)}</time><strong>{stateLabels[event.to_state]}</strong><span>{event.reason_codes.map((reason) => reasonLabels[reason] ?? reason).join(" · ")}</span></li>)}</ol> : <p className="section-empty">状态事件缺失，无法还原信号过程。</p>}</section></div><section className="content-panel" aria-labelledby="outcomes-title"><div className="section-heading"><div><p className="eyebrow">仅为价格观察</p><h2 id="outcomes-title">信号后的固定窗口结果</h2></div></div><p className="section-description">最高涨幅不等于实际可获得收益。退出、手续费和滑点规则尚未批准，因此策略盈亏为“未评估”。</p><OutcomeTable outcomes={detail.outcome_summary.outcomes} /></section></>;
}

export function ResultsPage({ history = developmentHistory, statistics = developmentStatistics, outcomes = developmentOutcomes, onOpenDetail = () => undefined }: { history?: Signal[]; statistics?: StatisticsDto; outcomes?: Outcome[]; onOpenDetail?: (signal: Signal) => void }) {
  return <><section className="summary-panel" aria-labelledby="results-title"><div><p className="eyebrow">观察结果</p><h1 id="results-title">历史与统计</h1><p className="summary-note">这里只描述信号出现后的价格事实，不宣称胜率或策略盈利。</p></div></section><section className="stats-grid" aria-label="观察统计"><div><span>信号样本</span><strong>{statistics.total_signals}</strong></div><div><span>完整观察窗口</span><strong>{statistics.complete_price_observation_windows}</strong></div><div><span>不完整窗口</span><strong>{statistics.incomplete_windows}</strong></div><div><span>观察到的最高涨幅</span><strong>{percentText(statistics.observed_max_rise_pct)}</strong></div></section><div className="not-evaluated" role="note"><strong>策略盈亏：未评估</strong><span>退出、手续费和滑点规则尚未批准，不能把最高涨幅当成策略收益。</span></div><section className="content-panel" aria-labelledby="history-title"><h2 id="history-title">历史信号</h2>{history.length ? <div className="history-list">{history.map((signal) => {
    const signalOutcomes = outcomes.filter((outcome) => outcome.signal_id === signal.signal_id);
    const completeRises = signalOutcomes.filter((outcome) => outcome.complete).map((outcome) => outcome.max_rise_pct).filter((value): value is number => value !== null);
    const hasIncomplete = signalOutcomes.some((outcome) => !outcome.complete);
    return <article className="history-row" key={signal.signal_id}><div><span className="exchange-badge">{signal.exchange_label}</span><strong>{signal.symbol.replace("USDT", " / USDT")}</strong><span className={`state-badge state-${signal.state}`}>{signal.state_label}</span></div><p>{timeText(signal.signal_time)} · {reasonText(signal)}</p><p className="history-observation">价格观察：{completeRises.length ? `最高涨幅 ${percentText(Math.max(...completeRises))}` : "暂无完整窗口"}{hasIncomplete ? " · 含不完整窗口" : ""} · 策略盈亏未评估</p><button className="text-button" type="button" onClick={() => onOpenDetail(signal)}>查看记录 →</button></article>;
  })}</div> : <div className="section-empty" role="status">还没有历史信号记录；不会用虚构结果填充。</div>}</section></>;
}

function HelpPage() {
  return <section className="content-panel help-page" aria-labelledby="help-title"><p className="eyebrow">阅读帮助</p><h1 id="help-title">先看行动，再看原因</h1><h2>信号消失是什么意思？</h2><p>表示原来的做多观察条件已经失效，应停止按该信号继续埋伏。它不是做空建议。</p><h2>最高涨幅是收益吗？</h2><p>不是。最高涨幅只记录价格在固定窗口内曾经到过哪里，不包含可执行退出、手续费或滑点。</p><h2>数据延迟怎么办？</h2><p>页面会关闭入场建议并明确标注过期或缺失；等待数据恢复后再判断。</p></section>;
}

function PageShell({ children, view, onNavigate }: { children: ReactNode; view: View; onNavigate: (view: View) => void }) {
  return <div className="app-shell"><a className="skip-link" href="#main-content">跳到主要内容</a><header className="site-header"><div className="header-row"><div className="brand"><span className="brand-mark" aria-hidden="true">↗</span><div><p className="brand-name">妖币雷达</p><p className="brand-subtitle">做多观察</p></div></div><span className="dev-badge">开发 / 测试数据</span></div><nav className="primary-nav" aria-label="主导航"><button type="button" aria-current={view === "signals" || view === "detail" ? "page" : undefined} onClick={() => onNavigate("signals")}>信号</button><button type="button" aria-current={view === "results" ? "page" : undefined} onClick={() => onNavigate("results")}>结果</button><button type="button" aria-current={view === "help" ? "page" : undefined} onClick={() => onNavigate("help")}>帮助</button></nav></header><main id="main-content" className="page-content" tabIndex={-1}>{children}</main><footer className="site-footer">只读观察工具 · 不连接真实交易所 · 不构成投资建议</footer></div>;
}

export function RadarApp({ initialView = "signals" }: { initialView?: View }) {
  const [view, setView] = useState<View>(initialView);
  const [selected, setSelected] = useState<Signal>(developmentSignalDetail.signal);
  const openDetail = (signal: Signal) => { setSelected(signal); setView("detail"); };
  const detail = selected.signal_id === developmentSignalDetail.signal.signal_id ? developmentSignalDetail : { ...developmentSignalDetail, signal: selected, state_events: [], outcome_summary: { outcomes: [], strategy_result_status: "not_evaluated" as const } };
  return <PageShell view={view} onNavigate={setView}>{view === "signals" ? <DashboardPage onOpenDetail={openDetail} /> : view === "results" ? <ResultsPage onOpenDetail={openDetail} /> : view === "help" ? <HelpPage /> : <SignalDetailPage detail={detail} onBack={() => setView("signals")} />}</PageShell>;
}

export default function App() { return <RadarApp />; }
