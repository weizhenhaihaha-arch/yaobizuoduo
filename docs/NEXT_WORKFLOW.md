# 后续工作流程与授权门禁

更新日期：2026-07-22（Asia/Shanghai）

本文是面向产品负责人和执行团队的路线整理，不是任务授权书。
`PROJECT_STATUS.yaml` 仍是唯一可变的当前机器状态；任何新卡都必须由产品负责人
明确授权后，才能写入状态并开始执行。

## 1. 当前结论

- G0-T03 的最小 `main` 保护已生效：ruleset `19526291` 只针对
  `refs/heads/main`，无 bypass，要求 PR、零审批数量、唯一 required check
  `G0 / exact-head`，并禁止删除与 non-fast-forward。
- 用户授权的 PR #10 已合并为 authoritative main
  `02e05d1f2d68a9a1c89fda9c8636e2263fc48053`；push run
  `29929973216` 成功，最终 code/security 为 `APPROVE`，architecture 为
  `CLEAR`。
- 产品能力仍为 `OFFLINE_EVIDENCE_ACCEPTED`。这只证明离线证据和治理链路，
  不代表真实行情、连续 Paper、部署或发布就绪。
- 当前机器状态仍把历史失败 run `29909220290` 保留为唯一 blocker，并把
  G0-T04 标记为 `not_authorized`。因此不能直接启动 G0-T04。

## 2. 推荐执行顺序

### 第一步：G0-T03 恢复后状态收口

先单独授权一张最小 D0 治理切片，目标不是改业务代码，而是让当前状态准确反映
已经发生的恢复事实：

1. 绑定 recovered main `02e05d1f...`、run `29929973216`、PR #10、最终双审和
   ruleset 真实回读。
2. 将 run `29909220290` 永久保留在历史证据中；只有 validator 明确允许且新
   main success 被精确绑定后，才可从“当前 blocker”中移除。
3. 不改 ruleset，不改成熟度，不授权 G0-T04/G1，不触碰行情、凭证、交易、
   部署、发布或 `LOCAL-PREVIEW`。
4. 按完整闭环走 exact-head CI、独立双审、用户合并决定、merged-main CI、
   finalization/D0 与记忆收口。

在这一步进入 authoritative main 且所有门禁成功前，状态保持 fail-closed。

### 第二步：定义并授权 G0-T04

仓库目前只有 `G0-T04 not_authorized`，没有冻结的 G0-T04 任务卡，所以不能猜测
其实现范围。状态收口后，应先产出一张 planning-only 任务卡，明确：

- G0 还缺少的治理交付物与完成定义；
- 精确基线、风险等级、允许/禁止路径和验收命令；
- 是否完成 G0，还是仍有后续 G0 子卡；
- 何时才允许把 `next_authorization` 指向 G1。

产品负责人审阅并明确授权后，才允许执行 G0-T04。

### 第三步：完成 G0，再进入 G1

G0-T04 必须按固定闭环合入 main，并完成 merged-main CI 和 finalization/D0。
只有 G0 的最终状态和证据都进入 authoritative main，才可另行授权 G1。

G1 的目标是可复现工程与完整 CI，包括统一验证入口、固定 Python/Node 与依赖、
后端/前端/fixtures/类型/格式/依赖/secret/禁区扫描。G1 仍不授权真实行情或交易。

### 第四步：按 G2-G9 串行推进

| Gate | 主要工作 | 最高成熟度/关键边界 |
| --- | --- | --- |
| G2 | 逐任务认证旧证据、SHA、测试与当前 HEAD 兼容性 | 仍为离线证据，不批量升级旧里程碑 |
| G3 | Binance/OKX USDT 永续公开行情采集、限频、重连、时钟与新鲜度 | 只用公开数据；无私有 API、凭证或订单 |
| G4 | 不可变历史数据 manifest、逐时成员、缺口报告、train/validation/holdout | 禁止未来数据与幸存者偏差 |
| G5 | 冻结评估协议、参数搜索和模拟口径 | 计入费用、滑点、资金费率、延迟；上涨不等于策略收益 |
| G6 | 真实端到端 Paper 系统与数据库/API/SSE/前端集成 | 最高 `INTEGRATION_ACCEPTED`；fixtures 只在测试路径 |
| G7 | 通知、指标、脱敏日志、告警和运行手册 | 不把失效提示解释为做空建议 |
| G8 | 预注册连续 Paper 观察、样本量、交易所下限和稳定性门槛 | 冻结 cohort；参数变化必须开新 cohort |
| G9 | Paper 观察版 go/no-go、浏览器/移动端/安全/恢复/隐私/发布评审 | 只有完整证据和产品负责人明确 go 才可 `RELEASE_READY` |

## 3. 每张任务的固定闭环

每一张卡都必须串行执行以下步骤：

1. 产品负责人明确授权精确任务卡。
2. 原子更新 `PROJECT_STATUS.yaml`、`CURRENT_TASK.md` 与基线身份。
3. 同一个开发 AG 只做 allowlist 内的当前切片，交付后停止。
4. 主 Codex 在精确 HEAD 复跑本地验收并更新 PR。
5. GitHub `G0 / exact-head`（或该阶段冻结的 required check）必须绑定精确 PR
   HEAD 且成功。
6. 独立 code/security 必须 `APPROVE`，独立 architecture/route 必须 `CLEAR`。
7. 任何负面结论只返修当前卡；旧 candidate、CI 和 reviewer 身份必须失效。
8. 达到门禁后请求用户明确合并决定，永不自动合并。
9. 合并后验证 ordered parents、tree、authoritative-main run 和真实远端规则/证据。
10. 完成 merged-main CI、finalization/D0、项目记忆与外部记忆收口。
11. 只有全部完成，才可请求下一卡授权。

## 4. 当前需要产品负责人做的决定

按推荐顺序，下一次明确授权应当是：

> 仅授权设计并执行 G0-T03 恢复后状态收口，不授权 G0-T04 或任何更高 Gate。

这张卡完成并进入 main 后，再决定是否授权“planning-only G0-T04 任务卡定义”。
在此之前，任何 G0-T04/G1+、真实行情、凭证、交易、部署或发布工作都保持冻结。
