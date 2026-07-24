# 后续工作流程与授权门禁

更新日期：2026-07-24（Asia/Shanghai）

`PROJECT_STATUS.yaml` 是唯一当前机器状态源。G0-T04 generation 4 已在
terminal main `dcb942a80a91312fad12d90b5e362cbdd0611017` 完整收口；其
push/main run `30043450574` 成功。

当前唯一工作是 Package A / G0-T05 generation 3 implementation。授权激活
已通过 PR #29 合并为 authoritative main `5f0ee472…`；implementation 和
delivery 必须从该 main 严格单父推进。

本切片仍只允许 manifest 中 G0-T05 的精确七路径，并保持 activation、
manifest/schema、ruleset、Package 顺序和历史字节不变。交付必须停在
`awaiting_review`，通过 exact-head CI 和独立双审后才进入 acceptance。

G1-T01 继续 `not_authorized`；能力保持 `OFFLINE_EVIDENCE_ACCEPTED`。
市场网络、凭证、交易、产品实现、工作流/规则集修改、部署、发布及本机系统
修改全部禁止。
