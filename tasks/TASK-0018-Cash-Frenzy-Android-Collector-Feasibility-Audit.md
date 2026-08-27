# TASK-0018 — Cash Frenzy Android Collector Feasibility Audit

- Kind: companion
- Status: Cancelled
- Project key: CASH-FRENZY
- Owner: User / ChatGPT
- Executor: none
- Priority: P1 candidate
- Date: 2026-08-27
- Cancellation reason: canonical Task ID collision
- Canonical task: `tasks/TASK-0018-Huuuge-Lottery-Numerical-Breakdown-Report.md`
- Companion role: cancelled collision stub; not an attachment to the Lottery scope
- Replacement: pending `TASK-0020 — Task Allocation & Namespace Governance` and later reissue under a verified unique ID

## Decision

本文件由 ChatGPT 在未完成完整 `tasks/` 目录预检时误建，并与先存在的 Huuuge Lottery canonical `TASK-0018` 冲突。

根据最新 Task Allocation Rule：

- 先存在的 Huuuge Lottery Task 保持 canonical；
- 本 Cash Frenzy Task 立即停止执行并标记 `Cancelled`；
- 原完整规格仍保留在 Git 历史中，不覆盖、不删除；
- Cash Frenzy 研究方向继续有效，但当前只作为 Candidate；
- 等 TASK-0020 完成编号治理、Registry 和 Candidate 迁移规则后，再由 User 确认并使用经 Git 验证的唯一编号重新发布。

## Safety

在重新发布前：

- 不创建或修改 Cash Frenzy 模拟器实例；
- 不拉取 APK；
- 不启动 Root、Frida 或动态 Capture；
- 不使用 Subagents 执行本文件；
- 不修改 Huuuge Collector、TASK-0018 Lottery、TASK-0019 或其他正在进行的工作。

## Historical Note

误建前的完整 Scope、Deliverables、Subagent Policy 和 Acceptance Criteria 可通过本文件的 Git 历史查看；它们不是当前可执行指令。
