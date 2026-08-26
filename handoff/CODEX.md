# Codex Handoff

这是 Codex 的固定交接入口。实现细节以对应外部项目仓库为准。

- Updated: 2026-08-26
- Task: TASK-0012
- Current state: Global AGENTS installed and public First Run path preserved; waiting for ChatGPT Review

## Objective

把 Document Assistant 和 Tool Discovery 提升为所有 Codex 项目共享能力，让 AI-Workspace 回到 Game Design 治理与项目控制面职责，同时确保只有公共 AI-Workspace 权限的新策划仍能执行 30 分钟 First Run。

## Completed

- 对照 OpenAI 官方 `AGENTS.md` 发现规则，确认 Global 层读取 `~/.codex/AGENTS.override.md` 或 `~/.codex/AGENTS.md`，再从仓库根目录向当前目录叠加项目指令。
- 检查本机 Global Codex 目录：开始时不存在 `AGENTS.md` 或 `AGENTS.override.md`，没有需要合并的既有规则。
- 新增 `bootstrap/AGENTS.md` 版本化模板，并安装到 `C:\Users\admin\.codex\AGENTS.md`。
- 建立 Tool Discovery 顺序、专用工具优先、READ/WRITE/ADMIN 分级、搜索防重、结果回读、缺失能力报告和禁止未批准替代入口规则。
- 将 Document Assistant 定义为跨项目共享工具；策划只使用管理员已配置的 Tool，不需要访问、Clone 或安装私有实现仓库。
- 将默认中文和新生成云文档默认企业内可编辑规则提升到 Global Codex 层。
- 新增 ADR-0002；更新 README、Architecture、Kernel、Capability Model、Manifest、Roadmap、RFC-0002、AI Team、Skill、Bootstrap、CONTRIBUTING 与 CHANGELOG。
- 根据 User 补充的访问边界，将 Huuuge First Run 更新为 RC4：公共 AI-Workspace 是唯一必需 Git 仓库；公司 SVN 提供正式采集包；Document Assistant 由管理员预配置并在前三分钟 fail fast。

## Confirmed Context

- AI-Workspace 只负责 Game Design 的架构、Capability、Workflow、Skill、Template、项目状态与交接。
- Tool Discovery、共享 Document Assistant 入口与跨项目安全基线属于 Global Codex 层。
- Tool 实现、测试、安装、endpoint、credential 和连接状态继续属于外部实现仓库、Host 配置与受控环境。
- 只有 AI-Workspace 已向新人开放公共访问；其他 Git 实现仓库保持私有，不能作为新人流程的前置条件。
- 30 分钟里程碑是“新策划在新电脑完成采集、生成 Markdown、AI 写入并回读飞书”；独立真实计时尚未发生。
- 本次没有修改 Document Assistant、MCP 配置、ChatGPT 设置、采集器、SVN 或业务功能。

## Validation

- 仓库模板与本机 Global 文件 SHA-256 一致。
- 本机没有 `AGENTS.override.md`，不会遮蔽新建的 Global `AGENTS.md`。
- 模板包含 Document Assistant 的 READ、WRITE、ADMIN/SECURITY 分类、默认企业内可编辑、权限失败和公共新人入口规则。
- First Run 中不再要求新人 Clone `huuuge-android-research` 或 Document Assistant；私有仓库只保留为维护者证据来源。
- 飞书 RC4 在同一 document ID 上 replace 并回读成功；再次验证 `link_share_entity=tenant_editable`、`verified=true`。
- Workspace Manifest 不再登记 Service endpoint、credential 或连接状态。
- 已执行 secret/boundary、内部链接、Git diff 和工作树检查；结果以本任务提交为准。

## Risks

- Codex 每次运行只构建一次 Agent 指令链；当前已打开会话可能不会自动重载新 Global 文件，重启后生效最稳妥。
- 后续若创建 `~/.codex/AGENTS.override.md`，它会在 Global 层遮蔽 `AGENTS.md`；排障必须先检查 override。
- 新人设备如果没有管理员预配置的 Document Assistant，就不能完成“AI 写飞书”；RC4 会在前三分钟报告，而不是在采集结束后才暴露阻塞。
- ChatGPT 和其他 Host 不会自动读取 Codex Global 文件，需要继续使用各自批准的 MCP/Connector 接入机制。
- TASK-0011 的独立策划盲测仍未完成，与 TASK-0012 的架构交付相互独立。

## Exact Next Action

ChatGPT Review `bootstrap/AGENTS.md`、ADR-0002、Workspace 边界与 First Run RC4，重点确认：Global 规则是否清晰、Document Assistant 是否无需私有仓库即可由策划使用、AI-Workspace 是否退出运行时工具入口职责，以及 30 分钟公共单仓路径是否没有新增前置阻塞。
