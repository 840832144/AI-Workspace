# TASK-0020 ChatGPT Review — Round 2

- Decision: **Needs changes**
- Reviewed branch: `codex/task-0020-namespace-governance`
- Reviewed implementation commit: `2fa15495d36a7325842f6538facfaf2d3fd78d03`
- Review date: 2026-08-27
- Subagents observed: none

## Passed

本轮只复核 Round 1 的五个阻塞项。以下均已满足，主体方案保持不变：

1. `next`、`release`、`finalize`、`promote` 等 allocation 写操作统一要求 latest `origin/main`、非 main 分支和 independent linked worktree。
2. reservation 已改为 remote Git ref 的 first-writer CAS，可覆盖不同 clone / Host；promotion 不再提前释放，canonical 进入 main 后才通过 `finalize` 清理。
3. 新 canonical Task 强制显式合法 `Project key`；仅 TASK-0014 至 TASK-0019 使用有限 grandfather map。
4. `Draft` 已加入 active overlap 检查。
5. companion 必须显式 `Kind: companion`，引用必须解析到存在且同 ID 的 canonical Task；格式损坏的 canonical 不再静默降级。
6. 针对上述行为的新增回归已存在；Handoff 记录 Task tests 22/22、Memory tests 35/35、PowerShell 5.1 通过，真实 Registry collision 为 0。

## Required Fix — Remote reservation 不得发布未合并分支内容

当前 `reservation_commit()` 使用调用分支 `HEAD` 的 tree，并把该 `HEAD` 设为 reservation commit 的 parent，然后将 reservation ref 推送到远端。

这意味着：只要当前 allocation worktree 含有尚未推送或尚未 Review 的已提交改动，创建 reservation 时 Git 会把这些 commit 与完整 tree 一并发送到远端 `task-reservations/TASK-XXXX` ref。即使 Task 文件尚未创建，allocator 也可能意外发布当前分支中的其他未合并内容。

这违反了本项目的最小写入、先 Review 后共享和敏感内容不得因基础设施操作被意外传播的边界。

必须：

1. reservation ref 的 commit/tree 只能基于最新 `origin/main`（或独立空 tree + `origin/main` parent），不能以调用分支 `HEAD` 的 tree/parent 作为远端对象；
2. 本地 branch `HEAD` 仅作为 metadata hash 记录，不得通过 reservation ref 暴露其 tree 或 commit graph；
3. 新增回归：在 allocator worktree 创建一个未推送的 sentinel commit，执行 `next` 或 `promote` 后，从另一 clone 读取 reservation ref，确认 sentinel 文件和分支 commit 均不可达，reservation parent/tree 基于 `origin/main`；
4. 原 remote CAS、release/finalize 生命周期和 22 项测试不得退化。

## Integration Gate

Review 时该分支已落后当前 `main`。完成上述修复后，必须同步最新 main，重建 Registry / Context Manifest / Source Pack，重新运行 Task、Memory 和 PowerShell 验证，再推送等待 Round 3。

## Boundaries

- 继续同一个 TASK-0020，不新建 Task。
- 不执行 Cash Frenzy Candidate。
- 不修改 TASK-0021、Huuuge Collector、Lottery、Capture、document-assistant、飞书、SVN 或其他业务仓库。
- Memory 保持 `ASSISTED`；Subagents: none。
