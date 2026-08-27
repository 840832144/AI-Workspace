# AI-Workspace

AI-Workspace 是面向游戏策划团队的 **Game Planner AI Workspace**。它以 Git 为协作真相源，管理游戏设计工作中的架构、能力、技能、工作流、模板、项目记忆、状态与 Agent 交接；本仓库不承载业务代码。

## 目标用户

- 游戏策划：玩法分析、方案设计和策划报告。
- 游戏数值策划：经济、付费、概率、成长与平衡设计。
- 系统策划：系统规则、任务、循环与功能结构设计。
- 活动策划：活动机制、Battle Pass、奖励和运营节奏设计。
- 数据分析：通过 Excel、SQL、Python 支撑策划判断与复盘。

## 仓库职责

本仓库负责回答四类问题：

1. 游戏策划 AI 工作台如何组织：Workspace Kernel、Capability Model、RFC、ADR 和标准。
2. AI 团队如何协作：角色所有权、Capability Discovery、审阅规则、工作流、实现边界和安全规则。
3. 游戏项目当前是什么状态：Context、Memory、Workflow、Status、Reports 和 Assets。
4. ChatGPT 与 Codex 如何交接：固定 handoff、确认事实、风险与下一动作。

项目实现、运行时数据、凭据和项目私有产物必须留在各自仓库或受控系统中。AI-Workspace 只记录关系、经过验证的事实和可复用的游戏策划方法。

## 核心结构

```text
AI-Workspace/
├── docs/
│   ├── architecture/  # Workspace Kernel
│   ├── experiments/   # 有边界、可复查的 Pilot 记录
│   ├── roadmaps/      # 服务与工具的 Capability Roadmap
│   ├── rfc/           # 提案、章程和跨体系设计
│   └── adr/           # 已采纳的架构决策记录
├── skills/            # Game Planner Skill Tree
├── capabilities/      # Capability Catalog 与稳定结果契约
├── workflows/         # 游戏策划工作流规范
├── templates/         # RFC、ADR、项目和交接模板
├── standards/         # 命名、证据、安全和文档标准
├── memory/            # Public-safe Candidate、Review、Archive 与索引
├── solutions/         # 已验证、可复用的 Public-safe Solution records
├── tools/memory/      # Memory reference implementation 与 Windows 入口
├── projects/          # 游戏项目控制面与统一模板
├── handoff/           # ChatGPT / Codex 固定交接入口
├── bootstrap/         # 新环境、Global AGENTS 与 Codex Agent 模板
├── tasks/             # 可执行任务规格与状态
└── workspace.yaml.example  # Workspace Manifest 规范示例
```

核心对象和关系见 [`docs/architecture/WorkspaceKernel.md`](docs/architecture/WorkspaceKernel.md)，能力分层见 [`docs/CapabilityModel.md`](docs/CapabilityModel.md)，统一发现入口见 [`Capability Catalog`](capabilities/README.md)。

当前登记项目：[`huuuge-android-research`](projects/huuuge-android-research/README.md)。

## 阅读顺序

新 Agent 或新会话按以下顺序开始：

1. `AI_TEAM.md`
2. `ARCHITECTURE.md`
3. `docs/architecture/WorkspaceKernel.md`
4. `docs/CapabilityModel.md`
5. `capabilities/README.md`
6. `CONTRIBUTING.md`
7. `projects/README.md`
8. 自己对应的 `handoff/CHATGPT.md` 或 `handoff/CODEX.md`
9. 相关 RFC、ADR 和项目 Status

## 基本原则

- Game Design 是默认且唯一的业务领域。
- Git 是协作记录的最终来源。
- 已确认事实与假设必须分开记录。
- 项目代码仓库是实现真相源；AI-Workspace 是游戏策划协作和治理真相源。
- 不在本仓库保存密钥、token、个人数据、完整运行日志或业务数据。
- 跨项目变更先写 RFC；不可逆或长期架构选择再写 ADR。
- 每次有意义的工作都必须留下可由下一个 Agent 独立继续的记录。

当前阶段只建立 Workspace Kernel、能力模型、Capability Roadmap、技能树和游戏项目标准，不迁移现有项目，也不实现业务功能。

TASK-0016 增加了治理控制面的 Memory reference implementation；它只处理 public-safe 元数据、Candidate 和 Context refresh，不把本仓库变成通用 Agent memory service，也不承载私有业务数据。

## Capability Discovery 边界

跨项目 Capability Discovery 和共享 Document Capability 规则属于 Global Codex 层。版本化模板见 [`bootstrap/AGENTS.md`](bootstrap/AGENTS.md)，实际运行文件位于 `~/.codex/AGENTS.md`。公共 AI-Workspace 提供 [`Capability Catalog`](capabilities/README.md)；策划先识别结果契约，再由当前 Host 选择实现。

AI-Workspace 维护 Capability contract、Game Design 使用边界、Workflow 和验收证据，但不维护运行时工具目录、安装入口、endpoint、credential 或连接状态。`Document Capability` 的稳定契约见 [`capabilities/document/README.md`](capabilities/document/README.md)；Document Assistant 是当前实现 provider，其源码和配置继续以外部仓库与受控环境为准。

`Memory Capability` 的稳定契约见 [`capabilities/memory/README.md`](capabilities/memory/README.md)。版本化 reference implementation 属于本仓库治理自动化，但 Host-local mode、Outbox、hook activation 和私有 repository registry 不进入公共 Git。
