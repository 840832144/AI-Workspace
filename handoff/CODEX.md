# Codex Handoff

这是 Codex 的固定交接入口。Codex 开始仓库工作前读取，提交和推送后更新。实现细节以对应游戏项目仓库为准。

- Updated: 2026-08-26
- Current state: Game Planner Workspace Kernel documented

## Incoming Request

当前无待处理实施交接。

## Completed This Session

- 将 AI-Workspace 从通用协作空间正式收敛为 Game Planner AI Workspace。
- 定义 Workspace、Project、Capability、Skill、Workflow、Template、Tool、Agent、Memory、Status 核心对象及 Mermaid 关系图。
- 建立 Capability、Skill、Workflow、Template、Tool 五层模型。
- 建立 11 类 Game Planner Skill Tree 目录，全部标记为未实现。
- 完善 ChatGPT / Codex Ownership、Decision、Review、Tool Ownership、Security 和 Escalation 规则。
- 建立包含 Context、Memory、Workflow、Status、Reports、Assets 的统一游戏项目模板。
- 增加声明式 `workspace.yaml.example`，仅作为未来规范。
- 将 Roadmap 重构为 Workspace Foundation、Document Assistant、Workspace Sync、Planner Toolkit 四阶段。
- 以 ADR-0001 记录 Game Design 领域收敛决定。

## Confirmed Context

- Game Design 是本 Workspace 默认且唯一的业务领域。
- ChatGPT 主要负责 Architecture、RFC、Review、Workflow、Skill。
- Codex 主要负责 Implementation、Automation、Git、Testing、Deployment。
- 当前新增内容均为文档模型和模板；没有业务功能、运行时或自动校验器。
- 本次未迁移任何仓库，也未修改 `feishu-doc-mcp`。

## Evidence / References

- `docs/adr/ADR-0001-Game-Planner-Domain.md`
- `docs/architecture/WorkspaceKernel.md`
- `docs/CapabilityModel.md`
- `skills/README.md`
- `projects/TEMPLATE/`
- `workspace.yaml.example`

## Risks

- Capability 与 Skill 目前只有概念边界，尚无稳定 ID、manifest 或版本规则。
- 11 个 Skill 分类可能在实际项目中出现重叠，需要由真实用例验证后再细分。
- `workspace.yaml.example` 没有 schema、loader 或 lint，不能作为可执行配置使用。
- Git → SVN、Git → Feishu 的真相源、冲突、安全和审计规则尚未形成 RFC/ADR。

## Todo

- 审阅并决定 RFC-0003 的 Skill manifest 格式与版本规则。
- 为首批游戏策划 Capability 定义稳定 ID 和验收结果，但暂不实现 Skill。
- 在 User 明确指定后，从 `projects/TEMPLATE/` 登记第一个游戏项目。
- Phase 2 开始前，为 Document Assistant 建立独立 RFC、权限边界和验收标准。

## Constraints

- 不在本仓库实现业务代码。
- 不登记婚礼、投资等非游戏领域内容。
- 不迁移或覆盖现有仓库内容。
- 不提交 secrets、玩家明细或敏感运行数据。

## Exact Next Action

由 ChatGPT 主审 RFC-0003，并提出 Game Planner Skill manifest 的最小字段与首批 Capability 清单，交 User 决定后再进入实现评估。

## Outgoing Handoff

请 ChatGPT 以 `docs/CapabilityModel.md` 和 `skills/README.md` 为边界进行模型审阅；不要把“规划中的 Skill”描述为已实现能力。
