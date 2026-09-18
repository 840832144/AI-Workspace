# TASK-0036 — CR 9.22 全项目数值体验与制作人汇报

- Status: Review
- Execution status: 数值报告Round 1 Accepted保留；相对外链master与无外链展示版已完成并回读，等待ChatGPT Review；不调参、不冻结或发布
- Project key: CR
- Owner: User
- Executor: Codex
- Priority: P1 / 9.22制作人汇报
- Date: 2026-09-17
- Updated: 2026-09-18
- User decision: Approved（全项目体验分析与报告；不调参、不改SVN、不冻结、不发布）
- PR: [#10](https://github.com/840832144/AI-Workspace/pull/10)（OPEN；数值报告已Accepted，展示副本登记待User轻量Review）
- Allocation relationship: new
- Related tasks: TASK-0033, TASK-0034, TASK-0035
- Subagents: none

## Goal

基于TASK-0033全数值底稿、TASK-0034规则闭合及TASK-0035薯片+777现值候选，形成可供制作人决策的全项目数值体验汇报，交ChatGPT Review。不重新盘点或验收已Accepted工作；当前任务只新增体验场景、跨系统解释和必要的变化数据。

## 2026-09-18 当前正式输入：原始r7013外链master与独立展示版

- [最新User决定](https://github.com/840832144/AI-Workspace/pull/10#issuecomment-5724897864)覆盖下方历史“全部自包含/每模块单页”约束；原Task与reservation沿用，不新建Task。
- [前版Excel产物Review](https://github.com/840832144/AI-Workspace/pull/10#issuecomment-5724542994)为Needs changes，针对User上传文件而非最新commit；不撤销原数值报告Accepted。本轮修复元数据本机路径、长表阅读结构，并按User最终输入保留全部逐行明细。
- 仅定向`svn export -r7013`导出实际所需37份trunk原始工作簿；新master配置输入来自这些原始格，r6961抽取不再作为本次Excel源。Accepted场景/结果用作定义与交付核对；旧Wiki只供结构、阅读节点和展示方式。
- master在受控本机使用，SRC相对外链直指原始源格；CALC/前台公式可追溯。每模块概览+明细，完整适用原行/原字段、筛选、冻结、分组/跳转；等级沿用旧表节点并补业务变化点。
- 独立飞书展示版使用相同版本清单和master已验证缓存，移除外链并保留内页跳转；不上传master/原始源包，不覆盖旧附件、不修改权限。生成后清理作者和绝对路径，验证整包搬移及master/展示版一致性。
- 已安全fetch main与原PR分支，远端未新增共享文件改动；Task补充输入造成Registry drift后按原工具重建，19 canonical / 0 collision / valid。Subagents: none。

## 历史正式输入：首版自包含数值体验Excel（已被上述要求覆盖）

- 沿用TASK-0036及原reservation，不新建Task。User及[PR #10正式输入](https://github.com/840832144/AI-Workspace/pull/10#issuecomment-5724092870)要求Excel作为主要策划/制作人展示产物，既有飞书文档保留为辅助说明。
- 只读下载旧`CashRoyal数值.xlsx`，分析模块、横向档位对比、累计和公式习惯；旧值、旧经验规则和外链不作为当前数值依据。当前依据仍为r7013适用版本及Accepted底稿，9组Unknown不改。
- 新`CR_9.22_数值体验表_r7013.xlsx`每模块一张前台Sheet；隐藏SRC配置、CALC计算和来源索引，前台公式引用。无外部文件链接，不手填派生结果，Unknown不补0。优先14模块含Buff；只定向读取所需Accepted抽取，不重跑旧Task、SVN或hash。
- 完整数值/旧表/预览/复核包留受控目录。Git只保存生成方法、旧表结构说明、脱敏验证摘要和治理记录。使用现有飞书CLI上传到旧数值资料所在知识目录，不覆盖旧表、不扩大权限。
- 开始前已安全fetch main及原分支；Registry 19 canonical、0 collision、valid，共享文件无新增并发差异。Workspace Sync ON_DEMAND/provider unavailable/stale 6/conflicts 0。原PR #10保持OPEN，交ChatGPT Review，不合并或finalize。Subagents: none。

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

## 交付与验证（2026-09-17）

- [脱敏制作人报告与受控入口](../projects/cr/REPORTS/CR-20260922-PRODUCER-EXPERIENCE/README.md)：八类系统、Executive Summary、静态分层、100/500/1000 Spin、资源产消、成长、付费/Pass、卡包与双活动、风险和Unknown均已覆盖。
- 15:49:34北京时间固定公司trunk r7013；r6961→r7013整个trunk变更路径摘要为空，包含ExcelConfigExport/Excel、QuestMap、slots及潜在新增数值路径。所有系统复用，源刷新0；r6961原证据与r7013适用revision分别标记，无hash、全量正文扫描或重新导出。
- 仅新增36组静态Spin、72条薯片/777结果、36条精确掉卡条件；连续积分用命中次数分布逐项结算，未将平均积分代入阶段充作期望。毛下注只记一次，跨活动相关性Unknown保留概率上下界。
- 固定档模型不代表玩家分布/真实升级；常规85%/95%与特殊RTP分离。道具来源上限不等于完整周期成本；未明经验、福利频次、商品单位、持卡状态、完整活动EV等归为9组解释边界，沿用历史22项来源，不新开冻结Gate。
- 完整数值、受控报告、38个实际读取的Accepted输入、可复算脚本与版本摘要在 `%LOCALAPPDATA%/AI-Workspace/cr-numerics-20260922/producer-experience-20260917/`。复核ZIP不含reservation token、内部SVN地址或完整运行日志；public Git只放脱敏报告/方法/治理记录。
- 新模型6项测试通过；实际输出的场景唯一性、概率质量、金币守恒、共享成本和八类覆盖通过。仅按既有工具重建/验证Task Registry，检查本轮diff/链接；没有重跑TASK-0033/0034/0035 Accepted数值验收或原始XLSX公式。
- 分支 `codex/cr-0922-producer-experience` 交ChatGPT Review；reservation保持pending-main，不合并或提前finalize。0035零数值变更候选、原始源表不动；不调参、不修改/提交SVN、不冻结、不发布。Subagents: none。

## 飞书展示副本链接登记（2026-09-17）

- 展示文档：[CR 9.22 全项目数值体验｜制作人展示版｜r7013](https://gfok27asqq.feishu.cn/docx/Rm2GdeMcXoEg2SxodIScDdzpn1c)。Git/TASK-0036继续是真相源；本篇仅为会议展示副本，不替代原报告或受控底稿。
- 依据PR #10已发布的ChatGPT Round 1 Accepted（受评`d663a0c728395f5f504f3ce5c7305c2aeaefcd8c`）及User同PR的展示授权；本轮只创建展示副本并登记链接，不改数值、Unknown、r6961原证据/r7013适用版本或既有候选。
- 使用已接入飞书CLI、显式user身份，在既有目录检查同名后创建；回读revision 4，7个章节顺序、8张展示表、36组Spin汇总、八类系统、9组Unknown、全部段落及2个Git来源链接与草稿一致，目标目录同名文档仅1篇。
- 权限回读为`tenant_readable`（公司内链接可读），沿用新文档默认内部权限；没有执行ACL/分享设置修改或开启公网链接分享。无附件，未上传受控包完整商业明细、源配置、内部URL/路径、token、私有Registry或敏感日志；完整展示草稿只留本机受控目录。
- 当前Review针对本次展示副本及链接登记；数值报告Accepted依据不变。未重算数值、重跑旧Task或做hash；Workspace Sync为ON_DEMAND/provider unavailable/stale 6/conflicts 0，展示文档CLI的真实创建/回读结果独立记录，不冒充Context provider可用。
- 按User本次授权仅登记Task/Status/Handoff链接；未执行正式冻结或发布，不修改/提交SVN、不调参、不合并PR #10或finalize，原reservation pending-main。Subagents: none。

## 2026-09-18 — TASK-0036双版本Excel完成，等待ChatGPT Review

- 按PR #10最新User输入形成相对外链master与无外链飞书展示版；原数值报告Round 1 Accepted保留，本次Excel仍为Review。前版14页产物的Needs changes与旧自包含方案保留为历史。
- [当前飞书展示版](https://gfok27asqq.feishu.cn/wiki/UZD8wLpQKicKV7kcorIcNIb8nwd)；原旧表及前版候选未覆盖。Git/TASK-0036与本机受控master是真相源，飞书是展示快照。公司内链接可读、external access closed，未修改ACL或开启公网分享。
- 37份原始trunk工作簿定向`svn export -r7013`导出；26张前台含12组概览/明细、总览和Unknown。等级5000行及升级奖励4999行、价格7236行完整保留；104个筛选表、26页冻结前6行/首列，等级分组和内页跳转。
- 最终master 1,062,421公式、37条相对外链；展示版0公式/0外链。969个关键输出与Accepted底稿一致，两个版本逐格一致，源格缓存一致；公式错误/缺缓存/作者或绝对路径检查为0。搬移后37条链接解析、代表源格刷新及原生窗格回读通过；26页视觉复核。飞书下载回读969项通过。
- 完整文件、相对源包、版本清单和验证证据位于受控`producer-master-20260918/`；公开Git仅工具、结构、方法、脱敏验证与交接。旧Wiki系统功能19页/17份XLSX子模块结构已检查，旧值没有入当前计算。
- 9组Unknown保留，未重跑旧Task模型/全量配置盘点或hash；未重算或修改源表。不调参、不提交SVN、不冻结或发布；PR #10保持OPEN，原reservation pending-main，不合并或finalize。Subagents: none。

- [结构/复现方法](../projects/cr/REPORTS/CR-20260922-PRODUCER-EXPERIENCE/WORKBOOK.md)、[最终验证摘要](../projects/cr/REPORTS/CR-20260922-PRODUCER-EXPERIENCE/WORKBOOK_VALIDATION.json)、[首版Excel产物Review](../reviews/TASK-0036-CHATGPT-EXCEL-REVIEW-1.md)。
