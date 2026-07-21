# 妖币暴涨做多开发工作流

## 1. 永久边界

本仓库只开发 Binance、OKX USDT 永续的做多信号雷达。V1 是
Paper-first 的观察、信号、历史和模拟评估产品；不保存交易所凭证，
不下单，不管理杠杆，不提供做空信号，不作收益保证，也不混入独立的
做空反转项目。

`PROJECT_STATUS.yaml` 是唯一可变的当前机器状态。本文定义路线和门禁，
`CURRENT_TASK.md` 保存当前任务卡，`PROJECT_MEMORY.md` 保存历史事实；三者
不得另写互相竞争的当前阶段声明。

## 2. 成熟度

- `OFFLINE_EVIDENCE_ACCEPTED`：纯函数、契约、fixtures 或离线边界通过。
- `INTEGRATION_ACCEPTED`：真实组件链路通过，尚未完成连续 Paper。
- `PAPER_VALIDATED`：冻结版本达到预注册的连续观察门槛。
- `RELEASE_READY`：发布门禁全部通过，并获得产品负责人明确批准。

机器上限是：G0-G5 不高于 offline，G6-G7 不高于 integration，G8 不高于
Paper validated。G9 只有在任务已 closed、产品负责人明确 go 且发布证据完整时
才允许 `RELEASE_READY`。

旧 M0-M7 成果只作为历史证据，最多映射为
`OFFLINE_EVIDENCE_ACCEPTED`。L0 是明确记录的 legacy-local 例外，不等于
远端 exact-HEAD CI、真实集成、Paper 验证或发布就绪。

## 3. G0-G9 门禁

### G0：治理基线与最小 CI

建立 canonical status/schema/validator、旧证据映射、单活动任务规则、
bootstrap CI 与 main required check。权限不足时必须阻塞，不得假报 CI 或
分支保护生效。

### G1：可复现工程与完整 CI

建立跨平台统一验证入口，固定 Python/Node 与依赖，覆盖后端、前端、
fixture digest、类型/格式、依赖、secret 和禁区扫描。

### G2：旧证据认证

逐任务记录旧 SHA、测试、契约、能力限制和当前 HEAD 兼容性；不得按整个
里程碑批量升级成熟度。

### G3：真实公开行情采集

冻结 Binance/OKX 的 USDT 永续 instrument catalog 和逐时成员规则；分别
验证原生公开数据、限频、重连、时钟偏差、错序、断流、新鲜度与
fail-closed。不得使用私有 API、凭证或订单能力。

### G4：历史数据集与因果安全

建立带 hash 的不可变 manifest、逐时成员快照、缺口报告和固定
train/validation/untouched holdout；禁止未来数据和幸存者偏差。

### G5：策略校准与模拟口径

先冻结评估协议、搜索空间和基线，再从数据产生参数候选。模拟需计入费用、
滑点、资金费率、延迟和成交可实现性；价格上涨与策略收益永久分离。

### G6：真实端到端 Paper 系统

连接公开行情、标准化、策略、生命周期、PostgreSQL、API/SSE 与真实前端；
验证幂等、恢复、迁移、延迟和契约一致性。fixtures 只留在测试路径。

### G7：通知与可观测性

完成站内通知、指标、脱敏日志、告警和运行手册。默认高优先提醒仅为新确认
信号与信号失效；失效只表示停止按原做多信号关注，不表示做空。

### G8：连续 Paper 验证

预注册持续时间、总样本量、两交易所各自下限、缺口和稳定性阈值；冻结策略、
配置和观察池规则，参数变化必须开启新 cohort。

### G9：Paper 观察版发布评审

完成 go/no-go、移动端/浏览器/可访问性、新手理解测试、安全与依赖检查、
权限、滥用防护、备份恢复、部署回滚、隐私留存、风险披露和发布后观察。
只有全部通过并由产品负责人明确 go 才能标记 `RELEASE_READY`。

## 4. 每张任务的固定闭环

`任务卡冻结 → 开发交付 → candidate exact-HEAD CI → 独立代码/安全审核 +
独立架构/路线审核 → ACCEPTED | RETURNED | BLOCKED → closure CI → 固定 merge
进入 main → merged-main CI → finalization 收口 → finalization D0 CI → 下一卡授权`

- 任意时刻只有一个活动任务。
- 开发 AG 只能交付 `awaiting_review`，不能自行写 accepted。
- `RETURNED` 只返修当前卡；新 candidate 必须废止旧 reviewer/CI 身份。
- `closed` 只能来自 `merged_verified`；下一卡必须等待 finalization 已进 main
  且外部 D0 required check 成功。
- candidate、closure、implementation merge、finalization 使用不可变 SHA
  串联；禁止 squash/rebase 冒充固定 merge 证据。
- 缺数据、未知状态、权限不足或证据不匹配一律 fail-closed。
- SHA 只能由后续提交记录：delivery、closure 与 finalization 提交都不保存自身
  SHA；repository-aware validator 从 exact HEAD 解析隐式 subject，并在下一阶段
  检查对象、第一父状态、generation、祖先、authoritative main 可达性和 CI
  subject/origin/run 身份。
- 唯一例外是绑定 G0-T01 与授权基线的一次性 no-CI bootstrap exception；它要求
  两条独立本地审核均通过、local evidence 成功、成熟度仅 offline、使用次数为 1，
  且不可用于 G0-T02 或任何后续任务。
- G9 go/no-go 与 release completion 必须由进入 authoritative main 的不可变
  approval/manifest JSON artifact、commit、path 和 SHA-256 证明，不接受布尔自报。

## 5. 风险等级

- D0 文档/状态：schema、链接、Markdown、冲突、secret、diff、ancestry。
- D1 纯离线代码：D0 加针对性测试、全量单元/契约、类型、构建、fixtures、依赖检查。
- D2 网络/数据库/通知/部署：D1 加集成、故障注入、恢复、性能、安全、日志脱敏和回滚演练。

风险等级只是最低测试集合，不豁免独立审核、不可变 SHA、CI 或 merged-main 验证。

## 6. 变更控制

真实下单、凭证、多用户账户、自动止盈止损、杠杆、做空、新交易所及生产发布
必须分别设计并获得用户明确授权。策略阈值、采集 SLO、G8 门槛和模拟费用参数
必须在相应门禁前冻结，不能凭直觉写入。
