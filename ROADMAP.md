# Roadmap

## Phase 0 — Control Plane Bootstrap

状态：Completed

- 建立总控仓库目录和核心治理文档。
- 建立 Workspace Charter、Document Assistant、Skill System 三份初始 RFC。
- 建立 ChatGPT / Codex 固定交接入口。
- 定义项目必须包含 Context、Memory、Workflow、Status。

## Phase 1 — Operating Standards

状态：Planned

- 采纳证据、命名、安全和状态更新标准。
- 建立 ADR 编号与审阅流程。
- 定义项目登记、归档和 supersede 规则。
- 为交接和项目状态增加轻量一致性检查。

## Phase 2 — Skill Registry

状态：Planned

- 根据 RFC-0003 定义 Skill manifest 和版本规则。
- 登记现有可复用 Skill，不迁移其实现。
- 建立兼容性、安全审阅和弃用流程。

## Phase 3 — Workflow Orchestration

状态：Planned

- 建立需求到 RFC、ADR、执行、验证、交接的标准工作流。
- 定义 ChatGPT 与 Codex 的任务路由和冲突处理。
- 增加跨项目依赖图和里程碑视图。

## Phase 4 — Sustainable Automation

状态：Future

- 在不引入业务代码的前提下，评估文档校验、链接检查和状态汇总自动化。
- 建立总控仓库健康度指标。
- 定期清理失效 Memory、过期 Handoff 和已被替代的标准。

路线图只描述体系能力建设；具体项目里程碑应放在各自 `projects/<project>/STATUS.md`。
