# Codex Handoff

- Updated: 2026-08-27
- Task: TASK-0020 — Task Allocation & Namespace Governance
- Status: Review — waiting ChatGPT Review Round 2
- Latest main included: `b278afa`
- Latest-main merge: `95901a71fe9434c36aa606154d527999b102e0fc`
- Branch: `codex/task-0020-namespace-governance`
- Worktree: independent linked worktree
- Review Fix commit: this handoff's commit; use branch HEAD from Git
- Subagents: none

## Outcome

ChatGPT Review 1 的五项 Required Fix 已全部完成。identity policy 保持：

```text
canonical ID = 全局唯一 TASK-XXXX
project_key  = 新 canonical 必填且格式强制
human_alias  = 可选阅读别名
```

Task Markdown 仍是 canonical truth，`tasks/TASK_REGISTRY.yaml` 仍为确定性可重建索引。未新建 Task，TASK-0020 保持 `Review`。

## Required Fixes

1. Writer gate：`next` 与所有 allocation 写操作统一要求 latest `origin/main`、non-main branch、independent linked worktree。main 与普通 non-linked checkout 均 fail closed。
2. Reservation lifecycle：`next` / `promote` 成功后 reservation 保持 `pending-main`；canonical 进入最新 main 后才允许 token `finalize`，未创建 Task 的放弃才允许 `release`。提前 release 发现 canonical 时拒绝。
3. Cross-clone / Host：allocator 原子创建 `refs/heads/task-reservations/TASK-XXXX`，使用 `--force-with-lease=<ref>:` first-writer CAS；后到 clone 在写 Task 前改取下一 ID。同 clone 另有 Git common-directory lock。
4. Project key：新 canonical 缺失、大小写/字符格式非法均失败。只有代码内有限审计 map 的 `TASK-0014` 至 `TASK-0019` 可缺省，未来 Task 不再按标题/路径推断。
5. Classification / overlap：`Draft` 纳入 active overlap。root Task 默认按 canonical 严格解析；只有显式 `Kind: companion` 且 reference 解析到存在、同 ID canonical 时才成为 companion。

异常恢复使用 reservation expected OID 做 CAS 删除；测试专用 fault injection 只有存在 `.task-test-allow-faults` marker 时可启用，生产目录无法误启。

## Current Inventory

最新 main 的并发 TASK-0018 Review 已在本轮第二次 latest-main gate 后安全合并并纳入 Registry；没有修改该 Review、Lottery 正文或 TASK-0021。

| Kind | Count |
| --- | ---: |
| canonical | 8 |
| companion | 2 |
| candidate | 1 |
| review | 4 |
| canonical collision | 0 |

Canonical ID 仍为 `TASK-0014` 至 `TASK-0021`；TASK-0018 Huuuge Lottery 是唯一 canonical。Cash Frenzy 完整规格仍是非执行 Candidate，Cancelled collision stub 仍是 companion。TASK-0016 历史 authorization 仅补充显式 `Kind: companion` 以符合严格分类，不改变其授权内容或 Memory 模式。

## Allocator Workflow

```powershell
python .\tools\tasks\task_cli.py scan
python .\tools\tasks\task_cli.py validate
python .\tools\tasks\task_cli.py next --purpose "approved-task"
python .\tools\tasks\task_cli.py release --id TASK-XXXX --token <token>
python .\tools\tasks\task_cli.py promote tasks/candidates/CANDIDATE-....md
python .\tools\tasks\task_cli.py finalize --id TASK-XXXX --token <token>
```

- `release`：只用于尚未创建 canonical 的放弃场景。
- `finalize`：只在 canonical 已进入最新 `origin/main` 后清理 remote/local reservation。
- 原 linked worktree 必须先同步最新 main，再执行 lifecycle 写操作。
- 本次真实仓库验证没有调用 `next` / `promote`，因此没有创建真实 reservation，也没有执行 Cash Frenzy Candidate。

## Validation Evidence

- `python -m unittest discover -s tools/tasks/tests -v` → **22/22 passed**（原 14 项全部保留并通过）。
- `python -m unittest discover -s tools/memory/tests -v` → **35/35 passed**；Memory 无退化。
- `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\bootstrap\tasks\Test-TaskRegistry.ps1` → Python compile、22 fixtures、真实 scan、真实 validate、incident repair 全部 PASS。
- 真实 scan → 8 canonical、2 companion、1 Candidate、4 Review、0 collision。
- 真实 validate → valid；Registry byte-for-byte 一致，分支包含最新 `origin/main@b278afa`。

新增定向回归覆盖：main/普通 checkout writer gate；受支持 next+release；同 clone与跨 clone并发 next；跨 clone并发 promote；promote 后 pre-merge next 不复用；merge/finalize；提前 release 拒绝；fault injection 无 remote/local reservation 泄漏；project_key 缺失/非法/grandfather；Draft overlap；malformed canonical、implicit companion、nonexistent/mismatched reference。

## Governance and Source Replacement

已同步更新 Task、ADR-0006、Incident-0001、Task/Tool README、Core Rules、Project Instructions、New Chat Bootstrap、CONTRIBUTING、AGENTS、CHANGELOG 与 Registry。ADR-0006 仍为 `Proposed / Waiting for ChatGPT Review`。

Project Source Pack、Context Manifest、Current State 与 replacement list 已按最终文件刷新。状态保持 `manual upload required`；未调用浏览器、飞书或其他外部系统自动替换，也不声称 Project Sources 已更新。

Memory 最终模式保持 `ASSISTED`；未激活 Hook / AUTO。

## Safety and Boundaries

- 未执行或晋升 Cash Frenzy Candidate。
- 未修改 TASK-0021、Huuuge Collector、Lottery 正文/报告、Capture、document-assistant、飞书、SVN、业务仓库或 Global runtime。
- 未读取 Raw Capture、账号、Secret、完整响应或私有 Registry。
- 未建立外部数据库或新服务；remote reservation 仅使用测试 bare origin，真实 origin 未创建 reservation ref。
- Subagents: none。


<!-- MEMORY-REFRESH:START -->
## Memory Context Refresh

- Generated: 2026-08-27T08:15:06Z
- Effective mode: `ASSISTED`
- Manifest: `CONTEXT_MANIFEST.yaml`
- ChatGPT Project Sources: `manual upload required`
- Private repositories: not read unless explicitly registered and authorized
<!-- MEMORY-REFRESH:END -->
## Exact Next Action

ChatGPT Review Round 2：审查同一 branch 的五项修复、22 项 Task 回归、35 项 Memory 回归、真实 Registry 与 remote CAS/finalize ADR。返回 `Accepted` 或具体 `Needs changes`。Review 前不执行 Cash Frenzy Candidate，不把分支工具描述为 main 已生效。
