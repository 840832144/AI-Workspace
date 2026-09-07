# AI Workspace｜产品路线图（Product Roadmap）

> 更新时间：2026-09-07
> Git 真相源：`docs/roadmaps/PRODUCT_ROADMAP.md`
> 适用范围：Game Planner AI Workspace 的长期产品方向

本文是 AI Workspace 唯一的长期产品规划文档。它回答“接下来可能建设什么”，不替代 canonical Task、项目 Status、Documentation Hub、Knowledge Base 或根目录的 Workspace 阶段路线图。

条目必须归入以下四个固定分区之一。分类变化需要保留可复查依据；Roadmap 条目本身不等于执行授权，也不会自动创建 Task。

## 🔥 Current

### EarlyMeeting｜本人行填写与同卡汇总

- 当前状态：[TASK-0028](../../tasks/TASK-0028-EARLYMEETING.md) 核心实现提交 Review。User 已实际新增及保存本人行，按反馈改为策划 / 程序两个区域，各有人员和晨会内容两列、各自加号；最终布局已更新同一消息。取消部门列及通讯录读取，不追加复杂测试或验收流程，直接使用、有问题再改。
- 产品价值：保留现有应用、原模板与发送入口，通过已验证的长连接实现多人本人填写；业务规格与实现见 [EarlyMeeting 当前方向](https://github.com/840832144/EarlyMeeting/blob/codex/task-0028-local-callback/docs/CURRENT_DIRECTION.md#后续产品目标澄清)。此前 Backlog 的多人汇总范围合并到本条，不另建产品或 Future Task。
- 交付边界：范围限指定测试群与受控本机保存，工作日 10:00 调度关闭。已运行证据与未运行检查如实记录，不以额外多人/手机/压力测试作为交付前置；握手前 IPv4 TCP 超时已捕获，具体网络原因仍未确认，正式 Review 前不进入 Done。

### 【游戏】 Collector 1.0

- 当前状态：TASK-0026 已完成 allocator finalize；Collector 1.0 实现已 push 到 `CF_collect@7c32877` 并进入 ChatGPT Review，未执行新的动态 Spin。
- 产品目标：在不恢复新字段、不扩大 `batch_spin` 六字段 schema、不改变 Android 9 已验证采集路线的前提下，建立 Adapter Registry、统一 Event contract 与固定 Session artifacts。
- 下一动作：ChatGPT Review `codex/collector-1-engineering@7c32877` 的 Adapter contract、固定 artifacts、Sidecar allowlist 与部署兼容性；Review 前不合入正式仓库 main，不扩大字段或模块。

## 📋 Backlog

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

### One Research Environment → Multiple Games → Independent Evidence

- 设想：多个游戏可以复用受控 Research Runtime，但每个游戏的 Session、Capture、Manifest、Raw 与 Evidence 必须独立。
- 当前依据：`RFC-0004-Research-Environment-Strategy.md` 仍为 Proposed。
- 主要 Gate：单活动 Capture、前台包名校验、游戏级数据隔离和对现有独立环境决策的兼容性 Review。

## ✅ Done

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
