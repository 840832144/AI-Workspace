# TASK-0018 — Huuuge Lottery 活动数值拆解报告

- Status: Ready
- Owner: User / ChatGPT
- Executor: Codex
- Priority: P0 / business analysis
- Date: 2026-08-27
- Governance source: `840832144/AI-Workspace`
- Evidence / implementation source: `840832144/huuuge-android-research` 与本机已 Finalize 的 TASK-0015 Capture
- Related task: `TASK-0015 — Huuuge Lottery 限时活动实时采集与体验证据保全`
- Concurrent task: `TASK-0016` 正在 AI-Workspace 中修订；本任务不得覆盖其工作区或未提交变更

## Goal

基于 User 已完成的 Huuuge Lottery 活动体验和 TASK-0015 采集证据，生成一份可复查、面向游戏策划的数值拆解报告，覆盖：

1. 玩法结构与完整玩家循环；
2. 状态、消耗、进度、奖励和随机逻辑；
3. 可从当前单实例 / 单账号样本确认的规律；
4. Slots 活动道具、Lottery Toss、Puzzle、奖励等输入与输出统计；
5. 完成进度所需的 Ticket、Spin、筹码、时间和付费 / 免费路径；
6. 奖励返还、净消耗、节奏与体验压力；
7. 可用于 CR 项目功能优化的机制与参数建议。

本任务是 **Knowledge / Analysis**，不是 Collector 开发，也不是 AI Report Engine 开发。优先使用已有 Capture、module catalog、数据指南和本机工具；只有现有方法无法完成时，才允许新增最小、可复用的 Lottery 专用提取脚本。

## User Decision

- Lottery 体验已经结束，可以开始整理和分析数据。
- 所有付费、充值、Ticket 购买和资源消耗均由 User 在体验阶段亲自决定并执行。
- 本任务不再进行新的付费或游戏内操作。
- 如果数据缺口确实需要重新采集，先列出缺口和最小补采动作，等待 User 单独决定；不得自行启动新 Capture。

## Truth Sources and Required Reading

执行前同步并读取最新版本：

### AI-Workspace

- `AGENTS.md`
- `tasks/TASK-0015-Huuuge-Lottery-Live-Numerical-Breakdown.md`
- 本 Task
- `standards/HUUUGE_EVIDENCE_STANDARD.md`
- `projects/huuuge-android-research/CONTEXT.md`
- `projects/huuuge-android-research/MEMORY.md`
- `projects/huuuge-android-research/WORKFLOW.md`
- `projects/huuuge-android-research/STATUS.md`
- `projects/huuuge-android-research/KNOWLEDGE/README.md`

### huuuge-android-research

- `AGENTS.md`
- `CONTRIBUTING.md`
- `CURRENT_STATUS.md`
- `HUUUGE_CODEX_HANDOFF.md`
- `AGENT_DATA_USAGE_GUIDE.md`
- `artifacts/module_catalog/lottery.md`
- `artifacts/module_catalog/slots.md`
- `artifacts/module_catalog/rewards.md`
- `artifacts/module_catalog/liveops_events.md`
- `artifacts/module_catalog/economy.md`
- `artifacts/module_catalog/endpoints.csv`
- `artifacts/module_catalog/fields.csv`

### Local finalized evidence

按 `AGENT_DATA_USAGE_GUIDE.md` 的顺序读取：

1. `.local/controller/last_session.json` 或 TASK-0015 交接记录；
2. Session `manifest.json`；
3. `rpc_inventory.csv`；
4. `field_paths.csv`；
5. `index.csv`；
6. 与 Lottery / Slots / Reward / Inventory 直接相关的 decoded JSON；
7. 只有必要时才读取对应 Raw；Raw 永不进入 Git、飞书或公开输出。

User 的本地截图和体验笔记可以作为 Manual evidence，但必须与 Runtime evidence 分开标注，且提交前脱敏。

## Concurrency and Repository Rules

- TASK-0016 正在 AI-Workspace 中修订；本任务的主要分析、脚本和报告工作只在 `huuuge-android-research` 中进行。
- 如果需要修改 AI-Workspace Task / Status / Handoff，必须在独立 worktree / branch 完成，先同步最新 `main`，不得 force push，不得覆盖 TASK-0016 的改动。
- `huuuge-android-research` 开始前确认工作树状态；如存在不属于本任务的未提交改动，先停止并报告。
- 主 Agent 是唯一写入者；Subagents 不是前置条件，默认保持 OFF。

## Phase 0 — Close and Verify TASK-0015

在开始数值结论前，先验证采集已经完整结束：

1. 确认 Session `manifest.status = stopped`；
2. 确认 `collector-start`、`hooks-installed`、`collector-ready`、`collector-stop` lifecycle evidence；
3. 记录 RPC raw / decoded 数量、decode rate、起止时间、游戏版本和 descriptor / agent hash；
4. 确认 `rpc_inventory.csv`、`field_paths.csv` 和 module catalog 已生成；
5. 如果 Collector 仍在运行，使用现有 Stop / Finalize 正常结束，不直接杀进程；
6. 输出一份简短 Evidence Coverage：已捕获、未捕获、可分析、不可分析；
7. 上述条件通过后，才把 TASK-0015 状态更新为 `Complete`。TASK-0014 已通过 ChatGPT Review，状态同步为 `Accepted`；仅做状态治理，不重新实施任务。

如果 Session 不完整但仍可分析，必须明确写出限制；不得把未 Finalize 或未配对的数据当成完整样本。

## Phase 1 — Build a Sanitized Fact Layer for This Report

先检查已有脚本和输出。只有无法满足时，才在业务仓库建立最小 Lottery 专用提取器，例如：

```text
tools/analysis/lottery/
├── extract_lottery_facts.py
├── README.md
└── tests/
```

不得借本任务开发通用 Normalized Fact Layer 或 AI Report Engine。

需要形成以下去标识化事实表；可根据实际证据合并或拆分，但字段口径必须文档化：

### 1. Session summary

- session alias；
- instance alias / account alias（仅匿名别名）；
- game version、schema / descriptor version；
- start / stop、duration；
- total RPC、decoded、decode errors；
- relevant endpoint counts；
- evidence completeness。

### 2. Event configuration and state

- event / lottery alias；
- expire、free ticket timestamp / timer；
- free ticket progress / threshold / color；
- ticket balance 按匿名颜色 / 类型聚合；
- lottery multiplier；
- puzzle board / puzzle multiplier；
- bulk play cap；
- Ticket shop 与奖励配置是否出现。

### 3. Lottery actions

- action sequence；
- Toss / Draw 前后状态；
- ticket color / ticket number；
- 单次消耗；
- reward output；
- puzzle position / progress；
- multiplier / milestone / completion 变化；
- success / error status；
- paired request / response evidence。

### 4. Slots activity-item samples

- Slot alias；
- Bet tier / normalized bet；
- Spin count；
- chip cost aggregate；
- activity-item hit count；
- item quantity；
- item color / type；
- Free Spin / Bonus / special state；
- relevant reward / inventory delta。

### 5. Reward outputs

- reward category；
- anonymous currency / item type；
- quantity；
- source action；
- fixed / random / conditional；
- repeated / unique；
- claim / grant evidence；
- paid path / free path source。

不提交账号 ID、真实 Session ID、token、订单、完整绝对余额轨迹、完整 JSON、Raw、截图原件或绝对本地路径。

## Phase 2 — Gameplay and Logic Breakdown

报告必须先让策划看懂玩法，再进入数值。

### 1. Gameplay loop

输出完整玩家循环：

```text
入口 / 活动曝光
→ Ticket / 活动道具来源
→ Free / Paid 路径
→ Toss / Draw
→ 即时奖励
→ Puzzle / Board 进度
→ Board / 活动完成奖励
→ 下一轮 / 到期 / missed-info
```

用 Mermaid 或等价图表示，但正文必须同时给中文步骤说明。

### 2. State and rule logic

至少分析：

- Ticket 颜色 / 类型的意义与消费规则；
- Free Ticket progress、threshold、计时和领取逻辑；
- Toss / Draw 请求、响应和状态迁移；
- Puzzle Board 的位置、颜色、格子奖励、完成条件；
- Lottery multiplier 与 Puzzle multiplier 的可能生效方式；
- bulk play cap；
- Ticket shop 与付费路径；
- expire、missed-info、补发 / 过期状态；
- 普通 Lottery、Black Lottery、MiniGame Lottery Machine 是否为同一流程或独立子玩法。

没有 Runtime 证据的部分保持 `Schema-only` 或 `Hypothesis`，不得凭字段名称写成已确认规则。

## Phase 3 — Numerical and Pattern Analysis

### A. Coverage and sample quality

先给出：

- Session 数；
- 有效时间范围；
- Spin、Toss、Free Ticket、Puzzle、Reward 等样本量；
- endpoint / field coverage；
- 缺失、重复、未配对、decode error；
- 样本是否覆盖免费、付费、不同 Bet、不同颜色、完成前后状态。

### B. Activity-item / Ticket acquisition

按证据可用范围计算：

- 有掉落 Spin 占比；
- 每 Spin 平均掉落；
- 每 100 Spin 掉落；
- 每单位筹码消耗的活动道具产出；
- 按 Bet tier 的掉落概率和数量；
- 按颜色 / 类型分布；
- Free Spin、Bonus、普通 Spin 是否存在差异；
- 免费领取、购买、奖励等其他来源占比。

命中率建议使用 Wilson 95% 区间；均值必须给样本量和离散程度。样本不足时只给观察值和不确定性，不给伪精确概率。

### C. Consumption and progression

还原并统计：

- 单次 Toss / Draw 的 Ticket 消耗；
- 各颜色 / 类型的使用规则；
- 单格、单 Board、单轮和全活动进度需求；
- Free Ticket 对总需求的抵消；
- multiplier 对消耗或奖励的影响；
- 完成所需 Spin、筹码和时间。

输出三种情景：

- 保守：低掉落 / 低奖励；
- 中位：基于当前样本；
- 乐观：高掉落 / 高奖励。

全活动无法从一个账号完整推导时，输出已确认区间、计算公式和缺口，不伪造最终值。

### D. Reward and output statistics

至少统计：

- 每次 Toss / Draw 的奖励类型、数量和分布；
- Puzzle 单格奖励；
- Board 完成奖励；
- 免费 Ticket、Multiplier 和附加奖励；
- 固定、随机、条件奖励；
- 重复奖励与奖励池线索；
- 每 Ticket、每 Toss、每 Board 的平均输出；
- 奖励输出的最小、中位、均值、最大及样本量。

### E. Return and net cost

分别计算或保留公式：

- Reward / Ticket；
- Reward / Toss；
- Reward / Board；
- Reward / Chip spent；
- Ticket acquired / Chip spent；
- 总投入、总输出、净消耗；
- 免费路径与付费路径的投入 / 输出对比。

不同币种、道具或不可直接比较的奖励不要强行折成单一价值。只有存在可复查的兑换关系或 UI 价格时才做折算，并标记依据。

### F. Pattern discovery

验证或否定以下候选规律：

- Bet 是否影响掉落概率、掉落数量或颜色；
- 是否存在阈值、档位、保底、冷却或批量上限；
- Puzzle / Lottery multiplier 是否按颜色、等级或进度变化；
- 奖励是否随阶段、Board、Ticket 颜色或付费路径变化；
- 是否存在 deterministic state transition 与随机 reward 混合；
- 是否有 streak、重复、阶段切换或到期行为；
- 单账号样本是否可能受账号分层、活动阶段或个性化配置影响。

只允许写“当前单实例 / 单账号观察到的规律”。跨账号共同规律留待未来多实例独立数据库与脱敏聚合后验证。

## Phase 4 — CR Project Recommendations

不要修改 CR 仓库。本报告只输出可执行的 `Decision proposal`：

- 建议采用、调整或避免的机制；
- Ticket / 活动道具与 Bet 的推荐关系；
- 免费进度、付费加速和追赶机制的边界；
- 单阶段目标时长、Spin 数、道具需求和完成压力；
- 推荐奖励返还区间与奖励层次；
- Board / Puzzle、颜色、Multiplier 的可读性与惊喜设计；
- 保底、防挫败、重复奖励和到期处理；
- 可能造成通胀、付费压迫、节奏断层或玩家误解的风险；
- CR 下一步应验证的 3–5 个参数实验。

所有推荐数字标记为 `Decision proposal`，不能伪装成 Huuuge 已确认配置。

## Evidence and Claim Rules

每个关键结论和表格行至少包含：

- Claim type：`Confirmed` / `Estimate` / `Hypothesis` / `Decision proposal`；
- Evidence source：`Observed-live` / `Static-config` / `Schema-only` / `Manual` / `Inferred`；
- Huuuge Evidence Level：L0–L4；
- Session alias；
- endpoint；
- field path；
- sample count；
- limits / uncertainty。

禁止：

- 把字段存在写成当前有值；
- 把一次结果写成稳定概率；
- 把 UI 观察替代 RPC 事实；
- 把 Schema 推断写成 Live-confirmed；
- 用完整余额轨迹或账号数据支撑公开报告。

## Deliverables

在 `huuuge-android-research` 建立：

```text
reports/lottery/20260827_<event_slug>/
├── README.md                         # 报告入口与一页结论
├── LOTTERY_NUMERICAL_BREAKDOWN.md    # 完整数值拆解报告
├── PLAYFLOW_AND_LOGIC.md             # 玩法循环、状态机和规则
├── EVIDENCE_MATRIX.md                # 结论、证据、等级和限制
├── DATA_DICTIONARY.md                # 聚合表字段与口径
├── SESSION_SUMMARY.csv
├── SLOT_ITEM_DROP_STATS.csv
├── LOTTERY_ACTION_STATS.csv
├── PROGRESSION_MODEL.csv
├── REWARD_OUTPUT_STATS.csv
├── RETURN_MODEL.csv
└── CR_RECOMMENDATIONS.md
```

可增加一个策划可读工作簿：

```text
LOTTERY_NUMERICAL_BREAKDOWN.xlsx
```

建议 Sheet：`结论`、`玩法逻辑`、`掉落`、`消耗进度`、`奖励输出`、`返还`、`证据与缺口`。若生成 Excel，必须由同一组聚合 CSV 生成，避免两套口径。

实际目录名可按真实活动名调整，但必须保留可复查、去标识化、中文策划可读的入口。

## Feishu Delivery

通过 AI Document Assistant 搜索防重后创建或更新：

```text
《Huuuge Lottery 活动数值拆解（2026-08-27）》
```

至少包含：

1. 一页结论；
2. 玩法循环；
3. 核心逻辑；
4. 数据范围与样本质量；
5. 活动道具 / Ticket 获取；
6. 消耗与完成进度；
7. 奖励输出与返还；
8. 观察到的规律；
9. CR 可迁移建议；
10. 证据等级、限制和待验证项。

默认企业内获得链接的人可编辑。写入后必须回读正文与权限，返回最终飞书 URL。飞书只使用脱敏、聚合结果，不写 Raw、完整响应、账号信息或逐笔余额。

## Safety and Non-goals

本任务不做：

- 新的游戏内付费、充值或资源消耗；
- 修改请求、奖励、余额或服务器状态；
- 重放或伪造 RPC；
- Collector 重构；
- 通用 Normalized Fact Layer；
- AI Report Engine；
- 多实例跨账号聚合；
- CR 仓库配置或代码修改；
- 上传 Raw Capture、完整 JSON、账号 / Session 标识、订单、逐笔余额、截图原件、APK 或二进制；
- 用外部公共服务处理私有原始数据。

## Acceptance Criteria

- TASK-0015 Session 已验证 `stopped`，或报告明确说明不完整原因；
- TASK-0015 状态在证据通过后更新为 `Complete`，TASK-0014 状态治理为 `Accepted`；
- 玩法、逻辑、规律、输入、消耗、进度、奖励和输出统计均有独立章节；
- 每项关键数值可追溯到 sanitized fact table、endpoint、field path 和 sample count；
- 免费 / 付费路径分开，单账号观察与跨账号推断分开；
- 不足样本有区间、限制或缺口，不输出伪概率、伪 EV 或伪全活动成本；
- 报告和 CSV / Excel 口径一致；
- Raw 和敏感数据没有进入 Git、飞书或聊天；
- Feishu 文档已搜索防重、写入、回读并验证企业内可编辑；
- 更新 `huuuge-android-research` 的 `CURRENT_STATUS.md`、`HUUUGE_CODEX_HANDOFF.md`、`CHANGELOG.md` 和适用 Knowledge / dossier；
- 更新 AI-Workspace 的 TASK-0018 状态和必要 Handoff；与 TASK-0016 安全 rebase，无 force push；
- 两个仓库分别提交并推送，等待 ChatGPT Review。

## Handoff Required

Codex 完成后返回：

- 使用的 Session alias、状态、时间范围、游戏版本；
- RPC / decoded / relevant endpoint 与样本计数；
- 主要已确认玩法与逻辑；
- 主要数值、规律和限制；
- Git 报告目录；
- Feishu URL 与权限回读结果；
- `huuuge-android-research` commit；
- `AI-Workspace` commit；
- TASK-0014 / 0015 / 0018 最终状态；
- 新发现的优化项，仅作为下个 Task 候选，不擅自实施；
- `Subagents: none` 或实际使用记录。
