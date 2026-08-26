# Codex Handoff

这是 Codex 的固定交接入口。实现细节以对应外部项目仓库为准。

- Updated: 2026-08-26
- Task: TASK-0009
- Current state: Huuuge Knowledge Base initialized; waiting for ChatGPT Review

## Objective

建立整个 Huuuge Research 的统一知识导航，按 Slots、Systems、Events、Others 组织全部模块，并记录证据等级、数据来源、完成度和下一步计划。

## Completed

- 安全同步 AI-Workspace 与 `huuuge-android-research`，外部 evidence baseline 保持 `0590c2c37a0aa83b824920fa884f9f67007d3dcb`。
- 新增 `projects/huuuge-android-research/KNOWLEDGE/README.md` 统一入口。
- 新增四类策划导航：
  - Slots：1 module。
  - Systems：10 modules。
  - Events：14 modules。
  - Others：12 modules，包含礼包/购买、小玩法、Runtime 与未分类协议。
- 完整覆盖外部 catalog 37 modules：E3 Primary live 11、E2 Cross-cutting/config live 4、E1 Schema-only 22。
- 每个 module 记录 commit-pinned dossier、live/schema/ZPK 数据来源、completion score/label 和下一步计划。
- Huuuge 项目 README 与 Knowledge Index README 的策划入口文案已改为中文。
- 更新项目 README、Memory、Workflow、Status 和 CHANGELOG。

## Confirmed Context

- Knowledge taxonomy 是策划导航，不修改外部 `module_specs.json`、primary ownership 或 module catalog generator。
- Completion 表示结构目录成熟度，不等于数值研究、RTP/EV 或业务结论完成度。
- 当前 GUI 不要求手工 module/action marker；Knowledge 下一步计划使用正常操作、时间和 RPC 结构关联。
- 本次没有修改外部研究仓库、Collector、SVN release、Feishu 文档或本机环境。

## Risks

- Systems/Events/Others 是 planner-facing taxonomy，与协议 ownership 不是一一对应。
- Economy、Rewards、Lottery、Collection 等 cross-cutting evidence 会出现在多个业务视角，必须避免重复计算。
- `liveops_events` 与 `other_protocol` 仍是聚合/兜底 dossier，未来可能拆分。
- 所有外部 GitHub links 需要已授权的 private-repo session。

## Constraints

- 不在 Review 前修改分类、运行采集、开发 Extractor/Exporter 或生成新业务结论。
- 不复制 Raw/decoded values、账号/会话标识、APK、binary、credential 或完整外部 dossier。
- 外部仓库先更新证据，Knowledge Base 只同步经 Review 的导航事实。

## Exact Next Action

ChatGPT 审阅 `projects/huuuge-android-research/KNOWLEDGE/`，返回 Accepted 或针对分类、证据等级、数据来源、完成度和下一步计划的具体修订。Codex 等待 Review，不开始实现。
