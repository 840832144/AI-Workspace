# ChatGPT Handoff

这是 ChatGPT 的固定交接入口。长期事实必须同步到 Capability contract、项目 Memory/Status、Task、RFC、ADR 或正式 Review，而不是只留在聊天中。

- Updated: 2026-08-27
- Primary implementation task: TASK-0016
- Concurrent task: TASK-0017 正在独立分支 / worktree 执行
- Current state: TASK-0016 **Needs changes**
- Reviewed implementation HEAD: `1a48b176d453a021c4cc15e2186ed55653b6458a`
- Review record: [`reviews/TASK-0016-CHATGPT-REVIEW-1.md`](../reviews/TASK-0016-CHATGPT-REVIEW-1.md)

## Review Decision

TASK-0016 的架构方向和 ASSISTED Pilot 通过：

- Reuse-first 选型、Candidate-first、Git canonical truth、Public/private 安全边界合理；
- Capability、Governance、ADR、Host adapters、Context Manifest 和 Source Pack 可以保留；
- 17/17 测试、Pilot 计数、最终 `ASSISTED`、Hook/AUTO 未激活和边界声明可信；
- 未触碰 Huuuge、Collector、Capture、SVN、飞书或 Document Assistant。

但 TASK 整体尚不能 Accepted，需完成三个实现修订。

## Required Fixes

1. **实现批准的 Project-private Git routing。** 当前所有非 `public/public` 内容都只进入本机 Outbox，尚不能在有批准 writer 时写入对应私有项目仓库。必须使用 disposable private repo 验证，不能读取真实 Huuuge/CR 数据。
2. **AUTO Promotion 必须 branch-safe 且事务化。** 禁止在 `main/master` 或非隔离工作树直接写 canonical；canonical、Archive、index 任一步失败必须回滚，并增加故障注入测试。
3. **Public Candidate 禁止占位 provenance。** `source_host/project/actor/reference` 不能使用 `unknown`、`n/a` 等占位值；缺失时进入 Review / Outbox，不得写公共 Inbox。

完整验收和可选优化见正式 Review 文件。

## Parallel-safety Boundary

- TASK-0016 继续只修改 AI-Workspace，并保持最终模式 `ASSISTED`。
- 不激活 production Hook，不切 production AUTO，不新增外部 Memory 服务。
- TASK-0017 使用独立 worktree / branch；两项任务不得互相覆盖工作区或配置。
- TASK-0015 的 Huuuge Capture 继续由 User 控制；体验结束前不整理、分析或写报告。

## Exact Next Action

Codex 继续同一个 TASK-0016，读取 `reviews/TASK-0016-CHATGPT-REVIEW-1.md`，完成三个 Required Fix、隔离和 fault-injection 回归，更新 Task、CHANGELOG、Pilot、Governance、ADR 与 `handoff/CODEX.md`，提交并再次等待 ChatGPT Review。
