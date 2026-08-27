# 03 — New Chat Bootstrap

新建项目对话后，按本协议开始。它的目标是防止新对话在不了解体系时直接发明方案、重复开发已有功能或给 Codex 下错误任务。

## 启动顺序

1. 读取 `00_CORE_RULES.md`。
2. 读取 `01_SYSTEM_CONTEXT.md`。
3. 读取 `02_CURRENT_STATE.md`。
4. 判断当前请求属于：讨论、设计、执行话术、当前状态查询、Review、文档生成或排障。
5. 只要请求涉及当前 Task、功能是否已实现、最新 commit、运行状态、给 Codex 下任务或 Review，先查询 Git 中的最新信息。

## 发给 Codex 任务前

必须确认：

- Task 文件是否真实存在；
- Task 状态是否为 Ready / Changes Requested；
- 当前执行仓库和真相源；
- 是否已有任务正在执行，避免并发改同一范围；
- 是否触及付费、权限、发布、外部写入或敏感数据；
- 是否已有本地、内部、官方或成熟开源方案；
- User 是否已经确认任务范围。

完整细节应先写入 AI-Workspace 的 `tasks/` 和 Handoff。发给 User 的 Codex 话术通常只包含：

```text
执行 TASK-XXXX。
请同步 AI-Workspace main 和对应业务仓库，读取任务文件。
严格按 Scope / Boundaries 实施、验证并提交。
完成后更新 Handoff，返回 commit，等待 ChatGPT Review。
```

不得在聊天中使用一个 Git 中不存在的 Task 编号。

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
6. 当前请求是否已有可复用 Capability 或工具？
7. 是否涉及付费、权限、敏感信息或不可逆操作？
8. 输出是否足够简洁、可执行？

如果第 5 项无法确认，先查 Git，不要猜。
