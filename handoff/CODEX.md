# Codex Handoff

- Updated: 2026-08-27
- Task: TASK-0022 — Cash Frenzy Android Collector Feasibility Audit
- Status: Review
- Branch: `codex/task-0022-cash-frenzy-feasibility`
- Issuance main merge: `694e955b76405bd6fb97203110d6bc6f9a1185b2`
- Workspace Sync: `ON_DEMAND`
- WATCH: disabled
- Subagents: none
- Subagent mode: OFF

## Outcome

TASK-0022 已完成 Reuse-first、package/version/ABI/engine、APK/split、native/LuaJIT/resource、protocol static audit 和 5 次 User 普通 Spin 的最小动态证明。整体等级为 **F3 Live structured outbound fields recovered**；入站 result/win/balance/update 未解码，F4 不成立。

## Environment Decision

Task 早期建议独立 `CashFrenzyResearch`。动态门槛处 User 明确将原 `HuuugeResearch` 重命名为共享 `AppResearch`，并指定以后测试 App 共用该实例；这是最新决定。

- Runtime target：`Pie64_1 / AppResearch`、Android 9、ADB alias `emulator-5564`、x86_64 + `libnb.so` arm64 native bridge。
- Package：`slots.pcg.casino.games.free.android` 4.78 / 478 / arm64-v8a。
- 数据隔离：Cash APK/SO/static、probe、Session、Raw、manifest 与账号数据仅在 Host-local `CashFrenzyResearch/local-only`；不进入 Huuuge 路径或 Git。

## Reuse-first Decision

只读 baseline：`huuuge-android-research@4a5dddf7782307c6a8f368c9f1dc6390eec6f65b` / Collector 1.0.1。

- Adopt：lifecycle、manifest/state、Raw immutability、privacy、evidence discipline。
- Wrap：`AppResearch` + exact package binding、Frida/Gadget staging/cleanup、APK/split inventory。
- Build：Cash `BLSocket`/UDP adapter、Lua request schema、inbound decoder、module taxonomy。
- Reject：Huuuge descriptor/decoder、agent.js、Session/Raw/database/Collector runtime。

## Static Results

- Cocos2d-x + LuaJIT；main native `libcocos2dlua.so`；entry `org.cocos2dx.lua.AppActivity`。
- base + arm64-v8a + hdpi + zh splits；APK signing v3；minSdk 24 / targetSdk 35。
- 16,887 LuaJIT bytecode；Systems 5,739 files；Themes 528 files。
- Static protocol signals：`BLSocket`、`BATCH_SPIN`/keepalive/reconnect/enter-theme/jackpot command map、TLS/LuaSocket/WebSocket/XXTEA/Protobuf/encryption/signing candidates。
- 23 个 proto/textproto 均为 SDK 范围；无游戏业务 descriptor。

## Dynamic Results

- Outer x64 Frida 看不到 arm64 target；已审计 Houdini bootstrap + temporary Frida 17.17.0 Gadget 成功进入 Cash app namespace。
- 大厅活动路径：`BLSocket` + UDP `sendto/recvfrom`。`SSL_read/write`、BIO、LuaSocket 与 WebSocket 在验证窗口内均 0。
- 15 秒 baseline：5 outbound / 207 bytes，5 inbound / 378 bytes，0 errors，opaque binary。
- User action：金猪主题机台，Bet 10000，累计 5 次普通 Spin，无自然 Feature、Auto Spin、购买或充值。
- 3-Spin proof：36 outbound / 2,048 bytes，38 inbound / 14,793 bytes；恰好 3 个 novel 255-byte outbound packet，随后出现 1.1–2.5 KB inbound bursts。
- 2-Spin proof：31 outbound / 1,617 bytes，34 inbound / 9,960 bytes；恰好 2 个 255-byte packet 和 2 个同构 Lua request。
- Live request shape：`[command-string, payload-table, metadata-table]`；Spin payload fields=`autoSpin`、`bet`、`client_coins`、`free_spins`、`lines`、`spin_count`、`turbo`，metadata=`_timestamp`。字段值未记录。
- Inference：length-10 command + static map + Spin correlation 高置信对应 `BATCH_SPIN`，但 command 值未直接读取。
- Blocker：inbound `BLMessage.getObj` 未触发；result/win/balance/update schema 未恢复，完整数值链和 F4 decoder 未证明。

## Cleanup and Safety

- 所有 Raw/Lua shape Sessions Clean Stop；正式 Sessions 0 errors；无 capture/shape process。
- Cash app 已停止；Cash 专属 Gadget/config、ADB 27043 forward 与临时 Frida server process 已移除。
- 预存 Frida server binary 未删除；`AppResearch` 保留为 User 指定共享实例。
- Huuuge repo clean；Collector、Session、Raw、SVN、飞书与业务仓库未修改。
- Raw、APK、SO、完整响应、账号、endpoint 与字段值未进入 Git。

## Deliverables

- `reviews/cash-frenzy/FEASIBILITY.md`
- `reviews/cash-frenzy/REUSE_MATRIX.md`
- `reviews/cash-frenzy/STATIC_INVENTORY.md`
- `reviews/cash-frenzy/PROTOCOL_EVIDENCE.md`
- `reviews/cash-frenzy/DYNAMIC_PROOF.md`
- `reviews/cash-frenzy/NEXT_TASK_PROPOSAL.md`


<!-- MEMORY-REFRESH:START -->
## Memory Context Refresh

- Generated: 2026-08-27T10:29:11Z
- Effective mode: `ASSISTED`
- Manifest: `CONTEXT_MANIFEST.yaml`
- ChatGPT Project Sources: `manual upload required`
- Private repositories: not read unless explicitly registered and authorized
<!-- MEMORY-REFRESH:END -->
## Exact Next Action

ChatGPT Review TASK-0022。重点检查：F3 分级是否恰当、共享 `AppResearch` 的 package/data isolation 是否足够、`BATCH_SPIN` 是否保持 Inference、是否应批准新的 Inbound Protocol Decoder / Passive Collector Adapter Candidate。Review 前不创建新 Task，不启用 WATCH，不继续 Spin。
