# ChatGPT Handoff

这是 ChatGPT 的固定交接入口。长期事实必须同步到项目 Memory/Status、RFC 或 ADR，而不是只留在聊天中。

- Updated: 2026-08-26
- Task: TASK-0008
- Current state: Huuuge Project initialization review requested

## Incoming Review

审阅 `projects/huuuge-android-research/` 的项目边界、长期 Memory、研究 Workflow、当前 Status 和 Battle Pass/Slots/Lottery/Task 入口。

## Confirmed Context

- 外部仓库 baseline 为 `0590c2c37a0aa83b824920fa884f9f67007d3dcb`。
- AI-Workspace 是项目控制面，不迁移 Huuuge 代码、采集数据或工程证据。
- Battle Pass、Lottery dedicated endpoint、generic Missions 的 live evidence 仍不完整；Slots 当前最成熟。
- Generic Missions 与 MiniPass task flow 必须分开。
- TASK-0008 没有授权新研究执行。

## Review Files

- `projects/huuuge-android-research/README.md`
- `projects/huuuge-android-research/CONTEXT.md`
- `projects/huuuge-android-research/MEMORY.md`
- `projects/huuuge-android-research/WORKFLOW.md`
- `projects/huuuge-android-research/STATUS.md`

## Review Questions

1. Context 的研究边界和成功标准是否足以约束后续工作？
2. Memory 是否只保留 durable Confirmed/Decision，并正确标记 Hypothesis？
3. 四条入口的当前 evidence 分级是否准确？
4. Workflow 是否正确体现 ChatGPT 设计/Review与 Codex 实施/验证 Ownership？
5. Review 通过后，应从四条入口中选择哪一个作为唯一下一研究阶段？

## Exact Next Action

返回 Accepted 或逐项修改意见；在 Review 完成和 User 选定优先模块前，不向 Codex 下发采集、Extractor 或报告实现任务。
