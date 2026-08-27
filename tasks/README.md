# Tasks

`tasks/` 保存可直接执行的任务规格。聊天只负责通知任务编号，Codex 必须先同步 `main` 并读取对应文件，不得仅凭聊天摘要猜测范围。

## 状态

- `Draft`：仍在讨论，不执行。
- `Ready`：User 已确认，可执行。
- `In Progress`：Codex 正在实施。
- `Review`：已提交，等待 ChatGPT Review。
- `Accepted`：Review 通过。
- `Changes Requested`：需要修改。
- `Cancelled`：明确取消或误建，保留历史。

## 最低字段

每个 canonical Task 至少包含：Status、Owner、Executor、Goal、Scope、Non-goals、Deliverables、Acceptance、Safety、Validation 和 Handoff。

## Canonical Task 与附件

- `tasks/` 根目录中，标题为 `# TASK-XXXX — ...` 且包含完整 Task 字段的文件视为 canonical Task。
- 每个 canonical Task ID 在整个仓库中必须唯一。
- 授权书、Review、补充说明、实验记录等不得伪装成第二个 canonical Task；新附件应放入 `tasks/support/TASK-XXXX/`、`reviews/`、`docs/experiments/` 或对应项目目录。
- 历史上已存在的 companion 文件可以保留，但治理工具必须明确标注其类型，不能把它们当作新 Task 编号占用或第二个执行入口。

## 新 Task 分配规则

创建新 Task 前必须：

1. 从 Git 最新 `main` 枚举完整 `tasks/` 目录；
2. 建立 canonical ID、完整文件名、状态和目标摘要清单；
3. 检查同 ID 冲突、同目标重复、相关活动 Task 和并发修改范围；
4. 决定继续已有 Task、创建子任务、保留 Candidate，或分配经验证未占用的新 ID；
5. User 尚未确认时，只能保留 Candidate，不能创建 `Ready` Task；
6. 创建后重新枚举目录并验证 ID 唯一、文件名/标题一致、状态正确。

禁止根据聊天记忆、过期 Project Source、局部搜索结果或“最大编号 + 1”直接分配。编号冲突时 fail closed：先存在 Task 保持 canonical；误建 Task 标记 `Cancelled` 或迁入 Candidate；不得覆盖或删除历史。

在正式分配工具完成前，所有新编号必须由人工完成上述目录级预检，并在 Task 中记录 `Allocation evidence`。

## Candidate 规则

讨论中的新方向默认先进入 Candidate，不立即占用 Task ID。Candidate 至少记录：目标、所属项目、优先级建议、依赖、风险、User 是否确认。只有 User 明确批准后才转成 canonical Task。

新增游戏研究默认采用：

```text
Feasibility Audit
→ ChatGPT Review
→ User 决定
→ Adapter / Collector Task
→ Planner Release
```

不得从聊天直接跳到完整 Collector 开发。

## 执行规则

1. 执行前拉取最新 `main`，读取 Global/Project `AGENTS.md`、相关 RFC/ADR、当前 Handoff 与 Task。
2. 不擅自扩大范围；发现额外优化时写入建议，由 User 决定是否进入下个 Task。
3. 实施完成后更新 Task 状态、`CHANGELOG.md` 与 `handoff/CODEX.md`，提交并推送，等待 ChatGPT Review。
4. 密钥、token、本机私有配置值、完整运行日志和业务数据不得进入 Git。
5. 如果发现 Task ID、标题、状态或范围存在冲突，停止实施并先报告治理问题，不得自行选择其中一个继续。
