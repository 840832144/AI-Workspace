# ADR-0006: Task Identity and Allocation

- Status: Proposed / Waiting for ChatGPT Review
- Date: 2026-08-27
- Decision owners: User / ChatGPT
- Executor: Codex
- Related Task: [`TASK-0020`](../../tasks/TASK-0020-Task-Allocation-and-Namespace-Governance.md)
- Related Incident: [`INCIDENT-0001`](../incidents/INCIDENT-0001-DUPLICATE-TASK-ID.md)
- Supersedes: none

## Context

AI-Workspace 是跨游戏、跨项目的治理控制面。历史 Task 已经广泛使用全局 `TASK-XXXX` 链接。2026-08-27 曾有两个不同会话在未完整扫描最新 `tasks/` 的情况下，把 Huuuge Lottery 报告与 Cash Frenzy 可行性审计都分配为 `TASK-0018`。

紧急规则已经要求完整目录预检和 fail closed，但人工清单仍不能提供 Registry 漂移、并发 linked worktree、Candidate promotion 和 Git 最新性验证。长期方案必须兼容历史链接，并让 Project 可读性与 canonical identity 分离。

## Decision

采用：

```text
canonical ID = 全局唯一 TASK-XXXX
project_key  = 必填命名空间元数据
human_alias  = 可选的人类可读别名
```

具体规则：

1. `TASK-XXXX` 在 AI-Workspace 根 `tasks/` canonical Task 中全局唯一、不可复用。
2. 新 canonical Task 必须显式记录格式合法的 `Project key`。只有审计白名单 `TASK-0014` 至 `TASK-0019` 可以缺省，并由代码内有限 grandfather map 提供固定值；禁止按标题或路径为未来 Task 推断。
3. `human_alias` 只改善阅读，例如 `CF-FEASIBILITY-001`；它不参与 canonical 链接或唯一性判断。
4. Markdown Task 是真相源。`tasks/TASK_REGISTRY.yaml` 由完整扫描重建并做 byte-for-byte 漂移验证，不可手工作为第二真相源。
5. 根目录文件默认按 canonical 严格解析；只有显式 `Kind: companion` 才能分类为 companion。companion 必须引用当前存在且 ID 与自身文件名一致的 canonical 文件。
6. 历史 `TASK-0016-EXECUTION-AUTHORIZATION.md` 作为 companion；Cancelled Cash Frenzy collision stub 增加显式 `Kind: companion` 并保留旧链接，不静默改指新的 Cash Frenzy Task。
7. 未获 User 明确批准的新方向使用 `CANDIDATE-YYYYMMDD-<PROJECT>-<SLUG>`，不占 Task ID且不可执行。
8. `next` 与所有 allocation 写操作必须完整 scan、validate、fetch `origin/main`，并验证当前是包含最新 main 的 non-main independent linked worktree；main、普通 checkout、stale branch 或无法验证远端时 fail closed。
9. allocator 先用 `refs/heads/task-reservations/TASK-XXXX` 和 `--force-with-lease=<ref>:` 原子创建 remote reservation。Git common-directory lock 与 token-gated local metadata 负责同 clone 串行及生命周期操作；remote ref 的 first-writer CAS 负责不同 clone / Host 排他。
10. Candidate promotion 必须检查 User decision、`Draft / Ready / In Progress / Review / Changes Requested` overlap、分配锁和创建后验证。promotion 成功后 reservation 保持 `pending-main`，不得立即释放。
11. canonical Task 进入最新 `origin/main` 后，创建 reservation 的 linked worktree使用 token 执行 `finalize`；未创建 Task 的放弃场景使用 `release`。`release` 发现本地或 main 已有 canonical 时拒绝，异常路径按 expected OID 删除 remote ref并清理 local metadata。

本 ADR 在 ChatGPT Review 前保持 Proposed；不触发历史大规模重编号。

## Alternatives Considered

### 1. 单一全局连续编号，不增加项目元数据

优点是最兼容现有链接。缺点是跨项目可读性差，也无法稳定表达 ownership、过滤和 alias。它保留了 identity，却没有解决 namespace 可读性。

### 2. 每个游戏/项目独立编号，例如 `CF-TASK-001`

优点是局部清晰。缺点是当前 AI-Workspace 的跨项目链接、聊天话术、Review 与 Handoff 都使用 `TASK-XXXX`；迁移会产生大量重编号、双链接和旧引用漂移。本次事故来自缺少完整分配 gate，不是四位全局空间不足。

### 3. 全局 canonical ID + `project_key` / alias（选择）

保留现有全局链接和时间序列，以结构化项目元数据增强过滤与可读性。新增工具和 Registry 有维护成本，但能以最小迁移代价覆盖 collision、companion、Candidate 和并发需求。

### 4. 外部数据库或中心化分配服务

可提供跨 Host 强锁，但引入账号、权限、部署、可用性和第二真相源。本阶段选择 Git remote reservation refs：沿用现有 origin 权限与原子 ref 更新，不把 Registry 或外部数据库变成第二个 Task 真相源。

## Consequences

### Positive

- 现有 `TASK-XXXX` 链接保持有效，不批量重编号。
- Registry 可从 Markdown 重建，漂移可检测。
- linked worktree 同 clone 以及不同 clone / Host 的并发分配都由 first-writer CAS 排除同号。
- Candidate 不再提前消耗编号，也不会被误当执行入口。
- Project 过滤与 human alias 不再污染 canonical identity。

### Negative / Costs

- grandfather map 中历史 Task 缺少显式 `Project key` 时会产生 warning；白名单变更必须接受治理 Review。
- origin 会暂时存在 `task-reservations/TASK-XXXX` ref；成功 Task 合入 main 后必须显式 finalize，放弃时必须用 token release。
- reservation metadata 与 token 只保存在创建它的 clone；Host 丢失时需人工审计 remote ref，不允许无条件删除。
- 新 Task 创建流程比手工复制模板多一次确定性验证。

## Validation

- duplicate canonical ID、canonical + companion、文件名/标题/Registry 漂移；
- Pending / approved Candidate，以及包含 Draft 的 active scope overlap；
- main/普通 checkout writer gate、同 clone及跨 clone并发 allocator / promotion；
- promotion 未 merge 时继续占号、merge 后 finalize、放弃 release、fault-injection cleanup；
- project_key 缺失/非法/grandfather，malformed canonical 与 companion reference；
- lock conflict、目录不完整、解析失败、非最新 main；
- 当前真实仓库唯一 active canonical TASK-0018；
- Cash Frenzy 完整规格位于 Candidate，Cancelled stub 保持 companion。

证据命令与结果记录在 [`handoff/CODEX.md`](../../handoff/CODEX.md)。

## Follow-up

ChatGPT Review 本 ADR 与 TASK-0020。Accepted 后，新 Task 使用显式 `Project key` 和 allocator；Cash Frenzy Candidate 是否晋升、分配哪个 ID、何时执行，仍由 User 单独决定。
