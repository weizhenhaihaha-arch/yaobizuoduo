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

`closed` 只能跟随 `merged_verified`。返修启动时清空旧 candidate、reviewer 和
CI 身份；下一 candidate 使用递增 generation。未知状态、非法跳转、多活动任务
或必需证据缺失均由 validator 拒绝。

## 3. 派发与交付

任务卡必须固定：任务号、G 门禁、D 风险、基线、允许/禁止范围、验收命令和
报告格式。开发 AG 从授权基线创建任务分支，只修改 allowlist；交付时提交并
推送不可变 candidate，设置 canonical status 与任务卡为 `awaiting_review`，
更新记忆，然后停止。开发 AG 不得合并 PR、启动下一卡或自我验收。

交付报告必须包含：任务号、文件、决定、精确命令/结果、candidate SHA、
分支/upstream、PR、风险/阻塞、工作区与记忆更新。

## 4. 独立审核与 Git 证据链

主 Codex 必须检查 candidate 基线和范围，并启动彼此独立的代码/安全与
架构/路线审核。只有代码结论 `APPROVE` 且架构结论 `CLEAR` 才可继续；否则
状态为 `returned` 或 `blocked`，同一开发 AG 只修当前卡。

通过后的证据顺序为：candidate SHA、closure SHA、固定 implementation merge
SHA、merged-main CI、finalization SHA、finalization D0 required check。每一步
必须校验祖先、exact HEAD、allowlist 和 CI 身份；证据不匹配会废止接受结论。

## 5. 三分钟循环

活动会话每三分钟检查：canonical task/state、开发 AG 是否 running、是否有
工作报告或共享工作树变化、HEAD/工作区、测试/阻塞/越界证据和下一动作。
只有 `running`、新报告或真实 Git/文件变化才能证明 AG 在工作。

连续三次检查无进展时唤醒同一 AG 并要求报告已完成、正在做或阻塞原因。
心跳脚本或旧系统任务只可视为历史辅助证据，不能替代活动会话、独立审核，
也不能证明当前 macOS 环境存在后台监督器。本卡不建设或修改监督器。

## 6. 结论与记忆

审核只允许 `ACCEPTED`、`RETURNED`、`BLOCKED`。每次派发、返修、审核、合并、
收口和下一授权前都要更新 `PROJECT_STATUS.yaml` 与 `PROJECT_MEMORY.md`，并在
安全扫描后提交上传。通过测试不是验收；缺 exact-HEAD CI、远端权限或外部证据
时必须准确保留较低成熟度。
