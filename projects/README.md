# Projects

`projects/` 是所有 AI 协作项目的控制面索引，不保存业务实现。

## 强制结构

每个项目必须建立稳定目录 `projects/<project-slug>/`，并包含：

```text
projects/<project-slug>/
├── CONTEXT.md
├── MEMORY.md
├── WORKFLOW.md
└── STATUS.md
```

### Context

定义项目目标、范围、非目标、外部仓库或系统、Owner、依赖、安全边界和成功标准。Context 变化通常需要 User 决策或 RFC。

### Memory

保存长期有用的 Confirmed Facts、Decision 引用、复用经验和仍待验证的 Hypothesis。不得保存聊天流水、credential、完整日志、私有 Registry 或业务数据副本。

### Workflow

定义输入、前置条件、执行步骤、责任角色、验证关卡、失败/回滚处理、输出和交接方式。

### Status

只描述当前状态：阶段、Owner、更新时间、当前里程碑、确认事实、证据、阻塞、进行中工作和唯一明确的下一动作。

## 真相源

- 项目源码和测试：外部项目仓库。
- 项目协作控制面：本目录。
- 跨项目决策：RFC/ADR。
- 当前角色交接：`handoff/`。

从 `templates/projects/` 复制四件套创建项目。初始化阶段不登记或迁移现有项目。
