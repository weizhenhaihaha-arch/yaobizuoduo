# 后续工作流程与授权门禁

更新日期：2026-07-23（Asia/Shanghai）

本文是人类可读路线，不是当前状态源或执行授权。
`PROJECT_STATUS.yaml` 是唯一可变的当前机器状态。

## 已完成的治理基础

- G0-T03 恢复后状态收口已进入 authoritative main
  `1671568fd5bb33d1e316f8cbe8e9708d7d4d5d1f`。
- 历史失败 run `29909220290` 永久保留为 immutable history，但不再是当前
  blocker。
- recovered main `02e05d1f...`、planning-recovery main `c11eae1...`、PR #10
  双审、ruleset `19526291` 与远端 CI 证据均已机械绑定。
- 能力上限仍为 `OFFLINE_EVIDENCE_ACCEPTED`。

## Package A 的冻结顺序

唯一规划 artifact 是
`governance/packages/package-a.manifest.json`，schema 为
`package-a-manifest.v2`。它固定严格顺序：

1. `G0-T05`：只完成 G0 治理交接，绑定产品负责人确认的 manifest digest，
   不修改 workflow、required check、ruleset 或产品能力。
2. `G1-T01`：建立可复现、跨平台、完整后端与前端 CI 统一入口和固定
   Python/API/Node 运行时及依赖身份；`tests/test_m5_transport.py` 必须实际收集
   并通过，缺 API 依赖、未收集、跳过或失败都 fail closed。该卡不实现 G2、
   真实行情或任何交易/部署能力。

G0-T04 是 manifest 规划卡本身，不能复用为实施卡。产品负责人已于
2026-07-23 确认精确 `payload_sha256`
`815a40dc1fb47b367e1fe5707c16911862feeb929b0356aff769d0544500ca27`；
独立 activation record 已授权首卡 G0-T05。G1-T01 仍须等待 G0-T05 在
authoritative main 完整关闭后，才能按同一冻结 package 自动激活。

## 自动化边界

- 已明确授权的当前卡只有在 exact-HEAD CI、独立 code/security `APPROVE`、
  architecture/route `CLEAR`、父节点、tree、allowlist、ruleset 与远端回读全部
  无漂移时才可自动合并。
- 自动合并当前卡不授权下一卡。
- Package A 只有在产品负责人确认精确 digest 并激活后，才允许前卡完整
  `closed` 后按 manifest 严格顺序自动创建下一卡授权。
- `G1-T01` 是 Package A 最后一张卡。跨 package、G2+ 或 scope 变化必须停止并
  重新取得明确授权。

## 永久停止条件

未知字段、顺序/digest/baseline/scope 漂移、非串行卡、缺独立双审、隐式激活、
跨 package 延伸，或出现网络、凭证、账户、订单、杠杆、做空、真实交易、付费
资源、部署、发布、ruleset 变更需求时，一律 fail closed，不猜测、不降级。

G2-G9 的目标仍以 `DEVELOPMENT_WORKFLOW.md` 为准；Package A 不激活 Package
B/C/D，也不授予任何后续 Gate 的执行权。
