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

`blocked` 保持终态，不能直接恢复为 `in_progress`。产品负责人明确选择重试时，
必须从同一张卡之前的 authoritative close 建立新 generation 的两父授权记录：
第一父是该 close，第二父是上一 generation 的精确 blocked 记录；新记录只能是
`closed -> authorized`，必须清空 blocker、证据、审核与 CI。这样保留阻塞历史，
也不新增 `blocked` 出边或改写旧分支。

## 3. 派发与交付

任务卡必须固定：任务号、G 门禁、D 风险、基线、允许/禁止范围、验收命令和
报告格式。开发 AG 从授权基线创建任务分支，只修改 allowlist。实现内容可先
冻结为 `implementation_sha`；交付提交把 canonical status 与任务卡设为
`awaiting_review` 并成为 PR exact delivered HEAD。因为提交不能包含自己的
SHA，交付提交内的 `candidate.commit_sha` 必须为空；后续独立审核提交才记录
这个已经存在的 delivery SHA。开发 AG 推送后停止，不得合并 PR、启动下一卡
或自我验收。

主 Codex 可自动合并一张已经明确授权的当前卡，但仅限冻结的 exact-HEAD CI、
独立 code/security `APPROVE`、architecture/route `CLEAR`、allowlist、父节点、
tree、ruleset 和远端回读全部通过且无漂移。该权限不授权下一卡。若产品负责人
预先确认了不可变 package manifest 的精确 digest，则 package 内下一卡仍须等
前卡完整 `closed` 后按严格顺序建立新授权；最后一张卡和任何跨 package 延伸
必须停止。

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

此外，validator 必须读取当前 HEAD 的直接第一父提交。status 有变化时，项目、
任务、G 门禁、风险、授权基线与 bootstrap identity 不可改写；声明的
`transition.from` 必须等于父状态。普通转换保持 generation，只有
`returned -> in_progress` 精确加一并原子清空证据、审核、CI 和 blockers。
bootstrap 只能 `available/0 -> consumed/1`，消费后不可回滚、消失或重新出现。

`merged_main` 必须可从 canonical `refs/heads/main` 到达，仅在任务分支制造一个
merge commit 不算主线合并。每个 active CI URL 的 GitHub owner/repository 必须
等于 canonical `origin`，URL 中的 run number 必须等于 `run_id`，subject 必须
等于对应 phase commit。

六个治理文档 identity 是强制且唯一的：`AGENTS.md`、
`DEVELOPMENT_WORKFLOW.md`、`AG_WORK_LOOP.md`、`DESIGN.md`、
`CURRENT_TASK.md`、`PROJECT_MEMORY.md`。不得删除、重复或使用 `./`、`..`、
symlink alias 绕开冲突检查。

### G0-T01 一次性 no-CI bootstrap exception

由于 G0-T01 的任务范围禁止创建 CI，它有且仅有一次例外：固定 ID
`G0-T01-NO-CI-BOOTSTRAP-20260721`，只绑定任务 `G0-T01`、授权基线
`7aadae13efd45023d19bf8a280f7680667c930fa`、成功本地验收、代码/安全
`APPROVE`、架构 `CLEAR` 和 `OFFLINE_EVIDENCE_ACCEPTED`。消费次数必须从 0
变为 1，所有 phase CI 必须保持 `not_established`。它不能复制给 G0-T02、返修
generation、其他 G 卡或更高成熟度；G0-T02 及以后恢复正常 phase CI 门禁。

G9 的产品负责人 go 与完整发布证据不能用布尔值自报。二者必须分别绑定已进入
authoritative main 的不可变 JSON artifact：commit SHA、repository-relative
path 与内容 SHA-256。审批 artifact 必须明确 `decision=go` 并绑定 release
manifest digest；manifest 必须声明完整并绑定 release SHA。

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
