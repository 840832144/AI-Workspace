# TASK-0036 最新CF等级对齐：受控候选交User检查

2026-09-22 · Status: Review · PR #10 OPEN · Subagents: none。

本轮按User最新决定制作等级、Bet及金币兑换候选。已生成5份受控配置副本、5000级体验Excel和逐格/逐键diff，等待User检查及ChatGPT Review；**尚未提交dev**。原Accepted报告、旧CF及历次SVN提交保留历史身份，本候选不自动覆盖它们。

## 已确认口径

- 经验点同比缩小，要求尽量小且规整，不固定除100。全部候选Bet的金币公约数为10,000，因此每Spin经验=`Bet/10000`，升级门槛=`CF原始EXP×3/10000`。38档经验均为正整数，最小档1点；已知44段理论及向上取整Spin不变。
- 基础金币兑换最低500,000、最高1,500,000金币/USD，档位倍率从1到3，保留30档现有相对形状。等级和VIP倍率另乘，不把150万作为所有倍率叠加后的上限。
- **所有.99标价按向上取整美元计算**，例如0.99→1、4.99→5、99.99→100；原money标价字段不变。此为User指定的本任务美元计算口径，不是支付链或实付金额审计。
- 最新CF已知等级倍率按当前证据；**125级及以后保留dev原等级膨胀解锁节点与数值**。撤回临时×14平延尾段。商城档位倍率与等级倍率分别计算。
- 对齐Bet、EXP比例、Spin及毛下注；净耗保留双方原模型。CR 5%、CF 15%为本Task既定等级模型/历史假设，未改变机器RTP。表中的CF假设净耗是同一候选毛下注乘CF假设净耗率，不冒称51+的CF真实兑币成本。

## 固定来源和落点

2026-09-22 06:19:06 UTC只读定向检查并导出CR dev **r7284**。来源URL、UUID和完整receipt仅受控保存；没有读入trunk、101或变化中的工作副本。LevelCfg最后变更r7247，BetList/Unlock为r7258，BetShow/PriceSetting为r5923，PriceCheatSheet为r6662，CommCfg为r7283。后者仅大厅随机宝箱冷却有变更，未写候选。

价格依据当前正式读取路径PriceCheatSheet：既有业务代码的基准取priceType=9/money=99，线性兑值取priceType=17/money=100。User取整口径使两路基础金币一致。PriceSettingSvc已标退役，本轮不误写旧表，也不修改生成/运行程序。VIP配置继续暂存，不包含在本次候选。

| 配置副本 | 目标变更 | 保护范围 |
|---|---|---|
| LevelCfg.xlsx | C列levelUpExp，4,995格 | 类型/VIP/其他列及5000级终点原样；前4级Spin门槛保留 |
| SlotsCasinoBetList.xlsx | 4个必要Bet金币档及34个经验格，共38格 | stable ID及非目标字段/公式保留；伴随Bet倍率公式原生回算 |
| SlotsCasinoBetUnlock.xlsx | 普通池增加308个复合键、移除9个，共1,278行 | 保留键的全部字段及485条HighRoller行不变 |
| SlotsCasinoBetShow.xlsx | 4格金币数值备注 | index/value等映射不变 |
| PriceCheatSheet.xlsx | priceType=9/17的金币输出，114,912格 | 原标价/键/钻石不变；VIP比例保留至整数金币舍入精度 |

BetList是普通与HighRoller共用表，因此后者虽未改变解锁行，仍会受到共用Bet金额/EXP变化影响。新增普通解锁行继承最近既有阶段最大档活动字段，来源行记录在受控输入中；没有重建已退场低Bet池。该保留/继承策略须随候选检查，不能写成游戏内活动验收。

## 计算与拟合边界

CF使用2026-09-22最新已交付实测/服务器规则。CSV的等级是**到达等级**：到达L7–L50的44段对应CR当前L6–L49，取出发等级Bet，禁止提前使用到达后解锁的Bet。

- L1–L5缺完整当前CF门槛：保留原CR Spin；L1–L4 Bet保持，L5金额仅由服务器无变更区间推定。不能称所有早期等级已按CF闭合。
- 到达L51起使用最新L30–L50门槛趋势，拟合式=`L50锚点+斜率×(到达等级−50)`；斜率为固定L50锚点的最小二乘，原始窗口与系数在受控输入。换算后四舍五入为整数经验；5000级为终点，无下一次升级。
- Bet后段依据L30/35/40/50金额趋势，以L50为锚点；从75级起每25级评估一次，取现有可用Bet档下界，不新建ID，封顶于现有最高档。75/100节点有服务器依据，之后等间距是候选假设，未伪称实测解锁。
- 毛下注金币=`理论Spin×Bet`；美元=`毛下注金币/(基础金币/USD×当前等级倍率)`。默认基础档、无VIP加成，商城档/VIP另列关系。净耗美元=`毛下注美元×各自净耗率`，不是实付金额。
- 同Bet下等比换算保持门槛/每Spin经验的比值。整数门槛仍可能产生细小理论偏差，明细保留Spin差列及CALC中的向上取整Spin。

**需User重点验收：最新拟合到达300级的门槛约为旧表推算门槛的24%，不符合“应该相差不多”的预期。** 旧300级只用于差异诊断，没有为贴近旧表而更改最新输入。51+全部标候选拟合，不能把拟合自洽说成与真实CF逐级验证一致。

源证据仍有102条非零EXP/Bet比例与标准Bet÷3冲突，详见[前轮证据限制](CF_LIVE_REBASE_VALIDATION.md)。本轮按User要求把该标准规则作为设计目标，不重新扫描逐手Raw，也不把原冲突改成已解决。累计段差不能独立证明无越界的精确配置门槛。

## 实际验证

- 5份最终保存配置逐项检查目标值和非目标字段/公式；来源副本只读，未打开写入。Unlock按复合键核对，保留行和HighRoller行一致；完整1–5000最大Bet与候选模型一致。
- 全部38档EXP为整数且无倒挂；目标升级门槛在int32内，5000终点原样。44段已知模型理论/整Spin相同；4,950个拟合转移的理论Spin舍入最大偏差约0.000162，向上取整Spin差异0。此处“相同”是与指定规则/拟合目标相比，非客户端实测。
- 30档取整美元、首末币率、基准两路一致、档位单调、VIP比例和125+原倍率/原节点核对通过。整数金币舍入边界单独校验，未放宽非目标数据保护。
- 报告为4个可见页：候选说明、等级概览、5000级明细、商城档位；概览仅28个最大Bet解锁点，整数等级膨胀、筛选、无冻结。隐藏SRC/CALC保存来源与计算。
- 最终工作簿公式缓存、5000级成本/净耗、3张原生折线图核对通过，0公式错误/外链/冻结。原生Excel驱动改变/恢复响应通过；4页及3图视觉完成。本轮没有WPS实机或游戏客户端验收。
- Registry由既有CLI首步和收尾重建validate，19 canonical/0 collision/valid；Git增量、语法与本轮治理链接定向检查。没有重复hash或全量无关校验，未重跑TASK-0033/0034。
- Workspace Sync仍ON_DEMAND，provider unavailable/stale 6/conflicts 0；Git fetch无新增并发覆盖。Subagents: none。

## 受控交付与复现

目录：`%LOCALAPPDATA%/AI-Workspace/cr-numerics-20260922/outputs/task0036-cf-alignment-20260922/`。

- `CR_CF_等级对齐候选_5000级.xlsx`：User阅读与对比。
- `candidate/`：上述5份配置副本；不能直接当作SVN已提交版本。
- `configuration_diff.csv`、`unlock_diff.csv`、`validation.json`：逐格/逐键变更与结果。
- `TASK-0036_CF等级对齐_受控审阅包.zip`：报告、候选、diff、脱敏验证和README；不含内部receipt/URL、源全包、逐手Raw或账号。

脚本依赖既有bundled Python/openpyxl只读、Artifact JS及本机Excel；原配置副本使用已记录的原生精确编辑路径，避免Artifact导入表保存时旧公式残留。Git只保存工具、方法及脱敏摘要，不保存完整候选/商业明细。

```text
python -X utf8 build_cr_cf_alignment.py prepare --base <受控数值根目录> --out <受控输出目录>
node render_cr_cf_alignment.mjs <输出目录/alignment-inputs.json> <受控输出目录>
powershell -File write_cr_cf_alignment_native.ps1 -Directory <受控输出目录>
python -X utf8 build_cr_cf_alignment.py verify --out <受控输出目录>
```

回滚本候选只需停止采用candidate目录，源dev未改；生成器从固定只读source重建，不以候选覆盖源。后续User验收并明确授权dev后，须重新定向确认最新依赖与并发，再按正式提交流程准备；此次不提交SVN、不冻结/发布、不合并PR #10、不finalize。
