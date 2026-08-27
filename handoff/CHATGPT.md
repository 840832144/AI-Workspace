# ChatGPT Handoff

这是 ChatGPT 的固定交接入口。长期事实必须同步到 Capability contract、项目 Memory/Status、Task、RFC 或 ADR，而不是只留在聊天中。

- Updated: 2026-08-27
- Primary implementation task: TASK-0016
- Concurrent operation: TASK-0015 Lottery capture-only is already running
- Current state: TASK-0016 authorized and Ready for Codex execution

## Confirmed Decisions

- TASK-0014：Accepted。Codex Subagent Pilot 保持默认 `OFF`。
- TASK-0015：Collector 已开始运行；User 继续亲自体验并决定所有付费、充值、礼包、Ticket 购买和资源消耗。体验结束前不做数据整理、数值分析、CR 方案或飞书报告。
- TASK-0016：User 已明确授权开始。完整设计见 [`TASK-0016`](../tasks/TASK-0016-Automatic-Cross-Conversation-Memory-Curation.md)，执行授权和并行边界见 [`TASK-0016 Execution Authorization`](../tasks/TASK-0016-EXECUTION-AUTHORIZATION.md)。

## TASK-0016 Objective

建立 Git-backed 自动记忆体系：

- 对话和 Agent 自动识别可长期复用的规则、决定、事实、Solution、Skill、Workflow、状态和失败经验；
- 自动优先生成结构化 Memory Candidate，人工作为冲突、敏感、高影响或无法判断时的兜底；
- Public / Project Private / Cross-project Private / Local-only 安全路由；
- OFF / ASSISTED / AUTO 模式与 Kill Switch；
- 自动刷新 Context Manifest、ChatGPT Project Source Pack、Status 和 Handoff；
- 优先复用本机、内部、官方和成熟开源方案，最后才自研。

## Parallel-safety Boundary

TASK-0016 可以与当前 Capture 并行，但必须：

- 只在 AI-Workspace 范围内研究、设计、实现和做隔离测试；
- 不修改 `huuuge-android-research`、运行中的 Collector、Capture Session、公司 SVN、AI Document Assistant 或飞书文档；
- 不停止、重启或重新配置当前采集环境；
- 不读取、整理或分析 TASK-0015 的实时数据；
- 会影响其他运行会话的生产安装、Global Hook、自动启动或重启操作保持关闭，直到证明无干扰并获得 User 授权；
- `AUTO` 允许隔离验证，但不得静默成为生产默认模式。

## Exact Next Action

Codex 同步 `AI-Workspace/main`，读取 Global/Project `AGENTS.md`、TASK-0016、Execution Authorization、本 Handoff 和相关 ADR。第一提交先把 canonical TASK-0016 状态改为 `In Progress`，完成 Reuse-first Solution Discovery，再按 Task 实施。完成后更新 Task、CHANGELOG 和 `handoff/CODEX.md`，提交并等待 ChatGPT Review。
