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
2. 新 canonical Task 必须显式记录 `Project key`；历史 Task 不批量重写，由确定性 legacy inference 生成 Registry，并输出 warning，后续发生实质修改时再补齐。
3. `human_alias` 只改善阅读，例如 `CF-FEASIBILITY-001`；它不参与 canonical 链接或唯一性判断。
4. Markdown Task 是真相源。`tasks/TASK_REGISTRY.yaml` 由完整扫描重建并做 byte-for-byte 漂移验证，不可手工作为第二真相源。
5. 根目录文件由一级标题和显式 `Kind` 分类。canonical、companion、candidate、review 可以关联同一 Task ID，但只有 `kind=canonical` 占用全局 ID。
6. 历史 `TASK-0016-EXECUTION-AUTHORIZATION.md` 作为 companion；Cancelled Cash Frenzy collision stub 增加显式 `Kind: companion` 并保留旧链接，不静默改指新的 Cash Frenzy Task。
7. 未获 User 明确批准的新方向使用 `CANDIDATE-YYYYMMDD-<PROJECT>-<SLUG>`，不占 Task ID且不可执行。
8. `next` 必须完整 scan、validate、fetch `origin/main` 并验证当前非 main linked worktree 包含最新 main，然后在 Git common directory 原子保留 ID。它不是只读的 `max + 1` 猜测。
9. Candidate promotion 必须检查 User decision、active scope overlap、分配锁和创建后验证。继续已有 Task 不分配新 ID；明确子任务才可关联晋升。
10. 不同 clone/Host 没有中心化 reservation；push、Review 和 merge gate 必须重新验证最新 main。若同号仍由不同 Host 产生，后到分支 fail closed，先进入 main 的 canonical Task 保留。

本 ADR 在 ChatGPT Review 前保持 Proposed；不触发历史大规模重编号。

## Alternatives Considered

### 1. 单一全局连续编号，不增加项目元数据

优点是最兼容现有链接。缺点是跨项目可读性差，也无法稳定表达 ownership、过滤和 alias。它保留了 identity，却没有解决 namespace 可读性。

### 2. 每个游戏/项目独立编号，例如 `CF-TASK-001`

优点是局部清晰。缺点是当前 AI-Workspace 的跨项目链接、聊天话术、Review 与 Handoff 都使用 `TASK-XXXX`；迁移会产生大量重编号、双链接和旧引用漂移。本次事故来自缺少完整分配 gate，不是四位全局空间不足。

### 3. 全局 canonical ID + `project_key` / alias（选择）

保留现有全局链接和时间序列，以结构化项目元数据增强过滤与可读性。新增工具和 Registry 有维护成本，但能以最小迁移代价覆盖 collision、companion、Candidate 和并发需求。

### 4. 外部数据库或中心化分配服务

可提供跨 Host 强锁，但引入账号、权限、部署、可用性和第二真相源。本阶段规模不需要；Git branch/Review gate 与本地 CAS 足够暴露冲突并 fail closed。

## Consequences

### Positive

- 现有 `TASK-XXXX` 链接保持有效，不批量重编号。
- Registry 可从 Markdown 重建，漂移可检测。
- linked worktree 同 clone 并发分配不会得到同一 ID。
- Candidate 不再提前消耗编号，也不会被误当执行入口。
- Project 过滤与 human alias 不再污染 canonical identity。

### Negative / Costs

- 历史 Task 缺少显式 `Project key` 时会产生 legacy warning。
- 不同 clone/Host 仍需依赖最新 main、push 冲突和 Review gate，不能宣称有全局中心锁。
- `next` 会产生 Host-local reservation；放弃编号时必须用 token 释放。
- 新 Task 创建流程比手工复制模板多一次确定性验证。

## Validation

- duplicate canonical ID、canonical + companion、文件名/标题/Registry 漂移；
- Pending / approved Candidate 和 active scope overlap；
- 并发 allocator、lock conflict、目录不完整、解析失败、非最新 main；
- 当前真实仓库唯一 active canonical TASK-0018；
- Cash Frenzy 完整规格位于 Candidate，Cancelled stub 保持 companion。

证据命令与结果记录在 [`handoff/CODEX.md`](../../handoff/CODEX.md)。

## Follow-up

ChatGPT Review 本 ADR 与 TASK-0020。Accepted 后，新 Task 使用显式 `Project key` 和 allocator；Cash Frenzy Candidate 是否晋升、分配哪个 ID、何时执行，仍由 User 单独决定。
