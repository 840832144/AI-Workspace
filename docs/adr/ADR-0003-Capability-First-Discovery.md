# ADR-0003: Capability-First Discovery

- Status: Accepted
- Date: 2026-08-26
- Decision owners: User
- Related RFC: [`RFC-0002-Document-Assistant.md`](../rfc/RFC-0002-Document-Assistant.md)
- Supersedes: [`ADR-0002-Global-Tool-Discovery.md`](ADR-0002-Global-Tool-Discovery.md)

## Context

ADR-0002 将跨项目发现入口直接建模为 Tool Discovery。这会让 Agent 从当前 Host 可见的 MCP、Connector、Skill、Plugin 或脚本出发，再反推用户需要的结果，混淆稳定 Capability contract 与易变实现。

User 决定改为 Capability-first：先识别“要完成什么”，再选择 Workflow、Skill 和实现；Tool 只属于 Capability 的实现层。

## Decision

1. Global AGENTS 建立 `Capability Discovery`，不建立独立的 Tool Discovery。
2. 公共 AI-Workspace 维护可审阅的 [`Capability Catalog`](../../capabilities/README.md) 与 provider-neutral contract。
3. Agent 必须先从 User 目标匹配 Capability、Operation、操作等级和成功证据，再检查当前 Host 的 Implementation Binding。
4. MCP、Connector、Skill、Plugin、仓库脚本和内置工具都是实现候选；其发现与选择只发生在 Capability 已确定之后。
5. Capability contract 与 Implementation availability 分开记录。没有可用 Tool 不等于 Capability 不存在；Tool 可见也不等于 Capability 已登记或已获授权。
6. `Document Capability` 是共享平台契约；`Document Assistant` 是当前实现 provider；Feishu MCP tools 是 provider-specific 接口。
7. AI-Workspace 不登记运行时 endpoint、credential、安装状态或连接状态，因此 Capability Catalog 不重新承担工具入口职责。

## Discovery Contract

```text
User outcome
  → Capability Catalog
  → Capability operation + READ/WRITE/ADMIN class
  → Workflow / Skill
  → Implementation Binding / Provider
  → Tool schema
  → execution
  → capability-level evidence
```

出现失败时必须区分：

- `Unknown capability`：Catalog 和项目规则都没有匹配契约；
- `Implementation unavailable`：Capability 已登记，但当前 Host 没有批准的 provider/Tool；
- `Unauthorized`：实现存在，但当前任务或 principal 没有操作权限；
- `Validation failed`：Tool 已调用，但 Capability 成功证据未满足。

## Consequences

### Positive

- User 目标不再依赖某个 Host 当前可见的工具品牌或名称。
- Provider 和 Tool 可以替换，而上层 Workflow 与 Capability 验收保持稳定。
- 文档能力可被 Codex、ChatGPT 或未来 Host 通过不同实现消费。
- 缺少私有实现权限的策划仍可从公共 Catalog 理解可用能力和管理员前置。

### Negative / Costs

- 需要维护 Capability contract 与 Implementation Binding 两种状态。
- Agent 不能只凭 tool list 开始执行，必须先完成一次结果契约匹配。
- 旧文档中的 Tool-first 表述需要迁移；ADR-0002 保留为历史记录并标记 Superseded。

## Validation

- Global AGENTS 顶层入口为 Capability Discovery。
- `capabilities/README.md` 提供 Catalog，`capabilities/document/README.md` 提供首个共享契约。
- Architecture、Kernel、Capability Model、Manifest、Roadmap 和 Document Assistant 文档统一使用 Capability-first 层次。
- Global 模板与本机 `~/.codex/AGENTS.md` 内容一致。

## Follow-up

- ChatGPT 审阅 Capability ID、Catalog schema、Document Operations 和 failure semantics。
- Review 通过前不实现 registry、resolver、自动选择器或新的 Tool。
