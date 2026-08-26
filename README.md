# AI-Workspace

AI-Workspace 是整个 AI 协作体系的总控仓库。它保存跨 Agent、跨项目长期有效的章程、决策、标准、工作流、模板、项目索引和交接状态，不承载业务代码。

## 仓库定位

本仓库负责回答四类问题：

1. 为什么做：章程、RFC、路线图和范围边界。
2. 如何协作：团队角色、标准、工作流和贡献规范。
3. 正在做什么：项目 Context、Memory、Workflow、Status。
4. 如何交接：ChatGPT 与 Codex 的固定交接文档。

业务实现、运行时数据、凭据和项目私有产物必须留在各自仓库或受控系统中。AI-Workspace 只记录它们的关系、经过验证的事实和可复用方法。

## 目录

```text
AI-Workspace/
├── docs/
│   ├── rfc/          # 提案、章程和跨体系设计
│   └── adr/          # 已采纳的架构决策记录
├── skills/           # 可复用 AI Skill 的规范与索引
├── workflows/        # 跨 Agent、跨项目工作流
├── templates/        # RFC、ADR、项目和交接模板
├── standards/        # 命名、证据、安全和文档标准
├── projects/         # 项目控制面；不复制业务仓库
├── handoff/          # ChatGPT / Codex 固定交接入口
└── bootstrap/        # 新环境、新 Agent 的接入清单
```

## 阅读顺序

新 Agent 或新会话按以下顺序开始：

1. `AI_TEAM.md`
2. `ARCHITECTURE.md`
3. `CONTRIBUTING.md`
4. `projects/README.md`
5. 自己对应的 `handoff/CHATGPT.md` 或 `handoff/CODEX.md`
6. 相关 RFC、ADR 和项目 Status

## 基本原则

- Git 是协作记录的最终来源。
- 已确认事实与假设必须分开记录。
- 项目代码仓库是实现真相源；AI-Workspace 是协作和治理真相源。
- 不在本仓库保存密钥、token、个人数据、完整运行日志或业务数据。
- 跨项目变更先写 RFC；不可逆或长期架构选择再写 ADR。
- 每次有意义的工作都必须留下可由下一个 Agent 独立继续的记录。

当前阶段只完成控制面初始化，不迁移现有项目，也不实现业务代码。
