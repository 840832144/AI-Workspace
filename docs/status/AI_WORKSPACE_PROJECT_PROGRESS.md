# Game Planner AI Workspace｜项目进度与能力状态

> **As of**：2026-08-27 15:22 +08:00
> **AI-Workspace 基线**：`main@070744944d02b8d493c737db74bdc3d404963158`
> **Git 源稿**：`docs/status/AI_WORKSPACE_PROJECT_PROGRESS.md`
> **项目全景**：[《Game Planner AI Workspace｜项目全景说明》](https://gfok27asqq.feishu.cn/docx/ZCssdia58oekMSxvwGYchxWNneh)
> **快照说明**：本文不是后台实时同步；以上述时点对 Git、业务仓库、SVN 与 Document Assistant 的实际核验为准。
> **维护说明**：任务、能力成熟度、阻塞与下一步只在本文更新；稳定架构在全景说明维护。

## 状态摘要

| 类别 | 数量 | 说明 |
| --- | ---: | --- |
| Capability `Available` | 5 | 有已批准/已合入实现与近期验证，在声明的 Host/环境中可用 |
| Capability `Partial` | 4 | 主体可用，但有 Review、人工步骤、证据覆盖或安全闭环缺口 |
| Capability `Planned` | 4 | 只有 Roadmap/架构/Candidate，没有可验收实现 |
| Capability `Blocked` | 2 | 目标明确，但受外部验证或平台限制阻塞 |
| 当前 Work Items | 9 | Accepted 1，Complete 2，Ready 2，Changes Requested 1，Review 2，Cancelled 1；Lottery 报告待 Review，TASK-0020/0021 已 Ready |

## 核验范围与真相源

| 真相源 | 核验版本 | 确认结论 | 局限 |
| --- | --- | --- | --- |
| AI-Workspace | `main@0707449` | 已读 Task headers、Status、Review、最新 ChatGPT/Codex Handoff、Capability、RFC/ADR、Roadmap、Workflow、Skill/Template/Standard；纳入 Lottery 报告交接与 TASK-0021 Live Context Hub | ChatGPT Project Source Pack 是快照；main Handoff 中 TASK-0019 仍是 Ready，当前分支 Task header 已进入 Review |
| `huuuge-android-research` | `main@bfed5f30e098522ffb98ef5eb7d63e824d68b1c4` | 本地与远程一致且工作树干净；TASK-0015 Finalize、Lottery 报告、6 份脱敏 CSV、Extractor 与测试已提交 | 报告仍等待 ChatGPT Review；Raw、账号和逐笔余额不进入 Workspace |
| 公司 SVN `trunk/HuuugeCollector` | r6429；手册/Installer 1.0.1 | 工作副本清洁；r6429 是 1.0.1 策划说明与下载入口；已记录包 SHA-256 与白名单 | 新机首次认证、专用实例和 Root/host 修改仍需 User 参与/授权 |
| `document-assistant` | `main@23197e2e57fb762d112c4d3429314ac6a6a5d0b8`；package 0.3.0 | 本地仓库 clean；当前 Codex Host 的 environment/token/API/Drive healthcheck 均为 ok；搜索、读取、创建、追加、替换、目录和授权工具可见 | ChatGPT 直连 Secure MCP Tunnel 受平台地区限制；当前由 Codex 执行飞书写入 |
| 已登记业务项目 | `projects/huuuge-android-research/` | AI-Workspace 当前只正式登记 Huuuge 一个业务项目 | Cash Frenzy 只保留为 Candidate，原冲突 Task 已 Cancelled，业务仓库未创建；CR 不是已登记 Project |

## 1. 当前能力矩阵

| Capability | User Outcome | Domain | Status | What Works Now | Entry / Provider | Evidence / Source | Known Limit | Exact Next Action | Last Verified |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Task / Review / Handoff 治理 | 将需求变成可执行、可审阅、可交接任务 | Governance | Available | Task 状态词汇、范围/验收/安全契约、ChatGPT Review 和固定 Handoff 均已用 Git 运行；冲突已 fail-closed 止损 | `tasks/`、`reviews/`、`handoff/` | RFC-0001 Accepted；`tasks/README.md`；`main@0707449` | 自动 Registry/allocator/并发锁尚未实现 | 执行 TASK-0020 建立 Registry、`scan/validate/next/candidate/promote` 和 ADR-0006 | 2026-08-27 15:22 +08 |
| Capability Discovery / Catalog | 先识别结果契约，再选 Provider/Tool | Shared governance | Partial | Global 和 Project AGENTS 已执行 Capability-first；Catalog 登记 CAP-DOC 与 CAP-MEM | `capabilities/`、Global AGENTS | ADR-0003 Accepted；Catalog `main@0707449` | 仅两个契约；CAP-DOC/CAP-MEM 仍等待 Review；无内建 resolver | ChatGPT 审阅现有 contract，再按 Game Design 成果扩展 | 2026-08-27 15:22 +08 |
| Document Capability（Codex Host） | 搜索、读取、创建/更新公司文档并验权 | Shared platform | Available | healthcheck；search/get/create/append/replace；folder；company/group/user edit；默认企业可编辑 | AI Document Assistant / `feishu-docs` | `document-assistant@23197e2`；2026-08-27 healthcheck all ok；CAP-DOC | 契约尚待 ChatGPT Review；飞书是展示层，不是 Git 真相源 | 对每次发布坚持 search → create/replace → get → permission verify | 2026-08-27 15:00 +08 |
| Huuuge Collector / Planner release | 在专用环境被动采集、解码、Finalize 并产生结构清单 | Huuuge | Available | 环境预检、READY、广泛 RPC、protobuf decode、manifest、lifecycle markers、Clean Finalize、inventory/catalog | SVN 1.0.1；`HUUUGE_BOOTSTRAP.cmd`、`HUUUGE_COLLECTOR.cmd` | `huuuge@bfed5f3`；SVN r6429；Lottery 8712/8712；1.0.1 发布记录 | 新机首次 Root/host 修改需 User 授权；不是所有模块都有 dedicated runtime evidence | 保持被动采集边界；Review 前不新开 Capture 或修改 Collector | 2026-08-27 15:17 +08 |
| Huuuge Knowledge / Analysis | 查看 Slots、Systems、Events、Others 的结构与证据等级 | Huuuge | Partial | 37 dossier；L3 12、L2 3、L1 22；Lottery 报告、6 份脱敏 CSV 与最小 Extractor 已提交 | Huuuge Knowledge Index / module catalog | Workspace Status；`huuuge@bfed5f3`；Lottery 飞书回读 | 0 个 L4；升级因果仅 Estimate L3；通用 Missions、Battle Pass 等证据不完整 | ChatGPT Review Lottery claim 分类、升级归因边界和 CR Candidate | 2026-08-27 15:17 +08 |
| Planner First Run | 新策划仅用公共 Workspace、SVN 和预配文档能力完成首次流程 | Huuuge UX | Blocked | RC4 指南、12 步新人主线、飞书版和验收模板已存在 | First Run Guide / Feishu | `projects/huuuge-android-research/STATUS.md`；company-editable 回读 | 尚无未参与开发的策划完成独立盲测，不能声称真实耗时/独立通过 | User 指定一位未参与开发的策划，仅给公共 Git + 飞书指南执行并记录 | 2026-08-27 15:00 +08 |
| Git-backed Memory | 将跨对话长期信息变成可路由、可 Review、可回滚的 Git Candidate | Shared governance | Partial | OFF/ASSISTED/AUTO；public/private/local 路由；transactional AUTO；Context refresh；34 项旧回归与 Pilot | CAP-MEM / `tools/memory/` | TASK-0016；`main@797bb79`；Review Round 2 | Review 2 发现 ASCII `-` provenance 和 `sensitivity=secret` Registry hard-deny 两个安全漏洞；production Hook/AUTO 关闭 | 修复两个漏洞，参数化覆盖占位符，添加恶意 Registry 回归，等待 Review Round 3 | 2026-08-27 15:00 +08 |
| Codex Subagent Pilot | 对独立、读多写少工作安全并行，可一键关闭 | Shared operations | Available | 1 主 + 4 只读 Agent；OFF/MANUAL；单写入者；安装原子性和 fail-closed 回归 | `bootstrap/codex/` | TASK-0014 Accepted；ADR-0004；Pilot 验证 | MANUAL 严禁与 full-access/yolo 并用；当前宽松权限会话必须 OFF | 仅在父会话受限且任务确有独立并行流时由 User 手动启用 | 2026-08-27 15:00 +08 |
| Codex Desktop 网络诊断/恢复 | 定位 WebSocket/代理/TLS 问题并最小可回滚修复 | Shared operations | Available | 状态、transport matrix、Repair、Restore、PowerShell 5.1 回归；当前 HTTP 101 | `bootstrap/codex/network/` | TASK-0017 Complete；`main@aa18233`；2026-08-27 transport status | `respect_system_proxy` 是当前版本验证 feature，升级后需复测；外壳正常重启待 User 方便时确认 | Codex 升级或代理改变后重跑 matrix；不叠加未验证环境变量 | 2026-08-27 15:00 +08 |
| ChatGPT Project Source Pack | 为新对话生成安全的 Workspace 上下文包 | Shared context | Partial | Manifest、Source Pack、replacement list 可一键生成；上次 refresh 42 sources、0 Secret issue、0 broken link | Memory Refresh | TASK-0016 Handoff；`PROJECT_SOURCE_PACK.md` | ChatGPT Project Sources 需人工上传；动态 Task/Status 会滞后 | TASK-0016 先完成安全修复；TASK-0021 再建立 authority 明确的 Live Context / Sync | 2026-08-27 15:17 +08 |
| AI Report Engine | 从已审阅 Knowledge + Template 生成可维护报告 | Game Design | Planned | 只有分层架构与 Candidate，无通用生成逻辑 | 未实现 | `bootstrap/chatgpt/01_SYSTEM_CONTEXT.md`；TASK-0019 边界 | 没有稳定输入 schema、template contract、回归和 provider | 在 Huuuge Lottery 人工报告固化口径后，另立 RFC/Task 定义最小 Report Capability | 2026-08-27 15:00 +08 |
| Workspace Live Context / Sync | 用 authority、白名单、冲突与 freshness 管理 Git、飞书和 Host Context | Shared delivery | Planned | Huuuge 有项目专属 SVN 同步；飞书可由 Codex 手动发布；完整实现 Task 已 Ready | TASK-0021 / Roadmap Phase 3 | `TASK-0021-Workspace-Live-Context-Hub.md`；Document Assistant Roadmap | Wiki 能力、通用同步契约、revision 冲突、自动 freshness 均未验证/实现 | 按 TASK-0021 先做 Feasibility Audit；未满足 Wiki 条件时使用唯一 Drive Folder MVP，不伪称知识库 | 2026-08-27 15:17 +08 |
| Planner Toolkit / 可执行 Skills | 复用 Slot、Lottery、Economy、Task、Excel/SQL/Python 等策划方法 | Game Design | Planned | 11 类 Skill Tree 和项目模板已定义 | `skills/`、`templates/` | `skills/README.md`；RFC-0003 Proposed | 所有 Skill 分类均是 Model only / Not implemented | 从已完成、有证据的 Lottery/Slot 分析中抽取第一个可回归 Skill | 2026-08-27 15:00 +08 |
| 多游戏/多实例数据层 | 每游戏独立 Adapter，每账号独立库，脱敏聚合后比较 | Game research | Planned | 隔离原则、字段契约和 Cash Frenzy Candidate 方向已记录 | Candidate / architecture only | `01_SYSTEM_CONTEXT.md`；Cash Frenzy Cancelled incident；TASK-0020 | 尚无独立业务仓库/动态证据；原冲突 Task 不可执行；无跨账号脱敏聚合实现 | TASK-0020 Accepted 后由 User 确认，再以唯一 ID 重发 Cash Frenzy Feasibility Audit | 2026-08-27 15:11 +08 |
| ChatGPT 直接飞书写入 | 让 ChatGPT 直连 Document Assistant 执行文档交付 | Shared platform | Blocked | Codex 本地 STDIO Provider 可代执行，文档 contract 不受影响 | Secure MCP Tunnel | `02_CURRENT_STATE.md`；Document Assistant README | OpenAI Control Plane 返回 `unsupported_country_region_territory` | 保持 Codex 作为当前写入 Host；等平台/地区状态变化后重验，不自建未批准 tunnel | 2026-08-27 15:00 +08 |

## 2. 当前任务与主线 / 支线

| Task / Work Item | Mainline or Side | Priority | Status | Owner / Executor | Current Result | Blocker / Dependency | Exact Next Action | Evidence / Source | Last Verified |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `TASK-0014-Codex-Subagent-Pilot.md` | 支线：协作运行 | P1 | Accepted | ChatGPT / Codex | 1+4 只读 Pilot 和 OFF/MANUAL 被接受 | MANUAL 必须使用受限父会话 | 按需使用，本任务不重新实施 | Task header；ADR-0004；`8f50cb3` | 2026-08-27 15:00 +08 |
| `TASK-0015-Huuuge-Lottery-Live-Numerical-Breakdown.md` | 主线：Huuuge 证据 | P0 | Complete | User / Codex | finalized alias `LOT-20260827-A` 已验证 stopped、4 markers、8712/8712 decode；Task 与 Status 已对齐 | 无实施 blocker；Raw 继续只留本机 | 保持证据封存，不因后续报告 Review 重新采集 | Task header；Huuuge `bfed5f3`；Workspace `828d3a7` | 2026-08-27 15:17 +08 |
| `TASK-0016-Automatic-Cross-Conversation-Memory-Curation.md` | 主线：治理安全 | P1 | Changes Requested（Task header=Review） | User/ChatGPT / Codex | Round 1 三项主体修复通过；Review 2 又发现两个安全漏洞 | ASCII `-` 可绕过 provenance；Registry 可误放宽 `secret`；`local-only` 需 hard deny | 修复硬边界、补参数化/恶意 Registry 测试，更新 contract 并等 Review 3 | Review 2 `d78edd9`；Task；`main@797bb79` | 2026-08-27 15:00 +08 |
| `TASK-0017-Codex-Desktop-Proxy-WebSocket-Reconnect.md` | 支线：运行可靠性 | P0 | Complete / merged | User / Codex | 根因确认；修复、Restore、3 次新任务和 HTTP 101 通过 | 完整 Desktop 外壳正常重启留待 User 方便时确认 | 升级/代理变化后重跑 status/matrix | Task；`aa18233`；transport status | 2026-08-27 15:00 +08 |
| `TASK-0018-Huuuge-Lottery-Numerical-Breakdown-Report.md` | 主线：业务分析 | P0 | Review | User/ChatGPT / Codex | Git/飞书中文报告、6 份脱敏 CSV、最小 Extractor 与 4 个测试已完成；Lottery L2→L3 | 等待 ChatGPT 核对 claim 分类、升级关联边界与 CR Candidate；升级因果仍为 Estimate L3 | ChatGPT 返回 Accepted 或具体修改项；Review 前不新开 Capture、不改 Collector/CR | Task；Huuuge `bfed5f3`；飞书 `IK5adi...`；Workspace `828d3a7` | 2026-08-27 15:17 +08 |
| `TASK-0018-Cash-Frenzy-Android-Collector-Feasibility-Audit.md` | 支线 Candidate：多游戏扩展 | P1 Candidate | Cancelled | User/ChatGPT / none | Task ID 冲突已 fail-closed 止损；历史可行性审计内容仅保留为非执行 Candidate | 必须先让 TASK-0020 Accepted，再由 User 确认并以唯一 ID 重发；业务仓库未创建 | 不执行原文件；治理通过后按 Candidate → promotion 流程重新分配唯一编号 | Cancelled Task；`cd2fcb8`；`6610fef` 事件记录 | 2026-08-27 15:11 +08 |
| `TASK-0019-AI-Workspace-Overview-and-Separate-Progress-Documents.md` | 支线：项目可见性 | P1 | Review（分支；main Handoff 仍显示 Ready） | User/ChatGPT / Codex | 两份职责分离的 Git 源稿和两份唯一飞书文档已完成；正文、7/9 张表格及企业内编辑权限已回读 | 等待 ChatGPT Review；合并前 main Handoff 的 Ready 属正常分支差异；不自行合并 main | ChatGPT 核对文档边界、动态证据、飞书回读和权限，给出 Accepted/修订项 | TASK-0019；独立 branch/worktree；`main@0707449` Handoff；Document verify | 2026-08-27 15:22 +08 |
| `TASK-0020-Task-Allocation-and-Namespace-Governance.md` | 主线：任务治理 | P0 / governance | Ready | User/ChatGPT / Codex | 已建立紧急 fail-closed 分配规则与冲突事件记录；自动 Registry、allocator 和并发锁尚未实现 | 中央写入型治理任务，不与其他任务共享写工作区；Cash Frenzy 迁移不得先行 | 在独立 worktree 实现 canonical Registry、`scan/validate/next/candidate/promote`、并发锁、ADR-0006 与回归 | 完整 Task；`tasks/README.md`；`6610fef` | 2026-08-27 15:11 +08 |
| `TASK-0021-Workspace-Live-Context-Hub.md` | 主线：协作基础设施 | P0 / collaboration | Ready | User/ChatGPT / Codex | Feishu-first、Git canonical、authority map、Live Context Set 与多 Host 验收已定义；最新 Handoff 已指向执行，尚未实现 | 必须先审计 Wiki/Drive/事件真实能力；与 TASK-0016/0019/0020 独立工作区；需要外部资源时先获授权 | 独立 worktree 完成 Phase 0 Feasibility Audit，满足条件才采用 Wiki，否则用唯一 Drive Folder MVP | 完整 Task 与 ChatGPT Handoff；`main@0707449` | 2026-08-27 15:22 +08 |

## 3. 已完成里程碑

| Milestone | Confirmed Result | Evidence | Last Verified |
| --- | --- | --- | --- |
| Game Planner 领域与 Workspace Kernel | 领域边界、对象模型、AI Team、Task/Review/Handoff 真相源已合入 main | RFC-0001/ADR-0001 Accepted；`AI-Workspace@0707449` | 2026-08-27 15:22 +08 |
| Capability-first 架构 | Capability 与 Implementation Binding/Tool 分离，Global 和 Project 规则已采用 | ADR-0003 Accepted；`main@0707449` | 2026-08-27 15:22 +08 |
| Task 编号冲突紧急止损 | `TASK-0018` 冲突已确定 canonical Huuuge Task，Cash Frenzy 原 Task 已 Cancelled，分配规则改为 fail-closed | `tasks/README.md`；Cancelled Task；`6610fef` 事件记录 | 2026-08-27 15:11 +08 |
| Huuuge Collector 工程基线 | 被动 RPC 采集、84/84 proof、741/741 broad decode、manifest、markers、Finalize、inventory/catalog 链路存在 | `huuuge@bfed5f3`；CURRENT_STATUS/CHANGELOG | 2026-08-27 15:17 +08 |
| Huuuge 策划发布 1.0.1 | SVN-first Installer/Manual，白名单、hash 与空目录验证记录存在 | SVN r6429；source `b4b440f`；Huuuge CURRENT_STATUS | 2026-08-27 15:00 +08 |
| Huuuge Knowledge Index | 37 模块在 Slots/Systems/Events/Others 中导航，统一 L0–L4 证据词汇；Lottery 已提升至 L3 | Workspace Status；`huuuge@bfed5f3` | 2026-08-27 15:17 +08 |
| Huuuge Lottery 数值报告交付 | 中文 Git/飞书报告、6 份脱敏 CSV、最小 Extractor 与测试已完成；结论严格区分 Confirmed/Estimate | TASK-0018 Review；`huuuge@bfed5f3`；飞书 company-editable 回读 | 2026-08-27 15:17 +08 |
| AI Document Assistant Codex 基线 | 文档搜索、读写、目录、权限与 healthcheck 在当前 Host 可用 | `document-assistant@23197e2`；healthcheck 2026-08-27 | 2026-08-27 15:00 +08 |
| Codex Subagent Pilot | 默认 OFF、单写入者、受限 MANUAL 与 4 个只读角色通过 Review | TASK-0014 Accepted；ADR-0004；`8f50cb3` | 2026-08-27 15:00 +08 |
| Codex 代理/WebSocket 修复 | 完成根因排除、最小可回滚修复、3 次新任务与 HTTP 101 验证并合入 main | TASK-0017；`aa18233` | 2026-08-27 15:00 +08 |
| Huuuge First Run 指南 RC4 | 公共 AI-Workspace + 公司 SVN + 管理员预配 Document Assistant 的新人主线与飞书版已发布 | Huuuge Project Status；飞书 company-editable 回读 | 2026-08-27 15:00 +08 |

## 4. 未完成与阻塞项

| Item | Missing | Why Not Complete / Blocker | Unblock Condition | Exact Next Action | Mainline Impact |
| --- | --- | --- | --- | --- | --- |
| TASK-0016 Memory 安全收尾 | ASCII `-` 全入口回归；Secret/local-only hard deny | Review 2 发现 contract 与实现不一致，Registry 可误放宽全局安全 | 两漏洞修复，原 34 tests + 新回归通过，Context refresh 0 Secret issue，Review 3 Accepted | 继续同一 Task 小范围修复，保持 ASSISTED/Hook OFF | 影响跨对话 Memory 主线，不阻塞当前 Codex 文档交付 |
| TASK-0020 Task Allocation 治理 | canonical Registry、自动分配、全量校验、Candidate promotion、并发锁与 ADR-0006 | 紧急规则已止损，但纯 Markdown/人工检查仍可能再次分配冲突编号 | TASK-0020 实现与回归完成并经 Review Accepted | 独立 worktree 执行 TASK-0020；未通过前所有新编号 fail-closed | 直接影响所有后续 Task 分配与 Cash Frenzy Candidate 重发 |
| Huuuge Lottery 报告 Review | ChatGPT 对 claim 分类、升级关联、结构化表和 CR Candidate 的审阅结论 | 实施与发布已完成，但升级因果缺少直接 grant payload/UI artifact，只能保持 Estimate L3 | ChatGPT 返回 Accepted 或具体修改项 | Review Git 报告与飞书版；不把 +16 Bronze 写成单局随机掉落 | 当前 P0 业务分析主线的验收门 |
| TASK-0021 Live Context Hub | Feishu Wiki/Drive 选型、Context Capability、同步引擎、freshness、冲突与 Host adapters | 当前只有完整 Task；Wiki API/权限/事件和跨 Host 可达性尚未验证 | Phase 0 证据支持明确方案，外部资源若需要则 User 单独授权 | 先做 reuse-first Feasibility Audit；保持 Git canonical 和 `ON_DEMAND` 默认 | 影响后续多 Host 实时上下文，不改变当前 Git 真相源 |
| Huuuge 独立 First Run 盲测 | 未参与开发的策划、新机流程与真实耗时 | 尚未指定外部测试者 | 测试者只获得公共 Git + 飞书指南，不接受口头帮助，记录所有停顿 | User 指定一位策划并确认 SVN/飞书/预配 Provider 权限 | 影响策划大规模推广，不否定已验证工程链路 |
| Document Capability contract | ChatGPT 对 CAP-DOC/RFC-0002/Roadmap 的 Accepted/Needs changes | 当前 Provider 可用，但稳定 contract 标记 waiting review | Review 确认 operation、失败语义、默认权限和 provider 边界 | ChatGPT 审阅 CAP-DOC 与 RFC-0002，不修改外部实现 | 影响契约稳定性，当前 Codex Host 实现仍可用 |
| AI Report Engine | 稳定输入、模板、生成契约、证据对齐和回归 | 只是架构/Candidate，TASK-0019 明确禁止顺手实现 | 首个人工业务报告口径稳定，User 授权独立 Task | 从 Lottery 报告产物提炼最小 RFC，不直连 Raw | 不阻塞人工报告，阻塞报告自动化 |
| Workspace Sync | 通用 Git → Feishu/SVN 白名单、对账、冲突与审计 | 项目专属 Huuuge SVN 流和手动飞书流不等于通用能力 | RFC/ADR 通过，凭据和漂移失败处理可验收 | 先定义双向与单向真相源及幂等/部分成功语义 | 不阻塞手动发布，影响规模化维护 |
| ChatGPT 直接飞书 | 平台地区限制解除 | OpenAI Control Plane 拒绝 Secure MCP Tunnel 地区 | 官方平台/组织权限状态变化且通过安全复测 | 继续由 Codex 本地 Provider 代执行，不搭建未授权替代 tunnel | 不阻塞当前文档交付，影响 ChatGPT 直写体验 |

## 5. 当前可直接使用的入口

| 入口 | 用途 | 做什么 | 成功表现 | 失败怎么办 | Evidence |
| --- | --- | --- | --- | --- | --- |
| [AI-Workspace Git](https://github.com/840832144/AI-Workspace) | 治理、Task、Status、Review、Handoff | 打开项目并先读最新 Task/状态 | commit、Task 与 Handoff 可对齐 | 先 `fetch/pull --ff-only`；有未提交改动时用独立 worktree | `main@0707449` |
| [Huuuge 新人上手指南](https://gfok27asqq.feishu.cn/docx/Ffibd2Cx2oXFgfxdKnJcE6uUnZf) | 策划首次使用 | 按 12 步主线安装、启动、采集、停止和交付 | 文档可读且企业内可编辑 | 三分钟内在 SVN/Provider/环境预检 fail-fast，找管理员而不输入凭据 | Huuuge Project Status |
| [Huuuge 采集器部署手册](https://gfok27asqq.feishu.cn/docx/DSx8doLpIoI7SXxHCIoc4DQTnSb) | Installer/GUI 使用 | 通过公司 SVN 获取 1.0.1，运行 Bootstrap/Collector | 预检通过并显示 READY | 首次 SVN/游戏登录由 User 完成；Root/host 需显式授权 | SVN r6429；`huuuge@bfed5f3` |
| `HUUUGE_BOOTSTRAP.cmd` / `HUUUGE_COLLECTOR.cmd` | Huuuge 安装/日常采集 | 双击安装/更新或日常 GUI | `ready_for_gui_validation` / `READY，可以开始玩了` | 不直接杀进程；根据唯一 action item 处理 | Huuuge release 1.0.1 |
| Document Capability via Codex | 搜索、创建/更新、回读、授权飞书 | 先 healthcheck 与 search，再 create/replace，最后 get/permission verify | 原 document ID 稳定，正文/表格/权限回读一致 | 已创建但权限失败时保留文档，不重建；交管理员或 grant 重试 | healthcheck 2026-08-27；`document-assistant@23197e2` |
| Codex Network status / Repair / Restore | WebSocket/代理运行可靠性 | 运行 `bootstrap/codex/network/` 下状态、matrix、Repair 或 Restore | WebSocket HTTP 101，HTTPS 可达，配置可恢复 | 预检失败不写入；升级后重测，不叠加多个 workaround | TASK-0017 / `aa18233` |
| Memory status / Context refresh | 查看 ASSISTED 队列与生成 Project Source Pack | 使用 `tools/memory/` 入口查状态/刷新 | 输出 mode、Manifest、hash、replacement list 与扫描结果 | 在 Review 2 安全修复前保持 ASSISTED，不激活 Hook/AUTO | TASK-0016 / Review 2 |

## 6. 可额外开展的支线 Candidate

> 以下只是 Candidate，不代表已授权、已排期或已分配。

| Candidate | Expected Value | Prerequisite | Risk / Cost | Mainline Impact | Suggested Trigger | Recommended Priority |
| --- | --- | --- | --- | --- | --- | --- |
| AI Report Engine | Knowledge → Template → Markdown 报告可重现 | 至少一份已 Review 的人工业务报告和稳定 fact schema | 过早自动化会放大证据/口径错误 | 不阻塞当前 Lottery 人工报告 | Lottery 报告 Accepted 后 | P1 |
| Git → Feishu / SVN Workspace Sync | 降低手工发布漂移和重复文档 | RFC/ADR、白名单、冲突/部分成功语义、凭据边界 | 外部写入、错误覆盖、权限与运维成本 | 不影响手动流，可后置 | 当同类文档需要第三次手工对账时 | P2 |
| 飞书 Sheets / Bitable Provider | 适合矩阵、数值表和持续维护状态 | Document contract 稳定；数据模型和权限审评 | 新 provider/权限、双真相源与对账复杂度 | 不影响当前两篇 Docx 交付 | Docx 表格不足以支撑高频结构更新时 | P2 |
| Planner Toolkit | 把 Slot/Lottery/Economy/Task/Excel/SQL/Python 从分类变成可执行 Skill | 一个有证据、有回归、多次复用的成熟方法 | 容易把单项目 prompt 过度泛化 | 支持主线，不先于业务报告 | Lottery/Slot 方法经两次独立使用后 | P1 |
| 多实例独立数据库与脱敏聚合 | 验证账号分层、版本/活动差异和跨账号共性 | 单账号口径稳定；User 批准多实例/账号 | 隐私、数据混污、环境和维护成本 | 不阻塞单账号结论；只限制普遍化 | 单账号报告明确出现需要跨账号验证的 Hypothesis 时 | P1 |
| Huuuge Slots / Systems / Events / Others 续研 | 补齐当前 L1/L2 模块并构建 normalized extractor | 当前 P0 Lottery 报告完成；User 选定优先系统 | 采集时间、活动可访问性、样本不平衡 | 应继承 `Slots → Systems → Events → Others` | Lottery 报告 Review 后选择下一个最高价值缺口 | P1 |
| Lottery 分析后的 CR 迁移建议 | 将竞品证据转换为可执行参数实验 | Lottery 报告数据口径、限制和 Decision proposal 完整 | 跨项目上下文、推荐数字被误写成竞品事实 | 是 P0 报告价值延伸，但不修改 CR 仓库 | Lottery 报告关键证据达到声明等级后 | P1 |
| Cash Frenzy 新游戏 Collector 可行性/Adapter | 验证 Huuuge 通用层能否扩展到新游戏 | TASK-0020 Accepted；User 确认；唯一 Task ID；TASK-0015 关闭；独立实例与登录 | 原冲突 Task 已 Cancelled；APK/账号/动态环境成本；不能先复制 Collector | 属多游戏支线，不打断 P0 Huuuge | 治理通过后按 Candidate → promotion 重发，Collector idle 且 User 准备好独立实例时 | P1 Candidate |
| ChatGPT Project Source Pack 自动刷新/替换 | 降低新对话读到过期状态的风险 | 可批准、可验证的 Project Source 替换 API | 无稳定 API 时浏览器自动化脆弱且可覆盖错文件 | 不阻塞 Git 主线，但影响 recall | 官方安全 API 可用或 User 单独批准受控实验时 | P2 |
| 策划真实盲测与 UX 持续优化 | 验证一键体验、文档清晰度和真实耗时 | 未参与开发的策划、新机、管理员预配权限 | 人力、环境差异；不能由开发者代替 | 高度支撑规模化推广 | User 指定测试者后立即执行 | P0（对推广阶段） |

## 7. 风险、依赖与治理问题

| Risk / Dependency | Current Evidence | Impact | Control / Exact Next Action |
| --- | --- | --- | --- |
| Task 编号冲突 | 事件已止损：Huuuge 为 canonical TASK-0018，Cash Frenzy 原文件 Cancelled；自动 Registry/allocator/锁仍缺失 | 人工规则能阻断当前冲突，不能充分消除未来并发分配风险 | 按 `tasks/README.md` fail-closed；执行 TASK-0020 并通过 Review 前，不执行冲突文件、不猜下一个编号 |
| ChatGPT Project Source 快照滞后 | `02_CURRENT_STATE` 仍把已 Accepted TASK-0014 写为 Review，且未包含新 Task | 新对话可读到错误优先级 | 任务状态必须查 Git；TASK-0016 修复后 refresh 并人工替换 Sources |
| 飞书展示层与 Git 漂移 | 当前没有通用 Workspace Sync | 在线文档可过时或被手工修改 | 顶部固定 As of/commit/源稿；每次 search + replace + get + permission verify；不新建副本 |
| 私有业务仓库访问依赖 | Huuuge/Document Assistant 实现仓库对新人不应成为前置 | 无权限 Host 不能核验实现，但不应要求输入 Secret | 新人只使用公共 AI-Workspace + SVN + 预配 Provider；维护者引用 commit/release 证据 |
| ChatGPT 直接写飞书的地区限制 | Secure MCP Tunnel 由 OpenAI Control Plane 拒绝 | ChatGPT 不能独立完成在线交付 | ChatGPT 设计/审阅，Codex 通过当前批准 STDIO Provider 写入；不建第三方 tunnel |
| 能力文档与实现成熟度混淆 | Skill Tree/Roadmap/Schema 多于已实现能力 | 把 Planned 误写成 Available | 每个 Available/Completed 必须有 Accepted Review/main commit/release/test/healthcheck；没有就降级 |
| 多任务并发工作区冲突 | TASK-0016、两个 TASK-0018、TASK-0019、TASK-0020/0021 可并行；本轮 main 已两次前进 | 覆盖、误提交、错误 rebase 或发布瞬间过时 | 每 Task 独立 branch/worktree；主 Agent 唯一写入；提交前 fetch/rebase；不 stash/reset/提交他人改动 |
| Huuuge Raw 与多账号隔离 | Raw 可含账号/Session/逐笔余额；当前只有策略，无通用聚合实现 | 隐私泄露、样本混污和假规律 | 每实例/账号独立库；先单账号，后脱敏聚合；Raw 不进入 Git/飞书/聊天 |
| AI-Workspace Status 与业务仓库漂移 | 本轮已对齐 Workspace `0707449` 与 Huuuge `bfed5f3`，但两仓可由并行任务继续前进 | 不做提交前 fetch 会立刻产生过时进度 | 业务仓库先提交/审阅，Workspace 用 commit-pinned 事实刷新；每次发布前再次 fetch，未提交内容不升格 |

## 8. 更新规则

本节是本文的维护手册，不创建第三份用户文档。

### 什么时候更新

发生以下任一事件后更新本文：Task 状态变化；ChatGPT Review；权威分支合入；release/SVN 修订版发布；能力 healthcheck 变化；阻塞解除/新增；主线或 Candidate 获得 User 授权。

### 标准更新流程

1. **先更新真相源**：业务实现先进业务仓库；Task/Review/Capability/Handoff 先进 AI-Workspace；release 先进批准分发系统。不先在飞书宣布完成。
2. **同步并读最新状态**：安全更新 AI-Workspace `main`，读全量 Task header、项目 Status、最新 Review 和 Handoff；业务仓库有未提交改动时只读/fetch，不覆盖。
3. **核验证据**：对每个 `Available / Completed` 至少记录一个 Accepted Review、main commit、release、test、runtime evidence 或 healthcheck。目录、Schema、Roadmap、聊天或未合入 branch 不足以升格。
4. **更新 Git 源稿**：修改本文的 `As of`、commit/发布基线、状态数量、矩阵、任务、阻塞、下一步和核验时间。不把动态清单复制到项目全景说明。
5. **搜索飞书原文档**：先运行 `feishu_healthcheck`，再用 `search_documents` 按精确标题和项目搜索。命中唯一文档后使用原 `document_id`；命中多个时停止并核对，不猜。
6. **使用 `replace_document` 更新**：整篇替换原文档，不用 `create_document` 生成日期副本；只在搜索确认不存在时创建。
7. **回读验收**：用 `get_document` 回读标题、`As of`、main commit、状态摘要、至少一张核心表格、阻塞与更新规则；再回读 `tenant_editable` 权限。
8. **判定成功**：Git 与飞书的 `As of`、基线 commit、状态数量和关键表格一致；原 document ID 未变；企业内获得链接的人可编辑。
9. **失败处理**：healthcheck 失败则停止写入；replace 回滚失败则保留 document ID 和准确错误；权限被管理策略拒绝时保留文档并交管理员，不重复创建。
10. **防止漂移**：飞书顶部始终保留 Git 源稿路径、基线 commit、更新时间与维护规则；后续状态只更新同一篇进度文档。

## 证据索引

- [AI-Workspace `main@0707449`](https://github.com/840832144/AI-Workspace/tree/070744944d02b8d493c737db74bdc3d404963158)
- [TASK-0016 Review Round 2](https://github.com/840832144/AI-Workspace/blob/070744944d02b8d493c737db74bdc3d404963158/reviews/TASK-0016-CHATGPT-REVIEW-2.md)
- [Huuuge Project Status](https://github.com/840832144/AI-Workspace/blob/070744944d02b8d493c737db74bdc3d404963158/projects/huuuge-android-research/STATUS.md)
- [Huuuge external `main@bfed5f3`](https://github.com/840832144/huuuge-android-research/tree/bfed5f30e098522ffb98ef5eb7d63e824d68b1c4)
- [Capability Catalog](https://github.com/840832144/AI-Workspace/blob/070744944d02b8d493c737db74bdc3d404963158/capabilities/README.md)
- [Document Capability](https://github.com/840832144/AI-Workspace/blob/070744944d02b8d493c737db74bdc3d404963158/capabilities/document/README.md)
- [Memory Capability](https://github.com/840832144/AI-Workspace/blob/070744944d02b8d493c737db74bdc3d404963158/capabilities/memory/README.md)
