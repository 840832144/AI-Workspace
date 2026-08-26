# ChatGPT Handoff

这是 ChatGPT 的固定交接入口。ChatGPT 开始工作前读取，向 Codex 或 User 交付后更新。长期事实必须同步到项目 Memory/Status 或 RFC/ADR，而不是只留在这里。

- Updated: 2026-08-26
- Current state: Workspace initialized

## Incoming Request

当前无待处理交接。

## Confirmed Context

- AI-Workspace 是治理与协作总控仓库，不承载业务代码。
- 项目必须采用 Context、Memory、Workflow、Status 四件套。
- 本阶段未迁移任何现有项目。

## Evidence / References

- `docs/rfc/RFC-0001-AI-Workspace-Charter.md`
- `ARCHITECTURE.md`
- `projects/README.md`

## Constraints

- 不复制项目源码、credential、私有数据或完整日志。
- 不把推断写成 Confirmed。

## Exact Next Action

等待 User 选择第一个需要登记到 `projects/` 的项目，或审阅 RFC-0002/RFC-0003。

## Outgoing Handoff

当前无待确认的 outgoing handoff。
