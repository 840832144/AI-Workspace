# Feishu Document

规划游戏策划文档在飞书中的创建、读取、维护、权限边界和交付方法。当前仅作为 Skill 分类入口，不包含 MCP 或 API 实现。

稳定结果契约见 [`Document Capability`](../../capabilities/document/README.md)，Document Assistant 的 provider Roadmap 见 [`DocumentAssistantCapabilityRoadmap.md`](../../docs/roadmaps/DocumentAssistantCapabilityRoadmap.md)。Skill 负责 Game Design 中的可复用方法，Document Assistant 负责外部实现，两者不得与 Capability contract 混用。

Capability Discovery 由 Global Codex 的 `~/.codex/AGENTS.md` 负责，版本化模板见 [`bootstrap/AGENTS.md`](../../bootstrap/AGENTS.md)。Feishu Tool 只在 Capability 确定后作为 Implementation Binding 选择；本 Skill 不保存安装入口、endpoint、credential 或连接状态。
