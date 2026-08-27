# Automatic Memory Solution Discovery

本文面向 TASK-0016 的实施与 ChatGPT Review，记录 2026-08-27 完成的 Reuse-first 调研、证据、选型和明确不采用项。结论仅覆盖 Game Planner AI Workspace 的 Git-backed Memory Capability，不把 AI-Workspace 扩展为通用记忆平台。

## 结论

采用 **Wrap + small Build**：复用 OpenAI/Codex 原生生命周期入口、`AGENTS.md`、结构化非交互输出和 Git；在 AI-Workspace 内实现一个无常驻服务、默认 `ASSISTED`、可关闭、可审阅的薄治理层，负责 schema、Public-safe 检查、Secret scan、去重、冲突、路由、Review Queue、Context refresh 和本机 Outbox。

不安装、Fork 或运行 Mem0、Letta Code、LangMem、Graphiti，也不新增外部 SaaS、账号、API key、向量库、图数据库或高权限 GitHub App。它们的 Candidate-first、后台整理、Git 历史、provenance、时间有效性等设计可借鉴，但不能替代本任务的跨 Host 安全路由和 Git contract。

## 需要交付的 Capability

- Outcome：把不同 Host 产生的高价值游戏策划规则、决定、事实、Solution、Skill、Workflow、状态和失败经验，转换为可审计、可路由、可 Review、可刷新上下文的长期记忆。
- Operation：`CAPTURE`、`VALIDATE`、`CURATE`、`REFRESH`、`STATUS`、`SET_MODE`。
- 等级：本地文件与 Git Candidate 为 `WRITE`；Canonical promotion 为受 policy 限制的 `WRITE`；架构、核心规则、权限和公开边界变更仍需要 Review/User gate。
- 成功证据：schema 与安全检查通过；Public / Private / Local-only 路由有隔离测试；OFF / ASSISTED / AUTO 可切换；Candidate 不静默覆盖 Canonical；Context Manifest 和 Source Pack 可刷新；失败进入 Outbox；Git diff、测试和 Handoff 可复查。

TASK-0016 是 User 已授权的新 Capability 建立任务。调研开始时公共 Catalog 只有 `CAP-DOC`，因此实施必须先新增 provider-neutral Memory contract，不能从本机可见 Tool 反推并虚构既有 Capability。

## 现有 Workspace 与本机能力

### AI-Workspace

Confirmed：仓库已有 Global/Project `AGENTS.md`、Task/Handoff、项目 `MEMORY.md`、ChatGPT 00–03 Source Pack 和 Git 协作规则；没有 Memory schema、Capture/Curator CLI、Review Queue、Context Manifest 或已启用 hook。仓库 `.git/hooks/` 只有 Git sample hooks。

可复用：

- Git 是既有协作和长期真相源；
- `bootstrap/chatgpt/` 已有 Source Pack，可由 refresh 工具生成动态部分和替换清单；
- Task、Handoff、ADR、Skill、Solution、Project Memory/Status 已有明确 canonical destination；
- TASK-0014 的 PowerShell 入口、fail-closed、备份和隔离测试风格可复用。

### Codex 本机

Confirmed：本机 `codex-cli 0.150.0-alpha.8`；`~/.codex/memories_1.sqlite` 存在 `jobs` 与 `stage1_outputs` 等本地整理表；当前 `config.toml` 没有 Memory hook；Subagent 最终模式为 `OFF`。本机有 Git、GitHub CLI、Python 3.12、Windows PowerShell 与 PowerShell 7；没有 `gitleaks` 或 `trufflehog`。PyYAML 可用，但其他 Host 不保证存在。

官方 OpenAI 文档说明：

- ChatGPT 与 Codex memory 是有帮助的 recall layer，必须执行的团队规则仍应保存在 `AGENTS.md` 或版本化文档中；本地 Codex 使用独立 local memory store。[Memories](https://learn.chatgpt.com/docs/customization/memories)
- Codex Hooks 原生支持 `Stop` 和 `SessionEnd`，官方明确列出“自动总结聊天形成持久记忆”为适用场景；`SessionEnd` 只对主线程生效、同步执行且最多 3 秒，因此适合写轻量 Outbox event，不适合在退出路径运行完整 Curator。[Hooks](https://learn.chatgpt.com/docs/hooks)
- `codex exec` 支持 JSONL 与 JSON Schema 结构化输出，并可显式限制 sandbox，适合作为可选的事件提取器；核心安全验证不能依赖模型判断。[Non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode)
- `AGENTS.md` 按 Global → Project → 当前目录分层加载，适合作为 Codex 的静默 Memory Check 和 CLI 调用契约。[AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

Decision：复用 Codex 原生 hooks 规范和本地 memory 的存在性，但不读取、导出或上传本地 memory 内容，不把它当跨 Host 真相源。本任务只提供禁用状态的 hook 模板；根据 Execution Authorization，不在本轮修改全局 `config.toml`、安装常驻 hook、重启 Codex 或影响运行会话。

### ChatGPT Project / GitHub

Confirmed：ChatGPT Projects 可使用同一 Project 的 chats/files，并可把单条 response 手动保存为 Project Source；Project memory 不是可枚举的 canonical database。标准 ChatGPT GitHub App 用于读取、搜索和分析，不能 push code/update/PR；GitHub event-triggered tasks 聚焦 PR 活动，不是每次聊天结束事件。[Projects](https://help.openai.com/en/articles/10169521), [GitHub in ChatGPT](https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt-deep-research)

Decision：ChatGPT adapter 使用 Project Instructions 的静默 Memory Check + 标准 Outbox event。只有当前会话另有已批准 Git writer 时才写 Candidate；标准 GitHub App 路径明确输出 `manual handoff required`。Project Source Pack refresh 只生成文件和替换清单，不通过浏览器自动上传。

### Trae + DeepSeek / Generic IDE Agent

Confirmed：本机 Trae 只有键位扩展，没有可复用 Memory、hook 或 Git curator 扩展；未发现团队内部已批准的跨 Host Memory 服务。

Decision：提供可复制规则、标准事件文件和跨平台 Python CLI；有 Git 权限的 Agent 写 Candidate branch，无 Git 写权限的 Agent 写本机 Outbox。核心实现不依赖 Trae 私有插件、账号或 Secret。

## 官方与开源候选比较

候选活跃度于 2026-08-27 通过 GitHub repository metadata 只读核对；stars 只作为维护活跃度旁证，不作为质量结论。

| Candidate | 可复用点 | 与 TASK-0016 的缺口 | 结论 |
| --- | --- | --- | --- |
| OpenAI Codex Hooks / AGENTS / `codex exec` | 原生生命周期、稳定规则、结构化输出、权限参数 | 只覆盖 Codex；不提供 Public/Private 路由、Git Candidate schema、Review Queue 或 Context Pack | **Adopt + Wrap** |
| ChatGPT Project Memory / Sources / GitHub App | 同 Project recall、来源文件、Git 实时只读 | memory 不可枚举；GitHub App 不写；没有通用 conversation-end writer | **Adopt as recall/read path** |
| Mem0, Apache-2.0, active | 多 Host SDK/CLI、自动提取、Codex/IDE 集成、向量检索 | 默认需要 LLM/embedding 或服务；偏个性化 memory；不是 Git canonical；Public-safe、Review/canonical routing 不匹配 | **Do not adopt/fork**；借鉴 hot/background capture |
| Letta Code / MemFS, Apache-2.0, active | Git-backed Markdown memory、commit 后生效、worktree 并发、shared memory | 是完整 agent harness，会自改 memory/skills/context；引入新 CLI、账号/模型配置或运行面；替换现有 Codex/ChatGPT 流程 | **Do not adopt/fork**；借鉴 Git history/worktree/context tree |
| LangMem, MIT, active | hot-path tool、background manager、storage-neutral primitives | 需要 LangGraph/模型，生产持久化通常另配数据库；没有 Git contract 和跨 Host adapter | **Do not adopt/fork**；借鉴两阶段 curator |
| Graphiti, Apache-2.0, active | temporal facts、provenance、supersede/history、hybrid retrieval | 需要 LLM/embedding 与 Neo4j/FalkorDB/Neptune 等图存储；运维和数据暴露面远超 Pilot | **Reject for Pilot**；保留为规模化后候选 |

Primary sources：

- [Mem0 repository](https://github.com/mem0ai/mem0)
- [Letta Code repository](https://github.com/letta-ai/letta-code) 与 [MemFS design](https://github.com/letta-ai/letta-docs-md/blob/main/concepts/memfs/index.md)
- [LangMem repository](https://github.com/langchain-ai/langmem)
- [Graphiti repository](https://github.com/getzep/graphiti)

## Adopt / Wrap / Fork / Build 决策

### Adopt

- Git commit/history/branch 作为审计、rollback 和并发边界；
- checked-in `AGENTS.md`、Task、Handoff、ADR、Skill、Solution、Status；
- Codex native `Stop`/`SessionEnd` hook contract，但只交付禁用模板；
- `codex exec --output-schema` 作为可选 Host extraction adapter；
- ChatGPT Project Sources 作为 snapshot recall layer。

### Wrap

- 用统一 Memory Event/Candidate schema 包装 ChatGPT、Codex、Generic Agent 输出；
- 用 deterministic validator 包装所有模型输出；
- 用 OS file lock + Git branch/commit policy 包装并发写入；
- 用 Context Manifest 包装 Source Pack 动态刷新。

### Fork

不 Fork。四个开源候选的核心 storage/runtime 与现有 Workspace 边界不同，Fork 会引入持续同步和安全审计成本，但不能减少本任务必须自有的治理规则。

### Small Build

实现一个 Python 3 标准库核心和 PowerShell Windows 入口，不依赖 PyYAML、数据库、向量索引、外部模型或服务。选择标准库是为了让 Generic Agent 在安装 Python 3 后即可运行，同时避免当前本机偶然存在的包成为隐式前置。

核心只负责：

- schema 与模板；
- Secret / sensitivity / scope 检查；
- deterministic dedup 与 conflict record；
- Candidate / Review / Archive / Local Outbox 路由；
- OFF / ASSISTED / AUTO；
- allowlist 内的低风险 auto-promotion；
- manifest 和 Source Pack refresh；
- 简洁计数与可机器读取 JSON。

模型负责“提出 Candidate”，不负责绕过 validator、决定公开边界或静默覆盖 Canonical。

## 实施约束

- Production 默认 `ASSISTED`；AUTO 只在隔离临时仓库测试，Pilot 后恢复 `ASSISTED`。
- `SessionEnd` hook 只写最小事件/Outbox，完整 validation/curation 由显式命令或后续批准的定时任务执行。
- 公共仓库只接收 `scope=public` 且 `sensitivity=public` 的 Candidate；其他内容只能输出目标路由或进入 Git ignored 的本机 Outbox。
- deterministic secret scan 是必经 gate；`gitleaks` 可作为未来可选加固，不作为本轮未安装依赖。
- 不遍历或上传完整聊天，不读取本机 Codex memory 正文，不读取 TASK-0015 Capture，不修改 Huuuge、Collector、SVN、Document Assistant 或飞书。
- Canonical auto-promotion 只允许纯 index/manifest/source-pack refresh，以及明确 allowlist 的完成状态/Solution；Core Rule、ADR、Capability、跨项目策略和冲突始终 Review。

## 调研完成判定

Confirmed：本报告完成了 Workspace → 本机/内部 → OpenAI/GitHub 官方 → 成熟开源 → Adopt/Wrap/Fork/Build 的顺序调研，并形成不安装新服务的实现决策。下一步按本报告实施 TASK-0016，不再先行探索会扩大权限或运行面的替代方案。
