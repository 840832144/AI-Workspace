# TASK-0019 — AI Workspace 项目全景说明与独立进度文档

- Status: Review
- Owner: User / ChatGPT
- Executor: Codex
- Priority: P1 / project visibility and long-term governance
- Date: 2026-08-27
- User authorization: User 已确认继续执行，并明确要求最终交付为两个独立文档，项目进度不得混入项目全景说明
- Execution repository: `840832144/AI-Workspace`
- Online provider: AI Document Assistant / `feishu-docs`
- Updated: 2026-08-29
- Review state: Round 1 修订完成；等待 Round 2

## Goal

为整个 Game Planner AI Workspace 建立两份职责清晰、可长期维护、面向 User 与策划成员的正式文档：

1. **项目全景说明**：回答“为什么立项、要解决什么问题、整体能做什么、采用什么架构和核心逻辑”。
2. **项目进度与能力状态**：回答“当前做到哪一步、现在能用什么、哪些已完成 / 未完成 / 受阻、还可以开展哪些支线”。

两份文档必须完全分开，不合并成一篇大报告。Git 保存可审计源稿，飞书提供在线阅读和协作入口。

## Core Document Boundary

### 文档一：项目全景说明（相对稳定）

描述项目的长期定位、立项原因、能力蓝图、整体架构、核心设计框架、协作逻辑、真相源、安全边界和发展方向。

不得放入：

- 当前 Task 明细表；
- 已完成 / 未完成任务列表；
- 当前阻塞项清单；
- 每个能力的实时成熟度；
- 每周或每日进度更新。

可以在开头提供一条“最新进度请查看文档二”的链接，但不得复制进度正文。

### 文档二：项目进度与能力状态（持续更新）

集中保存所有动态状态：

- 当前可用、部分可用、规划中、受阻的能力；
- 已完成、进行中、待开始、待 Review 和阻塞任务；
- 主线与支线；
- 近期里程碑、风险、依赖和精确下一步；
- 可额外开展但尚未授权的候选任务。

该文档不重复讲完整立项背景和架构，只保留三至五行项目说明并链接文档一。

## Truth Source Model

```text
AI-Workspace / 业务仓库 / 受控系统 = 真相源
                     ↓ 核验、脱敏、整理
Git 两份源稿 = 可审计版本
                     ↓ AI Document Assistant
飞书两份正式文档 = 面向人的在线入口
```

- AI-Workspace：治理、Capability、规则、Task、项目控制面、Review 与 Handoff。
- 业务仓库：业务代码、实现、测试、运行证据和发布状态。
- 飞书：正式说明和在线状态展示，不替代 Git 与业务仓库。
- ChatGPT Project Sources / Memory：上下文快照，不是实时状态源。

## Required Source Verification

开始写作前先同步最新 `main`，不得只使用聊天或 Project Source 快照。

### AI-Workspace 至少读取

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
- `skills/`
- `workflows/`
- `standards/`
- `templates/`
- `projects/*/STATUS.md`
- `tasks/README.md` 与全部当前 Task header
- `reviews/`
- `handoff/CHATGPT.md`
- `handoff/CODEX.md`
- 与 Memory、Subagent、Document Assistant、Huuuge、Report Engine、Workspace Sync 相关的 RFC、ADR、Roadmap 与实验记录

### 实现与运行真相源至少核验

- `840832144/huuuge-android-research`
- `840832144/document-assistant`
- AI-Workspace 当前登记的其他业务仓库（若存在）
- 公司 SVN 已发布包的非敏感版本信息（仅使用现有授权和现成入口）
- AI Document Assistant 的 `feishu_healthcheck`、工具清单和本机 Registry 搜索结果

每个“当前已可用”或“已经完成”的结论，至少附一项可复查依据：

```text
Task / Status / Handoff / Accepted Review / main commit / release / test / healthcheck
```

目录存在、Schema、Roadmap、RFC、未合入 branch 或聊天描述，均不能单独证明能力已经可用。

## Status Vocabulary

### Capability Status

- `Available`：已有实现与近期验证，User 当前可以使用。
- `Partial`：已有部分能力，但存在明确限制、人工步骤或未闭环环节。
- `Planned`：已有 Roadmap、RFC 或候选方向，但尚未实现。
- `Blocked`：目标明确，但受权限、平台、依赖或验证条件阻塞。
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

尚未创建正式 Task 的支线只标记为 `Candidate`，不得写成已经排期或获得授权。

所有结论继续区分：

```text
Confirmed / Estimate / Hypothesis / Decision proposal
```

若历史文件没有直接记录最初立项原因，可以根据 RFC、ADR、CHANGELOG、任务和已记录痛点进行归纳，但必须注明“基于现有项目记录归纳”，不得伪造 User 原话、日期或决策过程。

## Deliverable 1 — 项目全景说明

### Git 源稿

```text
docs/overview/AI_WORKSPACE_PROJECT_OVERVIEW.md
```

### 飞书标题

```text
《Game Planner AI Workspace｜项目全景说明》
```

### 内容要求

面向不阅读代码的策划成员，默认中文，先给结论，再逐层展开。至少包含：

1. **一页式项目说明**：项目是什么、为谁服务、核心价值是什么。
2. **立项背景**：长期项目上下文易丢失、重复开发、工具分散、研究证据不可追溯、报告与实现脱节、策划部署门槛高等已记录问题。
3. **项目目标与非目标**：明确 Workspace 是游戏策划 AI 工作台，不是通用 Agent 平台，也不直接承载所有业务实现。
4. **目标用户与典型场景**：玩法、数值、系统、活动策划及数据分析场景。
5. **能力蓝图**：说明系统计划提供哪些稳定结果，不在此处标记实时成熟度。至少覆盖：
   - 需求与研究任务治理；
   - Capability / Skill / Workflow 发现与复用；
   - 游戏证据采集；
   - Knowledge / Analysis；
   - 数值与机制拆解；
   - AI Report Engine；
   - AI Document Assistant；
   - Task / Review / Handoff；
   - Git-backed Memory 与跨对话上下文；
   - Planner-facing 安装、启动、检查和交付；
   - 多项目、多游戏和多实例扩展。
6. **总体架构**：清楚解释 Global Codex Layer、Governance Plane、Execution Plane、Evidence Plane，以及 AI-Workspace、业务仓库、飞书和 SVN 的关系。
7. **核心能力链路**：

   ```text
   Collector → Evidence → Knowledge / Analysis → AI Report Engine → AI Document Assistant
   ```

   说明每层职责，明确 Collector、Analysis、Report、Document 彼此解耦。
8. **设计框架与核心逻辑**：Capability-first、Reuse-first、Build-last、provider-neutral contract、Implementation Binding、证据驱动、最小权限、可回滚和可交接。
9. **核心对象关系**：Capability、Skill、Workflow、Tool、Template、Task、RFC、ADR、Review、Handoff、Memory、Project Control Plane。
10. **角色分工**：User、ChatGPT、Codex、只读 Subagent 与其他 AI 的职责、决策权和写入边界。
11. **Huuuge 作为首个业务落地案例**：简要说明研究优先级 `Slots → Systems → Events → Others`，以及 Slots、Systems、Events、Others 的研究范围；不要把整篇报告变成 Huuuge 专项报告。
12. **研究与证据原则**：L0–L4、Schema / Config / Runtime / UI / Manual、Confirmed / Estimate / Hypothesis / Decision proposal。
13. **多实例与多账号策略**：独立数据库、单账号先分析、脱敏聚合后跨账号比较，Raw 数据不直接混合。
14. **策划体验标准**：一键安装、一键启动、一键检查；每一步写清“做什么、成功表现、失败怎么办”。
15. **真相源与文档生命周期**：什么内容放 AI-Workspace，什么内容放业务仓库、SVN、飞书和本机受控环境。
16. **安全与授权边界**：Secret、账号、Raw Capture、完整响应、付费、权限扩大、外部发布和不可逆操作。
17. **长期演进方向**：只描述稳定方向和架构扩展点，不写当前完成百分比和实时 Task 状态。
18. **术语表与入口索引**：链接文档二、核心 Git 文档和已批准的在线入口。

### 文档一验收重点

- User 单独阅读本文即可理解项目为何存在、整体能做什么、架构如何组织、核心设计逻辑和安全边界。
- 不出现实时任务列表和详细项目进度。
- 任何当前状态信息只允许用一句话链接到文档二。

## Deliverable 2 — 项目进度与能力状态

### Git 源稿

```text
docs/status/AI_WORKSPACE_PROJECT_PROGRESS.md
```

### 飞书标题

```text
《Game Planner AI Workspace｜项目进度与能力状态》
```

### 内容要求

这是唯一的在线项目状态入口。顶部必须包含：

- `As of` 时间；
- AI-Workspace `main` commit；
- 已核验业务仓库及其 commit / release；
- 数据来源；
- “不是后台实时同步，以下为核验时点快照”的说明；
- 文档一链接；
- 状态数量摘要。

至少包含以下独立板块和原生表格。

### 1. 当前能力矩阵

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
Exact Next Action
Last Verified
```

必须区分“能力蓝图中存在”与“当前 Host 可用”。例如 AI Report Engine 即使架构中存在，未实现时仍应标记 `Planned`，不能因为有名称或 Roadmap 就写成 `Available`。

### 2. 当前任务与主线 / 支线

字段至少为：

```text
Task / Work Item
Mainline or Side
Priority
Status
Owner / Executor
Current Result
Blocker / Dependency
Exact Next Action
Evidence / Source
Last Verified
```

执行时必须处理仓库内重复或冲突的 Task 编号：保留真实文件名并在“风险与治理问题”中明确记录，不得只按编号合并不同任务。

### 3. 已完成里程碑

只列已经合入权威分支、通过验证且仍有效的成果。处于 `Review`、未合入 branch、本机未提交或仅有计划的内容，不得计为完成。

### 4. 未完成与阻塞项

逐项说明：

- 缺少什么；
- 为什么未完成；
- 当前阻塞；
- 解除条件；
- 唯一下一步；
- 是否影响主线。

### 5. 当前可直接使用的入口

面向 User / 策划列出经过验证的入口，例如一键脚本、正式 SVN 包、Codex Capability、飞书文档入口等。不得列出 Secret、endpoint、私有 Registry 或敏感本机配置。

### 6. 可额外开展的支线任务

尚未授权的方向统一标记 `Candidate`，字段至少为：

```text
Candidate
Expected Value
Prerequisite
Risk / Cost
Mainline Impact
Suggested Trigger
Recommended Priority
```

应核验后考虑但不限于：

- AI Report Engine；
- Git → Feishu / SVN Workspace Sync；
- 飞书 Sheets / Bitable Provider；
- Planner Toolkit；
- 多实例独立数据库与跨账号脱敏聚合；
- Huuuge Slots / Systems / Events / Others 后续研究；
- Lottery 数值分析与 CR 迁移建议；
- 新游戏 Collector 可行性与 Adapter；
- ChatGPT Project Source Pack 自动刷新；
- 策划真实盲测与 UX 持续优化。

不得因为本 Task 列出 Candidate，就自动创建、执行或分配这些任务。

### 7. 风险、依赖与治理问题

至少覆盖：

- Task 编号冲突；
- ChatGPT Project Source 快照滞后；
- 飞书展示层与 Git 真相源漂移；
- 私有业务仓库访问依赖；
- ChatGPT 直接写飞书当前受地区限制；
- 能力文档与实现成熟度混淆；
- 多任务并发工作区冲突；
- Huuuge Raw 数据与多账号隔离风险。

### 8. 更新规则

把维护说明放在本文末尾，不创建第三份用户文档。按策划可操作步骤写清：

1. 什么时候更新；
2. 先更新哪个真相源；
3. 如何核验 Task、Status、Handoff、commit、release 和 healthcheck；
4. 如何更新 Git 源稿；
5. 如何通过 `search_documents` 找到原飞书文档并使用 `replace_document` 更新；
6. 成功表现；
7. 失败怎么办；
8. 如何防止重复文档和状态漂移。

### 文档二验收重点

- User 单独打开本文即可看到当前能做什么、已完成什么、未完成什么、当前主线和候选支线。
- 不复制文档一的大段背景、架构和原则。
- 每条状态都有依据和最后核验时间。
- 项目变化时只需要更新本文，不需要改写文档一的稳定说明。

## Feishu Publication Workflow

通过 `feishu-docs` 完成两份、且仅两份正式用户文档：

1. 运行 `feishu_healthcheck`；
2. 使用 `search_documents` 和目标文件夹浏览，确认是否已有同名或旧版文档；
3. 已存在时使用 `replace_document` 更新原文，不重复创建；
4. 不存在时分别创建两份文档；
5. 默认设置为“企业内获得链接的人可编辑”，除非当前企业策略阻止；
6. 使用飞书原生标题、列表和表格；
7. 两份文档顶部都记录 Git 源稿路径、main commit、更新时间和维护说明；
8. 两份文档互相链接；
9. 写入后分别回读标题、关键段落、表格和权限；
10. Registry 仅用于防重，不复制到 Git、飞书或聊天。

若 `feishu_healthcheck` 或写入失败：

- 仍完成两个 Git 源稿；
- 在 Handoff 记录准确错误类型和唯一下一步；
- 不改用未授权第三方在线服务；
- 不宣称飞书交付成功。

## Non-goals

- 不把两个用户文档合并。
- 不创建第三份“维护手册”或第三个在线看板；维护规则写入文档二末尾。
- 不实现实时后台同步、定时任务或新的项目管理平台。
- 不实现飞书 Sheets、Bitable、Wiki 或新的外部 SaaS 集成。
- 不实现 AI Report Engine 的业务生成逻辑。
- 不修改 Huuuge Collector、Capture、游戏请求、奖励、余额或服务器状态。
- 不读取、复制或分析未授权的 Raw Capture。
- 不把 ChatGPT Memory、聊天、Schema、计划或目录存在当作当前实现证据。
- 不扩大权限、购买服务、付费、公开发布或进行不可逆操作。

## Safety

- Secret、Token、私钥、Authorization Header、账号信息、完整响应、逐笔余额、Raw Capture、私有 Registry、代理节点和敏感日志不得进入 Git、飞书或聊天。
- 私有仓库只引用必要的仓库名、commit、release 和脱敏结论，不复制源码或原始业务数据。
- 飞书默认企业内访问，不对公网开放。
- 无法核验的状态标记 `Unknown` 或 `Blocked`，不得猜测。

## Worktree and Concurrency

执行前检查所有 Task、branch、worktree 和本机未提交修改。本任务使用独立 worktree / branch，例如：

```text
branch: task-0019-workspace-docs
worktree: C:\AI-Workspace-task-0019
```

不得清理、stash、reset、提交或覆盖其他任务的文件。不得打断 Huuuge Capture、分析、Cash Frenzy 审计、Document Assistant 或其他运行任务。

## Validation

至少完成：

1. 两个 Git 源稿均存在，且职责无交叉；
2. 文档一没有 Task 明细、完成清单和动态能力状态；
3. 文档二包含能力、任务、已完成、未完成 / 阻塞、入口、候选支线、风险和更新规则；
4. 每项 `Available / Completed` 都有近期证据；
5. `Planned / Blocked / Candidate` 未被写成已实现或已授权；
6. 对比 Task header、项目 Status、Handoff、Review 和最新 commit，显式记录冲突；
7. 所有 Git 路径和引用链接有效；
8. 运行仓库已有 Markdown / link / secret scan；至少执行 `git diff --check` 和敏感模式扫描；
9. 飞书中恰好维护两份正式文档，没有重复创建；
10. 两份飞书文档均完成标题、正文关键内容、表格和权限回读；
11. Git 与飞书版本具有相同的 `As of`、commit 和状态摘要；
12. 未修改其他业务仓库、并行 Task 或本机敏感配置。

## Acceptance

满足以下条件才可进入 Review：

- Git 中存在两份职责分离的源稿；
- 飞书中存在两份职责分离、互相链接、企业内可编辑的在线文档；
- 项目全景说明能够独立解释立项原因、能力蓝图、整体框架和核心逻辑；
- 项目进度与能力状态能够独立展示当前能力、已完成、未完成 / 阻塞、主线和候选支线；
- 所有动态状态附证据与最后核验时间；
- 没有第三份用户文档、重复文档、越权操作或敏感信息；
- 后续 Codex 可以按文档二末尾的更新规则维护同一份在线进度文档。

## Completion and Handoff

完成后：

1. 将本 Task 更新为 `Review`；
2. 更新 `CHANGELOG.md`；
3. 更新 `handoff/CODEX.md`；
4. 记录独立 branch、commit、核验仓库与 commit、两份飞书链接、权限状态、验证结果、冲突和已知限制；
5. push 独立 branch，等待 ChatGPT Review；
6. 不自行合并 `main`。

## Implementation Evidence — 2026-08-29

### Branch and reuse boundary

- 从 AI-Workspace `main@c74c85a9524d1524ea3696835509de2a55e9f524` 新建独立分支 `codex/task-0019-overview-progress-refresh` 与 worktree `D:\AI-Workspace-TASK-0019`。
- 未 merge 旧 `origin/task-0019-overview-progress`；`merge-base --is-ancestor` 对旧分支与新分支返回 false。旧分支只通过 `git show` 提取两份文档供选择性复用。
- 项目全景说明保留当前 `main` 已吸收的稳定结构、Documentation Hub、Product Roadmap 和原生流程图；进度文档根据本轮权威核验重写。

### Verified truth sources

- AI-Workspace：`main@c74c85a9524d1524ea3696835509de2a55e9f524`。
- Huuuge：`main@4a5dddf7782307c6a8f368c9f1dc6390eec6f65b`，与 `origin/main` 一致、工作树干净。
- CF_collect：`main@4df10ec20e79bb737912c8d1b847fae3659031ae`，与 `origin/main` 一致、工作树干净；TASK-0026 Review Round 3 `Accepted`。
- Document Assistant：`main@b0292c3159db16542906948511b6b1ec58c360fd`，与 `origin/main` 一致、工作树干净；本机 healthcheck 的 token、API connectivity、Drive permission 均为 `ok`。
- Workspace Sync：`ON_DEMAND`，provider unavailable，stale 6，conflicts 0。该结果与 Document Assistant Available 分开记录。
- 新工作站：Global AGENTS hash 与批准值一致，Project AGENTS 已加载，Subagents `OFF`，Host readiness `Ready`。

### Corrected current-state semantics

- `bootstrap/chatgpt/02_CURRENT_STATE.md` 将 Huuuge First Run 从“暂定通过”更正为 `Blocked`，并在 Round 1 修订中明确双轨事实：正式 RC4 记录仍为 `Pending`；User 提供的实跑反馈已脱敏记为 `Failed/Invalid`，流程曾到达 `READY`，但没有形成独立测试者、完整计时和逐项成功证据。
- “新工作站 Ready”只证明当前 Host 的 Workspace 与 Document Assistant 接入，不替代 Huuuge First Run。
- `READY` 只表示采集前置条件满足；其后的游戏操作与执行授权仍由 User 控制。该反馈不改写正式 RC4 记录。
- 明确记录 Bet/RTP 证据风险：没有 Bet 分层受控运行证据或稳定 RTP/EV 统计，不得从字段、单次样本、bundle ratio 或描述性比率推导 Bet 与 RTP 关系。
- 进度文档第 7 节新增历史 TASK-0018 文件冲突与 ChatGPT 直写飞书地区限制；全景说明六个核心 Git 入口由旧 `070744...` 统一更新到 `c74c85a...` 基线。

### Git and Feishu deliverables

- Git 源稿：`docs/overview/AI_WORKSPACE_PROJECT_OVERVIEW.md` 与 `docs/status/AI_WORKSPACE_PROJECT_PROGRESS.md`；稳定说明与动态状态职责分离。
- 两份既有飞书文档在 Round 1 修订后再次通过 `replace_document` 原位更新，document identity 未变；没有创建重复文档，conversion warning 为 0。
- 两份文档分别回读标题、稳定链接、核验基线与关键正文；进度文档回读确认 As of、正式 RC4 `Pending`、User 实跑 `Failed/Invalid`、`READY`/执行边界、历史 TASK-0018 文件冲突、ChatGPT 直写飞书地区限制与 Bet/RTP 风险。
- 两份文档权限均回读为 `tenant_editable` / verified。
- 两份文档重新执行 `register_document` 后，导航中心回读通过：17 个登记项、`unique_links=true`，项目全景和项目进度标题各出现一次。
- 回归：Round 1 定向断言 10/10、Task 23/23、Memory 44/44、Context 13/13、Registry 13 canonical / 0 collision / valid、Context refresh 70 sources / 0 broken link / 0 secret issue、Workspace Doctor 与 `git diff --check` 通过；独立 rollback copy 恢复基线通过。

### Scope and handoff

- 未修改 Huuuge、CF_collect 或 Document Assistant 业务代码；未启动模拟器、Root、Frida、Collector，未执行 Spin。
- Subagents: none / `OFF`；Workspace Sync 保持 `ON_DEMAND`，WATCH disabled。
- ChatGPT Review Round 1 正式记录为 `reviews/TASK-0019-CHATGPT-REVIEW-1.md`，Decision `Needs changes`，reviewed commit `9403a09a445fd37548c78b3fc21709e91f5406d9`。
- Task 保持 `Review`；Round 1 指定修订完成，等待 ChatGPT Review Round 2，不自行合并 `main`。
