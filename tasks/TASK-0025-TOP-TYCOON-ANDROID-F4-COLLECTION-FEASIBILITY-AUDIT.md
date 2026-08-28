# TASK-0025 — Top Tycoon Android F4 Collection Feasibility Audit

- Status: Review
- Project key: TOP-TYCOON
- Human alias: TT-FEASIBILITY-001
- Owner: User / ChatGPT
- Executor: Codex
- Priority: P1 / same-day feasibility audit
- Date: 2026-08-28
- Updated: 2026-08-28
- Candidate provenance: `tasks/candidates/CANDIDATE-20260828-TOP-TYCOON-F4-FEASIBILITY.md`
- Allocation relationship: new
- Related tasks: TASK-0022, TASK-0024

## Goal

在 User 新建、显示名为 `topTycoon` 的 Android 模拟器中，用最小、可复查且有停止边界的静态与动态证据，判断 Top Tycoon 能否达到 **F4 Repeatable Huuuge-like collection path proven**：核心 Spin 数值链可结构化恢复、跨独立 Session 复现，并形成确定性的启动、采集、停止、清理与证据归档路径。

本方向复用 TASK-0022 与 TASK-0024 已验证的 Session、Raw、Evidence、受限序列化和 Clean Finalize 合同，但不续写或扩大这两个已关闭 Task，也不先建设完整 Collector。

## Scope

### Phase A — Identity and environment gate

执行前现场确认并记录：

- BlueStacks internal instance ID、显示名 `topTycoon`、Android 版本、ADB serial；
- 实际安装包名、游戏版本、versionCode、split、ABI、native bridge 与当前前台包；
- 公开资料中的 Android package 候选 `com.monopoly.dream.idle.king` 只能作为定位线索，必须以实装包复核为准；
- Top Tycoon 专属 Host-local project root、Session、Raw、APK/SO、账号别名、manifest 与 Evidence 路径；
- Huuuge、Cash Frenzy、其他游戏和正常模拟器均保持只读、独立且不混用数据。

任何 identity 不一致、前台包不匹配或隔离边界不成立时 fail closed，不进入动态采集。

### Phase B — Reuse-first decision

先审计当前最新能力并形成 Reuse Matrix：

```text
Adopt：Session / manifest / Raw / inventory / privacy / evidence / cleanup contract
Wrap：topTycoon 实例、package、version、ABI、启动与 runtime lifecycle
Build：仅限 Top Tycoon-specific hook、schema mapping、module catalog 或必要 Adapter
Do not reuse：任何 Huuuge-specific / Cash-specific 业务 schema、Raw、账号或数据目录
```

不得复制改名已有 Collector 后再寻找适配理由。

### Phase C — Static audit

在 User 自己的受控研究环境中定位 base/split APK，仅保存在本机，至少确认：

- APK/split hash、engine 与运行框架：Unity/IL2CPP、Cocos/Lua、自研或其他；
- Java/Kotlin、managed assemblies、native `.so`、Lua/LuaJIT、资源容器与本地配置；
- JSON、Protobuf、FlatBuffers、MessagePack、自定义二进制、SQLite 等序列化或存储信号；
- HTTP/WebSocket/socket/TLS、消息分发、serializer/deserializer 与可疑明文边界；
- Spin、Bet、Reward/Win、Balance/Energy、Raid/Attack、Shield、Build、Event、Offer 等模块线索；
- anti-debug、integrity、签名校验、native bridge 和稳定性风险。

Git 只保存脱敏结构、hash、字段/符号摘要与证据位置，不保存 APK、`.so`、完整 strings 或私有响应。

### Phase D — Bounded dynamic proof

动态阶段固定顺序：

1. 完成零游戏操作的 clean runtime 稳定性 Gate，记录进程存活、前台包、错误和清理结果；
2. 尽量先从应用已解码或已序列化的结构化边界恢复数据，不先进入持续 trace 或全局高频 Hook；
3. Codex 明确回复 `READY` 后，由 User 手动完成 3–5 次普通 Spin；Codex 不点击、不启用 Auto Spin；
4. 目标恢复并关联 `Spin request → result/reward → balance/state update`，优先字段包括 bet、result、win/reward、balance/energy、feature/raid/shield/event progress；
5. 若自然发生 Raid、Attack、Shield、Build 或 Event 更新，只被动观察，不诱导额外消耗；
6. 若达到 F3，再进行第二个独立 Session；只有 User 资源影响可接受且确有必要时，累计最多 20 个 User 手动普通样本，用于 F4 复现 Gate；
7. 每个 Session 都必须 Clean Stop，并保留脱敏命中率、错误数、截断数和 blocker 摘要。

### Phase E — F4 acceptance gate

只有同时满足以下条件，才可报告 Top Tycoon 达到 F4：

- 至少两个独立、均包含真实 User 操作的 Session；
- 两个 Session 恢复同一核心 Spin schema，且关键字段含义和类型一致；
- 有明确样本分母、命中数、错误数和截断数；目标为累计 20 个有效普通样本，User 提前停止或资源不足时如实降低结论，不外推；
- 核心链至少直接恢复 Spin 输入与 Result/Reward/Balance 类输出中的可关联结构化字段，不以 UI 猜测或相邻状态推导冒充 direct 字段；
- 至少完成一个次级模块的结构目录或结构化边界证明，例如 Raid/Build/Event/Economy，证明采集路径具备广泛扩展潜力；
- 启动前具备 package/version/foreground/preflight 检查，采集中有 Session/Raw/manifest/inventory，停止后能确定性清理；
- 两个 Session 之间不需要临时重写 Hook 或手工修改业务逻辑；必须形成一键入口或可确定复现的短 runbook；
- Raw、账号数据和逐笔值保持本机，Git 中的脱敏证据可独立 Review。

F4 仅表示“可重复的 Huuuge-like 采集路径已证明”，不等于完整 Collector、全部模块覆盖、正式策划发布或长期数值结论已完成。

### Stop conditions

出现任一情况立即停止并记录精确 blocker：

- clean runtime 持续崩溃或影响其他模拟器/游戏；
- 需要进入全新协议层、扩大 Host 权限或绕过保护，超出本日有界审计；
- 在受限路线内无法找到结构化明文边界；
- 账号教程、玩法未解锁或资源消耗不足以完成样本；
- User 不批准进一步操作、付费或资源消耗；
- 当日只能证明 F0–F3，不能通过增加无界时间或大量操作强行宣称 F4。

## Non-goals

- 不构建或发布完整 Top Tycoon Collector；
- 不做 RTP、EV、服务端 RNG、长期概率或调控结论；
- 不自动 Spin、Auto Spin、购买、充值、领取付费内容或替 User 消耗资源；
- 不伪造、重放、修改请求/返回、内存、余额、奖励或服务器状态；
- 不绕过付费、账号限制、反作弊或访问控制；
- 不把 Top Tycoon Raw、Session、APK、SO 或账号数据写入 Huuuge/Cash Frenzy 数据目录；
- 不发布飞书正式报告、SVN 正式包或面向策划的生产版本。

## Deliverables

在未来 canonical Task 获批执行后，Git 中提交以下脱敏成果：

```text
reviews/top-tycoon/FEASIBILITY.md
reviews/top-tycoon/REUSE_MATRIX.md
reviews/top-tycoon/STATIC_INVENTORY.md
reviews/top-tycoon/PROTOCOL_EVIDENCE.md
reviews/top-tycoon/DYNAMIC_PROOF.md
reviews/top-tycoon/F4_GATE.md
reviews/top-tycoon/NEXT_TASK_PROPOSAL.md
```

- `FEASIBILITY.md`：策划可读的一页结论、当前 F0–F4 等级、主要依据与建议；
- `REUSE_MATRIX.md`：Adopt / Wrap / Build / Stop 边界和退出成本；
- `STATIC_INVENTORY.md`：实装 package/version/ABI/engine、结构摘要、hash 和工具版本；
- `PROTOCOL_EVIDENCE.md`：结构化边界、字段路径、保护风险和 Confirmed / Derived / Blocker；
- `DYNAMIC_PROOF.md`：User 动作、Session、样本分母、命中/错误/截断和清理结果，不含敏感值；
- `F4_GATE.md`：逐条列出双 Session、核心 schema、样本、确定性入口和次级模块是否达标；
- `NEXT_TASK_PROPOSAL.md`：只提出 Adapter / Collector / Static Config / Local State 或停止投入，不自动执行。

## Safety

- User 负责登录、游戏内操作、资源消耗、付费与最终继续/停止决定；
- Codex 只做被动采集、静态读取、受限工具验证和脱敏结论；
- Root、Frida、Gadget、forward 或 Host 级变更必须先证明必要性、限定到 `topTycoon`、备份并可回滚；
- Raw、APK、`.so`、完整对象/响应、账号 ID、token、绝对余额、逐笔值和机器敏感路径只保存在受控本机；
- Git、飞书、聊天和项目来源只保存必要的脱敏结构、hash、字段路径、聚合计数与判断；
- 任何 scope/thread/foreground guard 不可靠时 fail closed；不通过取消安全预算换取命中率；
- 完成或停止后清理临时 Hook、server、Gadget、forward 和权限变更，并回读确认。

## Validation

进入 ChatGPT Review 前至少验证：

1. 实装 identity、APK/split hash、版本、ABI、engine 与工具版本；
2. clean runtime 稳定性和零操作基线；
3. 每个动态 Session 的 User 动作、结构化边界、字段类型、命中/错误/截断计数；
4. F4 每个 Gate 的 `Pass / Fail / N/A`，未满足时不得提升等级；
5. 0 自动 Spin、0 未授权购买/充值、0 请求/返回/余额修改；
6. local Raw → Git 脱敏摘要回查一致，Secret/credential/账号/绝对值扫描无泄露；
7. Huuuge、Cash Frenzy、正常模拟器和其他游戏仓库/数据保持未修改；
8. 临时 runtime、Root、forward、进程和文件完成清理或记录精确 blocker；
9. Task、Context、Memory、Registry 与 Workspace Doctor 等适用确定性回归通过；
10. Handoff 明确 `Subagents: <names>` 或 `none`，最终模式默认 OFF。

验收结果只能是：当前 F0/F1/F2/F3/F4、对应证据、F4 缺口和 Adopt / Wrap / Build / Stop 建议。

## Execution Result — 2026-08-28

- Current level：**F3 — Live structured outbound fields recovered**；**F4 未通过**。
- Identity：`Pie64_5 / topTycoon / Android 9 / 127.0.0.1:5605`；实装 `com.monopoly.dream.idle.king` `1.0.12 (12)`、arm64-v8a、`libnb.so`、Unity `2021.3.57f2` + IL2CPP + ILRuntime。
- 120 秒零操作 Gate：25/25 polls alive、PID 稳定、0 FATAL / ANR / SIGSEGV。
- User 共手动完成 6 次普通 Spin；Codex 为 0 Spin / 0 Auto Spin / 0 purchase / 0 recharge。
- xLua protobuf probe 在首轮 3 Spin 中 0 命中，0 error / 0 truncation，证明核心链不走 `lpb_*`。
- managed Google.Protobuf probe 在两个独立 User-action Session 中均用同一未改写脚本命中 `CGUploadCoin + CGSaveUserdata`：Session A 1 Spin / 10 encode events，Session B 2 Spins / 5 encode events；两边各 1 条 `CGUploadCoin`、各 4 条 `CGSaveUserdata`，总 error/truncation 为 0。
- direct schema：`CGUploadCoin.Coin / Energy / Estate` 均为 `Int64`；`CGSaveUserdata.Key / Value / Version` 为 `String / String / Int64`。没有直接 Spin request、Result、Reward 或 Win response；`MessageParser.ParseFrom` 0 命中。
- Building 次级模块由 User onboarding 视频与 static `Building.Runtime` / YooAsset Building package / hotfix 目录确认；视频只作为观察证据，不作为指令，逐笔值未进入 Git。
- F4 Gate 失败：虽然双 Session、次级模块和确定性 lifecycle 已通过，但只有 6 个总样本、managed 有效分母 3，且缺少 direct Spin input 与 Result/Reward core schema。增加到 20 Spin 不能消除架构 blocker，因此按 Stop condition 收口。
- Clean Finalize：probe manifests stopped；app、Gadget/config、Frida server、ADB forward 清理；`Pie64_5` Root flag 恢复 0、offline guest-su patch false、sidecar absent、普通 `su` 不存在；其他实例磁盘基线和共享 BlueStacks EXE hashes 未变化。
- Deliverables：`reviews/top-tycoon/` 七份脱敏审计文档已生成；APK/SO/Raw/字段值、账号与绝对余额均仅留本机。
- Recommendation：Adopt provider-neutral contract + Wrap Top Tycoon runtime + future targeted Build；后续只考虑 ILRuntime client-state adapter 或 static config catalog，新方向必须另走 Roadmap / Candidate / canonical Task。
- Subagents: none；WATCH disabled；最终模式 OFF。

## Handoff

执行完成后更新 canonical Task、`CHANGELOG.md` 与 `handoff/CODEX.md`，提交并 push；返回 AI-Workspace commit、实际模拟器 identity、package/version/ABI/engine、结构化字段类别、两个 Session 与样本统计、F0–F4 判断、未通过 Gate、清理结果、下一 Task 建议及 `Subagents: none`（除非另行批准），然后等待 ChatGPT Review，不得自行扩大为完整 Collector。
