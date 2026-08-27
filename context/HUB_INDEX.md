# Game Planner AI Workspace｜实时 Context Hub

这是策划、ChatGPT、Codex 和 Generic Agent 的统一协作入口。Git 保存规则、Task 和状态的可审计真相；飞书提供在线阅读与协作；本地 Context Pack 供没有飞书连接的 Host 使用。

## 怎么使用

1. 先看“Workspace 入口与同步状态”。成功表现是更新时间、Git commit 和各 Context 状态清晰；显示 stale/conflict 时不要继续引用旧状态。
2. 查规则和当前任务时打开只读内容，修改建议写入“策划协作与待确认事项”。不要直接把飞书修改当作已生效规则。
3. 策划只需在协作草稿中写完整问题、期望结果和证据。成功表现是下一次 Workspace Sync 生成 Candidate/Review；失败时联系 Codex 查看 sync 状态。
4. 阅读正式云文档时，从唯一的《AI Workspace｜文档导航中心》进入；Provider 链接由 Host-local Registry 提供，Git 不保存私有标识。

## Context Set

| Context | Authority | Planner Action |
| --- | --- | --- |
| Workspace 入口与同步状态 | Git | 阅读状态；stale/conflict 时停止引用 |
| 核心规则 | Git | 阅读；修改写协作草稿 |
| 系统上下文与能力边界 | Git | 阅读；不要把 Planned 当 Available |
| 当前状态与任务入口 | Git | 每次 Task/Review 前刷新 |
| 项目全景说明 | TASK-0019 Review branch | 阅读；等待 Review 后纳入 canonical sync |
| 项目进度与能力状态 | TASK-0019 Review branch | 阅读；动态更新在该文档维护 |
| 策划协作与待确认事项 | Feishu | 可编辑；内容先进入 Candidate/Review |
| AI 行文规范 | Git | 所有 AI 在生成内容前读取 |
| Capability / Workflow / Skill 索引 | Git | 从结果能力进入执行入口 |
| 文档导航中心 | Feishu | 浏览全部正式云文档；不直接维护目录 |
| Product Roadmap | Git / Feishu 正式发布 | 查看 Current、Backlog、Ideas、Done；不据此直接执行或手工建 Task |

Provider 链接由 Host-local Registry 注入飞书 Index；公共 Git 只保存稳定别名和 authority。
