# CR 卡包与卡片价值分析资料

本资料供 GPT 研究卡包、普通卡、金卡、Joker 的价值计算方法。包含功能说明、原始配置 Excel、可检索 CSV、字段注释、历史策划公式和核验结果。

- 整理日期：2026-09-15。
- 主分析基线：CR SVN **trunk r6880**。另附同 revision 的 dev 对照，禁止交叉混算。
- 当前讨论季：`CardAlbumCfg.id=2`，`themeId=3`，`seasonName=AUTUMN GLOW`，业务第三季。配置时间为 `2026-08-28 09:00:00` 至 `2026-10-27 08:59:59`，按服务器时间解释；服务器时区仍需上线信息确认。
- 这些是版本库配置及代码审阅事实，尚未证明线上正在使用该 revision。
- 原始来源是 User 于 2026-09-15 要求上传的私有 `840832144/cr_design`；2026-09-16 已批准随历史公开迁入 `AI-Workspace/projects/cr/`。本目录保存当时分析附件，不作为当前程序配置维护入口，不恢复全量配置同步体系。

## GPT 阅读顺序

1. [功能与执行规则](01_功能与执行规则.md)：先理解开包、集册、重复卡、兑换与赛季重置。
2. [数据与价值计算口径](02_数据与价值计算口径.md)：理解单位、计算方法、已有数据和缺口。
3. [给 GPT 的分析任务](03_给GPT的分析任务.md)：可直接复制为提问。
4. [卡包规格速查](04_卡包规格速查.md)：29 种卡包、79 条第三季规则的阅读入口。
5. 按需读取 `data/trunk/` 的 CSV，遇到解释问题查 [字段字典](data/field_dictionary.json) 和 `config/trunk/` 原始 Excel。CSV 的 `_excel_row` 对应原表行号。

## 配置下载与文本入口

每类均提供 trunk、dev 两份。全部来源、读取 revision、文件最后修改 revision、SHA-256 见 [sources.json](sources.json)。完整数据行保留在 Excel/CSV，不仅是截图或样例。

| 类别 | 配置表 | 用途 |
|---|---|---|
| 赛季 | CardAlbumCfg、CardAlbumTheme | 赛季时间、普通/高阶目标、大奖、星星系数、展示主题 |
| 开包 | CardPack、CardGroup | 卡包内规则及权重、卡组按天数与进度过滤 |
| 卡片与集齐 | CardList、CardChapter | 每张卡的类型/星级/玩家权重/交易属性、章节奖励与补缺参数 |
| 重复卡与社交 | CardStarTrade、CardTradeCfg | 星星换包门槛、共用冷却、交易/赠送/求卡限制 |
| 获取 | SlotsCasinoDropCards、Cardget | Spin 掉包、付费附赠/排除配置 |
| 换算及入口依赖 | PriceCheatSheet、SlotsCasinoBetList、PayDiamond、Item、ItemExchange、SysUnlock | 金币换算、Bet字段、商品与道具映射、未解锁替代奖励 |
| 关闭替代与模拟参考 | CardActivityClose、CardCollectSimulator | 功能关闭时的活动奖励替代、已有模拟参数；模拟参数不代表真实玩家分布 |

- [trunk 原始 Excel](config/trunk/) / [trunk 文本数据](data/trunk/)
- [dev 原始 Excel](config/dev/) / [dev 文本数据](data/dev/)
- [历史策划表文本](planning_reference/) / [原策划工作簿](../../../数据源/策划源表/卡包数值调整.xlsx)
- [两环境差异](checks/environment_diff.json) / [配置与文本核验](checks/validation.json)

## 已确认的关键边界

- 普通册 **19章、152张**；升级高阶后清空本季卡片，重收 **21章、168张**，不是只再收16张。
- 本季有 **138张普通卡、30张金卡**。三种 Joker 单独配置在 `seasonId=-1`，不计入168张。
- 章节补缺代码存在，但本季21章的启用参数均不成立，不能假定当前存在补缺保底。
- 原始核心配置和文本核验通过；存在 **16个规则槽位**的候选容量不足风险。不能把表中标注张数直接当作每包必得张数。
- `rewardType=17` 的数字是美元折算值×100，最终奖励为游戏金币；并非可提取现金或卡片市场售价。
- **换算需特别检查**：本季6500、10000奖励金额没有精确换算行，当前trunk代码会向上命中20000档。不能用配置金额直接代替实际金币奖励，详见价值口径文档。
- 只提供配置与规则，不提供线上用户明细，也没有编造全服平均卡价。

## 复核与可复现

在本目录执行：

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
python tools/check_bundle.py
```

36 个配置文件的摘要与来源清单一致，845,935 个 CSV 单元格与原始 Excel 的缓存值一致。公式与缓存缺失扫描为0，**未进行 Excel 重算**。状态覆盖检查对第三季天数0—59、唯一卡数0—168、普通/高阶状态进行区间等价检查，每个环境4290个模式状态；无正权重卡组缺失、无章节候选完全为空，102个模式状态存在候选数量不足。状态数不是玩家数或出现概率。

Subagents: none

迁移后的 `tools/check_bundle.py` 默认跳过文件哈希，直接核对 Excel/CSV 内容和业务引用。`sources.json` 的原有哈希仅保留来源；只有明确指定 `--verify-hashes` 才核对。
