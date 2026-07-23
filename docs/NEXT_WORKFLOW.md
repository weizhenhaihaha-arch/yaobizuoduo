# 后续工作流程与授权门禁

更新日期：2026-07-23（Asia/Shanghai）

本文只解释路线，`PROJECT_STATUS.yaml` 是唯一当前机器状态源。

## 当前唯一工作

当前只允许收口 `G0-T04` 治理异常。PR #15、#17、#19、#20、#21、#22
及其父节点、tree、CI runs 和空 reviews 作为不可改写历史保留。

PR #20 至 #22 中出现的“产品负责人已确认 Package A”“G0-T05 已授权并关闭”
等断言没有可接受的确认依据，不构成执行授权。恢复树删除该 activation assertion，
但不会改写包含它的历史 commits。

## 冻结但未授权

- Package A manifest/schema bytes、payload digest
  `815a40dc1fb47b367e1fe5707c16911862feeb929b0356aff769d0544500ca27`
  和顺序 `G0-T05 -> G1-T01` 保持冻结。
- Package A 状态为 `not_authorized`。
- `G0-T05` 为 `not_authorized`。
- `G1-T01` 及所有后续 Gate 为 `not_authorized`。
- 能力上限仍为 `OFFLINE_EVIDENCE_ACCEPTED`。

## G0-T04 恢复门禁

- 恢复实现必须直接基于 exact main
  `4f358cf42b9a8e0f741563425fc26cf532df98fb`。
- delivery 必须直接跟随 validator/tests-only implementation。
- 未来 merge 只能使用 ordered parents `[4f358cf, delivery]`，且 merge tree
  必须与 delivery 完全相同。
- live checkout 必须严格匹配 local/fetched main；历史 replay 不依赖移动 ref。
- manifest/schema blob、ruleset `19526291`、required check
  `G0 / exact-head`、零 required review 和无 bypass 均不得漂移。
- exact-head CI、独立 code/security `APPROVE` 和 architecture/route `CLEAR`
  之前，不得接受或合并恢复候选。

## 永久停止条件

任何未知路径、父节点/tree/run/review/blob/digest/order/ruleset/ledger 漂移，
或任何 G0-T05/G1、Package activation、网络、凭证、账户、订单、杠杆、做空、
真实交易、付费资源、部署、发布、ruleset 变更、产品代码或 `LOCAL-PREVIEW`
需求，都必须停止并只退回当前 G0-T04。
