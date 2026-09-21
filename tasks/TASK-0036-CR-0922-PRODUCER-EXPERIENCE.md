# TASK-0036 — CR 9.22 全项目数值体验与制作人汇报

- Status: Changes Requested
- Execution status: User修订CF币种与VIP膨胀口径；合并曲线候选需修VIP消费门槛证据与商城金币倍率曲线，等待Codex修订后回ChatGPT Review
- Project key: CR
- Owner: User
- Executor: Codex
- Priority: P1 / 9.22制作人汇报
- Date: 2026-09-17
- Updated: 2026-09-21
- User decision: Approved（全项目体验分析与报告；不调参、不改SVN、不冻结、不发布）
- PR: [#10](https://github.com/840832144/AI-Workspace/pull/10)（OPEN；原数值报告Accepted；返还闭环修订等待ChatGPT Review）
- Allocation relationship: new
- Related tasks: TASK-0033, TASK-0034, TASK-0035
- Subagents: none

## Goal

基于TASK-0033全数值底稿、TASK-0034规则闭合及TASK-0035薯片+777现值候选，形成可供制作人决策的全项目数值体验汇报，交ChatGPT Review。不重新盘点或验收已Accepted工作；当前任务只新增体验场景、跨系统解释和必要的变化数据。

## 2026-09-21 — CR/CF VIP口径修订（User新增输入）

- CF截图价格币种确认是**新加坡元SGD/S$**；`VIP_消费门槛`必须保留全部可读商城“价格→VIP点→点/SGD”样本、最低/最高效率来源、每档VIP最低/最高SGD门槛，并保留显式SGD→USD输入用于同轴比较。
- 原`VIP_膨胀系数`的“累计消费门槛/VIP1”定义退出当前展示，改为**商城金币倍率**同口径比较。
- CR r7013正式“商店VIP加成”来自`PriceSetting(currencyType=1,vipType=1)`：VIP0=1x、VIP1=1.25x、VIP2=1.5x、VIP3=1.75x、VIP4=2x、VIP5=2.25x、VIP6–15=2.5x封顶。
- r7013 `VipPrivilege`中确有最高650的其他VIP字段，但不是同口径商城金币，且旧payChipRate被注释为废弃；本页不得用650替代当前PriceSetting商店倍率。
- CF商城金币按截图：黄金2.5x、铂金4x、钛金7x、尊徽10x、百夫长20x、王者风范40x；缺失低档保持N/A，不外推。
- VIP膨胀主图改为`CR商城金币倍率`与`CF商城金币倍率`两条线，Y轴用倍数x，表格同时给百分比。完整细则见[CR_CF_CURVE_COMPARISON](../projects/cr/REPORTS/CR-20260922-PRODUCER-EXPERIENCE/CR_CF_CURVE_COMPARISON.md)。
- 第一动作重建/validate Registry；不改CR配置、历史附件、CF_collect，不采集、不发布、不合并或finalize。

## 2026-09-21 — CR vs Cash Frenzy合并曲线对照（User新增授权）

### 合并候选已交Review

- 已生成受控`CR_vs_CashFrenzy_数值曲线对照.xlsx`，见[脱敏验证摘要](../projects/cr/REPORTS/CR-20260922-PRODUCER-EXPERIENCE/CR_CF_CURVES_VALIDATION.md)。目录：`%LOCALAPPDATA%/AI-Workspace/cr-numerics-20260922/outputs/task0036-cr-cf-20260921/`。
- 固定5页/5原生主折线图/13系列，同指标CR与CF同图；等级主比较1–300，保留CR 4999级成本/返还、5000级Bet与CF完整300级，56个Bet冲突点不插值。来源只读既有曲线缓存，不重算旧模型。
- CF累计点、S$成本上下界及VIP1=100%的单条绝对膨胀已闭合。固定汇率未提供，黄色`VIP_消费门槛!B4`/`CF_SGD_TO_USD`留空；CF两条USD线等待输入，未把S$当USD。原单独CF候选的VIP N/A记录保留为历史。
- 输入缓存/输出逐点、图表范围、原生临时汇率变化并恢复及5页视觉检查通过。0非预期错误/缺缓存/外链/冻结/作者和绝对目录；缺汇率时隐藏图表区14个刻意NA()单列，不能声称零公式错误。完整值/图像不入Git。
- 首步Registry重建/validate为19 canonical、0 collision、valid；收尾由既有工具重建。Workspace Sync ON_DEMAND/provider unavailable/stale 6/conflicts 0。PR #10 OPEN、原reservation pending-main；未改CR/CF_collect/SVN、采集、发布、合并或finalize。Subagents: none。

### 本轮正式输入（保留）

- User提供Cash Frenzy App VIP与商城截图，闭合旧表VIP累计门槛属性，并要求把CR与CF曲线合并到同一Excel、同指标同页同图。
- 完整规格见[CR vs Cash Frenzy合并曲线对照](../projects/cr/REPORTS/CR-20260922-PRODUCER-EXPERIENCE/CR_CF_CURVE_COMPARISON.md)。
- CF VIP累计点门槛按旧表+截图闭合为0/1,000/10,000/31,000/260,000/2.1M/10M/50M；VIP2–7不再因“累计属性未明”标N/A。
- 商城截图兑换范围为18.0401–37.2542 VIP点/S$，VIP消费门槛需输出CF最低成本与最高成本两条边界；不得取平均。
- 绝对膨胀指数中兑换率为常数倍会约掉，因此CF膨胀只画一条线，不重复上下界。
- 合并表固定5页：VIP消费门槛、VIP绝对膨胀、等级升级消耗、等级Bet曲线、等级升级消耗返还；主比较图同页叠加CR/CF。
- 等级类主图使用共同1–300级区间，完整CR 1–4999与CF 1–300数据继续保留；CF已知冲突点不插值。
- 截图商城币种明确为S$；不得静默按USD或1:1。合并表需提供显式S$→USD输入，未获User汇率时不得冒充同单位得出最终金额结论。
- 第一执行动作重建/validate Registry；不修改原截图/历史附件、CR r7013、CF_collect，不采集、不发布、不合并或finalize。

## 2026-09-21 — Cash Frenzy竞品曲线对照表（User已授权）

### 本轮交付：等待ChatGPT Review

- 已按最新规格完成本地 `CashFrenzy_数值曲线对照.xlsx`，受控目录为`%LOCALAPPDATA%/AI-Workspace/cr-numerics-20260922/outputs/task0036-cashfrenzy-20260921/`；[脱敏验证摘要](../projects/cr/REPORTS/CR-20260922-PRODUCER-EXPERIENCE/CASH_FRENZY_CURVES_VALIDATION.md)。5页同名同序、5张原生折线图，300级完整明细，无冻结/外链。
- 只用旧总表CF区块，不混另一版竞品附件、CR或运行数据。VIP0–7全部保留；VIP1=100%，VIP2–7因累计属性未明标N/A。普通最大Bet与$1等值同图同单位；56个源表内部冲突等级的最大Bet为N/A，highroller条件缺口明确保留。
- 本轮来源复算、输出逐点、原生驱动变化并还原、图表点数和5页视觉验收通过；0公式错误/缺缓存/作者及绝对路径元数据。第一步Registry重建/validate为19 canonical、0 collision、valid；收尾继续由工具重建。
- Workspace Sync为ON_DEMAND/provider unavailable/stale 6/conflicts 0，不冒充外部同步。完整数值/原附件/预览留本机，不上传。无hash或无关全量重跑；PR #10 OPEN、原reservation pending-main，不合并或finalize。Subagents: none。

### 原授权规格（保留）

- 继续现有TASK-0036，不新建Task：该交付与当前CR数值整理/制作人曲线展示范围直接重叠。
- 完整规格见[Cash Frenzy竞品数值曲线对照表](../projects/cr/REPORTS/CR-20260922-PRODUCER-EXPERIENCE/CASH_FRENZY_CURVE_COMPARISON.md)。
- 目标：基于历史正式数值体验资料中的Cash Frenzy竞品数据，生成与当前CR曲线表v2同构的独立Excel，方便逐页并排比较；不把CR和竞品强行混在同图。
- 可见页固定5张：`VIP_消费门槛`、`VIP_膨胀系数`、`等级_升级消耗`、`等级_Bet曲线`、`等级_升级消耗返还`，全部折线图。
- VIP膨胀口径为绝对指数（VIP1=100%），不是相邻环比；最大Bet和$1等值推荐Bet必须同页同图。
- 首选旧`CashRoyal数值.xlsx`的`cashFrenzy等级`及同套历史竞品资料。不得用CR r7013或CR 95% RTP等规则填补Cash Frenzy缺口；来源不足则明确N/A/缺失字段。
- 本任务只整理已有竞品数据，不修改原附件、不改CR配置、不修改CF_collect、不启动Collector/模拟器/Root/Frida、不采集或Web补数。
- Task状态切为Changes Requested后Registry需由Codex使用既有工具重建/validate，禁止手工编辑Registry；完成后提交受控Excel与脱敏验证摘要交ChatGPT Review。

## 2026-09-20 — 返还闭环修订完成，交ChatGPT Review

- User后续决定已落实：总览及12张模块概览完全取消冻结（行/列均0），明细仍保留前6行/首列。双版本和受控ZIP同步；WPS只读回读13个概览均无冻结且滚动40→1行通过。仅修改视图，数值/公式/链接/页签顺序未变，未重算。
- User后续阅读调整：双版本统一为总览及12个模块概览在前、12个模块明细在后，最后保留关闭/历史配置与Unknown；隐藏源/计算页仍隐藏。已同步生成器及受控ZIP，定向验证仅页签元数据变化，数值、公式、样式和链接不变；不重算。
- 安全同步PR原分支至`1be0b64208892fa246eb15b95d14e618d6f8be39`后，第一步使用既有CLI重建并验证Registry：19 canonical、0 collision、valid；无新Task或reservation。
- 按[Dashboard Round 1](../reviews/TASK-0036-CHATGPT-DASHBOARD-REVIEW-1.md)完成等级阶段/累计、VIP礼包、商城支付与Pass玩法、777圈级/三轮的返还闭环。分母分别为机器理论净耗、充值/支付或明确分栏的综合成本；免费福利、货币基准、Buff权益为N/A。
- 卡册同版模型运行到章/整册完成，6000条完成记录；理论完成期望与赛季内完成率分列，整册取同路径终点。薯片复用原随机路径，11个目标的部分/全部路径超自然160上限，明确“自然渠道不可达”，另列两条当前SKU补包成本。没有重跑0033/0034/0035或旧969项验收。
- 777圈层按奖励实际取得时归属；库存结转使个别圈新增机器净耗为0时，返还率为“N/A：本圈新增净耗为0”，不误称无付费抽奖。常驻仅定向核对13项物品身份，获取成本/启用仍未闭合，不计入已完成经济结论。
- 受控当前目录：`%LOCALAPPDATA%/AI-Workspace/cr-numerics-20260922/producer-return-loop-20260920/`。MASTER与44份固定r7013相对源整包使用；展示版0公式/0外链。完整商业值、模拟明细和源文件不进Git。9/18飞书副本及下方旧Dashboard记录均为历史，本轮未上传云端。
- 896项返还闭环定向检查通过；源格、双版本、公式错误、缺缓存、作者/绝对路径差异均0；44条外链原生解析、VIP驱动变化并还原通过。27张前台保留完整细节，13张概览、4组新增子表和24张原生图表已视觉复核。最后仅修正文本标签，并验证未改变数值/公式运算。
- 详见[返还闭环报告](../projects/cr/REPORTS/CR-20260922-PRODUCER-EXPERIENCE/RETURN_LOOP.md)和[验证摘要](../projects/cr/REPORTS/CR-20260922-PRODUCER-EXPERIENCE/WORKBOOK_VALIDATION.json)。当前为Review，不自行Accepted；9组解释边界保留，卡册样本期望仍为Estimate。
- Workspace Sync：ON_DEMAND/provider unavailable/stale 6/conflicts 0，未宣称外部Context同步。PR #10保持OPEN，原reservation pending-main；不调参、不改/提交SVN、不冻结/发布、不合并或finalize。Subagents: none。

## 历史输入 — 2026-09-20 Dashboard Round 1 Needs changes：返还闭环补全

[Dashboard Review Round 1](../reviews/TASK-0036-CHATGPT-DASHBOARD-REVIEW-1.md) 已评审 `5ddb642925ae85ded6bc262a03b038c9504164a1`。本轮不重做已Accepted底稿，重点只补齐制作人汇报闭环。

- 所有真正有消费/成长/活动闭环的当前有效模块，概览必须统一回答：**机器理论净耗$ → 可计价返还$ → 返还率% → 净成本$ → 阶段/最终完成成本$**。
- 等级补阶段/累计返还率；VIP补本级/累计礼包返还率；BET/RTP同时展示机器返还率与净耗率；商城改用支付返还率%，薯片Pass与普通SKU拆分；777补圈级返还率/净成本与三轮总通关。
- 卡包将“理论完成期望”与“赛季内完成率”拆开：理论模型跑到章节/整册完成，季末只作为完成率/超期风险，不再用删失直接把期望成本写Unknown；整册必须由完整状态模拟直接得到。
- 薯片自然来源超过160写“自然渠道不可达”；自然区间保留真实返还率，超过上限的Pass/Grand展示缺口道具和补充渠道成本，不允许把自然单价无限外推。
- 福利/货币等无统一消费分母的模块返还率使用N/A并说明“免费投放/价值基准”；Buff并入实际权益模块；常驻无法闭合时明确“待启用确认/成本未闭合”，不能与已完成经济模块并列。
- 当前审查证据：卡包60行中39行返还率非数值；薯片21行中11行返还率非数值；等级/VIP已有成本与奖励但缺阶段返还率；777轮级已完成但圈级缺失。
- 修订后需更新Dashboard与各模块概览、定向验证返还公式/模型闭合、重做视觉复核；master仍使用r7013相对外链，展示版0外链且关键输出与master一致。
- 第一执行动作仍为按既有工具重建/验证Registry以同步Changes Requested；禁止手工编辑Registry。不调参、不改/提交SVN、不冻结/发布、不合并或finalize。

## 2026-09-20 — TASK-0036制作人Dashboard候选完成，交ChatGPT Review

- 按最新Task规格重构r7013双版本Excel；原数值报告Accepted保留，新Dashboard/模拟本身为Review。继续原PR #10与原reservation，不新建Task。起点安全同步e306145，首先按既有工具重建/验证Registry：19 canonical、0 collision、valid。
- 27张前台含Dashboard、12组概览/完整明细、关闭索引与9组Unknown；13张概览、24张原生Excel图表已视觉核对。保留5000级、4999条升级奖励、7236条价格原配置；不重做0033/0034/0035 Accepted底稿。
- 固定r7013原始导出源44份，MASTER相对外链44条；完整商业值仅留受控目录`%LOCALAPPDATA%/AI-Workspace/cr-numerics-20260922/producer-dashboard-20260920/`。展示版为无外链缓存快照。本轮未上传云端，9/18飞书链接是历史副本。
- 原生重算后36项新增关键输出通过；机型/VIP驱动变化后已还原，源格/双版本差异、公式错误、缺缓存、作者/绝对路径均0。MASTER实际1,625,084公式，展示版0公式/0外链；93个筛选表、27页冻结，完整长表分组与跳转保留。最终计数见WORKBOOK_VALIDATION.json。
- 已还原最大解锁Bet、等级经验与95%成本、VIP100点/$、当前价值换算；卡册逐章状态模型、薯片20盒/JP/Pass、777普通/特殊/圈/轮成本已形成。旧BET/卡包正式表只复用公式关系与阅读方式，旧值未入r7013。
- Review重点：显式机型列参考、卡册季末删失、薯片自然获取封顶、潜在奖励与已实现返还分开、777按User内圈口径与当前代码差异。通用VIP Pass字段未证实适用于薯片，已移历史索引；商品按实际薯片礼包/Pass表关联，不补0。9组Unknown仍保留，未新增冻结Gate。
- Workspace Sync仍为ON_DEMAND/provider unavailable/stale 6/conflicts 0；不冒充外部Context已同步。Git只保存方法/生成器/脱敏验证和治理；没有hash、全量无关扫描或旧Task重复验收。
- PR #10保持OPEN，原reservation pending-main，等待ChatGPT Review；不调参、不修改/提交SVN、不冻结/发布、不合并或finalize。Subagents: none。

## 2026-09-20 — 制作人汇报型Excel重构（User已授权执行）

本轮不再以“配置核对正确”为终点，而以“制作人/策划可直接汇报当前版本数值体验”为验收终点。继续复用r7013受控master的真实trunk相对外链证据链；数值结论、9组Unknown与已Accepted历史不因展示重构而自动改变。

### 总体交付

1. 本地受控 `CR_9.22_数值体验表_r7013_MASTER.xlsx` 继续作为可追溯master，直接引用固定r7013原始工作簿相对路径；禁止working copy、dev/101、旧附件或绝对本机路径。
2. 每个有效模块保持“概览 + 明细”双层。概览是汇报页，明细保留完整配置/公式/源格追溯。
3. 总览改为制作人Dashboard，不再以36组Spin技术场景为首页主体。按模块给：一句话作用、关键阶段、机器理论净耗USD、可计价返还USD、净成本、返还率、阶段膨胀、最终通关/完成总成本、关键Unknown。
4. 36组Spin、源字段、BetIndex、levelUpExp、probability等技术/配置语言下沉到明细、SRC、CALC、来源列或批注；前台统一使用策划语义。
5. 概览统一视觉：成本/消耗橙红、奖励/返还绿色、成长/权益蓝紫、Unknown黄色/灰色；美元2位、比例1位%、倍数x、金币K/M/B。每模块概览至少包含3~6个KPI、阶段表和1~2张有决策意义的趋势/成本返还图。
6. master验证后生成无外链飞书展示版；展示版必须与master关键输出一致，不上传master、r7013源包、内部路径或受控日志。

### 全局业务口径

- “消耗美金”主指标统一为**机器理论净耗USD**，即毛下注USD×(1-RTP)；毛下注仅作辅助过程指标。
- 常规老虎机仍按User规则：USD Bet≤1为95%，>1为85%；**等级升级成本专项统一按95% RTP**。
- 普通金币按当前等级/VIP的金币美元档折算；rewardType=17美金金币按配置美金价值；礼包金币type=9与rewardType=17同口径；钻石按当前商店购买钻石兑换比例折USD。
- 模块核心道具的基础单位价值只按“老虎机自然获取该道具所需机器理论净耗USD÷获取数量”计算；礼包、Pass、赠送等渠道不改变基础单价，只单独展示投放溢价。
- 模块“总返还”按当前有效的基础奖励 + 阶段奖励 + 最终/通关奖励汇总；同时保留分层拆解。总返还率=总可计价奖励USD/完成该模块所需机器理论净耗USD。
- 不能可靠美元计价的资源分账展示，不强行塞入总返还；Confirmed / Estimate / Unknown必须明确。
- 福利按各自真实周期展示，不强行统一日/周。
- 当前有效Pass仅薯片Pass；其他BP/Pass不计入当前版本。建造、比赛/牌桌、Spades、联盟、赛马/龙虎、马戏团、轮盘当前均关闭，不纳入有效产出/返还。Buff页需逐项映射启用模块，League/关闭模块Buff移到“关闭/历史配置”，仍有效Buff才保留。

### 等级

- 汇报终点是“升级成本与膨胀”，不是原门槛数字。
- 推荐Bet规则：每一等级/行使用**当前已解锁的最大Bet**；先从旧云端BET体验逻辑及r7013正式配置还原，不得继续静默固定bet2。
- `LevelCfg.levelUpExp` 是升级门槛且按设计不可为空；发现空值必须报配置异常，不得补值。
- `levelUpType=1`按Spin次数；`levelUpType=0`或空值按经验升级。
- 经验型升级使用推荐Bet对应 `SlotsCasinoBetList.levelExp` 换算预计Spin；升级后立即切新等级档；VIP不提供等级经验加成。
- 需要输出：等级段、推荐Bet($)、每Spin等级经验、阶段升级总经验/Spin门槛、预计Spin、毛下注$、机器理论净耗$、升级奖励$、净升级成本$、相对上一阶段成本膨胀、累计成本$。
- 等级阶段概览沿用旧表1/10/20/30/40/50/75/100/125/150/.../5000阅读节点并补r7013实际配置变化点；完整逐级数据保留明细。
- 若经验溢出是否跨级继承等实现语义在旧正式表/当前代码/配置中无法唯一还原，只报告一个具体 blocker，不自行假设。

### VIP / 权益

- VIP经验只来自充值；分析口径固定 **$1 = 100 VIP点**。
- 输出VIP段、增量/累计VIP点、升级等价美元成本、升级礼包可计价价值、净升级成本、任务/成就/经验/兑换等关键权益增量%、成本膨胀与权益膨胀。
- 不从Spin或LevelAward推导VIP购买成本；商品投放中的VIP点只用于验证$1=100点和实际SKU一致性。
- 权益无法美元化时用权益提升%/倍率表达，不强行估值。

### BET / RTP、货币、福利、商城

- BET/RTP：展示等级/VIP下最大已解锁推荐Bet变化，100/500/1000Spin的毛下注与机器理论净耗，以及95%→85%档位变化。
- 货币/美金金币：重点展示各等级/VIP的$1金币量、相邻阶段膨胀倍数与代表价格档；全量价格配置放明细。
- 福利/任务：按各自领取/刷新周期展示可计价价值、相当于多少机器净耗回补、阶段/解锁门槛；互斥方案不得叠加。
- 商城：展示价格、明确可计价总奖励、回报倍数、VIP点；混合资源分账。
- 薯片Pass：展示价格/可计价奖励、共享门槛、追领价值、完成预计Spin/机器理论净耗；除薯片Pass外其他Pass当前关闭。

### 卡包 / 卡册

- 目标不是“掉卡事件数”，而是**每章与整册的期望成本和返还**。
- 默认分析从空卡册、赛季第一天开始。优先复用旧 `卡包数值调整.xlsx` 已定义的玩家档位与模拟逻辑；旧数值不得作为输入。若旧表没有正式分档，再使用低/中/高代表玩家档（当前等级/VIP/推荐Bet）。
- 每章分别输出：章节/完成条件、预计Spin、推荐Bet、机器理论净耗$、章节奖励可计价$、章节返还率、章节净成本$、相对上一章成本膨胀。
- 整册输出：累计预计Spin、累计机器理论净耗$、全部章节+整册/赛季奖励$、总体返还率、总体净成本/预计总消耗$。
- 每100/500/1000Spin掉包/掉卡仅作为获取效率过程指标，下沉到次级表。
- 必须按CardChapter/CardAlbumCfg/CardPack/SlotsCasinoDropCards实际章节、卡池、包组成、掉落概率和阶段条件分别模拟，不得用整册平均卡数均摊章节。
- 重复卡/稀有度/控制/完成概率逻辑优先从旧正式卡包表与当前r7013还原；无法唯一确定时拆为Confirmed/Estimate/Unknown，并显式展示假设，不伪造完整期望。

### 薯片

- 初始活动道具=0；可用盒子初始满额20个。
- 每次开奖消耗1个薯片；普通开奖后可用盒子-1；重置效果恢复至20；Jackpot状态完成后清零并可重复。
- 在多个老虎机净耗区间（由当前配置分布选代表段）展示：预计薯片获取、基础单位价值、活动基础/阶段/Jackpot/薯片Pass奖励分层、阶段完成度、阶段/最终通关机器理论净耗$、总返还率、净成本。
- 薯片单位价值仅来自老虎机自然获取成本，活动内奖励不参与该单价定义。

### 777

- 沿用Accepted forceTurn：当前圈付费抽奖计数，普通格N前未自然命中则第N次强制；提前命中取消；换圈/轮重置；特殊格不参与forceTurn。
- 特殊格命中后临时进入内圈，从**当前尚未消失的内圈格**随机取得一个奖励；被取得的内圈普通格随之消失；之后返回原圈继续付费抽。
- 需要真正跑出普通格/特殊格/圈/轮/最终完成的期望骰子消耗、对应老虎机机器理论净耗$、基础/阶段/终局奖励$、总返还率和净成本，而不是只展示道具获取概率。

### 常驻与关闭模块

- 当前关闭：建造、比赛/牌桌、Spades、联盟、赛马/龙虎、马戏团、轮盘；不得出现在首页“当前有效模块”的成本/返还中。
- 当前仍有效的常驻系统按“解锁/参与成本→核心奖励/权益→阶段终点”汇报。
- 关闭模块可保留一张简洁“关闭/不计入经济”说明或明细索引，不能让制作人误以为本版生效。

### 验收

- master继续使用r7013相对外链，必须0绝对路径、0作者/本机敏感元数据；源工作簿只读，不修改/保存。
- 关键制作人指标必须可沿“概览→CALC→SRC相对外链→r7013源格”追溯；前台不得手填派生结果。
- 对新计算增加定向回归：最大已解锁Bet、levelExp→预计Spin、95%升级成本、VIP $1=100点、资源美元换算、卡册章节模拟、薯片20盒重置、777特殊内圈消格、模块总返还分层。
- 无公式错误/缺缓存；展示版0外链，关键输出与master一致；对所有概览页做视觉复核。
- 不重跑TASK-0033/0034/0035无关全量验收，不做无意义hash/全仓扫描。
- 如果旧正式测算表和r7013仍无法唯一解释某个业务规则，只回报具体规则+受影响指标，不用配置字段原样堆到前台，也不自行补值。
- 完整商业数值、master和源包继续受控；public Git只放生成器、结构说明、脱敏验证、Task/Review/Handoff。


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
