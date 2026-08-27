# ADR-0005: Git-Backed Automatic Memory

- Status: Proposed / Waiting for ChatGPT Review
- Date: 2026-08-27
- Decision owners: User / ChatGPT
- Executor: Codex
- Related task: [`TASK-0016`](../../tasks/TASK-0016-Automatic-Cross-Conversation-Memory-Curation.md)
- Research: [`MEMORY_SOLUTION_DISCOVERY`](../research/MEMORY_SOLUTION_DISCOVERY.md)
- Supersedes: None

## Context

ChatGPT Project Memory、Codex local memories 和各 Agent 的会话上下文可以改善 recall，但不是共同可枚举、可审计、可保证完整的真相源。不同 Host 的写能力、安全边界和 lifecycle 也不同。Workspace 需要自动优先、人工兜底的长期记忆流程，同时禁止完整聊天和私有业务数据进入公共仓库。

## Decision

1. Git 和对应业务仓库是长期 canonical source；Host memory 只作为 recall/capture source。
2. 采用 Candidate-first 两阶段流程：source-side capture → deterministic validation/router → Curator promotion/review/archive。
3. 采用 Public / Project Private / Cross-project Private / Local-only 四级路由；不明确时 fail closed。
4. 生产默认 `ASSISTED`。实现并隔离测试 `AUTO`，但不自动把生产默认切为 AUTO。
5. Core Rule、ADR、Capability、跨项目策略、权限、费用和冲突在 AUTO 中仍需 Review。
6. 复用 Codex Hooks、`AGENTS.md`、`codex exec` structured output、Git branch/worktree 与现有 ChatGPT Source Pack；不安装常驻服务。
7. reference implementation 使用 Python 标准库 + PowerShell 入口，不依赖模型、数据库、向量检索或外部 SaaS。
8. Context refresh 生成 Manifest、managed current-state block、Source Pack 和手动替换清单；不以浏览器自动化冒充可靠上传 API。

## Alternatives

- Mem0：成熟且跨 Host，但默认引入模型/embedding/service，storage 和 routing contract 不匹配。
- Letta MemFS：Git-backed 特征强，但属于完整 agent harness，会改变现有 Host、context 和运行面。
- LangMem：适合 LangGraph hot/background memory，但需要额外 runtime/store。
- Graphiti：provenance 和 temporal facts 很强，但图数据库与模型运维超出 Pilot。
- 只用 ChatGPT/Codex native memory：部署最少，但不能提供跨 Host Git 审计、路由、Review 和 Context refresh。

## Consequences

### Positive

- 所有自动写入可审阅、可关闭、可通过 Git 回滚。
- 不需要新账号、Secret、常驻服务或高权限 GitHub App。
- 不同 Host 使用同一 Candidate contract，写能力不足时不会丢失或假装提交。
- Public/private boundary 由 deterministic gate 执行，不依赖模型自信。

### Costs and Risks

- Agent 仍需在 source-side 生成高质量摘要；deterministic validator 不能判断所有语义风险。
- 无官方 conversation-end writer 的 Host 只能通过 instructions/Outbox handoff，自动化程度较低。
- 没有语义检索；规模增长后可能需要单独 RFC 评估索引或 graph provider。
- Hook 安装和 Global runtime 替换会影响其他会话，本 Pilot 只交付禁用模板。

## Review Gate

ChatGPT 必须审阅 Capability contract、governance、Public/private routing、AUTO allowlist、Pilot evidence 与未解决限制。Review 前不激活全局 hook、不切 production AUTO、不新增外部 provider。
