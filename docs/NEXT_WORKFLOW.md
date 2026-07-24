# 后续工作流程与授权门禁

更新日期：2026-07-24（Asia/Shanghai）

`PROJECT_STATUS.yaml` 是唯一当前机器状态源。G0-T04 generation 4 已在
terminal main `dcb942a80a91312fad12d90b5e362cbdd0611017` 完整收口；其
push/main run `30043450574` 成功。

当前唯一工作是 Package A reactivation / G0-T05 generation 3
`authorized` 治理记录。它绑定不可变 Package A payload、manifest/schema
blobs、ruleset readback、terminal N 与历史 generations `[1,2] -> 3`，
并明确禁止复活旧 activation blob。

本切片不启动 G0-T05 implementation。授权候选必须是 N 的严格单父子节点，
只改变 manifest 中 G0-T05 的精确七路径。未来 protected-main merge 只能是
`[N, accepted-authorization]` 且 tree 等于 second parent。

G1-T01 继续 `not_authorized`；能力保持 `OFFLINE_EVIDENCE_ACCEPTED`。
市场网络、凭证、交易、产品实现、工作流/规则集修改、部署、发布及本机系统
修改全部禁止。
