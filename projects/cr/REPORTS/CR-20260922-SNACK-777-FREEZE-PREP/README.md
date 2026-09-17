# CR 9.22 薯片 + 777 现值方案与冻结候选

## 1. 文档信息与结论

- Task：[TASK-0035](../../../../tasks/TASK-0035-CR-0922-SNACK-777-FREEZE-PREP.md)；执行：Codex；业务负责人：User；评审：ChatGPT；状态：Review，尚未Accepted。
- 适用：9.22已选择的薯片 + 777；2026-09-17制作，供最晚2026-09-19的冻结决策参考。
- User补充目标为“没有改动”。本候选**保留trunk r7004现值，数值变更0项**，没有调参目标或优化建议。没有修改源配置、提交SVN、正式冻结或发布。
- 两活动当前无剩余业务规则Gate；候选仍待ChatGPT Review和后续User明确授权。规则闭合、候选评审、正式冻结是不同状态。

## 2. 目标与范围

交付现值方案、零数值变更清单、受控候选及最小必要验证。复用TASK-0033盘点和TASK-0034 Accepted规则/计算；拳击、挖矿不纳入，G03/G12/G16在本组合不触发。其他原非阻塞缺口不因本Task升级为前置，不开展技术、线上或运营审计。

[活动组合](https://github.com/840832144/AI-Workspace/pull/7#issuecomment-5709745139)、[forceTurn完整定义](https://github.com/840832144/AI-Workspace/pull/7#issuecomment-5709928125)、[合并及新Task授权](https://github.com/840832144/AI-Workspace/pull/7#issuecomment-5709949277)为正式输入。原[业务规则](../../../../tasks/support/TASK-0034/USER-DECISIONS-20260917.md)继续适用。User本轮答复“没有改动”确定零数值变更方案。

## 3. 配置来源与候选清单

2026-09-17 **14:32:41北京时间**（06:32:41Z）只读取得公司SVN HEAD **r7004**。对下表14个明确路径逐一检查r6961:7004，全部无变化；随后统一按`-r 7004`和`@7004`导出，使用既有XLSX只读提取器。候选实际源版本是r7004，非把旧附件改名为新版本。没有目录全量扫描或哈希检查。

| 源表 / Sheet | 阅读范围与字段 | 选中行数 | 本轮动作 |
| --- | --- | ---: | --- |
| QuestPickGet / Sheet1 | questType=4/5；Id、Type、BetId、Probability、Points | 76 | 保留；获取概率及上下文 |
| QuestPointsCheatSheet / Sheet1 | questType=4/5；Id、level、vip字段 | 1596 | 保留；命中积分关联 |
| QuestGetLevel / Sheet1 | questType=4/5；Id、LevelUpPoints、num | 546 | 保留；连续积分阶段门槛与产量 |
| QuestInitItem / Sheet1 | questType=4/5；itemId、initItemCount、itemExchChip | 2 | 保留；初始道具/结束回收配置 |
| SnackDropItemCfg / Sheet1 | boxNum、luck、各奖励概率和数量字段 | 60 | 保留；状态奖池 |
| SnackAddLuck / Sheet1 | 使用量区间、addLuck | 5 | 保留；Sheet2/3空页只保留源结构 |
| QuestJackpotCfg / Sheet1 | Type=4/5；Id、NeedCount、权重、Reward字段 | 6 | 保留；收集奖励；空奖励字段不补0 |
| SnackPassReward / Sheet1 | category、levelId、LevelExp、Reward字段 | 30 | 保留；免费/付费同levelId共享门槛 |
| StrikeLucky / Sheet2 | gridId、round、inout、hitWeight、item字段、forceTurn | 108 | 保留；普通格/特殊格按正式规则解释 |
| StrikeLuckyRound / Sheet2 | round、分圈cost字段、cherry/seven收集字段 | 3 | 保留；每次付费抽奖和收集配置 |
| Item / item | 上述两活动初始道具及骰子的itemID、名称、类型 | 3 | 只读依赖；源名称不强行改写 |
| ItemExchange / item | 对应3种道具的itemId匹配 | 0 | 本表未匹配；不表示其他来源产消为0 |
| PriceCheatSheet / Sheet1 | 共用价值查档依赖，完整源文件受控保留 | — | 不重跑价格查档，不生成全量价格阅读层 |
| Activity / desc | id=1033/1034；none、type及活动字段 | 2 | 只读关联；不设定或改写开启时间 |

共14个XLSX、16个Sheet（含2个空Sheet）；阅读层2437行、35900个命名字段位置。共用源文件内其他系统的行仅随只读依赖文件保留，不进入本次调整或模型。PriceCheatSheet在机器清单中selected_rows=0表示本轮不展开，不能解释为源表空。

受控`现值阅读层.csv`逐字段给出表名、Sheet、Excel行、复合行键、单元格、现值、源注释、单位提示、公式和错误缓存；`action=KEEP`表示建议值等于现值。`null`保留为空值；不重算外链和公式缓存。单位提示只是索引，以源注释和下节明确口径为准。

## 4. 业务规则、单位与适用条件

| 环节 | 本候选采用的正式口径 | 源值与规则的边界 |
| --- | --- | --- |
| 连续积分 | 命中计分；达档只扣当前门槛；余量继续且可跨多档；末档循环，末档num=0不再产道具 | 源“升级后清0”旧注释原样保留；分析按User决定，不据此修改注释或宣称运行时已符合 |
| 薯片开盒 | 每次耗1开盒道具；多开顺序执行；每次只中一种奖励；主池不返该道具 | 不直接将源概率字段相加归一；数量、状态、概率字段均保持现值 |
| 薯片Jackpot与Pass | Jackpot期内可重复收集/领奖；Pass单独计；免费/付费同levelId门槛，购买可追领已达等级 | 付费轨空门槛仍为空；分析引用免费轨，不能据此填源表 |
| 777 | 普通格命中后移除，清完普通格进下一圈，三圈后下一轮；特殊格永久保留并临时给予一次内圈随机奖励；骰子是抽奖资源 | 不把格子数当付费次数；不沿用旧“每格一次清盘”作为完整周期成本 |
| forceTurn | 当前圈实际付费抽奖计数；普通格N若前N−1次未自然命中，第N次强制；此前已中则不强制；下一圈/轮重置；特殊格永不参与 | 保留现N及源注释；新定义在规则层落库。格子特殊标识未由本轮新增推断，不做程序验收 |
| 常规机器RTP | USD Bet>1用85%，≤1用95% | 沿用User规则；不覆盖独立的新手/活动特殊配置，不在本Task改RTP |

积分是积分，道具数量是对应道具单位；QuestPickGet的Probability按源注释分母1000。相对权重只在明确当前有效奖池时除以该池权重和。PriceCheatSheet的money为USD×100，配置价值不等于实付；奖励类型/查档键须按具体源表定义，不跨表推定。卡包奖励保留类型与ID，不在本轮重算包价值。

## 5. 公式与Accepted证据复用

固定同一Type/BetId/等级/VIP上下文、单次命中积分g>0、独立命中概率p>0时：累计阶段Spin期望为`ceil(sum(T_i)/g)/p`，相邻累计期望之差为边际阶段成本。T_i是各档积分门槛；不能改回逐档清零后分别向上取整。546条薯片/777阶段记录从TASK-0034 Accepted结果筛选引用，**证据revision=6961、适用revision=7004、recomputed=false**，两者由14表无变化证据关联。它们是固定示例上下文，不是所有玩家或完整活动期的平均值。

薯片开n次（n>0）主池开盒道具毛耗=n、主池净耗=n、主池该道具返还率=0/n；初始赠送、结束回收、Jackpot和Pass分别列示，不能把局部0返还推广到全活动。777付费抽奖资源毛耗为`Σ cost(round,inout)`，抽奖资源净耗=毛耗−同单位返还，返还率=返还/毛耗（分母>0）；完整周期次数分布未在本轮复算，保留为条件式，不填旧清盘数。两活动资源不相加冒充统一返还率。

毛下注W、机器返还R、机器净耗W−R、活动奖励与真实支付各自独立。仅在RTP规则确实适用且单位一致时使用`E[机器净耗]=W×(1−RTP)`；不由它推算未知实付。

复核入口：

```text
python projects/cr/数值策划/工具/prepare_snack777_freeze.py --input <受控任务目录> --prior <TASK-0034/round2> --output <新的受控候选目录>
```

工具只整理由既有extract_xlsx.py读取的14表，筛选Accepted结果并演示forceTurn定义；不连接SVN、不修改XLSX、不重跑TASK-0033或旧模型。复跑输出必须为新的受控目录。

## 6. 变更清单与验证

**数值变更清单为空（0项）**。无配置增删、数值调整、SVN提交清单或覆盖命令。候选以固定版本的只读源文件和规则说明组成，完整数值不进入public Git。

本轮验证：14个导出回执均为r7004；指定路径相对r6961无变化；选中2437行保留源坐标和空值，选中字段错误缓存0；0数值变更；Accepted阶段记录仅选questType4/5；forceTurn的8个输入/边界示例通过。圈/轮重置在示例中作为输入约定，不代表已验收游戏状态机。

源错误计数只适用于本次选中字段，不替代TASK-0033历史异常记录。未重跑已Accepted数值验收、源公式重算、全目录扫描、hash、catalog或validate_repository全量校验；按User要求采用本任务定向验证、Registry、变更链接和diff检查。验证摘要见[VALIDATION.json](VALIDATION.json)。

## 7. 冻结结论与证据限制

**可提交现值候选Review，尚未正式冻结。** 组合和forceTurn已正式闭合；拳击/挖矿条件不触发。新候选没有新业务问题需要User回答。薯片概率字段到单奖过程的映射、777特殊格标识和完整周期EV等原分析精度边界继续保留为Non-blocking，不据此伪造期望值或扩大审计范围。

Review通过仍不自动授权SVN、冻结或发布。若后续出现相关源变更，只复核变化路径和受影响关系，再更新一致版本候选；不能把本次读取时间之外的最新性当已验证。

## 8. 交付位置与复核顺序

受控根目录：`%LOCALAPPDATA%/AI-Workspace/cr-numerics-20260922/snack-777-freeze-20260917/`。

1. 本文：范围、正式输入、单位、公式、0变更和授权边界。
2. 受控`TASK-0035-CHATGPT-REVIEW-PACK-r7004.zip`：候选说明、脱敏版本锁、只读源XLSX及candidate目录。源表14个，不含allocation token、内部URL或完整历史包。
3. `candidate/冻结候选清单.csv`、`现值阅读层.csv`、`数值变更清单.csv`：版本、范围、单元格和现值。
4. `candidate/Accepted阶段成本引用.csv`、`Accepted规则与Pass引用.json`：保留r6961证据身份及r7004无变化适用关系。
5. `candidate/validation.json`：本轮定向结果和forceTurn示例。ChatGPT应注明其实际复核范围，未独立复跑不能写成独立验证。

本轮未写源配置，无需SVN回滚；撤回候选时保留历史证据，通过Git更正/后续提交处理，不强推或删除旧资料。Subagents: none。

## 9. Git收口与历史

PR #7于2026-09-17以merge commit `051a55195a6a483ce198fe432fe7af29d92444b3`合入main。确认TASK-0034 canonical和三轮Review进入main后，原reservation已finalized。TASK-0034 Complete元数据随本新分支更新，其原6 Closed / 4 Conditional / 12 Non-blocking Matrix保留为组合决定前的Accepted快照。

从最新main完整枚举30个tasks文件，Registry验证后由allocator分配TASK-0035。本任务保持Review，reservation pending-main，等待ChatGPT Review，不提前finalize。2026-09-17 v0.1：首次交付r7004零数值变更候选。
