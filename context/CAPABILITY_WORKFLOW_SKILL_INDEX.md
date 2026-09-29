# Capability / Workflow / Skill 索引

## CR 阅读入口

- [项目入口](../projects/cr/README.md)与[项目工作流](../projects/cr/WORKFLOW.md)。
- [根 Skill 路由](../.agents/skills/cr-project/SKILL.md)：正文唯一保存在 CR 项目内。
- [上下文摘要](../projects/cr/CONTEXT.md)：生成器只选入口，不递归收录 CR 工作簿或正文。
- [迁移报告](../docs/migrations/CR-MIGRATION-20260916.md)：公开范围、来源、路径、切换与回滚。

此处登记阅读路径，不新增 Capability 名称、不增加 Context Hub 自动发布项或外部分享权限。

## Capability

- `CAP-DOC`：发现、读取、创建、维护、发布和授权公司文档。
- `CAP-MEM`：捕获、验证、路由、整理和刷新跨对话长期记忆。
- `CAP-CONTEXT`：同步、诊断、发布、捕获协作草稿和解决 Context 冲突。

## Workflow

- `workflows/memory-curation/`：Candidate-first Memory 整理。
- `workflows/workspace-sync/`：Git、飞书协作层与 local pack 的 authority-safe 同步。

## Skill

Skill 分类与状态以 `skills/README.md` 为准。只有存在可执行入口、测试和证据的 Skill 才能称为已实现；目录或名称存在不等于 Available。

## 使用顺序

先确定 User Outcome 和 Capability，再选择 Workflow、Skill、Provider 与 Tool。当前 Host 没有实现时报告 `Implementation unavailable`，不从工具名称反推或虚构能力。
