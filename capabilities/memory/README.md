# Memory Capability

- ID: `CAP-MEM`
- Status: Registered / Waiting for ChatGPT Review
- Scope: Shared governance capability consumed by Game Design projects
- Contract owner: ChatGPT
- Implementation owner: Codex / current Host
- Related task: [`TASK-0016`](../../tasks/TASK-0016-Automatic-Cross-Conversation-Memory-Curation.md)
- Related ADR: [`ADR-0005`](../../docs/adr/ADR-0005-Git-Backed-Automatic-Memory.md)

## Outcome

Memory Capability 将不同对话、Agent 和团队成员产生的长期有效规则、决定、事实、Solution、Skill、Workflow、状态与失败经验，转换为可审计、可路由、可 Review、可撤销的 Memory Candidate，并在策略允许时整理到 Git canonical destination。

本契约不把完整聊天、Host 私有 memory store、模型上下文或 Raw 数据定义为长期真相源。Git 与对应业务仓库仍是 canonical source。

## Operations

| Operation ID | Outcome | Class | Required input | Success evidence |
| --- | --- | --- | --- | --- |
| `CAP-MEM-CAPTURE` | 生成结构化 Candidate 或安全 Outbox event | WRITE | 摘要、来源、scope、sensitivity、evidence | Candidate/Outbox ID、目标路径和路由结果 |
| `CAP-MEM-VALIDATE` | 验证 schema、安全、scope、去重与目标路径 | READ | Candidate | validation report；失败原因不泄露 Secret |
| `CAP-MEM-CURATE` | 晋升、Review、Archive 或 Reject Candidate | WRITE | 已验证 Candidate、mode、policy | 目标文件、index 与原 Candidate 状态一致；无静默覆盖 |
| `CAP-MEM-REFRESH` | 刷新 Manifest、Current State 与 Source Pack | WRITE | Workspace Git state | manifest、hash、替换清单和检查报告 |
| `CAP-MEM-STATUS` | 查看有效 mode、队列和上次结果 | READ | repository/state directory | OFF/ASSISTED/AUTO、计数和本机 Outbox 位置 |
| `CAP-MEM-SET-MODE` | 切换 Host-local kill switch | WRITE | `Off` / `Assisted` / `Auto` | 回读 mode 一致；OFF 不产生 Candidate |

## Inputs and Outputs

Candidate 至少包含 schema version、`memory_id`、type、scope、sensitivity、source host/project/actor/reference、Task/commit、scores、confidence、summary、evidence、constraints、normalized key、fingerprint、supersedes 和 canonical destination。

输出状态固定为：`captured`、`promoted`、`review`、`rejected`、`local-only`、`failed`，并可附 `duplicate`、`conflict`、`manual upload required` 等原因。

## Safety Contract

1. Public repository 只接受 `scope=public` 且 `sensitivity=public` 的 Candidate。
2. Project Private 写对应私有业务仓库；没有批准 writer 时进入本机 Outbox。
3. Cross-project Private 在 User 批准私有 Context Hub 前只进入本机 Outbox。
4. Local-only、Secret、Raw Capture、账号数据、逐笔余额、完整响应和敏感日志不得上传。
5. scope 或 sensitivity 不明确时 fail closed，不写公共仓库。
6. 单个 Agent 不静默覆盖 canonical file；冲突进入 Review，历史通过 `supersedes` 保留。
7. Core Rule、ADR、Capability、权限、费用和跨项目策略在 AUTO 中仍必须 Review。

## Current Implementation Binding

| Operation | Provider | Binding |
| --- | --- | --- |
| Capture / Validate / Curate / Refresh / Status / Set mode | AI-Workspace reference implementation | `tools/memory/memory_cli.py` + PowerShell entrypoints |
| Codex source-side capture | Codex native lifecycle + checked-in policy | `bootstrap/codex/` and disabled hook template |
| ChatGPT source-side capture | Project Instructions + Outbox handoff | `bootstrap/chatgpt/` |
| Generic IDE Agent | project rule + local CLI | `bootstrap/generic-agent/` |

当前实现不包含常驻服务、外部 SaaS、向量数据库、图数据库、浏览器抓取或高权限 GitHub App。实际 Host 没有 Python/Git writer 时报告 `Implementation unavailable` 或写标准 Outbox，不声称已提交。

## Failure Semantics

| Condition | Result |
| --- | --- |
| OFF | `rejected/suppressed`；不写 Candidate |
| Secret / private content targeting public Git | sanitized `local-only` Outbox；公共路径无写入 |
| Schema / destination invalid | `failed` 或 `review`；不晋升 |
| Duplicate | `rejected/duplicate`；不静默删除既有 canonical |
| Conflict | `review/conflict`；保留双方 provenance |
| Git/permission/write failure | sanitized Outbox + `failed`；不得声称上传成功 |
| Context Source 无安全自动替换 API | 生成替换清单并报告 `manual upload required` |

## Success Evidence

- OFF / ASSISTED / AUTO 隔离测试；
- Public / Private / Local-only、Secret、dedup、conflict、concurrency 与 rollback 测试；
- ChatGPT、Codex、Generic Agent 三种 Pilot；
- Manifest、Current State、Source Pack 和替换清单可重复生成；
- Git diff、commit、Task、CHANGELOG 和 Handoff 可复查。
