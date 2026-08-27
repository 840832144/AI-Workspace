# TASK-0016 ChatGPT Review — Round 1

- Date: 2026-08-27
- Reviewer: ChatGPT
- Result: **Needs changes**
- Reviewed HEAD: `1a48b176d453a021c4cc15e2186ed55653b6458a`
- Implementation commit: `ea4b7587432285ebaf2f7d99967b7f8e923820a3`

## Accepted Areas

以下部分通过本轮 Review：

- Reuse-first 选型合理：原生 Memory / Codex Hooks 作为 recall 与 lifecycle，Git 作为可审计长期真相源；未引入外部 SaaS、数据库或高权限 App。
- Candidate-first、Public / Private / Local-only、ASSISTED 默认、AUTO 隔离验证、完整聊天不入 Git 的架构方向正确。
- Capability、Governance、ADR、模板、ChatGPT/Codex/Generic adapters、Context Manifest 和 Source Pack 边界清晰。
- 未激活 production Hook 或 AUTO，未修改 Huuuge、Collector、Capture、SVN、飞书和 Document Assistant。
- 17/17 单元测试、Pilot 计数和 `manual upload required` 的表述可信，没有虚构真实召回准确率。

架构与 ASSISTED Pilot 可以保留；以下是 TASK-0016 关闭前必须完成的实现修订。

## Required Fix 1 — Project-private Git routing is not implemented

当前 `capture_command` 只允许 `scope=public` 且 `sensitivity=public` 写入 Git Inbox；任何 `project-private` / `cross-project-private` / `local-only` 都直接进入 Host-local Outbox。

因此现有 Pilot 只证明了“私有内容不会进入公共仓库”，尚未证明契约中承诺的“有批准 writer 时写入对应私有项目仓库”。这会阻断 Huuuge、CR 和其他私有项目之间真正共享 Solution / Skill / Project Memory 的核心使用场景。

必须：

1. 增加明确的 repository classification / approved destination contract，例如 `public-control-plane`、`project-private`、`cross-project-private-hub`。
2. 只有本机批准 Registry 与目标仓库 classification、scope、sensitivity 一致时才允许私有 Candidate 写入；否则继续 Outbox。
3. 不读取真实 Huuuge 或 CR 数据，使用 disposable private Git repository 完成真实路由测试。
4. 验证：私有 Candidate 进入私有 repo；公共 AI-Workspace 无写入；未批准 writer 仍进入 Outbox；错误 classification fail closed。

## Required Fix 2 — AUTO canonical writes must be branch-safe and transactional

Governance 规定自动 Git writer 只能使用独立 branch/worktree/PR，但当前 `curate_command` 在 AUTO 下没有检查当前 branch、clean state 或 worktree isolation，可以直接在 `main` checkout 写 canonical target、Archive 和 index。

同时 Promotion 的写入顺序不是事务：canonical target、Archive、index 任一后续步骤失败时，前面的文件可能已经落盘，造成“目标存在但 index 缺失”或“Candidate 已归档但 Promotion 未完成”的部分状态。当前测试中的 existing-target no-overwrite 不等于 rollback 测试。

必须：

1. AUTO Promotion 前 fail closed 检查：非 `main/master`、工作树符合允许范围、独立 branch/worktree 或等价隔离。
2. 把 canonical target、Archive 和 index 作为一个可恢复事务；任何阶段失败必须回滚到执行前状态，或写入明确的 recovery record 并禁止继续。
3. 增加 fault-injection 回归：target 写入后失败、Archive 前后失败、index 保存失败、Git 状态变化、main branch 调用。
4. 验证失败后 canonical、Candidate、Archive、index 四者一致，且不会声称 `promoted`。

## Required Fix 3 — Public Candidate provenance cannot accept placeholders

当前 `build_event` 会把 `source_host`、`source_project`、`source_actor_alias`、`source_reference` 默认成 `unknown`；validator 只检查非空，因此 `unknown` 可以作为 Public Candidate 的有效 provenance。

这不满足多对话、多 Agent、多人协作场景的审计要求。

必须：

1. 对所有进入 Git 的 Candidate 禁止空值和占位值：`unknown`、`n/a`、`none`、`-` 等。
2. Public Candidate 至少需要稳定的 source host、project、actor alias 和可复查 reference；缺失时进入 Review / Outbox，不得写公共 Inbox。
3. 为 CLI、Event file 和 Generic Agent 三条入口增加回归测试。

## Optional Follow-ups — not blocking this round

- 在 Inbox/Review 中增加相同 normalized key、不同 fingerprint 的 Candidate-to-Candidate conflict 标记。
- FileLock 使用 PID/lease 或更稳健的 stale-lock 规则，避免超过固定 300 秒的合法长任务被误判。
- Manifest 将 `generated_from_head` 与“提交后的 current HEAD”概念分开，避免 Source Pack 看起来一生成就落后一个 commit。

## Boundaries

- 不激活 production Hook，不切 production AUTO。
- 不访问或修改 Huuuge、CR、Collector、Capture、SVN、飞书或 Document Assistant。
- 不引入外部 Memory 服务、数据库或高权限 GitHub App。
- 保持最终模式 `ASSISTED`。

## Exact Next Action

Codex 继续同一个 TASK-0016，读取本 Review，完成三个 Required Fix、增加隔离与故障注入测试、更新 Task / CHANGELOG / Pilot / Governance / ADR / CODEX Handoff，最终保持 `ASSISTED`，提交并再次等待 ChatGPT Review。
