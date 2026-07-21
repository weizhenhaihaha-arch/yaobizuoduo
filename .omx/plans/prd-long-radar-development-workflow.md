# 做多妖币雷达开发治理 PRD（待产品负责人确认）

## 0. 授权边界

本文只定义开发与验收流程。确认本文不等于授权修改正式仓库文档、审核当前任务、接入交易所、启动自动监督或派发开发卡。

V1 永久边界：Binance、OKX USDT 永续；只做多信号；Paper-first；无订单 API、无交易所凭证、无杠杆、无做空、无收益保证。任一任务触及这些永久否决项，立即 `BLOCKED`。

## 1. 核心原则

1. 一个产品、一个正式信号事实源、一个活动任务。
2. 开发完成只叫“交付”，独立验收后才叫“接受”。
3. 任务通过不等于里程碑完成；成熟度必须显式分级。
4. 任何能力声明必须绑定不可变 SHA、CI run 和可复现证据。
5. 缺数据、数据延迟、未知状态和外部权限缺失一律 fail-closed，不降低门禁。
6. 普通用户界面只回答“有没有正式做多信号、为什么、是否仍有效、什么时候停止关注”；专业指标和工程状态不得抢占主流程。
7. 只有一个产品，不建立“新手版/专业版”两套事实源；复杂信息使用同一页面内的渐进披露，默认折叠。

## 1.1 普通用户产品合同

### 默认首页只显示

- 总结论：`做多信号已出现` / `暂时没有做多信号` / `数据延迟，暂不判断`。
- 已确认做多信号：交易所、币种、当前动作、白话原因、参考区域、失效条件、更新时间。
- 最近信号变化：减弱或失效必须可见，不能静默消失。
- 正在观察和无信号市场只显示数量与最近扫描时间，详细列表默认折叠。

### 默认隐藏

- OI、资金费率、多空比、MA/EMA、原始 K 线字段。
- 策略版本、阈值、reason code、状态枚举、event/availability time、fixture、DTO、SSE 等工程术语。
- 完整回放窗口表、最大回撤、滑点/手续费模型和实验参数。

这些信息只允许出现在同一产品内的 `了解更多` / `专业数据` 折叠区，不得创建第二套专家产品或第二套信号结论。

### 卡片信息预算

普通信号卡首屏最多包含六类信息：币种与交易所、当前结论、一句话原因、参考区域、失效条件、更新时间。质量分数、复杂指标、完整时间线和统计表不进入卡片首层。

### 普通人文案翻译

- `armed` → `做多信号已出现`
- `active` → `信号仍然有效`
- `potential` → `正在观察，还不能考虑入场`
- `weakening` → `信号正在减弱`
- `invalidated` → `信号已失效，停止按此信号关注`
- `stale` → `数据有延迟，暂时不要按此页面判断`
- `not_evaluated` → `还没有足够规则计算模拟结果`

用户界面不得直接显示内部英文状态或 reason code。

## 2. 能力成熟度

- `OFFLINE_EVIDENCE_ACCEPTED`：纯函数、契约、fixtures 或离线边界通过。
- `INTEGRATION_ACCEPTED`：真实组件链路通过，但尚未完成连续 Paper。
- `PAPER_VALIDATED`：冻结版本达到预注册的连续观察门槛。
- `RELEASE_READY`：发布评审全部通过并由产品负责人批准。

旧 M0-M7 证据全部保留原任务号、文件、测试和 Git 历史，最多映射为 `OFFLINE_EVIDENCE_ACCEPTED`，不得批量升级。

## 3. 一次性迁移收口 L0

在任何 G0 工作前，先冻结 `M7-T02`：

1. 不夹带治理文档或下一任务。
2. 在干净 checkout 中审核 `93720f8` 相对基线 `f307c81`，运行原验收集和三个对抗性 probe。
3. 证明 `93720f8..101e593` 未改变 M7 实现、测试和合同，并在 `101e593` 运行完整回归。
4. 通过只记录 `ACCEPTED_UNDER_LEGACY_LOCAL_REVIEW` 与 `OFFLINE_EVIDENCE_ACCEPTED`；明确无远端 exact-HEAD CI、无 live 通知、无真实监控、无 Paper 验证。
5. 失败只 `RETURNED` 当前任务；不得启动 G0。
6. L0 收口后才允许把 G0 设为唯一活动卡。

## 4. 唯一状态源

G0 建立机器可校验的 `PROJECT_STATUS.yaml`，至少记录：当前 G 门禁、唯一活动任务、任务状态、风险等级、candidate/closure/implementation-merge/finalization SHA、能力等级、reviewer verdict、CI run/link/status、阻塞项和 next authorization。

合法状态链：

`planned → authorized → in_progress → awaiting_review → returned | blocked | accepted_pending_merge → merged_verified → closed`

约束：

- `closed` 只能来自 `merged_verified`。
- 只有 `closed` 且 finalization 已进入 main、D0 required check 成功，才能产生下一张卡授权。
- `RETURNED` 后的新 candidate 自动废止旧 CI 与 reviewer verdict。
- `PROJECT_MEMORY.md` 只记录历史事实；`CURRENT_TASK.md` 只保存任务卡；其他文档不得保存易漂移的“当前阶段”。
- schema/validator 拒绝未知状态、非法跳转、多个活动任务、缺失 SHA/CI/reviewer 和冲突文档。

## 5. Git 与验收证据链

每张实现卡使用任务分支和 PR，禁止直接向 `main` 推送，禁止 squash/rebase 合并。

1. `candidate_sha`：开发交付的不可变提交，状态为 `awaiting_review`。PR CI 必须 checkout 并核对 `pull_request.head.sha`，不得使用 synthetic merge ref 冒充 exact HEAD。
2. `closure_sha`：独立审核通过后的收口提交，状态为 `accepted_pending_merge`。candidate 必须是其祖先；candidate 之后只允许审核结论、status、memory、任务归档 allowlist。
3. `implementation_merge_sha`：固定 merge commit 进入 main，运行完整 merged-main CI；closure 必须是其祖先。
4. `finalization_sha`：仅修改 status/memory/task archive，记录 implementation merge SHA 与其 CI run/link，落盘 `merged_verified → closed`。
5. finalization 经 PR 固定 merge 入 main 并运行 D0 required checks。下一任务以 finalization 已在 main 且外部 D0 check 成功为前置；不再提交自身 CI run ID，避免递归。

任一非 allowlist 差异、祖先关系失败或 CI/SHA 不匹配，原接受结论自动失效。

## 6. 风险分级

- D0 文档/状态：schema、链接、Markdown、冲突、secret、diff、ancestry 检查。
- D1 纯离线代码：D0 + 针对性测试、全量单元/契约、类型、构建、fixtures、依赖检查。
- D2 网络/数据库/通知提供商/部署：D1 + 集成、故障注入、恢复、性能、安全、日志脱敏、回滚演练。

D0-D2 是最低测试集合，不是审核豁免；所有等级仍需独立审核、不可变 SHA、CI 和 merged-main 验证。

## 7. G0-G9 产品开发门禁

### G0 治理基线与最小 CI

- 建立 canonical status schema/validator、旧 M→新 G 映射、单活动任务规则。
- 建立最小 bootstrap CI，验证状态、文档、secret、diff、SHA/祖先关系。
- 设置 main required check 与 branch protection。
- macOS 默认由活动 Codex 会话监督；不得声称旧 Windows Scheduled Task 正在运行。

退出：状态冲突为零；bootstrap CI 和分支保护真实生效。权限不足则 `BLOCKED`。

### G1 可复现工程与完整 CI

- 建立跨平台统一验证入口。
- 固定 Python/Node 版本和可复现依赖。
- CI 覆盖后端、前端测试/构建、fixture digest、类型/格式、依赖漏洞、secret 和禁区扫描。

退出：candidate、closure、implementation merge、finalization 对应的测试集合均可按风险等级机械执行。

### G2 旧证据认证

- 逐任务映射旧 SHA、测试、合同、能力限制及当前 HEAD 兼容性。
- 不重做有效成果，不用“整个里程碑完成”批量认证。

退出：每项旧证据都有明确成熟度，没有 live/integrated/validated/release-ready 误报。

### G3 真实公开行情采集

入口前冻结数据采集宇宙与逐时 instrument catalog：全量 USDT 永续或可复现过滤集合；新上市、下架、改名、迁移、缺失处理均有规则。

- Binance、OKX 分别提供原生证据。
- 原始事件与标准化事件可追溯。
- 覆盖限频、重连、时钟偏差、错序、延迟、断流、数据新鲜度和 fail-closed。
- 无私有 API、凭证和订单能力。

退出：达到预先批准的采集时长、数据缺口、可用率和恢复目标；任一交易所失败不能由另一家替代通过。

### G4 历史数据集与因果安全

- 生成带 hash 的不可变 manifest、逐时观察池/合约成员快照和缺口报告。
- 处理新上市、下架、幸存者偏差、未来数据、重复样本和数据许可/留存。
- 预先划分 train、validation 与密封 untouched holdout。

退出：固定数据版本可复现；当时不可用的数据不能影响回放；holdout 首次解封进入 experiment ledger。

### G5 策略校准与模拟口径

- 先冻结评估协议、参数搜索空间和基线，再调参。
- 数据证据产出候选/确认/入场/弱化/失效/退出/冷却/重触发参数，产品负责人只批准版本，不凭直觉定参数。
- 纳入手续费、滑点、资金费率、执行延迟、成交可实现性、置信区间和分交易所/市场环境报告。
- 价格后来上涨与策略盈利永久分离。

退出：策略版本、数据版本、实验 ledger、参数、样本量、缺失率和样本外结果可复现；holdout 不被重复调参污染。

### G6 真实端到端 Paper 系统

- 连接公开行情 → 标准化 → 策略 → 生命周期 → PostgreSQL → API/SSE → 真实前端。
- fixtures 只留在测试路径，不冒充运行结果。
- 验证重启、幂等、状态恢复、数据库迁移/恢复、延迟和前后端契约一致性。
- 落实默认简单视图：首页只突出正式信号；潜在/无信号列表和专业数据默认折叠；内部状态全部转换为普通中文。

退出：两个交易所真实公开数据稳定进入新手页面，每个状态能追溯到原始事件、数据版本和策略版本，全程不产生订单；普通用户不展开专业信息也能完成主任务。

### G7 通知与可观测性

- 先完成站内通知、指标、脱敏日志、故障告警和运行手册。
- 验证重复抑制、重启恢复、失败重试和告警闭环。
- Telegram 是独立可选门禁；不选不阻塞首个站内 Paper 观察版。
- 默认只把“新确认信号”和“信号失效”作为用户高优先提醒；减弱提醒先留在站内，避免普通用户被频繁状态变化打扰。

退出：网页、事件、通知和健康状态来自同一事实源；失效通知只表示停止按原做多信号埋伏，不表达做空。

### G8 连续 Paper 验证

- 开始前预注册持续时间、总样本量、Binance/OKX 各自下限、缺口与稳定性失败阈值。
- 策略、配置和观察池规则冻结；任何参数改变都关闭原 cohort 并开启新版本。
- 记录漏信号、误信号、延迟、断流、重复通知、最大不利波动和模拟结果。

退出：达到预先批准的时间、样本和稳定性门槛，两个交易所分别满足，无未关闭高风险问题。

### G9 Paper 观察版发布评审

- 完成 go/no-go、移动端/浏览器/可访问性、新手 5 秒理解测试、数据异常和空状态验收。
- 完成轻量 threat model、依赖扫描、最小权限、CORS/输入限制/API 滥用保护、备份恢复、部署回滚、隐私/留存/风险披露和发布后观察窗口。
- 发布 SHA、制品、配置和回滚版本可追溯。
- 用不了解 OI、资金费率、策略回放的普通用户完成理解测试：在不展开专业信息时，能判断现在是否有信号、为什么出现、是否仍有效、何时停止关注。
- 检查首页首屏无专业指标表、无内部状态码、无工程术语、无收益暗示，复杂内容均默认折叠且不影响主任务。

退出：仅当所有门禁通过且产品负责人明确 go，能力等级才可为 `RELEASE_READY`。

## 8. 每张任务固定闭环

`任务卡冻结 → 开发交付 → candidate exact-HEAD CI → 干净环境独立审核/对抗测试 → ACCEPTED | RETURNED | BLOCKED → closure CI → implementation merge → merged-main CI → finalization 收口 → finalization D0 CI → 下一卡授权`

- `RETURNED` 只返修当前卡。
- `BLOCKED` 保留准确原因，不降标绕过。
- reviewer 不使用开发 AG 的可写工作区。
- 开发 AG 不能自行写“已验收”。

## 9. 待产品负责人确认

现在确认：

- 是否采用本文流程。
- macOS 默认人工监督，是否暂不建设无人值守 supervisor。
- Telegram 是否排除在首个观察版之外。
- 是否接受 G0-G9 新编号并保留旧 M0-M7 为历史证据。

到对应门禁前再确认：采集宇宙规则、G3 SLO、G8 时间/样本门槛、数据留存、模拟费用/滑点/延迟假设、可用性测试人数和通过比例。

产品经理建议的首轮可用性门槛：至少 5 名不了解专业指标的目标用户；80% 以上能在 5 秒内正确回答“现在是否有正式做多信号”，并能在 30 秒内找到原因和失效条件。该数值须由产品负责人在 G6 前确认。

由数据产生后再批准：最终量价/OI、入场区间、失效、退出、冷却、重触发和排名参数。

## ADR

- Decision：采用 G0-G9 证据门禁和四阶段 Git/CI 证据链。
- Drivers：消除成熟度误报；保证只做多 Paper 产品的安全性；让每项能力可复现、可追踪。
- Alternatives：保留 M0-M8 加子门禁；只修状态文本。前者持续携带旧语义，后者无法解决 CI、自动化和能力误报。
- Consequences：每张卡增加审核和 CI 时间，但可按 D0-D2 控制测试成本；发布日期由真实证据决定。
- Follow-ups：用户确认后才创建正式治理卡；无确认不执行。
