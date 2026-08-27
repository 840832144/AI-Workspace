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

`next` 不是 `max + 1` 的只读猜测：它先完成完整 scan / validate / latest-main gate，再在 Git common directory 中建立原子 reservation。并发 linked worktree 会共享该 reservation 层，因此同一 clone 内不会获得同一 ID。若放弃该 ID，使用返回的 token 释放：

```powershell
python .\tools\tasks\task_cli.py release --id TASK-XXXX --token <returned-token>
```

已明确批准的 Candidate 可晋升：

```powershell
python .\tools\tasks\task_cli.py promote tasks/candidates/CANDIDATE-YYYYMMDD-PROJECT-SLUG.md
```

Candidate 与 active Task 目标重叠时默认阻断。只有明确决定为子任务时才使用 `--relationship subtask --related-task TASK-XXXX`；“继续现有 Task”不创建新 ID。

## 并发边界

- 本地 linked worktree：Git common directory 的 allocation lock + reservation 防止同号。
- 不同 clone / Host：各分支仍可能产生候选冲突；push / Review / merge gate 必须重新运行 validator，不能把本地 reservation 描述为中心化锁。
- `main/master`、普通主 checkout、无法 fetch `origin/main`、分支落后、lock 冲突全部 fail closed。
- Candidate 不是可执行入口；allocator 不会自动把 Candidate 变成 `Ready`。

## 回归

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\bootstrap\tasks\Test-TaskRegistry.ps1
```

测试只建立 disposable Git repository / bare origin / linked worktree，不访问业务仓库或外部系统。
