# TASK-0020 ChatGPT Review — Round 1

- Decision: **Needs changes**
- Reviewed branch: `codex/task-0020-namespace-governance`
- Reviewed implementation commit: `126adcf3e04a20bdc43833f9fc6a65eb27375012`
- Reviewed handoff commit: `19020fa4462e0a3e68cf84b4ca586a4704e1e87d`
- Review date: 2026-08-27
- Subagents observed: none

## Passed

以下主体方向可以保留：

1. 采用“全局唯一 `TASK-XXXX` + 必填 `project_key` + 可选 human alias”的兼容策略，不大规模重编号历史 Task。
2. Huuuge Lottery 保持唯一 canonical `TASK-0018`；误建 Cash Frenzy 文件成为 Cancelled companion，完整规格恢复为非执行 Candidate。
3. Markdown Task 保持 canonical source，`TASK_REGISTRY.yaml` 由扫描确定性重建并做 byte-for-byte 漂移检查。
4. canonical / companion / candidate / review 的当前仓库分类结果为 8 / 2 / 1 / 2，当前 collision 为 0。
5. Candidate-first、latest-main、Project Sources `manual upload required`、Memory `ASSISTED` 和未触碰业务仓库/飞书/SVN/Raw 的边界清晰。
6. 14 项 Task 测试、35 项 Memory 测试和 PowerShell 5.1 入口已有交接证据；TASK-0021 并发进入 main 后，旧基线被 latest-main gate 阻断并重新同步。

## Required Fix 1 — `next` 没有执行文档承诺的写入 Gate

ADR、工具 README 和 Handoff 声明分配写操作要求：最新 `origin/main`、非 main 分支、独立 linked worktree。实际 `next_command()` 只调用 `ensure_git_latest(root)`，没有传入 `require_linked_worktree=True` 和 `require_write_branch=True`。

后果：

- `next` 可以在 `main/master` 或普通主 checkout 创建 Host-local reservation；
- `release` 又明确拒绝普通主 checkout，因此该 reservation 可能无法通过正常命令释放；
- 实现行为与文档、ADR、Execution Result 不一致。

必须：

1. `next` 与所有分配写操作统一强制 non-main linked worktree；
2. 增加 `next` 在 main、普通非-linked checkout 上 fail-closed 的回归；
3. 验证成功分配和 release 使用同一受支持工作流，不产生不可释放 reservation。

## Required Fix 2 — `promote` 提前释放 reservation，仍可在同一 clone 产生重复 ID

`promote_command()` 在本地创建 Task、更新 Candidate/Registry 后立即调用 `release_reservation()`。此时新 Task 尚未合并到 `main`，其他 linked worktree 看不到该 Task；reservation 一旦释放，另一个 worktree 可以再次分配同一 ID。

这意味着当前 14 项测试只证明“两个同时执行 `next` 的进程”得到不同 ID，没有证明：

- 两个并发/连续 Candidate promotion 不会得到同一 ID；
- promotion 完成但尚未 merge 时，另一个 `next` 不会复用该 ID；
- 手工 Task 创建完成到进入 main 之间的 reservation 生命周期安全。

必须选择并实现一种可复查方案：

- reservation 保留到 canonical Task 已进入最新 main，再显式 finalize/release；或
- 使用 Git remote ref/branch 的原子 CAS reservation，merge/abandon 后清理；或
- 另一个经 ADR 证明能够覆盖跨 worktree 生命周期的方案。

至少新增：并发 promote、promote 后未 merge 再 next、merge/finalize 后释放、异常/放弃恢复测试。

## Required Fix 3 — 当前方案不能阻止不同 clone / Host 在分配阶段获得同一 ID

ADR 明确承认不同 clone/Host 没有中心 reservation，只能等 push/Review/merge 时发现冲突。这没有完全满足本 Task 的核心事故目标：“两个会话不能获得相同 canonical ID”，也没有满足 Phase 2 对可验证 CAS / branch gate 的要求。

本次事故本来就来自不同会话，因此只保护同一 Git common directory 不够。

必须二选一，并由 User / ChatGPT Review 确认：

1. 实现基于 Git remote ref/branch 的原子 reservation，使不同 clone/Host 的 first-writer 获得 ID，后到者在创建 Task 前 fail closed；或
2. 将 Task ID allocation 明确收敛为单一授权 allocator（例如指定 Codex Host），其他 ChatGPT/Codex/Agent 只能创建 Candidate，不能直接分配 canonical ID；同时更新角色、Core Rules、Bootstrap 和操作话术。

仅依赖 merge 时发现 duplicate，不足以宣称 allocation collision 已被防止。

## Required Fix 4 — “必填 project_key”没有被 validator 强制

`parse_root_task()` 的 canonical 必填字段目前只有 Status、Owner、Executor、Priority、Date。任何未来新 canonical Task 即使没有 `Project key`，仍会通过 legacy inference，仅产生 warning。

这与选定 policy 和 ADR 的“新 canonical Task 必须显式记录 `project_key`”不一致。

必须：

1. 为历史 canonical Task建立明确、有限、可审计的 grandfather/legacy 规则；
2. 除该历史集合外，新 canonical Task缺少或格式非法的 `Project key` 必须 fail closed；
3. 增加新 Task 缺 project_key、非法 project_key、历史 grandfather task 三类回归。

## Required Fix 5 — active overlap 与 root Task 分类仍有绕过路径

### A. Draft 未进入 active overlap

Core Rules 明确要求检查 `Draft / Ready / In Progress / Review / Changes Requested`，但 `ACTIVE_STATUSES` 未包含 `draft`。Approved Candidate 可以在同目标 Draft 已存在时继续晋升。

必须把 Draft 纳入检查并增加回归。

### B. 非 canonical 标题会被自动当作 companion

当前逻辑在一级标题不匹配 `# TASK-NNNN — Title` 时，如果没有显式 Kind，会默认归类为 companion。一个使用错误破折号或格式损坏的新 canonical 文件可能因此绕过格式失败、不占用 ID，并让 allocator 再次分配该 ID。

必须：

1. 非 canonical 标题只有显式 `Kind: companion` 才能成为 companion；否则 fail closed；
2. companion 的 canonical reference 必须解析到当前存在的 canonical 文件，且 ID 一致；
3. 增加 malformed canonical、隐式 companion、nonexistent/mismatched canonical reference 回归。

## Boundaries for Fix Round

- 继续同一个 TASK-0020，不新建 Task。
- 不执行 Cash Frenzy Candidate。
- 不修改 Huuuge Collector、Lottery 报告、Capture、document-assistant、飞书、SVN 或其他业务仓库。
- Memory 保持 `ASSISTED`；Subagents 继续 `none`。
- 使用同一独立 branch/worktree修复，先同步最新 main；不得 force push 或覆盖 TASK-0021/其他任务。

## Acceptance for Round 2

- 上述五项均有实现修复和针对性回归；
- 原 14 项 Task 测试和 35 项 Memory 测试继续通过；
- main/ordinary checkout、same-clone lifecycle、cross-clone policy、project_key、Draft overlap、malformed companion 均有可复查证据；
- 真实仓库 scan/validate 仍为 0 collision，Registry 与 TASK-0021 等最新 main 内容一致；
- Task、ADR、Incident、README、Core Rules、CHANGELOG、Handoff 和 Project Source replacement 状态同步更新；
- TASK-0020 状态为 `Review` 后再次提交，等待 ChatGPT Review Round 2。
