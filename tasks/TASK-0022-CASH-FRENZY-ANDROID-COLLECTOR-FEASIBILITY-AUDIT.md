# TASK-0022 — Cash Frenzy Android Collector Feasibility Audit

- Status: Review
- Project key: CASH-FRENZY
- Human alias: CF-FEASIBILITY-001
- Owner: User / ChatGPT
- Executor: Codex
- Priority: P1 candidate
- Date: 2026-08-27
- Updated: 2026-08-27
- Candidate provenance: `tasks/candidates/CANDIDATE-20260827-CASH-FRENZY-COLLECTOR-FEASIBILITY.md`
- Allocation relationship: new
- Related tasks: TASK-0018, TASK-0020

## Goal

用最小、可复查的静态与动态证据判断：

> Cash Frenzy 是否能达到与当前 Huuuge Collector 相近的“被动广泛采集 → 结构化解码 → Raw 保全 → 模块目录 → 按需数值分析”能力，以及需要采用什么 Adapter 路线。

本方向只做**可行性审计与最小链路证明**，不构建完整 Cash Frenzy Collector，不输出 RTP/EV 或长期概率结论。

## Scope

### Phase A — Reuse-first discovery

主 Agent 先读取届时最新 Core Rules、Capability / Workflow / Evidence 文档、Huuuge Collector 文档与已验证能力，形成 Reuse Matrix：

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

公开资料结论必须有来源；商店描述只能证明产品功能，不可证明客户端协议。

### Phase C — Isolated research environment

建立或确认独立研究实例，建议显示名 `CashFrenzyResearch`。要求：

- 独立于 HuuugeResearch；
- 独立账号/实例/session 目录；
- 不把不同游戏 Raw 混合；
- 记录 Android 版本、实例 ID、ADB serial、ABI list 和 native bridge；
- 只在真正需要时申请 Root/Frida 等机器级变更，先复用已审计方案或官方/成熟方案；
- 任何共用 Host 修改前说明影响、备份与回滚，并取得 User 确认。

### Phase D — APK acquisition and static audit

在 User 自己的研究环境中定位并拉取 base/split APK，保存在受控本机目录，不提交 Git/SVN/飞书。至少检查：

- package/version/split/ABI；
- Unity、IL2CPP、Cocos、Unreal、自研引擎或其他运行框架；
- Java/Kotlin、managed assemblies、native `.so`、Lua/LuaJIT；
- Protobuf descriptor、`.proto` 名称、FlatBuffers schema、MessagePack、JSON、SQLite；
- 网络库、WebSocket、HTTP/2、gRPC、自定义 socket、TLS；
- AssetBundle、资源包、配置表和本地数据库；
- 主要业务模块和可疑 hook target；
- anti-debug、integrity、签名校验和 native bridge 风险。

只提交脱敏结构、文件名、hash、字段/符号摘要和证据位置，不提交 APK、`.so`、完整 strings、账号数据或私有响应。

### Phase E — Minimal dynamic proof

目标不是长时间抓取，而是证明一条真实数值链。由 User 在正常游戏中亲自执行：

1. 进入一个可用 Slots 机台；
2. 记录当前可见 Bet 档位；
3. 进行 1–5 次本来就准备进行的普通 Spin；
4. 若自然触发 Feature / Free Spin / Jackpot，只被动记录，不诱导额外付费或大量资源消耗。

Codex 负责在操作前确认被动采集 Ready，捕获网络/序列化/本地状态层的最小证据，关联 request/response/update/balance change，区分观察与推断，并 Clean Finalize。Raw 只留本机。

无法捕获时必须给出精确 blocker，例如协议仍加密且尚未到明文层、native bridge / anti-debug 阻塞、结果只在本地对象、schema 缺失、账号/玩法未解锁，或需要新 hook / Local State Adapter。不得用“应该可以”代替证据。

### Phase F — Feasibility and architecture decision

按以下层次评分：

```text
F0 Unknown
F1 Static-only
F2 Live raw observed
F3 Live structured fields recovered
F4 Repeatable Huuuge-like collection path proven
```

分别评估 Slots/Spin、Feature/Free Spin/Jackpot、Missions/Pass/Club/Events、Offers/Economy/Rewards、Local config/static math、跨 Session 复现和策划一键包装潜力。最终给出当前等级、F4 缺口、预计 Adapter、Adopt/Wrap/Fork/Build 决策和是否值得进入完整实现 Task。

## Non-goals

- 不构建完整 Cash Frenzy Collector；
- 不复制/改名 Huuuge Collector 后发布；
- 不做长时间 Spin、RTP、EV、概率表或服务端 RNG 结论；
- 不绕过付费、伪造/重放请求、修改奖励/余额；
- 不解锁付费内容、自动购买或替 User 消耗资源；
- 不研究 Top Tycoon 或绯闻港口；
- 不发布飞书正式报告；
- 不创建业务仓库或 SVN 正式包，除非未来 Task 明确批准。

## Deliverables

若未来获批执行，在 `AI-Workspace/reviews/cash-frenzy/` 提交脱敏结果：

```text
FEASIBILITY.md
REUSE_MATRIX.md
STATIC_INVENTORY.md
PROTOCOL_EVIDENCE.md
DYNAMIC_PROOF.md
NEXT_TASK_PROPOSAL.md
```

- `FEASIBILITY.md`：一页结论、F0–F4、Huuuge 对比、Adopt/Wrap/Fork/Build/Stop 与证据标签。
- `REUSE_MATRIX.md`：通用层、Huuuge-specific、Adapter 边界、依赖与退出成本。
- `STATIC_INVENTORY.md`：package/version/ABI/engine、结构摘要、hash 和工具版本，不含二进制或完整 strings。
- `PROTOCOL_EVIDENCE.md`：网络/序列化候选、schema、hook target、保护风险和证据等级。
- `DYNAMIC_PROOF.md`：Session 别名、User 最小动作、捕获结果、确认字段与 blocker，不含敏感明细。
- `NEXT_TASK_PROPOSAL.md`：只提出 Collector Adapter、Static Config Adapter、Local State Adapter 或停止投入，不自动执行。

## Safety

- User 负责账号登录、游戏内操作、付费和资源消耗决定。
- Codex 只做被动采集、静态读取、工具验证和脱敏结论。
- Raw capture、APK、`.so`、完整响应、账号 ID、token、逐笔余额和私有路径保持受控本机。
- Git 只保存脱敏结构、hash、字段/符号摘要、复现步骤和判断。
- 不修改游戏请求、返回值、内存状态、余额、奖励或服务器状态。
- Cash Frenzy 数据不写入 Huuuge session/database；按实例、账号别名、Session、版本和 schema 隔离。

## Validation

未来执行至少验证 APK/split hash 与版本、静态工具版本、serialization signature、Session start/stop 与捕获计数、敏感扫描、Huuuge 业务仓库 clean/diff，以及最终 Subagent mode。完整日志留本机，Git 只保存脱敏摘要。

## Handoff

未来执行完成后必须返回：AI-Workspace commit、实际 package/version/ABI/engine、动态证明与 Evidence Level、F0–F4 结果、Adopt/Wrap/Fork/Build/Stop 建议、可复用 Huuuge 能力与新增 Adapter、下一 Task 建议、`Subagents: <names>` 或 `none`、最终 Subagent mode（应为 OFF），并等待 ChatGPT Review。

## Execution Progress — 2026-08-27

- Task issuance：正式 allocator 分配 `TASK-0022`，main merge `694e955b76405bd6fb97203110d6bc6f9a1185b2`，reservation 已 finalize。
- Reuse-first：完成 Huuuge 1.0.1 control-plane/Session/manifest/Raw/inventory/privacy 只读审计，决定 Adopt workflow contract、Wrap host binding、Build Cash-specific protocol adapter；不复制 Huuuge 工程。
- Static identity：确认 package `slots.pcg.casino.games.free.android`、sample 4.78 / 478、arm64-v8a、Cocos2d-x + LuaJIT、base + 3 splits。
- Protocol/resource：确认 `BLSocket`/command map、TLS/WebSocket/LuaSocket/XXTEA/Protobuf static signals、16,887 LuaJIT bytecode 与 Systems/Themes 目录；未恢复游戏业务 descriptor。
- User environment decision：执行门槛处 User 明确将原 `Pie64_1 / HuuugeResearch` 重命名为共享研究实例 `AppResearch`，用于后续测试 App；该决定 supersede 本 Task 早期“独立 `CashFrenzyResearch` 实例”建议。隔离边界改为 package、Host-local project root、Session、Raw、APK/SO、账号数据和 manifest，不允许跨 App 混用。
- Dynamic environment：`Pie64_1 / AppResearch`、Android 9、ADB alias `emulator-5564`、x86_64 Host ABI + `libnb.so` arm64 native bridge；Cash Frenzy 4.78 / 478 / arm64-v8a 现场复核通过。
- Runtime boundary：outer Frida 只能看到 x64；通过已审计 Houdini bootstrap 将通用 Frida 17.17.0 Gadget 临时放入 Cash Frenzy 自己的 arm64 namespace，确认 `libcocos2dlua.so`。`SSL_read/write`、BIO、LuaSocket 与 WebSocket 在大厅静置期均 0；真实业务链为 `BLSocket` + process `sendto/recvfrom`。
- Dynamic proof：User 累计执行 5 次普通 Spin（Bet 10000；金猪主题机台，名称未完整记录；无自然 Feature）。首轮 3 次与 3 个新 255-byte outbound packet 及 1.1–2.5 KB inbound bursts 对齐；第二轮 2 次与 2 个同构 outbound Lua request 对齐。
- Structured fields：live schema-only Lua hook 确认 request table 形态为 `[command-string, payload-table, metadata-table]`，Spin payload 包含 `bet`、`lines`、`spin_count`、`client_coins`、`free_spins`、`autoSpin`、`turbo`，metadata 包含 `_timestamp`。未记录字段值；command 仅依据长度、static map 与动作关联推断为 `BATCH_SPIN`，不写成直接观察。
- Current level：**F3 Live structured outbound fields recovered**。入站仍为 opaque binary Raw，未恢复 result/win/balance/update，完整数值链与可重复 Huuuge-like decoder 未达到，F4 不成立。
- Finalize：所有 capture/shape Session Clean Stop、0 errors、无残留进程；Cash 专属 Gadget 文件、27043 forward 与临时 Frida server 已移除，Cash app 已 force-stop。Huuuge repo/Collector/Session/Raw 未修改，WATCH 未启用；Subagents none / OFF。

## Phase 1.5 — Balance Recovery Spike

### Decision and scope

- 仅尝试恢复 `balance`，并在不增加协议层的前提下顺带验证 `win` 推导；未继续研究 RTP、EV、Feature、Jackpot、完整 result、Collector 重构或 OCR/UI 双轨。
- 复用 Phase 1 已确认的 outbound Spin payload，不解析 opaque inbound，不新增 Collector Capability，不提高 F0–F4 等级。

### Minimal method

连续 Spin 请求中的 `client_coins` 可形成相邻状态：请求 `i` 的值作为 Spin `i` 的 Balance Before，请求 `i+1` 的值作为 Spin `i` 的 Balance After。Bet 稳定且两次请求之间没有其他游戏动作时，可脱敏推导：

```text
Win Candidate(i) = client_coins(i+1) - client_coins(i) + bet(i)
```

该方法只读取客户端已序列化的 outbound payload；不修改请求、返回、内存、余额或服务器状态。逐笔数值只保存在 `D:\CashFrenzyResearch\local-only`，不进入 Git、Handoff 或云文档。

### Fault-bounded live result

- User 完成 3 次普通 Spin；probe 捕获 3 个符合既有 Spin shape 的样本，0 errors，形成 2 个相邻 Balance 转移。
- 3 个样本的 `bet` 均为数值且保持稳定，`client_coins` 均为数值；两个相邻转移均发生 Balance 变化。
- 两个 Win Candidate 均为非负整数，其中一个为非零；这证明公式可复算，但在未恢复 inbound result 的条件下仍标记为 **Derived**，不宣称为服务端 Win 字段。
- **成功标准 A 达成**：对连续请求中前两次 Spin，可恢复 `Spin → Balance Before → Balance After`。第三次 Spin 的 Balance After 需要下一次 Spin 请求作为后继状态，因此当前方法天然提供 `N` 个请求对应 `N-1` 个闭合转移。
- **成功标准 B 为 Derived candidate**：可结合稳定 Bet 推导 Win Candidate；未将其升级为直接观察到的 `win`。
- Collector 能力等级保持 **F3**。没有进入新协议层，也没有恢复 opaque inbound `result`。

### Current blocker and next recommendation

- Current blocker：最后一次 Spin 的 Balance After 只有在下一条 Spin 请求出现后才能闭合；Session 末尾即时 Balance/Win 仍需要 inbound result 或其他新的状态源，超出本 Spike 边界。
- Next recommendation：停止 Spike，保留 F3；后续 Demo 若获单独授权，可使用相邻 outbound request 构建脱敏 Balance 波动与 Spin Timeline，并明确尾部未闭合和 Win 为 Derived。当前不开始 Demo 报告。

### Clean finalize

- 达到成功标准后立即停止，没有扩大到 OCR/UI、完整协议解析或其他游戏。
- Cash app 已 force-stop；临时 Cash 专属 Gadget/config、ADB `tcp:27043` forward、Frida server 和本机 probe 进程均确认无残留。
- `HuuugeResearch` 仓库、Collector、Session、Raw 未修改；AI-Workspace governance、Top Tycoon、Gossip Harbor、WATCH 和 Capability 均未改动。
- Subagents: none；最终模式 OFF。

## Collector Demo — 2026-08-27

### Review decision and positioning

- User 转述 ChatGPT 已通过 Phase 1.5 Review；决定为 **Stop Spike**。本阶段不再恢复协议，不新建 Task。
- Demo 定位为“证明当前 F3 Collector 已能支持策划体验分析”，不是数值拆解；Collector 等级保持 F3。
- User 后续明确修正交付格式：不生成 Word；正式输出为 Git Markdown + 飞书文档 + Documentation Hub 登记。

### Live Demo result

- User 正常体验 Slots；Collector Session `20260827_192117` 捕获 193 个 outbound Spin 样本，0 errors，形成 192 个闭合 Balance Before / Balance After 转移和 1 个 open tail。
- 首末 Spin 覆盖约 15.1 分钟，含自然停顿；`bet`、`lines`、`spin_count`、`client_coins`、`free_spins`、`autoSpin`、`turbo` 和 `_timestamp` 均为 193/193。
- 观察到 5 个 Bet 档位；162 个样本为 `autoSpin=1 / turbo=1`，31 个样本为 `autoSpin=0 / turbo=0`；`lines` 保持 40。
- 相邻 `client_coins` 只用于生成归一化 Balance Curve 和 Derived Net Delta。报告不展示绝对余额，不把 Win、Feature 或 result 写成 Confirmed。
- User 提供覆盖不完整的 `demo.MP4`，仅用于展示时由 User 人工交叉验证；Agent 未读取视频内容，视频不进入 Git。飞书正文已预留手动拖入位置。

### Deliverables

- Markdown：`reviews/cash-frenzy/COLLECTOR_DEMO.md`。
- 中文图表：`reviews/cash-frenzy/assets/collector-demo/` 下的 Spin 时间线、余额变化曲线和 Bet 档位分布 PNG/SVG。
- 飞书：《Cash Frenzy｜老虎机体验验证（Collector Demo）》已创建，企业内可编辑权限 verified，正文与三组飞书原生中文图表回读通过；安全链接只在当前交付消息返回，不写入 Git。

### Documentation Hub blocker

- 当前会话的 Document Assistant 提供 create/search/get/share，但没有暴露已登记的 `register_document` binding。
- 唯一《AI Workspace｜文档导航中心》回读确认目标标题出现 0 次，因此正式 Hub 同步尚未完成。
- 按 Accepted governance 保留已创建文档、不重复创建、不人工修改 Hub。下一步必须在暴露 `register_document` 的会话中对现有文档补登记为 `📊 报告 / Review`，再回读 Hub 确认标题恰好出现 1 次。

### Clean finalize

- Demo 达成后立即停止；Cash app、Frida server、ADB forward、临时 Gadget/config、bootstrap 与 capture 进程均确认无残留。
- Raw、逐笔绝对余额、APK、SO、完整响应、账号数据和视频保持本机；Git 只保存脱敏聚合与归一化图表。
- 未修改 Huuuge Collector、Session、Raw、SVN、其他游戏、Capability、Workspace Sync 模式或 WATCH；Subagents: none / OFF。
