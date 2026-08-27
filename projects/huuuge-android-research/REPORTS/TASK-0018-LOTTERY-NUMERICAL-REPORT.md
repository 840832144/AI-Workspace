# TASK-0018 — Lottery 数值拆解交付索引

- 状态：Review
- 日期：2026-08-27
- 外部证据 commit：[`bfed5f30e098522ffb98ef5eb7d63e824d68b1c4`](https://github.com/840832144/huuuge-android-research/commit/bfed5f30e098522ffb98ef5eb7d63e824d68b1c4)
- 飞书：[`Huuuge Lottery 活动数值拆解（2026-08-27）`](https://gfok27asqq.feishu.cn/docx/IK5adiJyWoHVJzxlovEcjxiWnO3)，企业内可编辑已回读验证
- Subagents: none

## Git 交付

- [`报告入口`](https://github.com/840832144/huuuge-android-research/tree/bfed5f30e098522ffb98ef5eb7d63e824d68b1c4/reports/lottery/20260827_lottery-ticket-puzzle)
- [`完整数值拆解`](https://github.com/840832144/huuuge-android-research/blob/bfed5f30e098522ffb98ef5eb7d63e824d68b1c4/reports/lottery/20260827_lottery-ticket-puzzle/LOTTERY_NUMERICAL_BREAKDOWN.md)
- [`玩法与逻辑`](https://github.com/840832144/huuuge-android-research/blob/bfed5f30e098522ffb98ef5eb7d63e824d68b1c4/reports/lottery/20260827_lottery-ticket-puzzle/PLAYFLOW_AND_LOGIC.md)
- [`Evidence Matrix`](https://github.com/840832144/huuuge-android-research/blob/bfed5f30e098522ffb98ef5eb7d63e824d68b1c4/reports/lottery/20260827_lottery-ticket-puzzle/EVIDENCE_MATRIX.md)
- [`CR 建议`](https://github.com/840832144/huuuge-android-research/blob/bfed5f30e098522ffb98ef5eb7d63e824d68b1c4/reports/lottery/20260827_lottery-ticket-puzzle/CR_RECOMMENDATIONS.md)

## Review 摘要

- `Confirmed L3`：Finalize、346/346 Toss、933 张票消耗、阈值 7 的免费返还、直接奖励、拼图完成、六次升级后的票余额变化和总账闭环。
- `Estimate L3`：六次变化合计 +16 Bronze 的升级因果归因；Spin payload 没有直接 Lottery ticket grant。
- `Hypothesis L0`：高 Bet 可能仅通过加快升级间接影响单位时间票获取。
- `Decision proposal`：免费阈值实验、升级奖励节奏、拼图完成奖励波动控制和下一轮证据计划。

本索引不复制 Raw、decoded values、玩家明细、绝对余额或完整业务数据。详细数值与限制以外部 commit 固定报告为准。
