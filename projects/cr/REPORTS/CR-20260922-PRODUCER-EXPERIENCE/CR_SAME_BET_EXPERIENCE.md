# CR / Cash Frenzy 同Bet升级体验 — dev r7258

> 2026-09-22当前口径已转为[CF最新实测重基线](CF_LIVE_REBASE_VALIDATION.md)。本页CF旧表、插值及1/6折扣的对标结论均为历史；r7258提交事实保留，但不是最新CF一致性验收。本轮没有新增SVN写入或自动回滚。

## 2026-09-22 展示更新：整数等级膨胀与解锁概览

User要求追加第5列“等级膨胀”，概览只保留最大Bet变化的解锁等级。现为26行概览、5000行明细，两边列序均为等级、最大解锁Bet、Spin、消耗美金、等级膨胀。

等级膨胀按整数倍数、1级=1显示：CR为`本级金币/USD ÷ 1级金币/USD`，CF为`原始等级倍率 ÷ 1级倍率`；现有源值均为整数，不用显示舍入掩盖小数。CF仅1–300级有数据，其后N/A。新增列来自原有SRC，原四列在5000级逐级核对不变，三张原曲线仍保留全部300点。

当前产物在`%LOCALAPPDATA%/AI-Workspace/cr-numerics-20260922/outputs/task0036-bet-simple-20260922/CR_CF_等级体验_简表.xlsx`。52,960公式缓存无错误/缺缓存、0外链/冻结，26个概览等级与最大Bet变化点逐项对应，完成新增列和末级视觉复核。旧四列表及以下dev r7258提交记录保留历史身份；本轮只修改展示，没有重新拟合数值或再次修改/提交SVN。Task仍Review。Subagents: none。

2026-09-21 · TASK-0036 · dev已提交，Git待Review · Subagents: none。

## 当前结果：倒挂修复、dev提交与简表

User明确批准“dev可以先提了”，并批准缺档按相邻锚点线性插值、超过最高参考Bet按末档EXP/Bet比例延伸。已从最新dev **r7257**定向核对六份依赖，与上一轮r7252无内容变化；使用隔离工作副本和既有`svn_submit.py`完成dry-run及提交，实际版本 **r7258**。

- 仅提交`SlotsCasinoBetList.xlsx`、`SlotsCasinoBetUnlock.xlsx`。34个经验值修改，17个已对标锚点保留；全38档经验随Bet单调不下降，9处倒挂降为0。5–300级296个整Spin模拟结果保持，不因补缺档改变已有对标结果。
- 普通Bet的28个目标档首次解锁、1–5000级最大Bet全部符合User确认的同金币/保守取值目标。普通解锁新增11行，移除2行超过目标上限的档位；不是重写完整Bet池。现有保留行活动字段不变，新行沿用同等级原最高Bet的活动设置，不引入新活动参数。原HighRoller解锁485行保持原样；BetList经验字段两模式共用，因此HighRoller经验也会随之改变，未声称获得CF HighRoller实测对标。
- User的LevelCfg及5000级终点完整保留；VIP继续暂存。BetShow、PriceCheatSheet、CommCfg未变，未提交trunk、正式冻结或发布。
- 远端r7258两份工作簿与候选单元格差异0，提交路径仅两个目标文件；中文日志完整，作者与此前已授权dev提交一致，隔离工作副本干净。内部URL、账号和完整日志仅留受控目录。

## CF折扣与四列简表

User确认CF消耗按历史理论值的**1/6**计入本轮比较，这是业务输入，未声称来自实付账单。两边同金币Bet、同Spin的美元单位成本因此一致；保留原CR等级专项95%与CF历史85%及各自金币/USD，不修改价格或RTP配置。

- CR单级净耗USD：`CR整Spin × Bet ÷ CR金币/USD × CR净损率`。
- CF单级净耗USD：`CF原始期望Spin × Bet ÷ CF金币/USD × CF净损率 × 1/6`。
- 插值EXP：`左EXP + (右EXP−左EXP) × (Bet−左Bet)/(右Bet−左Bet)`，四舍五入至整数；尾部为`末档EXP × Bet / 末档Bet`再取整数。小于首个EXP模式锚点的档保持现值。
- 两个可见页依次为**概览、明细**，两边各四列：**等级、最大解锁Bet、Spin、消耗美金**。概览70行，按解锁/价值/模式变化点及其边界选择，明细保留全部5000级；3张同轴折线图保留1–300全部逐级点，公式与来源在隐藏SRC。
- “消耗美金”为该级到下一级的模型净耗，不是毛下注、累计消耗或实付金额。CF小数期望原样保留，不能通过显示取整制造一致；301级后CF Spin/消耗明确N/A，5000级没有下一次升级。

## 验证、边界与回滚

- 43,260个公式缓存定向验证通过，错误/缺缓存/外链/冻结均0；原生Excel完成CF折扣驱动变化/恢复。3张折线图各两条300点曲线、概览及300/5000边界表格完成视觉复核。当前验证是配置模型与实际SVN写后回读，**未执行游戏客户端运行验收**。
- 仍有明确差异：1–4级保留User的Spin门槛；7组共享Bet不能同时精确复现全部CF小数期望。整次Spin和小数期望导致的成本差别仍如实显示。缺档/301级后补齐为User授权拟合，不能改称CF原始数据或全部Bet实测一致。
- 配置生成时发现本机Artifact导入工作簿回写保留旧公式、只改变缓存，逐格验证拦截了该产物。用原生Excel在源配置副本精确修改，再按全部非目标值/公式及目标值重新核对；没有降低断言或直接提交缓存成功的文件。简表继续由Artifact生成，原生Excel回算验证。
- Registry只通过既有CLI重建/validate；不重跑TASK-0033/0034、不做hash或无关全量目录扫描。Task仍Review、PR #10 OPEN、原reservation保留，未合并/finalize。
- 若需回退，先获得User批准，在最新dev的独立工作副本对**r7258的两个文件**制作反向变更，核对后续并发及全部非目标值后走同一dry-run/提交/回读流程。不要覆盖或回滚User的LevelCfg/VIP，不直接以旧整表覆盖最新dev；Git文档可追加纠正或revert本轮收口commit，不强推历史。

受控目录：`%LOCALAPPDATA%/AI-Workspace/cr-numerics-20260922/outputs/task0036-bet-dev-20260921/`。
包含`CR_CF_等级体验_简表.xlsx`、`candidate/`两份提交表、`configuration_diff.csv`、`candidate-validation.json`、`workbook-validation.json`、`svn-result.json`及私有receipt。完整数值/源表/候选均不进public Git。复现工具为`build_cr_bet_dev.py`、`render_cr_bet_dev.mjs`、`verify_cr_bet_dev_native.ps1`；配置回写遇到导入公式保留限制时采用已记录的原生步骤，`-ReportOnly`只刷新简表。

## 历史记录：r7252的未提交候选

以下保留当时结论；“没有提交dev”“美元差异”“9处倒挂”等均为追加授权与修复之前的状态，以本页当前结果为准。

2026-09-21 · TASK-0036 · 待User验收 / ChatGPT Review · Subagents: none。

## 当前结论

本轮形成受控对比Excel、Bet解锁目标和17档经验拟议值，**尚未实现或验收游戏内全部一致**。没有修改LevelCfg或任何SVN配置，没有提交dev。

- User最终目标：相同金币Bet下的升级体验、Bet解锁节奏与CF一致；美元消耗门槛同时展示，用于发现分歧。美元成本不能代替游戏升级体验的判据。
- Bet按同级、金币原值对齐；CF主表与解锁表在56级存在历史冲突，User决定取较低金币Bet。两份原始来源保留，正式目标由较低值确定，不再作为未决来源问题。
- User允许根据Bet、升级Spin反推经验。固定dev门槛除以CF同级历史期望Spin得到逐级所需EXP，标为CR候选，不能称为CF原始经验配置。
- 1–300级中的经验模式区间，存在17档可行整数经验区间。最小改动候选可令5–300级的整Spin模拟次数与CF期望向上取整次数一致，共296点；这不是CF客户端实测，也不是小数期望零误差。
- 小数期望存在7组共享Bet经验冲突；1–4级是Spin门槛模式，按User要求保留dev值，调整Bet经验不能消除这4级差异。未擅自改LevelCfg或接受误差。
- 仅替换有对标点的17档而把缺来源档保留时，全Bet表会出现9处经验随Bet增大反而下降。候选页逐处标记，不输出可直接提交的BetList；不能把参考档通过扩大为所有Bet体验通过。
- 美元曲线仍有差异：沿用既有等级专项CR95% / CF历史85%成本口径及各自金币/USD分母。未更改价值换算或RTP来拉平。候选成本与同口径CF整Spin成本的差异在受控表中明确展示。

## 来源与边界

固定CR dev **r7252**，读取时间 **2026-09-21 12:25:10 UTC**。只读导出LevelCfg、SlotsCasinoBetList、SlotsCasinoBetUnlock、SlotsCasinoBetShow、PriceCheatSheet、CommCfg；私有SVN位置仅在受控receipt中。

User较r7237修改的4个LevelCfg门槛全部保留，5000级终点亦保留。此前r7237成本误差统计是历史结果，不是当前r7252候选结论。

CF仅用旧正式`CashRoyal数值.xlsx / cashFrenzy等级`：主表A:I、普通Bet解锁AJ:AK、固定美元分母及抽水字段。旧表可直接比较的同级经验/Spin范围仅1–300；更高等级只保留Bet解锁锚点，不虚构CF升级体验或EXP。没有用Collector、Web或其他竞品填补。

CR同Bet模拟使用CF正式目标金币Bet在现有BetList中的对应经验行，并另外显示该Bet是否已解锁；不得把CR当级最大Bet的经验误当成相同Bet经验。BetList所有拟议变更只展示在Excel候选页，源表未写入。

## 公式与候选选值

1. 正式CF金币Bet：共同范围内取`MIN(主表Bet, 解锁表Bet)`；300级后仅按解锁锚点。由主表保守选择新增的档位也进入目标清单，不能只复制原解锁表漏档。
2. 精确期望EXP：`dev本级门槛 / CF历史期望Spin`，只适用于经验门槛模式；Spin模式不通过此字段控制升级次数。
3. 单列整Spin比较基准：`n = CEILING(CF期望Spin)`。它是明确标注的模拟约定，并未将历史小数改成CF实测值。
4. 对整数门槛T，若要`CEILING(T / EXP) = n`，则EXP下界为`CEILING(T/n)`；n>1时上界为`CEILING(T/(n-1))-1`。同档各级区间取交集；交集为空不得自动拟合掩盖。
5. 可行区间内选择距当前EXP最近的整数，最小化本轮改动。缺CF同级来源的档位保持dev值，不能宣称已与CF对齐。
6. 升级美元消耗：`Spin × 同金币Bet ÷ 本游戏同级金币/USD × 本模型净耗率`。原始期望与整Spin结果分列；两边同取整后的偏差另列，避免把分母和取整差异混在一起。

## 交付

受控目录：`%LOCALAPPDATA%/AI-Workspace/cr-numerics-20260922/outputs/task0036-bet-exp-r7252/`。

- `CR_vs_CF_Bet解锁与经验对照_r7252.xlsx`：3个概览在前，随后Bet档位、完整5000级、Bet经验候选、经验约束明细；隐藏3份SRC，无外链、无冻结。
- 5张原生折线图：Bet 1–300、Bet 1–5000、同Bet升级次数、美元消耗门槛、EXP/Spin。共同经验区间保留全部逐级点，CF未覆盖区间不补值。
- 目标Bet清单28档，包含User保守决定从主表引入的档位；原CF解锁表27档保留来源。17档经验有拟议值，其他档位显示未对标、保留现值。
- `comparison-inputs.json`、`validation.json`和`previews/`保留完整数值与回读证据，仅本机受控保存。

生成器：`compare_cr_bet_exp.py`（prepare / verify）、`render_cr_bet_exp.mjs`（ArtifactJS）、`verify_cr_bet_exp_native.ps1`（原生回算和视觉导出）。完整数据、源表、候选Excel与私有receipt不进public Git。

## 验证与未完成项

- 已对本轮5000级数据、300个CF同级点、候选经验区间及108891个公式缓存定向核对；公式错误/缺缓存/外链/冻结均0。原生Excel完成反推驱动变化与恢复；5张原生折线图共13系列完整引用，直接导出PNG并视觉确认，包含最后一级，避免分页裁掉曲线末端。
- LevelCfg只读；未重跑TASK-0033/0034、无hash或无关全量扫描。Registry首步和收尾均用现有CLI重建/validate，沿用原Task/PR/reservation。
- Registry为19 canonical、0 collision、valid；本轮Task仍Review，重建没有Registry语义变化。Workspace Sync为ON_DEMAND/provider unavailable/stale 6/conflicts 0，未伪称外部来源已同步。按User定向效率边界，本轮不运行全库XLSX目录重扫，以本轮产物、生成器语法、链接和Git diff检查验收。
- **未完成**：1–4级体验对齐、7组小数期望精确对齐、美元消耗一致、300级后同级CF体验证据、非参考Bet的完整体验及9处经验倒挂，以及将Bet目标映射到含活动字段的正式解锁表。不能将本候选称为可直接提交或全量游戏验收通过。
- 后续仅在验收明确后，定向处理上述差异及Bet解锁表中的额外档/活动字段关系；没有自动把其他活动规则改成新值。VIP仍暂存。
- 当前没有源表变更，回滚仅需弃用受控候选；不可回滚User已修改的dev LevelCfg。待User明确批准后才执行下一次dev提交；不提交trunk、不冻结/发布、不合并PR #10或finalize。
