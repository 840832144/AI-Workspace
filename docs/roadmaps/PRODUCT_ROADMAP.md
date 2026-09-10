# AI Workspace｜产品路线图（Product Roadmap）

> 更新时间：2026-09-08
> Git 真相源：`docs/roadmaps/PRODUCT_ROADMAP.md`
> 适用范围：Game Planner AI Workspace 的长期产品方向

本文是 AI Workspace 唯一的长期产品规划文档。它回答“接下来可能建设什么”，不替代 canonical Task、项目 Status、Documentation Hub、Knowledge Base 或根目录的 Workspace 阶段路线图。

条目必须归入以下四个固定分区之一。分类变化需要保留可复查依据；Roadmap 条目本身不等于执行授权，也不会自动创建 Task。

## 🔥 Current

### EarlyMeeting｜本人行填写与同卡汇总

- 当前状态：[TASK-0028](../../tasks/TASK-0028-EARLYMEETING.md) 已返回 Review。2026-09-08 User 撤回正式群2预填及全员行操作，现已恢复为与群1一致：预填关闭，个人行仅本人提交/删除，今日交付仍本群共用。三个群原消息与记录保留，继续工作日09:45每群每天一张。名单匹配及新增只读权限流程暂停，不再等待权限；可选代码保留但不启用，不新增 Future Task。
- 产品价值：保留现有应用、原模板与发送入口，通过已验证的长连接实现多人本人填写；业务规格与实现见 [EarlyMeeting 当前方向](https://github.com/840832144/EarlyMeeting/blob/codex/task-0028-local-callback/docs/CURRENT_DIRECTION.md#后续产品目标澄清)。此前 Backlog 的多人汇总范围合并到本条，不另建产品或 Future Task。
- 交付边界：个人行 UI 曾获 User 验收；本次恢复后已真实 CONNECTED，三群原消息分别恢复1/8/6行，无重新发卡或模拟操作。两个正式群已于2026-09-08开始日常使用，三个群数据独立。Windows 程序需持续运行，没有系统自启；正式 Review 前不进入 Done。共享模式下逐查看者隐藏他人按钮仍未实现，个人行归属校验保留。

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

### EarlyMeeting｜10:15 指定名单未提交提醒（暂停）

- 设想：按每群指定的应参加晨会名单，在北京时间 10:15 提醒尚未提交者。
- 当前依据：User 提出后明确暂停，后续根据需求决定；本轮未实施、未启用，不收集名单或读取群成员。
- 恢复条件：User 重新明确批准后再核对范围与正式任务准备；本条不自动产生 Future Task。

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
