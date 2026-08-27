# Memory Governance Standard

- Status: Proposed / Waiting for ChatGPT Review
- Version: 1.0
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
- 自动 Git writer 只能使用独立 branch/worktree/PR 或等价隔离，不直接并发写共享 `main`。
- canonical write 使用临时文件 + atomic replace；目标已存在时不覆盖。
- Promotion 后 Candidate 保留在 Archive，index 记录 provenance、目标和 fingerprint。
- 历史记录通过 commit/revert、Archive 与 `supersedes` 恢复，不重写旧 ADR。

## Secret Handling

扫描匹配只记录 category，不回显 value。命中内容在任何 Outbox record 中都必须 redact。Secret、token、私钥、Authorization header、完整 session transcript、Raw Capture 和账号数据不得进入 Git。

## Context Refresh

Refresh 只读取批准范围内的 versioned public-safe 文件。私有仓库必须由显式 registry 与授权启用；默认不读取。生成物包含 hash manifest、Current State managed block、Project Source Pack 和替换清单。没有安全 API 时固定报告 `manual upload required`。

## Review and Archive

Review record 必须包含原因、evidence、冲突对象、建议动作与 actor。Reject/duplicate/superseded Candidate 进入 Archive 并保留最少 provenance。Review 后对 canonical 的修改仍遵循对应文件的 RFC/ADR/项目规则。
