# TASK-0036 数值体验工作簿：master 与飞书展示版

当前产物等待 ChatGPT Review，原数值报告 Accepted 保留。本次依据 [PR #10 最新 User 输入](https://github.com/840832144/AI-Workspace/pull/10#issuecomment-5724897864)，覆盖此前“全部自包含、每模块单页”的展示方案。未修改 TASK-0035 数值候选，尚未冻结或发布。

[飞书展示版](https://gfok27asqq.feishu.cn/wiki/UZD8wLpQKicKV7kcorIcNIb8nwd)。本机受控目录：`%LOCALAPPDATA%/AI-Workspace/cr-numerics-20260922/producer-master-20260918/`。master与`source/r7013/`需要整包搬移；展示版可单独使用。

## 旧资料的结构分析

已通过飞书 CLI 只读检查“系统功能”根及全部子节点：19个页面、17份XLSX附件结构。脚本、视频和采集附件只分类，未执行或作为当前数值输入。旧 `CashRoyal数值.xlsx` 共15个Sheet，宋体11号，常用“左侧配置档位、右侧体验/累计/横向比较”，主要公式习惯为跨Sheet引用、INDEX/MATCH、VLOOKUP、SUMIF/SUMIFS；旧文件有外链，不回存或重算旧附件。

| 旧主表Sheet | 本次沿用的阅读组织 |
|---|---|
| 基础金币、vip加成、BET | 等级/VIP/Bet条件分开，原配置与体验并列 |
| 等级体验表、等级+buff | 业务阶段概览可下钻逐级完整记录；加成独立解释 |
| 旧cr等级、cashFrenzy等级、档位膨胀 | 仅参考横向/累计布局；历史及竞品值不进入计算 |
| 美金金币档位、礼包加成 | 金额、价值类型、VIP类型和等级为独立筛选条件 |
| 卡包、免费奖励 | 条件概率、奖励与累计分开；领取/掉落分母明确 |
| 挖宝、挖宝-基础积分、挖宝-难度系数 | 仅参考阶段成本与奖励布局，不增加9.22活动组合 |

等级沿用的阅读标签为1/10/20/30/40/50/75/100/125/150/300/400/500/600/700/800/900/1000/1100/1200/1400/1600/1800/2000/3000/4000/5000。它们只决定展示节点，不携带旧表奖励、经验、概率或价值参数。另加入当前升级方式、VIP入账、奖励类型/道具和金币换算档位的变化点。连续逐级门槛变化保留明细，不把经验门槛解释成预计Spin或天数。

| 系统功能下的模块 | 已检查内容与本次处理 |
|---|---|
| 数值推导 | 主表15个Sheet，作为布局参考 |
| 免费奖励 | 领取条件/奖励/对比布局，当前福利取r7013 |
| 等级+buff | 多版本22个Sheet，旧倍数/经验不套用 |
| 卡包 | 新旧版本8个Sheet，现值来自r7013卡册/卡包表 |
| 老虎机关联：CR机台建模规范、调控 | 分母/条件分层；调控空页不补证据，不开展程序审计 |
| 疯狂探险 | 两份任务配置与体验附件，映射当前FrenzyMission |
| 竞品调研：弹球公园、tycoon翻地块 | 原始记录/媒体/脚本仅分类，竞品数值不导入 |
| 小游戏：薯片、挖宝、矿工、幸运7、新CR弹球 | 全部子模块及多版本附件已过结构；本次活动只薯片+777 |
| 未命名 | 空页面，明确无内容 |
| 建造 | 9个Sheet及报表结构；沿用已关闭规则，残留不计有效收入 |

## 当前工作簿结构

26张前台页：总览；货币、VIP、BET/RTP、等级、Buff、美金金币档位、福利、商城/Pass、卡包、薯片、777、常驻各有概览和完整明细；Unknown单列。隐藏SRC保存原始格引用、字段注释/坐标及版本清单，CALC保存计算。

- 概览按完整条件或业务阶段分组；36组Spin及各VIP/福利条件完整展示。价格概览按money/priceType/vipType分组，不跨单位平均；薯片/777按相邻相同阶段成本和奖励分组，保留全部变化点。
- 明细保留完整适用配置原行/原字段，包括5000级成长和全部金币价格档位，不删尾部。多个配置段各有筛选表，冻结前6行和首列；等级明细提供阶段分组，概览及总览可跳转。
- `CR_9.22_数值体验表_r7013_MASTER.xlsx`只在受控本机使用。37份实际所需trunk工作簿通过`svn export -r7013 URL@7013`导出；SRC外链直接指向`source/r7013/`原工作簿Sheet/单元格。没有引用working copy、dev/101或旧附件。
- 本工作簿公式或CALC计算派生结果，可沿“体验→CALC→SRC相对外链→源格”追溯。原文件只读，使用原缓存，不重算或保存源表；空值、明确零值、Unknown分别保留。
- `CR_9.22_数值体验表_r7013_飞书展示版.xlsx`从最终master已验证缓存生成，全部数值/文本内嵌，无外链、无公式更新负担，保留筛选/冻结/分组和工作簿内跳转。它是展示快照，不是修改数值或重算的入口。
- 两版使用同一`TASK-0036-r7013-master-display-20260918`版本清单。完整值只留受控包和公司内部飞书；master、原始源包和完整日志不上传。

旧14页候选及其产物评审属于历史。受评文件的公式计数与后续本地候选不同，不用历史计数替代最终XLSX实际计数。当前计数与验证以[WORKBOOK_VALIDATION.json](WORKBOOK_VALIDATION.json)为准。

## 生成与验证方法

生成器位于`projects/cr/数值策划/工具/`：Python负责固定源读取、业务公式/版式计划、外链和验证；`render_producer_workbook.mjs`仅为当前已配置Artifact Tool的渲染适配器。使用已配置运行时的Node、openpyxl（只读源）、lxml（保留OOXML命名空间）及原生Excel COM；不安装新依赖。

```text
python producer_workbook_sources.py --lock <受控source-lock.json> --catalog <WORKBOOK_STRUCTURE.json> --output <受控包目录>
python build_producer_workbook.py --analysis <Accepted分析目录> --sources <受控包目录> --output <受控包目录>
node --max-old-space-size=10000 render_producer_workbook.mjs <workbook-plan.json> <受控包目录>
python verify_producer_workbook.py --plan <workbook-plan.json> --xlsx <MASTER.xlsx> --native --portable-check
node render_producer_workbook.mjs <native-preview-plan.json> <受控预览目录> --preview-only
```

导出阶段保持37个相对源文件与master的目录关系；整个目录一起搬移，不能只发master单文件。版本清单记录导出时间和实际固定revision，不含内部SVN地址。原生Excel保存可能补写绝对路径/作者，因此最后保存后清理元数据，再检查最终ZIP中的XML；不在清理后再次保存master。飞书上传只选择展示版。

本次验证限定于新交付物：原格引用、969个既有结果的工作簿重现、空/零/Unknown及RTP边界、两版缓存一致性、外链解析/搬移、元数据与页面阅读操作。没有重跑TASK-0033/0034/0035的Accepted盘点或模型测试，没有hash、无关全量扫描或原始表重算。完整状态奖EV、成长速度、实付等9组Unknown不因此关闭。

按User本轮禁止无关全量扫描的要求，不运行遍历整个CR库的`build_catalog.py`或`validate_repository.py`；没有增删Git内源工作簿，原目录无需重建。改为本轮Python语法/变更Markdown链接、Git diff及既有Task Registry重建/validator检查。生成器的完整外链/Excel/飞书路径已经在实际交付物运行，不以语法检查冒充端到端。

## 复核与撤回

ChatGPT复核重点为：源版本与相对路径、概览分段是否便于策划阅读、完整明细与原格追溯、展示版与master一致，以及Unknown/计价分母没有改变。原数值Accepted不等于本次工作簿Accepted。

需要撤回时用新的Git更正提交并将本展示版标为历史；不重写共享分支，不覆盖旧附件或原配置。PR #10保持OPEN，reservation pending-main；不调参、不提交SVN、不冻结/发布、不合并或finalize。Subagents: none。
