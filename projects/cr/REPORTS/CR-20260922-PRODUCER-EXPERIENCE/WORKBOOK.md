# TASK-0036 数值体验工作簿：master 与飞书展示版

当前依据TASK-0036的“2026-09-20 — 制作人汇报型Excel重构”规格。原数值报告Accepted保留，新Dashboard候选单独交ChatGPT Review；不修改TASK-0035候选，尚未冻结或发布。

[9/18历史飞书展示版](https://gfok27asqq.feishu.cn/wiki/UZD8wLpQKicKV7kcorIcNIb8nwd)未被本轮覆盖，不能用其下载结果验收9/20产物。本轮受控目录为`%LOCALAPPDATA%/AI-Workspace/cr-numerics-20260922/producer-dashboard-20260920/`；master与`source/r7013/`整包使用，展示版可单独使用。本轮先交本地双版本Review。

## 9/20制作人Dashboard与计算方法

当前27张前台：Dashboard、12组模块概览/明细、关闭模块索引、9组Unknown。每张概览有4个KPI、完整阶段表和1–2张图；36组Accepted静态Spin下沉明细。各项成本和返还不可跨模块直接相加。

- 固定r7013，复用原37份工作簿并定向补充7份必要配置，当前相对外链源共44份。补充仅涉及解锁Bet、旧表逻辑还原、卡池、钻石/商品、Jackpot及指定常量；不做trunk全量扫描。原始源表只读，不保存或改数值。
- 等级全5000行使用当前最大已解锁普通Bet，经验门槛除以对应每Spin经验向上取整；升级成本统一95%。当前代码与配置表明单次升级上限为1且丢弃溢出。累计列采用前行累计加本行，避免重复长范围依赖。原4999条升级奖励与7236条价格配置完整保留。
- 旧正式BET表采用阈值近似匹配的INDEX/MATCH；沿用“已解锁档→Bet→体验”的关系。机型金额默认以旧二倍数制做显式参考，明细保留五列×四VIP敏感性；当前机台与五列的唯一绑定仍Unknown，不把默认列冒充全机台。
- VIP按100点/美元计算增量与累计充值成本，礼包单独估值；商品点数差异仅作一致性提示。VIP不增加等级经验。普通金币按当前等级/VIP，9/17类配置美元分除100，钻石列出当前可见商店所有档位；主估值使用最低标价档，并非统一市场公允价。
- 福利保留各自周期；混合商品只汇总可确定价值的部分。仅薯片Pass有效；通用VIP Pass字段未证明适用于薯片，移至关闭/历史索引，未加入有效Buff或薯片奖励。薯片商品按ID关联当前SnackItemPack或黄金Pass奖励，不用空的通用金币/钻石栏补0。黄金Pass回报明确是全完成潜在价值。关闭模块与历史Buff从当前有效经济中分离。没有唯一开放或兑换证据的常驻项保留具体Unknown。
- 薯片按20盒初始与重置、JP重复、Pass共享门槛模拟400条路径；阶段首达和固定开盒量分开。自然获取末档封顶，因此超过上限的样本不以零成本或已完成子集均值替代；阶段成本、Spin与返还率保留Unknown，另给自然上限内完成率与潜在奖励。黄金Pass奖励单列，不计免费总返还。
- 777按User已闭合forceTurn与内圈普通格消失规则模拟1000条三轮路径，区分普通/特殊付费命中、圈、轮和三轮累计骰子与自然获取成本。r7013代码自动进入内圈仍扣费，与User本轮免费临时取奖口径不同；本模型明确按User分析口径，不声称程序运行一致。
- 卡册从空册、赛季第1天开始，逐卡维护去重、稀有度、章节补缺与持卡状态。低/中/高三个情景各100样本，UID权重档等配，只是敏感性输入；使用r7013抽卡链和配置，不使用旧附件数字。季末未完成保留删失；仅全部样本完成时展示样本均值，否则章/册期望成本Unknown。高阶册未以普通册平均数替代。

旧`卡包数值调整.xlsx`共有8个Sheet：旧正式表以“所需开包数÷掉包效率”推最低局数，并按最高星瓶颈比较；未发现可直接复用的老虎机完整持卡状态模拟或正式玩家分层。其历史所需包数、旧概率与旧值均未进入r7013。当前逐章模拟是新增Estimate，不能沿用原报告Accepted标签。

随机计数与离散阶段路由由固定seed的生成器产生；金额与关键成本以工作簿公式引用源格。修改概率、卡池、离散数量或玩家情景后须重跑对应生成器，不能声称Excel会重新运行Monte Carlo。静态等级/VIP标签不作为任意修改即重算的选择器；机型列与VIP点/美元两个明确驱动在原生Excel做变化后还原验证。

```text
python build_producer_dashboard.py --baseline <9/18受控目录> --output <9/20受控目录>
node --max-old-space-size=10000 render_producer_workbook.mjs <9/20/dashboard-plan.json> <9/20受控目录>
python verify_producer_dashboard.py --directory <9/20受控目录> --baseline <9/18受控目录> --native
node render_producer_workbook.mjs <9/20/dashboard-preview-plan.json> <受控预览目录> --preview-only
```

`--reuse-simulation`仅用于同一固定源、同一模型的版式或公式修正；不用于源/概率变化。导出器保留未变的Accepted隐藏页，接回后由原生Excel重算当前master；这不是重跑TASK-0033/0034/0035验收。最终计数、链接、缓存一致性和实际视觉验收见[验证摘要](WORKBOOK_VALIDATION.json)。

## 以下为9/18方案与结构证据（历史）

下文的26页、37源、969检查及当时Unknown描述只记录9/18交付，不覆盖上方9/20新口径。

## 旧资料的结构分析

已通过飞书 CLI 只读检查“系统功能”根及全部子节点：19个页面、17份XLSX附件结构。脚本、视频和采集附件只分类，未执行或作为当前数值输入。旧 `CashRoyal数值.xlsx` 共15个Sheet，宋体11号，常用“左侧配置档位、右侧体验/累计/横向比较”，主要公式习惯为跨Sheet引用、INDEX/MATCH、VLOOKUP、SUMIF/SUMIFS；旧文件有外链，不回存或重算旧附件。

| 旧主表Sheet | 本次沿用的阅读组织 |
|---|---|
| 基础金币、vip加成、BET | 等级/VIP/Bet条件分开，原配置与体验并列 |
| 等级体验表、等级+buff | 业务阶段概览可下钻逐级完整记录；加成独立解释 |
| 旧cr等级、cashFrenzy等级、档位膨胀 | 仅参考横向/累计布局；历史及竞品值不进入计算 |
| 美金金币档位、礼包加成 | 金额、价值类型、VIP类型和等级为独立筛选条件 |
| 卡包、免费奖励 | 条件概率、奖励与累计分开；领取/掉落分母明确 |
| 挖宝、挖宝-基础积分、挖宝-难度系数 | 仅参考阶段成本与奖励布局，不增加9.22活动组合 |

等级沿用的阅读标签为1/10/20/30/40/50/75/100/125/150/300/400/500/600/700/800/900/1000/1100/1200/1400/1600/1800/2000/3000/4000/5000。它们只决定展示节点，不携带旧表奖励、经验、概率或价值参数。另加入当前升级方式、VIP入账、奖励类型/道具和金币换算档位的变化点。连续逐级门槛变化保留明细，不把经验门槛解释成预计Spin或天数。

| 系统功能下的模块 | 已检查内容与本次处理 |
|---|---|
| 数值推导 | 主表15个Sheet，作为布局参考 |
| 免费奖励 | 领取条件/奖励/对比布局，当前福利取r7013 |
| 等级+buff | 多版本22个Sheet，旧倍数/经验不套用 |
| 卡包 | 新旧版本8个Sheet，现值来自r7013卡册/卡包表 |
| 老虎机关联：CR机台建模规范、调控 | 分母/条件分层；调控空页不补证据，不开展程序审计 |
| 疯狂探险 | 两份任务配置与体验附件，映射当前FrenzyMission |
| 竞品调研：弹球公园、tycoon翻地块 | 原始记录/媒体/脚本仅分类，竞品数值不导入 |
| 小游戏：薯片、挖宝、矿工、幸运7、新CR弹球 | 全部子模块及多版本附件已过结构；本次活动只薯片+777 |
| 未命名 | 空页面，明确无内容 |
| 建造 | 9个Sheet及报表结构；沿用已关闭规则，残留不计有效收入 |

## 当前工作簿结构

26张前台页：总览；货币、VIP、BET/RTP、等级、Buff、美金金币档位、福利、商城/Pass、卡包、薯片、777、常驻各有概览和完整明细；Unknown单列。隐藏SRC保存原始格引用、字段注释/坐标及版本清单，CALC保存计算。

- 概览按完整条件或业务阶段分组；36组Spin及各VIP/福利条件完整展示。价格概览按money/priceType/vipType分组，不跨单位平均；薯片/777按相邻相同阶段成本和奖励分组，保留全部变化点。
- 明细保留完整适用配置原行/原字段，包括5000级成长和全部金币价格档位，不删尾部。多个配置段各有筛选表，冻结前6行和首列；等级明细提供阶段分组，概览及总览可跳转。
- `CR_9.22_数值体验表_r7013_MASTER.xlsx`只在受控本机使用。37份实际所需trunk工作簿通过`svn export -r7013 URL@7013`导出；SRC外链直接指向`source/r7013/`原工作簿Sheet/单元格。没有引用working copy、dev/101或旧附件。
- 本工作簿公式或CALC计算派生结果，可沿“体验→CALC→SRC相对外链→源格”追溯。原文件只读，使用原缓存，不重算或保存源表；空值、明确零值、Unknown分别保留。
- `CR_9.22_数值体验表_r7013_飞书展示版.xlsx`从最终master已验证缓存生成，全部数值/文本内嵌，无外链、无公式更新负担，保留筛选/冻结/分组和工作簿内跳转。它是展示快照，不是修改数值或重算的入口。
- 两版使用同一`TASK-0036-r7013-master-display-20260918`版本清单。完整值只留受控包和公司内部飞书；master、原始源包和完整日志不上传。

旧14页候选及其产物评审属于历史。受评文件的公式计数与后续本地候选不同，不用历史计数替代最终XLSX实际计数。当前计数与验证以[WORKBOOK_VALIDATION.json](WORKBOOK_VALIDATION.json)为准。

## 生成与验证方法

生成器位于`projects/cr/数值策划/工具/`：Python负责固定源读取、业务公式/版式计划、外链和验证；`render_producer_workbook.mjs`仅为当前已配置Artifact Tool的渲染适配器。使用已配置运行时的Node、openpyxl（只读源）、lxml（保留OOXML命名空间）及原生Excel COM；不安装新依赖。

```text
python producer_workbook_sources.py --lock <受控source-lock.json> --catalog <WORKBOOK_STRUCTURE.json> --output <受控包目录>
python build_producer_workbook.py --analysis <Accepted分析目录> --sources <受控包目录> --output <受控包目录>
node --max-old-space-size=10000 render_producer_workbook.mjs <workbook-plan.json> <受控包目录>
python verify_producer_workbook.py --plan <workbook-plan.json> --xlsx <MASTER.xlsx> --native --portable-check
node render_producer_workbook.mjs <native-preview-plan.json> <受控预览目录> --preview-only
```

导出阶段保持37个相对源文件与master的目录关系；整个目录一起搬移，不能只发master单文件。版本清单记录导出时间和实际固定revision，不含内部SVN地址。原生Excel保存可能补写绝对路径/作者，因此最后保存后清理元数据，再检查最终ZIP中的XML；不在清理后再次保存master。飞书上传只选择展示版。

本次验证限定于新交付物：原格引用、969个既有结果的工作簿重现、空/零/Unknown及RTP边界、两版缓存一致性、外链解析/搬移、元数据与页面阅读操作。没有重跑TASK-0033/0034/0035的Accepted盘点或模型测试，没有hash、无关全量扫描或原始表重算。完整状态奖EV、成长速度、实付等9组Unknown不因此关闭。

按User本轮禁止无关全量扫描的要求，不运行遍历整个CR库的`build_catalog.py`或`validate_repository.py`；没有增删Git内源工作簿，原目录无需重建。改为本轮Python语法/变更Markdown链接、Git diff及既有Task Registry重建/validator检查。生成器的完整外链/Excel/飞书路径已经在实际交付物运行，不以语法检查冒充端到端。

## 复核与撤回

ChatGPT复核重点为：源版本与相对路径、概览分段是否便于策划阅读、完整明细与原格追溯、展示版与master一致，以及Unknown/计价分母没有改变。原数值Accepted不等于本次工作簿Accepted。

需要撤回时用新的Git更正提交并将本展示版标为历史；不重写共享分支，不覆盖旧附件或原配置。PR #10保持OPEN，reservation pending-main；不调参、不提交SVN、不冻结/发布、不合并或finalize。Subagents: none。
