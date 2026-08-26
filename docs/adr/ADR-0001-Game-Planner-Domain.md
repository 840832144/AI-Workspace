# ADR-0001: Game Planner Domain

- Status: Accepted
- Date: 2026-08-26
- Decision owners: User
- Related RFC: [`RFC-0001-AI-Workspace-Charter.md`](../rfc/RFC-0001-AI-Workspace-Charter.md)
- Supersedes: None

## Context

AI-Workspace 初始化时以通用 AI 协作控制面描述自身。User 已决定正式收敛目标领域，以避免 Skill、Workflow、Template 和项目标准被无关领域稀释。

## Decision

AI-Workspace 定位为 **Game Planner AI Workspace**，默认且唯一的业务领域为 Game Design。目标用户包括游戏策划、游戏数值策划、系统策划、活动策划和数据分析。

Workspace Kernel、Capability Model、Skill Tree、Workflow、Template、Roadmap 和项目控制面都必须服务游戏策划。婚礼、投资等非游戏领域不进入本 Workspace。

## Alternatives Considered

- 继续作为通用 AI Workspace：覆盖面更广，但对象模型和技能边界会持续发散。
- 维护多个领域分区：当前没有明确需求，会增加治理、审阅和所有权成本。

## Consequences

### Positive

- 核心对象、技能树和项目模板可以围绕游戏策划形成一致语言。
- 后续 Document Assistant、Workspace Sync 和 Planner Toolkit 有明确边界。
- Agent 可直接拒绝或升级领域外需求，避免长期记忆污染。

### Negative / Costs

- 非游戏需求需要使用其他 Workspace，不能复用本仓库作为默认入口。
- 现有通用措辞需要持续清理，新增内容需要领域审阅。

## Validation

- README、Architecture、AI Team、Standards、Roadmap 与 Agent 入口均声明 Game Design 边界。
- Skill Tree 和项目模板只包含游戏策划对象。
- 本次变更未新增业务代码、未迁移仓库、未修改 `feishu-doc-mcp`。

## Follow-up

- 在新增 Capability、Skill、Workflow 或 Project 时执行 Game Design 领域检查。
- 若未来需要其他领域，必须由新的 RFC/ADR 明确建立独立边界，不隐式扩张本 Workspace。
