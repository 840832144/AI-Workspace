# Bootstrap

本目录定义新环境、新 Agent 或新协作者接入 Game Planner AI Workspace 的最小步骤。

## Global Codex Bootstrap

[`AGENTS.md`](AGENTS.md) 是 `~/.codex/AGENTS.md` 的版本化模板，提供所有项目共享的 Capability Discovery、保守 Subagent Policy、Document Capability、文档语言与安全规则。

1. 先检查 `~/.codex/AGENTS.override.md` 和 `~/.codex/AGENTS.md` 是否存在，不得直接覆盖已有个人或组织规则。
2. 没有现有规则时，将本模板复制为 `~/.codex/AGENTS.md`；已有规则时逐节合并并审阅冲突。
3. 重新启动 Codex，再确认全局与项目级 `AGENTS.md` 都已进入当前指令链。
4. Global Codex 层先发现 Capability；AI-Workspace 提供 Catalog 和 Game Design 治理，不作为 MCP、Connector、Plugin 或其他工具的运行时入口。
5. 新策划只需公共 AI-Workspace 模板和管理员已配置的共享 Tool；不得要求其访问或 Clone 私有实现仓库。

Codex 子 Agent 的可关闭试运行模板、安装脚本和开关说明见 [`codex/README.md`](codex/README.md)。安装后默认保持 `OFF`，不会改变上述新人入口或其他 Host。

官方发现顺序以 [OpenAI `AGENTS.md` 文档](https://learn.chatgpt.com/docs/agent-configuration/agents-md) 为准：Global 层只读取非空的 `AGENTS.override.md` 或 `AGENTS.md` 之一，然后从仓库根目录向当前目录叠加项目指令。

## Repository Bootstrap

1. Clone 私有仓库并确认 remote、branch 和访问权限。
2. 安全同步 `main`，确认工作树状态。
3. 阅读根目录 `README.md`、`AI_TEAM.md`、`ARCHITECTURE.md`、`CONTRIBUTING.md`。
4. 阅读自己的固定 handoff 和相关项目 Status。
5. 确认本地 Git identity；不得把 credential 写入仓库配置文件。
6. 开始前明确目标、范围、非目标和真相源。

## New Project Bootstrap

1. 从 `projects/TEMPLATE/` 复制统一结构到 `projects/<slug>/`。
2. 填写游戏项目 Context，并链接外部项目仓库或系统。
3. 只迁入已确认、长期有用且非敏感的 Memory。
4. 从 Catalog 引用或新增 Capability，定义 Workflow、Skill、Template、Implementation Binding 和验证关卡。
5. 初始化 Reports、Assets 和 Status，写明唯一下一动作。
6. 若项目改变整体体系，先创建 RFC。

## Session Completion

1. 审阅 diff 和内部链接。
2. 更新 Status、handoff 和 CHANGELOG 中适用部分。
3. 确认无 secrets、业务代码或隐私数据。
4. 按 `CONTRIBUTING.md` 提交。
5. 推送后确认远端 commit，再交接。
