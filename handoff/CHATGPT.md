# ChatGPT Handoff

这是 ChatGPT 的固定交接入口。长期事实必须同步到 Capability contract、项目 Memory / Status、Task、RFC、ADR 或正式 Review，而不是只留在聊天中。

- Updated: 2026-08-27
- New User-authorized task: `TASK-0019-AI-Workspace-Overview-and-Separate-Progress-Documents.md`
- TASK-0019 status: `Ready`
- Executor: Codex
- Execution rule: 独立 branch / worktree；不得覆盖其他任务或未提交修改

## Current Queue and Governance Notes

- `TASK-0016-Automatic-Cross-Conversation-Memory-Curation.md`：当前为 `Review`；Codex 已完成 Round 1 required fixes，等待 ChatGPT Review Round 2。未收到 Review 结论前不要继续修改。
- `TASK-0017-Codex-Desktop-Proxy-WebSocket-Reconnect.md`：已完成并合入 `main`。
- 仓库当前存在两个不同内容但同为 `TASK-0018` 的 Ready 文件：
  - `TASK-0018-Cash-Frenzy-Android-Collector-Feasibility-Audit.md`
  - `TASK-0018-Huuuge-Lottery-Numerical-Breakdown-Report.md`
- 执行或汇报 0018 时必须使用完整文件名，不能只写编号；编号冲突由后续治理修复处理，不在 TASK-0019 中重命名这两个既有任务。
- `TASK-0019` 使用新的唯一编号，不修改 Huuuge、Cash Frenzy、Memory 或 Document Assistant 的实现。

## TASK-0019 Outcome

为整个 Game Planner AI Workspace 生成两份、且仅两份正式用户文档：

1. `《Game Planner AI Workspace｜项目全景说明》`
   - 立项原因、目标用户、能力蓝图、整体架构、设计框架、核心逻辑、角色分工、真相源、证据与安全边界。
   - 相对稳定，不放当前 Task 明细、完成清单和实时进度。

2. `《Game Planner AI Workspace｜项目进度与能力状态》`
   - 当前可用 / 部分可用 / 规划中 / 受阻能力；已完成 / 未完成 / 阻塞任务；主线、支线候选、入口、风险和精确下一步。
   - 持续更新；维护步骤放在本文末尾，不再创建第三份用户文档。

Git 源稿分别为：

```text
docs/overview/AI_WORKSPACE_PROJECT_OVERVIEW.md
docs/status/AI_WORKSPACE_PROJECT_PROGRESS.md
```

飞书发布通过 `feishu-docs` 完成。创建前必须 healthcheck、搜索防重；写入后回读正文、表格和企业内编辑权限。

## Boundaries

- Git 与业务仓库是状态真相源，飞书只是面向人的在线展示层。
- 每项 `Available / Completed` 必须附 Task、Status、Review、commit、release、test 或 healthcheck 证据。
- 不把 Schema、Roadmap、聊天、目录存在或未合入 branch 写成已实现。
- 不读取或复制未授权 Raw Capture，不触碰游戏请求、奖励、余额、付费或服务器状态。
- Secret、Token、账号、完整响应、逐笔余额、私有 Registry 和敏感日志不得进入 Git、飞书或聊天。

## Exact Next Action

User 转发“执行 TASK-0019”后，Codex 同步 AI-Workspace `main`，读取完整 Task、最新 Task / Status / Review / Handoff 与已登记业务仓库，使用独立 worktree 实施。完成后将 TASK-0019 更新为 `Review`，更新 CHANGELOG 与 `handoff/CODEX.md`，提交并 push 独立 branch，返回 commit 和两份飞书链接，等待 ChatGPT Review；不得自行合并 `main`。
