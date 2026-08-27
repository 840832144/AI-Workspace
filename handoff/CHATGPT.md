# ChatGPT Handoff

这是 ChatGPT 的固定交接入口。长期事实必须同步到 Capability contract、项目 Memory / Status、Task、RFC、ADR 或正式 Review，而不是只留在聊天中。

- Updated: 2026-08-27
- New User-authorized task: `TASK-0019-AI-Workspace-Overview-and-Separate-Progress-Documents.md`
- TASK-0019 status: `Ready`
- TASK-0016 review state: **Needs changes — Round 2**
- Execution rule: 并行任务使用独立 branch / worktree；不得覆盖其他任务或未提交修改

## Current Queue and Governance Notes

- `TASK-0016-Automatic-Cross-Conversation-Memory-Curation.md`：Round 1 三个 Required Fix 的主体实现已通过；Round 2 Review 仍发现两个安全阻塞项。正式记录：[`reviews/TASK-0016-CHATGPT-REVIEW-2.md`](../reviews/TASK-0016-CHATGPT-REVIEW-2.md)。
- `TASK-0017-Codex-Desktop-Proxy-WebSocket-Reconnect.md`：已完成并合入 `main`。
- 仓库当前存在两个不同内容但同为 `TASK-0018` 的 Ready 文件：
  - `TASK-0018-Cash-Frenzy-Android-Collector-Feasibility-Audit.md`
  - `TASK-0018-Huuuge-Lottery-Numerical-Breakdown-Report.md`
- 执行或汇报 0018 时必须使用完整文件名，不能只写编号；编号冲突由后续治理修复处理，不在 TASK-0019 中重命名这两个既有任务。
- `TASK-0019` 使用新的唯一编号，不修改 Huuuge、Cash Frenzy、Memory 或 Document Assistant 的实现。

## TASK-0016 Review Round 2

### Passed

- Approved Project-private Git routing 已具备 Registry、writer、classification、scope、sensitivity、source project 和外部 Git root 校验；错配或未授权进入 Outbox。
- AUTO 已限制为 non-main linked worktree；canonical target、Candidate、Archive、index 使用可回滚事务，五类 fault injection 均保持 `promoted=0`。
- CLI、Event file、Generic Agent 已拒绝 `unknown`、`n/a`、`none` 等占位 provenance。
- 34/34 回归、Round 2 Pilot、最终 `ASSISTED`、Hook/AUTO 未激活和真实业务仓库未触碰的边界可保留。

### Required Fixes

1. **ASCII `-` provenance 漏洞**：Governance 声明 `-` 无效，但实现的 placeholder set 未包含 `-`，测试也未覆盖。需要对全部 documented placeholder 做参数化回归，三类入口均进入 Outbox，Git Inbox 为 0。
2. **Secret classification hard deny**：Registry 只能收紧权限，不能通过 `allowed_sensitivities` 放开 `sensitivity=secret`。即使 Registry 误配允许 `secret`，也必须只写脱敏本机 Outbox，Public / Private Git Inbox 均为 0；`scope=local-only` 同样不可被 repository alias 提升。

TASK-0016 最终模式继续保持 `ASSISTED`；不激活 Hook 或 production AUTO，不新增外部 Memory Provider。

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

## Shared Boundaries

- Git 与业务仓库是状态真相源，飞书只是面向人的在线展示层。
- 每项 `Available / Completed` 必须附 Task、Status、Review、commit、release、test 或 healthcheck 证据。
- 不把 Schema、Roadmap、聊天、目录存在或未合入 branch 写成已实现。
- 不读取或复制未授权 Raw Capture，不触碰游戏请求、奖励、余额、付费或服务器状态。
- Secret、Token、账号、完整响应、逐笔余额、私有 Registry 和敏感日志不得进入 Git、飞书或聊天。

## Exact Next Actions

1. TASK-0016 Codex：同步 `main`，读取 Round 2 Review，完成两个小范围安全修复和回归，更新 Task、CHANGELOG、Pilot、Governance、Capability、ADR 与 `handoff/CODEX.md`，提交并再次等待 ChatGPT Review。
2. TASK-0019 Codex：继续遵循独立 worktree / branch 规则实施，不得覆盖 TASK-0016 或两个 TASK-0018。
