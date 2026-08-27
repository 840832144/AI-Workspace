# TASK-0015 — Huuuge Lottery 限时活动实时采集与体验证据保全

- Status: Complete
- Owner: User / ChatGPT
- Executor: Codex
- Priority: P0 / time-critical
- Date: 2026-08-27
- Implementation source: `840832144/huuuge-android-research`

## Goal

在当前 Huuuge Lottery 活动结束前，使用现有 Collector 保住一轮完整、可复查的实时证据。

本轮由 User 亲自体验游戏并决定所有游戏内操作，尤其是任何付费、充值、礼包、票券购买或资源消耗行为。Codex 只负责：

1. 检查并启动 Collector；
2. 在看到精确 READY 信号后，按短步骤提醒 User 哪些页面和状态值得观察；
3. 被动记录 User 自己执行的正常游戏行为；
4. Clean Finalize 并确认数据完整；
5. 给出“已捕获 / 未捕获 / 后续可分析”的证据清单。

**本任务暂不做数值拆解、CR 方案、飞书报告或 AI Document Assistant 写入。**等 User 完成体验并明确说“可以开始分析”后，再建立独立任务。

## Confirmed Baseline

当前研究仓库已确认：

- Collector 的被动广泛采集、protobuf decode、Session manifest、自动 lifecycle markers 和 clean finalize 已可用；
- `artifacts/module_catalog/lottery.md` 当前为 cross-cutting/config-only live evidence；
- 已看到 Lottery config、free ticket、ticket balance、ticket rewards、puzzle board、multiplier、expiry 和 bulk cap 等结构；
- 仍缺少专用交互端点的 primary live sample，包括 `LotteryToss`、`CollectFreeTicket`、`NotifyBlackLotteryMissedInfo`、`MiniGameLotteryMachine` 等；
- Raw/value-bearing capture 只保存在本机，不进入 Git、飞书或公共资料。

## Work Order

### Phase A — 立即启动采集

Codex 首先同步并读取：

- `AGENTS.md`
- `CURRENT_STATUS.md`
- `HUUUGE_CODEX_HANDOFF.md`
- `HUUUGE_COLLECTOR_DEPLOYMENT_MANUAL.md`
- `AGENT_DATA_USAGE_GUIDE.md`
- `artifacts/module_catalog/lottery.md`

随后：

1. 不改 Collector 架构；先运行现有 Environment Check / Preflight。
2. 使用现有入口启动一个新的 Lottery 专用 Session。
3. 只有看到精确 READY 成功信号后，才通知 User 开始体验。
4. 记录 Session ID、开始时间和活动 UI 剩余时间；敏感值只留本机。
5. Collector 无法 READY 时，优先使用现有 Repair 流程；仅允许解决真实阻塞的最小修复。
6. 不为启用 Subagent、写文档或整理 Git 耽误活动窗口。

### Phase B — User 自主体验，Codex 只做提示与记录

Codex 的提示必须简短，一次只发一组操作。建议观察：

#### 1. 初始状态

- 活动名称、剩余时间；
- 当前 Lottery 道具 / Ticket 余额和颜色；
- Free Ticket 当前进度、阈值和计时；
- Puzzle Board 状态、颜色和奖励预览；
- Lottery / Puzzle multiplier；
- Ticket shop、bulk play cap、活动进度和关键 UI。

#### 2. 免费或自然可触发流程

- 打开、关闭并切换 Lottery 页面；
- 领取当前可领取的 Free Ticket；
- 查看 Ticket shop，但不替 User 决定购买；
- 执行 User 本来就准备进行的 Toss / Draw；
- 领取自然达到的普通奖励、Puzzle 奖励和完成奖励；
- 自然触发 board completion、new state 或 MiniGame Lottery Machine 时保留前后状态。

#### 3. Slots 与活动道具

User 按自己的体验计划游玩 Slots。Codex 记录：

- Slot 名称、Bet 档位、Spin 数；
- 活动道具是否掉落、数量、颜色 / 类型；
- 免费 Spin、Bonus 或特殊状态；
- 筹码与活动进度的阶段性变化。

本轮不强制 User 为统计样本执行固定 300 / 600 Spin，也不要求主动充值。样本量不足留待后续分析任务说明。

#### 4. 任何付费相关行为

- 付费、充值、礼包、Ticket 购买或显著资源消耗均由 User 自主决定并亲自操作；
- Codex 不点击、不自动化、不替 User 推荐是否购买；
- 每次付费动作前，Codex 停止推进并等待 User 明确说明“由我自行执行”；
- Collector 只被动记录操作前后的正常客户端数据；
- 若 User 不执行付费路径，明确记录该路径未覆盖，不将缺失内容推断为事实。

#### 5. 结束状态

- 最终 Ticket / 道具余额；
- Free Ticket、Board、Multiplier 和活动进度；
- 已领取 / 未领取奖励；
- 最终筹码与活动剩余时间；
- User 自己记录体验感受：节奏、卡点、付费压力、惊喜和不理解之处。

### Phase C — Clean Finalize 与证据检查

1. 使用现有 Stop / Finalize 正常结束 Session，不直接杀进程。
2. 验证 manifest 从 `ready` 到 `stopped`、RPC raw / decoded 数量、decode rate、inventory 和 module catalog 输出。
3. 优先检查是否出现：
   - `AddDciEventRequest.lottery`
   - `AppServer.CollectFreeTicket`
   - `AppServer.LotteryToss`
   - `AppClient.NotifyBlackLotteryMissedInfo`
   - `AppServer.MiniGameLotteryMachine`
   - Slots Spin / Reward / Inventory 相关变化
4. 输出简短证据清单：
   - 已捕获 endpoint / state；
   - User 已执行的动作；
   - 预期但未出现的 endpoint；
   - 后续分析可用的数据范围；
   - 仍需补采的关键缺口。
5. Raw、完整 JSON、账号标识、逐笔余额和截图原件全部保留本机。

## Deliverables

本轮完成条件仅包括：

- 一个 clean-stopped 的 Lottery 专用 Session；
- Session 完整性检查结果；
- 一份简短的本机 / Handoff 证据清单；
- User 的体验记录已保存或明确待补；
- 列出下一阶段可分析的内容和缺口。

**本轮不以生成报告、飞书文档、CR 参数建议或双仓 Git Commit 为完成条件。**时间紧张时，先保证 Capture 和 Clean Finalize。

## Deferred to a Separate Task

只有 User 明确确认体验结束并授权分析后，才另立任务处理：

- 活动道具掉落概率、数量和 Bet 关系；
- 完成进度所需 Ticket、Spin、筹码、时间和付费；
- 奖励结构、期望返还和净消耗；
- 保守 / 中位 / 乐观情景；
- CR 项目可迁移机制与参数建议；
- 脱敏 Git 报告；
- 通过 AI Document Assistant 创建或更新飞书报告。

## Subagent Policy

- 本任务不以 Subagent 为前置条件，默认保持 `OFF`；不得为切换模式延误采集。
- 主 Agent 是唯一操作协调者；不允许子 Agent 接触游戏付费、飞书写入或外部系统写入。
- 采集完成后的分析是否启用 MANUAL，由 User 在后续任务中决定。

## Safety and Boundaries

- 仅观察 User 自己的测试环境和正常游戏行为；不修改请求、奖励、余额或服务器状态。
- 不自动化游戏点击，不代替 User 执行任何付费或高价值资源消耗。
- 不提交 Raw capture、完整响应、账号 / Session 标识、余额明细、APK、二进制或截图原件。
- 不修改 SVN 正式发布包，除非出现阻断采集的真实缺陷且 User 明确批准。
- 不把本轮紧急采集扩大为 Collector 重构、Extractor、Normalized Fact Layer 或 AI Report Engine 开发。

## Handoff Required

采集结束后，Codex只需返回：

- Session ID 与起止时间；
- READY / stopped / decode 完整性；
- 已捕获的 Lottery / Slots 关键 endpoint；
- 未覆盖路径，尤其是付费路径；
- 本机证据位置；
- 是否可以进入下一阶段分析；
- `Subagents: none`（除非后续任务另行批准）。

## Completion Record — 2026-08-27

- 脱敏 Session alias：`LOT-20260827-A`；manifest `stopped`，四个 lifecycle marker 完整。
- 8712/8712 RPC 已解码，LotteryToss 346/346、Spin 588/588、FreeSpin 45/45。
- Raw、decoded values、真实 Session/account 标识保留在本机，未进入 AI-Workspace、Git 或飞书。
- TASK-0018 已使用该证据完成分析并进入 `Review`。
- Subagents: none。
