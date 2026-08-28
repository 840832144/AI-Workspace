# TASK-0016 — Automatic Cross-Conversation Memory Capture & Curation

- Status: Review
- Owner: User / ChatGPT
- Executor: Codex
- Priority: P1
- Reserved as: next task after TASK-0015
- Execution gate: Do not start until TASK-0015 is completed or paused and User explicitly says “开始 TASK-0016”
- Date: 2026-08-27

## Goal

建立一套以 Git 为长期真相源的自动记忆体系，使 ChatGPT Project 内不同对话、Codex、Trae + DeepSeek、其他 Agent 以及经授权的团队成员，在讨论或完成工作时能够：

1. 自动识别值得长期保留的规则、决定、事实、解决方案、Skill、Workflow、状态和失败经验；
2. 在安全、证据和作用域明确时自动生成并提交结构化 Memory Candidate；
3. 对高置信、低风险、可验证的内容自动整理到正确的长期位置；
4. 对无法写入、置信不足、存在冲突或敏感性不明确的内容进入 Review Queue，等待策划决定；
5. 自动刷新 Context Manifest、ChatGPT Project Source Pack、Status 和 Handoff，使新对话能够快速读取最新信息；
6. 不上传完整聊天、Secret、账号信息、Raw Capture、逐笔余额、私有 Registry 或敏感日志。

目标是“自动优先，人工兜底”，而不是把每次对话全文无差别保存。

## Product Reality and Constraints

- ChatGPT Project Memory 可以参考同一 Project 中的聊天和文件，但不是可审计、可枚举、保证完整召回的数据库。
- 标准 ChatGPT GitHub App 主要用于读取、搜索和分析；写入 Git 必须通过当前 Host 的写入能力、Codex 或后续批准的专用 Provider。
- 目前不存在可依赖的“每次 ChatGPT 对话结束自动触发 Git Hook”官方入口，因此自动沉淀必须优先在内容产生时完成；无法直接写 Git 的 Host 必须走统一 Outbox / Review Queue，不得假装已提交。
- Project Sources 是快照；实时 Task、Status、Handoff 和实现状态仍以 Git 与业务仓库为准。

Codex 实施前必须核对最新官方文档和当前 Host 能力，不得把本任务中的产品约束当作永久不变事实。

## Design Principles

### 1. Source-side capture

重要内容应在产生它的对话或 Agent 中尽早转成结构化 Memory Event，而不是依赖事后扫描全部聊天。

每个支持的 Host 在完成一段实质工作后执行一次静默 Memory Check：

- 是否产生了长期有效的新规则或明确 User 决定；
- 是否发现或修复了可复用问题；
- 是否形成了可重复执行的 Workflow / Skill；
- 是否改变了当前 Task、Status、Blocker、Evidence Level 或 Provider binding；
- 是否产生了会影响其他对话或项目的事实；
- 是否只是临时讨论、未验证想法、重复内容或调试噪声。

### 2. Candidate first, canonical later

自动化分两阶段：

```text
Conversation / Agent
    ↓
Memory Event / Candidate（安全、追加式、可撤销）
    ↓
Validator + Secret Scan + Dedup + Scope Router
    ↓
Memory Curator
    ├─ 自动晋升：高置信、低风险、可验证
    ├─ Review Queue：冲突、敏感、跨项目、高影响或证据不足
    └─ Reject / Archive：重复、短期、无证据或不适合沉淀
    ↓
Canonical Rule / ADR / Skill / Solution / Status / Handoff / Report
```

不得让单个对话直接静默覆盖 Canonical Memory。

### 3. Scope and storage routing

AI-Workspace 当前是公共治理仓库，不能成为所有内部对话的默认存储位置。

路由规则：

- `Public / Global`：脱敏、可公开、跨项目通用的规则、模板、Skill、Workflow、公开解决方案 → `AI-Workspace`。
- `Project Private`：Huuuge、CR 或其他业务项目的内部事实、决定、状态和解决方案 → 对应私有业务仓库。
- `Cross-project Private`：跨项目但不适合公开的内容 → 评估是否需要 User 创建批准的私有 Context Hub；没有批准目的地时保留在本机 Outbox 并提示一次。
- `Local only`：Secret、Raw Capture、账号数据、逐笔余额、完整响应、截图原件和敏感日志 → 只留在受控本机，禁止上传。

当作用域或敏感性无法判断时，默认不得写入公共仓库。

### 4. Provenance, not full transcript

每条 Candidate 至少记录：

```yaml
memory_id:
title:
type:
scope:
sensitivity:
status:
source_host:
source_project:
source_actor_alias:
source_reference:
related_task:
related_commit:
created_at:
durability_score:
reuse_score:
evidence_score:
confidence:
summary:
evidence:
constraints:
supersedes:
```

- `source_reference` 使用可控的 chat ID/hash、Task、commit、文件路径或 URL；不存完整对话。
- 所有内容区分 `Confirmed`、`Estimate`、`Hypothesis`、`Decision proposal`。
- User 明确决定必须保留作用域和时间，不能被 Agent 扩大解释。

### 5. Automation modes and kill switch

实现三个模式：

#### OFF

- 不自动生成 Candidate。
- User 仍可发送“沉淀本次对话”手动触发。

#### ASSISTED

- 自动生成并写入安全 Candidate / Outbox。
- Canonical 晋升默认需要 Curator 或 Review 规则确认。
- 作为第一阶段生产默认模式。

#### AUTO

- 自动生成 Candidate；满足 Auto-promotion Policy 的内容可自动晋升并提交。
- 高影响、冲突、敏感、跨项目、架构或规则变更仍必须进入 Review Queue。
- 本任务必须实现并验证 AUTO，但 Pilot 结束后的最终默认模式由 User 决定。

必须提供一键查看状态和切换模式，并保证 OFF 时不影响正常聊天、Codex、Trae 或项目工作。

## Auto-capture Policy

### 自动捕获候选

满足以下任一项且通过安全检查时，应自动生成 Candidate：

- User 明确采纳或否决一个长期决定；
- Task / Review / Release 状态发生变化；
- 一个问题得到可复现修复，并有 commit、测试或系统证据；
- 新增可复用 Capability、Provider、Tool binding、Workflow、Skill 或部署方法；
- 发现已有工具、内部方案、官方方案或成熟开源方案可替代自研；
- Huuuge Evidence Level、Blocker、数据口径或研究结论发生变化；
- 重要假设被证伪；
- 出现其他对话或项目以后很可能重复遇到的经验。

### 不自动捕获

- 闲聊、临时偏好和一次性表达；
- 尚未形成结论的 brainstorm；
- 无证据推测；
- 重复已有 Canonical Memory 的内容；
- 调试过程中的大量中间日志；
- Secret、Raw 数据、完整响应和个人敏感信息。

### 自动晋升允许范围

仅当内容同时满足“高置信、证据充分、低敏感、无冲突、目标路径明确”时允许自动晋升。第一阶段建议仅开放：

- 已完成 Task 的 Status / Handoff 更新；
- 与 commit 和测试直接绑定的 Solution record；
- 已明确接受的 Review 结果；
- 纯索引、Manifest 和 Context Pack 刷新。

以下内容即使在 AUTO 也必须 Review：

- Core Rule、架构、ADR 和 Capability contract 变更；
- 跨项目策略；
- User 权限、费用、付费或不可逆决定；
- 互相冲突的事实；
- 证据不足但可能影响业务结论的内容；
- 公开 / 私有路由不明确的内容。

## Memory Type Routing

| Memory Type | Canonical Destination |
| --- | --- |
| Global rule / governance | `00_CORE_RULES.md`、Standards 或 RFC/ADR |
| Architecture decision | `docs/adr/` |
| Reusable procedure | `skills/` 或 `workflows/` |
| Solved technical problem | `solutions/<scope>/<slug>/README.md` |
| Project fact / lesson | 对应项目 `MEMORY.md` / Knowledge |
| Current state / blocker | `STATUS.md` / `CURRENT_STATUS.md` |
| Task progress / handoff | `tasks/` / `handoff/` |
| Long research result | 对应私有项目 `reports/` / `knowledge/` |
| Uncertain / conflicting | `memory/review/` |
| Rejected / superseded | `memory/archive/` |

## Reuse-first Discovery

开始实现前，Codex 必须按以下顺序研究并记录结论：

1. AI-Workspace、Global AGENTS、现有 Task/Handoff/Project Sources；
2. 本机 Git、Codex hooks、CLI、MCP、Trae/DeepSeek 扩展和团队内部工具；
3. OpenAI / Codex / GitHub 官方方案；
4. 许可证清晰、维护活跃的成熟开源 Memory、Agent Memory、Knowledge Graph、Git-backed Context 或 Event Queue 方案；
5. 对 Adopt / Wrap / Fork / Build 做对比；
6. 只有现成方案不满足安全、跨 Host、Git 真相源和部署便利要求时才自研。

研究候选不等于自动安装。新增服务、账号、付费资源、外部 SaaS 或高权限 GitHub App 必须先取得 User 批准。

## Deliverables

### Governance and Contracts

- `capabilities/memory/README.md`：Memory Capability 与 Operations。
- `standards/MEMORY_GOVERNANCE.md`：捕获、路由、晋升、冲突、归档和安全规则。
- `docs/adr/ADR-0005-Git-Backed-Automatic-Memory.md`。
- `docs/research/MEMORY_SOLUTION_DISCOVERY.md`：Reuse-first 选型记录。

### Repository Structure

建立可审阅的结构，实际路径可在不破坏边界的前提下调整：

```text
memory/
├── README.md
├── inbox/
├── review/
├── archive/
└── index/
solutions/
templates/memory/
```

公共仓库只允许 Public-safe Candidate。私有/敏感路由必须在实现前被明确处理。

### Schemas and Templates

- `templates/memory/MEMORY_EVENT.yaml`
- `templates/memory/MEMORY_CANDIDATE.md`
- `templates/memory/MEMORY_REVIEW.md`
- `CONTEXT_MANIFEST.yaml`

Schema 必须支持版本、来源、证据、置信、作用域、敏感性、去重、supersede 和 Canonical destination。

### Capture and Curator Tooling

建立一键、可重复执行、可回滚的工具，优先采用跨平台实现并提供 Windows 入口：

- `Capture-MemoryCandidate`
- `Validate-MemoryCandidate`
- `Curate-MemoryCandidates`
- `Refresh-ProjectContext`
- `Get-MemoryStatus`
- `Set-MemoryMode -Mode Off|Assisted|Auto`

要求：

- 默认不覆盖现有文件；Canonical 修改走最小 diff 或 PR。
- 写入前 Secret Scan、敏感性检查、Schema 验证和去重。
- 写入失败自动保存到本机 Outbox；不得丢失，也不得声称已上传。
- 多 Agent / 多用户并发时使用 branch、lock、PR 或等价安全机制，避免直接争写 `main`。
- 公开仓库的 Candidate 自动写入前必须验证 Public-safe。
- 每次运行输出简洁状态：captured、promoted、review、rejected、local-only、failed。

### Host Adapters

至少覆盖：

1. **ChatGPT Project**
   - 更新 `bootstrap/chatgpt/PROJECT_INSTRUCTIONS.md` 和 00–03 Source Pack；
   - 在实质对话中执行静默 Memory Check；
   - 当前会话具备批准的 Git 写能力时自动写 Candidate；
   - 只有标准只读 GitHub App 时输出标准 Outbox 事件，由 Codex / Curator 接管；
   - 不依赖事后遍历全部项目聊天。

2. **Codex**
   - 更新 Global AGENTS；
   - Task / Review / Handoff 完成后自动运行 capture；
   - Codex 作为默认 Git writer 和 Curator executor；
   - 保持 Subagent OFF/MANUAL 独立，不把 Memory 功能依赖于 Subagent。

3. **Trae + DeepSeek / Generic IDE Agent**
   - 提供可复制的项目规则、Skill 和 CLI 调用；
   - 能写本机 Outbox，具备 Git 权限时提交 Candidate branch/PR；
   - 不要求读取私有实现仓库或配置 Secret。

4. **Human / Other Agent**
   - 提供最简网页、Issue Form、CLI 或文件 Drop 入口中的最佳批准方案；
   - 所有提交保留 actor alias 和来源，不信任未经验证的事实。

### Context Refresh

`Refresh-ProjectContext` 至少完成：

- 拉取 AI-Workspace 与登记业务仓库最新 Task、Status、Handoff、ADR、Skill、Solution 和 commit；
- 生成 `CONTEXT_MANIFEST.yaml`；
- 更新 `bootstrap/chatgpt/02_CURRENT_STATE.md`；
- 生成新的 ChatGPT Project Source Pack；
- 输出“哪些 Project Sources 需要替换”的清单；
- 检查过期引用、失效链接、冲突、Secret 和重复内容；
- 不把业务私有内容写入公共 Source Pack。

若当前产品没有安全 API 自动替换 ChatGPT Project Sources，必须明确报告 `manual upload required`，不得用浏览器脆弱自动化伪装成可靠集成，除非 User 单独批准实验。

## Conflict and Deduplication

- 同一事实以 `scope + type + normalized key + evidence reference` 去重；可增加语义相似度，但不得仅凭模型相似度静默删除。
- 新 Candidate 与 Canonical 冲突时不覆盖；生成 Conflict Record 并进入 Review。
- 长期决定使用 `supersedes`，保留历史，不重写旧 ADR。
- 不同账号、模拟器实例和项目的数据保持隔离；跨账号规律只进入脱敏聚合层。

## Pilot

选择至少三种真实场景：

1. ChatGPT Project 对话产生一个 User 明确决定和一个可复用设计；
2. Codex 完成一个 Task，产生 Solution、Status 和 Handoff；
3. Trae/DeepSeek 或 Generic Agent 产生一个候选 Skill / 解决方案。

每个场景验证：

- 自动检测是否合理；
- 是否正确路由 Public / Private / Local-only；
- 是否防止重复和 Secret；
- 是否成功进入 Candidate、Review 或 Canonical；
- 新对话能否通过 Manifest / Source Pack / Git 找到它；
- 无写能力时是否可靠进入 Outbox 并提示下一步；
- OFF / ASSISTED / AUTO 切换是否生效。

Pilot 结束后记录捕获数量、误捕获、漏捕获、人工干预次数、冲突、耗时和 User 决定；不得虚构准确率。

## Safety and Boundaries

- 不保存完整聊天原文，除非 User 明确要求且目标为批准的私有受控存储。
- 不把公司内部讨论、CR 细节或 Huuuge 私有研究自动写入公共 AI-Workspace。
- 不把 Project Memory 当作实时真相源。
- 不创建高权限 GitHub App、外部 SaaS、公开 webhook 或新付费服务，除非 User 明确批准。
- 不修改 Huuuge Collector、AI Document Assistant、SVN 正式包或当前 Lottery Capture。
- 不通过屏幕抓取、浏览器注入或 DOM scraping 获取 ChatGPT 对话，除非官方路线不可用、完成安全评审且 User 单独批准。
- 所有自动写入必须可回滚、可审计、可关闭。

## Non-goals

本任务不做：

- 保存所有聊天全文；
- 训练模型或建立通用个人记忆产品；
- 自动把 Hypothesis 提升为 Confirmed；
- 自动批准费用、权限、发布或不可逆决定；
- 将所有项目数据集中到公共仓库；
- 把 AI Report Engine、Workspace Sync 或多实例数据仓库混入本任务。

## Acceptance Criteria

- OFF / ASSISTED / AUTO 三种模式均可一键切换和查看。
- 至少 ChatGPT、Codex、Generic IDE Agent 三类 Host 有可执行接入路径。
- 高价值内容可以在无需 User 每次发“沉淀”指令时自动进入 Candidate。
- 无法判断、冲突、敏感或无法写入的内容自动进入 Review / Outbox，而不是丢失或错误上传。
- Public / Private / Local-only 路由有真实测试证据。
- Canonical Memory 不被单个 Agent 静默覆盖。
- Context Manifest、`02_CURRENT_STATE.md` 和 Project Source Pack 可以一键刷新。
- 新对话能找到 Pilot 中沉淀的规则、Solution、Skill 或状态。
- Secret scan、Schema、dedup、conflict、concurrency 和 rollback 测试通过。
- 更新 `CHANGELOG.md`、相关 README、Global/Project rules、`handoff/CODEX.md` 和本 Task 状态。
- 提交并推送，等待 ChatGPT Review。

## Handoff Required

Codex 完成后必须返回：

- Git commit / PR；
- 最终 Memory Mode；
- 实际采用、包装、Fork 或自研的方案及原因；
- ChatGPT、Codex、Trae/Generic 三类 Host 的接入状态；
- Public / Private / Local-only 路由测试；
- 自动捕获、自动晋升、Review、Outbox 的 Pilot 结果；
- Project Source Pack 刷新方式；
- 未解决限制和下一 Task 候选。

## Execution Result

- Reuse-first 调研完成：采用 OpenAI 原生 memory / Codex hooks 作为 Host recall 与 lifecycle 层，以 Git 作为可审计长期真相源；借鉴 Mem0、Letta/MemFS、LangMem、Graphiti 的分层与候选思想，但本阶段不安装、Fork 或引入外部服务。
- 已实现 Memory Capability、governance、ADR、schema、Public/Private/Local-only 路由、OFF/ASSISTED/AUTO、Windows 入口、ChatGPT/Codex/Generic adapters、Context refresh 与 disabled hook reference。
- `AUTO` 仅在隔离 Pilot 自动晋升一个新建、Public-safe、低风险 Solution；production 默认及最终模式均为 `ASSISTED`，未安装 hook。
- Round 1 的 17/17 单元测试与 Pilot 已由 ChatGPT 接受架构方向，但 Review 1 要求补齐 Private writer、AUTO transaction 和 provenance gate。
- 实际 AI-Workspace refresh 生成 Manifest、Current State、Source Pack 和替换清单；私有仓库未读取，ChatGPT Project Source 更新明确为 manual upload required。
- Implementation commit: `ea4b758`（rebase 后 hash）。最终交接提交另见 `handoff/CODEX.md` 所在 Git HEAD。
- Subagents: none。
- 未修改 Huuuge 仓库、运行中的 Collector、当前 Capture、SVN、飞书文档、Document Assistant 或 Global runtime。

### Review 1 Required Fix Result

- Required Fix 1：实现 Host-local approved Repository Registry。classification 支持 `public-control-plane`、`project-private`、`cross-project-private-hub`；私有写入同时验证 alias、writer、scope、sensitivity、source project、绝对 Git root，且目标必须位于 public AI-Workspace 之外。Disposable private Git Pilot 写入 1 个 Candidate，public Inbox 为 0；未批准 alias 与错误 classification 均进入 Outbox。
- Required Fix 2：AUTO promotion 只允许在非 main/master linked worktree 中执行，开始时只允许 `memory/inbox/` 变化；target、Candidate、Archive、index 使用执行前字节快照组成可恢复事务。target 后、Archive 前后、index save、Git status change 五类 fault injection 全部 rollback，`promoted=0`；main 与 unrelated dirty worktree 均在写入前 fail closed。
- Required Fix 3：所有 Git Candidate 禁止空值及 `unknown`、`n/a`、`none`、`null`、`-`、`tbd` 等 placeholder provenance。CLI、Event file 和 Generic Agent 三条入口均验证缺失时进入 Outbox，public Inbox 零写入。
- 回归：34/34 tests passed。Round 2 Pilot captured 3（approved private Git 1）、promoted 1、review 1、local-only/Outbox 4、OFF suppressed 1、failed 0；未测量 false captures / missed captures。
- Final mode：`ASSISTED`。未激活 Hook/AUTO，未访问真实私有项目仓库，未影响 TASK-0017。
- Review record：`reviews/TASK-0016-CHATGPT-REVIEW-1.md`；下一动作是 ChatGPT Round 2 Review。

### Review Round 2 与跨会话闭环结果

- Review Round 2 正式记录为 `reviews/TASK-0016-CHATGPT-REVIEW-2.md`，结果 Needs changes；本轮只修复其中两个安全问题并执行已批准 support `tasks/support/TASK-0016/WORKSPACE-MEMORY-CROSS-SESSION-CLOSURE.md`，没有新增 Task 或第二套 Memory 系统。
- provenance gate 改为“必须包含有效字母或数字 + placeholder denylist”；空值、ASCII `-`、`unknown`、`n/a`、`na`、`none`、`null`、`not applicable`、`tbd`、`unspecified` 和纯标点均确定性进入 Outbox。CLI、Event file、Generic Agent 的 ASCII `-` 回归均确认 public/private Inbox 为 0。
- `sensitivity=secret` 与 `scope=local-only` 在 Registry 读取前 hard deny。恶意/误配 Registry 即使显式允许 `secret` 或 `local-only` 也不能写任何 Git Inbox；声明 Secret 的正文、来源与目标提示在 Outbox 整体抑制，不保留测试 literal。Registry 只能收紧 Global Safety Contract。
- 建立唯一 `memory/context/WORKSPACE.md`，复用 `Memory Event → Candidate → Validator → Curator`。ASSISTED 下只有通过 `--approve-workspace` 显式批准，且 public-safe、高分、高置信、有 evidence、无冲突的 Candidate 才能晋升；同 key 冲突进入 Review，显式 supersede 保留旧来源和时间。
- 三个 public-safe Seed 已通过同一 Curator 晋升并归档：Git Memory / 云文档长期边界、TASK-0024 Accepted 的 Cash Frenzy F3 strengthened / F4 未证明与停止路线、TASK-0023 Accepted 的 Product Roadmap / Idea Governance / Planner Writing Style 生效状态。Read view 为 3 个唯一 key、3 个独立 source reference、0 duplicate。
- ChatGPT Bootstrap、Project Instructions、Core/System Context、Generic Agent、Capability、Governance 与工具说明统一为 Git-live-first：Core/System/Writing Style → 最新 Git `main` Workspace Memory → 相关 Task/Review/Status/Handoff/业务证据；Git unavailable 时才使用并标记 stale 的 Project Source Pack。
- Context refresh 将 Workspace Memory 纳入 Manifest / Source Pack，并输出 path、SHA-256、读取时 Git HEAD；未读取私有仓库，Project Sources 继续 `manual upload required`。
- 新会话测试确认不会将 F3 写成 F4，不会建议重复 TASK-0024 已停止路线；冲突或未 Accepted Candidate 不进入 canonical read view。
- 最终回归：Memory 44/44、Task 23/23、Context 13/13；Registry 12 canonical / 0 collision / status valid，Workspace Doctor 通过，Context refresh 68 sources / 0 secret issue / 0 broken link。
- 最终 production mode 保持 `ASSISTED`；AUTO 未启用，Hook 未安装/启用，Workspace Sync 保持 `ON_DEMAND` 且 WATCH disabled；未新增外部服务。Subagents: none。
- 当前状态：实现完成，等待 ChatGPT Review Round 3。
