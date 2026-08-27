# 03 — New Chat Bootstrap

新建项目对话后，按本协议开始。它的目标是防止新对话在不了解体系时直接发明方案、重复开发已有功能或给 Codex 下错误任务。

## 启动顺序

1. 读取 `standards/PLANNER_WRITING_STYLE.md`。
2. 读取 `00_CORE_RULES.md` 与 `01_SYSTEM_CONTEXT.md`。
3. 运行 Workspace Sync，读取最新 Git、`LIVE_CONTEXT_MANIFEST.json` 和 Host-local Context Pack。
4. 只有 Workspace Sync unavailable 时才把 `02_CURRENT_STATE.md` 当离线回退，并明确它可能过期。
5. 判断当前请求属于：讨论、设计、执行话术、当前状态查询、Review、文档生成或排障。
6. 只要请求涉及当前 Task、功能是否已实现、最新 commit、运行状态、给 Codex 下任务或 Review，先查询 Git 中的最新信息。
7. `CONTEXT_MANIFEST.yaml` 与 Project Source Pack 继续作为 Memory/Bootstrap 快照；动态状态由 Live Context 和 Git 提供，不再依赖人工替换 `02_CURRENT_STATE.md` 才能获知。

## 发给 Codex 任务前

必须确认：

- Task 文件是否真实存在；
- Task 状态是否为 Ready / Changes Requested；
- 当前执行仓库和真相源；
- 是否已有任务正在执行，避免并发改同一范围；
- 是否触及付费、权限、发布、外部写入或敏感数据；
- 是否已有本地、内部、官方或成熟开源方案；
- User 是否已经确认任务范围。

### 新建 Task 的编号预检

任何会创建新 Task 的请求，必须额外完成：

1. 从 Git 最新 `main` 枚举完整 `tasks/` 目录，不只搜索一个猜测编号；
2. 列出所有 canonical Task 的 ID、完整文件名和状态；
3. 检查同 ID 冲突、同目标重复、范围重叠和附件误判；
4. 只有 User 已确认且 ID 经目录验证未占用时，才创建 `Ready` Task；
5. 未确认需求先进入 Candidate，不分配正式 Task ID；
6. 创建后重新读取 `tasks/`，验证 ID 唯一和文件可见性。

不得把“当前看到的最大编号 + 1”当作充分依据，也不得根据另一个对话的记忆分配编号。若发现冲突，停止执行、保留先存在 Task、将误建项标记 `Cancelled` 或迁入 Candidate，并先建立治理修复 Task。

完整细节应先写入 AI-Workspace 的 `tasks/` 和 Handoff。发给 User 的 Codex 话术通常只包含：

```text
执行 TASK-XXXX。
请同步 AI-Workspace main 和对应业务仓库，读取任务文件。
严格按 Scope / Boundaries 实施、验证并提交。
完成后更新 Handoff，返回 commit，等待 ChatGPT Review。
```

不得在聊天中使用一个 Git 中不存在、存在冲突或尚未通过分配预检的 Task 编号。

## Review 输出

Review 默认采用：

```text
结果：Accepted / Needs changes

必须修改：
- 仅列阻塞项

可选优化：
- 作为下个 Task 候选，由 User 决定

下一步：
- 一条明确动作或简短 Codex 话术
```

发现优化项时，不擅自扩大当前任务；先简要告诉 User，由 User 决定是否进入下一 Task。

## Huuuge 请求

默认顺序：Slots → Systems → Events → Others。

限时活动可临时插队，但第一目标是保住实时证据。涉及付费、充值、礼包、票券或大量资源消耗时，User 亲自决定并执行；AI 只提示、记录和分析。

任何数值结论必须标记：

```text
Confirmed / Estimate / Hypothesis / Decision proposal
```

## 新游戏研究请求

新游戏不得从讨论直接进入完整 Collector 开发。默认阶段为：

```text
Feasibility Audit
→ ChatGPT Review
→ User 决定是否继续
→ Adapter / Collector Task
→ Planner Release
```

每个游戏使用独立实例、账号别名、Session、Raw 目录和业务证据；不得与 Huuuge 或其他游戏 Raw 混合。

## 文档请求

先区分：

- 业务内容生成：由分析或 Report 能力负责；
- 飞书读写：由 Document Capability / AI Document Assistant 负责。

面向策划的文档使用步骤化中文，不要求理解代码。正式云文档创建前先搜索防重；更新后回读正文和权限。

## 快速自检

正式回答前，确认自己能回答：

1. 当前项目核心目标是什么？
2. Huuuge 的研究优先级是什么？
3. AI-Workspace 和业务仓库谁分别是真相源？
4. ChatGPT、Codex、User 分别负责什么？
5. 当前 Task 是什么，是否真的从 Git 读取？
6. 若要新建 Task，是否已枚举完整目录并验证 ID 唯一？
7. 当前请求是否已有可复用 Capability 或工具？
8. 是否涉及付费、权限、敏感信息或不可逆操作？
9. 输出是否足够简洁、可执行？
10. 本轮是否产生需要 Candidate/Review/Outbox 的长期记忆，且没有重复 canonical update？

如果第 5 或第 6 项无法确认，先查 Git，不要猜。
