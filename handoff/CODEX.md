# Codex Handoff

- Updated: 2026-08-27
- Task: TASK-0022 — Cash Frenzy Android Collector Feasibility Audit
- Status: In Progress — waiting for User installation gate
- Branch: `codex/task-0022-cash-frenzy-feasibility`
- Issuance main merge: `694e955b76405bd6fb97203110d6bc6f9a1185b2`
- Workspace Sync: `ON_DEMAND`
- WATCH: disabled
- Subagents: none
- Subagent mode: OFF

## Allocation

User-approved Candidate 通过正式 `task_cli.py promote` 获得唯一 ID `TASK-0022`。Candidate/Registry/Task issuance 已进入 main，allocator reservation 已 finalize；远端 reservation ref 无残留。

## Reuse-first Decision

只读基线为 `huuuge-android-research@4a5dddf7782307c6a8f368c9f1dc6390eec6f65b` / Collector 1.0.1。Huuuge repo 在审计前后均 clean，运行中的 Collector、Session、Raw、SVN 和业务文件均未修改。

- Adopt：Session lifecycle、manifest、markers、Raw immutability、inventory/catalog、privacy 与 evidence discipline。
- Wrap：独立 BlueStacks/ADB/package binding、APK/split inventory、planner preflight。
- Build：Cash Frenzy `BLSocket`/TLS plaintext probe、LuaJIT command/schema mapping、module taxonomy。
- Reject：Huuuge descriptor/decoder、Huuuge Session/Raw/database/Collector process。

## Static Results

- Official product：Cash Frenzy™ - Casino Slots / SpinX Games Limited。
- Package：`slots.pcg.casino.games.free.android`。
- Read-only sample：4.78 / versionCode 478，minSdk 24，targetSdk 35，APK signing v3。
- Splits：base、arm64-v8a、hdpi、zh；primary ABI arm64-v8a。
- Engine：Cocos2d-x + LuaJIT；entry `org.cocos2dx.lua.AppActivity`；main native `libcocos2dlua.so`。
- Resources：16,887 LuaJIT bytecode、2,888 PNG、528 atlas、516 JSON、491 plist、121 CSB；Systems 5,739 files、Themes 528。
- Protocol signals：`BLSocket`、command map、keepalive/reconnect/batch spin/enter theme/jackpot；native TLS read/write、LuaSocket、WebSocket、XXTEA、Protobuf、encryption/signing candidates。
- Blocker：23 个 proto/textproto 都属于 Google/Firebase/SDK 范围，未发现游戏业务 descriptor；没有 Runtime evidence。
- Level：overall F1 Static-only；dynamic path F0。Decision proposal=`Wrap + Build`。

APK、split、SO、完整 strings 和 local extraction 只留 Host-local `CashFrenzyResearch/local-only`，不进入 Git、飞书或聊天。现有 `HuuugeResearch` 只作为 package APK 的只读来源，未读取应用私有数据、账号、Session 或 Raw。

## Deliverables

- `reviews/cash-frenzy/FEASIBILITY.md`
- `reviews/cash-frenzy/REUSE_MATRIX.md`
- `reviews/cash-frenzy/STATIC_INVENTORY.md`
- `reviews/cash-frenzy/PROTOCOL_EVIDENCE.md`
- `reviews/cash-frenzy/DYNAMIC_PROOF.md`
- `reviews/cash-frenzy/NEXT_TASK_PROPOSAL.md`

## Current Gate

Windows Computer Use helper 无法捕获 BlueStacks Multi Instance Manager 的 Qt 窗口，返回“不支持此接口”；未使用盲点坐标、未改配置文件。需要 User 通过界面创建 fresh Pie 64-bit `CashFrenzyResearch` 并从 Google Play 安装游戏。登录、验证码和商店操作由 User 完成。

安装后 Codex 先只读检查 instance name、ADB serial、package/version/ABI、foreground package 与隔离目录；通过后才准备最小被动 Capture。Spin Gate 将另行请求 1–5 次普通 Spin，不自动付费或大量消耗资源。


<!-- MEMORY-REFRESH:START -->
## Memory Context Refresh

- Generated: 2026-08-27T09:42:02Z
- Effective mode: `ASSISTED`
- Manifest: `CONTEXT_MANIFEST.yaml`
- ChatGPT Project Sources: `manual upload required`
- Private repositories: not read unless explicitly registered and authorized
<!-- MEMORY-REFRESH:END -->
## Exact Next Action

User 在 BlueStacks Multi Instance Manager 创建 fresh Pie 64-bit 实例 `CashFrenzyResearch`，启动后从 Google Play 安装由 SpinX Games Limited 发布的 Cash Frenzy™ - Casino Slots；安装完成但不要开始 Spin，然后回复“安装完成”。
