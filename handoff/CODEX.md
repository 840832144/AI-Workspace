# Codex Handoff

- Updated: 2026-08-27
- Current task: TASK-0022 — Cash Frenzy Android Collector Feasibility Audit
- Status: Review — Phase 1.5 complete, waiting ChatGPT Review
- Branch: `codex/task-0022-cash-frenzy-feasibility`
- Latest-main sync: merge `a1d055f` includes `origin/main@cf5ec9d`
- Workspace Sync: `ON_DEMAND`
- WATCH: disabled
- Memory mode: `ASSISTED`
- Subagents: none

## Phase 1 result

- Cash Frenzy identity：package `slots.pcg.casino.games.free.android`，sample 4.78 / 478，arm64-v8a，Cocos2d-x + LuaJIT，base + 3 splits。
- Dynamic proof：User 完成 5 次普通 Spin；live outbound Spin payload 已恢复 `bet`、`lines`、`spin_count`、`client_coins`、`free_spins`、`autoSpin`、`turbo` 与 `_timestamp`。
- Current level：**F3 Live structured outbound fields recovered**。Inbound result 仍为 opaque binary；F4 不成立。
- Research runtime：User 已将共享研究实例命名为 `AppResearch`。Cash Frenzy 证据继续按 package、Host-local project root、Session、Raw、APK/SO、账号数据和 manifest 隔离，不与 Huuuge 混用。

## Phase 1.5 — Balance Recovery Spike

- Scope 仅为 Balance，Win 只在低成本条件下顺带验证；没有进入新协议层、OCR/UI、完整 result、RTP/EV、Feature/Jackpot 或 Collector 重构。
- 方法：连续 outbound Spin 请求以 `client_coins(i)` 作为 Balance Before、`client_coins(i+1)` 作为 Balance After；稳定 Bet 下计算 `next - current + bet` 作为 Win Candidate。
- User 完成 3 次普通 Spin；probe 得到 3/3 合法样本、0 errors、2 个相邻 Balance 转移。Bet 稳定，两个 Balance 转移均变化，两个 Win Candidate 均为非负整数，其中一个非零。
- **成功标准 A 达成**：前两次 Spin 均形成 `Spin → Balance Before → Balance After`。第三次 Spin 的 After 需要下一次请求，属于该方法的 `N` 请求 / `N-1` 闭合转移边界。
- 成功标准 B 仅记为 **Derived candidate**；没有直接观察到服务端 `win` 字段。
- Collector 能力保持 **F3**，不因本 Spike 升级。

## Current blocker

Session 尾部 Spin 的即时 Balance After / Win 不能由当前 outbound-only 方法闭合；若要求该能力，需要进入 inbound result 或新的状态源，超出 Phase 1.5 范围。

## Next recommendation

停止 Balance Spike 并等待 ChatGPT Review。后续 Demo 若单独获批，可用相邻 outbound request 输出脱敏 Balance 波动与 Spin Timeline，同时标注尾部未闭合及 Win 为 Derived；当前不要开始 Demo 报告。

## Finalize and boundaries

- 逐笔 Balance/Win、Raw、APK、SO、完整响应与账号数据仅保存在 `D:\CashFrenzyResearch\local-only`，未进入 Git 或云文档。
- Cash app 已 force-stop；临时 Cash 专属 Gadget/config、ADB `tcp:27043` forward、Frida server 和 probe 进程均确认无残留。
- `D:\huuuge-research` 保持 clean；未修改 Huuuge Collector、Session、Raw、SVN、飞书、AI-Workspace governance、其他游戏或 Capability。
- Workspace Sync 保持 `ON_DEMAND`，WATCH disabled；Subagents none / OFF。

<!-- MEMORY-REFRESH:START -->
## Memory Context Refresh

- Generated: 2026-08-27T10:39:09Z
- Effective mode: `ASSISTED`
- Manifest: `CONTEXT_MANIFEST.yaml`
- ChatGPT Project Sources: `manual upload required`
- Private repositories: not read unless explicitly registered and authorized
<!-- MEMORY-REFRESH:END -->

## Exact Next Action

ChatGPT Review TASK-0022 Phase 1 与 Phase 1.5；在 Review 结论前不开始 Demo 报告或继续协议研究。
