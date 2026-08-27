# Cash Frenzy Collector Feasibility — In Progress

- Related Task: `TASK-0022`
- Date: 2026-08-27
- Current level: **F1 Static-only**
- Decision proposal: **Wrap + Build**
- Review status: Not ready；等待独立环境安装与最小动态证明

## 一页结论

**Confirmed · Static L1**：Cash Frenzy Android 包为 `slots.pcg.casino.games.free.android`，当前只读样本是 4.78 / versionCode 478、arm64-v8a。客户端采用 Cocos2d-x + LuaJIT，主 native 为 `libcocos2dlua.so`，业务层包含大量编译 LuaJIT 脚本、主题和系统资源。

**Confirmed · Static L1**：客户端存在自定义 `BLSocket`、command map、socket state、keepalive、reconnect、batch spin、enter theme 与 jackpot 等静态符号；native 同时包含 TLS read/write、LuaSocket、WebSocket、XXTEA 与 Protobuf 痕迹。APK 内可见的 `.proto` 仅能归因于 Google/Firebase 等 SDK，没有恢复到 Cash Frenzy 游戏业务 descriptor。

**Decision proposal**：不复制 Huuuge Collector。复用其 Session lifecycle、manifest、Raw 隔离、inventory/catalog、privacy 与 evidence discipline；为 Cash Frenzy 新建 package/ABI binding、`BLSocket` 明文层定位、LuaJIT command/schema mapping 和模块分类 Adapter。

当前只能评为 F1。进入 F2/F3 前必须在独立 `CashFrenzyResearch` 中完成安装、版本复核和 1–5 次 User 普通 Spin 的被动动态尝试。

## 分项等级

| Area | Level | Current evidence | Gap |
| --- | --- | --- | --- |
| Package / engine | F1 | package metadata、APK/split、Cocos/LuaJIT signatures | 独立实例复核 |
| Slots / Spin protocol | F1 | command names 与 `BLSocket` static symbols | 无 live request/result |
| Feature / Free Spin / Jackpot | F1 | static command/module names | 无 live state transition |
| Systems / Events / Offers | F1 | LuaJIT Systems/Themes/resource inventory | 无 live payload |
| Local config/static math | F1 | compiled LuaJIT、JSON/plist/atlas/csb inventory | 尚未恢复业务数值结构 |
| Repeatable collector path | F0 | 尚未在独立环境启动 Capture | 需要最小动态 proof |

## 安全结果

- APK、split、SO、完整字符串和本地提取目录仅留本机。
- 未读取 Cash Frenzy 应用私有数据、账号数据、Session 或 Raw。
- 未启动或修改 Huuuge Collector；`huuuge-android-research@4a5dddf7782307c6a8f368c9f1dc6390eec6f65b` 保持 clean。
- 未修改 `HuuugeResearch`；现有安装只作为 package APK 的只读来源。
- Subagents: none；mode OFF。
