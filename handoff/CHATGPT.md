# ChatGPT Handoff

这是 ChatGPT 的固定交接入口。长期事实必须同步到 Capability contract、项目 Memory / Status、Task、RFC、ADR 或正式 Review，而不是只留在聊天中。

- Updated: 2026-08-29
- Current Review request: TASK-0019 — 项目全景说明与独立进度文档
- TASK-0019 status: `Review`
- Project key: `WORKSPACE`
- Execution rule: 并行任务使用独立 branch / linked worktree；不得覆盖其他任务或未提交修改

## TASK-0019 — Current Review Request（Round 3）

- Review branch：`codex/task-0019-overview-progress-refresh`，基于 `main@c74c85a9524d1524ea3696835509de2a55e9f524`；未 merge 旧 `task-0019-overview-progress`。
- TASK-0019 Review Round 1 正式记录为 `reviews/TASK-0019-CHATGPT-REVIEW-1.md`：Decision `Needs changes`，reviewed commit `9403a09a445fd37548c78b3fc21709e91f5406d9`；本次只修指定的文档事实与验收缺口。
- TASK-0019 Review Round 2 正式记录为 `reviews/TASK-0019-CHATGPT-REVIEW-2.md`：Decision `Needs changes`，reviewed commit `e05d781e8aa54a6d10f1d0e44a1f84310fdf847e`；`e05d` 是已审基线，不是本轮新提交。
- Git deliverables：`docs/overview/AI_WORKSPACE_PROJECT_OVERVIEW.md`（稳定说明）与 `docs/status/AI_WORKSPACE_PROJECT_PROGRESS.md`（动态状态），不得合并职责。
- 核验 main：Huuuge `4a5dddf`、CF_collect `4df10ec`、Document Assistant `b0292c3`；均与远端一致且工作树干净。
- 必查口径：Huuuge First Run 保持 `Blocked`；正式 RC4 记录仍为 `Pending`；User 实跑仍为 `Failed/Invalid`。正式 Collector READY 未被可复核证明；只确认临时 SSL 捕获后进入 User 操作阶段，游戏由 User 亲自操作。Bet/RTP `Unsupported`。
- 必查历史与入口：进度文档第 7 节已补历史 TASK-0018 文件冲突和 ChatGPT 直写飞书地区限制；全景说明六个核心 Git 入口已统一到 `c74c85a...` 核验基线。
- 必查 Provider 分离：Workspace Sync 为 `ON_DEMAND / provider unavailable / stale 6 / conflicts 0`；Document Assistant 为 `Available`，healthcheck token/API/Drive 全部 `ok`。
- 飞书验收：Round 2 只原位 replace 既有进度文档，禁止创建副本，项目全景飞书文档未写；进度文档正文、document ID/链接和 `tenant_editable` 权限回读通过，Hub 保持 17 个登记项与 `unique_links=true`。
- Scope：未修改业务仓库；未启动模拟器、Root、Frida、Collector，未执行 Spin；Subagents: none / OFF。
- Validation：Round 2 定向断言 12/12、Task 23/23、Registry 13 canonical / 0 collision / valid、changed-document scan 0 broken link / 0 secret assignment、项目全景 hash 不变、0 新 Task 与 `git diff --check` 通过。
- 决策边界：下一业务决策候选是 P0 Reliability Hardening Decision proposal；未获 User 批准不创建 Task、不进入实现或运行。
- Review 输出：TASK-0019 Review Round 3 的 `Accepted` 或精确修改项；未 Accepted 前不得合并 `main`。

## TASK-0023 — Idea Governance & Product Roadmap

- ChatGPT Review Round 2：Accepted；正式记录为 `reviews/TASK-0023-CHATGPT-REVIEW-2.md`，reviewed commit 为 `bc0d3ad1e519fb908dce53a78a35f9c3687a5b51`。
- Idea Governance 与 Planner Writing Style 已转为 `Accepted / Active`；Product Roadmap 和统一技术术语规则正式生效。
- 收口前回归：Context / Source Pack 62 sources、0 broken link、0 secret issue；Task 23/23、Context 13/13、Memory 35/35、两个 PowerShell 入口、Registry 10 canonical / 0 collision 与 Doctor 全部通过。
- Workspace Sync 保持 `ON_DEMAND`、0 conflict；provider unavailable，6 个发布项保持 stale，没有启用 WATCH。

- ChatGPT Review Round 1 结论为 Needs changes；Roadmap / Idea Governance 主体已通过，唯一 Required Fix 是准确、克制、面向受众的技术术语规则。
- `standards/PLANNER_WRITING_STYLE.md` 已成为唯一 canonical 规则源；Core Rules、Repository/Bootstrap/Global AGENTS、Project Instructions、ChatGPT Bootstrap、Generic Agent 入口和 Context Hub 均引用同一标准。
- ChatGPT 单文件 Source Pack 与 6 个拆分来源清单均包含 canonical 规范正文，不再只依赖 Core Rules 摘要。
- 默认面向策划使用准确且可理解的研究表达；复现、工程判断、授权、合规、安全或风险依赖真实机制时必须保留 Root、Frida、Hook、逆向分析、协议解密、校验绕过、系统修改、exploit 等精确术语。
- 规则明确禁止通过改名或模糊化规避安全策略、权限检查、User 授权或 Review，不得弱化真实风险或夸大被动研究。
- Context / Source Pack 已刷新为 62 sources、0 broken link、0 secret issue；Task 23/23、Context 13/13、Memory 35/35、两个 PowerShell 入口、Registry 10 canonical / 0 collision 与 Doctor 均通过。
- Workspace Sync 保持 `ON_DEMAND`、0 conflict；provider unavailable，6 个发布项保持 stale，没有启用 WATCH。

- User 已批准建立新的独立治理任务；正式 Candidate 经 allocator 晋升为唯一 canonical TASK-0023，reservation 保持 `pending-main`，未手工指定编号或编辑 Registry。
- 已建立唯一 Git Product Roadmap，固定 `Current / Backlog / Ideas / Done`，并明确它不替代 Task、Documentation Hub、Knowledge、Memory 或项目 Status。
- ChatGPT 新规则：主动提出长期产品能力、Workflow、Capability、Collector 或 UX Idea 时，自动防重、分类，并在相关 Task 收尾时向 Codex 生成 Idea Handoff，不依赖 User 手工提醒。
- 唯一正式飞书 Product Roadmap 已创建、回读、企业内可编辑并自动登记；项目全景说明已原位增加 Roadmap 入口，导航中心当前登记 15 份正式文档。
- 真实临时 Idea 已进入 Ideas 并回读，随后删除；正式 Roadmap 已恢复，四分区各出现一次。
- Registry 10 canonical / 0 collision；Task 23/23、Context 13/13、Memory 35/35、两个 PowerShell 入口和 Workspace Doctor 通过；Context refresh 62 sources、0 broken link、0 secret issue。
- TASK-0022、Cash Frenzy、Huuuge、Document Assistant 和 Workspace Sync 状态均未修改；`ON_DEMAND` 保持不变，WATCH disabled，Subagents: none。
- Review 重点：分类 Gate 是否足够严格、Top Tycoon 的 Current 表达是否符合 User 给出的顺序、ChatGPT Idea Handoff 是否既主动又不会越权创建 Task。
- 收口：完成 deterministic regression 后合并并 push main，在原 allocator worktree finalize TASK-0023 reservation，复验 0 collision 后清理分支/worktree。

### Failed attempts

- Candidate 首次使用带说明的 User decision 文本，被 allocator 按枚举 Gate 拒绝；修正为规范 `Approved` 后才分配 canonical ID，首次失败未占号。
- 首次临时发布脚本因 CommonJS 不支持 top-level await，在编译阶段退出且没有云写入；改为 `async main()` 后完整发布与恢复通过。
- 当前 Codex 会话的旧 MCP 进程缺少 `register_document`；其 `get_document` 回读会按旧 Registry schema 写回，导致项目全景说明治理 metadata 暂时丢失。未创建副本；使用 Document Assistant 当前 `main` 新进程重新登记后，Hub 恢复 15 条、链接唯一，项目全景与 Roadmap 均存在。

## Allocation and Current Queue

创建 TASK-0021 前已从 Git 最新 `main@6610feff2acbb48e9058b237c3a12332394b7221` 完整枚举 `tasks/` 根目录；`TASK-0021` 未被占用，创建后复验为唯一 canonical 文件。

当前相关任务：

- `TASK-0016-Automatic-Cross-Conversation-Memory-Curation.md`：`Review`，安全加固继续在独立 worktree 处理；
- `TASK-0018-Huuuge-Lottery-Numerical-Breakdown-Report.md`：Huuuge Lottery 数值报告主线，范围不变；
- `TASK-0019-AI-Workspace-Overview-and-Separate-Progress-Documents.md`：`Ready`，其两份源稿将成为 Live Context 的重要输入；
- `TASK-0020-Task-Allocation-and-Namespace-Governance.md`：`Ready`，负责 Task Registry、allocator 和历史冲突治理；
- `TASK-0021-Workspace-Live-Context-Hub.md`：`Ready`，负责实时 Context、飞书协作、Workspace Sync 和行文规范。

历史 TASK-0018 编号冲突继续由 TASK-0020 处理。执行任何 0018 时必须使用完整文件名，不能只写编号。

## TASK-0021 Objective

解决 ChatGPT Project Sources 需要手工下载、编辑、重新上传，以及多个会话 / Agent 并行时上下文不能及时同步的问题。

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

核心要求：

1. 优先验证并采用飞书知识库；Wiki 条件不满足时使用专用飞书 Drive 文件夹 + Docx，不能回退到手工搬运 Markdown。
2. Git 继续是 Task、ADR、Capability、规则和实现状态的 canonical truth；飞书提供多人协作、在线编辑和面向人的入口。
3. Git-authoritative 内容只向飞书发布；飞书协作草稿进入 Memory Candidate / Review，不静默覆盖 Git。
4. ChatGPT 直接 Feishu MCP 暂不可用时，通过自动 Git mirror 获取最新 Context，不能把 Project Sources 当实时状态源。
5. 建立 `standards/PLANNER_WRITING_STYLE.md`，禁止单词 / 短句逐行排版，统一正常中文段落、结论—依据—下一步和策划步骤写法。
6. 为 ChatGPT、Codex、Trae / DeepSeek 提供各自的 Workspace Sync Binding；无法同步时明确显示 stale / unavailable。
7. 支持 OFF / ON_DEMAND / WATCH，Pilot 后默认 ON_DEMAND；未经 User 批准不得生产启用 WATCH。

## Confirmed Baseline

- ChatGPT Project Sources 是快照，动态状态当前仍需手工替换；
- AI Document Assistant 已支持飞书 Docx、Drive、搜索、创建、替换和权限管理；Wiki 工具目前只在架构中预留，尚未实现；
- ChatGPT 直接 Secure MCP Tunnel 目前受 OpenAI Control Plane 地区限制，Codex 本地 `feishu-docs` 正常；
- TASK-0016 已提供 Git-backed Memory Candidate、Review、Public / Private / Local-only 路由，可作为 Feishu 草稿入 Git 的基础；
- TASK-0019 将生成项目全景说明和项目进度文档，可由 TASK-0021 纳入 Live Context，但不得复制或覆盖其正在执行的工作。

## Shared Boundaries

- TASK-0021 必须先完成 Reuse-first Feasibility Audit，再决定 Feishu Wiki、Drive Folder 或其他 fallback；
- AI-Workspace 与 document-assistant 分别使用独立 branch / linked worktree；发现活动任务重叠时停止并报告；
- 不修改 Huuuge Collector、Lottery 报告数据、Capture、SVN、游戏请求、奖励、余额或服务器状态；
- 不把 Secret、Raw Capture、账号、完整响应、逐笔余额、Feishu token、document token、private URL 或本机 Registry 写入公共 Git、飞书正文或日志；
- 不把飞书设为代码、Task、ADR 或运行证据的唯一真相源；
- 不静默部署公网服务、付费 SaaS、GitHub Secret、管理员权限或生产 WATCH；
- 不自动合并冲突，不直接覆盖 `main`，不声称 Project Sources 已自动更新。

## Exact Next Action

ChatGPT Review Round 3 复审 TASK-0019 本轮新提交与原位飞书进度文档：确认正式 Collector READY 未被可复核证明，事实仅为临时 SSL 捕获后进入 User 操作阶段且游戏由 User 亲自操作；保留 RC4 `Pending`、实跑 `Failed/Invalid` 与 Bet/RTP `Unsupported`；确认 P0 Reliability Hardening Decision proposal 未批准且没有创建 Task。返回 `Accepted` 或精确修改项；Review 前不合并 main。
