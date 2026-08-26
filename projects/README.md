# Game Project Standard

`projects/` 是所有游戏策划项目的控制面索引，不保存业务实现。每个游戏项目必须从 `projects/TEMPLATE/` 建立统一结构，确保 ChatGPT、Codex 和 User 能从仓库独立恢复上下文。

## 强制结构

```text
projects/<project-slug>/
├── README.md
├── CONTEXT.md
├── MEMORY.md
├── WORKFLOW.md
├── STATUS.md
├── REPORTS/
│   └── README.md
└── ASSETS/
    └── README.md
```

### Context

定义游戏项目目标、类型与平台、目标玩家、策划范围、非目标、外部仓库/系统、Owner、依赖、安全边界和成功标准。Context 变化通常需要 User 决策或 RFC。

### Memory

保存长期有用的 Confirmed、Decision 引用、复用经验和仍待验证的 Hypothesis。不得保存聊天流水、credential、玩家明细、完整日志、私有 Registry 或业务数据副本。

### Workflow

定义策划输入、前置条件、步骤、责任角色、Skill、Template、Tool、审阅关卡、失败处理、输出和交接方式。

### Status

只描述当前状态：阶段、Owner、更新时间、当前里程碑、确认事实、证据、风险、阻塞、进行中工作和唯一明确的下一动作。

### Reports

保存或索引经过审阅的策划分析、方案、复盘和决策报告。大型文件、敏感数据或由外部系统托管的文档只记录引用。

### Assets

保存项目控制面所需的小型、非敏感参考资产或外部资产索引。游戏资源、构建产物和项目源码仍留在对应项目仓库。

## 真相源

- 游戏项目源码和测试：外部项目仓库。
- 策划数据：经授权的数据平台或项目受控存储。
- 项目协作控制面：本目录。
- 跨项目决策：RFC/ADR。
- 当前角色交接：`handoff/`。

## Registered Projects

- [`huuuge-android-research`](huuuge-android-research/README.md) — Huuuge Casino Android 游戏系统与数值研究控制面；外部仓库保留实现和证据真相源。

登记项目不会迁移外部仓库。新增项目继续从 `projects/TEMPLATE/` 创建，并先通过对应 Review gate。
