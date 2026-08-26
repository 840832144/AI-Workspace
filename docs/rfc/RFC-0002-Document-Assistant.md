# RFC-0002: Document Assistant

- Status: Proposed
- Date: 2026-08-26
- Actors: User, ChatGPT, Codex

## Summary

定义 Document Assistant 在 AI 协作体系中的位置：它保持现有名称，规划为外部项目提供的公司文档中台，不把实现迁入 AI-Workspace。

## Context

AI Team 需要创建、读取、更新、授权、发布和治理协作文档。相关能力可能由 MCP Server、平台 Connector 或其他受控接口提供。AI-Workspace 只定义 Game Design 使用场景下的能力契约、治理边界和项目关系；Document Assistant 作为共享公司基础设施可以服务其他使用方，但其非游戏业务内容不进入本 Workspace。

## Current Planning Decision

- 名称保持 `Document Assistant`，暂不改名。
- 定位为公司文档中台，而不是单一 Feishu tool 或单一 Agent helper。
- 本阶段只输出 Capability Roadmap，不修改任何实现。
- Roadmap 状态为 Waiting for ChatGPT Review。

详细路线见 [`DocumentAssistantCapabilityRoadmap.md`](../roadmaps/DocumentAssistantCapabilityRoadmap.md)。

## Proposed Capability Boundary

Document Assistant 应提供：

- 文档健康检查、读取、搜索和目录浏览。
- 文档创建、追加、替换和目录管理。
- 明确区分 READ 与 WRITE 操作。
- 在组织策略允许时管理文档协作者和分享权限。
- STDIO、Remote MCP 或其他 transport 复用同一业务服务层。
- 文档 Registry、Revision、发布、冲突和部分成功治理。
- 多客户端认证、最小权限、审计证据和运行健康能力。

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

- 本 RFC 不修改 `Document Assistant` 名称。
- 本 RFC 不迁移或修改现有 Document Assistant 仓库。
- 本 RFC 不选择具体 hosting、认证供应商或发布节奏。
- 本 RFC 不实现 MCP 工具。
