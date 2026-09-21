# CR vs Cash Frenzy合并曲线：交付与验证摘要

- Task: TASK-0036；Date: 2026-09-21；Status: Review，等待ChatGPT审阅。
- 规格：[CR_CF_CURVE_COMPARISON](CR_CF_CURVE_COMPARISON.md)。同一PR #10与原reservation，不新建Task。
- 本地交付：`CR_vs_CashFrenzy_数值曲线对照.xlsx`；受控目录为`%LOCALAPPDATA%/AI-Workspace/cr-numerics-20260922/outputs/task0036-cr-cf-20260921/`。
- 当前仅VIP美元金额比较待User提供固定汇率。未假定S$=USD，未使用Web汇率；不影响CF累计点、原币成本边界与绝对膨胀的闭合。

## 来源与本轮变化

CR直接读取已完成 `CR_9.22_数值曲线展示_r7013_v2.xlsx` 五页的已保存结果；CF等级/Bet/返还直接读取上一候选 `CashFrenzy_数值曲线对照.xlsx` 对应三页的已保存结果。两个来源都只读缓存，没有打开原生引擎重算或保存。旧模型的公式、参数和结果未改写；没有重跑0033/0034/0035。

CF VIP改用User本轮明确确认的累计点序列及Git规格中的商城转录：0/1K/10K/31K/260K/2.1M/10M/50M，兑换边界为18.0401–37.2542点/S$。本轮没有独立读取原App截图；证据是User正式输入及已落Git的规格，不宣称重新验图。原截图与账号当前VIP点不进入Git或本工作簿。已确认的VIP2–7名称保留，VIP0/1不猜名称。

新计算仅为CF VIP原币上下界、显式USD换算及累计点绝对指数。等级类曲线使用已有结果，完整数据在各页主图下方，所有页均无冻结。旧单独CF工作簿保留作历史候选，其中VIP累计属性未明的N/A记录已由本合并版本取代。

## 五页与实际验收

| 页签 | 同一主折线图的系列 | 主图实际点数 | 保留明细 |
|---|---|---|---|
| VIP_消费门槛 | CR累计USD、CF最低USD、CF最高USD | 15 / 0 / 0，CF两线等待汇率 | CR VIP1–15；CF VIP1–7名称、累计点、S$上下界、兑换效率和USD待汇率状态 |
| VIP_膨胀系数 | CR绝对指数、CF绝对指数 | 15 / 7 | 两边VIP1=100%；CF只保留一条线 |
| 等级_升级消耗 | CR机器理论净耗、CF历史抽水折算消耗 | 300 / 300 | CR 4999级；CF 300级；两边奖励和净成本均保留 |
| 等级_Bet曲线 | CR最大Bet、CR $1等值、CF普通最大Bet、CF $1等值 | 300 / 300 / 244 / 300 | CR 5000级；CF 300级；原金币、百万金币及原有USD折算列 |
| 等级_升级消耗返还 | CR返还率、CF返还率 | 300 / 300 | CR 4999级；CF 300级；各自分母和奖励 |

固定5张可见页、5张原生折线图、13条系列，均为主纵轴。等级类主图只引用1–300级；CF在15–19、250–300级的56个普通Bet冲突点仍N/A/真正空白，不补零、不插值，也不使用CR数据替代。CF缺300级以后数据时显示N/A，CR完整数据继续存在。

两页隐藏来源快照仅保存本轮所需结果和正式输入。`SRC_CR`的A/F/L/R/Y列起分别对应旧CR五页，`SRC_CF`的A/F/M列起对应旧CF的升级消耗/Bet/返还页；缓存区从第4行开始，对应来源表第6行。CF累计点与商城边界在`SRC_CF`的R/X列区，原始VIP0累计点仍保留。来源文件名及证据说明写入隐藏页。

## 汇率输入及公式

- 输入位置：`VIP_消费门槛!B4`，黄色可编辑格，名称`CF_SGD_TO_USD`。单位为“1 S$兑多少USD”；交付值为空，页头明确“需User确认”。
- CF最低S$成本＝累计VIP点÷37.2542；最高S$成本＝累计VIP点÷18.0401。效率更高对应更低成本，不取平均。
- CF USD上下界＝对应S$成本×输入汇率。只有正数输入时才给出USD值和两条曲线；空白或无效输入显示“待汇率”。CF超过VIP7后自然断线。
- CF绝对膨胀＝累计VIP点÷VIP1累计VIP点。常数兑换率和固定汇率在比例中约掉，只有一条CF线，VIP1为100%。该页完全不依赖汇率输入。
- CR USD、绝对膨胀以及CR/CF所有等级成本/Bet/返还来自已有缓存；没有重建模型。页面并列注明各自成本/返还分母，不将模型净耗当实付或机器RTP。

缺汇率时，隐藏绘图区有14个**刻意使用的`NA()`**，用于让两条CF USD线不绘制，填写正数汇率后自动消失。前台累计点、S$上下界和绝对指数都有数值，前台USD为“待汇率”。这14个绘图缺点单列记录，不冒称全表零错误；非预期公式错误与缺缓存均为0。

## 已执行的定向验证

1. 安全同步原分支到`8311516`后，首先使用既有工具重建并validate Registry：19 canonical、0 collision、valid，禁止手工编辑。
2. 对新工作簿的全部交付结果与两份输入缓存逐点比对，既有模型值变化0；没有复算旧模型或重新验收Accepted底稿。CR两VIP页的累计值与指数引用一致。
3. 原生表格引擎只打开合并输出，执行新表引用/换算重算。使用两个临时测试汇率验证CF最低/最高成本的线性响应；CR值、CF绝对指数及等级输出不变，随后恢复空白。测试汇率没有保存为业务输入。
4. 对导出文件核验5页、5图、13系列、1–300主比较范围、实际曲线缓存点数、56个Bet断点、完整4999/5000行明细。0外链、0冻结、0作者/绝对本机目录元数据、0非预期公式错误、0缺失缓存。
5. 五页原生预览逐页视觉复核通过；另核对有测试汇率时三条VIP成本曲线同图显示。修正了图表边界与打印预览末行裁切，成本/奖励小数展示到4位以免微额成本显示成零；没有改变实际值。
6. 工作区Sync仍为ON_DEMAND，provider unavailable/stale 6/conflicts 0，不宣称外部Context同步完成。没有hash、全量无差别扫描、采集、CR配置或CF_collect修改、SVN提交、调参、冻结、发布、PR合并或finalize。Subagents: none。

验证边界：独立ChatGPT Review尚未执行；CF VIP累计属性现已闭合，但未确认固定汇率，不能给出最终CR/CF美元消费高低结论。原有CF普通Bet冲突、highroller条件与历史版本边界继续保留，本轮没有扩展处理。

## 复现

使用既有Python/openpyxl只读解析缓存、Artifact JS生成、本机原生表格引擎校验。三个入口为`build_cr_cf_curves.py`、`render_cr_cf_curves.mjs`、`verify_cr_cf_native.ps1`；复用已有元数据清理函数，旧调用默认行为不变。

```powershell
python projects/cr/数值策划/工具/build_cr_cf_curves.py extract --cr $cr --cf $cf --output $out
# 在能访问既有Artifact依赖的受控目录执行JS；不得将输入JSON或XLSX提交Git。
node "$out/render_cr_cf_curves.mjs" "$out/comparison-inputs.json" $out
./projects/cr/数值策划/工具/verify_cr_cf_native.ps1 -Directory $out
python projects/cr/数值策划/工具/build_cr_cf_curves.py sanitize --cr $cr --cf $cf --output $out
python projects/cr/数值策划/工具/build_cr_cf_curves.py verify --cr $cr --cf $cf --output $out
```

仅在User提供正式固定汇率后，生成/验证命令才使用`--sgd-usd <User指定值>`；在现有工作簿直接填写黄色输入格也会自动更新两条线。完整商业明细与图像仅留受控目录，PR #10保持OPEN、reservation pending-main。
