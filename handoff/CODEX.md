# Codex Handoff

这是 Codex 的固定交接入口。实现细节以对应外部项目仓库为准。

- Updated: 2026-08-26
- Task: TASK-0013
- Current state: Capability Discovery and Document Capability ready; waiting for ChatGPT Review

## Objective

把全局发现入口从 Tool-first 调整为 Capability-first：Agent 先识别 User 需要的稳定结果契约，再选择 Workflow、Skill、Implementation Binding 和 Tool。

## Completed

- 将仓库模板与本机 `~/.codex/AGENTS.md` 的顶层入口改为 `Capability Discovery`。
- 明确 Tool 的检查与选择只属于 Capability 实现层，不建立独立的 Tool Discovery。
- 新增 `capabilities/README.md`，建立 Catalog schema、发现顺序和四类状态：Registered/available、Registered/unavailable、Proposed、Unknown。
- 新增 `capabilities/document/README.md`，定义 `CAP-DOC` 与 7 个结果型 Document Operations；`feishu_healthcheck` 只保留为 provider preflight。
- 将 Document Assistant 定义为当前实现 provider，将 Feishu MCP tools 定义为 provider-specific Implementation Binding。
- 新增 ADR-0003 并 supersede ADR-0002；历史 ADR 保留。
- 更新 Architecture、Workspace Kernel、Capability Model、AI Team、Manifest、Roadmap、RFC-0002、Document Assistant Roadmap、Skill、Bootstrap、README、CONTRIBUTING 和 CHANGELOG。

## Confirmed Context

- Capability contract 回答“能交付什么结果”；Implementation Binding 回答“当前 Host 由什么实现”。
- Capability 是否登记与当前实现是否可用必须分开报告。
- Tool 可见不等于 Capability 已登记或已获授权；Tool 不可见不等于 Capability 不存在。
- AI-Workspace 保存公开 Catalog 与 provider-neutral contract，但不保存运行时 endpoint、credential、安装状态或连接状态。
- 公共 AI-Workspace 仍是新人唯一必需 Git 入口；私有实现仓库不是策划前置条件。
- TASK-0011 的 30 分钟独立策划盲测仍未发生，本任务没有修改采集器或 First Run 云文档。

## Validation

- Global 模板与本机文件 SHA-256 一致；本机没有 `AGENTS.override.md`。
- `CAP-DOC-*` Operations 全部具有 Outcome、Class、Required input 和 Success evidence。
- Catalog 与 Document Capability 的相对链接验证通过。
- 当前生效文档不再把 Tool-first 作为顶层发现入口；ADR-0002 和历史 CHANGELOG 只保留历史记录。
- Secret、禁用词、私有 Clone 前置、diff 和 Git 状态检查通过。

## Risks

- Capability Discovery 当前是文档治理规则，不是已实现的 registry/resolver；Agent 仍需读取 Catalog。
- Codex 每次运行只构建一次 Agent 指令链；本次打开的会话不会证明新 Global 文件已自动重载，重启后生效最稳妥。
- Implementation availability 依赖具体 Host；Catalog 只能记录可审阅状态，不能替代实时 healthcheck。
- Document Assistant Roadmap 的 `DA-CAP-*` 是 provider 规划 ID，`CAP-DOC-*` 是稳定 Operation ID；后续必须避免混用。

## Exact Next Action

ChatGPT Review Capability Catalog、Document Capability、ADR-0003 和 Global AGENTS。重点确认：Capability-first 顺序、Catalog schema、Operation 粒度、failure semantics、provider/Tool 边界，以及 AI-Workspace 是否继续避免承担运行时工具入口职责。
