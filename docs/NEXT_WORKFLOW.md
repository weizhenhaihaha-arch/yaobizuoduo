# 后续工作流程与授权门禁

更新日期：2026-07-25（Asia/Shanghai）

`PROJECT_STATUS.yaml` 是唯一当前机器状态源。Package A 的 G0 治理链已在
authoritative baseline `94c87f28436e2ea8899c9a407e1f1413de893603`
完整收口。当前唯一获授权任务是 `G1-T01` generation 1，风险等级 `D1`。

本卡只建立一个开发者与 GitHub CI 共用的跨平台完整验证入口：

```bash
python3 scripts/verify_full_ci.py --offline --fail-closed --require-transport
```

入口必须在精确 Python、Node、npm 与递归依赖锁下运行，强制收集并通过
`tests/test_m5_transport.py`，同时覆盖 canonical governance、完整 Python
测试、前端测试与构建、fixture 摘要、依赖完整性、秘密扫描和冻结路径边界。
本地与 GitHub 的稳定汇总检查名保持 `G0 / exact-head`；Linux 与 Windows
必须使用相同入口，任何缺失、跳过、网络回退或平台差异都失败即停。

累计变更不得超出 Package A manifest 中 `G1-T01.allowed_paths`。Package A
manifest/activation、ruleset `19526291`、产品行为与
`OFFLINE_EVIDENCE_ACCEPTED` 能力上限保持不变。

本卡开发交付只能停在干净的 `awaiting_review` 候选，等待独立
code/security 与 architecture/product-route 审查。开发者不得 push、创建
PR、合并或启动下一卡。G2+、市场网络、凭证、账户、订单、交易、ruleset
修改、部署、发布及 LOCAL-PREVIEW 扩展均未获授权。
