# Cash Frenzy Collector Feasibility — Ready for Review

- Related Task: `TASK-0022`
- Date: 2026-08-27
- Current level: **F3 — Live structured outbound fields recovered**
- Decision proposal: **Wrap + Build**
- Review status: Ready for ChatGPT Review

## 一页结论

**Confirmed · Static**：Cash Frenzy Android package 为 `slots.pcg.casino.games.free.android`，现场版本 4.78 / versionCode 478、arm64-v8a，采用 Cocos2d-x + LuaJIT，主 native 为 `libcocos2dlua.so`。客户端包含 `BLSocket` command map、LuaJIT Systems/Themes、TLS/WebSocket/LuaSocket/XXTEA/Protobuf 痕迹，但 APK 内没有游戏业务 descriptor。

**Confirmed · Runtime**：`AppResearch` 中 outer x64 Frida 看不到 arm64 主模块；通过已审计 Houdini bootstrap 临时加载 Frida 17.17.0 Gadget 后，arm64 `libcocos2dlua.so` 可见。大厅业务流量没有经过模块内 `SSL_read/write`、BIO、LuaSocket 或 WebSocket；真实活动路径是 `BLSocket`，process socket 边界为 UDP `sendto/recvfrom`。

**Confirmed · Spin**：User 在金猪主题机台以 Bet 10000 累计执行 5 次普通 Spin，无自然 Feature。首轮 3 次与 3 个新 255-byte outbound packet 对齐；第二轮 2 次与 2 个同构 Lua request 对齐。schema-only hook 恢复 request table：`[command-string, payload-table, metadata-table]`，Spin payload 出现 `bet`、`lines`、`spin_count`、`client_coins`、`free_spins`、`autoSpin`、`turbo`，metadata 出现 `_timestamp`。字段值、账号和逐笔余额未写入 Git。

**Inference**：长度为 10 的 command string、static `BATCH_SPIN` map、字段集合和 User 动作高度一致，因此该 request 很可能是 `BATCH_SPIN`；本次探针未读取 command 值，不能标为直接观察。

**Blocker**：入站仍是不透明二进制 Raw；`BLMessage.getObj` 在 Spin proof 中未触发，尚未恢复 result、win、balance 或 update 字段。当前达到 F3，但未完成真实数值闭环、跨 Session decoder 或策划一键路径，F4 不成立。

**Decision proposal**：不复制 Huuuge Collector。Adopt 其 lifecycle/manifest/Raw/privacy contract，Wrap `AppResearch` package binding，Build Cash-specific inbound decoder、command/schema mapping 与 module taxonomy。下一步应先定位 `BLMessage` 构造/dispatch 的解密后边界，再决定是否构建 Passive Collector Adapter。

## 分项等级

| Area | Level | Confirmed evidence | Gap |
| --- | --- | --- | --- |
| Package / engine | F3 | install、split、ABI、native bridge、arm64 module live verified | 无关键缺口 |
| Slots / Spin protocol | F3 | 5 次 Spin packet correlation；live request field schema | 入站 result/win/balance 未恢复 |
| Feature / Free Spin / Jackpot | F1 | static command/module names | 5 次 Spin 均未自然触发 |
| Systems / Events / Offers | F2 | lobby BLSocket live traffic observed | 无结构化 payload |
| Local config/static math | F1 | LuaJIT/JSON/plist/resource inventory | 未恢复业务数值配置 |
| Repeatable collector path | F3 | baseline、3-Spin、2-Spin Session 均 start/READY/stop；0 errors | 无 inbound decoder、inventory/catalog/GUI |

## 安全与恢复

- Raw、APK、split、SO、完整响应、账号数据和本机探针仅在 `CashFrenzyResearch/local-only`。
- 只提交字段名/类型、聚合包计数、hash、版本和判断；不提交二进制、字段值或私有 endpoint。
- User 负责登录与 5 次普通 Spin；Codex 未点击、购买、充值、自动 Spin、修改请求/返回值或游戏状态。
- 两个 Cash 专属 Gadget 文件、ADB forward 和临时 Frida server 已移除；Cash app 已停止，无残留 capture 进程。
- `huuuge-android-research@4a5dddf7782307c6a8f368c9f1dc6390eec6f65b` 保持 clean；Huuge Collector、Session、Raw、SVN 未修改。
- Subagents: none；mode OFF；Workspace Sync `ON_DEMAND`；WATCH disabled。
