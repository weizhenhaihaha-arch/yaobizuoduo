# 后续工作流程与授权门禁

更新日期：2026-07-23（Asia/Shanghai）

本文只解释路线，`PROJECT_STATUS.yaml` 是唯一当前机器状态源。

## 当前唯一工作

当前只允许执行 `G0-T04` generation 4 治理恢复。PR #15 至 #23、异常
receipt/seal、父节点、tree、CI runs 和 reviews 均作为不可改写历史保留。

旧 activation assertion 保持删除，不能复活。产品负责人已在当前权威上下文中
重新确认 payload `815a40dc1fb47b367e1fe5707c16911862feeb929b0356aff769d0544500ca27`；
该确认只允许 G0-T04 完整关闭后创建绑定新 close 的全新 activation。

## 冻结但未授权

- Package A manifest/schema bytes、payload digest
  `815a40dc1fb47b367e1fe5707c16911862feeb929b0356aff769d0544500ca27`
  和顺序 `G0-T05 -> G1-T01` 保持冻结。
- Package A 状态为 `not_authorized`。
- `G0-T05` 为 `not_authorized`。
- `G1-T01` 及所有后续 Gate 为 `not_authorized`。
- 能力上限仍为 `OFFLINE_EVIDENCE_ACCEPTED`。

## G0-T04 generation 4 门禁

- 授权记录使用 ordered parents
  `[1671568fd5bb33d1e316f8cbe8e9708d7d4d5d1f,
  a88b4f9e5fa7d498aeb338ec9e8bbbe198241a87]`。
- generation 4 从该授权记录开始，blocked generation 3 历史不可移动。
- exact candidate `6541189bbdacc870de5691d07991b9103ee2c763` 已通过
  PR #23 run `30005396033`、主控复跑、code/security `APPROVE` 和
  architecture `CLEAR_FOR_SEAL`；这些结果只允许其 direct-child Stage-2
  seal `S` 固化证据。
- generation 3 的旧未来 merge 方案 `[4f358cf, S]` 仅作为异常历史保留，
  已被当前 generation 4 路线取代；不得据此集成当前候选。
- 新 implementation/candidate/closure 必须机械验证授权父顺序、blocked record、
  anomaly receipt/seal、Package blobs、activation 缺席和累计 allowlist。
- protected-main merge 必须以 `a88b4f9` 为第一父、accepted generation 4
  为第二父，merge tree 等于第二父。
- live checkout 必须严格匹配 local/fetched main；历史 replay 不依赖移动 ref。
- manifest/schema blob、ruleset `19526291`、required check
  `G0 / exact-head`、零 required review 和无 bypass 均不得漂移。
- exact-head CI、独立 code/security `APPROVE` 和 architecture/route `CLEAR`
  之前，不得接受或合并恢复候选；merged-main 与 finalization CI 全绿后才能关闭。

## 永久停止条件

任何未知路径、父节点/tree/run/review/blob/digest/order/ruleset/ledger 漂移，
或任何 G0-T05/G1、Package activation、网络、凭证、账户、订单、杠杆、做空、
真实交易、付费资源、部署、发布、ruleset 变更、产品代码或 `LOCAL-PREVIEW`
需求，都必须停止并只退回当前 G0-T04。
