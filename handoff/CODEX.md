# Codex Handoff

这是 Codex 的固定交接入口。实现细节以对应外部项目仓库为准。

- Updated: 2026-08-26
- Task: TASK-0007
- Current state: Document Assistant Capability Roadmap waiting for ChatGPT Review

## Objective

保持 `Document Assistant` 名称和现有实现不变，将其规划为公司文档中台，只输出 Capability Roadmap，不开发功能。

## Completed

- 新增 `docs/roadmaps/DocumentAssistantCapabilityRoadmap.md`。
- 定义 Access、Content、Collaboration、Delivery、Governance & Operations 五类共 15 个 Capability。
- 定义 Review/Baseline、Governance Contract、Core Platform、Secure Multi-client、Publication/Sync、Operations 六个演进关卡。
- 更新 Capability Model、Workspace Kernel、RFC-0002、Workspace Roadmap、Architecture、README、Feishu Document Skill 引用和 CHANGELOG。

## Confirmed Context

- 名称保持 `Document Assistant`，暂不改名。
- 外部 Document Assistant / `feishu-doc-mcp` 仓库继续作为实现真相源；本次没有读取、迁移或修改其实现。
- 现有 Feishu client、auth、registry、Markdown converter、MCP tools 和 STDIO 接入保持现状。
- Capability Roadmap 中的 Planned/Future 项目不代表已实现。
- Document Assistant 是共享公司基础设施；AI-Workspace 只治理它在 Game Design 中的使用边界。

## Risks / Open Decisions

- RFC-0002 仍是 Proposed，尚未获得 ChatGPT Review。
- READ / WRITE 是否需要增加 ADMIN-SECURITY 第三层仍待决定。
- Document Registry、Revision、Publication 的真相源和冲突规则尚未确定。
- Remote MCP、permission automation、Git → Feishu sync、monitoring 都只是规划，不得开始实现。

## Constraints

- 不修改 Document Assistant 名称、源码、MCP 配置或 ChatGPT 设置。
- 不调用 Feishu API，不写入 credential、token、Registry 或文档正文。
- 不在 ChatGPT Review 前授权 Codex 开发。

## Exact Next Action

ChatGPT 审阅 `docs/roadmaps/DocumentAssistantCapabilityRoadmap.md` 和 RFC-0002，返回 Accepted 或具体修订意见，并指出哪些阶段需要 ADR；Codex 等待 Review，不开始实现。
