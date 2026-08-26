# TASK-0014 — Codex Subagent Pilot with Kill Switch

- Status: Review
- Owner: ChatGPT
- Executor: Codex
- Priority: P1
- Date: 2026-08-26

## Goal

为 Codex 建立一套**可关闭、默认保守、单写入者**的子 Agent 试运行方案。复杂任务可以把独立的只读工作并行分配给轻量 Agent；简单任务继续使用单 Agent。User 必须能一键关闭多 Agent，且关闭后现有 Codex、MCP、项目配置和工作流不受影响。

## Confirmed Basis

当前 Codex 原生支持 Subagents 和自定义 Agent。全局硬开关是 `agents.enabled`；并发上限是 `agents.max_concurrent_threads_per_session`。自定义 Agent 位于 `~/.codex/agents/` 或项目 `.codex/agents/`，可分别设置模型、推理强度和沙箱。

官方资料：

- https://developers.openai.com/codex/subagents/
- https://developers.openai.com/codex/config-reference/
- https://developers.openai.com/codex/config-advanced/

## Scope

第一阶段采用 **1 个主 Agent + 4 个只读子 Agent**：

1. `repo_explorer`：定位仓库结构、真实调用链、相关文件和符号。
2. `knowledge_retriever`：读取项目文档、Memory、RFC、飞书文档和外部资料，返回有来源的摘要。
3. `evidence_test_verifier`：核对 Evidence Standard、验收条件、测试覆盖和可复现证据。
4. `reviewer`：独立审查正确性、安全、回归、范围漂移和遗漏。

主 Agent继续负责：任务拆解、复杂判断、代码修改、最终测试、整合、Git Commit 和 Handoff。

## Operating Modes

必须实现两个明确模式：

### OFF

- `agents.enabled = false`
- Codex 不可调用 Subagent 工具。
- 所有任务自动回退为单 Agent，不得因此阻塞。

### MANUAL

- `agents.enabled = true`
- `agents.max_concurrent_threads_per_session = 4`
- 仅在 User 明确要求、Task 明确允许，或存在至少两个真正独立的只读工作流时才可启动。
- 简单任务、单文件修改、短文档更新和明确命令不得自动启动子 Agent。

本阶段**不实现 AUTO 模式**，不允许 Codex 对所有任务主动并行。

安装与试验结束后，本机默认恢复为 `OFF`；由 User 决定何时切换到 `MANUAL`。

## Deliverables

### 1. Versioned Agent Templates

在 AI-Workspace 建立：

```text
bootstrap/codex/agents/
├── repo-explorer.toml
├── knowledge-retriever.toml
├── evidence-test-verifier.toml
└── reviewer.toml
```

每个 Agent 必须定义：

- `name`
- `description`
- `developer_instructions`
- `model`
- `model_reasoning_effort`
- `sandbox_mode = "read-only"`

推荐模型策略：

- `repo_explorer`、`knowledge_retriever`：优先 `gpt-5.6-luna`，`medium`。
- `evidence_test_verifier`、`reviewer`：优先 `gpt-5.6-terra`，`high`。

Codex 必须先检查当前账号与客户端实际可用模型。如果推荐模型不可用，选择当前可用的更低成本合理替代，并在 Handoff 记录实际值；不得因模型名不可用而阻塞整个任务。

### 2. Installation and Toggle Scripts

建立兼容 Windows PowerShell 5.1 的脚本：

```text
bootstrap/codex/Install-CodexSubagents.ps1
bootstrap/codex/Set-CodexSubagentMode.ps1
bootstrap/codex/Get-CodexSubagentStatus.ps1
```

要求：

- 安装脚本把版本化 Agent 模板同步到 `%USERPROFILE%\.codex\agents\`。
- `Set-CodexSubagentMode.ps1 -Mode Off` 关闭多 Agent。
- `Set-CodexSubagentMode.ps1 -Mode Manual` 启用保守试运行并设置并发上限 4。
- 状态脚本只输出：当前模式、并发上限、已安装 Agent 名称、配置来源和是否需要重启/新会话；不得输出 token、MCP Secret 或其他凭据。
- 所有脚本必须幂等，可重复执行。
- 修改 `~/.codex/config.toml` 前自动建立时间戳备份。
- 只修改 `[agents]` 相关键，保留现有模型、MCP、权限、通知和其他配置。
- 不使用会破坏既有 TOML 的简单整文件覆盖；若客户端提供官方安全配置命令则优先使用，否则实现可验证的最小补丁。
- 切换后明确说明是否需要关闭并重开 Codex 或新建会话。

### 3. Global Policy

更新 `bootstrap/AGENTS.md`，并在本机同步到 `~/.codex/AGENTS.md`。保留 Capability-first Discovery 作为第一入口，再增加 Subagent Policy：

- 默认单 Agent。
- 只有独立、可并行、读多写少的工作才考虑 Subagents。
- 同一工作区始终只有主 Agent 可以修改代码、文档和 Git；四个子 Agent 全部只读。
- 子 Agent 不得调用 Document Capability 的 WRITE 或 ADMIN/SECURITY Operation，不得修改飞书、权限、配置或外部系统。
- 主 Agent必须等待相关子 Agent 完成，核对冲突，再做最终判断。
- 子 Agent只返回简洁结论、证据位置、风险和未确认项，不回传大段日志。
- 如果 Multi-agent 为 OFF、Agent 不可用或委派失败，主 Agent继续单 Agent执行并报告降级，不得重新实现一套调度器。
- 最终 Handoff 记录本次实际使用了哪些 Agent；未使用时也明确写 `Subagents: none`。

### 4. Documentation and Decision Record

新增：

```text
docs/adr/ADR-0004-Codex-Subagent-Pilot.md
docs/experiments/CODEX_SUBAGENT_PILOT.md
bootstrap/codex/README.md
```

ADR 记录：为什么采用保守 1+4、为什么默认 OFF、为什么单写入者、为什么不立即扩到 1+8。

Pilot 文档记录实际试验，不虚构额度数字。若客户端提供可见 token/usage 信息，记录前后对比；若没有，只记录 Agent 数、模型、时长、是否产生返工、主观额度变化和 User 后续决定。

## Validation Scenarios

必须至少验证：

1. **OFF 模式**：新会话无法启动 Subagents，普通任务仍能完成。
2. **MANUAL 模式**：明确要求后可启动指定 Agent，并由主线程汇总。
3. **简单任务**：MANUAL 下执行一个短文档修改，确认不启动 Subagent。
4. **复杂只读任务**：并行启动 2–3 个 Agent 做仓库探索、资料读取和 Review，等待全部结束后汇总。
5. **复杂实现任务演练**：子 Agent只做前置探索/验证，主 Agent单独修改一个安全的测试夹具或文档；确认没有并行写冲突。
6. **切换回 OFF**：关闭后新会话恢复单 Agent，Agent 模板保留但不生效。
7. **配置完整性**：切换前后现有 MCP、Global AGENTS、其他 Codex 配置和 Secret 引用保持不变。

试验不得修改 Huuuge Collector、Document Assistant、SVN 发布包、飞书云文档或其他业务仓库。

## Non-goals

本任务不做：

- 1+8 全量 Agent Team。
- AUTO/主动委派模式。
- 多 Agent 并行写代码。
- Git worktree 自动编排。
- 额度计费系统或自建 Agent 调度器。
- 修改 Document Assistant、MCP Server、Secure Tunnel 或 ChatGPT 设置。
- 给 Trae、DeepSeek 或其他 Host 配置同类 Agent；后续另立 Task。

## Acceptance Criteria

- User 可用一个命令切换 `OFF` / `MANUAL`，另一个命令查看状态。
- 安装后默认 `OFF`，不会意外增加额度消耗。
- 四个 Agent 均能被 Codex 识别，全部只读。
- MANUAL 模式最多同时开放 4 个子线程。
- Global Policy 明确“简单任务不启用、主 Agent唯一写入、失败自动降级”。
- 现有 Codex 配置、MCP 和凭据未被覆盖或写入 Git。
- Pilot 场景全部有可复查结果。
- 更新 `CHANGELOG.md`、`AI_TEAM.md`、ADR Index、`handoff/CODEX.md` 和本 Task 状态。
- 提交并推送，等待 ChatGPT Review。

## Handoff Required

Codex 完成后必须返回：

- Git commit
- 当前最终模式（应为 OFF）
- 四个 Agent 的实际模型与推理强度
- 开关与状态命令
- 六类 Validation 结果
- 是否能观察到 usage/token；若不能必须明确说明
- 发现的优化项，单独列入下一个 Task 候选，不擅自实施
