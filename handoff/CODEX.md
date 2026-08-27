# Codex Handoff

这是 Codex 的固定交接入口。实现细节以 Git 中的 Capability、Governance、ADR、工具、测试和 Pilot 记录为准。

- Updated: 2026-08-27
- Task: TASK-0016
- Current state: implementation complete; waiting ChatGPT Review
- Final Memory Mode: `ASSISTED`
- Production activation: disabled
- Subagents: none

## Outcome

TASK-0016 已按 Reuse-first 顺序完成调研、实现、隔离 Pilot、回归、Context refresh 与 Git 提交。系统以 Git 为长期真相源，在内容产生端捕获结构化 Memory Event/Candidate，并在写入前执行 schema、Secret、作用域、敏感性、去重、冲突与目标检查。

Implementation commit: `ea4b758`。此前过程提交：`c243fd9`（In Progress gate）和 `5620c10`（Reuse-first discovery）。

## Reuse-first Decision

- **Adopt / Wrap**：采用 ChatGPT/Codex 原生 memory 作为 recall layer，采用 Codex `SessionEnd`/`Stop` hooks 作为可选 lifecycle binding，采用 Git 作为审计、Review、rollback 和跨 Host 共享层。
- **Learn, do not install**：研究了 Mem0、Letta/MemFS、LangMem 和 Graphiti；其分层、候选、文件化或图谱思路有参考价值，但当前任务不需要外部服务、数据库、账号或高权限 App。
- **Build small**：用 Python 标准库实现确定性的 schema、route、scan、dedup、lock、curate 和 refresh；Windows 仅提供薄 PowerShell 入口。
- 详细证据与 Adopt/Wrap/Fork/Build 对比见 `docs/research/MEMORY_SOLUTION_DISCOVERY.md`。

## Delivered

- `capabilities/memory/README.md`：CAP-MEM contract 与 CAPTURE/VALIDATE/CURATE/REFRESH/STATUS/SET_MODE operations。
- `standards/MEMORY_GOVERNANCE.md` 与 `docs/adr/ADR-0005-Git-Backed-Automatic-Memory.md`。
- `templates/memory/`、`memory/`、`solutions/` 和确定性 index/fingerprint contract。
- `tools/memory/memory_cli.py` 及 Capture/Validate/Curate/Refresh/Status/Mode PowerShell 入口。
- ChatGPT Project、Codex、Generic IDE Agent adapters；Codex hook 只提供 disabled reference，未安装。
- `CONTEXT_MANIFEST.yaml`、生成的 Project Source Pack 与 replacement list。

## Host Integration Status

| Host | Status | Write behavior |
| --- | --- | --- |
| ChatGPT Project | Rules and Source Pack ready | 有批准 Git writer 时写 Candidate；只有只读 GitHub App 时输出标准 Outbox event；Source 更新需人工上传 |
| Codex | Adapter and CLI ready | 默认 Git writer/curator；Task/Review/Handoff 后执行 Memory Check；不依赖 Subagent |
| Generic IDE / Trae + DeepSeek | Copyable rule and CLI ready | 有 Git 权限时走安全 Candidate；无权限或私有内容走 Host-local Outbox |
| Human / other agent | File drop/template ready | provenance 必填；事实未经验证不自动晋升 |

## Routing and Pilot Evidence

| Scenario | Route | Result |
| --- | --- | --- |
| ChatGPT explicit decision | Public / ASSISTED | captured 1, review 1 |
| Codex completed solution | Public / isolated AUTO | captured 1, promoted 1, archived 1 |
| Generic private procedure | Project Private | public write 0, local Outbox 1 |
| Read-only writer | Public but unavailable | public write 0, local Outbox 1 |
| Secret event | Local-only | literal redacted, public write 0, local Outbox 1 |
| OFF kill switch | All automatic capture | suppressed 1 |

Pilot totals：captured 2、promoted 1、review 1、local-only/Outbox 3、suppressed 1、conflicts 0、failed 0。False captures 和 missed captures 未测量，因为需要 User Review 与真实 Host 观察；没有从 synthetic scenarios 推断 accuracy。

## Validation

- `python -m unittest discover -s tools/memory/tests -v`：17/17 passed。
- Windows PowerShell memory entry scripts：parse passed；named-parameter capture wrapper 有真实回归。
- Isolation Pilot：passed，最终恢复 `ASSISTED`。
- AI-Workspace refresh：41 public control-plane sources、0 Secret issue、0 broken link、private repositories not read。
- Dirty repository 请求 sync 时 fail-closed，不声称 latest；默认 refresh 不读取未登记私有仓库。
- 最终回归发现并修复 omitted `ValueFromRemainingArguments` 产生空参数的问题；薄 wrapper 现在显式构造参数数组，Status/Mode/Curate/Refresh 已加入回归。

## Context Refresh

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\memory\Refresh-ProjectContext.ps1
```

输出 `CONTEXT_MANIFEST.yaml`、更新 `bootstrap/chatgpt/02_CURRENT_STATE.md`、生成 `bootstrap/chatgpt/generated/PROJECT_SOURCE_PACK.md` 和 `PROJECT_SOURCE_REPLACEMENT_LIST.md`。当前 `manual upload required=true`；没有用浏览器自动化伪装成可靠 Source 替换。

## Safety and Non-activation

- Final mode 为 repository-default `ASSISTED`；没有 Host-local production override。
- 没有安装 Global hook、修改 `~/.codex/config.toml`、替换本机 Global AGENTS、重启 Codex 或启用 production AUTO。
- 没有访问或修改 Huuuge 仓库、运行中的 Collector、当前 Capture、SVN、飞书文档、Document Assistant 或私有 Registry。
- AUTO 仅允许在隔离环境晋升目标不存在、Public-safe、高分、高置信、有证据的 `solution`；existing targets、规则、ADR、架构、冲突、高影响和敏感内容都进入 Review。

## Known Limits and Next-task Candidates

- ChatGPT Project Sources 当前需要人工替换；是否开发批准的写入 Provider 由 User 决定。
- Generic IDE adapter 已验证 contract/CLI/Outbox，没有真实 Trae lifecycle hook。
- 真实 false-positive/missed-capture、跨对话召回和人工成本需要 production ASSISTED 观察后测量。
- Semantic dedup、graph retrieval、跨项目私有 Context Hub、scheduled curator 和 hook activation 都是独立后续 Task 候选，不在本轮扩展。
- TASK-0017 是独立的 Codex Desktop proxy/WebSocket 任务，本轮未执行。






<!-- MEMORY-REFRESH:START -->
## Memory Context Refresh

- Generated: 2026-08-27T04:23:34Z
- Effective mode: `ASSISTED`
- Manifest: `CONTEXT_MANIFEST.yaml`
- ChatGPT Project Sources: `manual upload required`
- Private repositories: not read unless explicitly registered and authorized
<!-- MEMORY-REFRESH:END -->
## Exact Next Action

ChatGPT Review TASK-0016 的 Capability/governance、Public/Private/Local-only routing、AUTO allowlist、Pilot evidence、Context Pack 和边界，并给出 `Accepted` 或 `Needs changes`。Review 前不激活 hook、不切 production AUTO、不新增外部 provider。
