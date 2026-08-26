# Changelog

本文件记录 AI-Workspace 治理结构、标准、工作流和协作行为的变化。

## [0.5.0] - 2026-08-26

### Added

- TASK-0009：建立 `Huuge Research Knowledge Index` 作为整个研究知识的统一入口。
- 建立 Slots、Systems、Events、Others 四类导航，覆盖外部 catalog 全部 37 个模块。
- 为每个模块记录 evidence level、live/schema/static 数据来源、结构完成度和 Review 后下一步计划。
- 定义 E3 Primary live、E2 Cross-cutting/config live、E1 Schema-only、E0 Inferred/static 四级知识证据模型。

### Changed

- Huuuge Project README、Memory、Workflow、Status 接入 Knowledge Index，并将当前 milestone 更新为 TASK-0009 Review。
- 将 Huuuge 项目 README 与 Knowledge Index README 的策划入口文案改为中文，同时保留固定模块名和技术文件名。
- Codex/ChatGPT Handoff 更新为 Knowledge Base Review gate。

### Boundaries

- 未修改 `huuuge-android-research`、采集器、module catalog generator、SVN release 或本机研究环境。
- 未复制 Raw/decoded values、账号/会话数据、APK、binary、credential 或完整外部 dossier 正文。
- 未开发新采集、分类器、Extractor、Exporter 或报告功能。

## [0.4.0] - 2026-08-26

### Added

- TASK-0008：从 Workspace Project Template 初始化 `projects/huuuge-android-research/`。
- 建立 Huuuge 项目 Context、Memory、Workflow、Status、Reports 和 Assets 控制面。
- 建立 Battle Pass、Slots、Lottery、Task/Missions 四条稳定研究入口，并锁定外部 evidence baseline commit `0590c2c`。

### Changed

- `projects/README.md` 从“仅提供模板”更新为包含首个正式登记的游戏研究项目。
- Codex/ChatGPT Handoff 更新为 TASK-0008 Review gate。

### Boundaries

- 未迁移或修改 `huuuge-android-research` 的源码、采集器、脱敏产物或运行配置。
- 未复制 Raw/decoded values、账号/会话数据、APK、native/Frida binary、credential 或外部文档正文。
- 未开始新采集、Extractor、报告开发或 Feishu 发布。

## [0.3.0] - 2026-08-26

### Added

- TASK-0007 `Document Assistant Capability Roadmap`，规划公司文档中台的 15 个 Capability、六阶段演进、Review 问题与非目标。
- 新增 `docs/roadmaps/` 作为服务与工具 Capability Roadmap 的索引入口。

### Changed

- 明确 `Document Assistant` 暂不改名，现有实现保持不变，外部仓库继续作为实现真相源。
- 将 Workspace Phase 2 标记为 Planning / Waiting for ChatGPT Review。
- 明确共享公司基础设施可以服务多个使用方，但 AI-Workspace 只治理其 Game Design 使用边界，不导入其他领域业务内容。

### Boundaries

- 未修改 Document Assistant、`feishu-doc-mcp`、MCP 配置或 ChatGPT 设置。
- 未开发 transport、permission、sync、monitoring 或 deployment 功能。
- 未调用 Feishu API，未迁移仓库或文档数据。

## [0.2.0] - 2026-08-26

### Changed

- 将 AI-Workspace 从通用 AI 工作空间正式收敛为 Game Planner AI Workspace。
- 明确目标用户为游戏策划、游戏数值策划、系统策划、活动策划和数据分析，并排除非游戏领域。
- 将 Roadmap 重构为 Workspace Foundation、Document Assistant、Workspace Sync、Planner Toolkit 四阶段。
- 完善 AI Team 的 Decision、Review、Ownership、Tool Ownership、Security 和 Escalation 规则。
- 将项目标准从 Context、Memory、Workflow、Status 四件套扩展为包含 Reports、Assets 的统一游戏项目结构。
- 将项目模板的唯一入口收敛到 `projects/TEMPLATE/`，移除旧的重复四件套模板。

### Added

- 新增 Workspace Kernel，定义 Workspace、Project、Skill、Workflow、Capability、Template、Tool、Agent、Memory、Status 及 Mermaid 关系图。
- 新增 Capability Model，定义 Capability、Skill、Workflow、Template、Tool 的分层关系。
- 新增 Game Analysis、Slot Analysis、Battle Pass、Economy Design、Lottery、Task System、Excel、SQL、Python、Report Writing、Feishu Document 共 11 类 Skill 目录。
- 新增 `projects/TEMPLATE/` 游戏项目标准模板。
- 新增仅作规范示例的 `workspace.yaml.example`。
- 新增 ADR-0001，记录 Game Design 领域收敛决定。

### Boundaries

- 未实现任何业务代码、Skill 运行时、manifest loader 或同步程序。
- 未迁移任何现有仓库或游戏项目。
- 未修改 `feishu-doc-mcp` / `document-assistant`。
- 未加入任何非游戏领域内容。

## [0.1.0] - 2026-08-26

### Added

- 初始化 AI 协作总控仓库，不包含业务代码。
- 建立 RFC、ADR、Skills、Workflows、Templates、Standards、Projects、Handoff 和 Bootstrap 目录。
- 建立 README、AI Team、Architecture、Roadmap、Contributing 和 Agent 入口文档。
- 建立 Workspace Charter、Document Assistant、AI Skill System 三份初始 RFC。
- 建立 ChatGPT 与 Codex 固定交接文档。
- 定义项目 Context、Memory、Workflow、Status 四件套及可复制模板。
- 建立 RFC、ADR、项目和交接模板，以及各目录入口说明。

### Boundaries

- 未实现任何业务代码。
- 未迁移或修改任何现有项目仓库。
- 未修改 `feishu-doc-mcp` / `document-assistant`。
