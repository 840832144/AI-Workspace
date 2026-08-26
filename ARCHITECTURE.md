# Architecture

AI-Workspace 的架构范围限定为游戏策划 AI 工作台。它不提供通用领域能力，也不承载业务实现。Workspace Kernel 的对象定义见 [`docs/architecture/WorkspaceKernel.md`](docs/architecture/WorkspaceKernel.md)，能力分层见 [`docs/CapabilityModel.md`](docs/CapabilityModel.md)。

## 总体模型

游戏策划 AI 协作体系分为三个平面：

```text
Governance plane — AI-Workspace
  章程 / RFC / ADR / 标准 / 模板 / 项目索引 / 交接
                         │
                         ▼
Execution plane — project repositories and connected systems
  游戏项目代码 / 测试 / 部署 / 项目专属文档 / 实际配置
                         │
                         ▼
Evidence plane — verified outputs
  测试结果 / API 响应 / 版本号 / commit / artifact reference
```

AI-Workspace 管理“如何协作”和“各项目处于什么状态”，但不复制执行平面的实现。

## 信息架构

### RFC

RFC 描述尚需讨论或跨多个组成部分的提案。RFC 可以处于 Draft、Proposed、Accepted、Rejected、Superseded。

### ADR

ADR 记录已经采纳、会长期影响体系的架构决策。ADR 只记录一个决策及其上下文、取舍和后果；后续变化通过新的 ADR supersede 旧记录。

### Standards

Standards 是已生效的横向规则，例如证据纪律、命名、安全边界和文档质量。标准应引用其来源 RFC/ADR。

### Capabilities、Skills 与 Workflows

- Capability 定义游戏策划工作台可交付的结果，不绑定具体 Agent 或工具。
- Skill 是实现 Capability 的可复用方法单元，定义触发条件、输入、步骤、安全限制、输出和验证。
- Workflow 编排一个或多个 Agent、Skill、Template、Tool、项目或外部系统，定义顺序、检查点和失败处理。

### Projects

`projects/` 只保存游戏项目控制面。每个项目必须具有 Context、Memory、Workflow、Status、Reports、Assets 六部分，业务实现仍留在项目自己的仓库。

### Handoff

`handoff/CHATGPT.md` 与 `handoff/CODEX.md` 是角色固定收件箱/发件箱。它们记录当前可执行交接，不替代项目 Status、RFC 或 ADR。

## 真相源规则

| 信息 | 真相源 |
| --- | --- |
| 业务代码、测试、构建配置 | 对应项目仓库 |
| 跨项目章程、标准、路线图 | AI-Workspace |
| 长期架构决策 | `docs/adr/` |
| 提案与讨论结果 | `docs/rfc/` |
| 当前项目协作状态 | `projects/<project>/STATUS.md` |
| 当前 Agent 交接 | `handoff/` |
| 凭据和 secrets | Secret manager / 本机受控环境；不得进入 Git |

出现冲突时，先确认信息类型，再按上表选择权威来源；不要通过复制更多文档解决冲突。

## 变更生命周期

1. Intake：记录目标、范围和明确非目标。
2. RFC：当变更跨项目、改变体系边界或需要讨论时提出。
3. Decision：采纳后，必要时创建 ADR。
4. Project control：建立或更新 Context、Memory、Workflow、Status。
5. Execution：在项目仓库实施和验证。
6. Evidence：记录 commit、测试或系统结果的引用，不复制敏感内容。
7. Handoff：更新固定交接文档，给出下一项可执行动作。
8. Change record：更新 CHANGELOG。

## 安全边界

- 本仓库默认可被多个 AI Agent 阅读，因此按“无秘密、最少数据”设计。
- 任何 credential、访问 token、私钥、个人身份数据和客户数据都不得写入。
- 外部系统变更必须受对应项目权限和用户授权约束。
- 模板不得诱导 Agent 绕过管理员策略、安全控制或项目仓库规则。
