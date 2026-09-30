# AI Workspace｜产品路线图（Product Roadmap）

> 更新时间：2026-09-30
> Git 真相源：`docs/roadmaps/PRODUCT_ROADMAP.md`
> 适用范围：Game Planner AI Workspace 的长期产品方向

本文是 AI Workspace 唯一的长期产品规划文档。它回答“接下来可能建设什么”，不替代 canonical Task、项目 Status、Documentation Hub、Knowledge Base 或根目录的 Workspace 阶段路线图。

条目必须归入以下四个固定分区之一。分类变化需要保留可复查依据；Roadmap 条目本身不等于执行授权，也不会自动创建 Task。

## 🔥 Current

### Huuuge 自助研究工作台 V1

- 已批准：[TASK-0037](../../tasks/TASK-0037-HUUUGE-SELF-SERVICE-V1.md)，PR12/a91bf39及2026-09-30 User范围调整；后继TASK-0031 Accepted。
- 本阶段：官方Web玩固定账号＋独立采集小面板，可信同事约定轮流；基本鉴权、单采集任务防重复、云端常驻/受保护连接、一键启停、真实四态、结束下载及本地AI读包。取消SDK内嵌、统一登录与强制手机控制交接/防重连/旧凭证撤销验收。
- 当前：In Progress；User已批准并部署受限SSH/两个任务身份、常驻服务、可信HTTPS及续期。216b298真实API冒烟10捕获/10解码/0失败、正常结束/清理/ZIP回读通过；仅后台消息，无User游戏操作。User首次网页代理失败，经单地址例外授权修正并复测；正接续User双标签页Slots→结束下载及本地AI、轮流/异常/无管理会话A—F。User成员登录仍仅本人反馈；不扩大同事盲测/Android客户端或完整V1，不进入Done。新的费用/入口/云权限/共享变更先确认。

### 【游戏】 Collector 1.0

- 当前状态：TASK-0026 已完成 allocator finalize；Collector 1.0 实现已 push 到 `CF_collect@7c32877` 并进入 ChatGPT Review，未执行新的动态 Spin。
- 产品目标：在不恢复新字段、不扩大 `batch_spin` 六字段 schema、不改变 Android 9 已验证采集路线的前提下，建立 Adapter Registry、统一 Event contract 与固定 Session artifacts。
- 下一动作：ChatGPT Review `codex/collector-1-engineering@7c32877` 的 Adapter contract、固定 artifacts、Sidecar allowlist 与部署兼容性；Review 前不合入正式仓库 main，不扩大字段或模块。

## 📋 Backlog

### One Research Environment → Multiple Games → Independent Evidence

- 下一阶段Backlog：复用原方向；本次TASK-0037仅Huuuge，完成V1后才按具体游戏复用采集器与独立证据。
- 依据：PR12已批准路线图交接；RFC-0004仍Proposed，不自动授权其他游戏。
- Gate：单活动Capture、前台包名校验、游戏级数据隔离和每个游戏真实可行性验证；不预建通用插件平台。

### Top Tycoon

- 当前状态：canonical `TASK-0025` 已是 `Ready`，但尚未开始执行；User 后续明确把当前优先级切换到 TASK-0026，因此本方向暂留 Backlog，不与 Collector 1.0 并行执行。
- 已批准目标：在 `topTycoon` 研究实例中按 F0–F4 Gate 审计核心 Spin 链、跨 Session 复现、确定性 lifecycle 与次级模块边界。
- 恢复条件：User 再次明确切回本方向；届时从最新 main 和 TASK-0025 重新核对 identity、授权与执行前置，不复用本 Task 的业务 schema 或本地数据。

### Documentation Portal

- 价值：为策划提供比单篇文档导航更完整的可视化文档门户。
- 进入 Current 的条件：明确目标用户、页面范围、真相源、维护成本和与文档导航中心的边界。

### Recent Updates

- 价值：让策划快速看到 Workspace、研究项目和正式文档的近期变化。
- 进入 Current 的条件：定义更新时间窗、可信数据源、去重规则和隐私边界。

### Experience Timeline

- 价值：把游戏体验、系统解锁、活动节奏与证据时间线组合成策划可读视图。
- 进入 Current 的条件：确定最小数据模型、Evidence 要求和首个验证项目。

## 💡 Ideas

### 每位策划独立云手机

- 未来Ideas：每人独立实例/账号隔离尚无采购授权，本版固定一台共享体验账号，不扩资源。

## ✅ Done

### CR 单仓策划入口

- 已交付：public AI-Workspace/projects/cr 的资料、唯一 Skills 与分析工具；User 明确批准三个 Top Tycoon 工作簿及原始记录历史。
- 完成依据：TASK-0032 全新单仓候选验收、[ChatGPT Round 1 Accepted](../../reviews/TASK-0032-CHATGPT-REVIEW-1.md)，以及 User 最终授权后 PR #5 merge commit `3c214e2`、最新 main 入口/祖先核验与原 reservation finalized。评审未独立复跑测试的限制保留。
- 当前边界：CR 日常只写 AI-Workspace/projects/cr；公司 SVN 正式配置不变，旧库保留不双写，暂不归档、不删除。来源、[RFC-0005](../rfc/RFC-0005-CR-Subtree-Public-Migration.md) 与[迁移报告](../migrations/CR-MIGRATION-20260916.md)可追溯。本次仅更新 Git，未发布飞书或扩大分享。

### 【游戏】 Inbound Structured Capture Spike

- 已交付：Android 9 inbound-scoped Lua 边界、5/5 `batch_spin` direct Result/Win/Balance 字段路径、受限 serializer、脱敏聚合与 clean finalize。
- 完成依据：TASK-0024 ChatGPT Review Round 1 Accepted；等级为 F3 strengthened，F4 未证明。
- 后续边界：完整 Collector、20-Spin、最小 adapter 或其他模块必须另走 Roadmap / Candidate / 新 Task。

### Documentation Hub

- 已交付：唯一《AI Workspace｜文档导航中心》、八分类、自动登记、回读和防重复治理。
- 完成依据：TASK-0021 / ADR-0007 已 Accepted。

### Workspace Sync

- 已交付：Git-authoritative Context 的 `ON_DEMAND` 同步、冲突模型、local pack 与 Host bindings。
- 完成依据：TASK-0021 已 Accepted；生产 `WATCH` 仍未启用。

### Task Governance

- 已交付：Candidate、全局 canonical Task ID、Registry、remote-CAS allocator、collision gate 与生命周期管理。
- 完成依据：TASK-0020 已 Accepted。
