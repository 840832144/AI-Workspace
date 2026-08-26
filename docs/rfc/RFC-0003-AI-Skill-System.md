# RFC-0003: AI Skill System

- Status: Proposed
- Date: 2026-08-26
- Actors: User, ChatGPT, Codex

## Summary

建立面向 Game Design、可登记、可审阅、可版本化和可弃用的 AI Skill 体系，使游戏策划方法不依赖单次提示词或某个 Agent 的隐式记忆。

## Problem

当前可复用方法可能散落在聊天、仓库说明和本地工具中。没有统一契约时，Agent 难以判断何时触发 Skill、需要哪些输入、会修改什么状态，以及如何验证完成。

## Proposed Skill Contract

每个 Skill 至少定义：

- Name 与稳定 ID。
- Purpose 与明确非目标。
- Trigger：何时必须或不应使用。
- Inputs：必需信息、权限和前置条件。
- Procedure：可执行步骤和检查点。
- Safety：禁止操作、敏感数据和外部副作用。
- Outputs：文件、状态或交接结果。
- Validation：成功证据和失败语义。
- Compatibility：支持的 Agent、工具、平台和版本。
- Ownership：维护者、状态和弃用替代项。

## Lifecycle

```text
Draft → Review → Active → Deprecated → Retired
                    ↘ Suspended
```

- Draft 不应用于生产关键流程。
- Active 必须通过安全和可执行性审阅。
- Deprecated 必须给出替代项和迁移期。
- Suspended 表示存在安全或正确性问题，必须停止自动触发。

## Repository Boundary

`skills/` 在本阶段只保存规范、索引和外部实现引用。具体 Skill 实现可以留在专用插件或项目仓库；是否集中托管由后续 RFC/ADR 决定。

Skill Tree 仅接受游戏分析、游戏系统/数值设计、策划分析工具和文档交付方法。非游戏领域 Skill 不进入默认 Workspace。

## Open Questions

- Skill manifest 采用 Markdown、JSON 还是二者组合？
- 如何表达 Agent/tool 兼容范围和权限需求？
- 如何对 Skill 做自动化 lint、secret scan 和回归验证？
- 哪些变更需要 major version？

## Non-goals

- 本 RFC 不创建具体可执行 Skill。
- 本 RFC 不安装或迁移现有 Skill。
- 本 RFC 不定义运行时插件协议。
