# ChatGPT Handoff

这是 ChatGPT 的固定交接入口。长期事实必须同步到 Capability contract、项目 Memory / Status、Task、RFC、ADR 或正式 Review，而不是只留在聊天中。

- Updated: 2026-08-27
- New User-authorized task: `TASK-0020-Task-Allocation-and-Namespace-Governance.md`
- TASK-0020 status: `Ready`
- TASK-0016 status: `Review`
- TASK-0019 status: `Ready`
- Execution rule: 并行任务使用独立 branch / linked worktree；不得覆盖其他任务或未提交修改

## Task ID Collision Incident

完整 Git `tasks/` 目录确认曾同时存在两个不同内容的 canonical `TASK-0018`：

- `TASK-0018-Huuuge-Lottery-Numerical-Breakdown-Report.md`
- `TASK-0018-Cash-Frenzy-Android-Collector-Feasibility-Audit.md`

处理决定：

- 先存在的 Huuuge Lottery Task 保持唯一 canonical `TASK-0018`，状态继续以该文件为准；
- 误建的 Cash Frenzy 文件已标记 `Cancelled`，完整规格保留在 Git 历史；
- Cash Frenzy 研究方向仍有效，但在 TASK-0020 Accepted 并重新分配唯一编号前只作为 Candidate，不可执行；
- 新游戏顺序仍为 Cash Frenzy → Top Tycoon → 绯闻港口，但必须一个一个建立 Feasibility Audit，不并行开发。

## Emergency Governance Patch

在 TASK-0020 实施前，已先加入 fail-closed 紧急规则：

- `bootstrap/chatgpt/00_CORE_RULES.md`：新增完整目录枚举、ID 唯一、Candidate-first、冲突止损和新游戏 Feasibility Audit 规则；
- `bootstrap/chatgpt/03_NEW_CHAT_BOOTSTRAP.md`：新增新 Task 编号预检和创建后复验；
- `tasks/README.md`：区分 canonical / companion / candidate，并禁止猜编号；
- `AGENTS.md`：所有 Agent 创建或重编号 Task 前必须读取完整最新目录。

这些规则立即生效，但自动 Registry、allocator、并发锁、Candidate migration、Incident/ADR 和测试由 TASK-0020 完成。

## TASK-0020 Outcome

TASK-0020 必须建立：

1. 可重建的 canonical Task Registry；
2. `scan / validate / next / candidate / promote` 最小工具；
3. duplicate、companion、格式漂移、并发分配和非最新 Git 的 fail-closed 验证；
4. Candidate 工作流；
5. `ADR-0006`，比较全局编号、项目命名空间和“全局 ID + project_key/alias”；
6. Cash Frenzy 完整规格从 Git 历史迁入非执行 Candidate；
7. duplicate incident record；
8. Core Rules、Global AGENTS、ChatGPT Project Source Pack、Current State 和 Handoff 的统一刷新。

默认兼容方向：保留全局唯一 `TASK-XXXX` 作为 canonical ID，增加 `project_key` 和可选 human alias；不大规模重编号现有任务。最终决策等待 TASK-0020 实现证据和 ChatGPT Review。

## Current Queue

- `TASK-0015-Huuuge-Lottery-Live-Numerical-Breakdown.md`：限时采集任务，实际状态读取文件和业务仓库；不得由治理任务修改 Collector 或 Raw。
- `TASK-0016-Automatic-Cross-Conversation-Memory-Curation.md`：`Review`；使用独立 worktree，不得覆盖。
- `TASK-0017-Codex-Desktop-Proxy-WebSocket-Reconnect.md`：已完成并合入 `main`。
- `TASK-0018-Huuuge-Lottery-Numerical-Breakdown-Report.md`：唯一 canonical TASK-0018；业务分析范围保持不变。
- `TASK-0019-AI-Workspace-Overview-and-Separate-Progress-Documents.md`：`Ready`；不得被 TASK-0020 覆盖。
- `TASK-0020-Task-Allocation-and-Namespace-Governance.md`：`Ready`；User 已明确授权开始。

## Shared Boundaries

- AI-Workspace 是治理、Task 和 Handoff 真相源；业务实现仍在对应业务仓库。
- TASK-0020 不修改 Huuuge Collector、Capture、飞书、SVN、Document Assistant 或其他业务实现。
- 不读取或复制 Raw Capture、账号、Secret、完整响应、逐笔余额或私有 Registry。
- 不 force push、不重写先存在 Task 历史、不自动提升 Candidate。
- Task 分配不再依据聊天记忆或“最大编号 + 1”；必须先完整 scan 和 validate。
- Project Sources 是快照；TASK-0020 完成后生成 replacement list，人工重新上传。

## Exact Next Action

Codex 执行 `TASK-0020-Task-Allocation-and-Namespace-Governance.md`：

1. 在独立 linked worktree / branch 同步最新 `main`；
2. 读取 Task、最新 Handoff、Core Rules 和完整 `tasks/` 目录；
3. 严格按 Scope 实现 Registry、allocator、Candidate、incident、ADR 和测试；
4. 不执行 Cash Frenzy Candidate；
5. 更新 Task、CHANGELOG、`handoff/CODEX.md` 和 Project Source replacement 状态；
6. 提交并推送，等待 ChatGPT Review。
