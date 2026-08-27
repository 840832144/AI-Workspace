# TASK-0020 — Task Allocation & Namespace Governance

- Status: Review
- Project key: WORKSPACE
- Owner: User / ChatGPT
- Executor: Codex
- Priority: P0 / governance
- Date: 2026-08-27
- Repository: `840832144/AI-Workspace`
- Subagents: none by default; this is a central write-heavy governance task

## Allocation Evidence

本 Task 创建前已从 Git 最新 `main` 完整枚举 `tasks/` 根目录，而不是根据聊天或最大编号猜测。

已确认 canonical / related 文件包括：

```text
TASK-0014-Codex-Subagent-Pilot.md
TASK-0015-Huuuge-Lottery-Live-Numerical-Breakdown.md
TASK-0016-Automatic-Cross-Conversation-Memory-Curation.md
TASK-0016-EXECUTION-AUTHORIZATION.md            # historical companion / needs classification
TASK-0017-Codex-Desktop-Proxy-WebSocket-Reconnect.md
TASK-0018-Huuuge-Lottery-Numerical-Breakdown-Report.md
TASK-0018-Cash-Frenzy-Android-Collector-Feasibility-Audit.md  # erroneous collision, now Cancelled
TASK-0019-AI-Workspace-Overview-and-Separate-Progress-Documents.md
```

`TASK-0020` 在创建时未被占用。创建后必须重新枚举目录并验证唯一性。

## Incident

两个不同会话在没有完成完整目录级编号预检时，先后把新需求分配成已被占用的 `TASK-0018`，导致两个不同 canonical Task 共用同一编号。

已执行紧急止损：

- 先存在的 `TASK-0018-Huuuge-Lottery-Numerical-Breakdown-Report.md` 保持 canonical；
- 误建的 Cash Frenzy 文件已标记 `Cancelled`，完整内容保留在 Git 历史；
- `bootstrap/chatgpt/00_CORE_RULES.md`、`03_NEW_CHAT_BOOTSTRAP.md`、根 `AGENTS.md` 与 `tasks/README.md` 已加入 fail-closed 编号预检规则；
- Cash Frenzy 在本 Task 完成前只是 Candidate，不可执行。

## Goal

建立一套**不会依赖聊天记忆、不会猜编号、能检测并阻断冲突、兼容历史任务**的 Task 分配与命名治理机制。

最终任何 ChatGPT、Codex 或其他 Agent 在创建 Task 前都必须能够确定：

1. 哪些文件是 canonical Task；
2. 哪些 ID 已被占用；
3. 是否已有相同目标或范围重叠的活动 Task；
4. 新需求应继续已有 Task、成为 Candidate、子任务，还是获得新 ID；
5. 创建后如何自动验证没有冲突。

## Required Decision

在 ADR 中比较：

1. 全局连续编号；
2. 游戏/项目命名空间编号；
3. 全局 canonical ID + `project_key` / human alias。

默认推荐并要求优先验证的兼容方案：

```text
canonical ID: 全局唯一 TASK-XXXX
project_key: HUUUGE / CASH-FRENZY / WORKSPACE / DOCUMENT / ...
human_alias: 可选，如 CF-FEASIBILITY-001
```

原因：AI-Workspace 是跨项目控制面，已有大量 `TASK-XXXX` 链接；不应为了本次事故大规模重编号。游戏级 alias 可提升可读性，但不能取代全局 canonical ID。

若 Codex 发现更优方案，可在 ADR 中提出，但不得未经 User / ChatGPT Review 迁移全部历史 Task。

## Scope

### Phase 0 — Safe execution setup

1. 同步最新 `main`，读取：
   - `AGENTS.md`
   - `CONTRIBUTING.md`
   - `tasks/README.md`
   - `handoff/CHATGPT.md`
   - `handoff/CODEX.md`
   - `bootstrap/chatgpt/00_CORE_RULES.md`
   - `bootstrap/chatgpt/03_NEW_CHAT_BOOTSTRAP.md`
   - 当前所有 `tasks/` 文件
2. 使用独立 branch / linked worktree，不覆盖 TASK-0016、TASK-0018 Lottery、TASK-0019 或其他未提交工作。
3. 检查工作树；发现不属于本 Task 的改动时停止并报告。
4. 本任务默认单 Agent；不要为了 Subagent 试验扩大范围。

### Phase 1 — Canonical Task Model

建立明确、机器可验证的 Task schema，至少包含：

```text
id
canonical_file
title
status
project_key
owner
executor
priority
created_date
updated_date
related_tasks
kind = canonical | companion | candidate | review
```

要求：

- 根目录 canonical Task ID 全局唯一；
- 文件名、一级标题和 schema 中的 ID 必须一致；
- companion / authorization / review / experiment 不得被扫描为第二个 canonical Task；
- 历史 companion 文件需要明确迁移或登记策略；
- 不删除 Git 历史，不批量重写已接受 Task。

建议建立：

```text
tasks/TASK_REGISTRY.yaml
```

如果选 JSON/CSV，必须在 ADR 说明原因。Registry 应可由 Task 文件重建，不能成为与文件内容相互矛盾的手工第二真相源。

### Phase 2 — Allocation / Validation Tool

优先复用现有 Python / PowerShell 和仓库惯例；不要引入外部服务或数据库。

实现一个可在 Windows 与 CI 使用的最小工具，例如：

```text
tools/tasks/task_cli.py
bootstrap/tasks/Test-TaskRegistry.ps1
```

至少支持：

```text
scan       # 枚举 canonical / companion / candidate
validate   # 检查重复、格式、状态、Registry 漂移
next       # 在完整 scan 成功后返回下一个可用全局 ID
candidate  # 创建不占正式 ID 的 Candidate 模板
promote    # User 已确认后，把 Candidate 转成唯一 canonical Task
```

要求：

- 重复 canonical ID 时退出非 0，不能返回 next ID；
- 目录读取不完整、解析失败、Git 非最新状态或存在分配锁冲突时 fail closed；
- `next` 不能只做字符串最大值 + 1，必须先完成完整 validate；
- 创建后再次 validate；
- 并发创建需要最小锁或可验证的 compare-and-swap / branch gate，不能让两个会话获得相同 ID；
- 不修改业务仓库、外部系统或用户配置；
- 输出不得包含 Secret、私有路径或无关内容。

### Phase 3 — Candidate Workflow

新增：

```text
tasks/candidates/README.md
```

Candidate 规则：

- 未获 User 明确批准的讨论项不占用 Task ID；
- Candidate 使用不与 Task 冲突的稳定名称，例如 `CANDIDATE-YYYYMMDD-<project>-<slug>.md`；
- 记录目标、项目、建议优先级、依赖、风险、User decision 和来源；
- Promote 时由工具验证相关活动 Task、分配唯一 ID、保留 Candidate provenance，并在成功后标记 migrated；
- Candidate 不是可执行入口。

### Phase 4 — Incident Repair

1. 保持 Huuuge Lottery 文件为 canonical `TASK-0018`。
2. 从 Git 历史恢复误建 Cash Frenzy Task 的完整规格，迁移为：

```text
tasks/candidates/CANDIDATE-20260827-CASH-FRENZY-COLLECTOR-FEASIBILITY.md
```

3. Candidate 标记：User 已确认研究方向，但等待本治理 Task Accepted 后重新分配 canonical ID。
4. 保留当前 Cancelled collision stub，或迁入明确的 incident archive；选择必须在 ADR 说明，且旧链接不能静默指向另一个任务。
5. 审计 `TASK-0016-EXECUTION-AUTHORIZATION.md` 等历史 companion，按新模型登记或迁移，不把它误报为第二个 canonical Task。
6. 生成一份脱敏 incident record：

```text
docs/incidents/INCIDENT-0001-DUPLICATE-TASK-ID.md
```

包含原因、影响、止损、长期修复和回归测试，不保存聊天全文。

### Phase 5 — Governance and Bootstrap Propagation

统一更新：

- `AGENTS.md`
- `CONTRIBUTING.md`
- `tasks/README.md`
- `bootstrap/chatgpt/00_CORE_RULES.md`
- `bootstrap/chatgpt/03_NEW_CHAT_BOOTSTRAP.md`
- 必要的 Architecture / Workflow / ADR Index
- `bootstrap/AGENTS.md`（Codex Global 模板）
- `CHANGELOG.md`
- `handoff/CODEX.md`
- 本 Task 状态

然后重新生成/刷新：

- `bootstrap/chatgpt/generated/PROJECT_SOURCE_PACK.md`
- `bootstrap/chatgpt/generated/PROJECT_SOURCE_REPLACEMENT_LIST.md`
- `CONTEXT_MANIFEST.yaml`
- `bootstrap/chatgpt/02_CURRENT_STATE.md`

Project Sources 仍需人工上传时，明确输出 replacement list；不要假装已自动更新 ChatGPT Project。

### Phase 6 — Tests

必须使用 disposable fixture / temp Git repository 验证，至少覆盖：

1. 两个 canonical 文件使用同一 ID → validate 失败；
2. canonical + companion 同 ID → 正确分类，不误报第二个 Task；
3. 文件名 / 标题 / registry ID 不一致 → 失败；
4. 未确认 Candidate → 不分配 Task ID；
5. Promote 已确认 Candidate → 获得唯一 ID并保留 provenance；
6. 相同目标已有 `Ready / In Progress / Review / Changes Requested` → 警告或阻断，要求明确继续/子任务决策；
7. 两个并发 allocator 请求 → 不能得到相同 ID；
8. 不完整目录、解析错误、Registry 漂移、Git 非最新 → fail closed；
9. 当前真实仓库 scan → 0 个 active canonical ID collision；
10. 误建 Cash Frenzy 内容已进入 Candidate，Huuuge Lottery 仍是唯一 canonical TASK-0018。

如果仓库已有 CI，加入最小 Task validation；如果没有，不为本任务搭建大型 CI，只提供确定性本地命令并在 Handoff 记录。

## Deliverables

```text
tasks/TASK_REGISTRY.yaml              # 或 ADR 批准的等价格式
tasks/candidates/README.md
tasks/candidates/CANDIDATE-20260827-CASH-FRENZY-COLLECTOR-FEASIBILITY.md
tools/tasks/task_cli.py
bootstrap/tasks/Test-TaskRegistry.ps1
docs/adr/ADR-0006-Task-Identity-and-Allocation.md
docs/incidents/INCIDENT-0001-DUPLICATE-TASK-ID.md
```

路径可以因现有仓库结构做最小调整，但能力与证据不可缺失。

## Non-goals

本任务不做：

- 执行 Cash Frenzy、Top Tycoon 或绯闻港口研究；
- 修改 Huuuge Collector 或当前 Lottery 分析；
- 大规模重编号全部历史 Task；
- 建立外部数据库、服务或中心化锁服务；
- 多 Agent 自动调度；
- 自动替换 ChatGPT Project Sources；
- 修改飞书、SVN、业务仓库或私有 Capture；
- 将 Candidate 自动提升为 Ready，绕过 User 决策。

## Safety and Concurrency

- AI-Workspace 是唯一治理真相源；Task allocator 不写业务仓库。
- 不读取 Raw Capture、账号、Secret、完整响应或私有 Registry。
- 不 force push，不覆盖别的 Task worktree，不重写先存在 Task 历史。
- 主 Agent 是唯一写入者。
- 任何不确定分类或冲突均 fail closed。
- TASK-0018 Lottery、TASK-0019 和正在修订的其他任务保持原范围。

## Acceptance Criteria

全部满足才可进入 Review：

1. `TASK-0018-Huuuge-Lottery-Numerical-Breakdown-Report.md` 是唯一 active canonical TASK-0018。
2. Cash Frenzy 完整规格已成为非执行 Candidate，未丢失历史内容。
3. Core Rules、New Chat Bootstrap、Global/Project AGENTS 和 tasks README 使用一致的目录级预检规则。
4. Registry/scan 能正确区分 canonical、companion、candidate 和 review。
5. 重复 ID、格式漂移、并发分配和非最新 Git 状态全部 fail closed。
6. `next` / `promote` 只有在完整 validate 和 User approval 后才成功。
7. 当前仓库通过 validator，active canonical ID collision 为 0。
8. 不进行历史大规模重编号，不破坏现有链接。
9. Incident、ADR、tests、CHANGELOG 和 Handoff 完整。
10. 生成最新 Project Source replacement 状态并明确是否需要人工上传。
11. 提交并推送，等待 ChatGPT Review。

## Validation Commands

Codex 必须在 Handoff 中给出真实命令和输出摘要，例如：

```powershell
python .\tools\tasks\task_cli.py scan
python .\tools\tasks\task_cli.py validate
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\bootstrap\tasks\Test-TaskRegistry.ps1
```

不得虚构 CI 或并发测试结果。

## Handoff Required

Codex 完成后返回：

- Git branch / worktree
- commit SHA
- 最终 Task ID policy
- Registry 与 allocator 使用方法
- 当前 canonical Task 清单与冲突数
- Cash Frenzy Candidate 路径
- 10 类测试结果
- Project Source replacement 状态
- Subagents: none（若确有使用必须解释为何符合单写入者和受限权限）
- 等待 ChatGPT Review，不执行 Cash Frenzy Candidate

## Execution Result — 2026-08-27

- Final policy：全局唯一 `TASK-XXXX` + 必填 `project_key` + 可选 human alias；历史 Task 不批量重编号，ADR-0006 保持 Proposed 等待 Review。
- Registry：`tasks/TASK_REGISTRY.yaml` 由 Markdown 全量扫描确定性重建；当前记录 8 canonical、2 companion、1 Candidate、2 Review，canonical collision 为 0。
- Tooling：标准库 `tools/tasks/task_cli.py` 支持 `scan / validate / next / release / finalize / candidate / promote`；分配写操作要求 latest `origin/main`、non-main independent linked worktree，并使用 common-directory lock + remote Git ref CAS reservation。
- Candidate：Cash Frenzy 完整规格从 `7f6d9a5` 恢复到 `tasks/candidates/CANDIDATE-20260827-CASH-FRENZY-COLLECTOR-FEASIBILITY.md`，当前 User decision 为条件性确认，工具不能晋升。
- Incident：保留 Cancelled collision stub 并显式分类为 companion；Huuuge Lottery 是唯一 canonical TASK-0018。
- Tests：首轮 14/14 disposable Git tests 与 Windows PowerShell 5.1 一键入口通过；Review Round 1 后扩展为 22 项，覆盖 writer gate、reservation 生命周期、跨 clone/Host、project_key、Draft overlap、companion 和 fault injection。
- Concurrency evidence：两个同时运行的 allocator 在同一 clone 返回不同 ID；真实执行期间 `origin/main` 新增 TASK-0021 后，latest-main gate 阻断 Registry 写入，重新同步后 TASK-0021 被纳入 Registry。
- Project Sources：Source Pack、Manifest、Current State 和 replacement list 已刷新；当前仍需人工替换，未自动上传。
- Boundaries：未执行 Cash Frenzy；未修改 Huuuge Collector、Lottery、Capture、document-assistant、飞书、SVN、业务仓库或本机 Global runtime。
- Subagents: none。
- Branch: `codex/task-0020-namespace-governance`；提交与 push 结果见最终 Codex Handoff / Review 交付。
- Implementation commit: `126adcf3e04a20bdc43833f9fc6a65eb27375012`。

## Review Fix Round 1 — 2026-08-27

ChatGPT Review 1 的五项 Required Fix 已全部实施，状态保持 `Review`：

1. `next`、`release`、`finalize`、`candidate`、`promote` 与 Registry 写入统一要求 latest `origin/main`、non-main independent linked worktree；main 和普通 checkout fail closed。
2. `next` / `promote` 先原子创建 `refs/heads/task-reservations/TASK-XXXX`。promotion 成功后保持 `pending-main`，canonical 进入 main 后才用 token `finalize`；未创建 Task 的放弃才 `release`。
3. remote ref 使用 `--force-with-lease=<ref>:` first-writer CAS，不同 clone / Host 的后到者在创建 Task 前冲突并改取下一 ID；同 clone 仍使用 common-directory lock。
4. 新 canonical 缩紧为显式合法 `project_key`；只有有限审计 map 中的 `TASK-0014` 至 `TASK-0019` 可缺省。未来 ID 不再按标题或路径推断。
5. `Draft` 纳入 active overlap。root Task 默认按 canonical 严格解析；只有显式 `Kind: companion` 且 reference 指向存在、同 ID canonical 时才分类为 companion。

针对性回归包括 main/普通 checkout、受支持 next+release、同 clone与跨 clone并发 next、跨 clone并发 promote、promote→pre-merge next→main→finalize、提前 release 拒绝、fault-injection remote cleanup、project_key 三类、Draft overlap 及四类 malformed companion。原 14 项 Task 测试与 35 项 Memory 测试必须在最终 Handoff 中给出不退化证据。

边界未变化：不执行或晋升 Cash Frenzy Candidate；不修改 TASK-0021、Huuuge Collector、Lottery、Capture、飞书、SVN、document-assistant 或其他业务仓库；Memory 保持 `ASSISTED`；`Subagents: none`。
