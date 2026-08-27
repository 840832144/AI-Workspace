# TASK-0024 — Cash Frenzy Inbound Structured Capture Spike

- Status: Review
- Project key: CASH-FRENZY
- Human alias: 
- Owner: User / ChatGPT
- Executor: Codex
- Priority: P1 / focused research spike
- Date: 2026-08-27
- Updated: 2026-08-27
- Candidate provenance: `tasks/candidates/CANDIDATE-20260827-CASH-FRENZY-INBOUND-STRUCTURED-CAPTURE.md`
- Allocation relationship: new
- Related tasks: TASK-0022

## Goal

在 Cash Frenzy Android 9 上按稳定性 Gate、inbound-scoped Lua 参数、BLMessage 解码对象、decrypt/framing fallback、Local State Adapter 的顺序，恢复一次普通 Spin 的 direct result/win/balance/feature 至少一项，或按停止条件给出可复查 blocker。

## Scope

本 Task 是 `TASK-0022` 之后的新范围，不回写或扩大已完成的 Feasibility Audit。只研究 Cash Frenzy Android 9 入站结构化采集，固定按以下顺序推进；后序路线只有在前序失败并留下证据时才可进入：

1. **稳定性 Gate**：先完成无操作 clean Gadget 稳定性测试，记录 attach/load、进程存活、前台包、crash signature、持续时间和清理结果；此阶段 0 Spin。
2. **Inbound-scoped Lua 参数**：仅在 Cash inbound dispatch thread 且 `onUIThreadReceiveMessage` 调用 scope 内，采集 `LuaStack/lua_pcall` 入参；禁止全局高频 Lua API 日志。
3. **`BLMessage` 解码后对象**：在已确认 inbound type/dispatch/conversion boundary 上读取解码后对象的 shape 与受限字段路径，不把边界命中等同于字段恢复。
4. **decrypt/framing fallback**：只有 Lua 与 `BLMessage` 两条结构化路线都有失败证据时，才研究 `libEncryptorP`、`libsigner`、XXTEA 调用链；Stalker 仅允许单消息 summary，不做持续 trace。
5. **Local State Adapter**：前四步无法得到 direct 字段时，最后评估受控、本地只读状态变化；不得把相邻 outbound `client_coins` 再包装成 direct inbound Balance。

第一目标是恢复一次普通 Spin 的 direct `result / win / balance / feature` 中至少一项；不先写完整 Collector，不继续 Nougat64。

### Environment identity gate

- User 已删除旧 `AppResearch2`，重新创建同名 Android 9 实例并安装 Cash Frenzy。
- 执行前必须重新确认 BlueStacks internal instance ID、ADB serial、Android 版本、package、version/versionCode、ABI、native bridge 与前台包；不得沿用旧 Android 7 `AppResearch2 / Nougat64` 的身份或配置。
- 仅使用这一个 Cash 研究实例和 Cash 专属本机目录；不修改正常 BlueStacks、HuuugeResearch、其他游戏或 Huuuge Collector。

### Serializer safety budget

优先实现受限递归 Lua stack serializer，并把限制做成显式常量与 focused tests：

- 默认最大递归深度 `4`；
- 默认每 table / collection 最大元素数 `64`；
- 默认单消息序列化上限 `64 KiB`；
- 循环引用检测；不可安全读取的 userdata/function/thread 只输出类型摘要；
- 超限时写入 `truncated`、`reason`、计数与字段路径，不继续展开；
- 只有已标记的 Cash inbound dispatch thread/scope 激活，离开 scope 立即关闭。

若运行时需要调整预算，必须先用 synthetic/offline test 证明边界行为并记录实际值；不得通过取消限制换取命中率。

### Dynamic interaction gate

- 动态阶段先完成无操作稳定性测试。
- 需要真实 gameplay event 时暂停并明确通知 User，由 User 手动执行 `3–5` 次普通 Spin；Codex 不点击 Spin、不启用 Auto Spin。
- 只被动观察自然出现的 Feature；不诱导购买、充值、额外资源消耗或长时间挂机。

## Non-goals

- 不构建完整 Cash Frenzy Collector，不发布 planner-facing GUI / installer / SVN package。
- 不继续 Android 7 / Nougat64，不复用旧实例 identity。
- 不做全局高频 Lua API 日志、持续 Stalker trace、长时间 capture、RTP/EV 或服务端 RNG 结论。
- 不自动 Spin、Auto Spin、购买、充值、领取付费奖励或替 User 消耗资源。
- 不伪造、重放或修改请求/返回值，不修改内存、余额、奖励或服务器状态。
- 不研究 Top Tycoon、Gossip Harbor、Huuuge 或其他游戏。

## Deliverables

Git 只提交：

- canonical Task 与执行/停止条件；
- 受限 serializer、scope guard、聚合器等工具和 focused tests；
- 脱敏结构、字段路径、类型、聚合计数、稳定性结论与 crash signature 摘要；
- Confirmed / Derived / Blocker、F3/F4 判断和 Adopt / Wrap / Build 建议。

本机保存：Raw、APK、`.so`、完整 response/object dump、账号/session 值、绝对余额、逐 Spin 完整值与机器敏感路径。

## Safety

- 所有 Hook 只在 Cash inbound dispatch thread/scope 激活；scope 不能可靠限定时 fail closed。
- 只复制客户端已经解码、序列化或本地可见的状态用于被动分析；不改变控制流、请求、返回或值。
- Raw 与敏感资料只保存在 `D:\CashFrenzyResearch\local-only\` 或等价受控本机目录，不进入 AI-Workspace、Huuuge Git、SVN、飞书或聊天。
- Android 9 clean Gadget 若仍连续崩溃，停止并保留 blocker；不通过关闭安全限制、扩大 Host 修改或回到 Nougat64 规避 Gate。
- 若一天内只能证明必须进入全新协议层，停止并给出 blocker，不无限消耗。

## Validation

进入 ChatGPT Review 前必须确认：

1. 实际 Android 9 clean Gadget 稳定性与无操作时长；
2. 命中的结构化边界，以及 scope/thread 证据；
3. direct 恢复的 `result / win / balance / feature` 字段，或每条路线的失败证据；
4. 有足够人工样本时给出 `20-Spin` 复现率；若本轮只获准 3–5 Spin，则明确样本不足，不虚构 20-Spin 结论；
5. F3/F4 判断与 Adopt / Wrap / Build 建议；
6. 0 自动 Spin、0 购买/充值、0 请求/返回修改；Raw/敏感扫描与 Hook 预算测试通过；
7. 所有临时 Hook、forward、process 与环境变更均清理或记录明确 blocker。

## Handoff

更新本 Task、`CHANGELOG.md` 与 `handoff/CODEX.md`，提交并 push 后返回：实际稳定性、命中的结构化边界、恢复字段、20-Spin 复现率或失败证据、F3/F4 判断、下一步 Adopt / Wrap / Build 建议、`Subagents: none`，然后等待 ChatGPT Review。不得自行扩大为完整 Collector。

## Execution Progress — Pre-Spin Gate

### Confirmed environment

- 新同名实例现场确认为 BlueStacks internal ID `Pie64_3`、display name `AppResearch2`、Android 9、ADB `127.0.0.1:5585`、x86_64 Host + `libnb.so` arm64 native bridge。
- Cash Frenzy package `slots.pcg.casino.games.free.android`，版本 `4.78 / 478`，primary ABI `arm64-v8a`；旧 Android 7 `Nougat64` identity 未复用。
- Root 前完成 clean VHDX、配置/磁盘/descriptor 本机备份与 SHA-256 一致性验证；只修改 `Pie64_3` 的 root flag 和两个已审计 guest-`su` 三字节入口，现场 `uid=0(root)`。正常 `Pie64` 保持 root flag 0，`Pie64_1` 未启动。

### Stability Gate

- Android 9 clean Gadget 在 120 秒零操作测试中完成 arm64 `libcocos2dlua.so` namespace load，Cash 始终存活且前台包正确。
- 0 probe errors、0 matching `gum-js-loop` / GLThread SIGSEGV / Fatal signal；计划内 `application-requested` detach 的 `crash_present=false`。
- 结论：旧 Android 7 约 15 秒 crash blocker 在当前 Android 9 Gate 中未复现，可以进入 scoped Hook。

### Inbound-scoped Lua baseline

- 60 秒零操作 Lua baseline：21 个 type-3 `onUIThreadReceiveMessage` scope、21 个 scope 内 `lua_pcall` 参数事件，全部来自 1 个 dispatch thread。
- 事件结构为 `arg[1]: number`、`arg[2]: table`；`arg[2].[1]` 是 command string，`arg[2].[2]` 是 payload，`arg[2].[3]._timestamp` 是 metadata。
- command 聚合为 `tick=15`、`keepalive=6`。keepalive payload 的 value-free 路径包含 `avg_bet.bc`、`chips`、`coins`、`keepalive_from`、`time`。
- 0 errors、0 truncation；没有全局 Lua API 日志。`coins/chips` 已证明 direct inbound structured Balance 类边界存在，但尚未与普通 Spin 关联，不能作为 Task 第一目标完成证据。

### Current gate

启动新的 scoped capture 后暂停，由 User 手动执行 3–5 次普通 Spin；在 User 回报完成前不进入 `BLMessage`、decrypt/framing、Local State Adapter 或完整 Collector。

## Execution Result — User 5-Spin Gate

### Confirmed

- User 在 READY 后手动执行 5 次普通 Spin；Codex 没有点击、Auto Spin、购买、充值、修改请求或修改返回。
- Session 捕获 65 个 type-3 inbound scopes / 65 个 scope 内 `lua_pcall` 参数事件，始终只有 1 个 dispatch thread，0 probe errors。
- command `batch_spin` 恰好出现 5 次；5 个事件均包含同一 direct structured result entry：`arg[2].[2].list.[1]`。
- 5/5 事件均命中 `base_win:number`、`bonus_base_win:number`、`total_win:number`、`coins:number`、`win_lines:table`、`win_pos_list:table`。字段值和绝对余额未进入 Git。
- Spin pilot 复现率为 **5/5（100%）**。本轮只获准 3–5 次人工 Spin，样本不足以报告 20-Spin 复现率；20-Spin 结论为 `N/A`，不做外推。
- serializer 保持 depth 4、64 elements/collection、64 KiB/message、32 pcalls/scope；Spin Session 有 159 个预期的 `depth-budget` 截断摘要，0 element/message budget overflow，0 serializer/probe error。

### Route decision

- 第一条结构化路线已经成功恢复 direct Result/Win/Balance 类字段，因此按顺序 Gate 停止；没有进入 `BLMessage`、decrypt/framing、`libEncryptorP` / `libsigner` / XXTEA、Stalker 或 Local State Adapter。
- 本轮没有自然出现可确认的 Feature 字段；这不影响“至少恢复一项”的成功条件。

### F3 / F4

- 当前等级仍为 **F3，但证据已从 outbound-only 增强为 live inbound structured Spin result/win/balance recovered**。
- **F4 未证明**：本轮只有一个含 Spin 的独立 Session，未满足“两独立 Session 同一 Spin schema”和 20-Spin 样本要求；也未构建可重复的一键 collector path。

### Cleanup

- Cash app 已 force-stop；临时 probe process、Frida server、Gadget/config 与 ADB forward 已移除并回读确认。
- `Pie64_3` guest-`su` 两处入口已由审计工具恢复，root flag 已回到 0，VHDX clean 且 root state false；本机可回滚备份保留。
- Huuuge repo、正常 BlueStacks、其他游戏、SVN、飞书、请求/返回和服务端状态均未修改。

### Final validation

- local Raw → Git 脱敏聚合逐字段回查一致；email/credential scan 0 hit，Git artifact 不含字段值或绝对余额。
- focused probe tests 3/3、Task tests 23/23、Context tests 13/13、Memory tests 35/35、Task/Context PowerShell entry 与 Workspace Doctor 全部通过；Registry 11 canonical / 0 collision。
- Workspace Sync 保持 `ON_DEMAND`、0 conflict；provider unavailable，6 个发布项保持 stale，没有启用 WATCH。

### Recommendation

等待 ChatGPT Review。若 Review 接受本 Spike，建议 **Adopt** 既有 Session/Raw/privacy/evidence contract，**Wrap** Android 9 exact instance/package/version 与 scoped Lua preflight/cleanup，后续只在新授权 Task 中 **Build** 最小 `batch_spin` inbound schema adapter；当前不构建完整 Collector。
