# TASK-0036 — CR 9.22 全项目数值体验与制作人汇报

- Status: In Progress
- Execution status: 已由allocator登记；先定向检查数值相关路径版本差异，再复用/增量刷新并制作报告
- Project key: CR
- Owner: User
- Executor: Codex
- Priority: P1 / 9.22制作人汇报
- Date: 2026-09-17
- Updated: 2026-09-17
- User decision: Approved（全项目体验分析与报告；不调参、不改SVN、不冻结、不发布）
- Allocation relationship: new
- Related tasks: TASK-0033, TASK-0034, TASK-0035
- Subagents: none

## Goal

基于TASK-0033全数值底稿、TASK-0034规则闭合及TASK-0035薯片+777现值候选，形成可供制作人决策的全项目数值体验汇报，交ChatGPT Review。不重新盘点或验收已Accepted工作；当前任务只新增体验场景、跨系统解释和必要的变化数据。

## 范围与正式输入

- 必须覆盖Slots Bet/RTP、货币价值、等级/VIP、任务福利、常驻系统、商城礼包/Pass、卡包卡册、9.22薯片+777。
- 制作人版包含Executive Summary、玩家分层体验、100/500/1000 Spin体验、资源产消、成长节奏、付费价值、活动叠加、风险与Unknown。
- 沿用User常规RTP：USD Bet>1为85%，≤1为95%；新手及活动特殊RTP独立呈现，未明优先级不擅自推定。连续积分、Pass共享门槛、薯片单奖及777 forceTurn沿用已Accepted正式规则。
- 9.22活动仅薯片+777；不把拳击/挖矿引入体验组合。完整公式和明细在受控包；public Git只保存脱敏汇报、方法、版本摘要和治理记录。
- 不做广告经济、生命周期/老客迁移、线上/运营或技术审计；不请求线上数据作为前置。不调参、不修改或提交SVN、不执行正式冻结或发布。

## 登记与并发

- 起点最新main `b0a36c8e1b75299814b3354530a58bbf59518714`，PR #9已合并；0033/0034/0035均Complete，0035原reservation已finalized。
- 完整枚举tasks/31个文件；Registry 18 canonical、0 collision、valid。活跃0018（Huuuge Review）、0025（Top Tycoon Ready）及远端0027/0028/0030/0031 reservations不覆盖本CR范围。
- 既有allocator返回TASK-0036，原reservation保持pending-main；独立linked worktree及分支`codex/cr-0922-producer-experience`，不猜号、不借旧Task。
- Workspace Sync：ON_DEMAND，provider unavailable，stale 6、conflicts 0；Git为真相源，不发布云文档或改变分享权限。

## 方案

1. 以TASK-0033既有完整数值目录和机台/地图数据根界定相关路径，读取当前trunk revision及r6961到该revision的变更路径元数据；覆盖新增/删除，锁定一致版本。只读取有变化的数值文件；无变化直接引用Accepted证据，不重复提取全库或计算hash。
2. 未变化系统标记原证据revision与当前适用revision。变化系统只刷新受影响源数据及派生关系；不混dev、101或旧附件数值，不覆盖旧Accepted产物。
3. 从现行配置可支持的等级/VIP/Bet/解锁条件构造透明的代表场景；将配置分层与真实玩家分布区分。100/500/1000 Spin分别给毛下注、机器返还/净耗、活动获取、阶段达成与成长关系；概率/方差缺失时不声称破产概率或百分位体验。
4. 汇总各系统资源入口、消耗和返还、成长门槛、商品配置价值、卡包卡册及双活动叠加。每个数值保留表/Sheet/行键/字段、单位、分母、版本和假设；不把配置美金当实付，不把E[进度]代入离散阶段当E[阶段]。
5. 形成中文制作人报告（Executive Summary优先）、可复算方法、受控明细/复核包、Unknown与责任来源。Unknown不补0，已有非阻塞缺口不自行升级为配置冻结Gate。
6. 只验证新增场景的关键公式/边界、受影响版本关系和交付覆盖，重建Registry、检查变更diff/链接；提交候选分支和PR交ChatGPT Review，不合并、不finalize。

## 验收与回滚

- 八类业务范围与九个报告主题均有结论或具体Unknown；明确体验推断的条件和实际配置证据，不把源存在当全系统已验收。
- SVN差异摘要列出数值相关路径边界、读取时间、固定revision、变化清单及复用/刷新决定；原Accepted工作不重跑。
- public报告不含完整商业数值/受控数据/内部地址/凭据。受控包含复算输入引用、公式、阶段/资源结果、当前版本证明及证据限制。
- 仅新增分析与Git记录，无源配置回滚；需撤回时保留旧证据，通过后续Git更正处理，不强推或删除原数据。Review通过不自动授权调参、SVN、冻结或发布。
