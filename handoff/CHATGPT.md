# ChatGPT Handoff

这是 ChatGPT 的固定交接入口。长期事实必须同步到 Capability contract、项目 Memory/Status、Task、RFC 或 ADR，而不是只留在聊天中。

- Updated: 2026-08-27
- Task: TASK-0015
- Current state: Ready for Codex execution

## Review Decision

- TASK-0014：Accepted。
- Codex Subagent Pilot 的原子安装、OFF/MANUAL 开关、父会话权限限制、单写入者、MCP deny、回归测试和最终 OFF 均已通过 Review。
- 当前默认模式继续保持 `OFF`；是否按任务启用 `MANUAL` 由 User 决定。

## New Objective

执行 [`TASK-0015 — Huuuge Lottery 限时活动采集与数值拆解`](../tasks/TASK-0015-Huuuge-Lottery-Live-Numerical-Breakdown.md)。

User 报告 Lottery 活动剩余约 5 小时。本任务优先级为 P0，必须先启动现有 Collector 保住实时证据，再进行分析、文档和 Git 沉淀。

核心交付：

- Lottery 专用实时 Capture；
- Slots 活动道具掉落；
- 完成进度需要的道具、Spin、筹码和时间；
- 奖励结构与返还；
- 可直接用于 CR 项目的参数建议；
- 脱敏 Git 报告和企业内可编辑飞书报告。

## Boundaries

- 不为本任务重构 Collector、开发通用 Extractor、Normalized Fact Layer 或 AI Report Engine。
- Raw/value-bearing capture、账号信息、逐笔余额和截图原件保持本机。
- 不进行付费购买、充值、请求修改或服务器状态修改。
- Subagents 不是前置条件；不得为了切换模式延误采集。主 Agent仍是唯一写入者。

## Exact Next Action

Codex 同步 AI-Workspace 与 `huuuge-android-research`，读取 TASK-0015 和 Huuuge 当前规则。立即完成 Environment Check，启动一个新的 Lottery 专用 Capture，看到 READY 后再向 User逐步发操作指令。采集结束后 clean finalize、完成分析和飞书报告，提交两个仓库并等待 ChatGPT Review。
