# 后续工作流程与授权门禁

更新日期：2026-07-24（Asia/Shanghai）

本文只解释路线，`PROJECT_STATUS.yaml` 是唯一当前机器状态源。

## 当前唯一工作

当前只执行 `G0-T04` generation 4 main-drift reconciliation。PR #15 至
#24、异常 receipt/seal、父节点、tree、CI runs、空 review，以及废弃的
off-main generation-4 链均作为不可改写历史保留。

旧 activation assertion 保持删除，不能复活。产品负责人重新确认 payload
`815a40dc1fb47b367e1fe5707c16911862feeb929b0356aff769d0544500ca27`；
该确认只允许 G0-T04 完整关闭后创建绑定新 close 的全新 activation。

## 冻结但未激活

- Package A manifest/schema bytes、payload digest 和顺序
  `G0-T05 -> G1-T01` 保持冻结。
- `G0-T05` 与 `G1-T01` 在 G0-T04 完整关闭前保持 `not_authorized`。
- G2、市场 API、凭证、交易、部署、发布与本机系统修改保持禁止。
- 能力上限仍为 `OFFLINE_EVIDENCE_ACCEPTED`。

## G0-T04 generation 4 门禁

- 新授权记录 ordered parents 固定为
  `[1671568fd5bb33d1e316f8cbe8e9708d7d4d5d1f,
  414fa392026c71b01378c64cbf62cb6b304b2eed]`。
- PR #24 head `db507f75f46196a03a9d87725be5946e6f05575c`、run
  `30014856791`、merge `414fa392026c71b01378c64cbf62cb6b304b2eed`
  和空 review 必须机械冻结。
- 旧 off-main `de070276… -> 45e714f…` 只作废弃历史，不得成为当前
  candidate、second parent 或 CI/review 身份。
- 新 implementation/candidate/closure 必须验证授权父序、PR #24、
  abandoned chain、历史 anomaly seals、Package blobs、activation 缺席和
  累计 allowlist。
- protected-main merge 必须以 `414fa392…` 为第一父、accepted
  generation 4 为第二父，merge tree 等于第二父。
- exact-head CI、独立 code/security `APPROVE` 和 architecture/route
  `CLEAR` 之前不得接受；merged-main 与 finalization CI 全绿后才能关闭。

## 自动续行边界

G0-T04 完整关闭并经 terminal main 回读后，才可创建绑定新 close 的全新
Package A activation；随后按冻结顺序重跑 G0-T05，再执行 G1-T01
generation 2 divergence reconciliation。G2 永不在本授权内启动。

任何未知路径、父节点/tree/run/review/blob/digest/order/ledger 漂移，或任何
市场 API、凭证、账户、订单、交易、付费资源、部署、发布、本机系统修改需求，
都必须 fail-closed。

## PR #26 过早合并恢复

PR #26 把仍为 `in_progress` 的 `c22bc286…` 过早合并为 F
`8a7b8aca2b59a5598f0e721f557c06a008f362e0`。F 的 ordered parents 固定为
`[414fa392…, c22bc286…]`，tree 固定为 `930c412…`。PR exact-head run
`30028693653` 只作为异常历史；push/main failure run `30028739788` 是当前
恢复 blocker，二者都不是 acceptance。

从 F 开始的严格单父恢复 candidate `388a75b18f37ddd970a37938dba8b955dc95e719`
已通过 exact-head run `30036514625`、独立 code/security `APPROVE` 与
architecture/route `CLEAR`。Acceptance
`9652fabb655b1d678ef7677f173c2f15d65f881d` 通过 exact-head run
`30037270342`；authoritative main
`1419f7c77ff102fd68eb9583f5ec5c3b196ae4be` 的 ordered parents 精确为
`[8a7b8aca…, 9652fabb…]`，tree 等于 second parent，并通过 push/main run
`30037311721`，因此先推进到 `merged_verified`，sole failed-main blocker
已按精确证据清除。Finalization subject
`80effc864ce6788ebf6be8485ca1273ae52de538` 随后通过 exact pull-request
run `30039415469`；当前严格单父 close record 只执行
`merged_verified -> closed`。

恢复 implementation I 已固定为
`0a752ac8f14bafb42a18922d8155944612d6d21c`；reviewed candidate 固定为
`388a75b18f37ddd970a37938dba8b955dc95e719`。Closure、merged-main 与
finalization evidence 均已建立。未来 terminal bridge 只能使用 ordered
parents `[1419f7c77ff102fd68eb9583f5ec5c3b196ae4be, exact-close-record]`
且 merge tree 等于 close-record tree；普通 closed merge 不具权威。
Package A、G0-T05、G1、G2 以及产品、联网、凭证、交易、部署和发布仍未授权。
