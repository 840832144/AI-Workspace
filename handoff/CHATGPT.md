# ChatGPT Handoff

这是 ChatGPT 的固定交接入口。长期事实必须同步到项目 Memory/Status、RFC 或 ADR，而不是只留在聊天中。

- Updated: 2026-08-26
- Task: TASK-0012
- Current state: Ready for ChatGPT Review

## Review Objective

审阅 Global AGENTS、Tool Discovery 和 Workspace 边界调整，确认 Document Assistant 已成为跨项目共享工具，AI-Workspace 不再承担运行时工具入口职责，并且只拥有公共 AI-Workspace 权限的新策划仍可执行 30 分钟 First Run。

## Prepared Files

- `bootstrap/AGENTS.md`
- `bootstrap/README.md`
- `docs/adr/ADR-0002-Global-Tool-Discovery.md`
- `ARCHITECTURE.md`
- `docs/architecture/WorkspaceKernel.md`
- `docs/CapabilityModel.md`
- `workspace.yaml.example`
- `docs/rfc/RFC-0002-Document-Assistant.md`
- `docs/roadmaps/DocumentAssistantCapabilityRoadmap.md`
- `projects/huuuge-android-research/FIRST_RUN_GUIDE.md`
- `projects/huuuge-android-research/REPORTS/TASK-0011-FIRST-RUN-VALIDATION.md`
- `CHANGELOG.md`

## Confirmed Decisions

- Global Codex 运行文件为 `~/.codex/AGENTS.md`；仓库只在 `bootstrap/AGENTS.md` 保存可版本化模板。
- Tool Discovery 和共享 Document Assistant 入口属于 Global Codex/Host 层。
- AI-Workspace 只保留 Game Design 的能力契约、Workflow、Skill、Template、项目状态和交接，不登记运行时工具目录、安装入口、endpoint、credential 或连接状态。
- Document Assistant 工具分为 READ、WRITE、ADMIN/SECURITY；工具可见不自动授予写入或权限操作授权。
- 新生成的云文档默认企业内可编辑；管理员策略阻止时保留文档、报告失败、不绕过也不重复创建。
- 公共 AI-Workspace 是新人唯一必需的 Git 仓库。私有实现仓库只供已授权维护者追溯，不得成为新人前置条件。
- 30 分钟 First Run 通过公司 SVN 正式包完成采集，通过管理员预配置的 Document Assistant 写飞书；共享 Tool 缺失时在前三分钟 fail fast。
- 飞书指南已原文档更新到 RC4，回读关键标记成功并再次确认企业内可编辑权限。
- 本次没有修改 Document Assistant 实现、MCP 配置或 ChatGPT 设置。

## Review Checklist

1. Global 模板是否只包含跨项目稳定规则，没有混入 Huuuge 当前状态？
2. Tool Discovery 是否明确检查当前 Host 实际能力，并避免要求新人访问私有源码？
3. 专用工具优先、READ/WRITE/ADMIN 分级、搜索防重和回读验证是否足够明确？
4. credential、管理员策略和外部写入边界是否安全？
5. Architecture、Kernel、Capability Model、Manifest 与 Roadmap 是否一致表达 Workspace 不再是运行时工具入口？
6. First Run RC4 是否能只从公共 AI-Workspace 进入，并在开始采集前确认 SVN 和 Document Assistant？
7. 30 分钟目标是否仍需真实独立策划计时，而没有被文档提前宣称成功？

## Known Risks

- 新 Global 文件需要在新 Codex 会话中加载；当前会话不能作为自动重载证据。
- 未来的 `~/.codex/AGENTS.override.md` 会遮蔽同级 `AGENTS.md`。
- 新人设备仍需要公司 SVN/飞书权限和管理员预配置的 Document Assistant；这些是里程碑环境前置，不是 Git 私有仓库权限。
- ChatGPT 不自动继承 Codex Global 文件，仍需通过已批准的 Remote MCP/Connector 机制使用 Document Assistant。
- TASK-0011 的独立策划盲测仍待 User 安排，不应在本次 Review 中误标为完成。

## Exact Next Action

ChatGPT 按上述清单给出 `Accepted` 或 `Needs changes`。本轮只审阅架构、规则、公共入口和边界，不开发功能，不修改 Document Assistant，也不修改 ChatGPT 设置。
