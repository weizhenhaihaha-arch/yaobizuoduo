# 后续工作流程与授权门禁

更新日期：2026-07-24（Asia/Shanghai）

`PROJECT_STATUS.yaml` 是唯一当前机器状态源。G0-T04 generation 4 已在
terminal main `dcb942a80a91312fad12d90b5e362cbdd0611017` 完整收口；其
push/main run `30043450574` 成功。

当前唯一工作是 Package A / G0-T05 generation 3 `in_progress`。正式实现
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
