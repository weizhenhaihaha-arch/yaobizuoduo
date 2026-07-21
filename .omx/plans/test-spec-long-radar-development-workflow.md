# 做多妖币雷达开发治理验收规格（待确认）

## 流程验收

1. 任意时刻最多一个活动任务。
2. 非法状态跳转、未知状态、缺 SHA/CI/reviewer 必须被 validator 拒绝。
3. `candidate_sha` 是 `closure_sha` 祖先；candidate 后差异只允许固定收口 allowlist。
4. `closure_sha` 是 `implementation_merge_sha` 祖先，合并不得 squash/rebase。
5. finalization 只能记录已通过完整 merged-main CI 的 implementation merge。
6. finalization 未进入 main 或 D0 required check 未通过时，不得授权下一卡。
7. RETURNED 的新 candidate 必须废止旧 verdict 和 CI 身份。
8. PR candidate check 必须验证 `pull_request.head.sha`。

## 范围验收

1. 只允许 Binance、OKX USDT 永续做多信号。
2. 发现订单 API、凭证、杠杆、做空或收益保证立即失败。
3. 旧 M0-M7 最多映射为 `OFFLINE_EVIDENCE_ACCEPTED`。
4. fixtures 不得出现在真实运行路径。

## 普通用户体验验收

1. 首页不展开任何详情时，只需阅读总结和信号卡即可判断是否存在正式做多信号。
2. 正式信号卡首层最多显示六类信息：币种/交易所、结论、原因、参考区域、失效条件、更新时间。
3. 潜在和无信号项目不占据首页主要视觉区域，详细列表默认折叠。
4. OI、资金费率、MA/EMA、reason code、状态枚举、策略版本、回放参数、DTO/SSE 等不得出现在普通用户默认层。
5. 内部状态必须翻译为普通中文；数据延迟必须直接关闭行动建议并解释原因。
6. 信号失效不能静默删除，必须明确告诉用户停止按原信号关注，同时说明这不是做空信号。
7. 历史页默认先显示白话结果；完整窗口、回撤、费用和实验口径放入折叠的专业说明。
8. 产品只有一个正式信号事实源；不得通过“新手版/专业版”产生两个不同结论。
9. G6 前冻结可用性测试人数与通过比例；G9 必须提供真实目标用户测试记录。

## 数据与策略验收

1. 两个交易所分别提供原生采集、健康、缺口和恢复证据。
2. 采集前冻结 instrument catalog 和逐时成员快照规则。
3. 历史数据 manifest、event/availability time、缺口和 holdout 可复现。
4. 评估协议先于调参冻结；holdout 解封有 ledger，不能重复用于调参。
5. 价格观察和策略收益分开；费用、滑点、资金费率和延迟进入模拟口径。
6. G8 所有时间、样本和失败门槛必须在观察开始前登记。

## 工程、安全与发布验收

1. G0 bootstrap CI 和 main required check 可阻断失败提交。
2. G1 提供一条跨平台统一验证入口和可复现依赖。
3. D2 覆盖网络/数据库故障注入、恢复、日志脱敏、权限、回滚和备份恢复。
4. G9 覆盖移动端、浏览器、可访问性、新手理解、风险披露、隐私留存和发布后观察。
5. 任一关键门禁失败必须退回对应 G 阶段，不得带病发布。

## L0 特例验收

1. M7-T02 审核不夹带 G0 修改。
2. 审核 `f307c81..93720f8` 并证明后续至 `101e593` 无 M7 实现变化。
3. 在当前树运行完整回归。
4. 通过只允许 legacy local review 与 offline evidence 标签，不宣称远端 CI、集成或 Paper 能力。
