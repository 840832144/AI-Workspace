# ChatGPT Handoff

这是 ChatGPT 的固定交接入口。长期事实必须同步到 Capability contract、项目 Memory/Status、RFC 或 ADR，而不是只留在聊天中。

- Updated: 2026-08-26
- Task: TASK-0013
- Current state: Ready for ChatGPT Review

## Review Objective

审阅 Capability-first Discovery：Global AGENTS 应先从 User Outcome 匹配 Capability，Tool 只在 Implementation Binding 阶段选择。

## Prepared Files

- `bootstrap/AGENTS.md`
- `capabilities/README.md`
- `capabilities/document/README.md`
- `docs/adr/ADR-0003-Capability-First-Discovery.md`
- `docs/adr/ADR-0002-Global-Tool-Discovery.md`
- `ARCHITECTURE.md`
- `docs/architecture/WorkspaceKernel.md`
- `docs/CapabilityModel.md`
- `workspace.yaml.example`
- `docs/rfc/RFC-0002-Document-Assistant.md`
- `docs/roadmaps/DocumentAssistantCapabilityRoadmap.md`
- `CHANGELOG.md`

## Confirmed Decisions

- Global 顶层入口是 Capability Discovery，不建立独立的 Tool Discovery。
- 发现顺序是 User Outcome → Catalog → Operation/Class → Workflow/Skill → Implementation Binding → Tool → capability-level evidence。
- `Document Capability` 是 provider-neutral contract；Document Assistant 是当前 provider；Feishu tools 是实现接口。
- `Unknown capability`、`Implementation unavailable`、`Unauthorized` 和 `Validation failed` 必须分开报告。
- AI-Workspace 维护公开 Catalog，但不登记运行时 endpoint、credential、安装状态或连接状态。
- 公共新人入口和现有 30 分钟 First Run 路径保持不变。

## Review Checklist

1. Catalog schema 是否足以支持后续 Game Planner Capabilities？
2. Capability contract 与 Implementation Binding 是否清晰分离？
3. `CAP-DOC-*` 的 7 个结果型 Operations 是否过粗、过细或遗漏关键 Outcome？
4. READ、WRITE、ADMIN/SECURITY 分类与默认公司可编辑规则是否一致？
5. 四种 failure semantics 是否足以防止“能力不存在”和“实现不可用”混淆？
6. Document Assistant 是否已明确成为 provider，而不是 Capability 本身？
7. Architecture、Kernel、Manifest 和 Roadmap 是否仍然避免运行时工具目录职责？
8. ADR-0003 supersede ADR-0002 的历史处理是否合规？

## Known Risks

- 当前只有文档规范，没有 Capability resolver 或自动路由实现。
- Catalog 中的 implementation status 不能替代当前 Host healthcheck。
- ChatGPT 不自动读取 Codex Global 文件；其他 Host 需要使用各自批准的 Capability/Provider 接入机制。
- TASK-0011 独立策划盲测仍待 User 安排，不应在本次 Review 中误标为完成。

## Exact Next Action

ChatGPT 按清单给出 `Accepted` 或 `Needs changes`。本轮只审阅架构、Catalog、Document contract 和边界，不开发 resolver，不修改 Document Assistant，也不修改 ChatGPT 设置。
