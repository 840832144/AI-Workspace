# Task Candidates

本目录保存尚未成为 canonical Task 的方向。Candidate 不是可执行入口，不占用 `TASK-XXXX`，也不能因为出现在 Project Sources、聊天或 Handoff 中就被视为 `Ready`。

## 命名与最低字段

文件名和一级标题统一使用：

```text
CANDIDATE-YYYYMMDD-<PROJECT-KEY>-<SLUG>
```

每个 Candidate 至少记录 `Kind`、`Status`、`Project key`、建议优先级、User decision、来源、创建/更新时间、Goal、依赖、风险和 Promotion Gate。`User decision` 未明确批准时，allocator 禁止晋升。

## 生命周期

```text
讨论 / 新方向
→ Candidate（不分配 TASK ID，不执行）
→ User 明确批准
→ 完整 scan + validate + active overlap 检查
→ 原子 reservation
→ canonical Task + Candidate provenance
→ 创建后再次 validate
→ ChatGPT Review / User 决定执行顺序
```

- `Pending` / 条件性确认：继续保留 Candidate。
- `Approved` / `Confirmed`：具备晋升资格，但仍需 allocator 与冲突检查。
- `Migrated`：保留原文件和 `Migrated to/at`，不删除 provenance。
- `Rejected` / `Superseded`：保留原因，不占 Task ID。

相同目标已有 `Ready / In Progress / Review / Changes Requested` 时，默认阻断新 ID。决定“继续已有 Task”时直接更新原 Task；只有明确决定为子任务时，才以 `--relationship subtask --related-task TASK-XXXX` 晋升。

## 安全

- Candidate 不得包含 Secret、Raw Capture、账号、完整响应、逐笔余额、私有 Registry 或敏感日志。
- 不得自动把 Candidate 改成 `Ready`，不得依据 `max + 1` 手工猜号。
- 不同 clone/Host 之间没有中心化锁；分支 push、Review、merge 前必须重新验证最新 `origin/main`。
