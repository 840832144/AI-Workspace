# TASK-0015 — Huuuge Lottery 限时活动采集与数值拆解

- Status: Ready
- Owner: ChatGPT
- Executor: Codex
- Priority: P0 / time-critical
- Date: 2026-08-27
- Implementation source: `840832144/huuuge-android-research`

## Goal

在当前 Huuuge Lottery 活动结束前，优先保住一次完整、可复查的实时证据，并基于采集结果完成一版面向游戏策划的数值拆解：

1. 活动道具从 Slots 等来源的掉落概率、掉落数量、颜色/类型与 Bet 关系；
2. 完成活动各阶段所需的道具、Spin、筹码消耗与时间；
3. 奖励结构、预期返还、净消耗和关键随机性；
4. 可迁移到 CR 项目的机制、参数区间和风险建议；
5. 生成 Git 中的脱敏报告，并通过 AI Document Assistant 写入同一篇企业内可编辑飞书云文档。

User 报告任务发布时活动剩余约 5 小时。**先采集，后美化；不得因写文档、开发通用功能或多 Agent 配置而错过活动窗口。**

## Confirmed Baseline

当前研究仓库已确认：

- Collector 的被动广泛采集、protobuf decode、Session manifest、自动 lifecycle markers 和 clean finalize 已可用；
- `artifacts/module_catalog/lottery.md` 当前为 cross-cutting/config-only live evidence；
- 已看到 Lottery config、free ticket、ticket balance、ticket rewards、puzzle board、multiplier、expiry 和 bulk cap 等结构；
- 仍缺少专用交互端点的 primary live sample，包括 `LotteryToss`、`CollectFreeTicket`、`NotifyBlackLotteryMissedInfo`、`MiniGameLotteryMachine` 等；
- Raw/value-bearing capture 只保存在本机，不进入 Git、飞书或公共资料。

## Work Order

### Phase A — 立即保住实时证据

Codex 首先同步并读取：

- `AGENTS.md`
- `CURRENT_STATUS.md`
- `HUUUGE_CODEX_HANDOFF.md`
- `HUUUGE_COLLECTOR_DEPLOYMENT_MANUAL.md`
- `AGENT_DATA_USAGE_GUIDE.md`
- `artifacts/module_catalog/lottery.md`
- `artifacts/module_catalog/slots.md`
- `artifacts/module_catalog/rewards.md`
- `artifacts/module_catalog/liveops_events.md`

随后：

1. 不改 Collector 架构；先运行现有 Environment Check/Preflight。
2. 使用 `HUUUGE_COLLECTOR.cmd` 启动一个新的 Lottery 专用 Session。
3. 只有看到精确 READY 成功信号后才让 User 开始操作。
4. 记录 Session ID、开始时间、活动 UI 显示的剩余时间；不在 Git 记录账号、余额明细或其他敏感值。
5. 如果 Collector 无法 READY，先使用现有 Repair 流程；只有真实 blocker 才允许最小修复，修复不得替代本轮采集目标。

### Phase B — User 操作清单

Codex 给 User 提供短步骤，每完成一组动作即确认。至少覆盖：

#### 1. 初始快照

- 活动名称与剩余时间；
- 当前 Lottery 道具/票券余额及颜色；
- Free Ticket 当前进度和阈值；
- Puzzle Board 当前格子、颜色和完成状态；
- Lottery / Puzzle multiplier；
- 奖励预览、完成奖励、Ticket shop、bulk play cap；
- 初始筹码、活动进度和关键 UI 截图。

截图和手工观察记录保存在本机 Session/工作目录；提交到 Git 或飞书前必须脱敏。

#### 2. Lottery 专用交互

在正常游戏允许的范围内尽量触发：

- 打开、关闭并切换 Lottery 所有页面；
- 领取 Free Ticket（若当前可领取）；
- 查看 Ticket shop，但**不得购买付费商品，除非 User 再次明确批准**；
- 执行 Lottery Toss/Draw：最低 3 次，建议 10 次；如有多种颜色，尽量覆盖不同颜色；
- 领取普通奖励、Puzzle Board 奖励和完成奖励；
- 若自然达到条件，触发一次 board completion / new state；
- 若存在 MiniGame Lottery Machine，完成至少一次合法交互；
- 记录每次操作前后道具、Board、Multiplier 和奖励变化。

#### 3. Slots 掉落样本

为了判断活动道具是否随 Bet 缩放：

- 尽量固定同一台 Slot、相同模式和相近时段，减少外部变量；
- 选择低 / 中 / 高 3 个 Bet 档；
- 每档目标 100 个有效 Spin，最低总样本 300 Spin；
- 同时以“至少 30 次非零活动道具掉落”为补充目标；
- 若总计 600 Spin 后仍不足 30 次掉落，停止扩样并标记样本不足；
- 记录每档 Bet、Spin 数、筹码消耗、掉落次数、掉落数量、颜色/类型、免费 Spin/特殊状态；
- 不为了采样主动充值或购买礼包；资源不足时保留已有证据并报告。

如果现有数据表明活动道具并非来自普通 Spin，应立即根据实际 endpoint/事件调整采集动作，而不是机械完成 300 Spin。

#### 4. 结束快照

- 最终 Ticket/道具余额；
- Free Ticket、Board、Multiplier 和活动进度；
- 已领取和未领取奖励；
- 最终筹码；
- 活动剩余时间；
- User 对体验、卡点、节奏和付费压力的简短主观记录。

#### 5. 到期后可选补采

如时间允许，在活动结束后重新进入游戏并开一个短 Session，尝试捕获 missed-info、过期补发、自动结算或残余道具处理。此步骤不能影响到期前的主采集。

### Phase C — Clean Finalize 与数据检查

1. 使用现有 Stop/Finalize 正常结束 Session，不直接杀进程。
2. 验证 manifest 从 ready 到 stopped、RPC raw/decoded 数量、decode rate、inventory 和 module catalog 输出。
3. 优先检查并列出：
   - `AddDciEventRequest.lottery`
   - `AppServer.CollectFreeTicket`
   - `AppServer.LotteryToss`
   - `AppClient.NotifyBlackLotteryMissedInfo`
   - `AppServer.MiniGameLotteryMachine`
   - Slots Spin / Reward / Inventory 相关变化
4. 如果专用 endpoint 仍未出现，明确记录“执行了什么动作、预期看到什么、实际缺少什么”，不得把 schema 推断写成 live-confirmed。
5. Raw、完整 JSON、账号标识、逐笔余额和截图原件保持本地；Git 只提交聚合、脱敏、可复查结果。

## Analysis Requirements

优先复用现有脚本、字段表、module catalog 和本机工具。只有现有方法无法完成时，才允许新增最小、可复用的分析脚本；不得为本任务重构 Collector 或开发通用 Report Engine。

### 1. 掉落模型

至少计算：

- 每档 Bet 的有效 Spin 数；
- 有掉落 Spin 占比；
- 每 Spin 平均掉落数量；
- 每 100 Spin 掉落数量；
- 每单位筹码消耗的道具产出；
- 颜色/类型分布；
- Bet 与掉落概率、数量的关系；
- 样本量、置信区间或至少给出样本不确定性说明；
- Free Spin、Bonus、特殊 Slot 状态是否采用不同规则。

### 2. 进度与消耗模型

还原：

- 单次 Toss/Draw 消耗；
- Free Ticket threshold、progress 规则和冷却；
- Puzzle Board 格子、颜色、奖励和完成条件；
- Lottery/Puzzle multiplier 的生效方式；
- bulk play cap 与批量消耗；
- 完成一轮 / 一板 / 全活动所需 Ticket、Spin、筹码和时间。

输出至少三种情景：

- 保守：低掉落 / 低奖励；
- 中位：基于当前样本；
- 乐观：高掉落 / 高奖励。

不能从现有证据推导全活动时，给出已确认区间和缺口，不伪造精确值。

### 3. 奖励与返还模型

建立奖励表：

- 每次 Toss/Draw 奖励；
- Puzzle 单格奖励；
- Board 完成奖励；
- 免费 Ticket、Multiplier 和附加奖励；
- 固定奖励、随机奖励、条件奖励分开；
- 重复奖励、奖励池或权重若不可见，单独标记。

至少给出：

- 已确认奖励总量；
- 样本平均奖励；
- 以筹码或可比较价值折算的预期价值（若无法统一定价，保留多币种表）；
- 奖励返还 / 筹码消耗；
- 奖励返还 / 活动道具消耗；
- 净消耗、回收率和完成压力。

### 4. CR 项目建议

不要只写“值得参考”。必须给出可执行建议：

- 建议采用 / 不采用的机制；
- 道具掉落与 Bet 的推荐关系；
- 每阶段目标时长、Spin 数和道具需求；
- 推荐奖励返还区间；
- 免费进度、保底、追赶和防挫败机制；
- 付费点与免费路径的边界；
- 可能造成资源通胀、付费压迫或体验断层的风险；
- 对 CR 当前功能可直接验证的下一步实验。

所有数字必须标记来源：`Confirmed`、`Estimate`、`Hypothesis` 或 `Decision proposal`。

## Deliverables

在 `huuuge-android-research` 中建立本轮脱敏结果目录，例如：

```text
reports/lottery/20260827_<event_slug>/
├── README.md                 # 报告入口
├── EVIDENCE.md               # Session、endpoint、字段和证据等级
├── DROP_ANALYSIS.csv         # 聚合掉落数据
├── PROGRESSION_MODEL.csv     # 阶段、需求和情景
├── REWARD_MODEL.csv          # 奖励与返还
└── CR_RECOMMENDATIONS.md     # 可执行迁移建议
```

实际文件可根据现有仓库规范调整，但必须保持：原始数据本地、聚合结果可复查、策划报告中文可读。

同时通过 AI Document Assistant 创建或更新：

```text
《Huuuge Lottery 活动数值拆解（2026-08-27）》
```

飞书报告至少包含：

1. 一页结论；
2. 活动循环与进度图；
3. 道具掉落；
4. 完成消耗；
5. 奖励与返还；
6. 三种情景；
7. CR 可迁移方案；
8. 证据等级与未确认项；
9. 附录：Session 和聚合表引用。

默认企业内可编辑；创建前先搜索防重，写入后回读正文与权限。返回最终飞书 URL。

## Subagent Policy

- 本任务**不以 Subagent 为前置条件**，当前默认模式可以保持 `OFF`；不得为了切换模式延误实时采集。
- 只有在实时采集完成以后、父会话确认不是 full-access / `--yolo` / 宽松权限，并由 User 明确切换到 `MANUAL` 时，才可把独立只读分析交给 `repo_explorer`、`evidence_test_verifier` 或 `reviewer`。
- 主 Agent始终是唯一写入者，飞书 READ/WRITE 只由主 Agent执行。
- 未使用时在 Handoff 写 `Subagents: none`。

## Safety and Boundaries

- 仅观察 User 自己的测试环境和正常游戏行为；不修改请求、奖励、余额或服务器状态。
- 不使用付费购买、充值、自动化点击或超出正常游戏范围的操作，除非 User 单独明确批准。
- 不提交 Raw capture、完整响应、账号/Session 标识、余额明细、APK、二进制或截图原件。
- 不修改 SVN 正式发布包，除非发现会阻断采集的真实缺陷并由 User 确认。
- 不把本轮紧急研究扩大为 Collector 重构、Normalized Fact Layer、通用 Extractor 或 AI Report Engine 开发。

## Acceptance Criteria

- 在活动结束前完成一轮 Lottery 专用 READY → 操作 → clean finalize Session；若客观失败，保留失败证据和明确 blocker。
- 初始/最终状态、Lottery 交互和 Slots 掉落样本均有可核对记录。
- 专用 endpoint 至少被触发一个；若没有，动作与缺失证据被明确记录。
- 掉落、进度消耗、奖励返还和三种情景完成，所有重要结论标记证据等级。
- 给出可直接用于 CR 方案评审的参数建议，而非只有机制描述。
- Git 中只有脱敏聚合结果；Raw 保持本机。
- 飞书报告成功创建或更新、企业内可编辑并回读验证。
- 更新 Huuuge `CHANGELOG.md`、`CURRENT_STATUS.md`、`TASKS.md`、`COLLAB_LOG.md` 和 `HUUUGE_CODEX_HANDOFF.md`。
- 更新 AI-Workspace 的项目 Status / Memory / Handoff，记录证据基线和最终报告链接。
- 两个仓库提交并推送，工作区干净，等待 ChatGPT Review。

## Handoff Required

完成后返回：

- 活动名称、剩余/结束时间；
- Capture Session ID、decoded/total、关键 endpoint；
- 样本 Spin、掉落次数、Lottery 交互次数；
- 四项核心结论：掉落、消耗、返还、CR 建议；
- Git commits；
- 飞书 URL；
- Confirmed / Estimate / Hypothesis 清单；
- 未解决缺口和建议的下一个 Task；
- `Subagents: <names>` 或 `Subagents: none`。
