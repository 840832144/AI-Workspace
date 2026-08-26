# Feishu Document

规划游戏策划文档在飞书中的创建、读取、维护、权限边界和交付方法。当前仅作为 Skill 分类入口，不包含 MCP 或 API 实现。

Document Assistant 的公司文档中台能力规划见 [`DocumentAssistantCapabilityRoadmap.md`](../../docs/roadmaps/DocumentAssistantCapabilityRoadmap.md)。Skill 负责 Game Design 中的可复用方法，Document Assistant 负责外部文档 Capability/Tool Service，两者不得混用。

运行时 Tool Discovery 与共享入口由 Global Codex 的 `~/.codex/AGENTS.md` 负责，版本化模板见 [`bootstrap/AGENTS.md`](../../bootstrap/AGENTS.md)。本 Skill 不保存安装入口、endpoint、credential 或连接状态。
