# 01 — System Context

## 总体架构

```text
AI-Workspace（治理、Task、规则、Memory、Handoff）
        │
        ├── huuuge-android-research（采集器、研究实现、证据）
        ├── AI Document Assistant（公司文档读写 Provider）
        ├── CR 等业务项目仓库（各自实现真相源）
        └── 公司 SVN（正式包和公司资源分发）
```

跨 Host Context 使用独立的 provider-neutral 能力：

```text
Git canonical truth
→ Workspace Sync / fingerprint / revision / conflict gate
→ 飞书 Drive Context Hub（协作与展示）
→ Host-local Context Pack（ChatGPT/Codex/Generic fallback）
```

当前 provider binding 是飞书 Drive + Docx，不是 Wiki。稳定 context ID 和 authority contract 位于 `LIVE_CONTEXT_MANIFEST.json` 与 `capabilities/context/`；folder/document ID 只留 Host-local Registry。

核心能力保持解耦：

```text
Collector → Raw / Decoded Evidence
Knowledge / Analysis → 结构化事实、模型和结论
AI Report Engine（规划中）→ 根据知识与模板生成报告内容
AI Document Assistant → 读取、创建、追加、替换和授权云文档
```

Collector 和报告生成是两个独立功能。AI Document Assistant 只负责文档结果，不负责推导游戏业务结论。

## 主要仓库

### AI-Workspace

- GitHub：`840832144/AI-Workspace`
- 定位：Game Planner AI Workspace 的治理与任务真相源。
- 保存：Capability Catalog、Workflow、Skill、标准、Project Control Plane、Task、ADR、Handoff、Bootstrap。
- 不保存：业务代码、运行时 endpoint、Secret、原始采集数据、私有 Registry。

### huuuge-android-research

- GitHub：`840832144/huuuge-android-research`
- 定位：Huuuge Android 采集器、协议恢复、运行时证据、模块目录和研究实现真相源。
- 策划正式包：公司 SVN `trunk/HuuugeCollector`。
- 日常入口：`HUUUGE_BOOTSTRAP.cmd`、`HUUUGE_COLLECTOR.cmd`。
- Collector 采用被动广泛采集，正常游戏行为由 User 执行；不修改请求、奖励、余额或服务器状态。

### AI Document Assistant

- 实现仓库：`840832144/document-assistant`
- 非敏感运行手册镜像：`840832144/larkdoc_bot`
- Codex MCP 名称：`feishu-docs`
- 产品名：AI Document Assistant
- 当前能力：健康检查、文档读取、目录浏览、搜索、创建、追加、替换、创建目录、企业内只读/可编辑、群和用户授权。
- 创建文档默认企业内获得链接的人可编辑，除非 User 明确要求其他权限。
- Codex 已可使用该能力；新的 Codex 项目通过 Global `~/.codex/AGENTS.md` 进行 Capability-first 发现。
- ChatGPT 直接通过 Secure MCP Tunnel 连接仍受 OpenAI Control Plane 的地区限制阻塞，因此当前 ChatGPT 通常负责设计与内容，Codex 执行最终飞书读写。

## Capability-first

AI 先识别需要的稳定结果，再选择 Provider 和 Tool：

```text
User Outcome
→ Capability
→ Operation / 安全等级
→ Workflow / Skill
→ Implementation Binding
→ Tool
→ 按 Capability contract 验收
```

例如：

```text
读取策划飞书文档
→ Document Capability / READ
→ AI Document Assistant
→ feishu-docs MCP
→ get_document
```

Tool 不可见不等于 Capability 不存在；Capability 已登记但当前 Host 没有实现时，应报告 `Implementation unavailable`，不能直接说“不会”。

## Huuuge 研究结构

Huuuge Knowledge 按四层组织：

1. Slots
2. Systems
3. Events
4. Others

统一 Evidence Level：

- L0：Unknown
- L1：Schema-only
- L2：Static Config
- L3：Runtime Capture / Live evidence
- L4：充分验证，可支持稳定结论

Lottery、Slots、Rewards、LiveOps 等模块已有结构目录；具体成熟度和最新证据必须读取最新 Knowledge Index、模块 dossier、项目 Status 和真实 Capture。

## 多实例 / 多账号数据策略

一个模拟器实例对应一个账号时，每个实例建立独立数据库，先做单账号分析，再通过脱敏聚合层寻找共同规律。

每条记录至少保留：

```text
instance_id
account_alias
session_id
game_version
schema_version
capture_time
```

Raw 数据不跨账号直接合并；聚合层统一字段和统计口径后，才进行跨账号对比、分群和规律归纳。

## Codex Subagents

已建立保守的 1 个主 Agent + 4 个只读子 Agent Pilot：

- `repo_explorer`
- `knowledge_retriever`
- `evidence_test_verifier`
- `reviewer`

默认模式为 `OFF`；只有 User 确认父会话权限受限且任务适合并行只读工作时，才切换到 `MANUAL`。主 Agent始终是唯一写入者。Subagents 不是任何任务的前置条件。

## 项目记忆与跨对话

ChatGPT Project 的项目指令、来源文件和同一 Project 内的历史对话用于减少重复说明；新对话仍必须在涉及“当前状态、是否已实现、Task、commit、运行结果”时查询 Git 或相应受控系统，不能把项目记忆当作实时数据库。

### Git-backed Memory Capability

```text
Conversation / Agent
→ Memory Event / Candidate
→ deterministic validator + scope router
→ ASSISTED Review / AUTO allowlist promotion / Local Outbox
→ Canonical Git + Context Manifest + Project Source Pack
```

标准 ChatGPT GitHub App 只读时使用 Outbox handoff；Codex 是默认 Git writer/Curator。Global hook、外部服务和生产 AUTO 不在默认接入中。
