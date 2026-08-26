# ChatGPT Handoff

这是 ChatGPT 的固定交接入口。长期事实必须同步到 Capability contract、项目 Memory/Status、Task、RFC 或 ADR，而不是只留在聊天中。

- Updated: 2026-08-26
- Task: TASK-0014
- Current state: Ready for Codex execution

## Review Decision

- TASK-0013：Accepted。
- Capability-first Discovery、Document Capability、Global AGENTS 与 AI-Workspace 边界已确认可继续使用。

## New Objective

执行 [`TASK-0014 — Codex Subagent Pilot with Kill Switch`](../tasks/TASK-0014-Codex-Subagent-Pilot.md)。

目标是在不影响现有 Codex、MCP 和业务仓库的前提下，建立可一键关闭的保守子 Agent 试运行：

- 1 个主 Agent负责判断、写入、整合和 Git。
- 4 个只读子 Agent负责探索、资料读取、证据/测试验证和 Review。
- 安装后默认 `OFF`；User 可切换到 `MANUAL`，并发上限 4。
- 简单任务不启用，复杂且可独立并行的只读工作才使用。

## Boundaries

- 不实现 AUTO 模式或 1+8 全量角色。
- 不允许并行写代码或写飞书。
- 不修改 Huuuge Collector、Document Assistant、SVN、Secure Tunnel 或 ChatGPT 设置。
- 不覆盖现有 `~/.codex/config.toml`；只安全修改 `[agents]` 相关设置并保留备份。
- 不在 Git 或日志中写入任何 Secret。

## Exact Next Action

Codex 同步 AI-Workspace `main`，读取 Global/Project `AGENTS.md`、本 Handoff 和 TASK-0014，按 Task 实施、验证并推送。完成后把 Task 状态改为 `Review`，更新 `CHANGELOG.md` 与 `handoff/CODEX.md`，返回 commit 和开关命令，等待 ChatGPT Review。
