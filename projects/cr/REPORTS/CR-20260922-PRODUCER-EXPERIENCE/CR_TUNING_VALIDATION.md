# TASK-0036 — POP/CF调优候选验证

> 后续User已撤销A/B等级拉伸方案，改为已有300级同级对标、后续拟合，并授权等级提交dev；当前实际结果为[CR_LEVEL_DEV_RESULT](CR_LEVEL_DEV_RESULT.md)中的r7237。本文保留6d02f8c阶段的历史候选验证，不能作为当前等级提交输入。VIP继续暂存，PriceSetting未提交。

2026-09-21 · **Review；配置应用条件未满足** · [实施规格](CR_TUNING_POP_CF.md) · [Task](../../../../tasks/TASK-0036-CR-0922-PRODUCER-EXPERIENCE.md) · PR #10 OPEN · Subagents: none。

本轮已按User授权生成受控候选与可复算曲线，未提交SVN、覆盖r7013、冻结、发布、合并或finalize。原报告Accepted不自动覆盖本轮候选。完整商业值、代码证据、逐格diff和Excel仅在受控目录；Git只保留方法与脱敏结果。

## 交付及实际修改

受控根：`%LOCALAPPDATA%/AI-Workspace/cr-numerics-20260922/outputs/task0036-tuning-pop-cf-20260921/`。

| 文件 | 结果 |
|---|---|
| `CR_调优候选_vs_CF_POP_数值曲线.xlsx` | 8可见页、2隐藏计算/来源页、7原生折线图；所有等级明细保留 |
| `candidate/VipCfg.xlsx` | 仅Sheet1!B5:B19，15个needExp候选；零门槛安全Gate未通过，不能直接导入 |
| `withheld/LevelCfg.xlsx` | 未修改的r7013基线，0格变化；不是已选定的新候选 |
| `withheld/PriceSetting.xlsx` | 未修改的r7013基线，0格变化；不是可提交的调优配置 |
| `diff/config_actual_diff.csv` | 实际15个VIP改格；字段、行ID、坐标、before/after及差值 |
| `diff/PriceSetting_proposal_NOT_APPLIED.csv` | 928格拟议变化，全部未应用；不包含非金币货币 |
| `TASK-0036_TUNING_REVIEW.zip` | 上述交付、验证记录、说明及预览；不含内部URL、完整代码或原始日志 |

VIP权益、商城金币倍率、Bet、等级奖励、原r7013配置及CF历史表均未改变。曲线表为独立、自包含的候选分析文件，不替换先前r7013相对外链MASTER。

## 证据与当前结论

固定配置来源为既有`producer-dashboard-20260920/source/r7013/`及对应export receipt；receipt中的`LevelCfg.fresh.xlsx`是固定r7013原始导出。仅读取VipCfg、LevelCfg、PriceSetting、PriceCheatSheet及等级Bet两表。前轮固定汇率合并曲线的CR消耗/奖励/Bet缓存直接复用，未重算已Accepted模型。

CF历史只读正式`CashRoyal数值.xlsx`及同套既有曲线。POP输入沿用本Task已登记的User截图口径，未重新读取App或采集。定向代码证据固定r7013；读取时间、精确SVN位置与revision写在受控`source-receipt.local.json`、`evidence/`，不进public Git。本轮不把r7013称为今日最新trunk。

| 项目 | 已验证 | 尚未闭合 / 下一步 |
|---|---|---|
| VIP门槛 | 前10档为指定值；后5档按User选择POP高阶趋势；15档严格递增、均在int32范围 | 零门槛安全Gate未通过；需程序负责人确认初始化、直接升级、登录校正和客户端进度/领奖的一致行为 |
| 等级难度 | 两套完整5000级阶梯映射，整Spin门槛及实际成本可追溯 | User选择A或B，或提供唯一正式映射；此前不写LevelCfg |
| 档位膨胀 | 30档旧形状与r7013同维度一致；100%→500%保形归一；同档比例与VIP倍率保留 | 配置制作负责人确认当前制作表→PriceCheatSheet生成关系；此前不写PriceSetting或替代文件 |
| 等级膨胀 | CR/CF共同1–300级逐级一致，No Change | CF301–5000无来源；保持CR现值，不用外推冒充验证 |

VIP零门槛证据：`VipLevelUtils.AddVipExp`在传入经验为0时直接返回；`CorrectVipExp`按门槛重算；`AddVipLevel`从0到1的候选差值为0；同版`LoginHandler.cs`调用`CorrectVipExp`。静态有限遍历及边界复算只证明对应分支，未运行客户端/服务端，不能宣称安全通过，也不把入口差异直接判定为线上故障。

PriceSetting证据：同版`PriceSettingSvc.cs`已标记废弃并指向PriceCheatSheetSvc；后者经`PriceCheatSheetDescMgr.Instance.GetValue`取值。有限制作脚本检查未找到唯一生成关系。此证据足以暂停指定表写入，不等于完成全调用链或线上审计。

## 计算方法

VIP1–10：POP累计TP÷80 TP/USD×100 CR点/USD；按User指定整数落候选。VIP2的取整差异保留在对照中，未反向修改POP原值。

VIP11–15：令k为POP Tier6–10，固定Tier10锚点。`b=Σ((k−10)×ln(TP[k]/TP[10]))/Σ((k−10)²)`；后续门槛=`ROUND_HALF_UP(VIP10锚点×EXP(b×(VIP−10)))`。这是一种明确标注的高阶趋势外推假设，不是POP真实Tier11–15。窗口、斜率、原始门槛和输出在SRC/前台中可追溯，后5档舍入误差各不超过0.5点；VIP权益不拟合。

历史映射仅检查正式表的等级+buff、旧cr等级、等级体验表、基础金币及档位膨胀，未发现唯一CF→CR引用链，不能把历史手填Spin列当成已确认映射。当前两套待选方案均只索引CF完整逐级值，不插值或补缺：

- A全段拉伸：CR等级L=1..4999，CF索引=`1+INT((L−1)×299/4998)`。
- B保留前100：L≤100直接同级；其后索引=`101+INT((L−101)×199/4898)`。
- 目标机器净耗来自该CF索引的既有历史成本；预计Spin=`MAX(1,CEILING(目标净耗/(CR最大解锁BetUSD×5%)))`。
- Spin型候选门槛=预计Spin；经验型=向上取整(预计Spin×原levelExp)。再按原升级模式反推实际整Spin和机器净耗，展示目标与实现差；Excel对浮点接近整数的中间商先ROUND到10位再向上取整。
- 升级返还率=原CR升级奖励USD÷候选实际机器理论净耗USD；不是RTP或实付返还。低成本方案可能产生高返还率，未同步调奖励。5000为终点，5000→5001明确N/A。

档位维度是价格SKU的money，不是角色等级。旧shape=`vip0÷((money+1)/100)÷最低档基准金币`，30档与旧正式表一致。保形归一=`1+4×(旧shape−旧最低shape)/(旧最高shape−旧最低shape)`；同档金币各VIP与vipType统一乘`新shape/旧shape`，只生成方案，不写任何价格表。旧形状有平台段，候选保留平台段并单调不下降；没有擅自线性化或逐相邻档乘5。

## 定向验收

- 首步安全快进至`9fa2cd7`，按既有CLI重建/validate Registry；19 canonical、0 collision。没有新Task或新reservation。
- 三个配置输出逐格对照：实际改格15/0/0，其他字段、Sheet结构和行数不变；源文件只读。
- 原生Excel重算新候选；VIP尾部锚点加倍→输出响应→还原通过。未打开或保存源表。
- 5000级两方案的映射、整Spin、经验门槛、实际净耗及返还率逐级核对通过；5000级终点保留N/A。
- 30档端点/单调/保形及VIP比例验证通过；等级倍率1–300共300级匹配；新曲线7图全部折线/单主轴，完整系列点保留。
- 新曲线公式错误0、缺缓存0、外链0、冻结0；作者及绝对本机目录残留0。VipCfg和两份基线副本也清理元数据。
- 8个前台与30档完整表视觉复核。预览漏字时同时核对PDF正文与独立渲染，不把预览异常当成源格丢失；最终可见编号、单位、图例、尾部门槛及N/A。
- 收尾再次用CLI生成Registry并validate，不手改Registry。Workspace Sync为ON_DEMAND/provider unavailable/stale 6/conflicts 0，外部Context未同步。

未做hash、全量无差别扫描、旧Accepted Task重跑、CF_collect修改、采集或线上/技术审计。独立ChatGPT Review和VIP零门槛运行验收尚未执行。

## 复现

依赖既有bundled Python/openpyxl（只读）、Node/Artifact Tool（生成）、本机Excel COM（候选原生验算）。`$base/$out`必须指向受控目录。先保留固定r7013导出receipt、前轮曲线、历史正式表及本轮只读代码证据；缺少任一输入应报错，不回退到working copy。

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -X utf8 projects/cr/数值策划/工具/build_cr_tuning.py extract --baseline $base --output $out
# 将render_cr_tuning.mjs复制到已有Artifact依赖可用的受控目录执行。
node --max-old-space-size=8192 "$out/render_cr_tuning.mjs" "$out/tuning-inputs.json" $out
./projects/cr/数值策划/工具/verify_cr_tuning_native.ps1 -Directory $out
python -X utf8 projects/cr/数值策划/工具/build_cr_tuning.py sanitize --baseline $base --output $out
python -X utf8 projects/cr/数值策划/工具/build_cr_tuning.py verify --baseline $base --output $out
```

前台按`候选总览 / VIP门槛 / VIP商城金币 / 等级升级消耗 / Bet / 升级返还 / 档位膨胀 / 等级膨胀`排列；明细位于各页图表下。隐藏SRC保存固定抽取，CALC保存新增方案公式。本轮曲线交付不改变原制作人双版本文件。
