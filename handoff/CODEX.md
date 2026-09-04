# Codex Handoff

- Updated: 2026-09-04
- Current task: TASK-0027 — Huuuge Laptop Demo Reliability Hardening
- Status: In Progress — Phase C static preflight complete；dynamic lifecycle blocked before start
- Branch: AI-Workspace `codex/huuuge-laptop-reliability-readiness-audit` from `main@1dd6de3e244858c44b716cacd72961ea9419f564`
- Workspace Sync: `ON_DEMAND` — provider unavailable; stale 6; conflicts 0
- WATCH: disabled
- Memory mode: `ASSISTED`
- Subagents: none

## Current Task — TASK-0027

- User 已批准 P0 Reliability Hardening，范围固定为“笔记本汇报实机演示”。allocator 通过 remote-CAS 正式分配 `TASK-0027`，reservation 保持 `pending-main`；没有手工选号，token 未写入 Git/Handoff。
- Phase A 只读 Audit 与 Phase B BlueStacks Environment-ready 已完成；验收见 `tasks/support/TASK-0027/ENVIRONMENT_READY_ACCEPTANCE.md`。
- BlueStacks：App Player `5.22.262.1001`、Services `3.0.9`、Now.gg 有效签名；program `C:\Program Files\BlueStacks_nxt\`、data `D:\BS\BlueStacks_nxt\Engine\`；当前 Hypervisor/VMP 保持不变并完成正常启动、退出、重启复现。
- 实例：本机安装生成的唯一 internal ID `Pie64` 已显示为 `HuuugeResearch`；Pie 64-bit、4 CPU / 4096 MB、config ABI `x86,x64,arm,arm64`；没有 clone 台式机实例/VHD/path/port/Root 配置。
- ADB：默认 5555 被本机 Windows excluded range `5485–5584` 覆盖；User 另行批准 5585。复启后唯一 `127.0.0.1:5585` listener 归属 `HuuugeResearch`，5037 无争用，remote ADB OFF，Root OFF，direct ADB transport probe 通过。
- Huuuge：User 完成安装/登录与游戏启动；只读回读为 `com.huuuge.casino.slots` / versionName `12.08.27100` / versionCode `1786533240` / primary ABI `arm64-v8a`。Codex 未安装、登录、点击游戏或执行 Spin。
- 已知 Reliability 风险：BlueStacks 随附 `HD-Adb.exe` 在 excluded default emulator ports 上长时间扫描、未及时开放 5037；两次 run-owned 尝试均按精确 PID 清理，最终 `HD-Adb=0`、5037=0。Phase C 必须固定 deterministic ADB implementation/timeout/cleanup，不得把该失败静默记为通过。
- 共存：MuMu 保持原运行状态，Nox 保持原状；二者未占用 5585/5037，未停止或修改。D: 仍有约 201.5 GB 可用，当前 data path 适合汇报环境，不触发重装 Gate。
- 最终状态：BlueStacks Player、Multi-instance Manager、ADB client 均退出；port 5037/5585 均无 listener。没有 Root、Frida、Collector 或 Spin；没有修改业务仓库、飞书文档或 Codex 配置。Subagents: none / OFF。
- 回退：config Baseline 5/5、Modified 7/7；另一份 copy 上 rollback 恢复 Baseline 5/5。live config 保持 User 批准的 `HuuugeResearch / ADB enabled / 5585 / Root OFF`。
- Phase C 正式包：公司 SVN working copy `C:\HuuugeCollector@r6701` clean；version `1.0.1`；source revision `77e0339fa73da2ab02fcbb6cff125604a9a8abd5`；ZIP SHA-256 `ACAC144B3CB58E861345D33F6CEEB95ACA0E1CE3CF8B49211C6E7AFB260A958A`；manifest `3/3`、PowerShell `9/9`、Python AST `5/5` 通过。
- Phase C blocker：正式 controller 固定 `Pie64_1 / 127.0.0.1:5565 / uid=0(root)`，本机批准边界为 `Pie64 / 127.0.0.1:5585 / Root OFF`；固定 ADB/Frida 路径也缺失。按 scope 在启动前停止，未运行 READY/短 Session/Stop/Finalize；Demo Ready=`No`。
- Validation：Task 23/23、Context 13/13、Memory 44/44、Phase C focused 20/20；Registry 14 canonical / 0 collision / valid；Context refresh 74 sources / 0 broken link / 0 secret issue；changed-document allowlist 12/12；Workspace Doctor、PowerShell Context entry 与 `git diff --check` 通过。
- 回归失败记录：第一次组合运行在默认 Windows TEMP 遇到测试子进程退出后的临时目录 handle race，Context 5 项、Memory 4 项仅在 tearDown 报 WinError 32；改用隔离 ASCII TEMP 并固定 UTF-8 后，Context 13/13 与 Memory 44/44 全量通过，没有修改测试或产品代码。
- 唯一下一步：User 决定是否另行授权 Collector 工程适配，使正式入口支持本机 `Pie64 / 5585 / Root OFF`。未获授权不启动 BlueStacks、Root、Frida、Collector 或 Spin。

## Current Task — TASK-0019

- 新分支从最新 `main@c74c85a9524d1524ea3696835509de2a55e9f524` 建立；未 merge `origin/task-0019-overview-progress`，只用 `git show` 提取旧分支两份源稿作为选择性复用输入。
- `docs/overview/AI_WORKSPACE_PROJECT_OVERVIEW.md` 保持稳定定位、架构、能力链路与安全边界；`docs/status/AI_WORKSPACE_PROJECT_PROGRESS.md` 成为动态能力、Task、阻塞、风险、入口和更新规则的独立源稿。
- 业务真相源已现场核验：Huuuge `main@4a5dddf7782307c6a8f368c9f1dc6390eec6f65b`、CF_collect `main@4df10ec20e79bb737912c8d1b847fae3659031ae`、Document Assistant `main@b0292c3159db16542906948511b6b1ec58c360fd` 均与远端一致且工作树干净。
- TASK-0026 已按 Review Round 3 `Accepted` 纳入；Collector 1.0 的 cleanup、固定六字段与验证边界不变，本 Task 未修改任何业务实现。
- 当前 Windows 工作站 Host readiness 为 `Ready`：Global + Project AGENTS 已加载，Global hash 与批准值一致，Git 可用，Subagents `OFF`，Document Assistant 可发现且 healthcheck token/API/Drive 全部 `ok`。
- Huuuge First Run 保持 `Blocked`：正式 RC4 记录仍为 `Pending`，User 实跑仍为 `Failed/Invalid`。正式 Collector READY 未被可复核证明；只确认临时 SSL 捕获后进入 User 操作阶段，游戏由 User 亲自操作，不能据此认定 Collector 达到 READY。
- Bet/RTP `Unsupported`：没有 Bet 分层受控运行证据或稳定 RTP/EV 统计，不从字段、单次样本、bundle ratio 或描述性比率推导 Bet 与 RTP 关系。
- Workspace Sync 与 feishu-docs 分别验收：Sync 为 `ON_DEMAND / provider unavailable / stale 6 / conflicts 0`；Document Assistant 为 `Available`，两者不得合并成一个 Provider 状态。
- Round 3 只对既有飞书进度文档执行 `replace_document`；没有创建副本，项目全景飞书文档保持未写。回读确认 document ID/链接不变，并包含 TASK-0019 `Accepted`、Collector READY 未证明、临时 SSL 捕获/User 亲自操作边界和 Bet/RTP `Unsupported`。
- 进度文档权限保持 `tenant_editable` / verified；重新登记后 Hub readback 保持 17 个登记项、`unique_links=true`，进度标题出现一次。
- Validation：Round 3 定向断言 12/12、Task 23/23、Context 13/13、Memory 44/44、Registry 13 canonical / 0 collision / valid、Context refresh 70 sources / 0 broken link / 0 secret issue、changed-document scan 11 files / 0 broken link / 0 secret assignment / 0 stale READY / 0 new Task、项目全景 SHA-256 `BBC2393DCE276678D13363D65099FA3185D23BEB3AA6127CCBBA45387D350E61` 不变与 `git diff --check` 通过。
- 本轮未启动模拟器、Root、Frida、Collector，未执行 Spin；Workspace Sync 保持 ON_DEMAND，WATCH disabled；Subagents: none / OFF。
- ChatGPT Review Round 3 正式记录为 `reviews/TASK-0019-CHATGPT-REVIEW-3.md`：Decision `Accepted`，reviewed commit `ccc1610a69808f7516e4d215d2177454021d108a`；canonical TASK-0019 已更新为 `Accepted`。
- TASK-0019 收口时 P0 Reliability Hardening 仍只是 Decision proposal；该历史 Gate 已由 2026-09-04 User 批准和 TASK-0027 supersede。
- TASK-0019 已结束；其后续执行入口统一为 TASK-0027，不在已接受 Task 内追加实现。

## Current Task — TASK-0026

- User 已明确把当前目标切换为 Collector 1.0 工程化；Approved Candidate 经 allocator 以 `relationship=new` 晋升为唯一 TASK-0026，canonical 已合入 AI-Workspace main 并 finalize，不续写 TASK-0024。
- 正式 GitHub 仓库已按 User 指令从 `CashFrenzy_collect` 改名为 `CF_collect`；面向用户的介绍使用“【游戏】”，运行所需 package、command 与代码技术标识保持不变。
- 固定交付为 `adapters/batch_spin`、`adapters/keepalive`、`adapters/registry`、统一 `event + adapter + source + payload` Event contract，以及 `session_manifest.json / source_events.jsonl / events.jsonl / spin_records.jsonl / summary.*` Session layout。
- `batch_spin` 只允许 TASK-0024 已确认的 `base_win / bonus_base_win / total_win / coins / win_lines / win_pos_list` 六字段；额外键必须被忽略，不允许字段发现或 schema 扩展。
- 只选择性采用 DS Sidecar 的 exact-target gate、fail-closed/type/truncation handling 与合成测试思想；禁止迁移 `.local/`、真实 Session、fixture/artifact、Git 历史、schema expansion、`same_object_fields` 或实验文件。
- ChatGPT Review Round 1 正式记录为 `reviews/TASK-0026-CHATGPT-REVIEW-1.md`：`Needs changes`；READY 与 Root 已通过，只修 cleanup 未停止本轮 `cf_rt_mon -D` 后台进程。
- cleanup-only 修订已推送为 `CF_collect@4e6f0625e2e39dfeb6ebb4dfb2fd6a29d5c1999c`：helper 返回 `pid / remote_path / started_by_run`；严格 PID+path ownership；LIFO/idempotent stop+verify；运行、停止、验证和残留错误聚合。
- ChatGPT Review Round 2 正式记录为 `reviews/TASK-0026-CHATGPT-REVIEW-2.md`：`Needs changes`；Round 1 cleanup 主体通过，只修 run/helper 列表函数 `return ,$array` 与调用方 `@()` 形成嵌套数组。
- Round 2 修订已推送为 `CF_collect@4df10ec20e79bb737912c8d1b847fae3659031ae`：列表返回统一去掉一元逗号，调用方继续用 `@()` 接收扁平 0/1/N 项；空 PID 不触发 ownership residual，空 residual 不产生空 verify error。
- finally 后继续验证 Probe、server、forward、Gadget/config 与 `/data/local/tmp/cf_*` 无残留。focused 16/16、cleanup injection 7/7、实际生产函数 shape 10/10、compileall、PowerShell parser 5/5、六字段与 privacy Gate 通过。
- ChatGPT Review Round 3 正式记录为 `reviews/TASK-0026-CHATGPT-REVIEW-3.md`：`Accepted`；reviewed commit `4df10ec20e79bb737912c8d1b847fae3659031ae`。
- `CF_collect` 实现分支已 fast-forward 合入并推送 `main@4df10ec20e79bb737912c8d1b847fae3659031ae`；AI-Workspace 治理分支完成 Accepted 收口后合入 main。
- `cf_probe.py`、`adapters/batch_spin.py`、`docs/ROOT_TOGGLE.md` hash 不变；Android 9 Hook/serializer、READY、Root 和六字段边界未改。本轮没有启动模拟器、Root、Frida、Collector 或新 Session，没有 Spin。Workspace Sync `ON_DEMAND`，WATCH disabled；Subagents: none。
- 已解决的失败：Candidate 日期/slug 两次 fail-closed 且未误占 ID；新 clone 首次 commit 因缺作者身份失败后仅写 repo-local noreply identity；Task 23/23 后套件尾部一次真实 validate fetch 瞬时失败，独立 fetch/validate 随即通过 13 canonical / 0 collision / 0/0。

## Governance Task — TASK-0016 Review Round 3

- ChatGPT Review Round 3 已 Accepted；正式记录 `reviews/TASK-0016-CHATGPT-REVIEW-3.md`，reviewed commit `d3dd72592fc8c176f317ffe6d0ac1362eed5930e`。TASK-0016 与 Memory Capability/Governance 已转为 Accepted / Active。
- Review Round 2 两个安全问题已修复：全部 provenance placeholders（含 ASCII `-` / 纯标点）在 CLI、Event file、Generic Agent 路径 fail closed 到 Outbox；`secret/local-only` 在 Registry 前 hard deny，恶意 allowlist 不能写 public/private Inbox，Secret literal 不留 Outbox。
- 唯一跨会话 Git Memory 读入口为 `memory/context/WORKSPACE.md`。现有 Candidate/Validator/Curator 在 ASSISTED 下通过显式批准晋升 3 个 public-safe Seed，得到 3 unique key / 3 unique source / 0 duplicate；Candidate 已归档。
- 新会话固定 Git-live-first：Core/System/Writing Style → 最新 Git Workspace Memory → 相关 Task/Review/Status/Handoff/业务证据 → Git unavailable 时 stale-marked Source Pack。测试确认 F3 strengthened / F4 未证明，且不重复 TASK-0024 已停止路线。
- Context refresh 已纳入 Workspace Memory，并输出 path/hash/read Git HEAD；不读私有仓库，Project Sources 仍为 manual upload required snapshot。
- 最终 production mode `ASSISTED`；AUTO 未启用、Hook 未安装/启用、Workspace Sync `ON_DEMAND`、WATCH disabled、无新增外部服务。Subagents: none。
- 回归：Memory 44/44、Task 23/23、Context 13/13；Registry 已由正式 CLI 重建为 12 canonical / 0 collision / status valid；Workspace Doctor 通过；Context refresh 68 sources / 0 secret issue / 0 broken link。
- 合并前审计与收口回归全部通过：默认 ASSISTED、Registry hard deny、canonical gate、Git-live-first priority 与调试开关均符合要求。本收口提交合入并 push main 后 TASK-0016 结束，无后续执行项。

## Deferred Ready Task — TASK-0025

- User 曾明确批准启动 Top Tycoon F4 可行性审计；canonical TASK-0025 保持 `Ready`，但尚未执行。2026-08-28 的后续 User 决定把当前优先级切换到 TASK-0026，因此本方向暂存 Backlog。
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

- Generated: 2026-09-04T05:01:05Z
- Effective mode: `ASSISTED`
- Manifest: `CONTEXT_MANIFEST.yaml`
- ChatGPT Project Sources: `manual upload required`
- Private repositories: not read unless explicitly registered and authorized
<!-- MEMORY-REFRESH:END -->
## Exact Next Action

TASK-0027 Phase C static preflight 已完成，动态 lifecycle 因正式 package contract 与本机 Root-OFF identity 冲突而在启动前阻断。User 决定是否另行授权 Collector 工程适配；未获授权不启动 BlueStacks、Root、Frida、Collector 或 Spin。
