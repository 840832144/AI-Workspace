# TASK-0016 Support — Workspace Memory Cross-Session Closure

- Kind: task support
- Canonical task: `tasks/TASK-0016-Automatic-Cross-Conversation-Memory-Curation.md`
- Status: Approved
- User decision: Approved / execute now
- Date: 2026-08-28
- Related review: `reviews/TASK-0016-CHATGPT-REVIEW-2.md`
- Scope relationship: closure of existing TASK-0016 acceptance criteria; no new Task and no second Memory system

## Goal

让不同 ChatGPT、Codex 和 Generic Agent 会话通过最新 Git `main` 读取同一份已确认关键记忆，从而知道其他会话已经形成的长期决定、Accepted 结果、重要失败经验和当前边界。

本收口只解决两个问题：

1. 多个会话产生的高价值信息如何进入统一 Git Memory；
2. 新会话如何确定性读取这些信息。

云文档继续只面向人类阅读和导航，不作为 AI 跨会话记忆真相源。Project Memory 和 Project Sources 只作为辅助召回与离线快照。

## Required Scope

### 1. 单一可读视图

在现有 `memory/` Candidate / Review / Archive 体系上增加一个 public-safe canonical read view：

```text
memory/context/WORKSPACE.md
```

第一阶段只建立这一份文件，不新增图数据库、向量库、网页、Timeline、Dashboard 或多层知识图谱。

`WORKSPACE.md` 只保留以下长期信息：

- User 明确确认的长期决定；
- Accepted Review、已完成 Task 和已启用 Capability 的稳定结论；
- 会影响后续工作的关键 blocker、停止条件和已证伪路线；
- 新会话需要避免重复研究或错误建议的事实。

每条记录至少包含：

```text
key
status
summary
scope
source_reference
related_task / related_review / related_commit
effective_date
supersedes
```

禁止写入完整聊天、Secret、账号、Raw Capture、完整响应、绝对余额、逐笔值、私有 Registry 或敏感日志。

### 2. 多会话汇总

继续复用现有 `Memory Event → Candidate → Validator → Curator` 流程，不新增旁路：

- ChatGPT、Codex、Generic Agent 在实质讨论、User 决定、Task/Review/Handoff 完成后执行现有 Memory Check；
- 具备批准 Git writer 时写 Candidate；无写能力时进入标准 Outbox；
- Curator 仅将高置信、证据充分、public-safe、无冲突的内容写入 `memory/context/WORKSPACE.md`；
- 相同 `key` 去重；新旧结论冲突时进入 Review，禁止静默覆盖；
- Supersede 必须保留原来源和时间；
- Candidate、Review、Archive 仍是过程记录，`WORKSPACE.md` 才是新会话的稳定阅读入口。

ASSISTED 继续作为生产默认模式。不得为了实时性启用 production AUTO、Hook、常驻服务或直接争写 `main`。

### 3. 新会话固定读取

更新 ChatGPT Bootstrap，使新会话按以下顺序读取：

1. Core Rules / System Context / Writing Style；
2. 最新 Git `main` 的 `memory/context/WORKSPACE.md`；
3. 与当前请求相关的最新 Task、Review、Status、Handoff 和业务仓库证据；
4. Git 不可用时才使用 Project Source Pack，并明确可能过期。

`WORKSPACE.md` 不替代 Task、Handoff 或业务实现真相源；它只提供跨会话的长期摘要和检索入口。

### 4. Context Refresh

扩展现有 `Refresh-ProjectContext`：

- 将 `memory/context/WORKSPACE.md` 纳入 `CONTEXT_MANIFEST.yaml` 和 ChatGPT Source Pack；
- 输出该文件的路径、hash 和生成时读取的 Git HEAD；
- Git live read 优先，Project Sources 仍明确为 snapshot / manual upload required；
- 不读取未授权私有仓库，不把私有内容复制到公共 read view。

### 5. 最小 Seed 与 Pilot

只用 public-safe、可复查来源初始化和测试，不增加研究范围。至少覆盖三个独立来源：

1. User 决定：Git Memory 是 AI 跨会话长期真相源；云文档主要给人看；
2. TASK-0024 Accepted：Cash Frenzy 已恢复 direct inbound Spin result/win/balance 类字段，但 F4 未证明；
3. TASK-0023 Accepted：Product Roadmap 与 Planner Writing Style 已生效。

Pilot 必须证明：

- 三个来源进入同一 read view，且没有重复记录；
- 一个新 ChatGPT 测试会话只读取 Bootstrap、Git Memory、相关 Task/Handoff，即可正确回答上述状态；
- 新会话不会把 F3 写成 F4，也不会建议重复已明确停止的路线；
- 冲突或未 Accepted 的结论不会被写成 canonical memory；
- Source Pack 落后于 Git 时，系统优先使用 Git 并标明 snapshot 过期。

## Existing Review Blockers

本收口不得跳过 `reviews/TASK-0016-CHATGPT-REVIEW-2.md` 的两个安全修复：

1. 所有 documented provenance placeholder，包括 ASCII `-`，必须被确定性拒绝并进入 Outbox；
2. `sensitivity=secret` 与 `scope=local-only` 必须是 Registry 无法放开的 hard deny。

只有这两个修复与本文件的跨会话 read/write 闭环同时通过，TASK-0016 才能进入 ChatGPT Review Round 3。

## Non-goals

- 不保存完整聊天或自动扫描历史全部会话；
- 不建立第二套 Memory Candidate / Curator；
- 不引入外部 SaaS、数据库、向量检索、知识图谱或高权限 GitHub App；
- 不做云文档同步、文档门户、Timeline、Dashboard 或 UI；
- 不启用 production AUTO、WATCH 或常驻 Hook；
- 不访问或修改 Huuuge Raw、Collector、Cash Frenzy Raw、Top Tycoon Raw、CR 私有数据、SVN 或 Document Assistant；
- 不因本收口新建 Task 编号或扩大到 Workspace Sync 其他功能。

## Acceptance

进入 ChatGPT Review Round 3 前必须满足：

1. Round 2 两个安全漏洞已修复并有回归；
2. `memory/context/WORKSPACE.md` 已生成，结构和 provenance 可验证；
3. 三个独立来源的 Seed / Pilot 通过，冲突和未 Accepted 内容未进入 canonical view；
4. ChatGPT Bootstrap、Project Instructions、Memory Capability / Governance 和工具说明统一指向同一 read view；
5. `Refresh-ProjectContext` 将 read view 纳入 Manifest / Source Pack，并保留 Git-live-first 语义；
6. 新会话读取测试通过；
7. 原有 Memory、Task、Context、Registry 和 Workspace Doctor 回归通过；
8. 最终模式保持 `ASSISTED`，Hook / AUTO / WATCH 均未启用；
9. 更新 canonical Task、`CHANGELOG.md` 与 `handoff/CODEX.md`，提交并 push，等待 ChatGPT Review。

## Handoff

Codex 完成后只需返回：

- implementation commit；
- `WORKSPACE.md` 路径与 Seed 条目数；
- 多会话 Pilot 和新会话读取结果；
- Round 2 安全修复结果；
- 回归结果；
- 最终 mode / Hook / AUTO / WATCH 状态；
- `Subagents: <names>` 或 `none`。
