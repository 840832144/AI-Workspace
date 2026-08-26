# Changelog

本文件记录 AI-Workspace 治理结构、标准、工作流和协作行为的变化。

## [0.2.0] - 2026-08-26

### Changed

- 将 AI-Workspace 从通用 AI 工作空间正式收敛为 Game Planner AI Workspace。
- 明确目标用户为游戏策划、游戏数值策划、系统策划、活动策划和数据分析，并排除婚礼、投资等非游戏领域。
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
