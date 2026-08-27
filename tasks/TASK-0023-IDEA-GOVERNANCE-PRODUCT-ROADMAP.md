# TASK-0023 — Idea Governance & Product Roadmap

- Status: Accepted
- Project key: WORKSPACE
- Human alias: 
- Owner: User / ChatGPT
- Executor: Codex
- Priority: P1 governance
- Date: 2026-08-27
- Updated: 2026-08-27
- Candidate provenance: `tasks/candidates/CANDIDATE-20260827-WORKSPACE-IDEA-GOVERNANCE-PRODUCT-ROADMAP.md`
- Allocation relationship: new
- Related tasks: TASK-0021, TASK-0022

## Goal

建立唯一 Product Roadmap 与 Idea Governance，使长期产品想法进入 Current、Backlog、Ideas、Done 之一，并通过正式飞书入口可发现。

## Scope

1. 建立唯一 Git 源稿 `docs/roadmaps/PRODUCT_ROADMAP.md`，并发布唯一正式飞书文档《AI Workspace｜产品路线图（Product Roadmap）》。
2. Product Roadmap 只维护长期产品方向，固定包含 `🔥 Current`、`📋 Backlog`、`💡 Ideas`、`✅ Done` 四个分区；不替代 Task、Documentation Hub、Knowledge、项目 Status 或根目录阶段路线图。
3. 建立 `standards/IDEA_GOVERNANCE.md` 与 `workflows/idea-governance/README.md`，定义 ChatGPT 在任何项目聊天中主动提出长期产品能力、Workflow、Capability、Collector 或 UX 改进时的自动分类和收尾交接规则。
4. 更新 `00_CORE_RULES.md`、`PROJECT_INSTRUCTIONS.md`、Repository/Bootstrap/Global AGENTS 与 ChatGPT/Codex Handoff，使值得长期保留的产品想法不能只停留在聊天。
5. 通过 Document Capability 搜索防重、创建或更新 Roadmap、正文回读、默认企业内可编辑、自动登记、导航中心回读。
6. 原位更新《Game Planner AI Workspace｜项目全景说明》，增加 Product Roadmap 可点击入口；不得创建第二份项目全景说明。
7. 使用一个可识别的临时测试 Idea 验证进入 `💡 Ideas`，回读成功后删除测试项并恢复正式 Roadmap。

## Classification Contract

- `🔥 Current`：仅允许当前正在开发，或已经批准且即将开发的方向。
- `📋 Backlog`：大概率会做，但尚未获得进入 Current 的执行批准。
- `💡 Ideas`：长期设想、待验证方向和讨论中产生的新能力。
- `✅ Done`：已经实现、验证并完成正式 Review 的能力。

ChatGPT 不直接把聊天建议变成 canonical Task。它应在相关 Task 收尾时向 Codex 交付最小 Idea Handoff，由 Codex 在最新 Git 上完成防重、分类和 Product Roadmap 更新。进入 `Current` 仍需 User 批准或已存在的 active canonical Task；进入 `Done` 需要可复查的完成证据。

## Initial Roadmap

- Current：Cash Frenzy；Top Tycoon（只记录已确定的后续顺序，Cash Frenzy Review 前不执行、不建业务环境）。
- Backlog：Documentation Portal、Recent Updates、Experience Timeline。
- Ideas：One Research Environment → Multiple Games → Independent Evidence。
- Done：Documentation Hub、Workspace Sync、Task Governance。

## Non-goals

- 不修改 TASK-0022、Cash Frenzy、Huuuge 或任何业务仓库。
- 不修改 Document Assistant 实现、配置、凭据或工具清单，只消费已批准的 Document Capability。
- 不启用 Workspace Sync `WATCH`，不新增 watcher、webhook、计划任务或后台服务。
- 不把聊天全文、每个临时念头、Task 状态、研究 Knowledge 或文档目录复制到 Product Roadmap。
- 不因 Roadmap 条目自动创建 Future Task；Task 仍须经过 User 决定与正式 allocator。

## Deliverables

- `docs/roadmaps/PRODUCT_ROADMAP.md`
- `standards/IDEA_GOVERNANCE.md`
- `workflows/idea-governance/README.md`
- 更新 Core Rules、Project Instructions、AGENTS、ChatGPT Bootstrap、两份 Handoff、项目全景说明、Roadmap 索引、CHANGELOG。
- 唯一正式飞书 Product Roadmap，以及导航中心和项目全景说明中的可点击入口。

## Safety

- Git 不保存飞书租户 URL、document ID、token、私有 Registry 或凭据；正式链接只在本次安全交付中返回。
- 云文档创建失败不得重复创建；导航中心登记失败时保留已创建文档并等待修复。
- 并行工作使用独立 linked worktree；TASK-0022 保持原文件、分支、reservation、状态与执行环境不变。
- `Subagents: none`；当前宽松权限会话不得启用 MANUAL。

## Validation

1. Registry validate：canonical 唯一、0 collision，且 `TASK_REGISTRY.yaml` 只由 CLI 重建。
2. Product Roadmap 标题唯一，固定四分区各出现一次。
3. Documentation Hub 可以进入 Roadmap；Roadmap 自动登记且 Hub 无重复链接。
4. 项目全景说明可以进入 Roadmap，链接目标一致。
5. 临时测试 Idea 写入 `Ideas` 后回读成功，再删除并确认正式正文恢复。
6. Roadmap 与项目全景说明均完成正文、权限和导航中心回读。
7. Task、Context、Memory、Doctor 回归通过；Workspace Sync 保持 `ON_DEMAND`。

## Handoff

更新 Task、CHANGELOG、`handoff/CHATGPT.md` 与 `handoff/CODEX.md`；提交并 push 独立分支，返回 Roadmap 安全链接并等待 ChatGPT Review。未经 Review 不合并 main，canonical 合入 main 后再 finalize allocator reservation。

## Execution Result — 2026-08-27

- Candidate 由 `task_cli.py candidate` 创建，首次因 User decision 非规范枚举被 `promote` 阻断且未占号；修正为 `Approved` 后由 allocator 分配唯一 `TASK-0023`，reservation 为 `pending-main`。
- Git Product Roadmap、Idea Governance standard/workflow 和所有指定规则入口已完成。
- 唯一正式飞书 Product Roadmap 已创建并自动登记；文档导航中心与项目全景说明均可进入 Roadmap。
- 临时测试 Idea 已真实进入 `Ideas` 并回读，随后删除；正式正文恢复，四个固定分区各出现一次。
- Roadmap 与项目全景说明企业内可编辑；项目全景原生工作流图保持存在；Hub 当前 15 条正式文档、链接唯一。
- Product Roadmap 最终只保留四个固定二级分区；治理说明统一放在 Idea Governance standard/workflow，不在 Roadmap 增加第五分区。
- 当前桌面会话挂载的旧 MCP 进程缺少 `register_document`，一次 `get_document` 回读按旧 schema 写回后使项目全景治理 metadata 暂时丢失；未创建副本，已使用 Document Assistant 当前 `main` 新进程重新登记并恢复 Hub 15 条、链接唯一。该问题属于会话进程陈旧，不修改 Document Assistant 仓库。
- 没有修改 TASK-0022、Cash Frenzy、Huuuge、Document Assistant 仓库或 Workspace Sync 模式。
- deterministic regression：Registry 10 canonical / 0 collision；Task 23/23、Context 13/13、Memory 35/35、两个 PowerShell 入口和 Workspace Doctor 通过；Context refresh 62 sources、0 broken link、0 secret issue。
- 当前状态为 Review；commit 在提交后写入最终交付消息，不在 Task 内制造自引用 commit。

## Review Round 1 Required Fix — 2026-08-27

- 正式 Review：`reviews/TASK-0023-CHATGPT-REVIEW-1.md`；主体 Product Roadmap 与 Idea Governance 已通过，唯一 Required Fix 为准确、克制、面向受众的技术术语规则。
- `standards/PLANNER_WRITING_STYLE.md` 作为唯一 canonical 规则源：默认使用策划可理解的研究表达；复现、工程判断、授权、合规、安全或风险依赖真实机制时保留精确技术术语。
- 规则明确禁止通过改名或模糊化规避平台安全策略、权限检查、User 授权或 Review，也不得弱化真实风险或把被动研究夸大为攻击。
- 同一规则已传播到 Core Rules、根与 Global AGENTS、Project Instructions、ChatGPT Bootstrap、Generic Agent 稳定入口和 Context Hub；其他入口只引用或摘要 canonical 规则，不建立第二套术语表。
- Context refresh 生成器已把 canonical 规范正文纳入 ChatGPT 单文件 Source Pack 和 6 个拆分来源替换清单，并用 Memory 回归测试锁定。
- 本轮不修改 Product Roadmap、Idea Governance 主体、TASK-0022、Cash Frenzy、Huuuge、Document Assistant 或 Workspace Sync 模式；`Subagents: none`。
- Context / Source Pack 已刷新为 62 sources、0 broken link、0 secret issue；Task 23/23、Context 13/13、Memory 35/35、两个 PowerShell 入口和 Doctor 全部通过，Registry 为 10 canonical / 0 collision。
- Workspace Sync 保持 `ON_DEMAND`、0 conflict；provider 不可用导致 6 个发布项 stale。Round 1 阶段保持 Review，并在 push 独立分支后等待 ChatGPT Review Round 2。

## Acceptance — 2026-08-27

- ChatGPT Review Round 2：Accepted；正式记录为 `reviews/TASK-0023-CHATGPT-REVIEW-2.md`，reviewed commit 为 `bc0d3ad1e519fb908dce53a78a35f9c3687a5b51`。
- Product Roadmap、Idea Governance 与准确、克制、面向受众的技术术语规则正式生效。
- 收口顺序固定为：更新 Registry / Context → deterministic regression → 合并并 push main → 原 allocator worktree finalize reservation → 0 collision 复验 → 清理任务 branch/worktree。
- 收口前回归：Context / Source Pack 62 sources、0 broken link、0 secret issue；Task 23/23、Context 13/13、Memory 35/35、两个 PowerShell 入口、Registry 10 canonical / 0 collision 与 Doctor 全部通过。
- 本次 Acceptance 不扩大范围，不修改 TASK-0022、Cash Frenzy、Huuuge、Document Assistant 或 Workspace Sync 模式；`Subagents: none`。
