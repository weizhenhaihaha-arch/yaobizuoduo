# 优化后的产品开发工作流

状态：`FROZEN_PROPOSAL_AWAITING_PRODUCT_OWNER_CONFIRMATION`

基线：`af25e573b6a1a8b38d8eaf9a60bcf4988be6ed32`

本文件固化产品/架构与工程/安全双重评审通过的后续工作流。它是待确认
标准，不是 `PROJECT_STATUS.yaml` 的替代品，也不授权 P0、G1、公开网络、
Paper、凭证、交易、ruleset、部署、发布或 `LOCAL-PREVIEW` 扩展。

## 1. 决策原则

1. 产品结果优先，但 fixture、stale 或未校准观察不得冒充真实信号。
2. 任意时刻只有一个活动任务、一个开发 AG；负面只返回当前卡。
3. 门禁必须绑定真实能力风险，历史治理不得成为第二产品。
4. 每个能力包只确认一次；包内 exact evidence 全绿后由主 Codex 严格串行
   审核、合并和验收。
5. 时间盒只是规划目标。到期只能是 `COMPLETE`、
   `SCOPE_REDUCTION_PROPOSAL` 或 `BLOCKED_EVIDENCE_GAP`；不得降低门槛、
   自动跳卡或暗改 manifest。

## 2. 包与任务顺序

```text
P0 路线/manifest 瘦身
  -> Foundation Package: P1 G1-min
  -> Public Evidence Package: P3 G3-A -> P4 G3-B -> P5 G4 -> P6 G5
  -> Paper Package: P7 G6
  -> STOP
```

G7-G9 必须另建 package。任何 package 切换、能力上限改变、私有 API、
凭证、账户、订单、真实资金、杠杆、做空、ruleset、部署或发布均重新取得
产品负责人明确授权。

### P0：路线与 manifest 瘦身

P0 是 D0 planning-only 卡，规划目标半个工作日，只允许：

- 冻结 `Linux full`、`macOS smoke`、`Windows deferred/not-supported`；
- 冻结 CI 分层、历史回归 path trigger、包 manifest、非目标和 SLO；
- 为 P3 内嵌 G2-JIT checkpoint 做最小 schema/validator/test 规划；
- 生成并验证已经存在的 Foundation manifest exact digest，供产品负责人
  一次确认；不得预确认未知未来 bytes。

P0 不实现 CI、legacy、业务、网络或产品。P0 完成时可同时请求 Foundation
digest 确认，不增加第二次“确认 P0 完成”仪式。

### Foundation Package：P1 G1-min

P1 只建立后续产品所需的最小工程底座：

- clean-clone 单一验证入口；
- Python、Node、API runtime/dependency pins、hash 和 integrity；
- 离线 HTTP/SSE transport tests 全部 collected/pass；
- frontend tests 与 production build；
- tracked-secret 与 forbidden-capability scan；
- 目标平台 required CI。

PR-fast 目标 15 分钟、硬上限 20 分钟。时间超限只能触发优化、分层、
缩 scope 提案或阻塞，不能删除必要测试或 retry-to-green。

### Public Evidence Package：P3-P6

首次 Binance/OKX 公开网络能力只确认一次。P3-P6 严格串行，仍禁止私有
API、凭证、账户、订单和交易。

#### P3：G3-A 双交易所公开行情纵向卡

P3 是唯一活动任务，必须通过以下机器状态，不得仅在文档中自报：

```text
G2_JIT_CHECKPOINT_PENDING
  -> G2_JIT_CHECKPOINT_VERIFIED
  -> G3_PUBLIC_COLLECTION_ACTIVE
  -> G3_API_UI_ACTIVE
```

`PENDING` 与 `VERIFIED` 阶段公开网络能力为 false。若现有 schema 不能表达，
P0 只做最小 schema amendment；不得跳过 G2，也不得恢复完整独立 G2 治理卡。

P3 内部采用严格单父 checkpoint：

1. A：真实 P3 entrypoint 的 G2-JIT、catalog、membership、identity；
2. B：公开 feed、host/rate/clock/gap/freshness；
3. C：最薄只读 API/UI health。

A 不绿禁止 B，B 不绿禁止 C，C 不得弱化 A/B。任一负面只返回 P3，清空旧
candidate/review/CI 身份。

G2-JIT 必须从真实 P3 entrypoint 生成静态与运行时
import/call/subprocess/data reachability inventory，并给每个节点记录
`reuse | rewrite | reject`：

- unknown dynamic edge = 0；
- private API、credential、account、order、trading、persistence、
  notification、deploy reachable edge = 0；
- `<=5 contracts`、`<=2 adapters` 只是 scope cap，不是安全放行条件；
- 实际 import graph 必须等于已审核 inventory；敏感或未知边直接 reject。

公开行情验收必须逐交易所机械计算：

- eligible denominator 是该 venue 当前小时 membership snapshot；
- identity 至少包含
  `venue/native_id/base/quote/settle/contract_type`，collision = 0；
- listing、suspend、delist 可追踪；
- public host/redirect escape = 0；
- live route fixture fallback = 0；
- coverage 每 venue `>=99%`，remaining missing/error 100% 显示；
- 每个 eligible instrument 都进入
  `fresh | stale | missing | error` 终态；
- freshness 使用冻结的 venue-event/monotonic-ingest 定义、样本窗口和
  时钟校正；不可靠 event time 为 `UNKNOWN`，不得进入 observation；
- scan latency 包含所有终态分类，不得忽略超时项；
- stale classified-as-fresh = 0；
- stale included-in-observation-board = 0，但 health UI 必须显示 stale；
- 每 venue 官方 rate-budget peak utilization `<50%`；无可靠官方计量模型
  则为 `UNKNOWN` 并 fail；
- gap、duplicate、out-of-order、reconnect、429、clock-skew hostile 全绿。

具体 endpoint、字段、采样周期、freshness 窗口和最小样本数在 Public
Evidence manifest 中冻结。

#### P4：G3-B Observation Board

P4 只提供事实型、可复现的市场异动观察：

- 公式版本固定；
- Binance 与 OKX 不合并；
- 显示 venue、source、event time、ingest time、freshness、last error；
- 不使用未来窗口或回放结果参与排序；
- 统一标识
  `OBSERVATION_ONLY / NOT_CALIBRATED / NOT_A_SIGNAL`。

禁止“潜在暴涨、推荐、可以买、胜率”、alert、push 和 trading CTA。

#### P5：G4 immutable replay

P5 规划目标两个工作日，验收为：

- content-addressed snapshots；
- hourly membership、watermark、missingness、cost guard；
- 相同输入 rebuild hash 100% 相同；
- decision time 后数据拒绝；
- 禁止未来数据与幸存者偏差。

目标到期不能替代验收。

#### P6：G5 signal calibration

P6 规划目标三个工作日。实验前冻结 label、window、top-K、baseline 和 cost：

- append-only trial ledger；
- 所有 feature、参数和窗口访问计入最多 20 次预算；
- 最多 3 个 feature families；
- 至少 3 个 walk-forward，并覆盖预注册 regimes；
- holdout access count = 1；
- venue、liquidity、regime 分开报告；
- multiple-testing correction；
- 成本、滑点和 funding 提高 50% 后方向反转则
  `NO_STABLE_SIGNAL`。

无稳定增益必须交付“暂无稳定信号”，不得无限调参或偷看 holdout。

### Paper Package：P7 G6

首次 stateful Paper 能力只确认一次。P7 只建立：

- 单进程、单 canonical store；
- 幂等事件、恢复、migration、stale 抑制；
- store、API、UI 共用一个 truth source；
- duplicate lifecycle = 0；
- illegal state regression = 0；
- store/API/UI mismatch = 0；
- migration up/down、restart、replay 全绿；
- stale input creates new signal = 0。

不加入 Redis、queue、Telegram、高级 observability 或真实订单。P7 完成后
停止，G7-G9 另包。

## 3. 每张卡的固定闭环

```text
权威 main / PROJECT_STATUS / AG / 工作区回读
  -> 唯一开发 AG 实现当前卡
  -> exact candidate 与当前路径测试
  -> 独立 code/security APPROVE
  -> 独立 architecture/product-truth CLEAR
  -> HEAD/base/main/ruleset/allowlist 无漂移
  -> 主 Codex 对 D2/stateful 当次证据人工 go/no-go
  -> 自动 merge
  -> authoritative-main CI/readback
  -> required fresh clone
  -> repository 与外部 memory
  -> 包内下一卡或停止
```

- 开发 AG 不能自我批准、合并或启动下一卡。
- 任一非绿只返回当前卡，新 candidate 清空旧 reviewer/CI 身份。
- CI 后 base/main 漂移必须重跑关键门。
- 主 Codex 的 D2/stateful go/no-go 是负责人审核，不再次向用户确认，也不是
  无人值守合并。

## 4. CI 与历史回归分层

普通产品 PR required：

- current authorization/base/head/allowlist/status；
- 当前产品路径功能、fault-injection、secret 与 forbidden-scope；
- exact candidate 和必要 target-runtime build。

修改 validator、schema、package activation 或 merge route 时，相关全历史
suite 自动成为 PR-blocking。其他旧 generation/fixture 进入 nightly/manual。

P3-P7、package terminal、validator/schema/package/merge-route 变更合并后执行
一次 fresh-clone canonical。普通 P0/P1 在 GitHub clean checkout 与 main CI
已经等价时不重复人工 full clone。

Nightly 失败立即暂停新的自动合并和下一卡，不自动回滚 main，也不关闭已有
只读产品。主 Codex 在一次 bounded triage 中分类：

- `REGRESSION_CURRENT_MAIN`；
- `INFRA_EXTERNAL`；
- `STALE_HISTORICAL_ASSERTION`。

只有当前 main regression 返回当前卡修复；外部基础设施保持真实阻塞，不得
重跑取绿；历史断言只有在规范明确更新并经双审后才能降级。

## 5. 永久能力边界

- 产品只扫描 Binance、OKX USDT 永续。
- G3 是公开市场观察，不是做多信号。
- G5 前不得使用“做多信号、潜在暴涨、推荐、胜率”等预测性结论。
- 不使用私有 API，不保存凭证，不管理账户，不下单，不管理杠杆，不做空。
- 不修改 ruleset，不部署、不发布，除非对应能力卡另获明确授权。
- 本提案不能被本地状态文字、自动化心跳或旧分支自行激活。
