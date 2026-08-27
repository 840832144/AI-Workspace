# TASK-0018 — Lottery 数值拆解交付索引

- 状态：Review Round 1 修订完成，等待 Review Round 2
- 日期：2026-08-27
- Review Round 1：[`Needs changes`](../../../reviews/TASK-0018-HUUUGE-LOTTERY-CHATGPT-REVIEW-1.md)
- 外部证据 commit：[`4a5dddf7782307c6a8f368c9f1dc6390eec6f65b`](https://github.com/840832144/huuuge-android-research/commit/4a5dddf7782307c6a8f368c9f1dc6390eec6f65b)
- 飞书：[`Huuuge Lottery 活动数值拆解（2026-08-27）`](https://gfok27asqq.feishu.cn/docx/IK5adiJyWoHVJzxlovEcjxiWnO3)，原文档原位替换，企业内可编辑已回读验证
- Subagents: none

## Git 交付

- [`报告入口`](https://github.com/840832144/huuuge-android-research/tree/4a5dddf7782307c6a8f368c9f1dc6390eec6f65b/reports/lottery/20260827_lottery-ticket-puzzle)
- [`完整数值拆解`](https://github.com/840832144/huuuge-android-research/blob/4a5dddf7782307c6a8f368c9f1dc6390eec6f65b/reports/lottery/20260827_lottery-ticket-puzzle/LOTTERY_NUMERICAL_BREAKDOWN.md)
- [`玩法与逻辑`](https://github.com/840832144/huuuge-android-research/blob/4a5dddf7782307c6a8f368c9f1dc6390eec6f65b/reports/lottery/20260827_lottery-ticket-puzzle/PLAYFLOW_AND_LOGIC.md)
- [`购买记录`](https://github.com/840832144/huuuge-android-research/blob/4a5dddf7782307c6a8f368c9f1dc6390eec6f65b/reports/lottery/20260827_lottery-ticket-puzzle/PURCHASES.csv)
- [`Evidence Matrix`](https://github.com/840832144/huuuge-android-research/blob/4a5dddf7782307c6a8f368c9f1dc6390eec6f65b/reports/lottery/20260827_lottery-ticket-puzzle/EVIDENCE_MATRIX.md)
- [`策划建议`](https://github.com/840832144/huuuge-android-research/blob/4a5dddf7782307c6a8f368c9f1dc6390eec6f65b/reports/lottery/20260827_lottery-ticket-puzzle/CR_RECOMMENDATIONS.md)
- [`Extractor 与 7 个测试`](https://github.com/840832144/huuuge-android-research/tree/4a5dddf7782307c6a8f368c9f1dc6390eec6f65b/tools/analysis/lottery)

## Round 1 修改结果

- 主报告按策划阅读顺序重组为玩法、实际行为、票来源、消耗与进度、奖励、付费与价值、策划结论和技术附录。
- 588 次普通筹码下注、45 次 Free Spin 与四次真实货币购买已经分开表述，不再用付费概念描述普通下注。
- 四次真实货币购买全部成功，合计 54.43 SGD、763 张 Lottery 票和 235 loyalty points。
- 每个购买礼包都有其他奖励，因此表观每票成本只用于描述礼包，不代表独立票价、RTP、ROI 或长期付费回报。
- 117.516 只保留在技术附录，定义为不含充值购买的筹码奖励输出与普通 Spin 筹码成本的描述性比值。
- Extractor 新增购买链提取和 `PURCHASES.csv`；7/7 测试覆盖购买字段、失败链闭合、普通下注命名与礼包限制。

## 仍然成立的证据边界

- 已确认：Finalize、346/346 Toss、933 张票消耗、阈值 7 的免费返还、四次购买的金额/币种/礼包发放、直接奖励、拼图完成、六次升级后的票余额变化和总账闭环。
- 本次样本观察：六次变化合计 +16 Bronze 的升级因果归因；Spin payload 没有直接 Lottery ticket grant。
- 待验证：不同等级区间、下注档与完整活动周期下的稳定分布。
- 策划建议：只作为后续方案或实验建议，不替代线上配置或长期回报结论。

## 飞书验证

- 搜索确认唯一同名文档后使用替换接口；未创建第二份文档。
- 最终回读 367 blocks、4568 个正文字符、单一标题，策划章节顺序和四条购买记录完整。
- 权限回读为企业内可编辑。

本索引不复制 Raw、decoded values、玩家明细、真实 Session/account/request/product/store/order 标识、绝对余额、完整余额轨迹或完整业务数据。详细数值与限制以外部 commit 固定报告为准。
