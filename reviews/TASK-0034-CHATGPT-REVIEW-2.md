# TASK-0034 — ChatGPT Review Round 2

## 已发布评审原文

## TASK-0034 — ChatGPT Review Round 2

**结果：Needs changes**

Reviewed commit：`761b08cd34994598d5777db2cb3474a979b9f6e6`。

本轮按 User 要求只做最小必要复核：核对 PR #7 当前 Matrix、受控 Round 2 增量包和受影响规则，不重跑 TASK-0033、catalog、全量扫描或哈希。正式业务决定的应用、连续积分模型、Pass 共用门槛、777 特殊格、拳击抽组、挖矿点击/连锁与 G20 范围本身均未发现计算问题。

### 已确认通过
- 当前 22 Gate 的表内计数确为 7 Closed / 2 Conditional / 13 Non-blocking；正式 User 输入已写入模型。
- G07 连续积分采用累计门槛首次到达，旧“逐档清零/逐档取整相加”已退出当前模型。
- G13 共享门槛和追溯付费奖励正确应用。
- G03 原 5 处 money=1500 缺档在移除建造币后仍属于非建造币金币奖励，保留为条件问题是正确的。
- 受控包明确保留挖矿源配置缺口：地图 id=1..12，但 `QuestMinerStageReward` 仅有 id=1..3（各含 round），没有用取模/旧值/0补 id4..12。
- 受控包同时记录当前源配置仍有 27 个建造币奖励槽位被“分析层排除”：拳击 Pass 12、拳击奖池 6、挖矿通关奖 9。User 的决定是“本版建造模块关闭，建造币奖励先去掉”，但本 Task 尚未获授权修改源配置。

### 必须修改：冻结 Gate 分类要区分“规则闭合”和“配置已满足规则”
当前 Matrix 写“最多2类条件问题：G09、G03”，这不足以支持冻结决策。因为四活动仍都保留候选，只要对应活动被选中，以下两类源配置差异会直接影响冻结：

1. **挖矿通关奖励覆盖不足**：User 已确认 `map.id = QuestMinerStageReward.id`、最大 id=12、12关结束；但 r6961 的通关奖励只覆盖 id1..3。若选择挖矿，id4..12 的通关奖励在冻结前必须补齐或由 User 明确决定“这些关无通关奖励”。因此 G12 不能仅写 Closed；至少应是 `Conditional`（规则 Closed，但配置覆盖在选择挖矿时阻塞）。
2. **建造币奖励尚存在于源配置**：User 已明确本版建造模块关闭、建造币奖励去掉；当前只是在分析模型里排除了 27 个槽位，源表未改。若选择拳击或挖矿，相关候选配置在冻结前仍需移除这些奖励。建议把 G16 改为 `Conditional`，或在 G10/G12/G13 中明确同等的“候选被选中时配置落实阻塞”，但不能继续列为纯 Non-blocking/Closed。

因此可以继续保留“**无无条件业务规则阻塞**”这个结论，但“**只有2类 Conditional**”需要修正。当前至少还应显式包含：
- 选777 → G09 forceTurn；
- 需要比较拳击/挖矿缺档价值 → G03；
- 选挖矿 → G12 id4..12 通关奖励配置覆盖；
- 选拳击或挖矿 → 建造币奖励源配置移除（可落在 G16 或对应活动 Gate）。

### 修订要求
只修改 Matrix、Task/Status/Handoff/报告中的 Gate 状态与冻结结论，并保留“规则层已闭合”的说明。**不要重算数值、不要重跑 TASK-0033、不要做哈希、不要全量扫描，也不要改源配置。**

修订后目标应是：清楚区分 `业务规则 Closed` 与 `候选配置可冻结`，让 User 在最终选四活动中的两个时能一眼看到仍需执行的配置动作。其余本轮计算和定向证据无需返工。

PR #7 保持 OPEN，reservation 继续 pending-main；不合并、不 finalize、不提交 SVN、不调参、不执行冻结或发布。

## 落库记录（Codex，2026-09-17）

- Kind: review
- Canonical task: [tasks/TASK-0034-CR-0922-FREEZE-GATES.md](../tasks/TASK-0034-CR-0922-FREEZE-GATES.md)
- Project key: CR
- Decision: Needs changes
- Reviewer: ChatGPT
- Review date: 2026-09-17
- Subagents: none

来源：[PR #7 已发布Round 2](https://github.com/840832144/AI-Workspace/pull/7)，review ID `PRR_kwDOUEpZyM8AAAABN8zm-Q`，发布于2026-09-17 04:44:38 UTC，受评commit `761b08cd34994598d5777db2cb3474a979b9f6e6`。GitHub记录类型COMMENTED，业务结论Needs changes。以上完整正文原样保存，第一轮评审保留；本轮没有把前轮计算证据当作重新执行的验证。

User已明确授权本轮仅修Gate状态：G12改Conditional；建造币源配置未移除落G16 Conditional；保留G03/G09，规则Closed放在说明列。状态履历为Review → Changes Requested（Round 2）→ Review（状态修订后，等待下一轮轻量Review）。没有修改或重新执行分析工具，没有改配置、提交SVN、冻结、合并或finalize。
