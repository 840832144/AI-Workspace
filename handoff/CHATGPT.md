# ChatGPT Handoff

## 2026-09-21 — TASK-0036 POP/CF调优候选交Review（当前）

- 当前Review，PR #10 OPEN；原报告Accepted不扩展为本轮候选Accepted。受控目录为 `outputs/task0036-tuning-pop-cf-20260921/`，完整交付及验证见下方报告链接。
- VIP1–10为指定值，11–15按User选择的POP高阶趋势，以VIP10为锚点拟合Tier6–10后外推。仅VipCfg的15个needExp格改变，严格单调/int32范围通过，权益不变；VIP1=0登录校正与加0经验入口行为不同，客户端/服务端未运行验证，安全Gate未通过。
- LevelCfg未改：历史正式表未恢复唯一CF→5000映射，只交A全段拉伸/B保留前100级两套体验方案。PriceSetting未改：30档可保形归一100%→500%，但旧服务已废弃，现有取值指向PriceCheatSheet，制作生成链未证实；928格仅拟议diff。
- 等级膨胀1–300逐级一致，No Change；301–5000缺CF证据，保留CR现值。8可见页/7原生折线图，5000级完整明细、15/0/0实际改格、公式/锚点响应及前台视觉通过；0错误/缺缓存/外链/冻结。
- 需Review/后续确认：VIP零门槛安全、两套等级映射选择、正确价格制作源。当前不是可直接导入/冻结的配置包。
- Registry首步/收尾均由CLI重建validate；Workspace Sync ON_DEMAND/provider unavailable/stale 6/conflicts 0。未重跑旧Accepted模型、hash或全量扫描；未改r7013/SVN/CF_collect、采集、冻结/发布、合并/finalize，原reservation pending-main。Subagents: none。

[当前候选、证据与复现](../projects/cr/REPORTS/CR-20260922-PRODUCER-EXPERIENCE/CR_TUNING_VALIDATION.md)。

## 2026-09-21 — TASK-0036档位膨胀最终口径

- User纠正：档位膨胀=最低100%→最高500%的整体曲线，最高/最低=5x；**不是相邻档5x**。
- 中间档位单调升高；优先按当前/旧档位相对形状归一到100%→500%，不得默认等差。无法唯一恢复时只出“保形归一/线性”两套候选，不写PriceSetting。
- 其他调优范围不变；仍只做受控候选，不提交SVN、不冻结/发布。

## 2026-09-21 — TASK-0036 CR数值调优候选

- User已授权从展示进入定向调优候选；完整规格见[CR_TUNING_POP_CF](../projects/cr/REPORTS/CR-20260922-PRODUCER-EXPERIENCE/CR_TUNING_POP_CF.md)。
- POP只对标VIP消费门槛；CR VIP1–10目标needExp候选0/94/375/2000/6875/27500/75000/312500/937500/2500000，VIP1=0先验证升级逻辑安全；VIP权益不改。
- 升级难度复用历史CF→CR映射扩5000级；等级膨胀只验证预期No Change；档位膨胀相邻业务档5x，定向PriceSetting且禁止全表×5。
- 允许改受控候选VipCfg/LevelCfg/PriceSetting，但不得SVN commit、覆盖r7013、冻结或发布。第一步重建/validate Registry，完成后交diff+新曲线Excel。

## 历史候选 — 2026-09-21 TASK-0036固定汇率/商城金币倍率交Review

- 同一Task/原PR #10；当前Review。[交付目录、来源与验证](../projects/cr/REPORTS/CR-20260922-PRODUCER-EXPERIENCE/CR_CF_CURVES_VALIDATION.md)。新候选在受控`outputs/task0036-cr-cf-fixed-vip-20260921/`，旧合并候选为历史。
- CF前台统一VIP1–VIP7；1 SGD=0.78408 USD固定，无可编辑输入；SGD原始上下界、USD两条成本线和九个商城样本完整。倍率页改为商城金币：CR最高2.5x、CF最高40x；旧累计消费门槛指数已删除。
- CR倍率只读r7013 PriceSetting商店金币行；CF VIP1=1.5x由旧正式表唯一补齐并注明历史，VIP2–7依已登记截图口径。未独立复读App截图，不冒充新的现网验证。
- 5页/5原生图/13系列，成本15/7/7点、倍率16/7点；既有等级缓存不变，完整明细和56个CF Bet缺口保留。公式错误/缺缓存/外链/冻结/作者及绝对目录均0，五页视觉通过；独立ChatGPT Review尚未执行。
- Registry首步及收尾均用既有工具重建validate，19 canonical/0 collision/valid；Workspace Sync ON_DEMAND/provider unavailable/stale 6/conflicts 0。PR #10 OPEN、reservation pending-main；不改源数据/CR/CF_collect、不采集、无hash或全量重跑、不提交SVN、不冻结/发布、不合并/finalize。Subagents: none。

## 历史输入 — 2026-09-21 TASK-0036 CF标签与固定汇率

- User最终决定：CF前台统一VIP1–VIP7，不显示称号；固定分析汇率 **1 SGD = 0.78408 USD**（2026-09-21 02:24 UTC），不再保留可编辑汇率输入。
- CF VIP消费门槛保留SGD原始上下界并按×0.78408生成USD上下界；点数兑换边界18.0401–37.2542点/SGD不变。
- VIP膨胀继续按商城金币倍率：CR r7013 PriceSetting最高2.5x，CF最高40x。
- Task已Changes Requested；先重建/validate Registry，再修订合并Excel并做定向验证，不改源数据、不采集、不发布。

## 历史输入 — 2026-09-21 TASK-0036 CR/CF VIP曲线修订

- User确认CF商城截图为SGD/S$；VIP消费门槛需补全9个可读商城样本、点/SGD上下界、每档VIP最低/最高SGD门槛及显式SGD→USD输入。
- VIP膨胀改成商城金币倍率：CR用r7013 PriceSetting商店VIP加成（1x→2.5x封顶），CF用截图2.5x/4x/7x/10x/20x/40x；旧累计门槛指数退出当前展示。
- 650是CR其他/旧VIP字段，不是同口径商城金币；不要混用。第一步重建Registry，修订合并Excel后回Review。

## 历史候选 — 2026-09-21 TASK-0036合并曲线待Review

- 已提交本地受控`CR_vs_CashFrenzy_数值曲线对照.xlsx`，Task为Review；[脱敏验证摘要](../projects/cr/REPORTS/CR-20260922-PRODUCER-EXPERIENCE/CR_CF_CURVES_VALIDATION.md)。5页同指标同主折线图，等级1–300比较且完整数据保留。
- Review重点：本轮User正式输入已闭合CF累计VIP点；消费边界按最高/最低点/S$分别推最低/最高成本；CF绝对膨胀只一条线。固定S$→USD未提供，黄色输入留空，不作最终美元成本结论。
- 原生测试确认填入汇率后CF两条USD线响应，绝对指数不变，测试后恢复空白。当前该图实际点数15/0/0，其余图点数见摘要；14个刻意绘图NA()显式记录，非预期错误/缺缓存均0。56个CF Bet冲突点仍断线。
- 既有模型缓存原样复用，无重跑；五页视觉、输出定向验证、Registry重建validate完成。PR #10 OPEN、原reservation pending-main；不改CR/SVN/CF_collect、采集、发布、合并或finalize。Subagents: none。

## 历史输入 — 2026-09-21 CR vs Cash Frenzy合并曲线

- User补充CF App VIP/商城截图并要求把CR与CF合并到同一曲线Excel；Task已切Changes Requested。完整规格：[CR_CF_CURVE_COMPARISON](../projects/cr/REPORTS/CR-20260922-PRODUCER-EXPERIENCE/CR_CF_CURVE_COMPARISON.md)。
- CF累计VIP点现闭合为0/1k/10k/31k/260k/2.1m/10m/50m；商城兑换上下界18.0401–37.2542点/S$。
- 输出5页同指标CR/CF同图；VIP消费门槛画CF最低/最高成本，VIP绝对膨胀只画一条CF线；等级主比较1–300并保留完整数据。
- S$不得冒充USD；做显式S$→USD输入。第一步重建/validate Registry；不改CR、CF_collect、历史附件，不采集、不发布。

## 2026-09-21 — TASK-0036 Cash Frenzy曲线等待轻量Review

- 当前Review。新增本地受控`CashFrenzy_数值曲线对照.xlsx`与[脱敏验证摘要](../projects/cr/REPORTS/CR-20260922-PRODUCER-EXPERIENCE/CASH_FRENZY_CURVES_VALIDATION.md)，完整值仅在本机。5页同名同序、全部原生折线图、300级完整成本/返还、最大Bet与$1等值同图同单位，0冻结。
- Review重点：VIP1=100%的绝对口径；VIP2–7因原经验未注明累计/本级而N/A；普通最大Bet244个一致点、56个源表冲突留空；highroller条件未明，不能当全模式绝对上限。另一版同套附件不混用，CF曲线不套CR RTP/币值。
- 原表缓存复算、前台逐点、原生驱动变化并还原、图表缓存点数和五页视觉检查通过；0公式错误/缺缓存/外链/作者及绝对路径。Registry已由CLI重建并验证，非手工编辑。
- PR #10 OPEN，原reservation pending-main；原CR返还闭环候选及Accepted报告保持。无hash/全量扫描、源附件改写、SVN/CF_collect修改、上传发布、合并或finalize。Subagents: none。

## 历史输入 — 2026-09-21 Cash Frenzy竞品曲线对照

- User已授权继续现有TASK-0036新增Cash Frenzy同构曲线Excel；Task已切Changes Requested，完整规格见[竞品曲线规格](../projects/cr/REPORTS/CR-20260922-PRODUCER-EXPERIENCE/CASH_FRENZY_CURVE_COMPARISON.md)。
- 首选历史正式数值体验资料的旧`CashRoyal数值.xlsx` / `cashFrenzy等级`及同套竞品数据；缺失字段不得借CR规则补齐。
- 可见5页与CR v2一一对应，全部折线图；VIP膨胀=绝对指数(VIP1=100%)；最大Bet与$1等值推荐Bet同页同图。
- 第一动作重建/validate Registry；只生成本地受控Excel+脱敏验证，不修改CR r7013、CF_collect或历史附件，不启动Collector/模拟器/Root/Frida，不发布。

## 2026-09-20 — TASK-0036返还闭环修订待复核（当前）

- User后续决定已落实：总览及12张模块概览完全取消冻结（行/列均0），明细仍保留前6行/首列。双版本和受控ZIP同步；WPS只读回读13个概览均无冻结且滚动40→1行通过。仅修改视图，数值/公式/链接/页签顺序未变，未重算。
- User后续要求的页签排序已落实：总览与12个概览在前，12个明细在后，关闭/历史与Unknown置末。双版本及受控ZIP已更新；只有页签元数据变化，数值/公式/样式/链接不变，未重算。
- Task已回到Review，继续原PR #10（OPEN）和reservation pending-main；原数值报告Accepted、Dashboard Round 1 Needs changes保留。[修订逐项说明](../projects/cr/REPORTS/CR-20260922-PRODUCER-EXPERIENCE/RETURN_LOOP.md) · [实际验证摘要](../projects/cr/REPORTS/CR-20260922-PRODUCER-EXPERIENCE/WORKBOOK_VALIDATION.json)。Registry已由既有CLI重建验证，无新Task。
- 请复核分母与终点：等级/卡册/777用机器理论净耗；VIP与普通商品用充值/支付；薯片补包和Pass分别列机器净耗、补包及Pass支付。免费福利/货币无分母为N/A，Buff归权益，常驻待启用确认/成本未闭合不作为已完成经济结论。
- 卡册理论模型6000条章/册记录全部完成，季内完成率另列，整册直接取同路径终点；固定日Spin/UID等仍是Estimate。薯片11个目标含自然不可达路径，已列上限内实际返还、缺口与两种当前SKU补包成本，不能把自然单价外推或把潜在奖当已得奖。
- 777圈级按实际奖归属，三轮总成本/返还独立汇总；零新增机器成本来自库存结转，返还率N/A而非无付费抽奖。User内圈分析口径与当前代码差异未被消除，也没有程序审计。
- 当前双版本位于受控`producer-return-loop-20260920/`：44相对外链MASTER与0外链展示版；896项定向检查、源格/双版本一致性、13概览/4子表/24原生图表视觉复核通过。完整商业明细仅在受控ZIP，Git是方法和脱敏结果；旧云端链接没有替换，不能拿历史附件复核当前版。
- Workspace Sync provider unavailable；9组解释边界保留，尚未冻结或发布。没有重跑0033/0034/0035、hash、调参、SVN写入、合并或finalize。Subagents: none。

## 历史输入 — 2026-09-20 TASK-0036返还闭环补全

- Dashboard Round 1对`5ddb642`结论为Needs changes；完整阻塞见[Review](../reviews/TASK-0036-CHATGPT-DASHBOARD-REVIEW-1.md)与canonical Task最新章节。
- 目标不是继续加配置字段，而是把当前有效消费/成长/活动模块统一补齐“机器理论净耗$→返还$→返还率%→净成本$→最终完成成本$”。
- 等级/VIP/商城/777补已有输入可直接计算的返还率；卡包拆理论完成期望与赛季完成率；薯片拆自然不可达与补充渠道；福利/货币用N/A；Buff并入权益；常驻未闭合项明确状态。
- 执行前先重建/验证Task Registry；继续r7013相对外链master与0外链展示版，不重跑0033/0034/0035全量，不调参、不改SVN、不冻结/发布、不合并或finalize。

## 2026-09-20 — TASK-0036制作人Dashboard候选完成，交ChatGPT Review

- 按最新Task规格重构r7013双版本Excel；原数值报告Accepted保留，新Dashboard/模拟本身为Review。继续原PR #10与原reservation，不新建Task。起点安全同步e306145，首先按既有工具重建/验证Registry：19 canonical、0 collision、valid。
- 27张前台含Dashboard、12组概览/完整明细、关闭索引与9组Unknown；13张概览、24张原生Excel图表已视觉核对。保留5000级、4999条升级奖励、7236条价格原配置；不重做0033/0034/0035 Accepted底稿。
- 固定r7013原始导出源44份，MASTER相对外链44条；完整商业值仅留受控目录`%LOCALAPPDATA%/AI-Workspace/cr-numerics-20260922/producer-dashboard-20260920/`。展示版为无外链缓存快照。本轮未上传云端，9/18飞书链接是历史副本。
- 原生重算后36项新增关键输出通过；机型/VIP驱动变化后已还原，源格/双版本差异、公式错误、缺缓存、作者/绝对路径均0。MASTER实际1,625,084公式，展示版0公式/0外链；93个筛选表、27页冻结，完整长表分组与跳转保留。最终计数见WORKBOOK_VALIDATION.json。
- 已还原最大解锁Bet、等级经验与95%成本、VIP100点/$、当前价值换算；卡册逐章状态模型、薯片20盒/JP/Pass、777普通/特殊/圈/轮成本已形成。旧BET/卡包正式表只复用公式关系与阅读方式，旧值未入r7013。
- Review重点：显式机型列参考、卡册季末删失、薯片自然获取封顶、潜在奖励与已实现返还分开、777按User内圈口径与当前代码差异。通用VIP Pass字段未证实适用于薯片，已移历史索引；商品按实际薯片礼包/Pass表关联，不补0。9组Unknown仍保留，未新增冻结Gate。
- Workspace Sync仍为ON_DEMAND/provider unavailable/stale 6/conflicts 0；不冒充外部Context已同步。Git只保存方法/生成器/脱敏验证和治理；没有hash、全量无关扫描或旧Task重复验收。
- PR #10保持OPEN，原reservation pending-main，等待ChatGPT Review；不调参、不修改/提交SVN、不冻结/发布、不合并或finalize。Subagents: none。

## 2026-09-20 — TASK-0036制作人汇报型Excel重构执行入口

- User已授权继续现有TASK-0036，不新建Task；Task已切到Changes Requested。执行前先同步当前PR #10分支并读取Task最新2026-09-20规格。
- 核心目标：把r7013双版本Excel从技术/配置核对表升级为制作人可直接汇报的Dashboard；保持“概览+完整明细”和r7013相对外链证据链。
- 已闭合业务口径：成本=机器理论净耗USD；等级95%RTP+最大已解锁Bet+levelExp；VIP $1=100点；模块道具价值只按老虎机自然获取成本；总返还按基础/阶段/终局分层；卡册按章/整册；薯片20盒；777特殊内圈消格；关闭模块不纳入经济总览。
- 第一执行动作：重建/验证Task Registry以同步Changes Requested状态；禁止手工编辑Registry。随后只做定向生成/验证，不重跑0033/0034/0035全量。
- 不调参、不修改/提交SVN、不冻结/发布、不合并PR #10、不finalize；完成后更新Task/Status/Handoff/Registry并返回commit和受控产物交ChatGPT Review。

## 2026-09-18 — TASK-0036双版本Excel完成，等待ChatGPT Review

- 按PR #10最新User输入形成相对外链master与无外链飞书展示版；原数值报告Round 1 Accepted保留，本次Excel仍为Review。前版14页产物的Needs changes与旧自包含方案保留为历史。
- [当前飞书展示版](https://gfok27asqq.feishu.cn/wiki/UZD8wLpQKicKV7kcorIcNIb8nwd)；原旧表及前版候选未覆盖。Git/TASK-0036与本机受控master是真相源，飞书是展示快照。公司内链接可读、external access closed，未修改ACL或开启公网分享。
- 37份原始trunk工作簿定向`svn export -r7013`导出；26张前台含12组概览/明细、总览和Unknown。等级5000行及升级奖励4999行、价格7236行完整保留；104个筛选表、26页冻结前6行/首列，等级分组和内页跳转。
- 最终master 1,062,421公式、37条相对外链；展示版0公式/0外链。969个关键输出与Accepted底稿一致，两个版本逐格一致，源格缓存一致；公式错误/缺缓存/作者或绝对路径检查为0。搬移后37条链接解析、代表源格刷新及原生窗格回读通过；26页视觉复核。飞书下载回读969项通过。
- 完整文件、相对源包、版本清单和验证证据位于受控`producer-master-20260918/`；公开Git仅工具、结构、方法、脱敏验证与交接。旧Wiki系统功能19页/17份XLSX子模块结构已检查，旧值没有入当前计算。
- 9组Unknown保留，未重跑旧Task模型/全量配置盘点或hash；未重算或修改源表。不调参、不提交SVN、不冻结或发布；PR #10保持OPEN，原reservation pending-main，不合并或finalize。Subagents: none。

## 2026-09-17 — TASK-0036飞书展示副本已创建，待User轻量Review

- [展示文档：CR 9.22 全项目数值体验｜制作人展示版｜r7013](https://gfok27asqq.feishu.cn/docx/Rm2GdeMcXoEg2SxodIScDdzpn1c)；[TASK-0036](../tasks/TASK-0036-CR-0922-PRODUCER-EXPERIENCE.md)与Git仍为真相源，飞书仅为会议展示副本。
- 依据PR #10已发布Round 1 Accepted（受评d663a0c）；本轮只创建及登记展示链接，数值、9组Unknown和r6961原证据/r7013适用口径不变。当前等待User对展示副本与Git登记做轻量Review；下方数值报告“待ChatGPT Review”为当时历史。
- CLI显式user创建并回读revision 4：7节顺序、8张表、36组Spin、八类系统、9组Unknown、段落与来源链接一致，同名1篇。只展示报告汇总；无源配置/受控包附件、内部URL/路径或敏感日志上传。
- 当前公司内链接可读（tenant_readable）；未改权限、未开启公网链接分享。原分支codex/cr-0922-producer-experience / PR #10保持OPEN；不调参、不改SVN、不冻结、不发布、不合并或finalize，reservation pending-main。Subagents: none。

## 历史 — TASK-0036全项目数值体验提交ChatGPT Review时


- [TASK-0036](../tasks/TASK-0036-CR-0922-PRODUCER-EXPERIENCE.md)为Review；allocator原reservation pending-main，分支codex/cr-0922-producer-experience / [PR #10](https://github.com/840832144/AI-Workspace/pull/10) OPEN。起点main b0a36c8，PR #9与0035 Complete记录已合入，下方旧待Review语句为历史。
- 15:49:34北京时间固定trunk r7013；r6961→r7013全trunk变更路径摘要为空，覆盖全部数值根及新增/删除。所有系统直接复用Accepted证据，源刷新0；不重做0033/0034/0035、不做hash或全量正文扫描。
- [制作人报告及受控包](../projects/cr/REPORTS/CR-20260922-PRODUCER-EXPERIENCE/README.md)已完成八类覆盖；36组静态Spin、72条双活动、36条掉卡条件；6项新增模型测试与定向输出核对通过。仅普通扣金币Spin，固定档/足够余额；不代表真实玩家分布、升级路径或实际机台适用RTP。
- 剩余9组解释边界逐项列缺项/影响/负责人，历史22项保留来源，不新开冻结Gate。完整数值与复算输入受控，Git仅脱敏报告和方法；777 forceTurn闭合，活动仅薯片+777，0035现值候选不改。
- Review重点：特殊/常规RTP分层，离散积分期望，毛下注及资源不重计，成长/付费/卡册Unknown。Task Registry按既有工具重建验证；不调参、不改或提交SVN、不冻结、不发布，不合并或finalize。Subagents: none。

## 2026-09-17 — TASK-0035合并与finalize完成

- [TASK-0035](../tasks/TASK-0035-CR-0922-SNACK-777-FREEZE-PREP.md)治理状态Complete；[PR #8](https://github.com/840832144/AI-Workspace/pull/8)已合并，merge commit及本次同步main为`fde35b2f804e1f69bf02acc6d9581c5d009b118a`。
- 已直接确认canonical与Round 1 Accepted Review进入main，使用原reservation执行既有finalize返回finalized，远端reservation已解除；不新建或重新分配Task。
- r7004现值、0数值变更的薯片+777候选保持原样，Accepted结论及证据限制保留；没有重算、hash、全量业务扫描或SVN操作。**尚未正式冻结或发布**。Subagents: none。
- 本次仅收口Task/Status/Handoff、报告治理状态和Registry；Complete元数据随codex/task-0035-git-closeout候选分支提交PR，等待Review。下方Accepted/OPEN/pending-main为合并前历史。

## 历史 — TASK-0035 ChatGPT Round 1 Accepted（合并前）

- [完整Round 1](../reviews/TASK-0035-CHATGPT-REVIEW-1.md)已落库，受评0676ef3，结论Accepted，无阻塞项。ChatGPT独立核对35900个选中字段无差异，未独立连接公司SVN；本次只做治理收口，不重算、不重跑TASK-0033/0034、不做hash或全量扫描。
- PR #7已按User授权以merge commit `051a55195a6a483ce198fe432fe7af29d92444b3`合入main；canonical及三轮Review进入main后，原TASK-0034 reservation返回finalized，旧Task的Gate交付与Git收口Complete。
- [TASK-0035](../tasks/TASK-0035-CR-0922-SNACK-777-FREEZE-PREP.md)由allocator正式分配，当前Accepted；仅9.22薯片+777。User确认“没有改动”，r7004零数值变更方案、清单、候选及受控复核包已完成；forceTurn已正式闭合，两个活动无剩余业务规则Gate。
- 2026-09-17 14:32:41北京时间读取HEAD r7004；14个指定工作簿相对r6961无变化，统一导出r7004。阅读层2437行；复用546条Accepted阶段记录不重算；8个forceTurn定义示例及候选定向验证通过。
- 新分支codex/cr-snack777-freeze-prep / [PR #8](https://github.com/840832144/AI-Workspace/pull/8)，原Task完整历史保留；新reservation pending-main。PR保持OPEN，等待User明确合并授权；不改源配置、不提交SVN、不调参、不正式冻结或发布。旧Task Complete元数据随本新分支更新；新Task不提前finalize。Subagents: none。
- [当前方案、候选及受控复核包导航](../projects/cr/REPORTS/CR-20260922-SNACK-777-FREEZE-PREP/README.md)；完整数值继续留受控目录。历史TASK-0034的6/4/12为组合决定前快照，不能用其中待授权/待forceTurn语句替代当前输入。


## 历史 — TASK-0034 Round 3 Accepted（合并前）

- [Task](../tasks/TASK-0034-CR-0922-FREEZE-GATES.md)为**Accepted**；[完整Round 3](../reviews/TASK-0034-CHATGPT-REVIEW-3.md)已落Git，受评d8f1b72，无必须修改项；Round 1/2及历史证据保留。
- [当前Matrix](../projects/cr/REPORTS/CR-20260922-FREEZE-GATES/FREEZE_GATE_MATRIX.md)保持**6 Closed / 4 Conditional / 12 Non-blocking**。G03/G09/G12/G16按原条件触发；规则Closed不等于源配置已满足冻结条件，活动组合仍由User决定。**尚未冻结或发布**。
- Review仅做轻量状态复核，未独立重跑前轮数值、Registry、链接、diff或其他Codex证据；本轮仅落库评审并同步治理状态，不重算、不重跑TASK-0033、不做哈希或全量业务扫描。完整数值留原受控目录。
- 原分支codex/cr-0922-freeze-gates / PR #7等待User明确合并授权；reservation保持pending-main，不新建Task、不提前finalize。不改源配置、不提交SVN、不调参、不冻结、不发布、不合并。Subagents: none。


## 历史Round 3候选 — TASK-0034 Gate状态修订（d8f1b72，已Accepted）

- [Task](../tasks/TASK-0034-CR-0922-FREEZE-GATES.md)为Review；[完整Round 2](../reviews/TASK-0034-CHATGPT-REVIEW-2.md) Needs changes，受评761b08c；经过Changes Requested后只修状态，原分支codex/cr-0922-freeze-gates / PR #7及pending-main reservation不变。Subagents: none。
- [当前Matrix](../projects/cr/REPORTS/CR-20260922-FREEZE-GATES/FREEZE_GATE_MATRIX.md)：**6 Closed / 4 Conditional / 12 Non-blocking**。无无条件业务规则阻塞；不能再写只有2类条件，业务规则Closed与候选配置可冻结分开。
- **G12 Conditional**：选挖矿时，r6961缺id4–12通关奖励必须补齐，或由User明确这些关无通关奖励；同ID/12关结束的规则Closed保留。
- **G16 Conditional**：选拳击或挖矿时，必须移除对应源配置中的相关建造币奖励；关闭建造/移除奖励的决定Closed，前轮分析层排除27槽位不能替代源修改。
- G03（剩余缺档需价值比较）和G09（选777补forceTurn）继续Conditional；其他状态/数值规则不变，不代选活动。
- [报告](../projects/cr/REPORTS/CR-20260922-FREEZE-GATES/README.md)已同步；本轮只做Gate/文档一致性、链接/diff及Registry校验，不重算数值、不读源表、不运行分析工具、不重跑TASK-0033、不做哈希或全量业务扫描。原受控Round 2包数值继续复用，旧Gate统计为历史。
- 下一轮轻量Review只核对上述分类和冻结条件；不改配置、不提交SVN、不调参、不冻结、不发布、不合并或finalize。下方“仅2类条件”为受评历史，当前以本节为准。


## 历史Round 2候选（761b08c，Gate分类已修正）— TASK-0034 请轻量Review Round 2

- [TASK-0034](../tasks/TASK-0034-CR-0922-FREEZE-GATES.md)仍为Review，原分支codex/cr-0922-freeze-gates / PR #7，原reservation pending-main；Subagents: none。
- [Round 1完整记录](../reviews/TASK-0034-CHATGPT-REVIEW-1.md)Needs changes，基线007202e；PR #7 User正式决定已逐项应用。状态经过Changes Requested，当前等待Round 2，不预先写Accepted。
- [Matrix](../projects/cr/REPORTS/CR-20260922-FREEZE-GATES/FREEZE_GATE_MATRIX.md)当前7 Closed、2 Conditional、13 Non-blocking，**无无条件业务阻塞，最多2类条件问题**：选777才补forceTurn；拳击/挖矿仍需比较缺档奖励价值才处理G03。G01/G02退出前置；其他原非阻塞缺口不要求本轮关闭。
- 积分改为溢出连续跨档/末档规则，Pass共享门槛；建造币从受影响模型排除，5处金币缺档仍在；777旧每格一次账本退出当前周期成本。四活动保留可选候选，不决定组合。
- 固定r6961；只读8张受影响表，550条阶段记录、30对Pass、27个建造币奖励槽位排除。源奖励只覆盖挖矿id1..3且有round，未用取模补4..12；G12规则Closed不代表现表齐备或完整12关EV。仅计算层覆盖，没有源配置写入。
- 4项连续结算回归及受影响输出定向核对；Registry工具重建/验证，变更链接/diff检查；不重跑TASK-0033、catalog、全仓业务扫描或哈希。完整数值及[增量复核包导航](../projects/cr/REPORTS/CR-20260922-FREEZE-GATES/README.md)留受控目录，旧Accepted及首轮包保持历史。
- Round 2只核对正式输入应用、旧假设退出当前结论、最多2类条件Gate及源表证据限制。PR保持OPEN，不改配置、提交SVN、调参、冻结、发布、合并或finalize。下方首轮8组问题是历史，不再要求重答。


## 历史首轮 — 2026-09-17 TASK-0034 CR冻结Gate，等待ChatGPT Review

- 新Task：[TASK-0034](../tasks/TASK-0034-CR-0922-FREEZE-GATES.md)，Review，独立分支codex/cr-0922-freeze-gates；TASK-0033保持Complete，不续写。原reservation pending-main，不提前finalize。Subagents: none。
- [报告](../projects/cr/REPORTS/CR-20260922-FREEZE-GATES/README.md)及[Matrix](../projects/cr/REPORTS/CR-20260922-FREEZE-GATES/FREEZE_GATE_MATRIX.md)已经交付；10项Needs Planner Decision、1项Conditional、11项Non-blocking。已闭合子项与整Gate状态分开，冻结依据尚不充分；没有执行冻结。
- 2026-09-17 10:40:04北京时间读取SVN：HEAD r6987，trunk最后内容r6918，相对r6961无路径变化，继续同版r6961。只读23张关联表和既有索引，没有重跑Accepted总表或文件哈希。
- User已确定常规USD Bet=1归95%；新受控CSV为220条参考组合增加决策覆盖，原总表不动。特殊RTP优先级仍待确认，不能把策划决定当配置已符合。
- 价格缺档收敛为同一金额的5处引用；4个阶段样例、9个777圈/轮的条件清盘账本和资源关系可复算。候选保留薯片/777/拳击/挖矿，不替User选四选二。G13因薯片/拳击仍在候选中保持条件阻塞。
- 9份当前正式知识库原文有revision证据；历史数值附件未作当前输入。全局搜索权限不足但已知CashRoyal目录读取成功；不扩大权限，也不声称已检索所有正式资料。8组最小问题集中在Matrix的Q1–Q8，由对应策划/User补规则，不要求程序/线上/运营/支付审计。
- 验证：新工具真实输出、3个RTP边界、220条新旧口径分离、4个阶段手算、777条件清盘、定向价格覆盖和22项Matrix状态一致；AST通过。Registry由工具重建后valid（17 canonical/0 collision，6项既有legacy提示）；新增文档14个相对链接有效，diff检查通过。未重复Accepted工作簿/源缓存/外链/catalog/全仓业务验收。
- 完整数值、受控复核包与证据仅在本机；public Git只有脱敏报告/工具/治理。未改源表、提交SVN、调参、冻结、发布、合并或权限。
- 唯一下一步：ChatGPT Review本轮Gate整理及条件边界；User/策划集中答复Q1–Q8。下方TASK-0033及其他任务记录保留原时点。


## 2026-09-17 — TASK-0033 PR #6已合并，原reservation已finalized

- User已明确批准Git收口；[PR #6](https://github.com/840832144/AI-Workspace/pull/6)于2026-09-17 09:50:41（北京时间）通过merge commit合入main：`998a4d8a90541df25b0cedbcaeba069bbd1a010d`。保留候选f6bf84b、受评bdcdb3d及TASK-0033历史；[Round 1](../reviews/TASK-0033-CHATGPT-REVIEW-1.md)和[Round 2](../reviews/TASK-0033-CHATGPT-REVIEW-2.md)原文未改。
- 合并树与候选直接diff为空；main中的canonical Task、CR Status、Handoff、Registry及两轮Review已核对。Registry valid/16 canonical/0 collision；canonical进入main后，原linked worktree安全快进，再以原reservation执行既有finalize，结果finalized。不新建Task。
- [Task](../tasks/TASK-0033-CR-0922-NUMERICAL-INVENTORY.md)为Complete（整理交付及Git收口），Review Round 2仍为Accepted。固定 trunk r6961 现值整理已通过；22项业务缺口保留；尚未冻结或发布。完整数值与受控附件仍留本机，不新增公开数值。
- 本次只做Git收口；未改配置、提交SVN、调参、冻结或发布，也未改权限。各轮证据限制继续保留，不把合并检查当业务复算重跑。Subagents: none。
- 下方为历史阶段记录；当前事实以本节、Task和[报告](../projects/cr/REPORTS/CR-20260922-NUMERICAL-INVENTORY/README.md)为准，其他任务交接保持原样。

## 历史阶段 — 2026-09-17 TASK-0033 Round 2 Accepted，等待User合并授权

- [完整Round 2](../reviews/TASK-0033-CHATGPT-REVIEW-2.md)已落库：Accepted，评审基线`bdcdb3da6d1367c38e62fe7d45428b752d7e3063`；[Task](../tasks/TASK-0033-CR-0922-NUMERICAL-INVENTORY.md)已更新为Accepted，保留Round 1历史，不新建Task。
- 固定 trunk r6961 现值整理已通过；22项业务缺口保留；尚未冻结或发布。R1/R2均通过，无必须修改项；不等于完整机台/活动周期EV或所有业务定义已闭合。
- 评审独立验证与未复跑项按原文保留；本次不改数值产物或重复业务测试。[报告](../projects/cr/REPORTS/CR-20260922-NUMERICAL-INVENTORY/README.md)提供当前状态，受控包及VALIDATION-R1.json保留受评版本证据，不将旧状态当当前状态。
- PR #6和原分支`codex/cr-0922-numerical-inventory`保留，等待User明确合并授权；原reservation pending-main。不改配置、不提交SVN、不调参、不冻结、不合并、不提前finalize；完整数值和受控附录继续留受控目录。Subagents: none。
- 下方为历史阶段记录；其他任务交接保持原样。

## 历史阶段 — 2026-09-16 TASK-0033 R1/R2修订完成，等待Round 2

- [完整 Review](../reviews/TASK-0033-CHATGPT-REVIEW-1.md)已落库：Needs changes，基线04f7b29；Task经过Changes Requested，修订后回到Review，等待ChatGPT Round 2。
- R1：特殊RTP条件页/CSV保留同版全部9行、空/重复ID、等级上下界、5个活动条件与本表枚举；与常规85/95分开。优先级/实际生效继续关联G01/G02。
- R2：6处缺缓存、2处Excel错误缓存、19处外链分别定位，G05补齐说明字段异常；不把错误字符串用作数值，不判派奖/运行故障。
- 最终XLSX实际5699个公式（XML `<f>`自动计数），全部缓存与Python复算一致；19964个数值输出一致，公式错误/缺缓存均0；16页、4923条阅读记录。4个改动页视觉复核；81个特殊配置源字段和2处错误原式/缓存独立读取一致；非编辑范围50625个既有阅读单元格值/类型保持一致。
- [整理报告](../projects/cr/REPORTS/CR-20260922-NUMERICAL-INVENTORY/README.md)与验证文件已统一实测数字，最终统计工具排除以“=”开头的说明。catalog/repository/Registry/diff通过；3项R1/R2回归通过。
- 固定trunk r6961，22项业务缺口保留；完整数值和受控附录留本机。没有重新访问SVN或混版，源公式/外链未独立求值，完整机台/活动EV仍未闭合。Round 1未独立复跑catalog/Registry/视觉的限制照录，不能将本轮Codex验证冒充第二轮Review。
- 原分支codex/cr-0922-numerical-inventory、PR #6；原reservation pending-main。不新建Task、不调参、不改源表、不提交SVN、不冻结、不合并、不finalize、不改权限；Subagents: none。
- 下方首轮交付为历史候选，当前交付以本节和报告为准；保留其他任务交接。

## 历史候选 — 2026-09-16 TASK-0033 首轮交付（04f7b29）

- [TASK-0033](../tasks/TASK-0033-CR-0922-NUMERICAL-INVENTORY.md)：Review；固定trunk r6961，读取2026-09-16 17:58:52（北京时间）；Subagents: none。
- [整理报告](../projects/cr/REPORTS/CR-20260922-NUMERICAL-INVENTORY/README.md)提供范围、版本、完整交付文件名、方法和验证。完整15页总表、资源关系、明细与22项缺口仅保存在本机受控复核包，未上传public Git。
- 请复核表/字段/行ID追溯、概率分母、阶段清零、枚举隔离、状态期望和毛下注/机器净耗/实付区别。不能把读取完成称为数值全部闭合；不得用历史资料补当前缺口。
- 首轮XLSX实际5699个公式（Round 1已纠正原计数误报），19909个数值一致，16个关键源格独立读取通过；源外链/缺缓存未独立复跑，完整机台/活动整轮EV尚未建立。当时ChatGPT Review尚未执行；已发布Round 1及当前修订见上文。
- User只授权现值整理/复算；不设优化目标、不选四活动组合或排期、不改配置、不作SVN提交/冻结/发布；排除广告、生命周期、线上运营与技术审计。附件v0.1扩展指令不覆盖本轮User范围。
- 候选 `codex/cr-0922-numerical-inventory` 待Review；原reservation pending-main，不重新分配、不提前finalize。既有TASK-0032合并/切换事实及下方其他任务交接保持历史。

这是 ChatGPT 的固定交接入口。长期事实必须同步到 Capability contract、项目 Memory / Status、Task、RFC、ADR 或正式 Review，而不是只留在聊天中。

## 2026-09-16 — TASK-0032：已合并并切换单仓入口

PR：[AI-Workspace #5](https://github.com/840832144/AI-Workspace/pull/5) 已按 User 最终授权于 2026-09-16 15:03:31（北京时间）使用 Create a merge commit 合并，merge commit `3c214e2ca75eb82c16af6a186f7366fb3c249140`。当前日常入口为 AI-Workspace `main`，CR 资料与工具只写 `projects/cr/`；原 reservation 已 finalize。旧 cr_design 保留，不归档、不删除，权限不变。

- Task：[TASK-0032](../tasks/TASK-0032-CR-SUBTREE-PUBLIC-MIGRATION.md)，Complete；Review Round 1 Accepted；Subagents: none。
- 合并前 main 与 CR 来源未变，候选 `04a7568` 相对 `83eadec` 只有已授权评审记录；PR #2/#4 既有共享文件工作留在各自分支，无新增 main 冲突。
- 合并后 `1409737` / `fe07557` 均为 main 祖先；根与 CR 两入口、5个唯一 Skill、276文件映射和工具边界通过，catalog 14工作簿/0异常，repository 0错误/0警告。
- canonical 进入 main 后按原 reservation 返回 `finalized`；没有新分配 Task。候选分支 `codex/cr-subtree-migration@04a7568` 保留作历史，后续从最新 main 建独立分支/PR。
- 日常 CR Git 资料和工具只写 `AI-Workspace/projects/cr/`，旧库不再双写。公司 SVN 正式配置流程、CR/101 隔离与 HuuugeCollector 历史副本定位不变。
- [迁移报告](../docs/migrations/CR-MIGRATION-20260916.md)记录实际合并、最小必要验证和回滚。下方候选/Review 为历史：Review 未独立复跑，81项测试是此前本机候选验收，不是本轮或 GitHub CI。
- 未执行旧库归档/删除、权限调整、源表修改、同步 apply、SVN 提交、采集、部署或云端发布；手工 Project Sources 尚未上传，联网 Agent 以最新 Git main 为准。

## 历史阶段：2026-09-16 TASK-0032 ChatGPT Review Round 1 Accepted（合并前）

PR：[AI-Workspace #5](https://github.com/840832144/AI-Workspace/pull/5)，ChatGPT Review Round 1 已 Accepted（基线 `83eadec`）；等待 User 批准最终合并与切换。须使用 merge commit 保留 CR 导入历史；本轮不合并、不切换、不 finalize，旧库归档仍需另行授权。

- Task：[TASK-0032](../tasks/TASK-0032-CR-SUBTREE-PUBLIC-MIGRATION.md)；分支 `codex/cr-subtree-migration`；Subagents: none。
- 完整评审：[Round 1](../reviews/TASK-0032-CHATGPT-REVIEW-1.md)，来源为 PR #5 已发布评审，基线 `83eadec13cb4a03fa5b75de8dcbdd1f83cb61048`；无必须修改项。Review 未独立复跑测试、工作簿检查或备份恢复，未重复历史敏感内容审查，不能把报告的81项本机测试称为本轮独立验收或 GitHub CI。
- Task: Accepted；Execution status: 等待 User 批准最终合并与切换。本轮只固化完整评审、更新记录、重建/验证 Registry 并推送候选，不启动后续合并或切换流程。
- User 已批准 public 迁移以及三个 Top Tycoon 工作簿的原始记录与历史；不再清洗这三份文件，不新增重复哈希工作。其他敏感内容限制不变，权限不改。
- 来源 CR main `1409737648b15f602586b79ade7e0c3e7a3813a0`；原样导入 `fe07557ce5052da6a0eaaaaa1207b416ac081474`，直接 diff 为空且13个原提交保留。适配另行提交。
- 根/CR 规则、四启动文件、三 Agent 入口、唯一 Skill 路由、Context 与同步路径已适配。公司 SVN 正式配置保持原流程，HuuugeCollector 为历史副本，CR/101 分离。
- [迁移报告](../docs/migrations/CR-MIGRATION-20260916.md)记录来源、276文件映射、审查、验收与回滚。全新克隆的根/CR 两入口验收通过：14源表、36卡包附件、845935单元格、81项测试通过；上述为原迁移验收记录，Round 1 未独立复跑；现已 Accepted，尚未正式切换。
- 不执行源表修改、同步 apply、SVN 提交、真实采集或部署。最终合并和旧库归档仍待 User 确认；reservation 保持 pending-main，canonical 进 main 后才 finalize。

## 既有 Review 记录（保留原时点）

- Updated: 2026-08-29
- Current Review request: TASK-0019 — 项目全景说明与独立进度文档
- TASK-0019 status: `Accepted`
- Project key: `WORKSPACE`
- Execution rule: 并行任务使用独立 branch / linked worktree；不得覆盖其他任务或未提交修改

## TASK-0019 — Accepted Closure

- Review branch：`codex/task-0019-overview-progress-refresh`，基于 `main@c74c85a9524d1524ea3696835509de2a55e9f524`；未 merge 旧 `task-0019-overview-progress`。
- TASK-0019 Review Round 1 正式记录为 `reviews/TASK-0019-CHATGPT-REVIEW-1.md`：Decision `Needs changes`，reviewed commit `9403a09a445fd37548c78b3fc21709e91f5406d9`；本次只修指定的文档事实与验收缺口。
- TASK-0019 Review Round 2 正式记录为 `reviews/TASK-0019-CHATGPT-REVIEW-2.md`：Decision `Needs changes`，reviewed commit `e05d781e8aa54a6d10f1d0e44a1f84310fdf847e`；`e05d` 是已审基线，不是本轮新提交。
- TASK-0019 Review Round 3 正式记录为 `reviews/TASK-0019-CHATGPT-REVIEW-3.md`：Decision `Accepted`，reviewed commit `ccc1610a69808f7516e4d215d2177454021d108a`；canonical Task 已更新为 `Accepted`。
- Git deliverables：`docs/overview/AI_WORKSPACE_PROJECT_OVERVIEW.md`（稳定说明）与 `docs/status/AI_WORKSPACE_PROJECT_PROGRESS.md`（动态状态），不得合并职责。
- 核验 main：Huuuge `4a5dddf`、CF_collect `4df10ec`、Document Assistant `b0292c3`；均与远端一致且工作树干净。
- 必查口径：Huuuge First Run 保持 `Blocked`；正式 RC4 记录仍为 `Pending`；User 实跑仍为 `Failed/Invalid`。正式 Collector READY 未被可复核证明；只确认临时 SSL 捕获后进入 User 操作阶段，游戏由 User 亲自操作。Bet/RTP `Unsupported`。
- 必查历史与入口：进度文档第 7 节已补历史 TASK-0018 文件冲突和 ChatGPT 直写飞书地区限制；全景说明六个核心 Git 入口已统一到 `c74c85a...` 核验基线。
- 必查 Provider 分离：Workspace Sync 为 `ON_DEMAND / provider unavailable / stale 6 / conflicts 0`；Document Assistant 为 `Available`，healthcheck token/API/Drive 全部 `ok`。
- 飞书验收：Round 3 只原位 replace 既有进度文档，没有创建副本，项目全景飞书文档未写；进度文档正文、document ID/链接和 `tenant_editable` 权限回读通过，Hub 保持 17 个登记项、`unique_links=true`，进度标题唯一。
- Scope：未修改业务仓库；未启动模拟器、Root、Frida、Collector，未执行 Spin；Subagents: none / OFF。
- Validation：Round 3 定向断言 12/12、Task 23/23、Context 13/13、Memory 44/44、Registry 13 canonical / 0 collision / valid、Context refresh 70 sources / 0 broken link / 0 secret issue、changed-document scan 11 files / 0 broken link / 0 secret assignment / 0 stale READY / 0 new Task、项目全景 hash 不变与 `git diff --check` 通过。
- 决策边界：P0 Reliability Hardening 只保留 Decision proposal；未获 User 批准不创建 Task、不进入实现或运行。
- Closure：治理分支 fast-forward 合入 AI-Workspace `main` 后结束 TASK-0019；后续唯一动作是等待 User 审议 P0 Reliability Hardening Decision proposal。

## TASK-0023 — Idea Governance & Product Roadmap

- ChatGPT Review Round 2：Accepted；正式记录为 `reviews/TASK-0023-CHATGPT-REVIEW-2.md`，reviewed commit 为 `bc0d3ad1e519fb908dce53a78a35f9c3687a5b51`。
- Idea Governance 与 Planner Writing Style 已转为 `Accepted / Active`；Product Roadmap 和统一技术术语规则正式生效。
- 收口前回归：Context / Source Pack 62 sources、0 broken link、0 secret issue；Task 23/23、Context 13/13、Memory 35/35、两个 PowerShell 入口、Registry 10 canonical / 0 collision 与 Doctor 全部通过。
- Workspace Sync 保持 `ON_DEMAND`、0 conflict；provider unavailable，6 个发布项保持 stale，没有启用 WATCH。

- ChatGPT Review Round 1 结论为 Needs changes；Roadmap / Idea Governance 主体已通过，唯一 Required Fix 是准确、克制、面向受众的技术术语规则。
- `standards/PLANNER_WRITING_STYLE.md` 已成为唯一 canonical 规则源；Core Rules、Repository/Bootstrap/Global AGENTS、Project Instructions、ChatGPT Bootstrap、Generic Agent 入口和 Context Hub 均引用同一标准。
- ChatGPT 单文件 Source Pack 与 6 个拆分来源清单均包含 canonical 规范正文，不再只依赖 Core Rules 摘要。
- 默认面向策划使用准确且可理解的研究表达；复现、工程判断、授权、合规、安全或风险依赖真实机制时必须保留 Root、Frida、Hook、逆向分析、协议解密、校验绕过、系统修改、exploit 等精确术语。
- 规则明确禁止通过改名或模糊化规避安全策略、权限检查、User 授权或 Review，不得弱化真实风险或夸大被动研究。
- Context / Source Pack 已刷新为 62 sources、0 broken link、0 secret issue；Task 23/23、Context 13/13、Memory 35/35、两个 PowerShell 入口、Registry 10 canonical / 0 collision 与 Doctor 均通过。
- Workspace Sync 保持 `ON_DEMAND`、0 conflict；provider unavailable，6 个发布项保持 stale，没有启用 WATCH。

- User 已批准建立新的独立治理任务；正式 Candidate 经 allocator 晋升为唯一 canonical TASK-0023，reservation 保持 `pending-main`，未手工指定编号或编辑 Registry。
- 已建立唯一 Git Product Roadmap，固定 `Current / Backlog / Ideas / Done`，并明确它不替代 Task、Documentation Hub、Knowledge、Memory 或项目 Status。
- ChatGPT 新规则：主动提出长期产品能力、Workflow、Capability、Collector 或 UX Idea 时，自动防重、分类，并在相关 Task 收尾时向 Codex 生成 Idea Handoff，不依赖 User 手工提醒。
- 唯一正式飞书 Product Roadmap 已创建、回读、企业内可编辑并自动登记；项目全景说明已原位增加 Roadmap 入口，导航中心当前登记 15 份正式文档。
- 真实临时 Idea 已进入 Ideas 并回读，随后删除；正式 Roadmap 已恢复，四分区各出现一次。
- Registry 10 canonical / 0 collision；Task 23/23、Context 13/13、Memory 35/35、两个 PowerShell 入口和 Workspace Doctor 通过；Context refresh 62 sources、0 broken link、0 secret issue。
- TASK-0022、Cash Frenzy、Huuuge、Document Assistant 和 Workspace Sync 状态均未修改；`ON_DEMAND` 保持不变，WATCH disabled，Subagents: none。
- Review 重点：分类 Gate 是否足够严格、Top Tycoon 的 Current 表达是否符合 User 给出的顺序、ChatGPT Idea Handoff 是否既主动又不会越权创建 Task。
- 收口：完成 deterministic regression 后合并并 push main，在原 allocator worktree finalize TASK-0023 reservation，复验 0 collision 后清理分支/worktree。

### Failed attempts

- Candidate 首次使用带说明的 User decision 文本，被 allocator 按枚举 Gate 拒绝；修正为规范 `Approved` 后才分配 canonical ID，首次失败未占号。
- 首次临时发布脚本因 CommonJS 不支持 top-level await，在编译阶段退出且没有云写入；改为 `async main()` 后完整发布与恢复通过。
- 当前 Codex 会话的旧 MCP 进程缺少 `register_document`；其 `get_document` 回读会按旧 Registry schema 写回，导致项目全景说明治理 metadata 暂时丢失。未创建副本；使用 Document Assistant 当前 `main` 新进程重新登记后，Hub 恢复 15 条、链接唯一，项目全景与 Roadmap 均存在。

## Allocation and Current Queue

创建 TASK-0021 前已从 Git 最新 `main@6610feff2acbb48e9058b237c3a12332394b7221` 完整枚举 `tasks/` 根目录；`TASK-0021` 未被占用，创建后复验为唯一 canonical 文件。

当前相关任务：

- `TASK-0016-Automatic-Cross-Conversation-Memory-Curation.md`：`Review`，安全加固继续在独立 worktree 处理；
- `TASK-0018-Huuuge-Lottery-Numerical-Breakdown-Report.md`：Huuuge Lottery 数值报告主线，范围不变；
- `TASK-0019-AI-Workspace-Overview-and-Separate-Progress-Documents.md`：`Ready`，其两份源稿将成为 Live Context 的重要输入；
- `TASK-0020-Task-Allocation-and-Namespace-Governance.md`：`Ready`，负责 Task Registry、allocator 和历史冲突治理；
- `TASK-0021-Workspace-Live-Context-Hub.md`：`Ready`，负责实时 Context、飞书协作、Workspace Sync 和行文规范。

历史 TASK-0018 编号冲突继续由 TASK-0020 处理。执行任何 0018 时必须使用完整文件名，不能只写编号。

## TASK-0021 Objective

解决 ChatGPT Project Sources 需要手工下载、编辑、重新上传，以及多个会话 / Agent 并行时上下文不能及时同步的问题。

目标链路：

```text
稳定 Bootstrap / Project Instructions / AGENTS
                    ↓
              Workspace Sync
                    ↓
       最新 Context Manifest 与相关文档
          ├─ Git canonical truth
          ├─ 飞书协作与展示层
          └─ Host-specific local context pack
                    ↓
       ChatGPT / Codex / Trae / 策划共同工作
```

核心要求：

1. 优先验证并采用飞书知识库；Wiki 条件不满足时使用专用飞书 Drive 文件夹 + Docx，不能回退到手工搬运 Markdown。
2. Git 继续是 Task、ADR、Capability、规则和实现状态的 canonical truth；飞书提供多人协作、在线编辑和面向人的入口。
3. Git-authoritative 内容只向飞书发布；飞书协作草稿进入 Memory Candidate / Review，不静默覆盖 Git。
4. ChatGPT 直接 Feishu MCP 暂不可用时，通过自动 Git mirror 获取最新 Context，不能把 Project Sources 当实时状态源。
5. 建立 `standards/PLANNER_WRITING_STYLE.md`，禁止单词 / 短句逐行排版，统一正常中文段落、结论—依据—下一步和策划步骤写法。
6. 为 ChatGPT、Codex、Trae / DeepSeek 提供各自的 Workspace Sync Binding；无法同步时明确显示 stale / unavailable。
7. 支持 OFF / ON_DEMAND / WATCH，Pilot 后默认 ON_DEMAND；未经 User 批准不得生产启用 WATCH。

## Confirmed Baseline

- ChatGPT Project Sources 是快照，动态状态当前仍需手工替换；
- AI Document Assistant 已支持飞书 Docx、Drive、搜索、创建、替换和权限管理；Wiki 工具目前只在架构中预留，尚未实现；
- ChatGPT 直接 Secure MCP Tunnel 目前受 OpenAI Control Plane 地区限制，Codex 本地 `feishu-docs` 正常；
- TASK-0016 已提供 Git-backed Memory Candidate、Review、Public / Private / Local-only 路由，可作为 Feishu 草稿入 Git 的基础；
- TASK-0019 将生成项目全景说明和项目进度文档，可由 TASK-0021 纳入 Live Context，但不得复制或覆盖其正在执行的工作。

## Shared Boundaries

- TASK-0021 必须先完成 Reuse-first Feasibility Audit，再决定 Feishu Wiki、Drive Folder 或其他 fallback；
- AI-Workspace 与 document-assistant 分别使用独立 branch / linked worktree；发现活动任务重叠时停止并报告；
- 不修改 Huuuge Collector、Lottery 报告数据、Capture、SVN、游戏请求、奖励、余额或服务器状态；
- 不把 Secret、Raw Capture、账号、完整响应、逐笔余额、Feishu token、document token、private URL 或本机 Registry 写入公共 Git、飞书正文或日志；
- 不把飞书设为代码、Task、ADR 或运行证据的唯一真相源；
- 不静默部署公网服务、付费 SaaS、GitHub Secret、管理员权限或生产 WATCH；
- 不自动合并冲突，不直接覆盖 `main`，不声称 Project Sources 已自动更新。

## Exact Next Action

TASK-0019 已 Accepted。User 审议 P0 Reliability Hardening Decision proposal；未经明确批准不创建 Task、不进入实现或运行。在新的 User 决定前不启动业务环境。
