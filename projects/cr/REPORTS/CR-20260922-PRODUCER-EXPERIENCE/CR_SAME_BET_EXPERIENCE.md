# CR / Cash Frenzy 同Bet升级体验候选 — dev r7252

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
