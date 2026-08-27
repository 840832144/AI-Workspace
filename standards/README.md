# Standards

本目录保存已生效的跨项目规则。新标准应来自 Accepted RFC 或 ADR，并说明适用范围和版本。

初始化基线：

- Domain：默认且唯一的业务领域是 Game Design；不登记非游戏领域内容。
- Evidence：Confirmed、Hypothesis、Decision、Blocker 分开记录。
- Security：不提交 secret、token、私钥、个人数据和完整业务数据。
- Ownership：实现归项目仓库，治理归 AI-Workspace。
- Dates：状态文档使用绝对日期和时区。
- Naming：RFC/ADR 使用四位连续编号；项目目录使用稳定、可读 slug。
- Language：面向策划和用户的文档默认使用中文；只在专有名词、命令、文件名、稳定技术术语或必要解释中保留其他语言。
- Cloud Documents：新文档默认设置企业内可编辑；User 明确要求其他权限时才覆盖。管理员策略失败不得触发重复创建。
- Projects：每个游戏项目使用 `projects/TEMPLATE/` 的 Context、Memory、Workflow、Status、Reports、Assets 结构。
- Handoff：必须给出唯一明确的下一动作，不能只给聊天摘要。
- History：不用覆盖历史方式“纠错”；使用 supersede、changelog 和新 commit。

## 项目证据标准

- [`Huuuge Evidence Standard`](HUUUGE_EVIDENCE_STANDARD.md)：为 Huuuge Research 定义 L0–L4、Schema/Config/Runtime/UI/Manual 引用与升级/降级规则；当前状态为 Proposed，等待 ChatGPT Review。

## Memory 标准

- [`Memory Governance Standard`](MEMORY_GOVERNANCE.md)：定义 Candidate-first 捕获、Public/Private/Local-only 路由、Secret gate、去重、冲突、AUTO allowlist、Review、Archive、并发与 Context refresh；当前状态为 Proposed，等待 ChatGPT Review。

## 行文标准

- [`策划协作行文规范`](PLANNER_WRITING_STYLE.md)：定义完整中文段落、结论—依据—下一步、策划步骤、格式边界和轻量检查；当前状态为 Proposed，等待 ChatGPT Review。

## 产品想法治理

- [`Idea Governance`](IDEA_GOVERNANCE.md)：定义长期产品 Idea 的防重、Current/Backlog/Ideas/Done 分类、ChatGPT 收尾 Handoff 与 Codex Product Roadmap 更新规则；当前状态为 Review，等待 ChatGPT Review。
