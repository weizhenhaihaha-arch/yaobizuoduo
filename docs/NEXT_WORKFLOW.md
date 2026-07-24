# 后续工作流程与授权门禁

更新日期：2026-07-24（Asia/Shanghai）

`PROJECT_STATUS.yaml` 是唯一当前机器状态源。G0-T04 generation 4 已在
terminal main `dcb942a80a91312fad12d90b5e362cbdd0611017` 完整收口；其
push/main run `30043450574` 成功。

当前唯一工作是 Package A / G0-T05 generation 3 `closed` terminal
收口。正式实现
从 exact implementation main
`d3a617ab3081e03276a96142ae2b76349e7b2ef9` 启动；该 main 的 ordered
parents 为 `[f56c5969051694b35bb77289fbf4868b5e723bef,
ea91b842cc36b77acc77f83b7f189349e8e9ca4a]`，tree 为
`e08eb6de1c07415316e3ab0895fd58f9c178b322`。

实现/交付必须保持从 exact implementation main 开始的严格单父链，累计
变更不得超出 manifest 中 G0-T05 的精确七路径。Package A payload、
manifest/schema blobs、ruleset readback、terminal N、generation 选择与现有
activation receipt 均保持冻结。

G1-T01 在 G0-T05 完整 closed 前继续 `not_authorized`；能力保持
`OFFLINE_EVIDENCE_ACCEPTED`。
市场网络、凭证、交易、产品实现、工作流/规则集修改、部署、发布及本机系统
修改全部禁止。

Exact implementation `5862c7b4b7c9080ba20ed40e0a81f157d72a7cc5` 已完成
本地验收：canonical validator、60 个聚焦测试、551 个非 transport Python
测试、10 个 frontend 测试、frontend production build、compileall、diff
与 secret 检查均通过。Exact delivery HEAD
`a29c5f35bbbaada717c69c9d9b4749a07db2c464` 的 CI `30087724361`
成功，最终独立 code/security `APPROVE` 与
architecture/route/time-causality `CLEAR` 均已绑定该候选。Acceptance
`3f30ac7f…` 的 exact-head CI `30087824072` 成功；protected-main merge
`c7ed7691…` 保持 ordered parents `[d3a617…, 3f30ac7…]`，其 main CI
`30087883412` 成功。Finalization `27ff7803…` 的 exact-head CI
`30087966580` 成功；当前提交为其 strict-child close record。下一步只允许
terminal merge `[c7ed7691…, exact close record]` 与 authoritative-main CI；
该终态全绿前不得激活 G1-T01。
