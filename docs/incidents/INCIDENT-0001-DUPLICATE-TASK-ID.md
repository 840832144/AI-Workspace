# INCIDENT-0001 — Duplicate canonical TASK-0018

- Status: Mitigated; permanent controls implemented in TASK-0020, waiting ChatGPT Review
- Date: 2026-08-27
- Scope: AI-Workspace Task governance
- Severity: Governance integrity / no business runtime impact observed
- Related Task: [`TASK-0020`](../../tasks/TASK-0020-Task-Allocation-and-Namespace-Governance.md)
- Decision: [`ADR-0006`](../adr/ADR-0006-Task-Identity-and-Allocation.md)

## Summary

两个不同内容的 canonical 文件一度共用 `TASK-0018`：先存在的 Huuuge Lottery 数值拆解报告，以及后创建的 Cash Frenzy Collector 可行性审计。后者创建前没有读取 Git 最新 main 和完整 `tasks/` 目录，编号来自不完整上下文。

## Confirmed Impact

- canonical identity 在文件名、聊天执行话术和 Handoff 中产生歧义。
- Cash Frenzy 规格被短暂标记为可执行 `Ready`，但随后已停止并改为 `Cancelled`。
- Huuuge Lottery 文件保持先存在的 canonical `TASK-0018`。
- 未观察到 Cash Frenzy Candidate 被执行；未因此修改模拟器、Collector、Capture、业务仓库、飞书或 SVN。
- 完整 Cash Frenzy 规格仍在 Git commit `7f6d9a5f315c27e829e2dda75396200ee91cdf98`，没有数据丢失。

## Root Cause

1. Task ID 分配依赖聊天/局部目录视图，没有强制读取最新 main 的完整清单。
2. 没有机器可验证的 canonical / companion / candidate / review 分类。
3. 没有 Registry 漂移检查、Git latest writer gate 或跨 clone / Host 的原子 reservation。
4. 新方向在 User 决定执行前直接创建 `Ready` Task，没有 Candidate-first 缓冲层。

这不是编号空间耗尽；`max + 1` 本身也不能证明目录完整或防止并发。

## Immediate Containment

- 保留 Huuuge Lottery 为 canonical `TASK-0018`。
- 将 Cash Frenzy 同号文件改为 Cancelled collision stub，并禁止执行。
- Core Rules、New Chat Bootstrap、根 AGENTS 和 tasks README 加入完整目录预检与 fail-closed 规则。
- 创建 TASK-0020 处理长期治理；在 Accepted 前不重新分配 Cash Frenzy。

## Permanent Corrective Actions

- `tasks/TASK_REGISTRY.yaml` 从 Markdown 确定性生成。
- `task_cli.py scan / validate / next / candidate / promote`。
- 全局 `TASK-XXXX` + `project_key` + 可选 alias。
- Git latest、non-main independent linked-worktree writer gate、common-directory lock，以及 remote Git ref first-writer CAS reservation。
- reservation 保持到 canonical Task 进入 `origin/main` 后显式 `finalize`；未使用编号通过 token `release`，异常按 expected OID 清理。
- 新 canonical 强制显式 `project_key`；仅 `TASK-0014` 至 `TASK-0019` 使用审计 grandfather map。
- root Task 默认严格按 canonical 解析；companion 必须显式声明 Kind，并引用存在且 ID 一致的 canonical。
- Cash Frenzy 完整规格迁入非执行 Candidate；Cancelled stub 明确为 companion。
- companion、review 与 canonical 可关联相同 ID，但不占第二个 canonical identity。

## Regression Coverage

1. 两个 canonical 同 ID失败；
2. canonical + companion 同 ID正确分类；
3. 文件名、标题或 Registry ID 漂移失败；
4. 未批准 Candidate 不分配 ID；
5. approved Candidate 唯一晋升并保留 provenance；
6. active（含 Draft）目标重叠要求明确 continue/subtask；
7. 同 clone 与不同 clone / Host 的并发 allocator、并发 promotion 不返回相同 ID；
8. promotion 到 merge 前不释放编号，进入 main 后 finalize；放弃 release 与 fault injection 不泄漏 remote ref；
9. main、普通 checkout、lock、目录不完整、解析失败、Registry 漂移、非最新 main 均 fail closed；
10. project_key 缺失/非法/grandfather 和 malformed/implicit/nonexistent/mismatched companion 均有定向回归；
11. 真实仓库 active canonical collision 为 0；
12. Cash Frenzy Candidate 与 Huuuge canonical TASK-0018 同时验证。

## Lessons

- Project Sources 与聊天记忆只能做上下文，不是分配真相源。
- “当前最大编号”不等于“下一个安全编号”。
- 分配必须把目录完整性、Git 最新性、并发和创建后复验视为同一事务。
- 事故记录保留必要的 Git 证据和影响，不保存聊天全文或敏感业务数据。
