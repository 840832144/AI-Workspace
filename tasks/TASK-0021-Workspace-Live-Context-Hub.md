# TASK-0021 — Workspace Live Context Hub

- Status: Accepted
- Owner: User / ChatGPT
- Executor: Codex
- Priority: P0 / collaboration infrastructure
- Date: 2026-08-27
- Project key: `WORKSPACE`
- Human alias: `WORKSPACE-LIVE-CONTEXT-001`
- Kind: canonical
- Primary repositories: `840832144/AI-Workspace`、`840832144/document-assistant`
- Preferred collaborative provider: 飞书知识库 / AI Document Assistant
- User authorization: User 已明确要求开始，并要求在飞书知识库能满足时优先采用

## Allocation Evidence

创建本 Task 前，已从 Git 最新 `main@6610feff2acbb48e9058b237c3a12332394b7221` 完整枚举 `tasks/` 根目录，而不是根据聊天或最大编号猜测。

已确认 canonical Task ID 范围为 `TASK-0014` 至 `TASK-0020`；其中 `TASK-0018` 历史冲突已进入治理处理，`TASK-0020` 是 Task Allocation & Namespace Governance。完整目录中不存在 `TASK-0021`，本目标也不与现有 Task 等价：

- TASK-0016：Git-backed Memory Candidate、路由、Review 与 Context Pack；
- TASK-0019：两份正式项目说明 / 进度文档；
- TASK-0020：Task ID、Registry 与 allocator 治理；
- 本 Task：建立跨 ChatGPT、Codex、Trae / DeepSeek、策划成员共享的实时 Context Hub、同步机制和行文规范。

创建后必须再次完整扫描并验证 `TASK-0021` 唯一、文件名与一级标题一致。若 TASK-0020 在执行期间引入新的 Registry / allocator，Codex 必须先使用最新工具复验，不得建立第二个编号体系。

## Problem

当前 ChatGPT Project Sources 是上传时快照。动态状态变化后，需要下载 Markdown、本地编辑、重新上传；多个会话和 Agent 并行执行时，容易出现：

- 新会话读取到旧状态；
- 同一 Task、Handoff 或解决方案在不同 Host 中不一致；
- 策划成员无法方便地在线共同编辑；
- Git、飞书、Project Sources 和聊天之间发生状态漂移；
- AI 回答风格不统一，出现大量单词、短句逐行分隔，影响阅读。

现有 AI Document Assistant 已支持飞书 Docx、Drive 文件夹、搜索、创建、追加、替换和权限管理，但当前 README 明确说明 Wiki 工具仅在架构中预留，尚未实现。ChatGPT 直接通过 Secure MCP Tunnel 读取飞书目前也受 Control Plane 地区限制。因此，**飞书知识库不能在未验证前被当作所有 Host 唯一真相源**。

## Goal

建立一套“稳定启动信息 + Workspace Sync + 最新 Context”的实时协作体系，使策划、ChatGPT、Codex、Trae / DeepSeek 和其他批准 Agent 在开始工作前获得同一份最新上下文，而不再依赖频繁手工替换动态 Project Sources。

目标链路：

```text
稳定 Bootstrap / Project Instructions / AGENTS
                    ↓
              Workspace Sync
                    ↓
       最新 Context Manifest 与相关文档
          ├─ Git canonical truth
          ├─ 飞书协作与展示层
          └─ Host-specific local context pack
                    ↓
       ChatGPT / Codex / Trae / 策划共同工作
```

最终必须达到：

1. 策划可在飞书在线编辑批准的协作文档；
2. Git 继续保存可审计、可回滚的 canonical truth；
3. 新 ChatGPT 项目对话不依赖手工更新 `02_CURRENT_STATE.md` 才能了解实时状态；
4. Codex 和 Generic Agent 可一键同步并读取最新 Context；
5. 并行修改不会静默覆盖，冲突可检测、可 Review、可回滚；
6. 所有 AI 读取并遵守统一的中文行文规范。

## Required Decision — Feishu First, Not Feishu Only

Codex 必须先完成 Reuse-first Feasibility Audit，再选择实现。优先顺序：

1. 现有 AI Document Assistant 与飞书 Docx / Drive 能力；
2. 飞书官方知识库 / Wiki API、事件订阅、版本信息与权限能力；
3. 飞书集成平台或现有团队自动化；
4. GitHub / 本机已有脚本与 Hooks；
5. 只有不足时才开发最小同步层。

### 选择飞书知识库的最低条件

只有同时满足以下条件，才把正式协作层命名为“飞书知识库”：

- 可通过官方 API 确定性地列出、创建、定位和读取知识空间节点；
- 节点关联的文档正文可由 AI Document Assistant 读取和更新；
- 能取得稳定 node / document 标识、更新时间或 revision，用于增量同步和冲突判断；
- 权限模型支持公司成员协作，且不绕过管理员策略；
- 不要求把 Secret、Raw Capture 或私有 Registry写入公开位置；
- 能与 Git mirror / Candidate workflow 形成可验证闭环。

若 Wiki API、权限或当前租户条件不满足，允许使用专用飞书 Drive 文件夹 + 原生 Docx 作为 MVP 协作层，但必须：

- 明确标注为“飞书实时 Context Hub”，不能伪称已经使用知识库；
- 记录具体阻塞和切换到 Wiki 的条件；
- 不因 Wiki 缺失而回退到人工下载 / 上传 Markdown。

Google Drive、Notion、Confluence 等只作为 Feishu 不满足核心条件时的比较项，不在本 Task 中默认引入第二套平台。

## Truth and Authority Model

本任务禁止同一文档无规则双向同步。每个 Context 对象必须声明唯一 authority：

| Content type | Authority | Feishu role | Sync direction |
| --- | --- | --- | --- |
| Core Rules、Capability、Workflow、ADR、Task Registry | Git | 在线阅读 / 提案入口 | Git → Feishu；飞书修改只形成 Candidate |
| Current State、Task / Review / Handoff 摘要 | Git 与受控系统 | 面向人的最新视图 | Git → Feishu |
| 项目全景、进度与能力状态 | TASK-0019 Git 源稿 | 正式在线文档 | Git → Feishu |
| 策划协作笔记、讨论结论草稿、待确认事项 | Feishu | 多人编辑主界面 | Feishu → Memory Candidate / Review branch |
| Secret、Raw Capture、账号数据、完整响应、逐笔余额 | Local only | 禁止保存 | 不同步 |

飞书内容在通过验证、Review 和 Git commit 前，不得自动成为 canonical rule、Task、ADR 或业务结论。

## Live Context Set

第一版只维护最小且高价值的 Context，不镜像整个仓库：

1. `Workspace 入口与同步状态`
2. `核心规则`
3. `系统上下文与能力边界`
4. `当前状态与任务入口`
5. `项目全景说明`
6. `项目进度与能力状态`
7. `策划协作与待确认事项`
8. `AI 行文规范`
9. `Capability / Workflow / Skill 索引`

每个对象必须记录：

```text
context_id
title
authority
scope / sensitivity
git_path（如适用）
provider / document alias
last_git_commit
last_provider_revision
last_synced_at
sync_direction
status
```

飞书 document ID、wiki node token、folder token 和私有 URL 只保存在批准的本机 / 私有 Registry，不进入公开 AI-Workspace。

## Scope

### Phase 0 — Safe setup and current-state audit

1. 同步最新 `AI-Workspace/main` 与 `document-assistant/main`。
2. 读取 Global / Project `AGENTS.md`、Task Registry / Task 目录、最新 Handoff、TASK-0016、TASK-0019、TASK-0020 和本 Task。
3. 使用独立 branch / linked worktree；不得覆盖其他任务、未提交修改或正在运行的 Collector。
4. 审计 AI Document Assistant 真实工具、权限、Registry、Wiki 预留结构及测试。
5. 只使用官方飞书文档确认 Wiki / Docx / Drive / Event 能力、权限和限制；不能根据接口名称猜测。
6. 输出简短 Feasibility Matrix：Feishu Wiki、Feishu Drive Folder、Google Drive / other fallback 的能力、代价、权限、ChatGPT / Codex / Trae 可达性和退出成本。
7. 记录推荐方案并形成 ADR；若需要 User 新建知识空间、发布飞书应用权限或配置外部资源，先给出一次性操作清单并停在可继续状态。

### Phase 1 — Planner Writing Style Standard

在 AI-Workspace 建立并纳入 Live Context：

```text
standards/PLANNER_WRITING_STYLE.md
```

最低规则：

- 默认使用正常中文段落，不把一句话拆成多个单词或短句逐行排列；
- 普通回答优先采用“结论 → 当前依据 → 下一步”，不机械增加大量标题；
- 列表只用于真正并列的信息，每项使用完整句子；
- 命令、代码和结构图才使用代码块，普通文字不放入代码块；
- 不重复使用“我觉得”“其实”“以后”等口头填充词；
- 简单问题直接回答，复杂架构、流程或评审才展开；
- 面向策划的步骤必须写清“做什么、成功表现、失败怎么办”；
- 面向 User 的技术讨论可展示必要架构、逻辑和代码；
- 回答末尾最多保留一个明确下一步，不堆叠跟进建议。

更新以下入口，使 ChatGPT、Codex 和 Generic Agent 在生成内容前读取该规范：

- `bootstrap/chatgpt/PROJECT_INSTRUCTIONS.md`
- `bootstrap/AGENTS.md`
- `bootstrap/generic-agent/`
- 必要的 `AGENTS.md` / Workflow

可以增加一个轻量 Markdown style check，检测大量孤立短行、异常空行、过度标题和把普通散文放入代码块；但不得把中文写作变成僵硬模板，也不得阻断合法表格、命令和代码。

### Phase 2 — Context Capability and ADR

建立或扩展：

```text
capabilities/context/README.md
workflows/workspace-sync/README.md
docs/adr/<next-available>-Workspace-Live-Context-Hub.md
```

定义稳定 Operations：

- `CONTEXT_SYNC`
- `CONTEXT_STATUS`
- `CONTEXT_DOCTOR`
- `CONTEXT_PUBLISH`
- `CONTEXT_CAPTURE_DRAFT`
- `CONTEXT_RESOLVE_CONFLICT`

Operation contract 必须与具体 Provider 解耦；Feishu Wiki / Drive、GitHub、local pack 都是 Implementation Binding，不是 Capability 名称。

### Phase 3 — Feishu collaboration layer

若 Phase 0 选择 Feishu Wiki：

1. 在 `document-assistant` 中增加最小 Wiki Operation，不实现与本任务无关的完整 Wiki 产品；
2. 支持知识空间 / 节点定位、节点列表、创建或绑定 Docx、按 Wiki URL / node token 解析文档；
3. 复用现有 Feishu client、认证、Markdown converter、permission 和 Registry，不建立第二套 token / client；
4. 增加必要的官方 scope 检查、错误提示、回读和测试；
5. 工具分类继续区分 READ / WRITE / ADMIN，不扩大默认权限。

若选择 Feishu Drive Folder：

1. 复用 `create_folder`、`list_folder`、`create_document`、`replace_document`、`get_document` 和权限工具；
2. 建立唯一 Context Hub 文件夹和固定 Index 文档；
3. 使用本机 Registry 防重，不重复创建同名文档；
4. 保留未来迁移到 Wiki 的稳定 context_id 和 document alias。

无论采用哪种方案，正式创建前必须 search / list 防重，写入后回读正文、表格、标题和权限。

### Phase 4 — Workspace Sync engine

优先使用 Python 标准库 / 现有项目依赖，提供 Windows 一键入口：

```text
bootstrap/workspace-sync/Install-WorkspaceSync.ps1
bootstrap/workspace-sync/Invoke-WorkspaceSync.ps1
bootstrap/workspace-sync/Get-WorkspaceSyncStatus.ps1
bootstrap/workspace-sync/Test-WorkspaceContext.ps1
```

建议底层命令：

```text
workspace sync
workspace status
workspace doctor
workspace publish
workspace capture-draft
```

必须实现：

- Git 最新性检查、Context Manifest 和 authority map；
- Feishu revision / updated time / content fingerprint；
- 只同步发生变化的对象；
- Git-authoritative 文档发布到飞书；
- Feishu-authoritative草稿进入 Memory Candidate / Review branch，而不是直接覆盖 canonical；
- Secret Scan、scope / sensitivity 路由、去重和防路径穿越；
- 并发锁、幂等、重试上限、超时和可恢复状态；
- 全程不输出 token、document token、private URL 或完整正文日志；
- 一键查看每个 Context 的 `current / stale / conflict / unavailable` 状态。

### Phase 5 — Automatic freshness

必须比较并选择最小可维护方案：

1. 飞书官方事件订阅触发同步；
2. 飞书集成平台工作流；
3. Windows Scheduled Task / 常驻轻量 watcher；
4. GitHub Actions 定时同步；
5. 只在 Host 启动 / Task 开始时执行 on-demand sync。

最低验收是 **interaction-time freshness**：每个 Host 在任务、Review 或状态查询前主动同步，避免使用旧状态。

若不需要新付费资源或公网服务，优先增加自动传播，使批准的飞书修改在 2 分钟内形成 Git Candidate / mirror。若需要外部托管、GitHub Secret、Webhook 公网地址、飞书管理员配置或长期运行机器，先完成可回滚 PoC，再向 User 提交一次性授权清单；未经批准不得静默部署。

必须提供 Kill Switch：

```text
OFF      # 不自动同步，仍可手动执行
ON_DEMAND
WATCH
```

Pilot 后默认使用 `ON_DEMAND`，除非 User 明确批准 `WATCH`。

### Phase 6 — Host adapters

#### ChatGPT Project

- Project Sources 只保留长期稳定 Bootstrap，不再承载动态 Current State 作为唯一入口；
- 新会话第一步改为 `Workspace Sync`，即读取最新 Git `main`、Context Manifest、Task / Status / Handoff，再按需要读取 Live Context；
- ChatGPT 直接 Feishu MCP 不可用时，通过自动 Git mirror 获取最新公共 / 批准上下文；
- 不能访问最新 Context 时明确报告 `Context unavailable / stale`，不得凭旧 Sources 猜测。

#### Codex

- Global AGENTS 在任务、Review、状态查询前调用 Workspace Sync；
- 使用 AI Document Assistant 读取 / 发布飞书 Context；
- 保持主 Agent唯一写入者，Subagents 默认 OFF；
- Task 完成后刷新 Context 和 Handoff。

#### Trae / DeepSeek / Generic Agent

- 提供一份可复制规则和一键本地同步入口；
- 无 Feishu MCP 时读取 Git mirror / local context pack；
- 有 writer 时按 Task / Memory Candidate 规则提交，不能直接覆盖 main。

#### Planner

- 只需打开飞书 Hub；
- 明确哪些文档可直接协作、哪些只能提交建议；
- 不要求安装 Git、Python、Node 或理解 MCP；
- 操作说明按“做什么、成功表现、失败怎么办”编写。

### Phase 7 — Conflict and safety

必须验证以下规则：

- Git-authoritative 文件在飞书被修改时，不自动覆盖 Git；生成 Candidate 和差异摘要；
- Feishu-authoritative草稿在 Git mirror 也被修改时，标记 conflict，双方内容都保留；
- 同步前后记录 revision / fingerprint，不基于标题判断相同文档；
- 两个 Agent 同时 sync 时只能有一个 writer；
- Public / Project Private / Local-only 使用 TASK-0016 Memory Governance 的路由；
- AI-Workspace 公共仓库不得接收 Huuuge / CR 私有正文；
- Secret、Raw Capture、账号、完整响应和逐笔余额永不进入飞书 Hub、公开 Git 或日志；
- Feishu Registry 与 token 保持本机 / 私有；
- 任何失败不删除原文档、不覆盖 canonical、不虚报已同步。

### Phase 8 — Pilot

使用无敏感内容的隔离文档完成：

1. Git 更新 `AI 行文规范` → sync → 飞书回读一致；
2. 策划在飞书修改 `协作与待确认事项` → 自动形成 Git Memory Candidate / Review branch；
3. 新 Codex 会话运行 Workspace Sync，读取最新修改；
4. 新 ChatGPT Project 对话不重新上传动态 MD，也能通过 Git mirror识别最新 Task、commit、行文规范和 Context freshness；
5. Generic Agent同步同一 Context pack；
6. 两侧并行修改产生 conflict，不静默覆盖；
7. Feishu / Git 临时不可用时使用最近一次已验证 pack，并明确显示 stale；
8. OFF / ON_DEMAND / WATCH 切换和恢复通过；
9. 所有生成物 Secret Scan、Markdown 链接和行文检查通过。

真实 Huuuge / CR 私有内容不用于公开 Pilot。

## Deliverables

### AI-Workspace

```text
standards/PLANNER_WRITING_STYLE.md
capabilities/context/README.md
workflows/workspace-sync/README.md
docs/adr/<next-available>-Workspace-Live-Context-Hub.md
bootstrap/workspace-sync/
bootstrap/chatgpt/PROJECT_INSTRUCTIONS.md
bootstrap/chatgpt/00_CORE_RULES.md
bootstrap/chatgpt/01_SYSTEM_CONTEXT.md
bootstrap/chatgpt/03_NEW_CHAT_BOOTSTRAP.md
bootstrap/generic-agent/
CONTEXT_MANIFEST.yaml / Live Context manifest
CHANGELOG.md
handoff/CODEX.md
```

不要删除历史 Project Source Pack；将其降级为 Bootstrap / 离线回退，并明确动态状态不再靠手工上传维护。

### Document Assistant

只有 Feishu Wiki 被选中时才增加 Wiki 最小实现、权限 scope、测试、README、CHANGELOG 和 Handoff。若 Drive Folder 已足够，禁止为了“看起来更完整”额外开发 Wiki。

### Feishu

建立或复用一个唯一入口，并创建上述 Live Context Set。正式文档默认公司成员可按定义协作；高影响规则和状态文档的权限按 authority model 配置，不能把所有内容无差别设为可编辑。

## Non-goals

本 Task 不做：

- AI Report Engine；
- Huuuge Lottery 数值报告；
- Collector、Extractor 或多实例数据库开发；
- 语义向量数据库、知识图谱或通用 RAG 平台；
- 把整个 Git 仓库逐文件复制到飞书；
- 把飞书设为 Task、ADR、代码或运行证据的唯一真相源；
- 事后抓取并上传所有完整聊天；
- 绕过 OpenAI Control Plane 地区限制；
- 未经 User 批准的公网服务、付费 SaaS、GitHub Secret 或管理员权限变更；
- 自动合并冲突或直接写 `main`。

## Acceptance Criteria

- 完成 Feishu Wiki / Drive / fallback 的可复查选型，满足条件时优先使用 Feishu Wiki；
- 一个固定飞书入口可供策划在线阅读和协作，不再下载 / 上传动态 Markdown；
- Git canonical truth、Feishu collaboration layer 和 local context pack 的 authority 清晰；
- `Workspace Sync` 在 ChatGPT、Codex 和 Generic Agent 三类 Host 有明确可执行 Binding；
- 新 ChatGPT 对话无需重新上传 `02_CURRENT_STATE.md`，即可获取最新 Git Task / Status / Handoff；
- 飞书协作修改能在批准路径中进入 Candidate / Review，不静默覆盖 Git；
- 冲突、stale、offline 和 writer unavailable 均有清晰状态与恢复步骤；
- 行文规范已经进入 Git、飞书 Hub 和 Host instructions；正常回答不再采用单词 / 短句逐行排版；
- 一键安装、同步、状态、Doctor 和回滚均有策划可读说明；
- 所有测试、Secret Scan、链接检查、权限回读和防重复验证通过；
- 不影响 TASK-0016、TASK-0018 Lottery、TASK-0019、TASK-0020、Huuuge Capture、SVN 和现有 Document Assistant 能力；
- 两个仓库分别提交独立 branch / PR 或明确 commit，等待 ChatGPT Review；未经 Review 不合并和生产启用 WATCH。

## Validation Evidence Required

Codex 完成后必须返回：

- Feishu Wiki 是否满足，最终选择及证据；
- Git / Feishu authority map；
- Context Hub 入口和文档清单（只返回安全别名 / 飞书链接，不返回 token）；
- ChatGPT、Codex、Generic Agent 三种 Sync 结果；
- 同步耗时与 freshness；
- revision / conflict / rollback 测试；
- Style Standard 与检查结果；
- OFF / ON_DEMAND / WATCH 最终模式；
- 新增飞书权限或 User 操作（若有）；
- AI-Workspace 与 document-assistant commit / branch；
- 发现但未实施的优化项。

## Handoff

实施完成后：

1. 将本 Task 更新为 `Review`；
2. 更新两个仓库的 CHANGELOG / Handoff；
3. 刷新 Context Manifest，但不得声称 ChatGPT Project Sources 已自动替换；
4. 推送独立 branch，返回 commit / PR 与飞书安全链接；
5. 等待 ChatGPT Review，不自动合并或启用 WATCH。

## Parallel-safety Boundary

- TASK-0016、TASK-0019、TASK-0020 和 TASK-0018 Lottery 可能并行；本 Task 必须使用独立 linked worktree / branch。
- 对 AI-Workspace 的共享文件变更在最终提交前重新同步 `main` 并解决冲突；不得覆盖其他 Task 的 Task、Review、Handoff 或 generated files。
- `document-assistant` 如有其他活动 Task，先检查最新 Handoff 和工作区；发现重叠写入时停止并报告。
- 不停止、重启或重新配置正在运行的 Collector、模拟器、Secure Tunnel 或其他业务服务。

## Execution Result — 2026-08-27

- Final binding：飞书 Wiki Gate 未通过，采用现有飞书 Drive 文件夹 + 原生 Docx 的 Context Hub；Git 保持 canonical，协作草稿只进入 Candidate/Review。
- Workspace Sync：新增 provider-neutral Context Capability、ADR-0007、稳定 manifest、Host-local pack、状态/冲突/回滚实现和 ChatGPT/Codex/Generic Agent bindings。
- Writing standard：`standards/PLANNER_WRITING_STYLE.md` 已进入 Host instructions 与 Live Context。
- Freshness mode：最终保持 `ON_DEMAND`；`WATCH` 未启用，且实现要求显式 User approval。
- Drive Context Hub：原 Pilot 的唯一 Hub、7 个唯一标题、6 个 Git-authoritative `tenant_readable` 文档和 1 个协作草稿 `tenant_editable` 保持不变；本次 latest-main 集成没有再次发布、改名或改权限。
- Document Assistant：PR [#1](https://github.com/840832144/document-assistant/pull/1) 保持 OPEN，head `29fd9f1a58f2626f180e351133f2cd7571c7b43d`，未修改；该 PR 记录 8 files / 24 tests 与 live permission/readback Pilot。
- TASK-0020：Accepted implementation `5f0f6f7` 已通过 merge commit `31475bd` 进入 main；本分支语义合并 Workspace Sync 与正式 Task allocation governance，并将 TASK-0020 / ADR-0006 状态更新为 Accepted。
- AI-Workspace implementation：原实现 commit `0e902b2`；latest-main integration、generated artifacts 与 Review handoff 由本 Task 最终 commit 记录。
- Validation：Context Python tests 13/13；PowerShell Workspace Context 入口通过。正式 Task Registry、Task/Memory regression、Workspace Sync doctor、Manifest/Source Pack refresh 结果记录在最终 `handoff/CODEX.md`。
- Boundaries：未执行 Cash Frenzy；未启用 WATCH；未修改 Huuuge、SVN 或业务仓库；`Subagents: none`。

## Acceptance — 2026-08-27

- ChatGPT Review Round 1：**Accepted**。
- 正式 Review：`reviews/TASK-0021-CHATGPT-REVIEW-1.md`。
- Accepted implementation：`058887993a5d0aa98df68b814b8adc72477cdaf7`。
- Final mode：`ON_DEMAND`；Acceptance 不授权启用 `WATCH`。
- Integration：本 Task 分支与 Document Assistant PR #1 可以合并；现有 Drive Context Hub、权限和内容保持不变。

## Phase 2 Enhancement — 文档导航中心 — 2026-08-27

第一阶段 Acceptance 保持有效。本阶段不新建 Task，在同一 TASK-0021 下增加 Workspace 正式云文档导航治理，当前进入 ChatGPT Review。

### 实施结果

- 创建并复用唯一文档导航中心；其最终展示标题为《AI Workspace｜文档导航中心》。导航中心使用八个固定分类，每条正式文档展示标题、可点击链接、一句话介绍、分类、状态和最后更新时间。
- 历史扫描登记 14 份正式文档，覆盖 Workspace 项目介绍/进度、Huuuge 部署/采集/Lottery、Live Context 及现有正式规则文档；2 份历史临时连接测试被排除。
- Document Assistant 新增 `register_document`，正式 `create_document` 强制完成文档回读、自动登记、Hub 重建与 Hub 回读；Hub 失败时保留原文档、禁止重试创建。
- Core Rules、Project Instructions、Global AGENTS 模板、Repository AGENTS、Document Capability、Document Assistant Workflow 和 Workspace Sync Workflow 已接入统一治理规则。
- Hub 是飞书导航入口，Git 仍是真相源；Hub 正文不展示 token、独立 document ID、私有 Registry 或其他敏感信息。

### 验证

- 唯一 Hub、14 条正式文档、八个固定分类、链接唯一和正文 readback 通过。
- 真实创建正式测试文档后自动登记成功；测试文档删除后 Hub 恢复为 14 条，测试标题不再出现。
- Hub 企业内可编辑权限回读成功；Document Assistant TypeScript 构建和 10 个测试文件 / 32 项测试通过。
- Workspace Sync 保持 `ON_DEMAND`，WATCH disabled；未修改 ChatGPT 设置；`Subagents: none`。

### Review 请求

- 请核对正式文档/临时文档边界、Hub 失败语义、历史分类和两个仓库的回归证据。
- 本阶段独立分支等待 ChatGPT Review；未经 Review 不合并实现分支。

## Final UX Closeout — 2026-08-27

ChatGPT Review 2 确认主体实现通过，仅要求中文标题与项目全景入口收尾。本轮在同一 TASK-0021 中完成，不新建 Task。

### 完成内容

- 唯一导航入口从旧展示标题原位更名为《AI Workspace｜文档导航中心》，保留同一文档与 URL；稳定 alias、Registry Hub 标记和防重规则不依赖展示标题。
- 导航中心首页增加三句中文说明：统一导航入口、正式文档自动登记、Git 仍是真相源且本页只负责导航。
- 恢复 `docs/overview/AI_WORKSPACE_PROJECT_OVERVIEW.md` Git 源稿；原位更新 `Game Planner AI Workspace｜项目全景说明`，在“一页式项目说明”之后依次增加“📚 下一步推荐阅读”和“🗺 项目工作流总览”；未复制正文或创建副本。
- Documentation Governance 最终流程为 `create_document → 文档回读 → register_document → 文档导航中心回读 → Success`。导航中心失败时不删除已创建文档、不重复创建，返回失败并等待修复。
- 新增 Proposed `RFC-0004: Research Environment Strategy`，记录 `One Research Environment → Multiple Games → Independent Evidence`；不修改当前 Cash Frenzy Candidate 或 TASK-0022。

### 最终验证

- 文档导航中心同一 URL、唯一标题、14 条正式文档、八分类、链接唯一、首页中文说明和企业内可编辑权限回读通过。
- 项目全景说明同一文档，新增章节位置、可点击链接目标、飞书原生 Mermaid 白板块、正文回读和企业内可编辑权限通过；连续执行两次保持幂等。
- “核心规则”“实时 Context Hub”和“当前状态与任务入口”三份既有正式云文档已从最新 Git 源稿原位发布，并完成各自正文回读、自动登记与导航中心回读。
- Document Assistant 构建及 12 个测试文件 / 36 项测试通过；真实创建—登记—删除—恢复烟测通过；Workspace Task、Context、Memory 与 Doctor 回归通过。
- Workspace Sync 保持 `ON_DEMAND`；WATCH disabled；未修改 ChatGPT 设置；`Subagents: none`。

### Acceptance

- TASK-0021 最终状态：**Accepted**。
- ADR-0007 保持 Accepted，并补充最终中文导航治理决定。
- 两个实现分支按 Review 2 要求合入 main；最终 merge 与 closeout commit 记录在 `handoff/CODEX.md`。
