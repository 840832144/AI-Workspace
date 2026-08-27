# ADR Index

ADR 记录已采纳、会长期影响 AI 协作体系的架构决定。

- [`ADR-0001-Game-Planner-Domain.md`](ADR-0001-Game-Planner-Domain.md) — AI-Workspace 收敛为 Game Planner AI Workspace。
- [`ADR-0002-Global-Tool-Discovery.md`](ADR-0002-Global-Tool-Discovery.md) — 历史 Tool-first 决策；已被 ADR-0003 替代。
- [`ADR-0003-Capability-First-Discovery.md`](ADR-0003-Capability-First-Discovery.md) — 先发现 Capability，再在实现层选择 provider 与 Tool。
- [`ADR-0004-Codex-Subagent-Pilot.md`](ADR-0004-Codex-Subagent-Pilot.md) — 采用默认关闭、1+4、单写入者的 Codex 子 Agent 试运行。
- [`ADR-0005-Git-Backed-Automatic-Memory.md`](ADR-0005-Git-Backed-Automatic-Memory.md) — 采用 Candidate-first、Git-backed、默认 ASSISTED 的跨 Host 自动记忆体系；等待 ChatGPT Review。
- [`ADR-0006-Task-Identity-and-Allocation.md`](ADR-0006-Task-Identity-and-Allocation.md) — 采用全局 `TASK-XXXX` + `project_key` / alias，并以可重建 Registry、latest-main gate 和 remote CAS reservation 治理分配；Accepted。
- [`ADR-0007-Workspace-Live-Context-Hub.md`](ADR-0007-Workspace-Live-Context-Hub.md) — 采用 Git canonical + Feishu Drive Context Hub + Host-local pack，默认 ON_DEMAND；等待 ChatGPT Review。

ADR 状态：Proposed、Accepted、Deprecated、Superseded。历史 ADR 不删除、不重写结论；使用新 ADR 替代。
