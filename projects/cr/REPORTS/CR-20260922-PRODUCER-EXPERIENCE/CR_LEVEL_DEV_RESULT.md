# TASK-0036 — 等级同级对标、尾部拟合与dev提交

2026-09-21 · **CR dev r7237已提交并回读** · VIP暂存 · 尚未冻结或发布 · Subagents: none。

## 最终User输入

User批准等级先提交dev、VIP暂存；随后纠正“不能拉抻，已有的数据和等级完全对标，后续的进行拟合”。最终口径覆盖此前短暂选择B及原A/B拉伸候选。旧候选保留追溯，不能继续作为提交输入。

- CF历史正式表实际有1–300级，每一级的机器理论净耗目标与CR同级对应，不压缩、不重复、不重排、不以拟合替换已知点。
- 301级起才外推；5000为现有等级终点，只有1→5000的4999次升级需要门槛候选。
- 本轮只提交`LevelCfg.levelUpExp`，没有VIP、PriceSetting、PriceCheatSheet、Bet、奖励或活动配置写入。User的dev授权不代表trunk、正式冻结、发布、PR合并或finalize授权。

## 拟合与配置落表

CF旧正式表的原关系为：机器理论净耗USD＝Bet金币×Spin×净损率÷基础金币美元比÷等级金币倍率。末段250–300级Bet相同，将成本乘回等级倍率后，连续51点在浮点精度内严格线性；300级美元成本下降来自倍率换档，不作为“难度下降”趋势外推。

令`u(L)=CF净耗USD(L)×CF等级倍率(L)`，固定300级锚点，取：

`b=Σ[(L−300)×(u(L)−u(300))] / Σ[(L−300)²]`，L=250..300。

- L≤300：目标净耗直接使用同级CF历史原值。
- L=301..4999：目标净耗=`[u(300)+b×(L−300)] / CR现有等级金币倍率(L)`。
- 保留CR现有等级膨胀，包括其换档造成的成本变化；后续不是CF实测等级，也不是新编金币倍率。目标的归一趋势持续增长，不要求含换币档的美元成本单调。
- 预计Spin=`MAX(1,ROUNDUP(ROUND(目标净耗/(当前最大解锁BetUSD×5%),10),0))`。
- Spin型门槛=预计Spin；经验型门槛=向上取整(预计Spin×原levelExp)。再从门槛按原升级方式反推实际Spin、实际机器净耗及返还率。
- 5000级原门槛及其他字段原样保留，不把其终点值转为整数或产生5000→5001计算。

等级RTP仍95%，推荐Bet/EXP规则、金币价值和升级奖励沿用既有模型。拟合窗口来自最后可识别的同Bet连续阶段，未自行设留存、付费或回收目标。

**误差边界**：前300级目标值300/300同级对应；整数Spin落表后142级实际成本精确一致，其余向上取整，最大相对差3.174603%。不能把配置的整数分辨率隐藏为“实际完全相等”。受控明细逐级保留目标、实际、误差和返还分母。

## dev与并发核对

- 只读锁定CR dev r7232；通过既有WC元数据确认项目、dev路径与UUID，URL和账号信息只保存在受控证据中。
- 定向导出LevelCfg、SlotsCasinoBetList、SlotsCasinoBetUnlock、PriceCheatSheet四表。同一revision读取，未更新用户原工作副本。
- LevelCfg等级/升级方式/原门槛、Bet/levelExp、普通最大Bet解锁字段、money=100/priceType=17/vipType=1的等级金币倍率与r7013模型依赖一致，可复用已验结果。
- 两环境并非所有字段相同：dev额外保留薯片/777活动解锁内容，trunk BetList有空掉落字段。按源注释确认这些不是本次升级输入，并保留这些表原状。没有拿trunk全表覆盖dev。
- 建立仅含LevelCfg的独立稀疏工作副本。沿用`svn_submit.py`禁止项，使用该工作副本的严格定向策略：必须CR dev同UUID、只有LevelCfg修改、仅授权门槛格、其他值零差异、远端四表最近修改版本未变化。没有绕过冲突、缺失或临时文件检查，也没有运行不适用于配置工作副本的设计库全量校验。
- dry-run只有1项M；execute先update再核验上述条件，确认远端依赖未变化后提交，未覆盖其他人的修改。

## 实际提交与验收

| 项目 | 结果 |
|---|---|
| SVN提交 | **r7237，CR dev** |
| 文件/字段 | 仅`LevelCfg.xlsx / Sheet1 / levelUpExp` |
| 单元格 | C5:C5003，共4999格；5000级终点及其他字段不变 |
| 远端回读 | r7237文件与已验证候选逐格一致，差异0 |
| 提交日志 | 仅1条文件修改路径；UTF-8中文说明完整，作者已在受控记录回读 |
| 工作副本 | 干净，无冲突/待提交项 |
| 公式/缓存 | 新曲线0错误、0缺缓存；斜率变化仅影响尾部、前300不变，恢复通过 |
| 图表/元数据 | 2原生折线图，各3系列，300/4999全点；0外链/冻结/作者或绝对目录残留 |
| 视觉 | 前300、完整5000级曲线及300/301边界明细已复核 |
| 治理 | 原Task/PR/reservation沿用；Registry首步与收尾由CLI重建validate |

仅验证配置dev提交、回读和数值计算，不宣称客户端/服务端运行效果、正式冻结或发布已验收。VIP候选继续在原受控目录等待User确认；本轮未重算VIP或提交VIP。

## 受控交付与复现

目录：`%LOCALAPPDATA%/AI-Workspace/cr-numerics-20260922/outputs/task0036-level-dev-20260921/`。

- `CR_等级逐级对标及尾部拟合_dev.xlsx`：概览、完整等级明细及隐藏来源；新当前等级曲线。
- `candidate/LevelCfg.xlsx`：实际提交的等级配置；`LevelCfg.remote-r7237.xlsx`为远端回读证据。
- `LevelCfg_actual_diff.csv`、`level-validation.json`、`precommit-validation.json`、`svn-result.json`：逐格变更及校验。
- `dev-before/`、`dev-source.local.json`及本地SVN记录：受控版本/回滚证据，不进Git。

生成器为`build_cr_level_dev.py`与`render_cr_level_dev.mjs`；原生验证为`verify_cr_level_dev_native.ps1`。输入只使用既有已验证CF/CR缓存和同版dev导出。`prepare`生成独立输入，Artifact生成配置/曲线，原生重算后`verify`比较；`verify --root`额外检查工作副本身份/范围/并发，供现有svn_submit流程使用。旧build_cr_tuning的A/B产物只作历史重现，不能作为当前提交候选。

无文件hash、全量扫描或旧Accepted任务重复验收。完整商业值和内部URL不入public Git。

若User后续批准回滚，应在最新dev上按r7237这4999格diff反向应用，先检查后续他人变更，再提交新的SVN revision；不能整表覆盖最新dev、回滚其他文件或更改trunk。当前没有执行回滚。
