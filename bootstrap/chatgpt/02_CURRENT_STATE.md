# 02 — Current State

_Last reviewed: 2026-08-27_

本文件是便于 ChatGPT Project 新对话快速进入状态的动态摘要。执行任务前仍需读取 Git 中的最新 Task、Status、Handoff 和业务仓库。

## 已完成的重要里程碑

- AI-Workspace 已建立 Game Planner 领域边界、Workspace Kernel、Capability Model、Skill Tree、Project Template、Evidence Standard、Task 与 Handoff 机制。
- Huuuge Collector 已形成 SVN-first 策划发布流程，并具备环境检查、READY、广泛 RPC 捕获、protobuf decode、Session manifest、自动 lifecycle markers 和 Clean Finalize。
- Huuuge Knowledge Index 已按 Slots、Systems、Events、Others 整理研究模块，并采用统一 L0–L4 Evidence Standard。
- AI Document Assistant 已接入 Codex，可读写飞书云文档并自动设置企业内可编辑权限。
- Codex 跨项目 Global AGENTS 已采用 Capability-first / Reuse-first 规则。
- Codex 1+4 Subagent Pilot 已通过 Review；默认 `OFF`，可在受限权限和适合的复杂任务中手动启用。
- Git-backed Automatic Memory 已完成 TASK-0016 实施并进入 Review；production 默认 `ASSISTED`，AUTO 仅完成隔离验证，Global hook 未激活。
- “策划在新电脑上按文档和 AI 引导完成采集与文档流程”的首轮验收暂定通过，后续通过真实使用继续优化。

## 当前 Huuuge 任务

当前任务文件：

```text
AI-Workspace/tasks/TASK-0015-Huuuge-Lottery-Live-Numerical-Breakdown.md
```

实际范围已经收窄为：

- 在 Lottery 限时活动结束前启动并维护专用 Capture；
- User 亲自体验游戏，并决定所有付费、充值、礼包、票券购买和资源消耗行为；
- Codex 只负责环境检查、READY、短步骤提醒、被动采集、Clean Finalize 和证据覆盖清单；
- 本轮暂不做数值拆解、CR 方案、飞书报告或 AI Document Assistant 写入；
- User 明确说“体验完成，可以开始分析”后，再建立独立分析任务。

如果 Git 中该 Task 已更新或结束，以 Git 最新内容为准。

## 当前重要决策

### Automatic Memory

- Git 是可审计、可回滚的长期真相源；ChatGPT Project Memory / Codex memory 只作为 recall layer。
- Public-safe Candidate 可进入 AI-Workspace；Project Private、Cross-project Private、Local-only、Unknown 或 writer-unavailable 内容进入批准的私有目标或本机 Outbox，默认不公开。
- Production 当前保持 `ASSISTED`。Canonical 规则、ADR、架构、冲突、高影响和敏感内容即使在 AUTO 也必须 Review。
- ChatGPT Project Source Pack 可一键生成，但当前替换仍需人工上传。

### Collector / Analysis / Report / Document 解耦

- Collector 负责采集证据。
- Knowledge / Analysis 负责事实、模型和策划结论。
- AI Report Engine 是后续重点能力，负责从 Knowledge 与模板生成报告内容。
- AI Document Assistant 只负责文档读写和权限，不承担业务分析。

### 多实例数据隔离

- 每个模拟器实例 / 账号使用独立数据库。
- 先分析单账号行为，再通过脱敏聚合层寻找共性和分群规律。
- 不把不同账号 Raw 数据直接混合。

### 文档和部署标准

- 策划文档默认按步骤执行，不要求阅读代码。
- 优先一键安装、一键启动、一键检查、明确成功信号、失败时唯一下一步。
- 复杂技术信息留在维护文档；策划主流程只保留必要操作。

## 当前限制与风险

- ChatGPT 直接调用 AI Document Assistant 的 Secure MCP Tunnel 仍因 OpenAI Control Plane 返回 `unsupported_country_region_territory` 而不可用；Codex 本地 MCP 正常。
- ChatGPT Project Sources 是上传时的快照，不会自动跟随 Git commit 更新；重要状态变化后需要重新上传 `02_CURRENT_STATE.md`。
- Project Memory 可以引用同一项目内聊天和文件，但不保证每个新对话主动召回全部细节；项目指令和来源文件仍是稳定入口。
- 任何当前功能、任务或 commit 的判断必须查询对应 Git 仓库，不能仅依据本文件。

## 近期候选方向

- Lottery 体验完成后的独立数值分析与 CR 迁移建议 Task。
- AI Report Engine：Knowledge → Template → AI → Markdown。
- Planner-facing UX & Deployment Standard 的持续落地。
- Reuse-first Solution Discovery：本地、内部、官方、成熟开源优先，自研最后。
- 多实例独立数据库与跨账号脱敏聚合模型。
- Workspace Sync：Git → SVN / 飞书，当前仍处于设想与后续规划阶段。

<!-- MEMORY-CONTEXT:START -->
## Automatic Memory Context

- Generated: 2026-08-27T04:23:34Z
- Effective mode during refresh: `ASSISTED`
- Context Manifest: `CONTEXT_MANIFEST.yaml`
- Project Sources update: `manual upload required`
- Private repositories: not read by default; explicit registry and authorization required

### Active public control-plane tasks

- `TASK-0014-Codex-Subagent-Pilot.md` — Review
- `TASK-0015-Huuuge-Lottery-Live-Numerical-Breakdown.md` — Ready
- `TASK-0016-Automatic-Cross-Conversation-Memory-Curation.md` — Review
- `TASK-0016-EXECUTION-AUTHORIZATION.md` — Ready
- `TASK-0017-Codex-Desktop-Proxy-WebSocket-Reconnect.md` — Ready
<!-- MEMORY-CONTEXT:END -->
