# RFC-0001: AI-Workspace Charter

- Status: Accepted
- Date: 2026-08-26
- Actors: User, ChatGPT, Codex

## Summary

建立 AI-Workspace 作为 Game Planner AI Workspace 的治理与协调总控仓库，而不是代码仓库或通用 AI 平台。

## Motivation

多个 Agent 和多个项目如果只依赖聊天上下文，会出现决策丢失、状态冲突、重复实施和无法审计的问题。需要一个独立、轻量、长期可维护的 Git 真相源，保存跨项目协作规则和可继续执行的状态。

## Charter

AI-Workspace 负责：

- Game Design 领域边界与 Workspace Kernel。
- AI 团队角色和协作协议。
- 跨项目 RFC 与长期 ADR。
- 可复用 Skill、Workflow、Template 和 Standard 的定义与索引。
- 项目 Context、Memory、Workflow、Status 控制面。
- ChatGPT 与 Codex 固定交接入口。
- AI 协作体系路线图与变更记录。

## Non-goals

- 不服务婚礼、投资等非游戏领域，不建设通用 AI 能力市场。
- 不承载业务代码、构建产物或部署配置。
- 不替代项目自身 README、测试和 issue tracker。
- 不保存 credential、个人数据、客户数据或完整业务数据。
- 不通过复制现有仓库建立“影子实现”。
- 不在本阶段迁移任何现有项目。

## Governance

- User 对目标、优先级和最终冲突拥有裁决权。
- Accepted RFC 定义体系方向；长期架构决定进入 ADR。
- Git `main` 是共享记录来源，禁止 force-push 和无说明改写历史。
- 项目实现事实必须引用对应项目仓库的 commit 或验证结果。
- 所有 Agent 遵守 `CONTRIBUTING.md` 和固定 handoff 格式。

## Consequences

### Positive

- Agent 可以脱离原聊天上下文继续工作。
- 跨项目决策、状态和证据具有统一入口。
- 业务仓库保持聚焦，不被全局治理文件污染。

### Costs

- 需要持续维护 Status、handoff 和 CHANGELOG。
- 必须主动清理重复、过期和已被 supersede 的信息。

## Acceptance Criteria

- 核心目录和文档存在。
- ChatGPT 与 Codex 有固定交接文档。
- 游戏项目 Context、Memory、Workflow、Status、Reports、Assets 结构和模板已定义。
- 初始化内容提交并推送到 Git。
