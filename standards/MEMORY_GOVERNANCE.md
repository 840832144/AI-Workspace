# Memory Governance Standard

- Status: Proposed / Waiting for ChatGPT Review
- Version: 1.1
- Date: 2026-08-27
- Scope: Game Planner AI Workspace 与登记的游戏项目
- Source: TASK-0016 / ADR-0005

## Capture

Host 在完成实质讨论、Task、Review 或 Handoff 时执行 Memory Check。只有长期有效、可复用、有来源且不属于调试噪声的内容进入 Candidate。完整聊天、无证据推测、重复内容和临时偏好不捕获。

所有自动捕获先生成 Candidate；任何 Host-local memory 或模型输出都不能直接成为 canonical truth。

## Scope Routing

| Scope | Destination |
| --- | --- |
| Public / Global | 通过 Public-safe gate 后进入 AI-Workspace `memory/inbox/` |
| Project Private | 对应私有项目 repository；没有批准 writer 时进入本机 Outbox |
| Cross-project Private | 已批准私有 Context Hub；不存在时进入本机 Outbox |
| Local only | 受控本机；只保存最少、脱敏记录 |
| Unknown | Review / Outbox；禁止写公共 Git |

公共仓库中的 `internal`、`confidential`、`secret` 或 `unknown` sensitivity 一律 fail closed。

### Repository classification and approved destination

Git 写入目标必须先分类：

| Classification | Allowed scope | Purpose |
| --- | --- | --- |
| `public-control-plane` | `public/public` | 当前 AI-Workspace；禁止承载私有 Candidate |
| `project-private` | `project-private` + Registry 批准 sensitivity | 单个批准游戏项目的私有 Git repository |
| `cross-project-private-hub` | `cross-project-private` + Registry 批准 sensitivity | User 明确批准的跨项目私有 Context Hub |

Private writer 只信任 Host-local `repositories.json`。条目必须唯一匹配 `repository_alias`，并同时满足 `enabled=true`、`writer_enabled=true`、classification、`allowed_scopes`、`allowed_sensitivities`、`allowed_source_projects`、绝对 Git root path；目标必须位于 public control-plane repository 之外。任一条件缺失或冲突时进入 sanitized Outbox，不尝试猜测或降级写公共 Git。Registry 路径、仓库细节和私有内容不得写入公共 Manifest。

Registry 只能进一步收紧 Global Safety Contract，不能放宽它。无论 Registry 如何配置，`sensitivity=secret` 与 `scope=local-only` 都在读取 Registry 前进入本机 Outbox；声明为 Secret 的正文和来源字段在 Outbox 中整体抑制，避免未被 pattern 识别的 literal 泄漏。

### Git provenance gate

所有进入 Git 的 Candidate 必须提供稳定、可复查的 `source_host`、`source_project`、`source_actor_alias` 和 `source_reference`。空值以及 `unknown`、`n/a`、`none`、`null`、`-`、`tbd` 等占位值无效；CLI、Event file 与 Generic Agent 入口均在写 Git 前转入 Outbox。Local-only / route-required Outbox 可以保留最小缺失说明，但不得因此伪造 provenance。

## Validation Order

1. Schema 与必填字段；
2. Secret 与禁止内容扫描；
3. scope/sensitivity/public-safe；
4. normalized key 与 fingerprint；
5. deterministic duplicate；
6. canonical destination allowlist 与路径穿越；
7. evidence/confidence/score policy；
8. conflict 与 supersede；
9. mode 和 promotion policy。

模型相似度可作为未来 Review 提示，不能单独删除、合并或晋升。

## Modes

- `OFF`：不生成 Candidate；手动命令也返回 suppressed，除非 User 先切换模式。
- `ASSISTED`：安全 Candidate 进入 Inbox，Curator 将其送入 Review；这是 Pilot 后默认模式。
- `AUTO`：仅 allowlist 内、高置信、高证据、Public-safe、目标明确且无冲突的内容自动晋升。其他内容仍进入 Review。

Mode 是 Host-local kill switch。仓库保存默认值，Host 可在本机 state directory 覆盖；切回 OFF 必须立即对后续 capture 生效。

## Auto-promotion Allowlist

允许：

- 新建且目标不存在的 Public-safe Solution record；
- 纯 index、manifest、Context Pack refresh；
- 经明确 Review 接受并带 evidence/commit 的低风险记录。

始终 Review：

- Core Rule、Standard、RFC、ADR、Capability contract；
- 已存在 canonical file 的修改；
- 架构、跨项目策略、权限、费用、发布或不可逆决定；
- conflict、scope/sensitivity 不明确或证据不足。

## Concurrency and Rollback

- 写操作获取 repository-local exclusive lock；锁存在且未过期时 fail closed。
- AUTO canonical promotion 只允许在非 `main/master` 的独立 linked worktree 中运行；开始时工作树只能包含允许的 `memory/inbox/` Candidate，branch、HEAD 或其他 Git status 在事务中变化即失败。
- canonical write 使用临时文件 + atomic replace；目标已存在时不覆盖。
- canonical target、原 Candidate、Archive 和 index 构成一个 promotion transaction。任一步失败都按执行前字节快照恢复四者，并且 `promoted=0`；回滚本身失败时写 Host-local recovery record，存在未解决 recovery record 时禁止后续 AUTO promotion。
- Promotion 成功后 Candidate 保留在 Archive，index 记录 provenance、目标和 fingerprint。
- 历史记录通过 commit/revert、Archive 与 `supersedes` 恢复，不重写旧 ADR。

## Secret Handling

扫描匹配只记录 category，不回显 value。命中内容在任何 Outbox record 中都必须 redact。Secret、token、私钥、Authorization header、完整 session transcript、Raw Capture 和账号数据不得进入 Git。

## Context Refresh

Refresh 只读取批准范围内的 versioned public-safe 文件。私有仓库必须由显式 registry 与授权启用；默认不读取。生成物包含 hash manifest、Current State managed block、Project Source Pack 和替换清单，并明确输出 `memory/context/WORKSPACE.md` 的路径、SHA-256 与读取时 Git HEAD。没有安全 API 时固定报告 `manual upload required`。

## Workspace Memory read view

`memory/context/WORKSPACE.md` 是跨会话唯一 public-safe 长期记忆读入口。记录必须有稳定 key、状态、摘要、scope、source reference、关联 Task/Review/commit、生效日期和 supersedes。只有高分、高置信、有 evidence、无冲突且由已授权 writer 在 ASSISTED 下显式批准的 Candidate 才能由 Curator 写入；普通 ASSISTED curate 仍进入 Review。相同 key 冲突时进入 Review，显式 supersede 才能更新当前记录，并在历史区保留旧来源与时间。

新会话读取遵循 Git-live-first：最新 `main` 的 Workspace Memory 优先，随后读取相关事实来源。Project Source Pack 是 snapshot；Git unavailable 时才能回退并标记 stale。

## Review and Archive

Review record 必须包含原因、evidence、冲突对象、建议动作与 actor。Reject/duplicate/superseded Candidate 进入 Archive 并保留最少 provenance。Review 后对 canonical 的修改仍遵循对应文件的 RFC/ADR/项目规则。
