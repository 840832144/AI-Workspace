# TASK-0018 — AI Workspace 项目全景报告与在线进度看板

- Status: Ready
- Owner: User / ChatGPT
- Executor: Codex
- Priority: P1 / project visibility and governance
- Date: 2026-08-27
- User authorization: User 已明确要求整理整个 AI Workspace，并创建可在线查看的项目进度与能力看板
- Execution repository: `840832144/AI-Workspace`
- Concurrency: TASK-0016 仍可能存在独立 worktree / 未提交修改；TASK-0015 的 Huuuge Capture 由 User 控制。本任务必须使用独立 branch / worktree，不得覆盖、整理或中断其他任务。

## Goal

形成一套面向 User 和策划成员、可长期维护的 AI Workspace 项目说明与状态入口，使 User 能快速了解：

1. 项目为什么立项、解决什么问题；
2. 当前能实现哪些功能，哪些只是部分可用、规划中或受阻；
3. Workspace 的整体架构、核心原则、角色分工、仓库和真相源边界；
4. 当前主线进度、已完成事项、未完成事项、阻塞项和可选支线；
5. 后续如何更新状态，避免报告与 Git、业务仓库长期漂移。

本任务必须交付 Git 版本和飞书在线版本，不能只在聊天中总结。

## Core Decision

本阶段采用：

```text
Git / 受控业务仓库 = 真相源
        ↓ 经过核验的 public-safe 投影
飞书项目全景报告 + 飞书进度与能力看板 = 面向人的在线入口
```

当前 AI Document Assistant 已支持飞书云文档读写、权限和 Markdown 原生表格转换，但电子表格 / Wiki 仍是预留能力。因此本任务优先使用两份飞书云文档和原生表格，不为本任务新增 Sheets、Bitable、多维表格或第三方项目管理依赖。

若 Codex 在执行前确认已有成熟、已授权且更合适的内部在线工具，可提出替代建议，但不得未经 User 同意扩大权限、注册外部服务或改变真相源。

## Mandatory Source Verification

开始写作前必须同步并读取最新状态，不能只依赖 ChatGPT Project 快照：

### AI-Workspace

至少读取：

- `README.md`
- `AI_TEAM.md`
- `ARCHITECTURE.md`
- `ROADMAP.md`
- `CHANGELOG.md`
- `AGENTS.md` 与 Global `~/.codex/AGENTS.md`
- `bootstrap/chatgpt/00_CORE_RULES.md`
- `bootstrap/chatgpt/01_SYSTEM_CONTEXT.md`
- `bootstrap/chatgpt/02_CURRENT_STATE.md`
- `bootstrap/chatgpt/03_NEW_CHAT_BOOTSTRAP.md`
- `docs/architecture/WorkspaceKernel.md`
- `docs/CapabilityModel.md`
- `capabilities/`
- `skills/`、`workflows/`、`standards/`、`templates/`
- `projects/*/STATUS.md`
- `tasks/`、`reviews/`、`handoff/`
- 与 Memory、Subagent、Document Assistant、Huuuge、Workspace Sync、Report Engine 有关的 RFC、ADR、Roadmap 和实验记录

### 实现与运行真相源

只检查 AI-Workspace 已登记或明确引用的仓库 / 受控系统：

- `840832144/huuuge-android-research`
- `840832144/document-assistant`
- AI-Workspace 中实际登记的其他业务仓库（若存在）
- 公司 SVN 中已发布包的非敏感版本信息（仅在已有权限和现成入口下核验）
- AI Document Assistant 的本机 healthcheck、工具清单和文档 Registry

每个“当前可用”结论至少应有一个可复查依据：Task / Status / Handoff / commit / release / test / healthcheck。不得把目录存在、Schema、计划或文档描述直接写成“已实现”。

## Evidence and Status Rules

报告和看板统一使用以下状态：

### Capability Status

- `Available`：已有实现与近期验证，User 当前可使用。
- `Partial`：已有部分能力，但有明确限制、缺少完整流程或仍需人工步骤。
- `Planned`：已有 Roadmap / RFC / Task 候选，但尚未实现。
- `Blocked`：目标明确，但被权限、平台、依赖、验证或外部条件阻塞。
- `Deprecated`：已明确废弃或被替代。

### Work Item Status

沿用 `tasks/README.md`：

- `Draft`
- `Ready`
- `In Progress`
- `Review`
- `Accepted`
- `Changes Requested`
- `Cancelled`

另外，尚未建立正式 Task 的支线只能标记为 `Candidate`，不得写成已排期或已授权。

所有数值、能力成熟度和原因归纳必须区分：

```text
Confirmed / Estimate / Hypothesis / Decision proposal
```

若仓库没有明确记录最初立项原因，可以基于 RFC、ADR、CHANGELOG 和已记录痛点做归纳，但必须标记“基于现有记录归纳”，不能伪造历史原话或时间线。

## Scope

### A. 项目全景报告

在 Git 中创建：

```text
docs/overview/AI_WORKSPACE_PROJECT_OVERVIEW.md
```

报告面向 User 和策划成员，默认中文，不要求读者理解代码。至少包含：

1. 一页式摘要：项目是什么、当前做到哪、下一阶段是什么；
2. 立项背景与核心痛点；
3. 项目目标、目标用户与明确非目标；
4. 当前可实现的功能总览，按 `Available / Partial / Planned / Blocked` 分组；
5. 总体架构：Global Codex、Governance、Execution、Evidence，以及各仓库 / 受控系统关系；
6. 核心能力链路：Collector → Knowledge / Analysis → AI Report Engine → AI Document Assistant；明确哪些已实现、哪些规划中；
7. Capability-first / Reuse-first / Build-last 的核心逻辑；
8. User、ChatGPT、Codex 和其他 Agent 的分工与授权边界；
9. Task、Review、Handoff、Memory、RFC、ADR 的协作方式；
10. Huuuge 研究结构和优先级：Slots → Systems → Events → Others；
11. Evidence Standard、Confirmed / Estimate / Hypothesis / Decision proposal 的使用方法；
12. 多实例 / 多账号数据隔离与脱敏聚合策略；
13. 面向策划的一键安装、一键启动、一键检查、成功表现与失败处理标准；
14. 安全、隐私、Secret、Raw Capture、权限和付费操作边界；
15. 当前限制、已知风险和外部阻塞；
16. Roadmap、近期主线与可选支线；
17. 文档维护方式、真相源和“最后核验时间”；
18. 术语表与常用入口。

不要把底层实现细节堆在主流程中；必要技术内容放在附录或链接到现有文档。

### B. Git 进度与能力看板

在 Git 中创建：

```text
docs/status/AI_WORKSPACE_PROGRESS_DASHBOARD.md
```

如现有仓库已经有更合适的结构化状态文件或生成工具，优先复用；否则可补充一个最小、public-safe 的结构化来源和校验脚本，但不得新增重量依赖或另造第二套 Task 系统。

看板顶部必须显示：

- `As of` 时间；
- AI-Workspace main commit；
- 各实现仓库最后核验 commit；
- 数据来源和“不是实时自动同步”的说明；
- 状态统计摘要。

至少包含以下表格：

#### 1. 当前能力矩阵

字段至少为：

```text
Capability
User Outcome
Domain
Status
What Works Now
Entry / Provider
Evidence / Source
Known Limit
Next Action
Last Verified
```

#### 2. 项目进度

字段至少为：

```text
Work Item / Task
Mainline or Side
Priority
Status
Owner / Executor
Current Result
Blocker
Exact Next Action
Evidence / Source
Last Verified
```

#### 3. 已完成里程碑

按时间或能力域列出已经合入、已验证且仍有效的关键成果，不把仅进入 Review 的内容写成完成。

#### 4. 未完成与阻塞项

明确缺口、阻塞原因、解除条件和下一动作。

#### 5. 可额外开展的支线任务

只收录尚未授权的 `Candidate`，至少写明：价值、依赖、风险、是否影响主线、建议触发条件。不得擅自创建实现、付费或外部发布。

建议覆盖但不局限于：

- AI Report Engine；
- Git → Feishu / SVN Workspace Sync；
- 飞书 Sheets / Bitable Provider；
- Planner Toolkit；
- 多实例独立数据库与跨账号脱敏聚合；
- Huuuge Lottery 后续数值分析与 CR 建议；
- 自动刷新 ChatGPT Project Source Pack；
- 真实策划盲测和 UX 持续优化。

是否列入、当前状态和描述必须以最新仓库证据为准。

### C. 在线交付

通过 `feishu-docs` 执行：

1. 先运行 `feishu_healthcheck`；
2. 使用 `search_documents` 和目标文件夹浏览防止重复创建；
3. 创建或更新两份飞书文档：
   - `《Game Planner AI Workspace｜项目全景说明》`
   - `《Game Planner AI Workspace｜进度与能力看板》`
4. 报告文档对应 A；看板文档对应 B，并使用飞书原生表格；
5. 默认设置为“企业内获得链接的人可编辑”，除非 User 当前权限策略不允许；
6. 写入后必须回读标题、正文关键段落、表格和权限；
7. 在两份文档顶部记录 Git 来源路径、main commit、更新时间和维护说明；
8. 两份文档互相链接，并链接必要的 Git / Feishu 入口；不得链接 Raw Capture、私有 Registry 或敏感日志。

若 healthcheck 失败，仍完成 Git 交付，并在 Handoff 中记录准确错误类型和唯一下一步；不得为绕过问题改用未授权第三方服务。

### D. 维护机制

创建：

```text
docs/status/AI_WORKSPACE_STATUS_MAINTENANCE.md
```

写成策划也能照做的短步骤，说明：

- 什么时候更新：Task 状态变化、能力上线 / 受阻、Roadmap 决策、实现仓库发布、重大风险变化；
- 先更新哪个真相源；
- 如何重新核验 commit、Task、Status、Handoff 和能力；
- 如何更新 Git 看板；
- 如何使用 AI Document Assistant 替换同一篇飞书文档；
- 成功表现；
- 失败怎么办；
- 如何避免重复文档和状态漂移。

本任务只需形成可重复的 ASSISTED 更新流程，不要求实现实时后台同步。自动 Git → Feishu 同步属于独立后续 Task。

## Non-goals

- 不修改 Huuuge Collector、Capture、游戏请求、奖励、余额或服务器状态。
- 不读取、复制或分析 TASK-0015 的 Raw Capture；不提前生成 Lottery 数值结论。
- 不实现 AI Report Engine 的业务生成逻辑。
- 不实现飞书 Sheets、Bitable、Wiki 或新的外部 SaaS 集成。
- 不创建通用项目管理平台，不替代 Task、Status、Handoff 和业务仓库。
- 不把本机未提交代码、未合入 branch 或未经验证的描述计为 `Available / Completed`。
- 不把 ChatGPT Project Memory、聊天或飞书当成实时真相源。
- 不扩大权限、购买服务、付费、发布到公司外部或创建公开敏感页面。

## Safety

- 不写入 Secret、Token、私钥、Authorization Header、账号信息、完整响应、逐笔余额、Raw Capture、私有 Registry、代理节点、敏感日志或本机路径中的个人标识。
- 私有仓库只能记录必要的仓库名、commit 和脱敏结论；不要复制私有源码或原始业务数据到 AI-Workspace / 飞书。
- 外部链接必须检查访问边界；飞书默认企业内可编辑，不对公网开放。
- 所有来源都记录 `last_verified`；无法核验时标记 `Unknown / Blocked`，不得猜测。

## Worktree and Concurrency

使用独立 worktree / branch，例如：

```text
branch: task-0018-workspace-overview
worktree: C:\AI-Workspace-task-0018
```

执行前检查 TASK-0016、TASK-0015 和其他 worktree / branch；不清理、不 stash、不 reset、不提交其他任务的修改。只在自己的 branch 提交，等待 ChatGPT Review 后再合并。

## Validation

至少完成：

1. 检查所有引用路径和链接存在；
2. 检查每项 `Available / Completed` 都有近期证据；
3. 检查 Planned、Blocked、Candidate 没有被写成已实现；
4. 对比 Task header、项目 Status、Handoff 和最新 commit，列出并处理冲突；不能静默选择；
5. 检查飞书文档没有重复创建；
6. 回读两份飞书文档的标题、正文关键内容、表格和权限；
7. 执行仓库已有 Markdown / link / secret scan；没有现成检查时，至少运行 `git diff --check` 和敏感模式扫描；
8. 确认未修改 Huuuge、Document Assistant 或 TASK-0016 的实现文件；
9. 确认 Git 看板与飞书看板具有相同 `As of`、commit 和状态摘要；
10. 由 Codex 给出 8 行以内的 User 阅读指南：先看哪里、如何判断当前状态、如何发起下一任务。

## Acceptance

满足以下条件才可进入 Review：

- Git 中存在全景报告、进度看板和维护说明；
- 项目定位、立项原因、功能、架构、核心逻辑、角色、真相源、安全与 Roadmap 均有清晰说明；
- 看板明确展示当前能力、已完成、未完成 / 阻塞和可选支线；
- 所有状态都有来源和最后核验时间；
- 两份飞书在线文档创建或更新成功、可编辑、已回读、无重复；
- 未越权、未泄密、未触碰 Huuuge Capture 和其他并行任务；
- 结果可由后续 Codex 按维护文档重复更新，而不是一次性报告。

## Completion and Handoff

完成后：

1. 将本 Task 更新为 `Review`；
2. 更新 `CHANGELOG.md`；
3. 更新 `handoff/CODEX.md`，记录 branch、commit、核验仓库与 commit、飞书文档链接、权限状态、已知限制和唯一下一步；
4. 提交并 push 独立 branch；
5. 返回：Git commit、变更文件、两份飞书链接、验证结果、冲突 / 缺口；
6. 等待 ChatGPT Review，不自行合并 `main`。
