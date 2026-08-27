# TASK-0018 — Cash Frenzy Android Collector Feasibility Audit

- Status: Ready
- Owner: User / ChatGPT
- Executor: Codex
- Priority: P1
- Date: 2026-08-27
- Target game: Cash Frenzy / 爆有钱 Online
- Candidate package: `slots.pcg.casino.games.free.android`（执行时必须重新确认）
- Business repository: Not created; this Task is feasibility-only
- Subagent mode: MANUAL allowed under the restrictions below

## Execution Gate

本任务按 User 指定的多游戏优先级首先研究 Cash Frenzy，Top Tycoon 和绯闻港口后续分别另立 Task，不并行开发。

开始前必须满足：

1. `TASK-0015` 的 Huuuge Lottery 实时 Capture 已结束或 Collector 明确处于 idle；不得为了本任务打断限时证据保全。
2. 同步 `AI-Workspace` 与 `huuuge-android-research` 最新 `main`，读取当前 Task、Status、Handoff 和 Collector 能力边界。
3. 本任务使用独立模拟器实例和独立本机数据目录；不得复用或修改 `Pie64_1 / HuuugeResearch`。
4. 新建实例、安装游戏、账号登录、商店认证等需要 User 操作或授权时，由 User 决定并执行。

若 Gate 未满足，报告真实阻塞并停止，不得擅自扩大权限或绕过当前 P0 任务。

## Goal

用最小、可复查的静态与动态证据判断：

> Cash Frenzy 是否能达到与当前 Huuuge Collector 相近的“被动广泛采集 → 结构化解码 → Raw 保全 → 模块目录 → 按需数值分析”能力，以及需要采用什么 Adapter 路线。

本任务只做**可行性审计与最小链路证明**，不构建完整 Cash Frenzy Collector，不输出 RTP/EV 或长期概率结论。

## Success Question

任务结束时必须明确回答：

1. Cash Frenzy 的 Android 包、版本、ABI、引擎和主要运行模块是什么？
2. 它使用何种网络协议和序列化：Protobuf、FlatBuffers、JSON、MessagePack、自定义二进制或其他？
3. 是否存在可恢复的 descriptor/schema、符号、Lua/managed metadata、配置表或资源容器？
4. 能否在 User 正常执行一次 Spin 时，被动捕获可关联的 request/response/update 或本地状态变化？
5. 当前证据能否稳定还原 `game/machine id、bet、result、win、feature/free-spin、jackpot、balance/state` 中的哪些字段？
6. Huuuge Collector 的哪些通用能力可以 Adopt/Wrap，哪些必须为 Cash Frenzy 新建 Adapter？
7. 建议结论是：`Adopt / Wrap / Fork / Build / Stop` 中哪一种，置信度和主要风险是什么？

## Scope

### Phase A — Reuse-first discovery

主 Agent 先读取：

- `AI-Workspace/00_CORE_RULES.md` 对应的最新 Git 规则；
- `AI-Workspace` Capability / Workflow / Evidence 相关文档；
- `huuuge-android-research/docs/collector/`；
- Huuuge Collector 的 Bootstrap、GUI、Session、manifest、inventory、module catalog 和 adapter-sensitive 实现；
- 当前 Huuuge Collector 已验证能力与明确缺口。

输出一份 Reuse Matrix，至少区分：

```text
可直接复用：Bootstrap / GUI / Session / manifest / Raw / inventory / catalog / privacy
需要包装：模拟器实例、包名、ABI、启动与 hook 生命周期
必须新建：协议 decoder、hook target、schema mapping、模块分类
暂不采用：与 Cash Frenzy 不匹配的 Huuuge-specific code
```

不得先复制 Huuuge 工程再寻找理由。

### Phase B — Public and package identity verification

确认并记录：

- 官方游戏名称与地区名称关系；
- 官方开发/发行主体；
- Android package；
- 当前实际安装版本与 versionCode；
- 是否存在地区包、商店包或 ABI 差异。

公开资料结论必须有来源；商店描述只能证明产品功能，不可直接证明客户端协议。

### Phase C — Isolated research environment

建立或确认独立研究实例，建议显示名：

```text
CashFrenzyResearch
```

要求：

- 独立于 HuuugeResearch；
- 独立账号/实例/session 目录；
- 不把不同游戏 Raw 混合；
- 记录 Android 版本、实例 ID、ADB serial、ABI list 和 native bridge；
- 只在真正需要时申请 Root/Frida 等机器级变更，先复用已审计方案或官方/成熟方案；
- 任何共用 Host 修改前先说明影响、备份与回滚，并取得 User 确认。

### Phase D — APK acquisition and static audit

在 User 自己的研究环境中定位并拉取 base/split APK，保存在受控本机目录，不提交 Git/SVN/飞书。

至少检查：

- package/version/split/ABI；
- Unity、IL2CPP、Cocos、Unreal、自研引擎或其他运行框架；
- Java/Kotlin、managed assemblies、native `.so`、Lua/LuaJIT；
- Protobuf descriptor、`.proto` 名称、FlatBuffers schema、MessagePack、JSON、SQLite；
- 网络库、WebSocket、HTTP/2、gRPC、自定义 socket、TLS；
- AssetBundle、资源包、配置表和本地数据库；
- 主要业务模块和可疑 hook target；
- anti-debug、integrity、签名校验和 native bridge 风险。

输出仅提交脱敏结构、文件名、hash、字段/符号摘要和证据位置，不提交 APK、`.so`、完整 strings、账号数据或私有响应。

### Phase E — Minimal dynamic proof

目标不是长时间抓取，而是证明一条真实数值链。

由 User 在正常游戏中亲自执行：

1. 进入一个可用 Slots 机台；
2. 记录当前可见 Bet 档位；
3. 进行 1–5 次本来就准备进行的普通 Spin；
4. 若自然触发 Feature / Free Spin / Jackpot，只被动记录，不诱导额外付费或大量资源消耗。

Codex 负责：

- 在操作前确认被动采集已 Ready；
- 捕获网络层、序列化层或本地状态层的最小证据；
- 对 request / response / update / balance change 做时间关联；
- 判断哪些字段是直接观察、哪些只是推断；
- Clean Finalize 并保留 Raw 在本机。

如果无法捕获，必须给出精确 blocker，例如：

- 协议仍加密且尚未到明文层；
- native bridge / anti-debug 阻塞；
- 结果只在本地对象中；
- schema 缺失；
- 账号/玩法未解锁；
- 需要新的 hook 或 Local State Adapter。

不得用“应该可以”代替现场证据。

### Phase F — Feasibility and architecture decision

按以下层次评分：

```text
F0 Unknown
F1 Static-only
F2 Live raw observed
F3 Live structured fields recovered
F4 Repeatable Huuuge-like collection path proven
```

分别评估：

- Slots / Spin；
- Feature / Free Spin / Jackpot；
- Missions / Pass / Club / Events；
- Offers / Economy / Rewards；
- Local config / static math support；
- Cross-session reproducibility；
- Planner-facing one-click packaging potential。

最终给出：

- 当前等级；
- 达到 F4 的缺口；
- 预计新增 Adapter；
- Adopt / Wrap / Fork / Build 决策；
- 是否值得进入下一完整实现 Task。

## Subagent Policy

本任务**适合 MANUAL Subagents**，因为存在多个真正独立、读多写少的前置工作流。

允许的只读委派：

1. `repo_explorer`
   - 只读分析 Huuuge Collector 可复用层、adapter seam、相关文件和调用链；
   - 不修改任何仓库。
2. `knowledge_retriever`
   - 只读收集官方商店、官方帮助中心和已提供文档；
   - 不读取或写入飞书，主 Agent 如需飞书内容只提供最少脱敏摘要。
3. `evidence_test_verifier`
   - 只读检查 Evidence 标签、验收矩阵、复现条件和安全边界。
4. `reviewer`
   - 在主 Agent完成草案后，只读审查结论、范围漂移、证据过度和安全风险。

严格限制：

- 主 Agent 是唯一写入者、唯一 Git 提交者和唯一外部操作执行者；
- APK 拉取、模拟器、ADB、Root、Frida、动态 Capture、Raw 数据读取和所有文件写入由主 Agent负责；
- Subagent 不访问账号/session Raw、完整 APK/`.so`、Secret、飞书 WRITE 或其他外部 WRITE；
- `MANUAL` 禁止与 `--yolo`、Full access、`danger-full-access`、宽松 `/permissions` 或等价父会话权限并用；
- 无法确认父会话是受限权限时保持 `OFF`，单 Agent完成，不降低验收标准；
- 任务完成后切回 `OFF`，Handoff 必须记录实际使用的 Agent；未使用写 `Subagents: none`。

## Deliverables

在 `AI-Workspace/reviews/cash-frenzy/` 提交脱敏结果：

```text
FEASIBILITY.md
REUSE_MATRIX.md
STATIC_INVENTORY.md
PROTOCOL_EVIDENCE.md
DYNAMIC_PROOF.md
NEXT_TASK_PROPOSAL.md
```

其中：

### `FEASIBILITY.md`

- 一页结论；
- F0–F4 分项评分；
- 与 Huuuge 当前能力的对比；
- Adopt / Wrap / Fork / Build / Stop 决策；
- Confirmed / Estimate / Hypothesis 分离。

### `REUSE_MATRIX.md`

- Huuuge 通用层可复用项；
- Huuuge-specific 不可复用项；
- Cash Frenzy Adapter 边界；
- 依赖与退出成本。

### `STATIC_INVENTORY.md`

- package/version/ABI/engine；
- APK/split/native/managed/resource/schema 摘要；
- 本地证据 hash 和工具版本；
- 不包含二进制或完整 strings。

### `PROTOCOL_EVIDENCE.md`

- 网络与序列化候选；
- schema/descriptor 状态；
- hook target；
- anti-debug / TLS / native bridge 风险；
- 每项证据等级。

### `DYNAMIC_PROOF.md`

- Session ID 别名和游戏版本；
- User 实际执行的最小动作；
- 抓到的 endpoint/message/state；
- 已确认字段、缺失字段和 blocker；
- 不包含账号 ID、逐笔余额、完整结果数组或 Raw。

### `NEXT_TASK_PROPOSAL.md`

只提出下一步，不自动执行：

- 完整 Collector Adapter；
- Static Config Adapter；
- Local State Adapter；
- 或停止投入。

## Non-goals

本任务不做：

- 完整 Cash Frenzy Collector 产品化；
- 复制/改名 Huuuge Collector 后直接发布；
- 长时间 Spin 数据采样；
- RTP、EV、概率表或服务端 RNG 结论；
- 绕过付费、伪造请求、请求重放、奖励/余额修改；
- 解锁付费内容、自动购买或替 User 消耗资源；
- Top Tycoon 或绯闻港口研究；
- 飞书正式报告；
- 创建新的业务仓库或 SVN 正式包，除非下一 Task 由 User 明确批准。

## Safety and Data Boundaries

- User 负责账号登录、游戏内操作、付费和资源消耗决定。
- Codex 只做被动采集、静态读取、工具验证和脱敏结论。
- Raw capture、APK、`.so`、完整响应、账号 ID、token、逐笔余额和私有路径保持受控本机。
- Git 只保存脱敏结构、hash、字段/符号摘要、复现步骤和判断。
- 不修改游戏请求、返回值、内存状态、余额、奖励或服务器状态。
- 不把 Cash Frenzy 数据写入 Huuuge 的 session/database；按 `instance_id / account_alias / session_id / game_version / schema_version` 独立保存。

## Acceptance Criteria

必须全部满足：

1. package、version、ABI、Android 实例和引擎信息已现场确认。
2. 静态审计覆盖主要代码、native、serialization、network、config/resource 和保护机制。
3. 至少完成一次 User 正常 Spin 的最小动态尝试：
   - 成功时给出可复查 structured/raw evidence；
   - 失败时给出精确 blocker 和下一验证动作。
4. 明确列出当前可还原与不可还原的数值字段，不能把字段存在写成字段有值。
5. 完成 Huuuge Reuse Matrix 和 Cash Frenzy Adapter 边界。
6. 给出 F0–F4 分项等级、置信度、风险和 Adopt/Wrap/Fork/Build/Stop 决策。
7. 所有结论明确标为 Confirmed / Estimate / Hypothesis / Decision proposal。
8. `huuuge-android-research` 的生产 Collector、SVN 策划包和 `HuuugeResearch` 实例未被修改。
9. 本机 Raw/二进制/账号数据未进入 Git、飞书或聊天。
10. 若使用 Subagents，父会话为受限权限、主 Agent唯一写入、Handoff 列出实际 Agents，并在结束后恢复 `OFF`。
11. 更新本 Task 状态、`CHANGELOG.md` 和 `handoff/CODEX.md`，提交并推送，等待 ChatGPT Review。

## Validation

Codex 至少执行并记录：

- APK/split hash 与版本清单；
- 静态工具版本和可复现命令；
- schema/serialization signature 检查；
- 动态 Session start/stop、时间范围和捕获计数；
- 敏感数据扫描；
- Huuuge 业务仓库 clean/diff 检查；
- Subagent 最终模式状态检查（应为 `OFF`）。

完整日志留本机；Git 只保存脱敏摘要。

## Handoff Required

Codex 完成后必须返回：

- AI-Workspace commit；
- Cash Frenzy 实际 package/version/ABI/engine；
- 动态证明是否成功及证据等级；
- F0–F4 结果；
- Adopt / Wrap / Fork / Build / Stop 建议；
- 可复用 Huuuge 能力与必须新增的 Adapter；
- 下一 Task 建议；
- `Subagents: <names>` 或 `Subagents: none`；
- 最终 Subagent mode（应为 `OFF`）；
- 等待 ChatGPT Review。
