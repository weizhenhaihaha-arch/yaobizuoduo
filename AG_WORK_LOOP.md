# AG 开发审核工作循环

## 1. 权威状态与角色

`PROJECT_STATUS.yaml` 是唯一当前机器状态源，必须通过
`scripts/validate_project_status.py --repo-root .`。`CURRENT_TASK.md` 是任务卡，
`PROJECT_MEMORY.md` 是追加式历史事实，其他文档只定义稳定规则。

- 产品/验收负责人：主 Codex。
- 开发执行：一个被派发的开发 AG。
- 独立门禁：代码/安全审核与架构/路线审核。
- 任意时刻恰好一个活动任务；审核或返修期间不得派发并行任务。

## 2. 状态机

```text
planned -> authorized -> in_progress -> awaiting_review
                                     -> returned -> in_progress
                                     -> blocked
                                     -> accepted_pending_merge
accepted_pending_merge -> merged_verified -> closed
```

`closed` 只能跟随 `merged_verified`。`WATCH` 是真实的架构审核结论，但不可
合并；只有代码/安全 `APPROVE` 与架构 `CLEAR` 的组合可接受。返修启动时必须
在同一次状态转换中清空旧 implementation/candidate、全部 phase CI、reviewer
和 blocker 身份，并递增 generation。未知状态、非法跳转、多活动任务或必需
证据缺失均由 validator 拒绝。

## 3. 派发与交付

任务卡必须固定：任务号、G 门禁、D 风险、基线、允许/禁止范围、验收命令和
报告格式。开发 AG 从授权基线创建任务分支，只修改 allowlist。实现内容可先
冻结为 `implementation_sha`；交付提交把 canonical status 与任务卡设为
`awaiting_review` 并成为 PR exact delivered HEAD。因为提交不能包含自己的
SHA，交付提交内的 `candidate.commit_sha` 必须为空；后续独立审核提交才记录
这个已经存在的 delivery SHA。开发 AG 推送后停止，不得合并 PR、启动下一卡
或自我验收。

交付报告必须包含：任务号、文件、决定、精确命令/结果、candidate SHA、
分支/upstream、PR、风险/阻塞、工作区与记忆更新。

## 4. 独立审核与 Git 证据链

主 Codex 必须检查 candidate 基线和范围，并启动彼此独立的代码/安全与
架构/路线审核。只有代码结论 `APPROVE` 且架构结论 `CLEAR` 才可继续；否则
状态为 `returned` 或 `blocked`，同一开发 AG 只修当前卡。

每个阶段有独立 evidence/CI 槽，记录规则如下：

1. `awaiting_review` 的交付 HEAD 是隐式 candidate；审核提交记录 candidate SHA。
2. `accepted_pending_merge` 的审核/收口 HEAD 是隐式 closure；后续 merge/finalization
   记录已经存在的 closure SHA 及其 CI。
3. 固定 merge commit 是 merged-main subject；finalization 记录其 SHA 与 CI。
4. `merged_verified` 的 finalization HEAD 由后续 close record 记录；close record
   同时记录 finalization D0 CI。任何提交都不记录自己的 SHA。

开启 repository checks 后，validator 必须证明 Git 对象存在、阶段 status 匹配、
`baseline -> implementation -> candidate -> closure -> merge -> finalization`
祖先关系成立、merged-main 确为 merge commit，且每个 CI subject 等于对应 phase
commit。伪造、无关或跨阶段 SHA 失败。

### G0-T01 一次性 no-CI bootstrap exception

由于 G0-T01 的任务范围禁止创建 CI，它有且仅有一次例外：固定 ID
`G0-T01-NO-CI-BOOTSTRAP-20260721`，只绑定任务 `G0-T01`、授权基线
`7aadae13efd45023d19bf8a280f7680667c930fa`、成功本地验收、代码/安全
`APPROVE`、架构 `CLEAR` 和 `OFFLINE_EVIDENCE_ACCEPTED`。消费次数必须从 0
变为 1，所有 phase CI 必须保持 `not_established`。它不能复制给 G0-T02、返修
generation、其他 G 卡或更高成熟度；G0-T02 及以后恢复正常 phase CI 门禁。

## 5. 三分钟循环

活动会话每三分钟检查：canonical task/state、开发 AG 是否 running、是否有
工作报告或共享工作树变化、HEAD/工作区、测试/阻塞/越界证据和下一动作。
只有 `running`、新报告或真实 Git/文件变化才能证明 AG 在工作。

连续三次检查无进展时唤醒同一 AG 并要求报告已完成、正在做或阻塞原因。
心跳脚本或旧系统任务只可视为历史辅助证据，不能替代活动会话、独立审核，
也不能证明当前 macOS 环境存在后台监督器。本卡不建设或修改监督器。

## 6. 结论与记忆

审核只允许 `ACCEPTED`、`RETURNED`、`BLOCKED`；架构 lane 可给出非合并的
`WATCH`。每次派发、返修、审核、合并、
收口和下一授权前都要更新 `PROJECT_STATUS.yaml` 与 `PROJECT_MEMORY.md`，并在
安全扫描后提交上传。通过测试不是验收；缺 exact-HEAD CI、远端权限或外部证据
时必须准确保留较低成熟度。
