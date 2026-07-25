# 妖币暴涨做多

独立的币安、欧易妖币暴涨启动做多信号项目。

本仓库不包含另一项目的做空反转策略。权威路线是
[`DEVELOPMENT_WORKFLOW.md`](DEVELOPMENT_WORKFLOW.md) 的 G0-G9 串行门禁，
当前机器状态只以 [`PROJECT_STATUS.yaml`](PROJECT_STATUS.yaml) 为准。

产品/架构与工程/安全双重评审通过并已入库的开发标准记录在
[`docs/OPTIMIZED_PRODUCT_WORKFLOW.md`](docs/OPTIMIZED_PRODUCT_WORKFLOW.md)。
该标准不会自行授权后续任务、公开行情、Paper 或其他能力。

现有产品、策略、API、前端与通知成果仍只算
`OFFLINE_EVIDENCE_ACCEPTED`；这不代表真实行情、连续 Paper、部署、发布或交易
能力。任何公开行情接入、凭证、账户、订单、杠杆、做空、真实交易、部署或发布
都需要对应 Gate 的独立任务卡和产品负责人明确授权。

后续卡的冻结顺序记录在
[`governance/packages/package-a.manifest.json`](governance/packages/package-a.manifest.json)。
当前获授权的唯一任务是 Package A 最后一张卡 `G1-T01` generation 2。它只建立
跨平台、可复现的完整 CI 入口，不改变产品行为或离线能力上限。开发者与 CI
使用同一入口：

```bash
python3 scripts/verify_full_ci.py --offline --fail-closed --require-transport
```

该命令强制校验运行时与依赖锁、治理状态、固定 fixture、transport 测试、完整
Python 与前端测试、生产构建、依赖完整性、秘密与越界路径；任何缺项均失败即停。

Generation 2 修复把 Python 固定为 GitHub Actions 在 Ubuntu 24.04 与
Windows 2022 均提供制品的 `3.12.10`，所有 Python 制品均需 SHA-256 哈希。
PR CI 在依赖安装后临时阻断操作系统级出站连接，机械证明 Python、Node 和
curl 子进程无法联网，并在成功或失败后恢复原网络策略。每个平台的完整 Python
集合按稳定 node-id 哈希分成四个无重叠分片并在分片内并行；只有全部 Linux 与
Windows 分片成功，稳定检查 `G0 / exact-head` 才会通过。每个分片任务硬限制
20 分钟，不会通过跳过测试换取速度。
