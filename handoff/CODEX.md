# Codex Handoff

- Updated: 2026-08-27
- Current task: TASK-0022 — Cash Frenzy Android Collector Feasibility Audit
- Status: Review — Slots Deep Research stopped at AppResearch2 runtime / inbound boundary
- Branch: `codex/task-0022-cash-frenzy-feasibility`
- Workspace Sync: `ON_DEMAND`
- WATCH: disabled
- Memory mode: `ASSISTED`
- Subagents: none

## Current decision

- User 明确停止 Demo，继续同一 `TASK-0022` 的 Cash Frenzy Slots Deep Research；不新建 Task。
- 本轮使用 User 新建的 `AppResearch2`，没有使用旧 `AppResearch`，没有修改 Huuuge / Top Tycoon / Gossip Harbor / Collector 主架构。
- User stop gate 已触发：direct Win 需要新的 inbound protocol / runtime 层，且 AppResearch2 的 arm64 Gadget 可复现崩溃；动态研究已停止。

## Current recovery state

- **Balance — Recovered / Derived**：Phase 1.5 已用相邻 outbound `client_coins` 形成 Balance Before / After；Session 尾部仍有 open transition。
- **Win — Derived candidate only**：`next_balance - current_balance + bet` 可复算；未观察到 direct / server `win` 字段。
- **Result — Not recovered**：已定位 `BLMessage.type @ +0x24` 和 type 3 inbound dispatch，但未恢复明文字段。
- **Feature / Jackpot — Not recovered**：仅有 static command/module names；本轮 0 Spin。
- Collector 等级保持 **F3 Live structured outbound fields recovered**。

## AppResearch2 proof

- Environment：`Nougat64 / AppResearch2`，Android 7.1.1，ADB `127.0.0.1:5555`，x86_64 + `libnb.so` arm64 translation；Android ID 与旧 AppResearch 不同。
- App：`slots.pcg.casino.games.free.android` 4.78 / 478 / arm64-v8a。
- Nougat64 使用 legacy `NativeBridgeLoadLibrary(path, flags)`；Cash-local bootstrap 从 `/data/local/tmp` 成功加载 Frida 17.17.0 arm64 Gadget 并返回非空 handle，最小 probe 确认 `Process.arch=arm64`。
- 20 秒无操作 boundary：`sendMsg=6`、`sendTable=1`、`sendTickMsg=5`、`onSocketCallback=12`、`onUIThreadReceiveMessage=6`。
- guest / lobby Session 捕获 23 条 inbound message，全部 type 3，`ccvalue_to_luaval` dispatch-scope conversions=0，errors=0。
- Codex 只执行两个单点 UI tap：进入 guest 流程、领取免费 starter login reward；无 Spin、购买、充值、付费奖励、Auto Spin 或挂机。

## Exact blocker

- AppResearch2 拒绝向 `/data/app/.../lib/arm64` 写入，不能复用 Pie64 app namespace staging；只能从临时路径走 legacy bridge。
- 一次 delegate-vtable 枚举触发 SIGSEGV 后已永久停止该探针。
- 后续不加载业务 hook 的 clean Gadget run 仍复现 `gum-js-loop` + GLThread SIGSEGV；将资源从 1 GB / 2 CPU 提高到 4 GB / 4 CPU 后仍复现，排除单纯资源不足。
- 下一技术路线必须二选一：在 Android 9 级稳定 runtime 中继续 `BLMessage` / EventCustom 明文边界，或正式进入 UDP inbound framing / decrypt / dispatch 恢复。两者都属于新运行时或新协议层，当前不继续。

## Prior Demo state — frozen out of scope

- 既有 Collector Demo Markdown、图表和飞书文档保持原状；本轮不更新 Documentation / Report，不处理历史 Hub registration blocker，也不重复创建文档。

## Clean finalize

- Cash app force-stop；AppResearch2 专属 Frida server、Gadget/config、ADB `tcp:27042` / `tcp:27043` forwards 均删除或移除并回读确认。
- AppResearch2 root / CPU / RAM 已回滚到 `off / 2 / 1024 MB`；重启后 `su: not found`，Cash process 不存在。
- 新 Session、探针、runtime 和截图只留 `D:\CashFrenzyResearch\local-only`；没有 Raw、账号、字段值、APK、SO 或完整响应进入 Git。
- `D:\huuuge-research` 未修改；Workspace Sync `ON_DEMAND`，WATCH disabled；Subagents none / OFF。

<!-- MEMORY-REFRESH:START -->
## Memory Context Refresh

- Generated: 2026-08-27T10:39:09Z
- Effective mode: `ASSISTED`
- Manifest: `CONTEXT_MANIFEST.yaml`
- ChatGPT Project Sources: `manual upload required`
- Private repositories: not read unless explicitly registered and authorized
<!-- MEMORY-REFRESH:END -->

## Exact Next Action

ChatGPT Review 本轮 TASK-0022 Slots Deep Research 结论。Review 前不再启动 Cash、注入 Gadget、执行 Spin、处理 Demo/Documentation，或扩展 Collector。若未来批准继续，优先选择 Android 9 级独立 Cash runtime 复验 `BLMessage` / EventCustom；否则新协议层应先形成单独审计范围再执行。
