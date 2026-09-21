# CR 数值调优候选：POP VIP门槛 + Cash Frenzy等级体验 + 5x档位膨胀

- Parent Task: TASK-0036
- Status: Changes Requested / User Approved
- Date: 2026-09-21
- Scope: 生成CR定向调参候选与曲线验证；允许修改受控候选VipCfg / LevelCfg / PriceSetting，不提交SVN、不冻结、不发布

## User最终决定

1. **VIP消费门槛**：参考POP配置，CR前10个VIP完全对标POP Tier1–Tier10的消费门槛。
2. **VIP膨胀/权益**：先不动，保持CR当前配置；本轮只改消费门槛，不复制POP的Daily Bonus、Chip Package Bonus、VIP Period等权益。
3. **升级难度**：按Cash Frenzy等级体验做，最终仍然扩展到CR 5000级。
4. **等级膨胀**：完全参考Cash Frenzy；User判断当前CR配置应该已经如此，因此先验证，若一致则不改。
5. **档位膨胀**：按**5倍**；由`PriceSetting`承担该调整。
6. 本轮先做候选、diff和曲线复核；**不得SVN commit/发布**，等待User确认后再进入正式提交。

## A. POP VIP消费门槛

### App截图证据

POP VIP Tier门槛（TPs to Obtain）：

| POP Tier | 累计TP |
|---:|---:|
| 1 | 0 |
| 2 | 75 |
| 3 | 300 |
| 4 | 1,600 |
| 5 | 5,500 |
| 6 | 22,000 |
| 7 | 60,000 |
| 8 | 250,000 |
| 9 | 750,000 |
| 10 | 2,000,000 |

POP商城截图可见USD→TP：
- $1.99 → 160 TP
- $4.99 → 400 TP
- $9.99 → 800 TP
- $19.99 → 1,600 TP
- $49.99 → 4,000 TP
- $99.99 → 8,000 TP

这些商品显示设计标称约为 **80 TP / USD**（.99价格造成实际比率轻微偏差）。本轮消费门槛对标使用**标称80 TP/USD**，不按单一促销SKU的实际小数比率偏移门槛。

因此POP目标累计消费约为：
- Tier1 $0
- Tier2 $0.9375
- Tier3 $3.75
- Tier4 $20
- Tier5 $68.75
- Tier6 $275
- Tier7 $750
- Tier8 $3,125
- Tier9 $9,375
- Tier10 $25,000

### CR换算与VipCfg候选

CR已确认口径：**$1 = 100 VIP点**。

User要求“CR前10个VIP完全对标POP”，本轮按字面映射：
`CR VIP1..VIP10 ↔ POP Tier1..Tier10`。

目标`VipCfg.needExp`（累计）= POP累计消费USD × 100：
- VIP1 = 0
- VIP2 = 93.75 → 配置整数候选按四舍五入 **94**
- VIP3 = 375
- VIP4 = 2,000
- VIP5 = 6,875
- VIP6 = 27,500
- VIP7 = 75,000
- VIP8 = 312,500
- VIP9 = 937,500
- VIP10 = 2,500,000

VIP11–VIP15本轮先不改，保留当前值，除非前10档修改导致累计门槛不再单调；如出现后续VIP门槛低于VIP10，必须停下并报告，不得静默重排VIP11+。

**重要验证Gate**：CR存在VipPrivilege VIP0基线，而POP Tier1门槛为0。先按User字面生成VIP1=0候选；必须验证客户端/服务端升级逻辑对0门槛是否安全、是否会导致初始化自动升级/循环/状态异常。若0门槛不安全，停止在候选验证并报告，不得自行改成“CR VIP0↔POP Tier1”映射。

### 不改内容

本轮POP只用于**消费门槛**：
- 不复制POP VIP Period
- 不复制Daily Bonus Multiplier
- 不复制Chip Package Bonus
- 不复制Priority Support / Personal Host
- 不改CR当前VIP商店金币倍率、任务/成就等权益

## B. 升级难度：Cash Frenzy体验拉到5000级

目标不是直接复制CF原始经验数值，而是让CR的**升级消耗体验曲线**参考Cash Frenzy，同时保留CR 5000级结构。

Reuse-first：
1. 读取旧正式`CashRoyal数值.xlsx`的`cashFrenzy等级`、`旧cr等级`、`等级体验表`、`档位膨胀`及相关公式。
2. 读取已交付`CashFrenzy_数值曲线对照.xlsx`的CF 1–300级升级消耗曲线。
3. 先恢复历史表中是否已有“CF 300级 → CR 5000级”的映射/拉伸逻辑；**有现成逻辑就复用，不自行发明插值算法**。
4. 以“每级升级消耗USD/机器理论净耗”体验为目标反推CR `LevelCfg.levelUpExp`，保留现有`levelUpType`规则和5000级数量。
5. CR等级升级成本复算继续使用当前已确认的等级计算链：推荐Bet/levelExp/95%升级RTP；不要改变RTP规则来凑曲线。

如果历史正式表没有唯一的300→5000映射，则：
- 先只生成2–3种映射候选曲线和差异说明；
- **不写LevelCfg候选值**；
- 回报User选择，不自行决定拉伸方法。

## C. 等级膨胀：完全参考Cash Frenzy

User认为当前CR应该已实现。

Codex只做验证：
- 定义并复现旧正式表中“等级膨胀”的原业务口径；
- 对比当前CR配置与Cash Frenzy目标曲线；
- 若一致：明确标记`No Change`，不修改源表；
- 若不一致：输出差异位置/倍率/影响，**先不自动调整**，因为User预期“目前配置就是”。

不得把“等级膨胀”和“升级难度”混成同一指标。

## D. 档位膨胀：5x，修改PriceSetting

User明确要求档位膨胀改为**5倍**。

实施要求：
1. 先从旧`档位膨胀`表和当前配置恢复“档位”的业务维度、阶段边界及其在`PriceSetting`中的对应行/字段。
2. **5x指相邻业务档位的基准价值膨胀为5倍**，不是把PriceSetting全表数值整体×5。
3. 只调整承担金币/美金价值档位膨胀的PriceSetting数据；钻石、特殊货币、活动道具、VIP权益等非目标维度不得连带修改。
4. VIP倍率保持本轮开始前CR当前配置，不因5x档位膨胀改变。
5. 同一档位内各价格SKU的相对价格/金币关系保持原逻辑；改变的是档位基准。
6. 输出清晰的before/after阶段表：档位、等级/条件、旧基准、新基准、相邻倍率、受影响PriceSetting行数。

如果实际承担等级档位膨胀的真相源不是PriceSetting而是PriceCheatSheet/其他表，停止写入并报告证据；不得为了满足文件名要求改错表。

## E. 交付

受控候选至少包含：
1. `VipCfg.xlsx`候选（仅前10VIP门槛）
2. `LevelCfg.xlsx`候选（仅当CF→5000映射可唯一恢复）
3. `PriceSetting.xlsx`候选（5x档位膨胀）
4. 三份源表的逐单元格diff摘要
5. 新曲线Excel：`CR_调优候选_vs_CF_POP_数值曲线.xlsx`
6. 验证摘要：门槛单调性、5000级完整性、升级消耗曲线、等级膨胀No Change检查、5x档位检查、公式/缓存错误

新曲线至少保留：
- VIP消费门槛：POP目标 vs CR调优前 vs CR候选
- VIP商城金币倍率：CR调优前=CR候选（应重合；本轮不改）
- 升级消耗/等级：CF体验、CR调优前、CR候选
- 最大Bet/$1等值Bet：用于解释升级成本变化
- 等级升级消耗返还：CR调优前/候选
- 档位膨胀：旧基准 vs 5x候选

## F. 验收与边界

- 原r7013源表只读保留；修改写到独立受控候选副本/工作副本。
- 不修改CF历史附件。
- 不改CF_collect、不采集、不启动模拟器/Root/Frida。
- 不提交SVN、不冻结、不发布、不覆盖当前正式配置。
- 不重跑TASK-0033/0034/0035无关全量验收。
- User确认候选后，正式SVN写入/提交作为下一步明确授权执行。
