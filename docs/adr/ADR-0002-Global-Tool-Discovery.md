# ADR-0002: Global Tool Discovery

- Status: Superseded
- Date: 2026-08-26
- Decision owners: User
- Related RFC: [`RFC-0002-Document-Assistant.md`](../rfc/RFC-0002-Document-Assistant.md)
- Supersedes: None
- Superseded by: [`ADR-0003-Capability-First-Discovery.md`](ADR-0003-Capability-First-Discovery.md)

## Context

Document Assistant 已经是多个项目可以复用的公司文档能力。如果工具发现、接入入口和安全规则只记录在 AI-Workspace，新打开的其他仓库无法获得一致指引，AI-Workspace 也会逐渐承担超出 Game Design 治理边界的运行时职责。

Codex 支持在 `~/.codex/AGENTS.md` 中建立全局规则，再叠加每个仓库的项目规则。这一层适合保存跨项目稳定约定，不适合保存项目状态、业务事实或 credential。

## Decision

1. Tool Discovery、共享 Document Assistant 入口、云文档默认权限与跨项目安全基线由 `~/.codex/AGENTS.md` 提供。
2. 公共 AI-Workspace 在 `bootstrap/AGENTS.md` 保存可审阅、可版本化的全局模板和策划使用规则，但该仓库本身不是运行时工具入口。新人使用已配置工具，不需要访问私有实现仓库。
3. AI-Workspace 仍可定义 Game Design 对 Capability、Workflow、Skill、Template 和 Tool 的使用契约，也可以引用外部工具；不得维护运行时工具目录、安装状态、endpoint、credential 或连接状态。
4. 项目级 `AGENTS.md` 只补充项目领域、授权、安全和验证规则，不复制共享工具实现。
5. Document Assistant 的实现、测试与实际配置继续由外部实现仓库和受控运行环境负责。

## Tool Discovery Contract

Agent 在需要外部能力时必须：

1. 读取生效的 Global 与项目指令；
2. 检查当前 Host 实际提供的 MCP、Connector、Skill、Plugin 和内置工具；
3. 区分 READ、WRITE 与 ADMIN/SECURITY；
4. 优先使用已批准的专用接口和现有实现；
5. 在外部修改前确认目标，修改后验证结果；
6. 工具不可用时准确报告，不自行建立替代入口或绕过安全策略。

## Consequences

### Positive

- Codex 在任意项目中都能发现共享文档能力和一致安全规则。
- Game Design Workspace 不再承担公司级工具目录职责，领域边界更清晰。
- 项目规则可以针对本项目收紧权限，而不需要复制工具说明。
- 只获得公共 AI-Workspace 权限的策划仍能读取完整接入规则，不会因私有实现仓库而阻塞入口。

### Negative / Costs

- 全局模板更新后，需要受控同步到每台 Codex 设备并重新启动会话。
- `AGENTS.override.md` 会遮蔽同级全局模板，排障时必须先检查 override。
- ChatGPT 或其他 Host 不会自动读取 Codex 的全局文件，仍需各 Host 使用其批准的接入机制。

## Validation

- `bootstrap/AGENTS.md` 与本机 `~/.codex/AGENTS.md` 内容一致。
- 模板包含 Tool Discovery、Document Assistant、READ/WRITE/ADMIN、安全和云文档默认权限规则。
- 模板明确私有实现仓库只供已授权维护者追溯，不是策划使用前置条件。
- Workspace Architecture、Kernel、Manifest 和 Roadmap 均不再把 AI-Workspace 描述为运行时工具入口。

## Follow-up

- ChatGPT 审阅全局规则是否足够清晰、最小且不与项目级指令冲突。
- 后续设备接入使用 `bootstrap/AGENTS.md`，已有全局规则必须合并，不得盲目覆盖。
