# AI Workspace｜产品路线图（Product Roadmap）

> 更新时间：2026-10-17
> Git 真相源：`docs/roadmaps/PRODUCT_ROADMAP.md`
> 适用范围：Game Planner AI Workspace 的长期产品方向

本文是 AI Workspace 唯一的长期产品规划文档。它回答“接下来可能建设什么”，不替代 canonical Task、项目 Status、Documentation Hub、Knowledge Base 或根目录的 Workspace 阶段路线图。

条目必须归入以下四个固定分区之一。分类变化需要保留可复查依据；Roadmap 条目本身不等于执行授权，也不会自动创建 Task。

## 🔥 Current

### Bingo原客户端本地兼容里程碑

- 来源：沿用PR #21@7f9729f已有同名Idea；2026-10-16 User批准为独立可玩目标，remote-CAS登记TASK-0043，不新增同义方向。
- 交付：原客户端大厅→单卡持续游玩→基础道具→合法Bingo→正常结束返回并可再次入局。
- 当前状态：TASK-0043业务513f5da实证本地认证及六条初始化，后续初始化仍待闭合，尚未完整一局；按c3bc731由Codex统一A/B工程，已接收CardCandidate基线d35c8a0，dsh负责研究取证。恢复工程业务dfd312c已构建交互修复候选，后续测试交User；原版呈现与原客户端一局仍未验收。未以资源数量或局部回归计完成。完整依据为[执行规格](../../tasks/support/bingo-client-local-round-20261016/EXECUTION_SPEC.md)。
- 边界：原TASK-0039暂停，TASK-0041验证暂缓，不挪旧预算/规则，不据目标批准推定新增环境权限。不做全部房间、数字Auto Play或GM。
- 2026-10-17候选：业务19287fe接入六类初始化并完成M2实际素材/布局新包；M1的203恢复合同发现ErrResp误读，完整初始化仍待闭合；M2新版尚未User测试。
- 当前里程碑：按 User 最新指令及[e124b86专项执行单](../../tasks/support/TASK-0043/M1-ONLY-IMPLEMENTATION-20261017.md)，**M1 是 TASK-0043 唯一 Current 开发焦点**；M2 冻结工程、包与差异记录，暂停新视觉/功能研究。User 评价基本功能正常、原版效果差距非常大，不是 M2 验收通过。旧18c9361并行安排被本项覆盖。
- 当前依赖：dsh修正203缓存恢复和1001/2403/1205消费链，再延伸普通单卡必要协议；共享目录尚未收到新合同，已由ACK-014直接交接。Codex复用现有服务离线接入、构建及打包，User负责所有成品测试；完整候选就绪后一次提出有界复验方案，不自动重启现场。当前无新增业务行为或验收结果。
- 后续扩展：同一方向下保留 M2 恢复、多卡/完整道具池/Bet表和移交表现增强，待 M1 后由 User 决定，不挤占本轮一局交付。保留[10e6aa5历史范围](../../tasks/support/TASK-0043/DSH-CONTINUATION-AND-REUSE-20261016.md)，未承诺原始源码齐全或全游戏重建。本次仅更新Git，未发布云文档。

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
