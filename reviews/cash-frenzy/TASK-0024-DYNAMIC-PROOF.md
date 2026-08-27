# TASK-0024 — Cash Frenzy Inbound Structured Capture Dynamic Proof

- Status: In Progress / Awaiting User Spin
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

## Pending User Action

在 scoped capture 显示 READY 后，由 User 手动执行 3–5 次普通 Spin。Codex 不点击 Spin、不启用 Auto Spin、不购买或充值。
