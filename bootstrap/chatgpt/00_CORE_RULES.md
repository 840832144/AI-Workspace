# 00 — Core Rules

## 项目定位

Game Planner AI Workspace 是面向游戏策划研究、逆向分析、数值拆解、工具建设和文档协作的长期工作空间。当前重点是 Huuuge 研究、采集器、知识体系和文档基础设施。

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

面向策划的说明文档：

- 默认中文；不要求读者理解代码。
- 采用短步骤，写清“做什么 → 成功表现 → 失败怎么办”。
- 优先给按钮名、路径、截图位置和可复制话术。
- 不把架构、MCP、ADB、Proto、环境变量等底层知识作为主流程前置。
- 优先一键安装、一键启动、一键停止、一键检查和自动修复。
- 前几分钟完成权限、设备、环境和服务预检，避免流程末端才失败。

与 User 讨论复杂方案、架构和评审时，可以展示必要的逻辑、代码和技术细节。

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
3. 区分 canonical Task 与附件、授权书、Review、Candidate；附件不得伪装成第二个 canonical Task；
4. 决定继续已有 Task、创建子任务、保留 Candidate，或通过 allocator 保留一个经 Git 验证未占用的新 ID；
5. 创建后重建 Registry 并再次 validate，验证 ID 唯一、文件名与标题一致、Task 可被其他会话发现。

禁止：

- 猜“下一个编号”；
- 在未检查完整 `tasks/` 目录时创建 `TASK-XXXX`；
- 让两个不同 canonical Task 共用同一 ID；
- 因编号冲突覆盖、删除或改写先存在 Task 的历史；
- User 尚未确认范围时直接把讨论项升级为 `Ready` Task。
- 手工编辑 `TASK_REGISTRY.yaml` 消除漂移，或把本地 reservation 冒充跨 Host 中心锁。

发生 duplicate、解析失败、Registry 漂移、非最新 main、active scope ambiguity 或 lock/reservation 冲突时必须 fail closed：停止执行冲突 Task，保留先存在 Task 为 canonical，明确标记误建 Task 为 `Cancelled` companion 或迁入 Candidate。不同 clone/Host 在 push、Review 和 merge 前必须针对最新 main 复验。

新增游戏研究默认先经过 `Feasibility Audit → ChatGPT Review → User 决定 → Collector Adapter / Productization`，不得从聊天直接跳到完整 Collector 开发。

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

## Automatic Memory

- 重要内容在产生时先转成结构化 Candidate，不依赖事后遍历全部聊天。
- Candidate 只保留摘要、来源、evidence、scope 和 sensitivity，不保存完整 transcript。
- Public / Project Private / Cross-project Private / Local-only 分流；不明确时禁止写公共 Git。
- Project Memory 与 Host local memory 是 recall layer，Git 和业务仓库仍是 canonical source。
- OFF / ASSISTED / AUTO 是独立 kill switch；生产默认 ASSISTED，AUTO 不能绕过高影响 Review gate。
