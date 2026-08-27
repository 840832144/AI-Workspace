# 02 — Current State

_Last reviewed: 2026-08-27_

本文件是便于 ChatGPT Project 新对话快速进入状态的动态摘要。执行任务前仍需读取 Git 中的最新 Task、Status、Handoff 和业务仓库。

## 已完成的重要里程碑

- AI-Workspace 已建立 Game Planner 领域边界、Workspace Kernel、Capability Model、Skill Tree、Project Template、Evidence Standard、Task 与 Handoff 机制。
- Huuuge Collector 已形成 SVN-first 策划发布流程，并具备环境检查、READY、广泛 RPC 捕获、protobuf decode、Session manifest、自动 lifecycle markers 和 Clean Finalize。
- Huuuge Knowledge Index 已按 Slots、Systems、Events、Others 整理研究模块，并采用统一 L0–L4 Evidence Standard。
- AI Document Assistant 已接入 Codex，可读写飞书云文档并自动设置企业内可编辑权限。
- Codex 跨项目 Global AGENTS 已采用 Capability-first / Reuse-first 规则。
- Codex 1+4 Subagent Pilot 已通过 Review；默认 `OFF`，可在受限权限和适合的复杂任务中手动启用。
- Git-backed Automatic Memory 当前处于 `Review`；production 默认 `ASSISTED`，Global hook 与 production AUTO 未激活。
- “策划在新电脑上按文档和 AI 引导完成采集与文档流程”的首轮验收暂定通过，后续通过真实使用继续优化。

## 当前治理任务

当前 User 已授权：

```text
AI-Workspace/tasks/TASK-0020-Task-Allocation-and-Namespace-Governance.md
```

状态：`Review`；实现位于独立分支，等待 ChatGPT Review，尚未合入 main。

背景：仓库曾同时出现两个不同内容的 canonical `TASK-0018`。先存在的 Huuuge Lottery Task 保持 canonical；误建 Cash Frenzy 文件现为 `Cancelled` companion，完整规格已从 Git 历史恢复为非执行 Candidate，等待 TASK-0020 Accepted 后由 User 决定是否晋升。

TASK-0020 当前结果：

- 已建立可重建 Registry 和 canonical / companion / candidate / review 分类；
- 已实现 `scan / validate / next / release / candidate / promote`；
- duplicate、格式/Registry 漂移、并发分配、lock 和非最新 Git fail closed；
- ADR-0006 提议采用全局 `TASK-XXXX` + `project_key` + 可选 alias；
- 14/14 disposable tests 与 PowerShell 5.1 回归通过；真实仓库当前 8 canonical、0 collision；
- TASK-0021 在本任务期间进入 main，已重新同步并纳入 Registry，没有被覆盖；
- 不执行 Cash Frenzy，不修改任何业务仓库。

## 当前 Huuuge 任务

当前相关文件包括：

```text
AI-Workspace/tasks/TASK-0015-Huuuge-Lottery-Live-Numerical-Breakdown.md
AI-Workspace/tasks/TASK-0018-Huuuge-Lottery-Numerical-Breakdown-Report.md
```

实际状态和执行顺序必须读取文件、最新 Handoff 和 `huuuge-android-research`。TASK-0020 不得修改 Collector、Raw Capture 或 Lottery 业务分析范围。

## 当前并行 Workspace 任务

- `TASK-0019-AI-Workspace-Overview-and-Separate-Progress-Documents.md`：`Ready`。
- `TASK-0021-Workspace-Live-Context-Hub.md`：`Ready`；负责 Live Context / Workspace Sync，与本 Task 的 Registry / allocator 范围分离。

并行任务必须使用独立 branch / linked worktree。TASK-0020 的 Registry 只登记 TASK-0021，不执行、改写或提前实现其飞书 / Context Hub 范围。

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
- Task Registry / allocator 已在 TASK-0020 独立分支完成 Review Round 1 的五项修复，等待 ChatGPT Review Round 2；合入 main 前不能假装分支工具已成为生产治理规则。

## 近期候选方向

- Cash Frenzy Collector Feasibility Audit：完整规格已恢复为非执行 Candidate；等待 TASK-0020 Accepted 和 User 再次确认后才可通过 allocator 晋升。
- Top Tycoon Feasibility Audit：Cash Frenzy Review 后再建立，不并行。
- 绯闻港口 Feasibility Audit：Top Tycoon Review 后再建立，不并行。
- AI Report Engine：Knowledge → Template → AI → Markdown。
- Planner-facing UX & Deployment Standard 的持续落地。
- 多实例独立数据库与跨账号脱敏聚合模型。

<!-- MEMORY-CONTEXT:START -->
## Automatic Memory Context

- Generated: 2026-08-27T08:31:10Z
- Effective mode during refresh: `ASSISTED`
- Context Manifest: `CONTEXT_MANIFEST.yaml`
- Project Sources update: `manual upload required`
- Private repositories: not read by default; explicit registry and authorization required

### Active public control-plane tasks

- `TASK-0016-Automatic-Cross-Conversation-Memory-Curation.md` — Review
- `TASK-0018-Huuuge-Lottery-Numerical-Breakdown-Report.md` — Review
- `TASK-0019-AI-Workspace-Overview-and-Separate-Progress-Documents.md` — Ready
- `TASK-0020-Task-Allocation-and-Namespace-Governance.md` — Review
- `TASK-0021-Workspace-Live-Context-Hub.md` — Ready
<!-- MEMORY-CONTEXT:END -->
