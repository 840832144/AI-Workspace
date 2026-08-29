# 02 — Current State

_Last reviewed: 2026-08-29_

本文件是便于 ChatGPT Project 新对话快速进入状态的动态摘要。执行任务前仍需读取 Git 中的最新 Task、Status、Handoff 和业务仓库。

> TASK-0021 起，本文件降级为稳定 Bootstrap / 离线回退。动态 Task、Status、Handoff 和 freshness 由 `Workspace Sync` 从最新 Git 与 `LIVE_CONTEXT_MANIFEST.json` 生成；不能访问时必须显示 `Context unavailable / stale`，不得凭本文件猜测。

## 已完成的重要里程碑

- AI-Workspace 已建立 Game Planner 领域边界、Workspace Kernel、Capability Model、Skill Tree、Project Template、Evidence Standard、Task 与 Handoff 机制。
- Huuuge Collector 已形成 SVN-first 策划发布流程，并具备环境检查、READY、广泛 RPC 捕获、protobuf decode、Session manifest、自动 lifecycle markers 和 Clean Finalize。
- Huuuge Knowledge Index 已按 Slots、Systems、Events、Others 整理研究模块，并采用统一 L0–L4 Evidence Standard。
- AI Document Assistant 已接入 Codex，可读写飞书云文档并自动设置企业内可编辑权限。
- Codex 跨项目 Global AGENTS 已采用 Capability-first / Reuse-first 规则。
- Codex 1+4 Subagent Pilot 已通过 Review；默认 `OFF`，可在受限权限和适合的复杂任务中手动启用。
- Git-backed Automatic Memory 已通过 TASK-0016 Review Round 3 并 `Accepted`；production 默认 `ASSISTED`，Global hook 与 production AUTO 未激活。
- Task Registry / allocator、Workspace Sync contract、文档导航中心、Idea Governance 与 Product Roadmap 已分别通过 TASK-0020、TASK-0021、TASK-0023 Review。
- Collector 1.0 已通过 TASK-0026 Review Round 3 并 `Accepted`；实现位于 `CF_collect/main@4df10ec20e79bb737912c8d1b847fae3659031ae`，范围继续固定为已审阅 contract 与六字段。
- 当前 Windows 工作站的 Workspace 与 Document Assistant 接入已完成现场验收，可标记为 `Ready`；这只证明本机治理与文档能力可用，不等于 Huuuge First Run 已通过。
- Huuuge First Run 状态为 `Blocked`：正式 RC4 记录仍为 `Pending`；User 提供的实跑反馈已脱敏记为 `Failed/Invalid`，流程曾到达 `READY`，但没有形成独立测试者、完整计时和逐项成功证据。`READY` 只表示采集前置条件满足；其后的游戏操作与执行授权仍由 User 控制，该反馈不改写正式 RC4 记录。没有直接 Bet 分层运行证据或稳定 RTP/EV 统计证据，不得从字段、单次样本或描述性比率推导 Bet 与 RTP 关系。

## 当前执行入口

当前 User 已授权：

```text
AI-Workspace/tasks/TASK-0019-AI-Workspace-Overview-and-Separate-Progress-Documents.md
```

状态：`Review`；ChatGPT Review Round 1 为 `Needs changes`，指定的文档事实与验收缺口已修订，等待 Round 2。独立分支从 `main@c74c85a9524d1524ea3696835509de2a55e9f524` 建立。执行前仍需从最新 `main` 和 Handoff 确认边界，不得依据本离线摘要直接启动业务任务。

背景：TASK-0026 已 Accepted 并合入 `CF_collect/main@4df10ec20e79bb737912c8d1b847fae3659031ae`；当前任务只维护 Workspace 项目说明与状态入口，不启动模拟器、Root、Frida、Collector 或 Spin。

TASK-0020 已确认结果：

- 已建立可重建 Registry 和 canonical / companion / candidate / review 分类；
- 已实现 `scan / validate / next / release / candidate / promote`；
- duplicate、格式/Registry 漂移、并发分配、lock 和非最新 Git fail closed；
- ADR-0006 提议采用全局 `TASK-XXXX` + `project_key` + 可选 alias；
- Task 23/23 与 PowerShell 5.1 回归通过；真实仓库当前 13 canonical、0 collision；
- TASK-0021 已 Accepted，文档导航中心与 Workspace Sync 规则进入最终状态；
- TASK-0023 已完成 ChatGPT Review Round 2 并 Accepted；唯一 Product Roadmap、Idea Governance 与 Planner Writing Style 正式生效；
- 本轮不修改 Cash Frenzy、Huuuge 或 Document Assistant 业务实现仓库。

## 当前 Huuuge 任务

当前相关文件包括：

```text
AI-Workspace/tasks/TASK-0015-Huuuge-Lottery-Live-Numerical-Breakdown.md
AI-Workspace/tasks/TASK-0018-Huuuge-Lottery-Numerical-Breakdown-Report.md
```

实际状态和执行顺序必须读取文件、最新 Handoff 和 `huuuge-android-research`。TASK-0020 不得修改 Collector、Raw Capture 或 Lottery 业务分析范围。

## 当前并行 Workspace 任务

- `TASK-0019-AI-Workspace-Overview-and-Separate-Progress-Documents.md`：`Review`，当前唯一执行入口。
- `TASK-0021-Workspace-Live-Context-Hub.md`：`Accepted`；Live Context、Workspace Sync 和文档导航治理已完成。
- `TASK-0023-IDEA-GOVERNANCE-PRODUCT-ROADMAP.md`：`Accepted`；唯一 Product Roadmap、Idea Governance、技术术语规则与两个正式文档入口已完成并正式生效。
- `TASK-0025-TOP-TYCOON-ANDROID-F4-COLLECTION-FEASIBILITY-AUDIT.md`：`Ready`，等待 User 明确切回，不与当前任务并行执行。
- `TASK-0026-COLLECTOR-1-0-ENGINEERING.md`：`Accepted`，不在当前任务内扩大字段、模块或动态运行范围。

并行任务必须使用独立 branch / linked worktree。当前 TASK-0019 不合并旧 `task-0019-overview-progress`，只选择性复用其文档内容并以最新真相源重写。

## 当前重要决策

### Task Allocation

- 新 Task 创建前必须从 Git 最新 `main` 运行 Task Registry validator，不能依赖聊天、Project Source 快照、局部搜索或“最大编号 + 1”。
- canonical ID 使用全局唯一 `TASK-XXXX`；`project_key` 是项目元数据，可选 alias 只用于阅读。
- Markdown 是真相源，Registry 只能由完整 scan 重建；companion、authorization、review 和 candidate 必须明确分类。
- User 未确认的新方向先进入 Candidate，不占正式 ID；晋升前检查 active scope overlap 和 User approval。
- allocator 使用 remote Git ref first-writer CAS 防止不同 clone / Host 同号；同 clone 另有 common-directory lock。reservation 保持到 canonical 进入 main 后显式 finalize，放弃未创建 Task 才 release。
- 冲突时 fail closed：保留先存在 canonical Task，误建项保留为 `Cancelled` companion 或 Candidate，不覆盖历史。
- 新游戏研究默认采用 `Feasibility Audit → Review → User 决定 → Adapter / Collector → Planner Release`。

### Automatic Memory

- Git 是可审计、可回滚的长期真相源；ChatGPT Project Memory / Codex memory 只作为 recall layer。
- Public-safe Candidate 可进入 AI-Workspace；Project Private、Cross-project Private、Local-only、Unknown 或 writer-unavailable 内容进入批准的私有目标或本机 Outbox，默认不公开。
- Production 当前保持 `ASSISTED`。Canonical 规则、ADR、架构、冲突、高影响和敏感内容即使在 AUTO 也必须 Review。
- ChatGPT Project Source Pack 可生成，但当前替换仍需人工上传。

### Collector / Analysis / Report / Document 解耦

- Collector 负责采集证据。
- Knowledge / Analysis 负责事实、模型和策划结论。
- AI Report Engine 是后续重点能力，负责从 Knowledge 与模板生成报告内容。
- AI Document Assistant 只负责文档读写和权限，不承担业务分析。

### 多实例数据隔离

- 每个模拟器实例 / 账号使用独立数据库。
- 先分析单账号行为，再通过脱敏聚合层寻找共性和分群规律。
- 不把不同账号、不同游戏 Raw 数据直接混合。

### 文档和部署标准

- 策划文档默认按步骤执行，不要求阅读代码。
- 优先一键安装、一键启动、一键检查、明确成功信号、失败时唯一下一步。
- 复杂技术信息留在维护文档；策划主流程只保留必要操作。

## 当前限制与风险

- ChatGPT 直接调用 AI Document Assistant 的 Secure MCP Tunnel 仍因 OpenAI Control Plane 地区限制不可用；Codex 本地 MCP 正常。
- ChatGPT Project Sources 是上传时的快照，不会自动跟随 Git commit 更新；本次 Core Rules 与 Current State 变化后需要重新上传 00、02、03 或使用生成的 replacement list。
- Project Memory 可以引用同一项目内聊天和文件，但不保证每个新对话主动召回全部细节；项目指令和来源文件仍是稳定入口。
- 任何当前功能、任务、编号、状态或 commit 的判断必须查询对应 Git 仓库，不能仅依据本文件。
- Task Registry / allocator 已通过 TASK-0020 Review 并进入 main；任何新 Task 仍必须通过 latest-main、独立 worktree 和 remote-CAS 流程。

## 当前排队与候选方向

- Top Tycoon F4 Feasibility Audit 已是 canonical TASK-0025 / `Ready`，但 User 尚未切回该方向；不得与当前 TASK-0019 并行执行。
- Huuuge First Run 独立盲测是已存在的验证 Gate，不是已通过能力；由 User 指定未参与开发的策划后执行。
- AI Report Engine：Knowledge → Template → AI → Markdown；仍为 `Planned`，需要独立 Candidate、contract 与回归。
- Planner Toolkit：只从 Accepted、证据完整的方法中抽取可执行 Skill，不把分类模型写成 Available。
- 多实例独立数据库与跨账号脱敏聚合模型：保持 Planned，Raw 不跨账号直接混合。
- 新游戏 Adapter、Documentation Portal、Recent Updates 等方向仍需 User 批准，不因 Product Roadmap 或本文出现而自动创建 Task。

<!-- MEMORY-CONTEXT:START -->
## Automatic Memory Context

- Generated: 2026-08-29T07:36:52Z
- Effective mode during refresh: `ASSISTED`
- Context Manifest: `CONTEXT_MANIFEST.yaml`
- Project Sources update: `manual upload required`
- Private repositories: not read by default; explicit registry and authorization required

### Active public control-plane tasks

- `TASK-0018-Huuuge-Lottery-Numerical-Breakdown-Report.md` — Review
- `TASK-0019-AI-Workspace-Overview-and-Separate-Progress-Documents.md` — Review
- `TASK-0025-TOP-TYCOON-ANDROID-F4-COLLECTION-FEASIBILITY-AUDIT.md` — Ready
<!-- MEMORY-CONTEXT:END -->
