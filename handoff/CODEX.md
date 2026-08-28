# Codex Handoff

- Updated: 2026-08-28
- Current task: TASK-0025 — Top Tycoon Android F4 Collection Feasibility Audit
- Status: Ready — canonical issuance pending merge/finalize
- Branch: `chatgpt/top-tycoon-f4-feasibility`
- Workspace Sync: `ON_DEMAND`
- WATCH: disabled
- Memory mode: `ASSISTED`
- Subagents: none

## Current Task — TASK-0025

- User 已明确批准启动 Top Tycoon F4 可行性审计；Approved Candidate 已从最新 main 的独立 linked worktree 先重建 Registry，再由官方 allocator 以 `relationship=new` 晋升为唯一 canonical TASK-0025。
- reservation 当前保持 `pending-main`，token 不写入 Git/Handoff；canonical Task 合入 main 后必须从原 linked worktree同步最新 main 并 `finalize`，完成前不得执行动态或静态研究。
- 固定研究环境为 User 新建、显示名 `topTycoon` 的模拟器；执行前现场复核 internal instance ID、ADB serial、package/version/versionCode/split/ABI/native bridge 与前台包，不匹配即 fail closed。
- 动态样本 Gate：Codex 先完成零游戏操作稳定性与结构边界准备，再明确回复 `READY`；Spin、资源消耗、购买、充值及继续/停止决定全部由 User 操作。禁止 Auto Spin、自动点击、请求/响应修改与重放。
- 目标等级为 F4，但只有双独立 Session、同一核心 Spin schema、累计目标 20 个有效 User 手工样本、次级模块边界、确定性 lifecycle 与脱敏可 Review 证据全部通过时才可报告 F4；否则如实记录 F0–F3。
- Reuse-first 边界：Adopt Session/manifest/Raw/inventory/privacy/evidence/cleanup contract；Wrap Top Tycoon identity/runtime；仅 Build 必要 hook/schema/adapter；禁止复用 Huuuge/Cash Frenzy 业务 schema、Raw、账号或数据目录。
- Workspace Sync 为 ON_DEMAND / 0 conflict；provider unavailable，6 个 initial-publication stale；Git canonical 内容来自最新 main。WATCH disabled；Subagents: none。

## Closed Task — TASK-0024

- ChatGPT Review Round 1 已 Accepted；正式 Review 为 `reviews/TASK-0024-CHATGPT-REVIEW-1.md`，reviewed commit `1f666e79995537febce7a0bf2b98e7ba96100ea9`，Review main commit `17f776553c9d6450c25d145404c46ebaa59a3c3c`。
- Review 分支已合入 main，canonical TASK-0024 状态为 `Complete`；不在本 Task 内继续完整 Collector、20-Spin、adapter 或其他模块研究。
- 收口时 Registry writer 在 main 与普通 checkout 均按设计 fail closed；改用独立 linked worktree 后成功重建为 11 canonical / 0 collision，没有绕过 gate。
- 收口回归：focused 3/3、Task 23/23、Context 13/13、Memory 35/35、Task/Context PowerShell entry、JavaScript syntax 与 Workspace Doctor 全部通过；Workspace Sync ON_DEMAND / 0 conflict / provider unavailable / 6 stale。
- User 明确要求新建独立 Spike，不继续扩大已完成的 TASK-0022；Candidate 已由正式 CLI 创建并经 allocator 分配唯一 `TASK-0024`，relationship 为 `new`。
- 执行 contract：稳定性 Gate → `onUIThreadReceiveMessage` scope 内 `LuaStack/lua_pcall` 参数 → `BLMessage` 解码后对象 → decrypt/framing fallback → Local State Adapter。
- 优先实现深度 4、每集合 64 元素、单消息 64 KiB 的受限递归 Lua serializer；只在 Cash inbound dispatch thread/scope 激活，禁止全局高频 Lua API 日志。
- 只有 Lua 与 BLMessage 路线都失败才进入 `libEncryptorP` / `libsigner` / XXTEA 与单消息 Stalker summary。
- 新 `AppResearch2` 与历史同名实例不是同一环境；执行前重新确认 Android 9、internal instance ID、ADB serial、package/version/ABI/native bridge 和前台包。
- 真实 Spin 必须由 User 手动执行 3–5 次；在 User 操作前先完成 0 Spin 的 clean Gadget 稳定性 Gate。
- Huuuge repo、正常 BlueStacks、其他游戏、SVN、飞书正文与 WATCH 未修改；Cash 研究实例只做了可回滚的临时 runtime 变更。
- Android 9 identity 已重新确认；本机完成可回滚 `Pie64_3` Root、Frida 17.17.0 staging 与 120 秒 clean Gadget Gate，0 crash signature。
- 60 秒无操作 scoped Lua baseline 为 21 inbound scopes / 21 pcalls / 1 thread / 0 errors / 0 truncation；`tick=15`、`keepalive=6`，路径命中 `coins`、`chips`、`avg_bet.bc`。
- User 手动完成 5 次普通 Spin；`batch_spin=5`，direct result boundary `arg[2].[2].list.[1]` 的 `base_win`、`bonus_base_win`、`total_win`、`coins`、`win_lines`、`win_pos_list` 均为 5/5。
- Pilot 复现率 5/5；本轮只授权 3–5 Spin，20-Spin 样本不足，不外推。Lua 路线成功后没有进入 BLMessage/decrypt/XXTEA/Stalker/Local State。
- F3 strengthened；F4 因只有一个含 Spin Session、未满足双 Session/20-Spin Gate 而未证明。临时 probe/Gadget/server/forward 已清理，`Pie64_3` root/guest-`su` 已恢复且 VHDX clean。
- 脱敏聚合与 local summary 回查一致；focused 3/3、Task 23/23、Context 13/13、Memory 35/35、Task/Context PowerShell entry、Workspace Doctor、Registry 11 canonical / 0 collision 与 email/credential scan 全部通过。
- Workspace Sync 保持 ON_DEMAND / 0 conflict；provider unavailable，6 stale；WATCH disabled。Subagents: none。

## Closed Governance Task — TASK-0023

- ChatGPT Review Round 2：Accepted；正式记录为 `reviews/TASK-0023-CHATGPT-REVIEW-2.md`，reviewed commit 为 `bc0d3ad1e519fb908dce53a78a35f9c3687a5b51`。
- Idea Governance 与 Planner Writing Style 已转为 `Accepted / Active`，统一 Product Roadmap 与术语规则正式生效。
- 收口前回归：Context / Source Pack 62 sources、0 broken link、0 secret issue；Task 23/23、Context 13/13、Memory 35/35、两个 PowerShell 入口、Registry 10 canonical / 0 collision 与 Doctor 全部通过。
- Workspace Sync 保持 `ON_DEMAND`、0 conflict；provider unavailable，6 个发布项保持 stale，没有启用 WATCH。

- 独立 worktree / branch：`codex/idea-governance-product-roadmap`；不修改 TASK-0022 的 canonical 文件、reservation、执行分支或环境。
- Candidate 由正式 CLI 创建并经 allocator 晋升为唯一 canonical TASK-0023；Registry 仅由工具重建，reservation 保持 `pending-main`，token 未写入 Git/Handoff。
- 已建立 `docs/roadmaps/PRODUCT_ROADMAP.md`、Idea Governance standard/workflow，并更新 Core Rules、Project Instructions、AGENTS、ChatGPT Bootstrap、AI Team、Architecture 和入口索引。
- 唯一正式飞书 Product Roadmap 已完成创建、正文回读、企业内可编辑、自动登记与 Hub 回读；项目全景说明原位加入 Roadmap 链接且原生流程图仍存在。
- 临时测试 Idea 成功进入 Ideas，回读后已删除，正式 Roadmap 恢复；四个固定分区各出现一次，Hub 当前 15 条正式链接且无重复。
- 失败记录：Candidate 的非规范 User decision 文本被 allocator 拒绝且未占号；临时发布脚本首次在编译阶段因 top-level await 失败且未产生云写入，修正后通过。
- 当前桌面会话仍挂载缺少 `register_document` 的旧 MCP 进程；其 `get_document` 回读按旧 schema 写回后暂时移除了项目全景说明的治理 metadata。没有新建文档；改用 Document Assistant 当前 `main` 新进程重新登记，Hub 已恢复为 15 条、链接唯一。后续不要再用该旧进程做治理回读；新会话加载正式 main 后再使用。
- Workspace Sync：`ON_DEMAND`；WATCH disabled；Memory：`ASSISTED`；Subagents: none。
- deterministic regression：Registry 10 canonical / 0 collision；Task 23/23、Context 13/13、Memory 35/35、两个 PowerShell 入口和 Workspace Doctor 通过；Context refresh 62 sources、0 broken link、0 secret issue。
- 收口动作：完成 deterministic regression，合并并 push main；随后在原 allocator worktree finalize TASK-0023 reservation，复验 0 collision 并清理任务 branch/worktree。

### Review Round 1 Required Fix

- Review 记录：`reviews/TASK-0023-CHATGPT-REVIEW-1.md`；Roadmap / Idea Governance 主体已通过，唯一修改项为技术术语规则。
- `standards/PLANNER_WRITING_STYLE.md` 现为唯一 canonical 规范；Core Rules、Repository/Bootstrap/Global AGENTS、Project Instructions、ChatGPT Bootstrap 与 Generic Agent 入口均引用同一规则。
- Context refresh 生成器现将 canonical 规范正文加入 ChatGPT 单文件 Source Pack 与 6 个拆分来源清单；Memory 回归测试包含对应断言。
- 默认面向策划使用准确、克制、可理解的研究表达；复现、工程判断、授权、合规、安全或风险需要时必须保留真实低层术语。禁止用模糊改名规避安全、权限、授权或 Review，也不得淡化风险。
- 本轮仅做 Review 修订和 deterministic refresh/regression，不修改 TASK-0022、Cash Frenzy、Huuuge、Document Assistant 或 Workspace Sync 模式；Subagents: none。
- Context / Source Pack：62 sources、0 broken link、0 secret issue；Task 23/23、Context 13/13、Memory 35/35、两个 PowerShell 入口、Registry 10 canonical / 0 collision 和 Doctor 全部通过。
- Workspace Sync 仍为 `ON_DEMAND`、0 conflict；provider unavailable，6 个发布项维持 stale，没有启用 WATCH。
- Review Round 2 已 Accepted；执行上述 main / finalize / cleanup 收口，不再等待 Review。

## Closed TASK-0021
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

- Generated: 2026-08-27T13:39:12Z
- Effective mode: `ASSISTED`
- Manifest: `CONTEXT_MANIFEST.yaml`
- ChatGPT Project Sources: `manual upload required`
- Private repositories: not read unless explicitly registered and authorized
<!-- MEMORY-REFRESH:END -->

## Exact Next Action

将 canonical TASK-0025 issuance commit push 到 `chatgpt/top-tycoon-f4-feasibility`，合入并 push 最新 `main`；随后在原 linked worktree同步 main、finalize reservation，确认 Registry 无冲突后才开始 Task Phase A。
