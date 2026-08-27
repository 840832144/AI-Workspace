# Codex Handoff

- Updated: 2026-08-27
- Task: TASK-0020 — Task Allocation & Namespace Governance
- Status: Review
- Base main: `070744944d02b8d493c737db74bdc3d404963158`
- Branch: `codex/task-0020-namespace-governance`
- Worktree: independent linked worktree
- Implementation commit: `126adcf3e04a20bdc43833f9fc6a65eb27375012`
- Subagents: none

## Outcome

TASK-0020 已完成实现并等待 ChatGPT Review。最终 identity policy 为：

```text
canonical ID = 全局唯一 TASK-XXXX
project_key  = 必填项目元数据
human_alias  = 可选阅读别名
```

现有 Task 不批量重编号。Task Markdown 保持 canonical truth，`tasks/TASK_REGISTRY.yaml` 只由完整 scan 重建并以 byte-for-byte 比较检测漂移。

## Registry and Current Inventory

真实仓库最终扫描：

| Kind | Count |
| --- | ---: |
| canonical | 8 |
| companion | 2 |
| candidate | 1 |
| review | 2 |
| canonical collision | 0 |

Canonical Task：

- `TASK-0014` — Accepted / WORKSPACE
- `TASK-0015` — Complete / HUUUGE
- `TASK-0016` — Review / WORKSPACE
- `TASK-0017` — Complete / WORKSPACE
- `TASK-0018` — Review / HUUUGE；唯一 canonical 文件为 Lottery report
- `TASK-0019` — Ready / WORKSPACE
- `TASK-0020` — Review / WORKSPACE
- `TASK-0021` — Ready / WORKSPACE

TASK-0021 在本任务实施期间进入 `origin/main`。首次 Registry 写入被 latest-main gate 阻断；本分支安全同步到 `0707449` 后重新读取完整 Task/Handoff，并将 TASK-0021 纳入 Registry，没有覆盖其范围。

## Tooling

入口：

```powershell
python .\tools\tasks\task_cli.py scan
python .\tools\tasks\task_cli.py validate
python .\tools\tasks\task_cli.py next --purpose "approved-task"
python .\tools\tasks\task_cli.py candidate --help
python .\tools\tasks\task_cli.py promote --help
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\bootstrap\tasks\Test-TaskRegistry.ps1
```

- `scan`：分类 canonical / companion / candidate / review。
- `validate`：检查 duplicate、格式、Registry 漂移和 latest `origin/main`。
- `next`：完整验证后原子保留 ID，并返回 release token；不是只读 `max + 1`。
- `candidate`：创建非执行 Candidate，不分配 Task ID。
- `promote`：只晋升 User 明确批准的 Candidate；active overlap 默认阻断，子任务必须显式关联。
- `release`：释放未使用的 Host-local reservation。

分配写操作要求 non-main independent linked worktree。同一 clone 的 linked worktree 共享 Git common-directory lock/reservation；不同 clone/Host 没有中心化锁，因此 push、Review 和 merge 前仍必须复验最新 main。

## Candidate and Incident Repair

- Cash Frenzy 完整规格从 Git commit `7f6d9a5f315c27e829e2dda75396200ee91cdf98` 恢复到 `tasks/candidates/CANDIDATE-20260827-CASH-FRENZY-COLLECTOR-FEASIBILITY.md`。
- Candidate 明确非执行，当前为条件性 User decision，不满足工具的明确 approval gate。
- Cancelled 同号文件保留为 companion collision stub，旧链接不删除、不静默改成新的 Cash Frenzy Task。
- Huuuge Lottery 保持唯一 canonical TASK-0018。
- Incident：`docs/incidents/INCIDENT-0001-DUPLICATE-TASK-ID.md`。
- Decision：`docs/adr/ADR-0006-Task-Identity-and-Allocation.md`，状态 Proposed / Waiting for ChatGPT Review。

## Validation

`python -m unittest discover -s tools/tasks/tests -v`：14/14 passed。

TASK-0020 要求的 10 类验证：

1. duplicate canonical ID → non-zero；
2. canonical + companion 同 ID → 正确分类、无 collision；
3. filename / heading / Registry drift → non-zero；
4. Pending Candidate → 不分配 ID、promotion non-zero；
5. Approved Candidate → disposable fixture 中唯一晋升并保留 provenance；
6. active goal overlap → 无明确 subtask decision 时阻断；
7. 两个并发 allocator → 分别保留不同 ID；
8. lock busy、目录不完整、NUL/解析失败、Registry 漂移、branch 不含最新 main → fail closed；
9. 真实仓库 → 8 canonical、0 collision；
10. Cash Frenzy Candidate 存在且非执行，Huuuge Lottery 是唯一 canonical TASK-0018。

PowerShell 5.1 一键入口最终通过：Python compile、14 tests、真实 scan / validate 与 incident repair 均 PASS。首次运行暴露无 BOM 中文断言和 `$PSScriptRoot` 参数默认求值兼容问题；入口已改为 ASCII marker 与参数块后初始化，并完成回归。

## Governance Propagation

已统一更新 Project/Global AGENTS 模板、CONTRIBUTING、tasks README、Core Rules、New Chat Bootstrap 和 Project Instructions。规则一致要求：

- latest main + 完整 Registry validator；
- 全局 ID + project_key / alias；
- Candidate-first 和明确 User approval；
- active scope relationship；
- allocator reservation 与创建后复验；
- 任一 duplicate、漂移、解析、Git 或 lock 不确定性 fail closed。

## Project Source Replacement

- `CONTEXT_MANIFEST.yaml`、`bootstrap/chatgpt/02_CURRENT_STATE.md`、Project Source Pack 与 replacement list 已刷新。
- 当前状态：`manual upload required`。
- 未调用浏览器自动化、飞书或其他外部系统；没有声称 ChatGPT Project Sources 已自动替换。
- 按 replacement list 手工替换五个拆分来源，或只使用单文件 Source Pack；不要两者同时上传。

## Safety and Boundaries

- 未执行或晋升 Cash Frenzy Candidate。
- 未修改 Huuuge Collector、Lottery 业务结果、Capture、document-assistant、飞书、SVN、业务仓库或本机 Global Codex runtime。
- 未读取 Raw Capture、账号、Secret、完整响应或私有 Registry。
- 未建立外部数据库、服务、中心化锁或多 Agent 调度。
- Subagents: none。

## Known Limits

- Git common-directory reservation 只覆盖同一 clone；跨 Host 依赖最新 main、push 冲突和 Review/merge gate。
- 历史 Task 没有显式 `Project key` 时使用确定性 legacy inference，并输出 warning；不为消除 warning 批量改写已接受 Task。
- ADR-0006 和生产治理规则在 ChatGPT Review / merge 前仍是 Proposed；分支工具不能被描述为 main 已生效。
- Project Sources 仍需人工替换；TASK-0021 的 Live Context 工作是独立任务，本任务未执行。






<!-- MEMORY-REFRESH:START -->
## Memory Context Refresh

- Generated: 2026-08-27T07:35:19Z
- Effective mode: `ASSISTED`
- Manifest: `CONTEXT_MANIFEST.yaml`
- ChatGPT Project Sources: `manual upload required`
- Private repositories: not read unless explicitly registered and authorized
<!-- MEMORY-REFRESH:END -->
## Exact Next Action

ChatGPT Review TASK-0020：核对 ADR-0006 identity policy、可重建 Registry、latest-main / linked-worktree / reservation gate、Candidate promotion、10 类回归、Cash Frenzy incident repair 和 `manual upload required` 边界；返回 `Accepted` 或具体 `Needs changes`。Review 前不执行 Cash Frenzy Candidate，不把分支工具视为 main 已生效。
