# Huuuge Android Research

本目录是 `huuuge-android-research` 在 Game Planner AI Workspace 中的项目控制面。它保存 Context、Memory、Workflow、Status 和稳定研究入口，不复制外部仓库的源码、采集数据或运行日志。

## Project Index

- Context: [`CONTEXT.md`](CONTEXT.md)
- Memory: [`MEMORY.md`](MEMORY.md)
- Workflow: [`WORKFLOW.md`](WORKFLOW.md)
- Status: [`STATUS.md`](STATUS.md)
- Reports: [`REPORTS/`](REPORTS/README.md)
- Assets: [`ASSETS/`](ASSETS/README.md)
- Implementation/evidence repository: [`huuuge-android-research`](https://github.com/840832144/huuuge-android-research)
- Current evidence baseline: [`0590c2c`](https://github.com/840832144/huuuge-android-research/commit/0590c2c37a0aa83b824920fa884f9f67007d3dcb)

## Research Entry Points

| Track | Start here | Current evidence state | Next research entry after Review |
| --- | --- | --- | --- |
| Battle Pass | [`battle_pass.md`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/battle_pass.md), [`BattlePass_schema.md`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/recovered/BattlePass_schema.md) | Schema-only / live sample pending | 有资格账号可用后，采集主界面、奖励轨和任务流量；不阻塞其他模块 |
| Slots | [`slots.md`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/slots.md), [`broad capture summary`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/analysis/20260825_182300/summary.md) | Live-confirmed；当前最完整的主模块之一 | 基于已有 Spin 证据选择首个 normalized gameplay Extractor，或补充代表性机器样本 |
| Lottery | [`lottery.md`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/lottery.md) | Cross-cutting/config live evidence；无专用交互 endpoint 样本 | 访问 lottery/draw/ticket 界面，补充专用 endpoint 与字段证据 |
| Task / Missions | [`missions.md`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/missions.md), [`mini_pass.md`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/mini_pass.md) | Generic Missions schema-only；MiniPass task-related flow live-confirmed | 分别检查通用日/周任务与 MiniPass missions，避免把两种结构合并 |

跨模块入口：

- [`Collector capabilities`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/docs/collector/CURRENT_CAPABILITIES.md)
- [`Collector data flow`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/docs/collector/DATA_FLOW.md)
- [`Module catalog index`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/artifacts/module_catalog/MODULE_INDEX.md)
- [`Current external status`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/CURRENT_STATUS.md)
- [`External tasks`](https://github.com/840832144/huuuge-android-research/blob/0590c2c37a0aa83b824920fa884f9f67007d3dcb/TASKS.md)

所有研究执行必须先通过 [`WORKFLOW.md`](WORKFLOW.md) 的 Review 和安全关卡。
