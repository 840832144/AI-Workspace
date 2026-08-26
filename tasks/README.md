# Tasks

`tasks/` 保存可直接执行的任务规格。聊天只负责通知任务编号，Codex 必须先同步 `main` 并读取对应文件，不得仅凭聊天摘要猜测范围。

## 状态

- `Draft`：仍在讨论，不执行。
- `Ready`：User 已确认，可执行。
- `In Progress`：Codex 正在实施。
- `Review`：已提交，等待 ChatGPT Review。
- `Accepted`：Review 通过。
- `Changes Requested`：需要修改。
- `Cancelled`：明确取消，保留历史。

## 最低字段

每个 Task 至少包含：Status、Owner、Executor、Goal、Scope、Non-goals、Deliverables、Acceptance、Safety、Validation 和 Handoff。

## 执行规则

1. 执行前拉取最新 `main`，读取 Global/Project `AGENTS.md`、相关 RFC/ADR、当前 Handoff 与 Task。
2. 不擅自扩大范围；发现额外优化时写入建议，由 User 决定是否进入下个 Task。
3. 实施完成后更新 Task 状态、`CHANGELOG.md` 与 `handoff/CODEX.md`，提交并推送，等待 ChatGPT Review。
4. 密钥、token、本机私有配置值、完整运行日志和业务数据不得进入 Git。
