# Task Registry 与 Allocator

本工具为 `TASK-0020` 的标准库 reference implementation。Task Markdown 是 canonical source，`tasks/TASK_REGISTRY.yaml` 只能由扫描结果重建，不能手工维护成第二真相源。

## 日常检查

```powershell
python .\tools\tasks\task_cli.py scan
python .\tools\tasks\task_cli.py validate
```

成功表现：`status=valid`、`collision_count=0`。`validate` 会 fetch `origin/main`，当前分支不包含最新 main、Registry 漂移、解析失败或 canonical ID 冲突时返回非零。

修改 Task / Candidate / Review 后，在独立 linked worktree 的非 main 分支重建 Registry：

```powershell
python .\tools\tasks\task_cli.py scan --write-registry
python .\tools\tasks\task_cli.py validate
```

## 分配与 Candidate

未获 User 批准的方向先创建 Candidate，不占 `TASK-XXXX`：

```powershell
python .\tools\tasks\task_cli.py candidate `
  --title "候选方向" `
  --project-key WORKSPACE `
  --slug EXAMPLE `
  --source "User discussion reference" `
  --goal "记录待确认方向"
```

需要手工建立已批准 Task 时，先保留下一个 ID：

```powershell
python .\tools\tasks\task_cli.py next --purpose "approved-task"
```

`next` 不是 `max + 1` 的只读猜测：它先完成完整 scan / validate / latest-main gate，再用 remote Git ref first-writer CAS 建立 reservation。Git common directory lock 负责同 clone 串行，remote ref 负责不同 clone / Host 排他。所有分配写操作只允许包含最新 main 的 non-main independent linked worktree。

若未创建 Task 并决定放弃该 ID，使用返回的 token：

```powershell
python .\tools\tasks\task_cli.py release --id TASK-XXXX --token <returned-token>
```

创建或晋升 Task 后 reservation 保持 `pending-main`。先提交、Review 并合入 main；再让原 linked worktree 同步最新 main，并显式完成生命周期：

```powershell
python .\tools\tasks\task_cli.py finalize --id TASK-XXXX --token <returned-token>
```

`release` 在本地或 `origin/main` 已存在该 canonical Task 时会拒绝，防止 merge 前提前复用编号；`finalize` 在最新 main 尚无 canonical 时也会拒绝。

已明确批准的 Candidate 可晋升：

```powershell
python .\tools\tasks\task_cli.py promote tasks/candidates/CANDIDATE-YYYYMMDD-PROJECT-SLUG.md
```

Candidate 与 active Task 目标重叠时默认阻断。只有明确决定为子任务时才使用 `--relationship subtask --related-task TASK-XXXX`；“继续现有 Task”不创建新 ID。

## 并发边界

- 本地 linked worktree：Git common directory allocation lock 防止同 clone 写入争用。
- 不同 clone / Host：`refs/heads/task-reservations/TASK-XXXX` 由 `--force-with-lease` 原子抢占；后到者在创建 Task 前改取下一编号。
- promotion / manual creation：remote reservation 一直保留到 canonical 进入 main 后 `finalize`，放弃才使用 `release`。
- `main/master`、普通主 checkout、无法 fetch `origin/main`、分支落后、lock 冲突全部 fail closed。
- Candidate 不是可执行入口；allocator 不会自动把 Candidate 变成 `Ready`。

## 回归

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\bootstrap\tasks\Test-TaskRegistry.ps1
```

测试只建立 disposable Git repository / bare origin / linked worktree，不访问业务仓库或外部系统。
