# Cash Frenzy曲线对照：脱敏交付与验证摘要

- Task: TASK-0036；Date: 2026-09-21；Status: Review，等待ChatGPT审阅。
- 规格：[Cash Frenzy曲线对照](CASH_FRENZY_CURVE_COMPARISON.md)。延续PR #10与原reservation，不新建任务。
- 仅交付本地受控 `CashFrenzy_数值曲线对照.xlsx`。Git保存生成方法、结构和本摘要，不包含商业数值快照、源附件或预览。
- 受控目录：`%LOCALAPPDATA%/AI-Workspace/cr-numerics-20260922/outputs/task0036-cashfrenzy-20260921/`。同目录保留输入坐标、定向验证结果与五页原生预览。

## 来源与选择

数据只来自已下载的历史正式 `CashRoyal数值.xlsx`：`cashFrenzy等级!A:I`及同页驱动/Bet解锁区，`vip加成!F:I`的Frenzy区块。VIP页中的CR区块不读取为计算输入。源附件只读，没有保存、重算或改写。

同套 `03-CR等级+buff新.xlsx` 的 `cashFrenzy等级` / `cashFrenzy下注` / `Sheet1` 定向核对后，确认存在版本差异；主等级表A:I有47行与首选旧总表不同。按照规格优先保留来源更完整的旧总表版本，没有用另一版填补或覆盖数值。文件修改元数据仅存受控索引，不冒充游戏采样日期；历史游戏版本/采样日期仍未注明。

CR v2只作为五页顺序、表列、标题区、蓝色表头与原生折线图的版式参考，不进入CF计算。图表置于数据表右侧，避免覆盖Bet的六列数据。所有可见页均无冻结，原始逐级明细和筛选保留。

## 结构与实际点数

| 可见页（与CR v2同名同序） | 表格记录 | 图中有效数值点 | 缺口处理 |
|---|---:|---:|---|
| VIP_消费门槛 | VIP0–7，共8行 | 2 | VIP2–7累计/新增门槛N/A |
| VIP_膨胀系数 | VIP0–7，共8行 | 2 | VIP1=100%；VIP2–7绝对指数N/A |
| 等级_升级消耗 | 连续1–300级 | 300 | 不向300级后外推 |
| 等级_Bet曲线 | 连续1–300级 | 普通最大Bet244；$1等值300 | 56个内部冲突等级的最大Bet留空 |
| 等级_升级消耗返还 | 连续1–300级 | 300 | 与升级消耗页使用同一分母 |

另有1页隐藏 `SRC_CashFrenzy`，只保存本轮CF输入和原格坐标。图表辅助区保留真正空格，前台显示文本N/A；缺点不补0、不插值、不跨缺口连线。5张原生Excel折线图共6条序列，Bet两条线共用百万金币纵轴，不用第二轴或柱状图。

## 公式与准确含义

- 历史升级消耗USD：原表 `B×C×X2÷Y2÷I`。这是原资料自身的Bet、Spin、抽水与等级价值倍率模型，前台命名为“历史抽水折算升级消耗”；不是实付金额，没有套CR RTP。
- 升级金币奖励USD：原表 `E÷Y2÷I`。升级净成本为同级消耗USD减奖励USD。返还率直接引用消耗页的奖励和消耗，以奖励USD÷消耗USD计算。
- $1等值推荐Bet：按原表美元化公式逆算 `Y2×I`，再统一除以百万缩放因子。该等值未向可下注档取整，不宣称是游戏正式推荐档。
- 普通最大Bet：主表B与同页AJ/AK解锁上限一致时才采用；不一致则最大Bet、缩放值和美元折算全部N/A。历史升级成本仍忠实复现原模型，不擅自用解锁表改写成本。
- VIP：美元换算分母从Frenzy区块原公式提取，未使用CR点数规则。只有VIP0/1无需区分累计/本级；VIP2–7缺累计属性，故不擅自求和或直接当累计。绝对指数公式是当前累计门槛÷固定VIP1累计门槛，VIP1为100%，不是相邻环比，也不是金币加成系数。

## 仍需来源补充

| 缺什么 | 影响 | 由谁补充 |
|---|---|---|
| VIP“经验”是累计门槛还是本级需求的原始定义 | VIP2–7累计/新增消费及绝对指数 | 原资料维护者或User确认正式历史口径 |
| 同一工作表B与AJ/AK在15–19、250–300级不一致的版本依据 | 56个等级的普通最大Bet曲线及其USD折算 | 原资料维护者确认该历史版本采用哪组上限 |
| highroller额外可用条件 | 无法把普通Bet曲线宣称为全模式绝对上限 | 原资料维护者提供配套条件 |
| 历史采样版本、300级以后的完整逐级数据、金币外升级奖励 | 不支持当前版本结论、完整高等级成本或全部奖励价值 | 原资料维护者提供同版本资料 |

这些是来源缺口，不是已经解决的业务结论；本轮不从Web、CR规则或CF_collect运行数据补齐。

## 实际验证

1. 启动后首先使用既有CLI重建并验证Task Registry：19 canonical、0 collision、valid。没有新Task或reservation。
2. 本轮300条历史升级成本/奖励/返还逐点与原缓存复算一致。输出五页逐行校对与原公式依赖通过，保留真实零与N/A的区别。
3. 原生COM重算通过；只在新生成包中临时改变CF金币价值驱动，验证消耗/奖励价值及$1等值方向，返还率不变，随后还原。原附件没有写入。
4. 最终文件：0公式错误、0缺失缓存、0外链、0作者/绝对本机路径元数据、0冻结页；5页/5图/6序列及实际缓存点数通过。
5. 原生导出5页预览及5张图，逐页视觉复核完成：标题/表头完整、无图表覆盖数据、图表同单位、缺点留空、全部可用逐级点入图。移除了逐等级密集竖网格线，保留全部数据点。
6. 本轮仅做新工作簿定向验证和Registry检查，不重跑TASK-0033/0034/0035、不做hash或全量无差别扫描。未调参、改SVN、改CF_collect、采集、上传、发布、合并或finalize。

原生导出曾返回空值但已生成PNG，已按实际文件和图像解码验收；保存时回填的Host作者/目录提示已在输出包中移除。以上为本机结果，未声称独立Review Accepted或云端验收通过。Subagents: none。

## 复现入口

使用既有Python/openpyxl只读提取、Artifact JS生成和本机原生表格引擎；不用新依赖。`$source`指向旧总表，`$out`必须在受控目录，不能指向Git工作区；完整输入和输出不会自动提交。

```powershell
python projects/cr/数值策划/工具/build_cashfrenzy_curves.py extract --source $source --output $out
# 将render_cashfrenzy_curves.mjs复制到可访问既有Artifact依赖的受控目录执行。
node "$out/render_cashfrenzy_curves.mjs" "$out/cf-inputs.json" $out
./projects/cr/数值策划/工具/verify_cashfrenzy_native.ps1 -Directory $out
python projects/cr/数值策划/工具/build_cashfrenzy_curves.py sanitize --source $source --output $out
python projects/cr/数值策划/工具/build_cashfrenzy_curves.py verify --source $source --output $out
```

PR #10保持OPEN；TASK-0036提交ChatGPT Review。原报告Accepted与返还闭环候选历史保留；本竞品表不更改CR当前候选，不代表冻结或发布。
