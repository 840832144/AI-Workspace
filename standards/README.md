# Standards

本目录保存已生效的跨项目规则。新标准应来自 Accepted RFC 或 ADR，并说明适用范围和版本。

初始化基线：

- Domain：默认且唯一的业务领域是 Game Design；不登记非游戏领域内容。
- Evidence：Confirmed、Hypothesis、Decision、Blocker 分开记录。
- Security：不提交 secret、token、私钥、个人数据和完整业务数据。
- Ownership：实现归项目仓库，治理归 AI-Workspace。
- Dates：状态文档使用绝对日期和时区。
- Naming：RFC/ADR 使用四位连续编号；项目目录使用稳定、可读 slug。
- Projects：每个游戏项目使用 `projects/TEMPLATE/` 的 Context、Memory、Workflow、Status、Reports、Assets 结构。
- Handoff：必须给出唯一明确的下一动作，不能只给聊天摘要。
- History：不用覆盖历史方式“纠错”；使用 supersede、changelog 和新 commit。
