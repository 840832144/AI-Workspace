# 00 — Core Rules

## 项目定位

Game Planner AI Workspace 是面向游戏策划研究、游戏客户端研究、数值拆解、工具建设和文档协作的长期工作空间。当前重点是 Huuuge 研究、采集器、知识体系和文档基础设施。

默认领域是游戏策划，不主动把其他领域带入核心架构。

## 研究优先级

Huuuge 研究固定优先级：

```text
Slots → Systems → Events → Others
```

- Slots：机台玩法、中奖率、倍数分布、Feature、潜在调控等。
- Systems：经济、任务、Battle Pass、Lottery、成长及长期系统。
- Events：通过 Slots 消耗和目标进度驱动的运营活动。
- Others：礼包、小玩法及其他补充内容。

具体任务可因限时活动临时提高优先级，但必须明确说明原因。

## 角色与决策

- User：决定产品目标、优先级、付费和资源消耗、外部权限、风险偏好与最终验收。
- ChatGPT：负责产品与架构设计、RFC、Task、Workflow、Skill、评审和优化建议。
- Codex：负责实现、自动化、测试、Git、部署、运行验证和实现 Handoff。
- 其他 AI：可参与执行，但必须遵守相同 Capability、证据、安全和交接规则。

未经 User 授权，AI 不得替代 User 做付费购买、充值、不可逆操作、外部发布或权限扩大。

## Capability-first / Reuse-first / Build-last

收到需求后依次执行：

1. 明确 User 需要的结果、对象、操作等级和成功证据。
2. 匹配已有 Capability、Workflow、Skill 和项目规则。
3. 检查当前项目已有代码、脚本、依赖和配置。
4. 检查本机工具、MCP、CLI 和团队内部服务。
5. 检查团队仓库、公司 SVN 正式包和共享基础设施。
6. 检查官方文档、官方 SDK 和官方示例。
7. 检查许可证清晰、维护活跃、可验证的成熟开源方案。
8. 比较 Adopt / Wrap / Fork / Build 的成本、风险、兼容性和退出成本。
9. 只有现有方案不适配时才自行开发。

“发现候选方案”不等于“自动安装或采用”。新增依赖、外部服务、系统配置和权限变更仍需遵守安全与授权规则。

## 文档与交互标准

所有 AI 在生成面向 User 或策划的内容前读取 `standards/PLANNER_WRITING_STYLE.md`。默认使用完整中文段落，普通回答采用“结论 → 当前依据 → 下一步”，不把一句话拆成大量孤立短行。

面向策划的说明文档：

- 默认中文；不要求读者理解代码。
- 采用短步骤，写清“做什么 → 成功表现 → 失败怎么办”。
- 优先给按钮名、路径、截图位置和可复制话术。
- 不把架构、MCP、ADB、Proto、环境变量等底层知识作为主流程前置。
- 优先一键安装、一键启动、一键停止、一键检查和自动修复。
- 前几分钟完成权限、设备、环境和服务预检，避免流程末端才失败。

与 User 讨论复杂方案、架构和评审时，可以展示必要的逻辑、代码和技术细节。

### 技术术语与风险表述

所有 AI 使用 `standards/PLANNER_WRITING_STYLE.md` 作为唯一术语规范。面向策划默认使用准确、克制、可理解的研究表达；涉及复现、技术附录、代码、日志、工程判断、授权、合规或风险时，必须保留 Root、Frida、Hook、逆向分析、协议解密、签名校验绕过、完整性校验修改、exploit 等真实术语。

规则不允许通过改名或模糊化规避平台安全策略、权限检查、User 授权或 Review，也不允许弱化真实风险或把被动研究夸大为攻击。策划主流程可先给易懂结论，必要的精确机制放在括号、维护者说明或技术附录中。

## Documentation Governance

- 所有正式飞书文档必须登记到唯一的《AI Workspace｜文档导航中心》。Git 继续作为规则、Task、ADR、状态和实现的真相源；文档导航中心只是飞书导航入口，不是真相源。
- 导航中心使用固定分类和统一元数据，由 Document Assistant 自动生成，不允许人工维护目录，也不允许创建第二个同名入口。
- 正式文档创建流程固定为 `create_document → 文档回读 → register_document → 文档导航中心回读 → Success`。
- 导航中心更新或回读失败即流程失败：不删除已创建文档、不重复创建，返回失败并等待修复。不允许出现“正式文档已创建，但导航中心没有登记”的完成状态。
- 正式文档默认企业内可编辑，除非 User 明确要求私有、只读或不授予编辑权限。导航中心不展示 token、独立 document ID、私有 Registry 或其他敏感信息。

## Task 协作协议

```text
User 目标
→ ChatGPT 写完整 Task 到 AI-Workspace
→ User 只转发简短执行话术
→ Codex 同步 Git、读取 Task 后实施
→ Codex 提交、验证并更新 Handoff
→ ChatGPT Review：Accepted / Needs changes
→ 新发现的优化项作为下个 Task 候选，由 User 决定是否进入主线
```

不得只在聊天中口头创造一个并不存在的 Task 文件。涉及当前任务时必须读取 Git 中的真实 Task。

### Task 创建与编号分配规则

创建、重编号、晋升或引用新 Task 前，必须从 Git 最新 `main` 读取完整 `tasks/` 清单和当前 Handoff，并运行 Task Registry validator；不得依据聊天、记忆、最大编号或本地过期目录分配编号。

Task identity 采用：

```text
canonical ID = 全局唯一 TASK-XXXX
project_key  = 必填项目命名空间元数据
human_alias  = 可选阅读别名
```

`project_key` / alias 不替代 canonical ID。Task Markdown 是真相源，Registry 只能重建，不能手工维护为第二真相源。

强制顺序：

1. 枚举所有根目录 canonical Task 文件，确认已占用 ID、状态和完整文件名；
2. 检查是否已有相同目标或重叠范围的 `Draft / Ready / In Progress / Review / Changes Requested` Task；
3. 区分 canonical Task 与附件、授权书、Review、Candidate；root Task 默认严格按 canonical 解析，只有显式 `Kind: companion` 且引用存在、同 ID canonical 的文件才能成为 companion；
4. 决定继续已有 Task、创建子任务、保留 Candidate，或通过 remote Git reservation CAS 保留一个经 Git 验证未占用的新 ID；
5. 创建后重建 Registry 并再次 validate，验证 ID 唯一、文件名与标题一致、Task 可被其他会话发现。

禁止：

- 猜“下一个编号”；
- 在未检查完整 `tasks/` 目录时创建 `TASK-XXXX`；
- 让两个不同 canonical Task 共用同一 ID；
- 因编号冲突覆盖、删除或改写先存在 Task 的历史；
- User 尚未确认范围时直接把讨论项升级为 `Ready` Task。
- 手工编辑 `TASK_REGISTRY.yaml` 消除漂移，或在 canonical 进入 main 前释放 reservation。

所有 allocation 写操作要求包含最新 `origin/main` 的 non-main independent linked worktree。remote `task-reservations/TASK-XXXX` ref 使用 first-writer CAS 覆盖不同 clone / Host；创建或晋升 Task 后保持到 canonical 进入 main，再用 token `finalize`，只有未创建 Task 的放弃场景才 `release`。新 canonical 必须显式写合法 `project_key`，仅审计 grandfather 集合可缺省。

发生 duplicate、解析失败、Registry 漂移、非最新 main、active scope ambiguity 或 lock/reservation 冲突时必须 fail closed：停止执行冲突 Task，保留先存在 Task 为 canonical，明确标记误建 Task 为 `Cancelled` companion 或迁入 Candidate。

新增游戏研究默认先经过 `Feasibility Audit → ChatGPT Review → User 决定 → Collector Adapter / Productization`，不得从聊天直接跳到完整 Collector 开发。

## Idea Governance

任何值得长期保留的产品想法，不允许只停留在聊天。新的产品能力、长期优化、Workflow、Capability、Collector 思路和 UX 改进必须经过防重，并进入唯一 Product Roadmap 的四个固定分区之一：

```text
🔥 Current
📋 Backlog
💡 Ideas
✅ Done
```

- `Current` 只允许当前正在开发或已经批准即将开发的方向。
- `Backlog` 保存大概率会做、但尚未批准进入当前开发的方向。
- `Ideas` 保存长期设想、待验证方向和探索性建议。
- `Done` 只保存已经实现、验证并完成正式 Review 的能力。

ChatGPT 在任何项目聊天中主动提出值得长期保留的新方向时，必须在对应 Task 收尾时生成 Idea Handoff，主动通知 Codex 更新 Product Roadmap，不再依赖 User 手工提醒。Codex 必须读取最新 Git、防重并更新 canonical 源稿；Roadmap 更新不等于执行授权，也不会自动创建 Task。需要执行时仍由 User 决定并通过 Candidate 与正式 allocator。

Product Roadmap 是长期产品规划唯一入口，不与 Task、Documentation Hub、Knowledge、Memory 或项目 Status 混合。详细规则见 `standards/IDEA_GOVERNANCE.md`。

## 证据与安全

- Confirmed、Estimate、Hypothesis、Decision proposal 必须明确区分。
- Huuuge 使用统一 Evidence Standard；不得把 Schema 推断写成 Live-confirmed。
- Raw capture、完整响应、账号信息、逐笔余额、截图原件和私有 Registry 保持在受控本机环境。
- Git、飞书、聊天和项目来源只保存脱敏、聚合、必要且可复查的信息。
- Secret、token、私钥、凭据和 Authorization Header 永不进入 Git、文档、Task 或聊天。

## 真相源

- AI-Workspace：治理、Capability、规则、Task、项目控制面和 Handoff。
- `huuuge-android-research`：Huuuge Collector、业务实现、研究证据和发布状态。
- `document-assistant`：AI Document Assistant 实现与测试。
- 飞书：面向人的正式报告和团队知识成果。
- 公司 SVN：策划可用的正式发布包和公司资源分发。

项目来源和 Project Memory 只是便于新对话读取的上下文快照，不替代上述真相源。

## Workspace Live Context

- Task、Review、状态查询和 Handoff 前运行 `ON_DEMAND` Workspace Sync。
- Git-authoritative 内容只向协作层发布；飞书协作草稿进入 Candidate/Review，不直接覆盖 Git。
- 冲突时双方内容都保留，必须有 User/Review decision；provider unavailable 时使用最近验证的 local pack 并标记 stale。
- 未经 User 明确批准，不启用生产 WATCH、外部 webhook、长期 watcher、新权限或新知识空间。

## Automatic Memory

- 重要内容在产生时先转成结构化 Candidate，不依赖事后遍历全部聊天。
- Candidate 只保留摘要、来源、evidence、scope 和 sensitivity，不保存完整 transcript。
- Public / Project Private / Cross-project Private / Local-only 分流；不明确时禁止写公共 Git。
- Project Memory 与 Host local memory 是 recall layer，Git 和业务仓库仍是 canonical source。
- `memory/context/WORKSPACE.md` 是跨 ChatGPT、Codex 与 Generic Agent 会话的唯一 public-safe 长期记忆读入口。新会话必须 Git-live-first 读取最新 `main` 中的该文件，再核对相关 Task、Review、Handoff 与业务证据。
- 只有通过现有 `Memory Event → Candidate → Validator → Curator`、高置信、证据充分、public-safe、无冲突且经 ASSISTED 显式批准的记录才能进入该读视图；冲突或未 Accepted 结论不得写入。
- Project Source Pack / Project Sources 只是离线快照。Git 可用时禁止用旧快照覆盖 Workspace Memory；Git 不可用时必须标记快照可能过期。
- OFF / ASSISTED / AUTO 是独立 kill switch；生产默认 ASSISTED，AUTO 不能绕过高影响 Review gate。
