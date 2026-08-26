# RFC-0002: Document Assistant

- Status: Proposed
- Date: 2026-08-26
- Actors: User, ChatGPT, Codex

## Summary

定义 Document Assistant 在 AI 协作体系中的位置：它是外部项目提供的文档读写能力，不把实现迁入 AI-Workspace。

## Context

AI Team 需要创建、读取、更新和授权协作文档。相关能力可能由 MCP Server、平台 Connector 或其他受控接口提供。AI-Workspace 只需要定义能力契约、治理边界和项目关系。

## Proposed Capability Boundary

Document Assistant 应提供：

- 文档健康检查、读取、搜索和目录浏览。
- 文档创建、追加、替换和目录管理。
- 明确区分 READ 与 WRITE 操作。
- 在组织策略允许时管理文档协作者和分享权限。
- STDIO、Remote MCP 或其他 transport 复用同一业务服务层。

## Control-plane Record

若该项目登记到 `projects/`，只记录：

- Context：目标、外部源码仓库、能力和安全边界。
- Memory：已确认协议、工具分类和关键决策引用。
- Workflow：发布、验证、权限失败和交接流程。
- Status：当前版本、验证证据、阻塞和下一步。

不得复制 Document Assistant 的源码、credential、私有 Registry 或文档正文。

## Security Requirements

- credential 只存在于受控运行环境。
- 权限 API 不得绕过企业管理员策略。
- WRITE 工具必须显式标注并由客户端能力/用户授权约束。
- 部分成功必须可辨识，避免因重试创建重复文档。

## Open Questions

- 项目在 AI-Workspace 中采用正式登记还是仅建立外部引用？
- READ/WRITE policy 是否需要成为全局 Standard？
- Remote MCP 的运行状态应由项目仓库还是集中监控系统记录？

## Non-goals

- 本 RFC 不迁移或修改现有 Document Assistant 仓库。
- 本 RFC 不选择具体 hosting、认证供应商或发布节奏。
- 本 RFC 不实现 MCP 工具。
