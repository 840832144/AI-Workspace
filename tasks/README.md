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

每个新 canonical Task 至少包含：Status、Project key、Owner、Executor、Priority、Date、Goal、Scope、Non-goals、Deliverables、Acceptance、Safety、Validation 和 Handoff。`Project key` 必须使用大写字母、数字和单连字符；仅代码中明确列出的 `TASK-0014` 至 `TASK-0019` 历史 grandfather 集合可以缺省。

canonical identity 采用全局唯一 `TASK-XXXX`。`project_key` 用于项目过滤，可选 `human_alias` 用于阅读；两者都不能替代 canonical ID。

## Canonical Task 与附件

- `tasks/` 根目录中，标题为 `# TASK-XXXX — ...` 且包含完整 Task 字段的文件视为 canonical Task。
- 每个 canonical Task ID 在整个仓库中必须唯一。
- 授权书、Review、补充说明、实验记录等不得伪装成第二个 canonical Task；新附件应放入 `tasks/support/TASK-XXXX/`、`reviews/`、`docs/experiments/` 或对应项目目录。
- 历史上已存在的 companion 文件可以保留，但必须显式写 `Kind: companion`，且 canonical reference 必须解析到存在、ID 与 companion 文件名一致的 canonical Task。标题格式错误且没有显式 Kind 的文件按 malformed canonical 失败。

## 新 Task 分配规则

创建新 Task 前必须：

1. 从 Git 最新 `main` 枚举完整 `tasks/` 目录；
2. 建立 canonical ID、完整文件名、状态和目标摘要清单；
3. 检查同 ID 冲突、同目标重复、相关活动 Task 和并发修改范围；
4. 决定继续已有 Task、创建子任务、保留 Candidate，或分配经验证未占用的新 ID；
5. User 尚未确认时，只能保留 Candidate，不能创建 `Ready` Task；
6. 创建后重新枚举目录并验证 ID 唯一、文件名/标题一致、状态正确。

禁止根据聊天记忆、过期 Project Source、局部搜索结果或“最大编号 + 1”直接分配。编号冲突时 fail closed：先存在 Task 保持 canonical；误建 Task 标记 `Cancelled` 或迁入 Candidate；不得覆盖或删除历史。

正式工具入口：

```powershell
python .\tools\tasks\task_cli.py scan
python .\tools\tasks\task_cli.py validate
python .\tools\tasks\task_cli.py next --purpose "approved-task"
```

`next` 先完整 scan / validate / latest-main gate，再通过 remote Git ref first-writer CAS 保留 ID；不是只读 `max + 1`。同 clone 另有 common-directory lock，不同 clone / Host 由 remote CAS 在创建 Task 前排他。放弃未使用 reservation 时用 token 执行 `release`；创建或晋升 Task 后保留 reservation，直到 canonical 进入最新 main 才执行 `finalize`。

## Candidate 规则

讨论中的新方向默认先进入 Candidate，不立即占用 Task ID。Candidate 至少记录：目标、所属项目、优先级建议、依赖、风险、User 是否确认。只有 User 明确批准后才转成 canonical Task。

Candidate 路径与操作见 [`candidates/README.md`](candidates/README.md)。工具只接受明确 `Approved / Confirmed` 的 User decision；active 目标重叠时默认阻断，必须明确继续已有 Task 或作为子任务。

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
6. 修改 Task、Candidate 或 Review 后重建 `TASK_REGISTRY.yaml` 并再次运行 validator；Registry 是可重建索引，不是第二真相源。
