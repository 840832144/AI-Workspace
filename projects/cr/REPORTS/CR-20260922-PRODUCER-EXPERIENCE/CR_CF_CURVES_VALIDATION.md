# CR vs Cash Frenzy合并曲线：固定汇率与商城金币倍率修订

- Task: TASK-0036；Date: 2026-09-21；Status: Review，等待ChatGPT审阅。
- 当前规格：[CR_CF_CURVE_COMPARISON](CR_CF_CURVE_COMPARISON.md)。原PR #10保持OPEN，原reservation pending-main，不新建Task。
- 交付：`CR_vs_CashFrenzy_数值曲线对照.xlsx`；本机受控目录：`%LOCALAPPDATA%/AI-Workspace/cr-numerics-20260922/outputs/task0036-cr-cf-fixed-vip-20260921/`。
- 本候选取代前一合并候选的可编辑汇率、游戏内称号及累计消费门槛指数展示；旧候选目录及Git历史保留，不是当前入口。

## 本轮变化与来源

CF前台标签统一VIP1–VIP7，不显示游戏内称号。消费页同时保留SGD原始最低/最高门槛和USD最低/最高门槛；固定分析汇率为 **1 SGD = 0.78408 USD**，取值时点2026-09-21 02:24 UTC。没有可编辑汇率输入、实时汇率公式、待汇率状态或旧`CF_SGD_TO_USD`定义名称。本汇率仅用于分析，不代表配置冻结。

CF累计VIP点及九个商城样本继续使用User正式输入与Git规格；兑换上下界沿用18.0401–37.2542点/SGD，不重新取精度或平均。前台右下方完整列九个商品的价格、VIP点及点/SGD公式，并注明最高与最低效率对应商品。原App截图未在本轮独立重读，证据限制保留，不含账号当前点数。

商城金币倍率取代旧累计消费门槛指数：

- CR只定向读取既有固定r7013导出的`PriceSetting.xlsx/Sheet1`。注释明确currencyType=1为金币、vipType=1为商店VIP加成；30个适用money档的VIP/VIP0倍率一致。CR VIP0–15完整保留：1x起，VIP6–15封顶2.5x。隐藏来源保存同价源金币、VIP0金币和源格坐标，前台用除法计算倍率。
- CF VIP2–7采用已登记User截图商城金币口径。旧正式`CashRoyal数值.xlsx/vip加成!F3:H3`唯一补齐VIP1=1.5x；同区块VIP2–7与截图口径一致。VIP1前台明确标为“历史正式表”，不冒称本轮截图直接验证；最高40x。CF VIP0不进入前台数据/曲线。
- 主图只有CR/CF各一条商城倍率线，Y轴为倍数x；表格另列百分比。没有累计消费门槛膨胀指数，也没有用CR其他VIP字段的650代替商店倍率。

CR消费门槛、等级成本/Bet/返还只读已交付CR v2缓存；CF三个等级页只读已有CF曲线缓存。未打开来源文件的原生计算引擎，没有重算、改写既有模型或Accepted底稿。旧VIP指数不再读取或带入新输出。

## 五页与验证结果

| 页签 | 同一主折线图 | 实际数值点数 | 保留明细 |
|---|---|---|---|
| VIP_消费门槛 | CR累计USD、CF最低USD、CF最高USD | 15 / 7 / 7 | CR VIP1–15，CF VIP1–7；SGD与USD上下界；九个商城样本 |
| VIP_膨胀系数 | CR商城金币倍率、CF商城金币倍率 | 16 / 7 | CR VIP0–15；CF VIP1–7；倍数及百分比 |
| 等级_升级消耗 | CR机器理论净耗、CF历史抽水折算消耗 | 300 / 300 | CR 4999级、CF 300级及奖励/净成本 |
| 等级_Bet曲线 | CR最大Bet、CR $1等值、CF普通最大Bet、CF $1等值 | 300 / 300 / 244 / 300 | CR 5000级、CF 300级；金币、百万金币与原有USD列 |
| 等级_升级消耗返还 | CR返还率、CF返还率 | 300 / 300 | CR 4999级、CF 300级及各自分母 |

5张可见页、2张隐藏来源页、5张原生折线图、13条系列；每图只有一个主纵轴。等级主图仍为1–300，完整明细保留；CF 15–19、250–300级的56个普通Bet冲突点继续N/A/空白，不补0或插值。返还率按各自分母计算，不等同机器RTP；等级USD继续保留既有模型定义，不被本轮商城SGD汇率重算。

已执行最小必要核对：

1. 原分支安全快进至`1644afc`；第一步以现有CLI重建并validate Registry，19 canonical、0 collision、valid；收尾再次由工具更新，未手工编辑。
2. 定向读取r7013商店VIP金币行及旧正式表CF VIP区块。前台全部输出与引用缓存/本轮公式核对通过，既有模型值变化0。
3. 原生引擎仅打开新合并输出，验证14个CF USD边界、固定汇率、VIP标签与倍率；清理作者/绝对路径元数据。原生序列化去除简单Sheet名引号属于等价公式，没有改引用。
4. 公式错误0（包含绘图区）、缺缓存0、外链0、冻结0、可编辑汇率输入0；SGD/USD列格式和同图单位正确。旧14个待汇率NA()已移除。
5. 五页原生打印预览及图表视觉复核通过。初次导出第一页右缘布局未刷新；保存后只读重开输出再导出，确认VIP15、三条成本曲线、九个商城样本完整。生成脚本已保留此刷新步骤。
6. Workspace Sync：ON_DEMAND/provider unavailable/stale 6/conflicts 0；外部Context未同步。不做hash、全量无差别扫描、0033/0034/0035重跑、采集、调参、源数据/CR配置/CF_collect修改、SVN提交、配置冻结或发布。Subagents: none。

独立ChatGPT Review尚未执行。CF VIP1的历史证据来源、56个Bet冲突点、highroller条件与历史版本缺口继续保留，不将这些边界改成已确认现网规则。完整商业值、输入JSON、Excel、原生验证与预览只留受控目录，Git仅包含方法和脱敏记录。

## 公式与复现

- CF最低/最高SGD门槛＝累计VIP点÷37.2542或18.0401。
- CF最低/最高USD门槛＝对应SGD门槛×固定0.78408。
- CR商店倍率＝同money档VIP金币÷VIP0金币；百分比与倍率是同一比例的不同格式。
- `SRC_CR` A/F/L/R/Y区依次为消费缓存/r7013商店金币快照/等级成本/Bet/返还；`SRC_CF` A/F/M为既有等级缓存，R:V为VIP点、序号、倍率及证据，X5为固定汇率，W9:X17为商城样本。所有来源只用文件名和格坐标，不带绝对本机目录。

```powershell
# $price必须是既有固定r7013导出PriceSetting.xlsx；$history为旧正式CashRoyal数值.xlsx。
$inputs = @('--cr',$cr,'--cf',$cf,'--price-setting',$price,'--history',$history,'--output',$out)
python projects/cr/数值策划/工具/build_cr_cf_curves.py extract @inputs
# 在既有Artifact依赖可用的受控目录执行，不将输入JSON或XLSX写入Git。
node "$out/render_cr_cf_curves.mjs" "$out/comparison-inputs.json" $out
./projects/cr/数值策划/工具/verify_cr_cf_native.ps1 -Directory $out
python projects/cr/数值策划/工具/build_cr_cf_curves.py sanitize @inputs
python projects/cr/数值策划/工具/build_cr_cf_curves.py verify @inputs
```

原生计算/图表读回、`validation.json`和5页预览保存在同一受控目录。当前等待ChatGPT Review；PR #10不合并、原reservation不finalize。
