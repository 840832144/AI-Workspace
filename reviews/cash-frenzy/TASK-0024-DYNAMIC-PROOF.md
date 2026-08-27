# TASK-0024 — Cash Frenzy Inbound Structured Capture Dynamic Proof

- Status: Accepted / Complete
- Date: 2026-08-27
- Evidence: Confirmed unless explicitly marked otherwise
- Raw policy: local-only; this file contains no values, account data, full responses, APK/SO or absolute balance

## Environment

- BlueStacks `Pie64_3 / AppResearch2`, Android 9, ADB `127.0.0.1:5585`。
- Cash Frenzy `slots.pcg.casino.games.free.android`，`4.78 / 478`，arm64-v8a on x86_64 + `libnb.so`。
- 旧 Android 7 / Nougat64 AppResearch2 已删除且未复用。

## Stability Gate

- clean Gadget duration：120 秒，0 gameplay action。
- Gadget：arm64，`libcocos2dlua.so` 通过 `NativeBridgeLoadLibraryExt` 的真实 namespace 加载。
- Result：Cash process alive、foreground package matched、0 probe errors、0 matching crash lines。
- Planned detach：`application-requested`，`crash_present=false`。

## Lua Boundary

- Hook 仅在同 thread 的 `onUIThreadReceiveMessage` scope depth > 0 时采集 `lua_pcall` 参数。
- Baseline：21 inbound scopes / 21 scoped pcalls / 1 dispatch thread / type 3 only。
- Commands：`tick=15`、`keepalive=6`。
- Value-free field paths：

```text
arg[1]: number
arg[2]: table
arg[2].[1]: string
arg[2].[2]: table
arg[2].[2].avg_bet: table
arg[2].[2].avg_bet.bc: number
arg[2].[2].chips: number
arg[2].[2].coins: number
arg[2].[2].keepalive_from: number
arg[2].[2].time: number
arg[2].[3]: table
arg[2].[3]._timestamp: number
```

- 0 serializer errors、0 truncation；limits 为 depth 4、64 elements/collection、64 KiB/message、32 pcalls/scope。
- `coins/chips` 是 direct inbound structured fields；当前只在 keepalive baseline 观察到，尚未与普通 Spin 关联。

## Manual 5-Spin Proof

- User 在 capture READY 后手动执行 5 次普通 Spin；0 Auto Spin、0 购买/充值、0 Codex gameplay click。
- Session：65 inbound scopes / 65 scoped pcalls / 1 dispatch thread / type 3 only / 0 probe errors。
- `batch_spin` command：5 events；与 5 次 User action 计数对齐。
- direct result boundary：`arg[2].[2].list.[1]`。
- 5/5 event field paths：

```text
arg[2].[2].list.[1].base_win: number
arg[2].[2].list.[1].bonus_base_win: number
arg[2].[2].list.[1].coins: number
arg[2].[2].list.[1].total_win: number
arg[2].[2].list.[1].win_lines: table
arg[2].[2].list.[1].win_pos_list: table
```

- Pilot reproducibility：**5/5（100%）**。本轮授权明确限制为 3–5 次人工 Spin，不能给出 20-Spin 复现率；20-Spin 结果为 `N/A / insufficient authorized sample`。
- serializer 预算未放宽：depth 4、64 elements、64 KiB/message、32 pcalls/scope。159 个 `depth-budget` 摘要是受限递归的预期结果；0 element/message overflow、0 serializer/probe error。

## Evidence Classification

- **Confirmed**：Android 9 clean Gadget 120 秒稳定；inbound-dispatch scope guard 生效；`batch_spin` 5 次；上述 direct Result/Win/Balance 类字段路径各 5 次。
- **Derived**：5 个 `batch_spin` event 与 User 5 次普通 Spin 一一对应，依据 READY 后唯一手动 gameplay action、command 名与精确计数相关性；未记录或提交值。
- **Blocker**：本轮只有一个含 Spin 的独立 Session，因此 F4 的双 Session 重复性和 20-Spin 样本未满足；Feature 未自然出现。

## Route and Level Decision

- Lua 路线成功，按 Gate 不进入 `BLMessage`、decrypt/framing、XXTEA、Stalker 或 Local State Adapter。
- 等级保持 **F3 strengthened**：从 outbound-only 提升为 live inbound structured Spin result/win/balance recovered；**F4 未证明**。
- Recommendation：**Adopt** evidence/Raw contract，**Wrap** Android 9 identity + scoped Lua lifecycle，未来独立授权后 **Build** 最小 `batch_spin` schema adapter；当前不建设完整 Collector。

## Clean Finalize

- Capture 正常 STOPPED；Cash app、probe、Frida server、Gadget/config 和 ADB forward 均已停止或删除并回读确认。
- `Pie64_3` root flag、guest-`su` 与 VHDX 已恢复为 clean / root false；本机备份保留。
- Raw、字段值、完整 response、账号与绝对余额只在本机；Huuuge repo、正常 BlueStacks、其他游戏、SVN 与飞书未修改。
- 脱敏聚合与 local summary 逐字段回查一致；focused 3/3、Task 23/23、Context 13/13、Memory 35/35、Task/Context PowerShell entry、Workspace Doctor 与 Registry 11 canonical / 0 collision 全部通过。
- Workspace Sync：`ON_DEMAND`、0 conflict、provider unavailable、6 stale；WATCH disabled。

## Recovered Operational Issues

- 一次旧 `HD-Adb` client 启动时重启了 ADB daemon并清空 forward；重新连接 5585、恢复 27043 后确认 Cash process、前台包和 Gadget 均正常，再启动 User Spin capture。Spin Session 本身 0 errors。
- command-profile focused test 初版把非 payload argument 的 synthetic direct fields 计入 profile；已将规则收紧为 `arg[2].[2]` payload-only 并回归通过。
