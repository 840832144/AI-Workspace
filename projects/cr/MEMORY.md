# CR 长期记录入口

## 2026-09-17 当前决定 — 薯片+777零数值变更候选

PR #7已合并main（051a551），TASK-0034原reservation已finalized；6/4/12保留为历史Accepted快照。User后续正式选择薯片+777并闭合forceTurn：当前圈付费抽奖计数，普通格N前未自然命中则第N次强制，提前命中取消，换圈/轮重置，特殊格排除。[正式输入与当前方案](REPORTS/CR-20260922-SNACK-777-FREEZE-PREP/README.md)。

新TASK-0035按allocator登记，User答复“没有改动”，保持现值，0数值变更。2026-09-17定向检查14表无变化后锁定r7004；不将r6961历史证据重新标成新读取，不重跑Accepted模型。当前Review，未提交SVN、未冻结、未发布；新reservation仍pending-main。下节旧待合并/待组合/待forceTurn描述属于当时历史。


## 历史 — 2026-09-17 User后续决定与Round 3冻结Gate

[Round 3](../../reviews/TASK-0034-CHATGPT-REVIEW-3.md)已Accepted（受评d8f1b72）；仅接受Gate交付，6 Closed / 4 Conditional / 12 Non-blocking保留，尚未冻结或发布。PR #7仍等待User明确合并授权，原reservation pending-main。

[正式输入唯一原文](../../tasks/support/TASK-0034/USER-DECISIONS-20260917.md)已落Git。四活动积分按溢出连续结算；末档循环且num=0停产道具。薯片/拳击Pass共用同levelId门槛且可追溯付费奖励；本版建造模块关闭、奖励从分析层排除。不要沿用旧清零假设或777每格一次清盘总量作为现行成本。

当前[Matrix](REPORTS/CR-20260922-FREEZE-GATES/FREEZE_GATE_MATRIX.md)经[Round 2](../../reviews/TASK-0034-CHATGPT-REVIEW-2.md)修正为6 Closed / 4 Conditional / 12 Non-blocking：G09选777补forceTurn、G03剩余缺档需价值比较、G12选挖矿补齐id4–12奖励或User明确无奖励、G16选拳击/挖矿移除源建造币奖励。业务规则Closed保留在说明列；已决定但未落实的配置动作必须列条件阻塞，不能仅写证据限制或用分析层排除代替。当前不改源表、不冻结，不用旧值或0补奖励。

## 2026-09-17 User决策 — 常规USD Bet边界

User在[TASK-0034](../../tasks/TASK-0034-CR-0922-FREEZE-GATES.md)启动请求中明确：USD Bet=1归95%。常规规则保持>1为85%、<=1为95%；不重新设计RTP。该决定不自动覆盖新手/活动特殊配置，不证明trunk字段/注释或配置优先级已符合，也不授权改配置、SVN提交、调参、冻结或发布。历史TASK-0033中的“等于1待确认”保留为当时记录，当前使用本决策。

- [项目记忆](数值策划/知识库/项目记忆.md)：领域事实、版本边界和研究结论。
- [问题经验](.agents/skills/cr-capture-lessons/references/lessons.md)：失败、纠正、解决情况及来源。
- [迁移决策](../../docs/adr/ADR-0008-CR-Single-Repository.md)：单仓库日常入口与公司 SVN 边界。
- [迁移报告](../../docs/migrations/CR-MIGRATION-20260916.md)：源 SHA、历史保留、路径映射和回滚。

旧文件中的 cr_design、CR_design、D:\cr_design 和旧 SVN revision 是当时 provenance，按迁移映射阅读，不把旧机器路径作为当前配置。当前资料路径为 AI-Workspace/projects/cr；日期附件不代表当前环境。
