# Codex Handoff

- Updated: 2026-08-27
- Task: TASK-0020 — Task Allocation & Namespace Governance
- Status: Review — waiting ChatGPT Review Round 3
- Review source: `reviews/TASK-0020-CHATGPT-REVIEW-2.md`
- Latest main included: `f8a9ab0`
- Latest-main merge: `0121012`
- Branch: `codex/task-0020-namespace-governance`
- Worktree: independent linked worktree
- Review Fix commit: this handoff's commit; use branch HEAD from Git
- Subagents: none

## Outcome

Review 2 确认 Round 1 的五项 Required Fix 全部通过。本轮唯一剩余问题已修复：remote reservation 不再发布调用分支的未合并 tree 或 commit graph。

`reservation_commit()` 现在执行：

```text
tree   = latest origin/main^{tree}
parent = latest origin/main
requesting HEAD = SHA metadata only
```

requesting HEAD 不再是 reservation commit 的 tree 或 parent。remote first-writer CAS、token-gated release/finalize、promotion pending-main 生命周期及 writer gate 均未改变。

## Sentinel Evidence

新增 `test_remote_reservation_does_not_publish_requesting_branch_graph`：

1. allocator linked worktree 创建并提交一个未推送 sentinel 文件；
2. 执行 `next` 创建 remote reservation；
3. 另一独立 clone fetch 该 reservation ref；
4. 验证 reservation parent 等于 `origin/main`；
5. 验证 reservation tree 等于 `origin/main^{tree}`；
6. sentinel 文件不在 reservation tree；
7. sentinel commit object 在另一 clone 中不可访问，且不是 reservation ancestor；
8. local reservation metadata 仍记录 requesting HEAD、`base_ref=origin/main` 与 exact base OID；
9. token release 成功且没有 remote/local reservation 残留。

## Validation

- Task tests：**23/23 passed**；原 22 项全部通过。
- Memory tests：**35/35 passed**；最终模式 `ASSISTED`。
- PowerShell 5.1：Python compile、23 fixtures、真实 scan、真实 validate、incident repair 全部 PASS。
- 真实 Registry：8 canonical、2 companion、1 Candidate、5 Review、0 collision。
- Registry 与 latest `origin/main@f8a9ab0` 一致。
- 真实 origin 未创建 `task-reservations/TASK-*` ref；sentinel 验证只使用 disposable bare origin。

## Updated Artifacts

- `tools/tasks/task_cli.py`
- `tools/tasks/tests/test_task_cli.py`
- `tools/tasks/README.md`
- `tasks/TASK-0020-Task-Allocation-and-Namespace-Governance.md`
- `tasks/TASK_REGISTRY.yaml`
- `docs/adr/ADR-0006-Task-Identity-and-Allocation.md`
- `CHANGELOG.md`
- `CONTEXT_MANIFEST.yaml`
- `bootstrap/chatgpt/generated/PROJECT_SOURCE_PACK.md`
- `bootstrap/chatgpt/generated/PROJECT_SOURCE_REPLACEMENT_LIST.md`

Project Source replacement 状态保持 `manual upload required`；未自动操作 ChatGPT Project、浏览器或任何外部文档系统。

## Safety and Boundaries

- 未执行或晋升 Cash Frenzy Candidate。
- 未修改 TASK-0021。
- 本轮没有修改 Huuuge、Lottery、Capture、document-assistant、飞书、SVN 或其他业务仓库；仅同步了已在 main 的既有提交。
- 未读取 Raw Capture、账号、Secret、完整响应或私有 Registry。
- Memory 保持 `ASSISTED`；Hook / AUTO 未激活。
- Subagents: none。


<!-- MEMORY-REFRESH:START -->
## Memory Context Refresh

- Generated: 2026-08-27T08:31:10Z
- Effective mode: `ASSISTED`
- Manifest: `CONTEXT_MANIFEST.yaml`
- ChatGPT Project Sources: `manual upload required`
- Private repositories: not read unless explicitly registered and authorized
<!-- MEMORY-REFRESH:END -->
## Exact Next Action

ChatGPT Review Round 3：仅复核 reservation commit 的 `origin/main` parent/tree 隔离、跨 clone sentinel 回归与完整无退化证据。返回 `Accepted` 或具体 `Needs changes`。Review 前不执行 Cash Frenzy Candidate。
