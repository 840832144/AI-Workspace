# Game Planner AI Workspace｜项目进度与能力状态

> **As of**：2026-09-04 +08:00
>
> **AI-Workspace 核验基线**：`main@1dd6de3e244858c44b716cacd72961ea9419f564`
>
> **Git 源稿**：`docs/status/AI_WORKSPACE_PROJECT_PROGRESS.md`
>
> **项目全景**：[《Game Planner AI Workspace｜项目全景说明》](../overview/AI_WORKSPACE_PROJECT_OVERVIEW.md)
>
> **快照说明**：本文不是后台实时同步；以下结论来自该时点对 AI-Workspace、业务 `main`、本机 Workspace Sync 与 Document Assistant 的分别核验。
>
> **维护说明**：任务、能力成熟度、阻塞与下一步只在本文更新；稳定定位、架构与边界在项目全景说明维护。正式飞书链接由 Document Assistant 发布与导航中心登记，不写入公共 Git 源稿。

## 状态摘要

| 类别 | 数量 | 说明 |
| --- | ---: | --- |
| Capability `Available` | 7 | 有 Accepted/Complete、权威 `main`、测试或本机 healthcheck 支持，可在声明边界内使用 |
| Capability `Partial` | 4 | 主体存在，但当前 Provider、证据覆盖、人工步骤或同步闭环不完整 |
| Capability `Planned` | 3 | 只有稳定方向、模型或 Roadmap，尚无可验收实现 |
| Capability `Blocked` | 2 | 目标明确，但缺少外部验证或当前平台实现 |
| Canonical Work Items | 14 | Accepted 7、Complete 4、Review 2、Ready 1、In Progress 0 |
| Host readiness | Ready | Global + Project AGENTS 已加载，Subagents `OFF`，Git 可读写，Document Assistant healthcheck 成功 |

## 核验范围与真相源

| 真相源 | 核验版本 / 现场结果 | 确认结论 | 局限 |
| --- | --- | --- | --- |
| AI-Workspace | `main@1dd6de3e244858c44b716cacd72961ea9419f564`；TASK-0027 从该提交新建独立 linked worktree | allocator 以 remote-CAS 建立 TASK-0027；Phase A-D 已完成，当前分支进入 Review | 本分支尚未进入 main；reservation 保持 pending-main |
| Huuuge 业务仓库 | `main@4a5dddf7782307c6a8f368c9f1dc6390eec6f65b`；本地只读 clone 与 `origin/main` 一致、工作树干净 | Lottery 运行证据和 1.0.1 策划发布基线存在；本机正式 Collector 1.0.1 lifecycle 已达到 READY/Stop/Finalize；正式 RC4 记录仍为 `Pending`，User 提供的历史实跑仍为 `Failed/Invalid` | 本轮没有修改业务仓库；工程 lifecycle 不替代独立策划 First Run；Bet/RTP `Unsupported` |
| `CF_collect` | `main@4df10ec20e79bb737912c8d1b847fae3659031ae`；与 `origin/main` 一致、工作树干净 | TASK-0026 Review Round 3 Accepted；Collector 1.0 cleanup、固定六字段与测试已进入 `main` | Accepted 范围不包含新的字段、模块、Spin 或动态运行 |
| Document Assistant 实现 | `main@b0292c3159db16542906948511b6b1ec58c360fd`；与 `origin/main` 一致、工作树干净 | 当前 Host 可发现 `feishu-docs`；token、API connectivity、Drive permission healthcheck 均为 `ok` | Git 真相源与云文档仍需显式发布、回读、登记和权限验收 |
| Workspace Sync | `ON_DEMAND`；provider `unavailable`；stale 6；conflicts 0 | 本地 Context Pack 与 publish plan 可生成，冲突为 0 | 当前 Host 没有可用发布 Provider；6 个发布项仍 stale，不得写成已同步 |
| 当前 Windows 工作站 | Global AGENTS SHA-256 `41A5141D9DC4C026BA02D02258AC1EEEBEA658AEA63A103F3AB44A4998F20343`；Project AGENTS 已加载；Subagents `OFF` | 新工作站治理接入和 Document Assistant 已现场验收，可标记 `Ready` | “工作站 Ready”只描述 Host 接入，不替代任何游戏业务 First Run、采集或报告验收 |

> **两项 Provider 必须分开判断**：Workspace Sync Provider 当前为 `unavailable`；`feishu-docs` / Document Assistant 当前为 `Available` 且 healthcheck 成功。两者不是同一 Capability、同一进程或同一验收结果。

## 1. 当前能力矩阵

| Capability | User Outcome | Domain | Status | What Works Now | Entry / Provider | Evidence / Source | Known Limit | Exact Next Action | Last Verified |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Task / Review / Handoff 治理 | 把需求变成唯一、可执行、可审阅、可交接的 Task | Governance | Available | Candidate、全局 Task ID、Registry、remote-CAS allocator、Review、Handoff 与 fail-closed collision gate 已运行 | `tasks/`、`reviews/`、`handoff/`、`tools/tasks/task_cli.py` | TASK-0020 Accepted；TASK-0027 allocator reservation；Registry 14 canonical / 0 collision | Registry 是扫描生成索引，不是第二真相源 | TASK-0027 reservation 保持 pending-main，canonical 进入 main 后 finalize | 2026-09-04 |
| Capability Discovery / Catalog | 先确定结果契约，再选择实现 | Shared governance | Partial | CAP-DOC、CAP-MEM 已登记；CAP-CONTEXT 有 reference implementation | `capabilities/` | Capability Catalog；ADR-0003 | CAP-MEM/CAP-CONTEXT 文档中仍有状态陈述漂移；Catalog 尚未覆盖全部 Game Design outcome | 后续按独立 Review 更新契约状态；不从 Tool 名称反推能力 | 2026-08-29 |
| Document Capability（当前 Codex Host） | 搜索、读取、维护、发布和授权公司文档 | Shared platform | Available | `feishu-docs` Provider 可发现；healthcheck 的 token/API/Drive 三项均 `ok`；支持原位替换、回读、登记与授权 | AI Document Assistant / `feishu-docs` | 实现 `main@b0292c3`；本机 healthcheck | 飞书是展示层；搜索结果、Registry 与权限仍需每次发布现场核验 | 对两份正式文档执行 search/get → replace → get → permission verify → register → Hub readback | 2026-08-29 |
| Workspace Sync / Context | 在 Git、Host Context 与发布目标之间管理 freshness 和冲突 | Shared delivery | Partial | ON_DEMAND 可生成 Local Context Pack 与 publish plan；本次 0 conflict | `bootstrap/workspace-sync/Invoke-WorkspaceSync.ps1` | TASK-0021 Accepted；现场 `provider_available=false, stale=6, conflicts=0` | 当前 Workspace Sync Provider unavailable；6 项 stale；WATCH 关闭 | 保持 ON_DEMAND；由管理员/维护者恢复该 Provider 后重新 sync 并确认 stale 归零 | 2026-08-29 |
| Git-backed Memory | 将长期信息变成可验证、可路由、可回滚的 Candidate | Shared governance | Available | ASSISTED、hard-deny、Curator、Context refresh 与 Git-live-first 已通过 Review | CAP-MEM / `tools/memory/` | TASK-0016 Review Round 3 Accepted | Project Sources 仍需人工更新；Memory 不替代 Git 实时状态 | 只在实质 Task 后按 ASSISTED 流程维护；当前 Task 的 canonical update 不再制造重复 Candidate | 2026-08-29 |
| Codex Subagent Pilot | 在受限父会话中保守并行只读工作 | Shared operations | Available | OFF/MANUAL、单写入者和回滚脚本已 Accepted；当前 Host 状态可检测 | `bootstrap/codex/` | TASK-0014 Accepted；现场 `Current mode: OFF` | 当前会话为宽松权限，必须保持 OFF；Installed agents none | 本 Task 保持单 Agent；只有受限新会话和独立只读流才由 User 手动启用 | 2026-08-29 |
| Codex Desktop 网络诊断 | 诊断和回滚代理/WebSocket 连接问题 | Shared operations | Available | transport matrix、Repair/Restore 与回归已合入 | `bootstrap/codex/network/` | TASK-0017 Complete | Codex 或代理升级后需重验 | 仅在网络症状复现时运行 status/matrix，不叠加未验证配置 | 2026-08-29 |
| Huuuge Collector / Planner release | 在专用环境被动采集、解码、Finalize 并生成结构清单 | Huuuge | Available / laptop ready | SVN 1.0.1 来源、revision/hash/依赖、static preflight 与正式 lifecycle 已在笔记本核验 | 公司 SVN 1.0.1；Huuuge 业务仓库 | `C:\HuuugeCollector@r6701`；TASK-0027 Phase D | `Pie64_1 / 5565 / uid=0(root)` 已通过；app 更新后需重验 Gadget/config；本轮只做生命周期 | TASK-0027 Review；未来采集必须另给 Session scope | 2026-09-04 |
| Huuuge Knowledge / Analysis | 以证据等级查看 Slots、Systems、Events、Others | Huuuge | Partial | Slots 与 Lottery 有 L3 样本；37 个 dossier 形成结构索引 | Huuuge Knowledge Index / reports | `huuuge@4a5dddf`；TASK-0015 Complete | 0 个 L4；多模块仍 L1/L2；无稳定 RTP/EV 和 Bet 因果证据 | 未获独立 Task 与 User 操作授权前不新增 Capture；现有结论保持样本边界 | 2026-08-29 |
| Huuuge Planner First Run | 让未参与开发的策划在新电脑独立完成端到端流程 | Huuuge UX | Blocked | RC4 指南、飞书版与长期 Huuuge Research Laptop 已完成；正式 Collector lifecycle 已证明 READY/Stop/Finalize | First Run Guide / TASK-0027 Phase D | 正式 RC4 `Pending`；User 历史实跑 `Failed/Invalid`；Bet/RTP `Unsupported` | 尚无未参与开发策划的独立端到端记录；工程生命周期不能替代该证据 | User 指定独立策划后另行执行 RC4 First Run | 2026-09-04 |
| Collector 1.0 | 以固定 Adapter/Event/Session contract 复用 Cash 采集实现 | Game research | Available | Registry、统一 Event contract、固定 artifacts、精确 cleanup 和 0/1/N shape 已合入 `CF_collect/main` | `CF_collect` | TASK-0026 Review Round 3 Accepted；`main@4df10ec`；focused 16/16、cleanup 7/7、shape 10/10 | 六字段固定；没有新增模块、Spin 或运行验收 | 维持 Accepted 范围；任何新游戏/字段走新 Task 和独立证据 Gate | 2026-08-29 |
| ChatGPT Project Source Pack | 为新会话提供脱敏 Workspace 快照 | Shared context | Partial | 可生成 manifest 与单文件 Source Pack | Memory Context refresh | TASK-0016 Accepted；现有 generated pack | 快照会落后于 Git；本 Task 改动后需刷新/重新上传 | 本分支刷新 generated pack；合入后由 Project Sources 使用者替换旧快照 | 2026-08-29 |
| AI Report Engine | 从已审阅 Knowledge + Template 生成可维护报告 | Game Design | Planned | 只有分层架构、报告样例和 Candidate | 尚无批准实现 | Architecture / Roadmap | 没有稳定输入 schema、模板 contract、回归与 provider | 由 User 批准独立 Candidate 后再定义最小 Report Capability | 2026-08-29 |
| Planner Toolkit / 可执行 Skills | 复用 Slots、Lottery、Economy、Excel/SQL/Python 等策划方法 | Game Design | Planned | Skill Tree 和部分模板已定义 | `skills/`、`templates/` | RFC-0003 Proposed | 多数为模型分类，不是可执行且有回归的 Skill | 从 Accepted、证据完整的分析中另立 Task 抽取首个可回归 Skill | 2026-08-29 |
| 多实例 / 多账号脱敏聚合 | 隔离单账号事实并在统一口径后比较 | Game research | Planned | 有隔离原则与 Collector Adapter 边界 | Architecture / Roadmap | RFC-0004 Proposed；TASK-0026 boundary | 没有通用独立数据库和跨账号聚合实现；Raw 不得混合 | 先完成单游戏独立 Session 设计 Review，再由 User 授权聚合方案 | 2026-08-29 |
| ChatGPT 直接飞书写入 | 让 ChatGPT Control Plane 直接发布公司文档 | Shared platform | Blocked | 当前 Codex Host 可通过本地 Document Assistant 完成交付 | Secure MCP Tunnel / Codex local provider | Current State；Document Assistant healthcheck | ChatGPT 直连仍受平台地区限制；这不影响当前 Codex Host 的文档能力 | 继续由当前批准 Codex Host 写入；不建立未批准 tunnel | 2026-08-29 |

## 2. 当前任务与主线 / 支线

| Task / Work Item | Mainline or Side | Priority | Status | Owner / Executor | Current Result | Blocker / Dependency | Exact Next Action | Evidence / Source | Last Verified |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-0014 Codex Subagent Pilot | 支线：协作运行 | P1 | Accepted | ChatGPT / Codex | OFF/MANUAL、单写入者与只读角色被接受 | MANUAL 依赖受限父会话 | 当前保持 OFF | Task / Accepted decision | 2026-08-29 |
| TASK-0015 Huuuge Lottery Live Breakdown | 主线：Huuuge Evidence | P0 | Complete | User / Codex | finalized Lottery 样本与清单已完成 | Raw 继续留本机 | 保持证据封存 | Task / Huuuge `4a5dddf` | 2026-08-29 |
| TASK-0016 Memory Curation | 主线：治理 | P1 | Accepted | User / ChatGPT / Codex | Round 3 已接受，ASSISTED 生效 | 无当前 blocker | 按规则使用，不扩展为通用服务 | Review 3 / Task | 2026-08-29 |
| TASK-0017 Codex Network Recovery | 支线：运行可靠性 | P0 | Complete | User / Codex | 诊断、修复、Restore 与回归合入 | 升级后需重验 | 症状复现时运行 matrix | Task / Handoff | 2026-08-29 |
| TASK-0018 Huuuge Lottery Report | 主线：业务分析 | P0 | Review | User / ChatGPT / Codex | 报告与飞书原文档已更新，Round 1 修订完成 | 等待 ChatGPT Review Round 2 | ChatGPT 返回 Accepted 或精确修改项 | Workspace Project Status / Huuuge `4a5dddf` | 2026-08-29 |
| TASK-0019 Workspace Overview + Progress | 已完成：项目可见性 | P1 | Accepted | User / ChatGPT / Codex | Review Round 3 Accepted；两份文档职责、First Run 事实、Provider 分离与在线进度入口收口 | 无 | 保持进度文档更新规则 | Review Round 3 / canonical Task | 2026-08-29 |
| TASK-0020 Task Governance | 主线：治理 | P0 | Accepted | User / ChatGPT / Codex | Registry、allocator、CAS 与 collision gate 生效 | 无当前 blocker | 所有新 Task 继续走 Candidate/allocator | Review / Task CLI | 2026-08-29 |
| TASK-0021 Workspace Live Context Hub | 主线：协作基础设施 | P0 | Accepted | User / ChatGPT / Codex | Documentation Hub 与 ON_DEMAND Sync contract 已交付 | 当前 Host Sync Provider unavailable，6 stale | 修复 Provider 后重跑 ON_DEMAND | Review / sync output | 2026-08-29 |
| TASK-0022 Cash Frenzy Feasibility | 主线：新游戏研究 | P1 | Complete | User / ChatGPT / Codex | F3 outbound 边界与停止路线已完成 | F4 未证明 | 不在已完成 Task 内续做 | Review 1 Accepted / Task | 2026-08-29 |
| TASK-0023 Idea Governance | 主线：产品治理 | P1 | Accepted | User / ChatGPT / Codex | Product Roadmap、Idea Governance 与写作规范生效；Collector 1.0 已归入 Done，TASK-0027 进入 Current | 无当前 drift | 按 Task 状态继续维护 | Review 2 / Roadmap | 2026-09-04 |
| TASK-0024 Inbound Structured Capture Spike | 主线：Cash evidence | P1 | Complete | User / ChatGPT / Codex | F3 strengthened，5/5 六字段，F4 未证明 | 已达到 Stop Gate | 不在该 Task 内做完整 Collector | Review 1 Accepted / Task | 2026-08-29 |
| TASK-0025 Top Tycoon F4 Audit | 支线：新游戏 | P1 | Ready | User / ChatGPT / Codex | Canonical Task 已就绪但未开始 | User 尚未切回该方向 | User 明确恢复后再做现场 identity Gate | Task / Handoff | 2026-08-29 |
| TASK-0026 Collector 1.0 Engineering | 主线：Collector | P1 | Accepted | User / ChatGPT / Codex | 两个 `main` 已对齐；cleanup、shape 与固定六字段 Review 通过 | 无当前 blocker | 保持边界，任何扩展另立 Task | Review 3；CF `4df10ec` | 2026-08-29 |
| TASK-0027 Huuuge Research Laptop Reliability | 主线：Huuuge First Run | P0 | Review | User / ChatGPT / Codex | 长期 `Pie64_1 / 5565 / Root ON` 研究环境与正式 1.0.1 lifecycle 已通过 | 无实施 blocker；尚待 Review | 审阅 Phase D 结果；不自动开始新 Session | canonical Task / Phase D setup | 2026-09-04 |

## 3. 已完成里程碑

1. **任务治理闭环**：TASK-0020 Accepted；14 个 canonical Task 可由完整扫描重建，编号冲突 fail closed。
2. **Workspace Sync 与文档导航治理**：TASK-0021 Accepted；ON_DEMAND、冲突模型、唯一文档导航中心、自动登记和回读规则已建立。当前 Provider unavailable 是 Host 绑定状态，不撤销已接受的 contract。
3. **Memory 与 Idea Governance**：TASK-0016、TASK-0023 Accepted；ASSISTED Memory、Git-live-first、唯一 Product Roadmap 与写作规范生效。
4. **Cash Frenzy 到 Collector 1.0**：TASK-0022 Complete、TASK-0024 Complete、TASK-0026 Accepted；`CF_collect/main@4df10ec` 为当前实现真相源。
5. **Huuuge 证据基线**：TASK-0015 Complete；Huuuge 1.0.1 与 Lottery 运行样本有权威 commit/release 依据。TASK-0018 报告仍在 Review，不计作 Accepted 里程碑。
6. **当前新工作站接入**：Global + Project AGENTS、Git、Subagents OFF 与 Document Assistant 已现场验收，Host readiness 为 `Ready`。
7. **TASK-0027 Huuuge Research Laptop**：原 `Pie64 / 5585 / Root OFF` 保留；独立研究 clone 已对齐 `Pie64_1 / 5565 / Root ON`。正式 Collector 1.0.1 完成 READY、15 秒无操作 Session、Stop 与 Finalize，RPC/decoded `61/61`；最终 run-owned process、Frida server、forward 与临时 residual 均已清理。

## 4. 未完成与阻塞项

| 项目 | 缺少什么 / 为什么未完成 | 当前阻塞 | 解除条件 | 唯一下一步 | 是否影响主线 |
| --- | --- | --- | --- | --- | --- |
| Huuuge First Run | 正式 RC4 记录仍为 `Pending`；User 历史实跑为 `Failed/Invalid`；TASK-0027 已证明正式 Collector lifecycle READY/Stop/Finalize | 只缺未参与开发策划的独立端到端记录；工程生命周期不是 RC4 盲测 | User 指定独立策划并单独授权 First Run | 等待独立 RC4 First Run，不复用本轮工程结果冒充通过 | 是：不能宣称新人端到端通过 |
| Huuuge Bet / RTP | 没有 Bet 分层的受控运行样本、长期统计或可证明 RTP/EV 的证据；描述性 bundle ratio 与单次 Win 不是 RTP | Bet/RTP `Unsupported`，且本 Task 禁止动态采集 | 只有独立决策获批后才能讨论证据设计 | 保持 `Unsupported`；不得由本提案自动创建 Bet/RTP Task | 否：不影响现有结构/Collector，但影响数值结论 |
| TASK-0018 | Lottery 报告 Round 2 未完成 | ChatGPT Review | Accepted 或完成指定修订 | ChatGPT 审阅 `huuuge@4a5dddf` 与原飞书文档 | 是：Huuuge 报告线 |
| Workspace Sync Provider | provider unavailable，6 个 stale | Host 实现绑定缺失/不可用 | Provider 恢复且 ON_DEMAND 后 stale=0、conflict=0 | 管理员/维护者恢复 Provider 后重跑脚本 | 否：Git 与 Document Assistant 可独立工作 |
| TASK-0025 | 已 Ready 但未开始 | 当前优先级未切回 | User 明确恢复方向并完成现场 identity Gate | 等待 User 决定 | 否 |
| AI Report Engine / Planner Toolkit | 只有架构、Roadmap 或模型 | 无正式实现 Task | User 批准 Candidate 并完成 contract/回归 | 保持 Planned | 否 |

## 5. 当前可直接使用的入口

| 入口 | 用途 | 成功表现 | 失败处理 | 依据 |
| --- | --- | --- | --- | --- |
| AI-Workspace `main` | 读取规则、Task、Review、Status、Handoff | `main` 与 `origin/main` 一致，Registry valid | 有本机改动时使用独立 worktree，不覆盖 | `1dd6de3` 基线 |
| `tools/tasks/task_cli.py` | 扫描、校验和重建 Task Registry | 14 canonical、0 collision、status valid | 任一 drift/collision 即停止 | TASK-0020 Accepted / TASK-0027 reservation |
| `bootstrap/workspace-sync/Invoke-WorkspaceSync.ps1` | 生成 ON_DEMAND Context Pack 和发布计划 | 输出 mode/provider/stale/conflict | provider unavailable 时只报告，不借用 feishu-docs 代替 | TASK-0021 Accepted |
| Document Assistant / `feishu-docs` | 搜索、读取、原位更新、登记与授权飞书文档 | healthcheck token/API/Drive 为 ok；写后 get + permission + Hub readback | 失败保留原 document ID，不重复创建 | 本机 healthcheck / `b0292c3` |
| 项目全景说明 | 了解长期定位、架构和边界 | 稳定内容与动态进度分离 | 动态状态只查本文 | Git 源稿 / 原位飞书文档 |
| 项目进度与能力状态 | 查看当前能力、任务、阻塞和唯一下一步 | As of、commit、矩阵、任务和阻塞一致 | 先回到 Git 真相源核验，再原位 replace | 本 Git 源稿 / 原位飞书文档 |
| Huuuge 1.0.1 策划入口 | 使用已发布的专用研究流程 | 预检、READY、Finalize 与清单满足发布口径 | 首次环境授权或独立盲测失败时停止并记录 | `huuuge@4a5dddf` / SVN 1.0.1 |
| `CF_collect/main` | 维护 Accepted Collector 1.0 | main=`4df10ec`，固定测试通过 | 不扩大六字段或动态范围 | TASK-0026 Review 3 |
| `Get-CodexSubagentStatus.ps1` | 查看当前协作模式 | `Current mode: OFF` | 宽松父会话继续保持 OFF | TASK-0014 / 本机输出 |

## 6. 可额外开展的支线任务

以下均为 `Candidate`，不因出现在本文而获得执行授权或 Task ID。

| Candidate | Expected Value | Prerequisite | Risk / Cost | Mainline Impact | Suggested Trigger | Recommended Priority |
| --- | --- | --- | --- | --- | --- | --- |
| AI Report Engine 最小 contract | 将已审阅 Knowledge 稳定组装为报告 | 一个 Accepted 业务报告样例、输入 schema、模板与回归 | 容易把生成文本误当事实 | 中 | TASK-0018 Accepted 后 | P1 |
| Planner Toolkit 首个可执行 Skill | 把成熟分析方法变成策划可复用入口 | 选定单一、证据完整的方法 | 过早泛化会制造空壳 Skill | 低 | Report contract 稳定后 | P1 |
| Huuuge Bet / RTP 证据计划 | 回答 Bet 档位与 RTP/波动是否存在可证关系 | User 明确批准、统计设计、最小样本、独立 Session 与安全 Gate | 时间/资源成本高；错误外推风险高 | 低 | 业务决策确实需要该结论时 | P1 |
| 多实例 / 多账号脱敏聚合 | 支持分群与跨账号比较 | 单账号 schema 稳定、隔离数据库、隐私 Review | Raw 混污、隐私和假规律风险 | 中 | 至少两个独立、可比 Session 后 | P2 |
| 新游戏 Adapter | 复用 Collector 1.0 生命周期 | User 批准具体游戏 Task、identity Gate、独立数据目录 | 不能借用 Cash/Huuuge schema | 中 | TASK-0025 恢复或新 Candidate 被批准 | P1 |
| Documentation Portal / Recent Updates | 改善策划浏览体验 | 定义真相源、维护成本、与 Hub 边界 | 可能制造第三套状态源 | 低 | User 明确需要门户而非现有 Hub | P2 |

## 7. 风险、依赖与治理问题

| 风险 / 依赖 | 当前事实 | 可能后果 | 控制措施 |
| --- | --- | --- | --- |
| Workspace Sync 与 feishu-docs 混淆 | 前者 provider unavailable/stale 6；后者 healthcheck 全部 ok | 把文档可写误报成 Workspace 已同步，或反之 | 分别运行、分别记录、分别验收；一个结果不得替代另一个 |
| Huuuge First Run 误报 | 正式 RC4 `Pending`、User 历史实跑 `Failed/Invalid`；TASK-0027 已证明本机正式 Collector READY/finalize/cleanup，但没有独立策划盲测 | 把工程生命周期通过误报成 RC4 端到端通过 | First Run 继续 Blocked；只有独立 RC4 证据才能解除，TASK-0027 生命周期只解决环境可靠性 |
| Bet / RTP 无证据外推 | 当前样本没有稳定 RTP/EV 或 Bet 因果证据，结论为 Bet/RTP `Unsupported` | 把单次 Win、字段或描述性比率误作概率结论 | 保持 `Unsupported`；独立决策批准前不建立统计 Task |
| 历史 TASK-0018 文件冲突 | canonical 为 `tasks/TASK-0018-Huuuge-Lottery-Numerical-Breakdown-Report.md`；历史 `tasks/TASK-0018-Cash-Frenzy-Android-Collector-Feasibility-Audit.md` 是已取消 companion | 只写编号会把 Huuuge 报告与 Cash Frenzy 历史审计混为同一执行入口 | 始终使用完整文件名并核对 Registry kind/status；不得从历史 companion 启动执行 |
| ChatGPT 直写飞书地区限制 | ChatGPT Control Plane 的 Secure MCP Tunnel 仍受地区限制；当前 Codex Host 的本地 Document Assistant 独立可用 | 把 ChatGPT 直连受阻误写为 Document Capability 不可用，或建立未批准 tunnel | 两条实现路径分别验收；继续使用当前批准 Codex Host，不绕过地区或组织策略 |
| 飞书与 Git 漂移 | 云文档可被手工修改，Git 分支仍在 Review | 在线状态过时或先于权威分支 | 顶部固定 As of/commit/source；只原位 replace；写后 get + permission + register + Hub readback |
| Project Source Pack 滞后 | 生成包与上传 Sources 是快照 | 新会话读取旧 Task/优先级 | Git-live-first；本分支刷新生成包，合入后人工替换 Sources |
| 私有业务仓库访问 | 新人不应依赖私有实现仓库 | Onboarding 在权限阶段卡住 | 新人只需公共 AI-Workspace、公司 SVN 与管理员预配 Provider；维护者才核验私有 commit |
| Roadmap 与 Task 状态漂移 | Product Roadmap 已将 TASK-0026 对齐到 Done，并把已批准 TASK-0027 放入 Current | 后续状态变化仍可能使页面过时 | 每次 Task 阶段变化同步 Roadmap；Task/Review/main 继续是执行真相源 |
| 多工作区并发 | 多个 worktree/branch 同时存在 | 覆盖、误提交或发布瞬间过时 | 每 Task 独立 worktree；主 Agent 单写入；提交前 fetch/validate；不合并旧 TASK-0019 分支 |
| Huuuge Raw / 多账号隔离 | Raw 可能含账号、Session、逐笔余额 | 泄露、样本混污、假规律 | 每实例/账号独立库；先单账号再脱敏聚合；Raw 不进 Git/飞书/聊天 |
| 能力名称与成熟度混淆 | Architecture/Roadmap/Tool 可见不等于 Available | 把计划或接口误写成已交付 | 每个 Available/Complete 至少附 Accepted Review、main、test、release 或 healthcheck |

## 8. 更新规则

本节是本文内置维护流程，不创建第三份用户文档。

1. **触发时机**：Task 状态、ChatGPT Review、权威 `main`、release/SVN、Capability healthcheck、Provider 状态、阻塞或 User 优先级变化后更新。
2. **先更新真相源**：业务实现先进入业务仓库；Task/Review/Capability/Handoff 先进入 AI-Workspace；release 先进入批准分发系统。不要先在飞书宣布完成。
3. **同步 AI-Workspace**：从 clean `main` 执行 `fetch` 与 `pull --ff-only`；读取全量 Task/Registry、Project Status、Review、CHANGELOG 和 Handoff；并行任务使用独立 worktree。
4. **分别核验 Provider**：运行 Workspace Sync 并记录 mode/provider/stale/conflict；另行运行 `feishu_healthcheck` 并记录 token/API/Drive 安全状态。禁止合并成一个“Provider 正常/异常”。
5. **核验业务 main**：记录业务 `HEAD`、`origin/main` 与工作树；每个 `Available/Complete` 至少有 Accepted Review、main commit、test、release、runtime evidence 或 healthcheck。
6. **更新 Git 源稿**：修改本文的 As of、commit、状态数量、矩阵、任务、阻塞、风险和下一步；项目全景说明只在稳定定位/架构变化时更新，不复制动态任务清单。
7. **飞书防重**：先按精确标题执行 `search_documents`；若 Registry 搜索无结果但 canonical Git/已登记链接存在，必须对原 document ID 执行 `get_document` 并核对唯一标题，不能创建副本。
8. **原位发布**：对唯一原文档使用 `replace_document`；不使用 `create_document` 生成日期副本。发布内容与 Git 源稿保持相同 As of、基线、状态摘要和关键口径。
9. **回读验收**：分别 `get_document` 回读标题、As of、commit、状态摘要、First Run、Workspace Sync、Document Assistant 与 Bet/RTP 风险；确认原 document ID 未变。
10. **权限与导航**：确认企业内可编辑权限；调用 `register_document` 更新唯一文档导航中心，再回读 Hub，确认标题和链接各出现一次。
11. **失败处理**：healthcheck 失败则停止云写入；replace/权限/登记/Hub 回读任一步失败都保留原 document ID、记录准确错误并等待修复，不重复创建。
12. **提交与 Review**：运行 Registry validator、Markdown/link/secret scan、`git diff --check` 和相关回归；提交并 push 独立分支，只等待 ChatGPT Review，不自行合并 `main`。

## 证据索引

- AI-Workspace `main@c74c85a9524d1524ea3696835509de2a55e9f524`
- Huuuge `main@4a5dddf7782307c6a8f368c9f1dc6390eec6f65b`
- CF_collect `main@4df10ec20e79bb737912c8d1b847fae3659031ae`
- Document Assistant `main@b0292c3159db16542906948511b6b1ec58c360fd`
- TASK-0026 ChatGPT Review Round 3 — Accepted
- TASK-0019 ChatGPT Review Round 1 — Needs changes；reviewed commit `9403a09a445fd37548c78b3fc21709e91f5406d9`
- TASK-0019 ChatGPT Review Round 2 — Needs changes；reviewed commit `e05d781e8aa54a6d10f1d0e44a1f84310fdf847e`
- TASK-0019 ChatGPT Review Round 3 — Accepted；reviewed commit `ccc1610a69808f7516e4d215d2177454021d108a`
- `projects/huuuge-android-research/STATUS.md`
- `projects/huuuge-android-research/REPORTS/TASK-0011-FIRST-RUN-VALIDATION.md`
- `capabilities/README.md`
- `handoff/CODEX.md`
