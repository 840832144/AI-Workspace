# Bootstrap

本目录定义新环境、新 Agent 或新协作者接入 AI-Workspace 的最小步骤。

## Repository Bootstrap

1. Clone 私有仓库并确认 remote、branch 和访问权限。
2. 安全同步 `main`，确认工作树状态。
3. 阅读根目录 `README.md`、`AI_TEAM.md`、`ARCHITECTURE.md`、`CONTRIBUTING.md`。
4. 阅读自己的固定 handoff 和相关项目 Status。
5. 确认本地 Git identity；不得把 credential 写入仓库配置文件。
6. 开始前明确目标、范围、非目标和真相源。

## New Project Bootstrap

1. 从 `templates/projects/` 复制四件套到 `projects/<slug>/`。
2. 填写 Context，并链接外部项目仓库或系统。
3. 只迁入已确认、长期有用且非敏感的 Memory。
4. 定义 Workflow 和验证关卡。
5. 初始化 Status，写明唯一下一动作。
6. 若项目改变整体体系，先创建 RFC。

## Session Completion

1. 审阅 diff 和内部链接。
2. 更新 Status、handoff 和 CHANGELOG 中适用部分。
3. 确认无 secrets、业务代码或隐私数据。
4. 按 `CONTRIBUTING.md` 提交。
5. 推送后确认远端 commit，再交接。
