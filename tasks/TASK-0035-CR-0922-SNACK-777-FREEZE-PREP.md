# TASK-0035 — CR 9.22 薯片 + 777 数值调整与冻结准备

- Status: In Progress
- Execution status: 已登记；User确认没有数值改动；待相关trunk定向freshness check后制作现值冻结候选
- Project key: CR
- Owner: User
- Executor: Codex
- Priority: P1 / 2026-09-19 冻结决策依据
- Date: 2026-09-17
- Updated: 2026-09-17
- User decision: Approved（启动新任务、制作方案/清单/候选及验证；补充“没有改动”）
- Allocation relationship: new
- Related tasks: TASK-0033, TASK-0034
- Subagents: none

## Goal

只为9.22已选择的薯片 + 777交付数值方案、变更清单、冻结候选和验证材料，提交Git后交ChatGPT Review。User在本轮明确“没有改动”，因此保留实际选定版本的现值，数值变更清单应为0；不自行设置优化目标、幅度或留存/付费指标。TASK-0033盘点与TASK-0034 Accepted业务规则复用，不续写旧任务。

## 正式输入与边界

- [组合决定](https://github.com/840832144/AI-Workspace/pull/7#issuecomment-5709745139)：薯片+777；拳击/挖矿本轮不纳入，G03/G12/G16不触发。
- [forceTurn正式闭合](https://github.com/840832144/AI-Workspace/pull/7#issuecomment-5709928125)：进入当前圈后按实际付费抽奖次数计数；普通格forceTurn=N时，前N-1次未自然命中则第N次强制命中；此前已自然命中则不再强制；进入下一圈/下一轮计数重置；特殊格永远不参与forceTurn。
- [合并与新任务授权](https://github.com/840832144/AI-Workspace/pull/7#issuecomment-5709949277)及User本轮请求：只做相关trunk定向freshness check，发生变化采用最新一致revision。User后续答复“没有改动”是本轮数值目标，原配置保持现值。
- 薯片G07/G08/G13和777 G09规则已由User闭合。业务Gate闭合不代表现配置已正式冻结，也不证明运行时实现；不开展程序/线上/运营/支付技术审计。
- 不改原始源配置、不提交SVN、不调参、不执行正式冻结或发布，不扩展到拳击/挖矿或其他系统。当前只允许受控本机候选/分析层与Git文档写入；后续高影响动作另等User明确授权。

## 登记、并发与前置

- 起点为最新main `051a55195a6a483ce198fe432fe7af29d92444b3`，PR #7已merge，canonical TASK-0034确认进入main后以原reservation返回finalized。
- 完整枚举tasks/的30个文件；Registry scan/validate：17 canonical、0 collision、valid，6项既有legacy提示。active TASK-0018（Huuuge）/0025（Top Tycoon）和远端0027/0028/0030/0031 reservations不覆盖本次CR范围；0033已Complete、0034已Accepted且已合并，不另占其范围。
- 正式allocator返回TASK-0035 / pending-main；token仅受控本机保存，禁止提前finalize。独立linked worktree，分支codex/cr-snack777-freeze-prep。
- Workspace Sync：ON_DEMAND、provider unavailable、stale 6、conflicts 0；Git为真相源，没有扩大外部权限或发布云文档。
- 公司trunk版本读取时间、实际revision、受影响路径待定向检查后记录；尚未假定r6961仍有效。只读相关依赖，不做无关全量扫描或哈希。

## 方案与交付计划

1. 读取相关trunk最新revision和相对r6961路径差异；锁定单一revision后读取薯片/777获取、消耗、奖励、Pass及共用价值/道具关系，排除其他Quest类型，禁止混revision。
2. 复用Accepted证据，将无变化关系沿用原证明；有变更仅更新受影响部分。User已确认的连续积分、薯片单次单奖/不返道具/重复Jackpot、Pass共享门槛及777流程/forceTurn作为规则层独立记录。
3. 输出保持现值的数值方案、0项数值变更清单、逐文件/Sheet/字段候选映射、受控冻结候选与只读验证记录。配置美元/金币/道具、毛下注/机器净耗/实付分别记录，未知不补0。
4. 验证只覆盖新候选版本一致、范围与源引用、零改动约束和新闭合forceTurn边界；不重复TASK-0033全量验收或TASK-0034已Accepted计算，不把规则测试当运行时证明。
5. 同步Task/Status/Handoff和报告，生成Registry并提交PR交ChatGPT Review。完整数值、SVN内部地址、源表留受控目录；public Git只放脱敏方案、方法、清单摘要、工具及治理记录。

## 验收与回滚

- 可从受控候选定位每个相关源文件及固定revision；新方案不包含拳击/挖矿数值，数值变更为0，正式冻结状态为未执行。
- ChatGPT可复核版本、范围、规则、单位、变更清单和验证边界；本Task状态不预先写Accepted。
- 本轮无SVN写入，因此无需源配置回滚；候选未获认可时保留上一已Accepted材料，撤回/替换Git候选文档，不删除旧证据、不强推或改变权限。
