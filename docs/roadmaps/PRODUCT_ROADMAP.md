# AI Workspace｜产品路线图（Product Roadmap）

> 更新时间：2026-10-15
> Git 真相源：`docs/roadmaps/PRODUCT_ROADMAP.md`
> 适用范围：Game Planner AI Workspace 的长期产品方向

本文是 AI Workspace 唯一的长期产品规划文档。它回答“接下来可能建设什么”，不替代 canonical Task、项目 Status、Documentation Hub、Knowledge Base 或根目录的 Workspace 阶段路线图。

条目必须归入以下四个固定分区之一。分类变化需要保留可复查依据；Roadmap 条目本身不等于执行授权，也不会自动创建 Task。

## 🔥 Current

### Bingo核心玩法本地试玩版

- 当前状态：TASK-0041已交付0.2.1原生候选，Round 1为Needs changes；2026-10-16完成R1/R2代码修订，User要求先跳过验证。尚未Accepted，原TASK-0039继续暂停。
- 价值：把Bingo研究转成可独立游玩、可配置、可重复验证、可移交Unity团队的核心玩法原型。
- 范围：大厅、选卡/Bet、开局、填格、Normal/Rare/Epic九道具、Bingo剩余计数、结束及返回大厅；默认1卡，暂定1/2/4/6卡，Bet与每卡Bingo上限按完整规格采用五档暂定映射，未知原随机策略先用固定卡面和出球；不做多人信息、成长与局外奖励发放。
- 当前依据：[完整执行规格](../../tasks/support/bingo-core-demo-20261015/EXECUTION_SPEC.md)。dsh二次核验与开发并行，未验证项明确暂定；旧[方案讨论稿](../proposals/BINGO-CORE-DEMO-CANDIDATE-20261015.md)保留为历史。
- 下一动作：后续恢复验证时，冻结修订候选并用短固定场景补当前原生/HTTP/离线闭环；本轮不跑验证、不以旧成绩关闭缺口，不重做现有核心。

### 【游戏】 Collector 1.0

- 当前状态：TASK-0026 已完成 allocator finalize；Collector 1.0 实现已 push 到 `CF_collect@7c32877` 并进入 ChatGPT Review，未执行新的动态 Spin。
- 产品目标：在不恢复新字段、不扩大 `batch_spin` 六字段 schema、不改变 Android 9 已验证采集路线的前提下，建立 Adapter Registry、统一 Event contract 与固定 Session artifacts。
- 下一动作：ChatGPT Review `codex/collector-1-engineering@7c32877` 的 Adapter contract、固定 artifacts、Sidecar allowlist 与部署兼容性；Review 前不合入正式仓库 main，不扩大字段或模块。

## 📋 Backlog

### Bingo Voyage 原客户端自动玩（User暂停）

- 当前决定：2026-10-15 User明确暂停TASK-0039，优先本地核心玩法Demo；不因原实例恢复而自动续跑。
- 保留：原PR #16/#17、全部历史实现/失败/账本/登记，原目标未Accepted、不取消或finalize。本轮已回写暂停指令；canonical Task/Status/Handoff由Codex按现有工具同步。
- 恢复条件：User再次明确切回该目标；与新Demo任务、未来GM工具分开，不继承线上额度给新任务。来源见[优先级与范围](../proposals/BINGO-CORE-DEMO-RULES-AND-UNITY-20261015.md)。

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

### Bingo本地Auto Play / GM工具

- 状态：2026-10-15 User明确要求只记录、不启动；不创建执行子任务。
- 价值：在自研规则服上通过同一动作合同执行策略、场景重放和数值实验，不依赖原客户端外部坐标点击。
- 前置：核心Demo与可复用规则内核完成，另行确认GM范围和验收；本Demo普通单元测试/固定案例不等同于GM产品。
- 来源：[最新补充规则与后续里程碑](../proposals/BINGO-CORE-DEMO-RULES-AND-UNITY-20261015.md)。

### Bingo原客户端本地兼容里程碑

- 状态：保留为后续可行性候选；User看重该里程碑，但不把它作为自研Demo交付前置。
- 2026-10-16下一步方案：[Round 1兼容计划](../../tasks/support/TASK-0041/ORIGINAL-CLIENT-NEXT-PLAN-20261016.md)。先盘点获准构建/配置入口与最小初始化依赖，拟以一张合成卡、一次叫号/手工填格到结束返回验证；本轮仅形成方案，不新建Task、不操作原实例。
- 评估范围：可用原工程/测试构建、受支持的服务配置入口、核心初始化/资源依赖，以及同一本地规则服的兼容适配成本。已有局内协议不等于完整启动链可用。
- 边界：当前不启动原APK改接或保护组件修改，不扩展旧研究权限；确定可行性与范围后再申请执行。
- 来源：[路线比较](../proposals/BINGO-CORE-DEMO-RULES-AND-UNITY-20261015.md)。

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
