# Workflows

Workflow 描述游戏策划目标中多个 Agent、Skill、Template、Tool、项目或外部系统之间的可重复协作顺序。

每个 Workflow 应定义：目标、触发条件、输入、步骤、责任角色、检查点、失败处理、输出、验证和交接目标。初始化阶段只建立规则，不实现自动化编排。

默认生命周期：Intake → RFC/Decision → Project plan → Execution → Validation → Status/CHANGELOG → Handoff。

- [`workspace-sync/`](workspace-sync/README.md)：在 Task、Review、状态查询和 Handoff 前刷新 Git、飞书协作层与 Host-local Context Pack。
