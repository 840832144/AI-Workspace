# Huuuge Android 研究项目

本目录是 `huuuge-android-research` 在 Game Planner AI Workspace 中的项目控制面。它保存 Context、Memory、Workflow、Status 和稳定研究入口，不复制外部仓库的源码、采集数据或运行日志。

新人 First Run 只需要公共 AI-Workspace 这一处 Git 入口；下面的私有实现仓库链接只供已授权维护者追溯证据，不是新人 30 分钟流程的前置条件。

## 项目索引

- 项目背景与边界：[`CONTEXT.md`](CONTEXT.md)
- 长期知识：[`MEMORY.md`](MEMORY.md)
- 研究工作流：[`WORKFLOW.md`](WORKFLOW.md)
- 当前状态：[`STATUS.md`](STATUS.md)
- 新人首跑：[`FIRST_RUN_GUIDE.md`](FIRST_RUN_GUIDE.md)
- 知识库：[`KNOWLEDGE/`](KNOWLEDGE/README.md)
- 证据标准：[`Huuuge Evidence Standard`](../../standards/HUUUGE_EVIDENCE_STANDARD.md)
- 报告索引：[`REPORTS/`](REPORTS/README.md)
- 资产索引：[`ASSETS/`](ASSETS/README.md)
- 实现与证据仓库：[`huuuge-android-research`](https://github.com/840832144/huuuge-android-research)
- 当前证据基线：[`0590c2c`](https://github.com/840832144/huuuge-android-research/commit/0590c2c37a0aa83b824920fa884f9f67007d3dcb)

## 研究入口

完整 37-module 导航统一从 [`Huuuge Research Knowledge Index`](KNOWLEDGE/README.md) 进入；下表保留 TASK-0008 定义的四条优先研究入口。

| 研究方向 | 入口文档 | 当前证据状态 | Review 后的下一入口 |
| --- | --- | --- | --- |
| Battle Pass | [`battle_pass.md`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/battle_pass.md), [`BattlePass_schema.md`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/recovered/BattlePass_schema.md) | L1 Schema；Runtime sample pending | 有资格账号可用后，采集主界面、奖励轨和任务流量；不阻塞其他模块 |
| Slots | [`slots.md`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/slots.md), [`broad capture summary`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/analysis/20260825_182300/summary.md) | L3 Runtime Observed；当前最完整的主模块之一 | 基于已有 Spin 证据选择首个 normalized gameplay Extractor，或补充代表性机器样本 |
| Lottery | [`lottery.md`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/lottery.md) | L2 Configured / Visible；无专用交互 endpoint 样本 | 访问 lottery/draw/ticket 界面，补充专用 endpoint 与字段证据 |
| Task / Missions | [`missions.md`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/missions.md), [`mini_pass.md`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/mini_pass.md) | Generic Missions L1；MiniPass task flow L3 | 分别检查通用日/周任务与 MiniPass missions，避免把两种结构合并 |

跨模块公共入口：

- [`采集器当前能力`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/docs/collector/CURRENT_CAPABILITIES.md)
- [`采集器数据流`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/docs/collector/DATA_FLOW.md)
- [`模块目录总索引`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/MODULE_INDEX.md)
- [`外部仓库当前状态`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/CURRENT_STATUS.md)
- [`外部仓库任务列表`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/TASKS.md)

所有研究执行必须先通过 [`WORKFLOW.md`](WORKFLOW.md) 的 Review 和安全关卡。
