# Changelog

本文件记录 AI-Workspace 治理结构、标准、工作流和协作行为的变化。

## [0.18.6] - 2026-09-04

### TASK-0027 Accepted and presentation rehearsal passed

- User 明确接受 Phase D，并批准进入汇报彩排；Huuuge Research Laptop 保持 `Pie64_1 / 5565 / Root ON`，原 `Pie64 / 5585 / Root OFF` 保留。
- 彩排 Session `20260904_142442` 在 READY 时为 RPC/decoded `63/63`，User 按最小脚本完成操作后为 `123/123`；Stop/Finalize exit `0`。
- 最终 active state absent，Frida/game PID 为空，ADB forward、host capture process 与临时 residual 均为 `0`；长期 Gadget/config 保留。
- User 明确给出 `彩排 Accepted`；canonical TASK-0027 更新为 `Accepted`，Product Roadmap 移入 Done。正式汇报仍需单独开启 Session Gate。
- 本轮不修改 Collector、Hook/serializer、六字段、Huuuge 业务仓库、飞书或 Codex 配置；不执行 Win/Reward、Bet/RTP 分析。RC4 继续保留独立策划 First Run 边界。
- Accepted closeout 回归：Task 23/23、Context 13/13、Memory 44/44；Registry 14 canonical / 0 collision / valid；Context refresh 75 sources / 0 broken link / 0 secret issue；changed-document scan 12 files / 0 broken link / 0 secret assignment；Workspace Doctor 与 `git diff --check` 通过。

## [0.18.5] - 2026-09-04

### Huuuge Research Laptop Ready

- User 批准 Scheme C 与 TASK-0027 Phase D 工程部署。原 `Pie64 / 5585 / Root OFF` 保留；当前本机 Huuuge 实例被克隆为长期研究环境 `Pie64_1 / HuuugeResearch / 5565 / Root ON`，没有复制台式机 VHD、port、Root 或黑盒配置。
- Windows 动态 excluded range 覆盖 5565 后，按 User 单独批准建立单端口 administered exclusion；最终 `127.0.0.1:5565` listener count 1。MuMu/Nox 未停止或修改。
- Google platform-tools `37.0.1`、Frida host/server/Gadget `17.17.0` 与正式 SVN Collector `1.0.1@r6701` 已对齐；正式 bootstrap 无 action item。Collector 业务逻辑、Hook/serializer 与六字段未改。
- 正式 `-ValidationOnly` Session `20260904_135724` 完成 Start、strict READY、15 秒无操作 Session、clean Stop 与 Finalize：RPC/decoded `61/61`、manifest `stopped`、controller `finalized`。未执行 Spin、Win/Reward 或 RTP/Bet 分析。
- Final cleanup 后 host capture process 与 guest temporary residual 均为 0；本轮 root Frida server、Huuuge process 与 ADB forward 已停止，长期 Gadget/config 保留。Root/Gadget rollback 已在独立 copy 验证，live 环境保持长期研究状态。
- 新增 `tasks/support/TASK-0027/PHASE_D_LAPTOP_SETUP.md`；TASK-0027 进入 `Review`，`Huuuge Research Laptop Ready = Yes`。正式 RC4 继续 `Pending`，历史 User 实跑继续 `Failed/Invalid`，Bet/RTP 继续 `Unsupported`。
- Workspace Sync 保持 `ON_DEMAND / provider unavailable / stale 6 / conflicts 0`；WATCH disabled；Subagents: none / OFF。业务仓库、飞书与 Codex 配置未修改。
- 验证通过：Task 23/23、Context 13/13、Memory 44/44、Registry 14 canonical / 0 collision / valid、Context refresh 75 sources / 0 broken link / 0 secret issue、changed-document scan 13 files / 0 broken link / 0 secret assignment、Workspace Doctor 与 `git diff --check`。Context 首轮仅在 Windows TEMP teardown 出现 handle race，改用独立 D: ASCII TEMP 后 13/13 通过。

## [0.18.4] - 2026-09-04

### Phase C preflight

- User 批准 TASK-0027 Phase C。公司 SVN 1.0.1 正式包已 checkout 到 `C:\HuuugeCollector@r6701`；installer/tree last-changed revision 为 `6624`，manifest source revision 为 `77e0339fa73da2ab02fcbb6cff125604a9a8abd5`，ZIP SHA-256 为 `ACAC144B3CB58E861345D33F6CEEB95ACA0E1CE3CF8B49211C6E7AFB260A958A`。
- 单文件 export 与 working-copy release ZIP hash 一致；manifest allowlist `3/3`、PowerShell parser `9/9`、Python AST `5/5`，SVN status clean。
- 启动前 static preflight 确认正式 controller 固定 `Pie64_1 / 127.0.0.1:5565 / uid=0(root)`，而本机批准边界为 `Pie64 / 127.0.0.1:5585 / Root OFF`；固定 `C:\platform-tools\adb.exe` 与 Frida server 依赖也缺失。

### Stop gate

- 继续动态验收需要修改 Collector 实现或改变 Root/实例边界，超出当前授权。按 User 指令在启动前停止；未运行 BlueStacks、Frida、Collector、READY、短 Session、Stop、Finalize 或 Spin，未执行 Win/RTP/Bet 分析，未新增字段。
- 新增 `tasks/support/TASK-0027/PHASE_C_PREFLIGHT_ACCEPTANCE.md`；Demo Ready=`No`。唯一下一步是 User 决定是否另行授权 Collector 工程适配。
- 验证通过：Phase C focused 20/20、changed-document allowlist 12/12、Task 23/23、Context 13/13、Memory 44/44、Registry 14 canonical / 0 collision / valid、Context refresh 74 sources / 0 broken link / 0 secret issue、Workspace Doctor、PowerShell Context entry 与 `git diff --check`。PowerShell wrapper 首次默认 TEMP teardown 遇到 WinError 32，设置 ASCII `TEMP/TMP/TMPDIR` 后全量通过。

## [0.18.3] - 2026-09-04

### Environment-ready

- User 批准保留现有 BlueStacks，并在确认默认 5555 端口冲突后单独批准改为 5585。BlueStacks 5 `5.22.262.1001` / Services `3.0.9` 在当前 Hypervisor/VMP 下完成启动、正常退出和重启复现。
- 本机安装生成的唯一 fresh Pie 64-bit internal ID `Pie64` 已显示为 `HuuugeResearch`；program `C:\Program Files\BlueStacks_nxt\`、data `D:\BS\BlueStacks_nxt\Engine\`、4 CPU / 4096 MB、ADB `127.0.0.1:5585`、remote ADB OFF、Root OFF 均已回读。
- User 完成 Huuuge 安装/登录与游戏启动；只读 ADB 证据确认 package `com.huuuge.casino.slots`、versionName `12.08.27100`、versionCode `1786533240`、primary ABI `arm64-v8a`。Codex 未执行安装、登录、游戏点击或 Spin。
- 新增 `tasks/support/TASK-0027/ENVIRONMENT_READY_ACCEPTANCE.md`；TASK、Project Status、Product Roadmap、Current State、Workspace Progress 与两个 Handoff 已切到 Phase C User Gate。

### Reliability finding

- Windows TCP excluded range `5485–5584` 覆盖 BlueStacks 默认 5555；Player 日志记录 5555 port-forward failure。User 批准 5585 后，唯一 Player listener 与 direct ADB transport probe 通过，5037 无争用。
- BlueStacks bundled `HD-Adb.exe` 在 excluded default emulator ports 上长时间扫描；两次 run-owned 尝试均按精确 PID 清理，最终 HD-Adb/5037 无残留。该行为保留为 Phase C Reliability Hardening 输入，不静默记为 CLI 成功。
- MuMu 保持原运行状态，Nox 保持原状；没有停止或修改。验收结束后 BlueStacks Player、Multi-instance Manager、ADB client 和 5037/5585 均停止。

### Validation

- BlueStacks config Baseline 5/5、Modified 7/7；另一份 copy 上 rollback 恢复 Baseline 5/5，live config 保持批准的 5585。
- Task 23/23、Context 13/13、Memory 44/44、TASK-0027 定向 18/18；Registry 14 canonical / 0 collision / valid；Context refresh 73 sources / 0 broken link / 0 secret issue；changed-document scan 13 files / 0 unexpected / 0 broken link / 0 secret assignment / 0 stale；Workspace Doctor 与 `git diff --check` 通过。
- 默认 Windows TEMP 的首次组合回归只在临时目录 tearDown 出现 handle race；切换到隔离 ASCII TEMP + UTF-8 后 Context/Memory 全量通过，未修改测试或产品代码。
- 未安装/卸载软件，未修改 Windows feature、MuMu/Nox、业务仓库、Collector、飞书文档或 Codex 配置；未启动 Root、Frida、Collector 或 Spin。Subagents: none / OFF。

### Gate

- 唯一下一步是 User 审批 Phase C 的正式 Collector 包路径/取得方式、version/hash/依赖/static preflight 与最小 Reliability Hardening；Environment-ready 不等于 Collector READY、正式 RC4 通过或现场演示成功。

## [0.18.2] - 2026-09-04

### Added

- User 批准 P0 Reliability Hardening 后，使用 remote-CAS allocator 正式建立 canonical `TASK-0027 — Huuuge Laptop Demo Reliability Hardening`，没有手工选号；reservation 保持 `pending-main`。
- 新增 `tasks/support/TASK-0027/LAPTOP_READINESS_AUDIT.md`，按“笔记本汇报实机演示”的最小范围记录已具备项、缺失项、推荐动作、成功标准和回退方案。

### Confirmed

- 本机 Windows hypervisor/VMP、31.7 GB RAM、Git、Python、SVN CLI/TortoiseSVN、`D:\AI-Workspace` 和 Document Assistant 可用。
- 审计期间先发现下载目录与 Temp 中 2 个 Installer 进程；最终回查时进程已退出，BlueStacks 5 `5.22.262.1001`、BlueStacks Services `3.0.9`、产品目录与 `HD-Adb.exe` 已出现；下载器和关键 EXE Authenticode 为 `Valid / Now.gg, INC`。Codex 未发起或操作安装，也未启动 BlueStacks。
- BlueStacks data/config、专用 `HuuugeResearch`、可验证 ADB 目标、Huuuge 实装 identity 与正式 Collector 本机包仍缺失；MuMu 已安装并运行，NoxPlayer 已安装，当前无 ADB/5037 listener。
- 当前 Workspace 路径是 `D:\AI-Workspace`；没有把旧电脑 `C:\AI-Workspace`、`Pie64_1`、ADB port、VHD、Root 或 `.local` 当作本机事实。

### Gate

- TASK-0027 停在 Environment Change Approval Gate。User 需先决定保留并核验当前 BlueStacks 安装，或批准卸载 BlueStacks/BlueStacks Services；路径、其他模拟器共存处理、管理员/重启、新实例、ADB、游戏/SVN 登录和正式包目录均等待 User 审批。
- 未安装或启停任何软件/模拟器/服务，未创建实例，未 Root，未启动 Frida/Collector，未执行 Spin；未修改业务仓库或飞书文档。Subagents: none / OFF。

### Validation

- Task 23/23、Context 13/13、Memory 44/44、TASK-0027 定向断言 12/12；Registry 14 canonical / 0 collision / valid。
- Context refresh 72 sources / 0 broken link / 0 secret issue；changed-document scan 13 files / 0 unexpected path / 0 broken link / 0 secret assignment；Workspace Doctor 与 `git diff --check` 通过。

## [0.18.1] - 2026-08-29

### Accepted

- TASK-0019 ChatGPT Review Round 3 `Accepted`；正式记录为 `reviews/TASK-0019-CHATGPT-REVIEW-3.md`，reviewed commit 为 `ccc1610a69808f7516e4d215d2177454021d108a`。
- canonical TASK-0019 状态由 `Review` 更新为 `Accepted`。

### Finalized

- First Run 最终口径保持：正式 RC4 `Pending`、User 实跑 `Failed/Invalid`、正式 Collector READY 未被可复核证明、临时 SSL 捕获后进入 User 操作阶段且游戏由 User 亲自操作、Bet/RTP `Unsupported`。
- P0 Reliability Hardening 只保留 Decision proposal；未经 User 批准不创建 Task、不进入实现或运行。
- 项目全景说明保持不变；只原位更新既有飞书进度文档，不创建副本。

### Context and Validation

- Context Manifest、Project Source Pack 和 replacement list 已刷新为 70 sources / 0 broken link / 0 secret issue；旧 READY 事实口径为 0。
- Round 3 定向断言 12/12、Task 23/23、Context 13/13、Memory 44/44、Registry 13 canonical / 0 collision / valid、changed-document scan 11 files / 0 broken link / 0 secret assignment / 0 stale READY / 0 new Task、项目全景 SHA-256 不变与 `git diff --check` 均通过。
- 既有飞书进度文档完成原位替换、正文与 `tenant_editable` 权限回读；Hub 保持 17 个登记项、`unique_links=true`，进度标题唯一。项目全景飞书文档未写入。
- 未启动模拟器、Root、Frida、Collector，未执行 Spin；Subagents: none / OFF。

## [0.18.0] - 2026-08-29

### Added

- 执行 TASK-0019，从 `main@c74c85a9524d1524ea3696835509de2a55e9f524` 新建 `codex/task-0019-overview-progress-refresh`，未 merge 旧任务分支；选择性复用旧文档结构并按当前真相源刷新两份独立 Git 源稿。
- 新增唯一动态状态源稿 `docs/status/AI_WORKSPACE_PROJECT_PROGRESS.md`；项目全景说明继续只维护稳定定位、架构、能力链路与边界。

### Changed

- 纳入 TASK-0026 Review Round 3 `Accepted`、`CF_collect/main@4df10ec`、新工作站 `Ready` 与 Document Assistant `Available`。
- TASK-0019 ChatGPT Review Round 1 为 `Needs changes`；正式记录 reviewed commit `9403a09a445fd37548c78b3fc21709e91f5406d9`，只修文档事实与验收缺口。
- `bootstrap/chatgpt/02_CURRENT_STATE.md` 将 Huuuge First Run 从“暂定通过”更正为 `Blocked`，并区分正式 RC4 `Pending` 与 User 实跑反馈 `Failed/Invalid`；只脱敏记录临时 SSL 捕获后进入 User 操作阶段、User 控制的执行边界和无证据 Bet/RTP 风险，正式 Collector READY 未被可复核证明。
- 进度文档第 7 节补充历史 TASK-0018 文件冲突与 ChatGPT 直写飞书地区限制；全景说明六个核心 Git 入口从旧 `070744...` 统一更新到 `c74c85a...` 核验基线。
- Workspace Sync 与 Document Assistant 分开验收：前者 `ON_DEMAND / provider unavailable / stale 6 / conflicts 0`；后者 healthcheck token/API/Drive 全部 `ok`。

### Published

- 两份既有飞书文档通过 Document Assistant 原位替换，conversion warning 0；正文、交叉链接、基线和关键状态回读通过。
- 两份文档均验证为企业内可编辑；导航中心自动登记与回读通过，17 个登记项、链接唯一，未创建重复文档。
- Round 1 修订后再次原位更新同一 document ID；回读确认指定正文与稳定链接，权限 `tenant_editable` / verified；Hub 为 17 个登记项、`unique_links=true`，两份标题各出现一次。

### Validation

- AI-Workspace、Huuuge、CF_collect 与 Document Assistant 的权威 `main` 已分别核验；业务仓库工作树均干净。
- 文档职责、八个进度板块、关键状态、secret scan、`git diff --check`、Task Registry、Context/Memory 回归与 rollback copy 通过。
- Round 1 定向断言 10/10；Task 23/23、Memory 44/44、Context 13/13、Registry 13 canonical / 0 collision / valid、Context refresh 70 sources / 0 broken link / 0 secret issue 与 Workspace Doctor 通过。
- 未启动模拟器、Root、Frida、Collector，未执行 Spin；Workspace Sync 保持 ON_DEMAND，WATCH disabled，Subagents: none / OFF。

### Review

- TASK-0019 保持 `Review`；Round 1 修订完成，等待 ChatGPT Review Round 2，不自行合并 `main`。

## [0.17.4] - 2026-08-29

### Accepted

- TASK-0026 ChatGPT Review Round 3 `Accepted`；正式记录为 `reviews/TASK-0026-CHATGPT-REVIEW-3.md`，reviewed implementation commit 为 `4df10ec20e79bb737912c8d1b847fae3659031ae`。
- TASK-0026 canonical 状态由 `Review` 更新为 `Accepted`。

### Merged

- `CF_collect` 分支 `codex/collector-1-engineering` 已 fast-forward 合入并推送 `main@4df10ec20e79bb737912c8d1b847fae3659031ae`。
- AI-Workspace 治理分支完成 Task、三轮 Review、Registry、CHANGELOG 与 Handoff 收口后合入 `main`。

### Validation

- 最终复验 focused 16/16、cleanup injection 7/7、production shape 10/10；Task Registry 为 13 canonical / 0 collision / valid。
- LIFO、精确 PID+path、READY、Root、Hook/serializer 与六字段不变；未启动模拟器、Root、Frida、Collector，未执行 Spin。Subagents: none。

### Closure

- TASK-0026 结束，不在本 Task 内继续字段恢复、20-Spin/F4 或其他模块研究。

## [0.17.3] - 2026-08-29

### Review

- 正式记录 `reviews/TASK-0026-CHATGPT-REVIEW-2.md`：Decision `Needs changes`；Round 1 cleanup 主体通过，唯一 required fix 为 run/helper 的 `return ,$array` 与调用方 `@()` 形成嵌套集合。

### Fixed

- `CF_collect@4df10ec` 统一移除 cleanup 列表函数 `return` 前的一元逗号，调用方继续用 `@()` 接收扁平 0/1/N 项；空 PID 不再触发 ownership residual，空 residual 不再生成空 verify error。

### Validation

- 实际生产函数 shape tests 10/10，覆盖 0/1/2 PID、ADB 行、路径、residual error 与两个空集合边界；focused 16/16、cleanup injection 7/7、PowerShell parser 5/5、compileall、六字段、privacy scan 与 diff check 通过。
- LIFO、精确 PID+path、READY、Root、Hook/serializer 与六字段不变；未启动模拟器、Frida、Collector，未执行 Spin。Subagents: none。

### Next

- TASK-0026 保持 `Review`，等待 ChatGPT Review Round 3；不自动合并 main。

## [0.17.2] - 2026-08-29

### Review

- 正式记录 `reviews/TASK-0026-CHATGPT-REVIEW-1.md`：Decision `Needs changes`；READY 与 Root 已通过，唯一 required fix 为 cleanup 只删除 `cf_rt_mon` 文件、未停止本轮 `cf_rt_mon -D` 后台进程。

### Fixed

- `CF_collect@4e6f062` 让 Frida helper 返回 `pid / remote_path / started_by_run`；cleanup 只停止本轮拥有且 PID、路径精确匹配的 server，不使用宽泛进程终止。
- cleanup engine 增加严格 LIFO、幂等 stop/verify、ownership gate 与错误聚合；finally 后验证 Probe/server/forward/Gadget/config/cf_* 无残留。

### Validation

- baseline 15/15；修订后 focused tests 16/16、可注入 cleanup tests 7/7、compileall、PowerShell 5.1 parser、六字段冻结、secret/local-data scan 与 diff check 通过。
- READY、Root、Hook/serializer 与六字段边界文件 hash 不变；未启动模拟器、Root、Frida、Collector，未执行 Spin。Subagents: none。

### Next

- TASK-0026 保持 `Review`，等待 ChatGPT Review Round 2；不自动合并 main。

## [0.17.1] - 2026-08-29

### Fixed

- 完成 TASK-0026 ChatGPT Review 指定修订：`CF_collect@261af96` 将运行时 cleanup 放入 `finally` 并显式报告失败，异常和 READY 失败也进入同一清理路径。
- READY 仅接受已验证的 Lua `hook-status`，要求 `onUIThreadReceiveMessage` 与 `lua_pcall` 同时安装；进程启动、`script.load()`、任意消息、错误或 detach 不再误报 READY。
- Root 文档统一为“Collector 只检测、不改变 Root”；自动 cleanup 只处理 Gadget/server/forward/进程/临时文件，Root 由 User 手动关闭、重启并验证失效。

### Validation

- 正式仓库 baseline 12/12、修订后 focused tests 15/15、Python compileall、PowerShell 5.1 parser、六字段冻结、secret/local-data scan 与 diff check 通过。
- 未启动模拟器、Root、Frida 或 Collector，未执行 Spin，未扩大 `batch_spin` 六字段 schema；Subagents: none。

### Review

- TASK-0026 维持 `Review`，等待 ChatGPT 复审 `codex/collector-1-engineering@261af96acd93bb4be785ea9c1cb82c91fa31e434`。

## [0.17.0] - 2026-08-28

### Added

- 通过 User 已批准 Candidate 与 remote-CAS allocator 创建唯一 canonical `TASK-0026 — 【游戏】 Collector 1.0 Engineering`；Allocation relationship 为 `new`，不续写已完成的 TASK-0024。
- Task 固定 Adapter Registry、`event + adapter + source + payload` 统一 Event contract、Session/Manifest/Events/Spin Records artifact layout，以及 DS Sidecar 选择性迁移 allowlist。

### Changed

- User 将当前产品优先级从尚未执行的 TASK-0025 切换到 TASK-0026；Top Tycoon 保留 `Ready` 并进入 Backlog，不在 Collector 1.0 期间并行执行。
- 正式实现仓库由 `CashFrenzy_collect` 改名为 `CF_collect`；面向用户的介绍改用“【游戏】”，运行所需 package、command 与技术标识不做破坏性替换。

### Implemented

- `CF_collect@7c32877` 建立 `batch_spin / keepalive / registry` Adapter architecture、统一四段 Event、固定 Session artifacts、deterministic re-extract 与 JSON/Markdown value-free summary。
- `batch_spin` 严格冻结六字段；未迁移 DS Sidecar schema expansion、same-object discovery、`.local/`、真实 Session、fixture/artifact 或 Git 历史。
- 修复一键入口的项目根、Frida server `.xz` 路径和 helper venv binding；Android 9 probe/bootstrap JavaScript 与 main 基线逐字一致。

### Validation

- 正式仓库 focused tests 12/12、Python compileall、PowerShell 5.1 parser、deterministic/legacy read-only、Event envelope、value-free summary、secret/local-data scan 与 diff check 通过。
- AI-Workspace Registry 重建后为 13 canonical / 0 collision；本 Task 未启动模拟器、未执行新 Spin、未产生真实 Session。Subagents: none。

### Boundaries

- 不继续恢复字段，不扩大 `batch_spin` 六字段 schema，不做 20-Spin/F4，不改 Android 9 Hook/serializer/部署路线。
- 不迁移 DS Sidecar Git 历史、`.local/`、真实 Session、fixtures/artifacts、schema expansion、`same_object_fields` 或实验文件；`Subagents: none`。

## [0.16.9] - 2026-08-28

### Accepted

- TASK-0016 ChatGPT Review Round 3 Accepted；正式记录为 `reviews/TASK-0016-CHATGPT-REVIEW-3.md`，reviewed implementation commit 为 `d3dd72592fc8c176f317ffe6d0ac1362eed5930e`。
- TASK-0016 转为 Accepted；Memory Capability 与 Memory Governance 转为 Active。

### Validation

- 合并前人工复核通过：默认模式 `ASSISTED`；Secret/Local-only hard deny 早于 Registry；Workspace canonical gate 精确且冲突 fail closed；Git-live-first 与业务真相源优先级明确；无生产调试开关残留。
- 保持 production AUTO / Hook / WATCH disabled，不新增外部服务，不修改业务模块；`Subagents: none`。

## [0.16.8] - 2026-08-28

### Fixed

- 修复 TASK-0016 Review Round 2 的两个安全问题：provenance 现在必须包含有效字母或数字，并拒绝全部 documented placeholders（含 ASCII `-`）；`sensitivity=secret` 与 `scope=local-only` 在 Registry 前 hard deny。
- Host-local Registry 只能收紧 Global Safety Contract。误配 Registry 不能把 Secret/Local-only Candidate 写入 public 或 private Git Inbox；声明 Secret 的正文在 Outbox 整体抑制。

### Added

- 建立唯一 `memory/context/WORKSPACE.md`，作为跨 ChatGPT、Codex 与 Generic Agent 会话的 public-safe Git Memory 稳定读入口；继续复用 Candidate / Validator / Curator，不建立旁路。
- 在 `ASSISTED` 中增加显式 Workspace Memory 批准路径；高置信、有证据、public-safe、无冲突 Candidate 才能晋升，相同 key 去重、冲突进入 Review、supersede 保留历史。
- 通过三个独立正式来源初始化 Seed：Git Memory 长期真相源决定、TASK-0024 Accepted 研究边界、TASK-0023 Accepted 治理状态。

### Changed

- ChatGPT Bootstrap、Project Instructions、Core/System Context、Generic Agent、Memory Capability/Governance 和工具说明统一使用 Git-live-first 读取顺序。
- Context Refresh 将 Workspace Memory 纳入 Manifest 与 Source Pack，并输出 path、SHA-256 和读取时 Git HEAD；Project Sources 继续作为 `manual upload required` 离线快照。

### Boundaries

- 最终模式保持 `ASSISTED`；production AUTO、Hook、WATCH 与外部服务均未启用。未修改 TASK-0022、Cash Frenzy/Huuuge/Top Tycoon 研究、Collector、Document Assistant、飞书或 SVN；`Subagents: none`。

## [0.16.7] - 2026-08-28

### Added

- 通过 User 已批准 Candidate 与 remote-CAS allocator 创建唯一 canonical `TASK-0025 — Top Tycoon Android F4 Collection Feasibility Audit`；Allocation relationship 为 `new`，没有手工猜测 Task 编号。
- Task 固定使用 User 新建、显示名为 `topTycoon` 的模拟器，按 Identity → Reuse → Static → Bounded Dynamic → F4 Gate 执行，并要求双 Session、确定性生命周期与次级模块证据。

### Boundaries

- Spin、Auto Spin、资源消耗、购买与充值均不由 Codex 操作；动态样本前必须明确回复 `READY`，真实普通 Spin 仅由 User 手工完成。
- 不复用 Huuuge/Cash Frenzy 业务 schema、Raw、账号或数据目录，不在本 Task 建设完整 Collector，不修改、伪造或重放请求/响应/余额/奖励。

### Validation

- 从最新 `origin/main@a670fca` 建立独立 linked worktree，先重建 Registry，再通过官方 `task_cli.py promote ... --relationship new` 晋升；晋升前为 11 canonical / 0 collision / `status=valid`。
- Workspace Sync 保持 `ON_DEMAND` / 0 conflict；provider unavailable，6 个 Git-authoritative 发布项为 initial-publication stale，不影响 Git canonical Task 真相源；WATCH disabled，`Subagents: none`。

## [0.16.6] - 2026-08-27

### Accepted

- TASK-0024 ChatGPT Review Round 1 Accepted；正式 Review main commit 为 `17f776553c9d6450c25d145404c46ebaa59a3c3c`，reviewed branch commit 为 `1f666e79995537febce7a0bf2b98e7ba96100ea9`。
- `codex/cash-frenzy-inbound-structured-capture-spike` 已合入 main，canonical TASK-0024 状态收口为 `Complete`；F3 strengthened / F4 未证明保持不变。

### Boundaries

- 不在 TASK-0024 内继续完整 Collector、20-Spin、最小 adapter 或其他模块研究；未来方向必须另走 Roadmap / Candidate / 新 Task。
- Product Roadmap 将 Cash Frenzy Spike 从 Current 移入 Done；Top Tycoon 仅等待 User 决策，没有自动创建或执行 Task。

### Validation

- Registry writer 在 main 和普通 checkout 两次按设计 fail closed，均未改写 Registry；转入独立 linked worktree 后成功重建并验证为 11 canonical / 0 collision。
- focused 3/3、Task 23/23、Context 13/13、Memory 35/35、Task/Context PowerShell entry、JavaScript syntax 与 Workspace Doctor 全部通过。
- Workspace Sync 保持 ON_DEMAND / 0 conflict；provider unavailable，6 stale；WATCH disabled。

## [0.16.5] - 2026-08-27

### Confirmed

- TASK-0024 User 5-Spin Gate 捕获 5 个 `batch_spin` direct result objects；`base_win`、`bonus_base_win`、`total_win`、`coins`、`win_lines`、`win_pos_list` 各 5/5 命中。
- Pilot 复现率为 5/5；本轮人工授权只允许 3–5 Spin，因此 20-Spin 为样本不足，不做外推。
- Lua 路线成功后按 Gate 停止，未进入 `BLMessage`、decrypt/framing、XXTEA、Stalker、Local State Adapter 或完整 Collector。
- Capture 0 errors；临时 Hook/process/Gadget/server/forward 已清理，`Pie64_3` root 与 guest-`su` 已恢复，VHDX clean / root false。

### Changed

- value-free summarizer 新增受限 command profile 与 direct field event counts；focused tests 继续验证不输出字段值、identity 或隐私数据。
- TASK-0024 进入 Review；等级记录为 F3 strengthened，F4 因缺少双 Session/20-Spin 证据而未证明。建议 Adopt contract + Wrap scoped Android 9 binding + future small Build。
- 最终回归：focused 3/3、Task 23/23、Context 13/13、Memory 35/35、Task/Context PowerShell entry、Workspace Doctor 与 Registry 11 canonical / 0 collision 全部通过；Workspace Sync 为 ON_DEMAND / 0 conflict / provider unavailable / 6 stale。

## [0.16.4] - 2026-08-27

### Added

- TASK-0024 新增 inbound-scoped Lua probe、受限递归 serializer、value-free structure summarizer 与 3 项 focused tests。
- 新增 TASK-0024 Dynamic Proof 与脱敏 Lua baseline summary；Raw、字段值、绝对余额和完整响应继续只留本机。

### Confirmed

- 新 `Pie64_3 / AppResearch2` 为 Android 9；Cash Frenzy 4.78 / 478、arm64-v8a、`libnb.so` 现场确认。
- clean Gadget 零操作 120 秒保持稳定，0 errors、0 crash signature；旧 Android 7 约 15 秒 crash blocker 未复现。
- 60 秒 scoped baseline 捕获 21/21 type-3 inbound scope / `lua_pcall` 对，1 个 dispatch thread，0 errors、0 truncation；value-free 路径命中 `coins`、`chips` 与 `avg_bet.bc`。

### Gate

- `coins/chips` 当前来自 keepalive，不能写成普通 Spin direct Balance。下一步仅等待 User 手动执行 3–5 次普通 Spin；不进入 BLMessage/decrypt fallback。

## [0.16.3] - 2026-08-27

### Added

- 通过 User 已批准 Candidate 与 remote-CAS allocator 创建唯一 canonical `TASK-0024 — Cash Frenzy Inbound Structured Capture Spike`；Allocation relationship 为 `new`，不是 TASK-0022 子任务。
- Task 固定 Android 9 入站研究顺序、Lua serializer 安全预算、人工 Spin Gate、数据边界和停止条件。

### Changed

- 合入 ChatGPT Review 已 Accepted 的 TASK-0022 脱敏结果并将 canonical 状态收口为 `Complete`；没有向 TASK-0022 增加技术范围。
- Product Roadmap 的 Cash Frenzy Current 从 TASK-0022 Feasibility 更新为 TASK-0024 focused spike；不自动授权完整 Collector。

### Boundaries

- 新 Task 仅研究 Cash Frenzy Android 9；不继续 Nougat64，不自动 Spin/购买/充值，不修改请求、返回、余额或服务器状态。
- Raw、APK、`.so`、完整响应、账号与绝对余额留在本机；`Subagents: none`。

## [0.16.2] - 2026-08-27

### Accepted

- TASK-0023 ChatGPT Review Round 2 Accepted；reviewed commit 为 `bc0d3ad1e519fb908dce53a78a35f9c3687a5b51`，正式记录为 `reviews/TASK-0023-CHATGPT-REVIEW-2.md`。
- Idea Governance 与 Planner Writing Style 转为 `Accepted / Active`，Product Roadmap 和技术术语治理正式生效。

### Changed

- 更新 Standards 索引、Task、Handoff、Registry、Context Manifest 和 ChatGPT Source Pack，进入 main 收口与 allocator finalize 流程。

### Validation

- Context / Source Pack 刷新为 62 sources、0 broken link、0 secret issue；TASK-0023、两项 Active 标准与 Review 2 已进入刷新产物。
- Task 23/23、Context 13/13、Memory 35/35、PowerShell Task Registry 与 Workspace Context 入口全部通过；Registry 为 10 canonical / 0 collision，Doctor `ok: true`。
- Workspace Sync 保持 `ON_DEMAND`、0 conflict；provider unavailable，6 个发布项保持 stale，没有启用 WATCH。
- main push、allocator finalize 与清理结果在执行完成后通过最终交付 commit 和命令证据确认，不在提交内容中制造自引用 hash。

### Boundaries

- 不修改 TASK-0022、Cash Frenzy、Huuuge、Document Assistant 或 Workspace Sync 模式；`Subagents: none`。

## [0.16.1] - 2026-08-27

### Changed

- 按 TASK-0023 ChatGPT Review Round 1 的唯一 Required Fix，在 `standards/PLANNER_WRITING_STYLE.md` 建立准确、克制、面向受众的技术术语规范。
- 默认面向策划使用可理解的研究表达；复现、工程判断、授权、合规、安全与风险依赖真实机制时，强制保留 Root、Frida、Hook、逆向分析、协议解密、校验绕过、系统修改与 exploit 等精确术语。
- Core Rules、Repository/Bootstrap/Global AGENTS、Project Instructions、ChatGPT Bootstrap、Generic Agent 入口与 Context Hub 引用同一 canonical 规则，不维护第二套术语表。
- Context refresh 生成器把 `standards/PLANNER_WRITING_STYLE.md` 纳入 ChatGPT 单文件 Source Pack 与拆分来源替换清单；新增回归断言，避免新会话只获得摘要而漏读 canonical 规则。

### Safety

- 明确禁止通过改名或模糊化规避平台安全策略、权限检查、User 授权或 Review；禁止弱化真实风险，也禁止把被动研究夸大为攻击。

### Validation

- Context / Source Pack 刷新为 62 sources、0 broken link、0 secret issue；`planner-writing-style` 已使用新规则哈希进入 manifest 与 source pack。
- Task 23/23、Context 13/13、Memory 35/35、PowerShell Task Registry 与 Workspace Context 入口全部通过；Registry 为 10 canonical / 0 collision，Doctor `ok: true`。
- Workspace Sync 保持 `ON_DEMAND`、0 conflict；provider 当前不可用，因此 6 个发布项保持 stale，没有改成 `WATCH` 或伪称已发布。

### Boundaries

- Product Roadmap 与 Idea Governance 主体保持不变；未修改 TASK-0022、Cash Frenzy、Huuuge、Document Assistant 或 Workspace Sync 模式；`Subagents: none`。

## [0.16.0] - 2026-08-27

### Added

- 通过正式 Candidate 与 remote-CAS allocator 创建唯一 canonical `TASK-0023 — Idea Governance & Product Roadmap`；没有手工指定编号或编辑 Registry。
- 新增唯一 Git 源稿 `docs/roadmaps/PRODUCT_ROADMAP.md`，固定使用 `🔥 Current / 📋 Backlog / 💡 Ideas / ✅ Done` 四个分区。
- 新增 `standards/IDEA_GOVERNANCE.md` 与 `workflows/idea-governance/README.md`，定义 ChatGPT 主动发现、分类、Task 收尾 Idea Handoff 和 Codex 更新职责。
- 创建唯一正式飞书《AI Workspace｜产品路线图（Product Roadmap）》，自动登记到文档导航中心并默认企业内可编辑。

### Changed

- Core Rules、Project Instructions、Repository/Bootstrap/Global AGENTS、ChatGPT New Chat Bootstrap、AI Team 和 Architecture 纳入 Idea Governance。
- 项目全景说明原位增加 Product Roadmap 可点击入口，保留原生项目工作流图；文档导航中心自动增加 Roadmap 链接。
- 根目录 `ROADMAP.md` 明确只维护 Workspace 阶段建设，长期产品方向以唯一 Product Roadmap 为准。

### Validation

- 飞书 Product Roadmap 标题唯一且最终只保留四个固定二级分区；临时测试 Idea 成功进入 Ideas，回读后删除并恢复正式正文。
- 文档导航中心和项目全景说明均可进入 Roadmap；Roadmap、Hub、项目全景说明正文与企业内可编辑权限回读通过，Hub 登记恢复为 15 份正式文档且链接唯一。
- Task Registry 为 10 canonical / 0 collision；Task 23/23、Context 13/13、Memory 35/35、两个 PowerShell 入口与 Workspace Doctor 全部通过；Context refresh 为 62 sources、0 broken link、0 secret issue。
- Workspace Sync 保持 `ON_DEMAND`，WATCH disabled。

### Boundaries

- 未修改 TASK-0022、Cash Frenzy、Huuuge、Document Assistant 仓库或 Workspace Sync 运行状态；`Subagents: none`。

### Recovered validation issue

- 当前 Codex 会话仍连接缺少 `register_document` 的旧 MCP 进程；使用其 `get_document` 做回读后，项目全景说明的本机治理 metadata 被旧进程写回时丢失。未创建重复文档；改用 Document Assistant 当前 `main` 新进程重新登记并回读，Hub 恢复为 15 条正式文档、链接唯一。后续云验证不再调用该旧进程的写 Registry 路径。
## [0.15.5] - 2026-08-27

### Changed

- TASK-0022 停止 Collector Demo，继续同 Task 的 Cash Frenzy Slots Deep Research 子阶段，并切换到 User 指定的独立 `AppResearch2`。
- Nougat64 legacy native bridge 适配已验证；补充 `BLMessage.type @ +0x24`、type 3 inbound dispatch 与 Cocos Value conversion 边界证据。

### Validation

- AppResearch2 identity、Android 7.1.1、package 4.78 / 478、arm64 translation、Frida 17.17.0 server 与 arm64 Gadget handle 均现场确认。
- 20 秒无操作 BLSocket 边界复验通过；23 条入站均为 type 3，dispatch-scope `ccvalue_to_luaval=0`，probe errors=0。
- 1 GB / 2 CPU 和 4 GB / 4 CPU 两组 clean Gadget run 均复现 `gum-js-loop` + GLThread SIGSEGV，确认不是单纯资源不足。

### Result and boundaries

- Balance 保持 Phase 1.5 Derived recovery；Win 仍为 Derived candidate，direct Win / Result / Feature / Jackpot 未恢复，F3 不变。
- 本轮 0 Spin；仅执行 guest 入口和免费 starter login reward 的两个单点 UI tap，无购买、充值、付费奖励、Auto Spin 或挂机。
- root / CPU / RAM 已回滚，临时 server、Gadget/config、forwards 和 Cash process 已清理；未修改 Huuuge、其他游戏、Collector 主架构、Documentation、Report 或 WATCH；`Subagents: none`。

## [0.15.4] - 2026-08-27

### Added

- TASK-0022 新增面向游戏策划的《Cash Frenzy｜老虎机体验验证（Collector Demo）》Markdown，以及全中文 Spin 时间线、余额变化曲线和 Bet 档位分布 PNG/SVG。
- 飞书同名正式文档已创建并回读；正文使用飞书原生中文表格/条形图，预留 User 手动拖入不完整交叉验证视频的位置。

### Changed

- Phase 1.5 Review 决定记录为 Stop Spike；不再恢复协议。Demo 只使用既有 F3 outbound 字段，Collector 等级保持 F3。
- User 明确取消 Word 交付；本轮输出为 Git Markdown 与飞书文档。

### Validation

- Demo 捕获 193 个 Spin 样本、0 errors、192 个闭合 Balance 转移和 1 个 open tail；8 个已恢复字段均达到 193/193。
- 三张中文图表完成 960×480 PNG 渲染与逐张视觉检查；报告不含绝对余额、Raw、账号、本机路径或完整响应。
- 飞书创建、企业内可编辑权限、同名唯一性与正文回读通过；Document Assistant healthcheck 通过。

### Known issue

- 当前会话没有暴露 `register_document`，Hub 回读确认新标题出现 0 次。已创建文档保留且不重复创建；禁止人工修改 Hub，待可用 binding 对原文档补登记并回读唯一性。

### Boundaries

- 未继续 RTP、EV、Feature、Jackpot、result 或协议恢复；所有 Balance After / Net Delta 均标记为 Derived，Win 未写成 Confirmed。
- Demo 后 Cash、Frida、ADB forward、临时 Gadget/config 和采集进程均已清理；未修改 Huuuge、SVN、其他游戏、Capability 或 WATCH；`Subagents: none`。

## [0.15.3] - 2026-08-27

### Changed

- TASK-0022 增加 Phase 1.5 Balance Recovery Spike：复用已确认的 outbound Spin payload，以相邻 `client_coins` 形成 Balance Before/After，并在 Bet 稳定时生成脱敏 Win Candidate。
- 3 个普通 Spin 样本形成 2 个闭合 Balance 转移，成功标准 A 达成；Win 仅保留为 Derived candidate，Collector 等级保持 F3，未解析 opaque inbound result。

### Boundaries

- 达标后停止 Spike；未开始 Demo 报告，未扩大到 RTP、EV、Feature、Jackpot、OCR/UI、完整 result 或 Collector 重构。
- 逐笔 Balance/Win、Raw、APK、SO、完整响应和账号数据只留本机；未修改 Huuuge、Workspace governance、其他游戏、Capability 或 WATCH。
- 临时 Cash 专属 Gadget/config、ADB forward、Frida server 和 probe 进程已清理；`Subagents: none`。

### Validation

- 3/3 样本满足既有 Spin shape，Bet 数值且稳定，`client_coins` 数值；2/2 相邻转移发生 Balance 变化，2/2 Win Candidate 为非负整数，probe errors 为 0。
- 清理后 Cash 进程、Frida server、`tcp:27043` forward、本机 probe 进程及临时 Gadget/config 均不存在；Huuuge 仓库保持 clean。

## [0.15.2] - 2026-08-27

### Accepted

- TASK-0021 最终 UX 收尾完成并更新为 Accepted；ADR-0007 保持 Accepted，补充中文文档导航治理。

### Changed

- 唯一飞书入口原位更名为《AI Workspace｜文档导航中心》，保持同一 URL、14 条正式文档、八分类和企业内可编辑权限。
- 恢复 `docs/overview/AI_WORKSPACE_PROJECT_OVERVIEW.md` Git 源稿；项目全景说明原位增加“📚 下一步推荐阅读”和紧随其后的“🗺 项目工作流总览”，可直接进入文档导航中心并以图形理解完整协作链路。
- Core Rules、Project Instructions、Global AGENTS 模板、Repository AGENTS、Document Capability、Document Assistant Workflow、Workspace Sync Workflow 和 Context Hub Index 统一采用最终创建/登记/回读失败语义。

### Added

- 新增 Proposed `RFC-0004: Research Environment Strategy`，记录共享 Research Runtime、按游戏隔离 Evidence、单一活动 Capture 与前台包名 READY Gate；不修改当前 Cash Frenzy Candidate 或 TASK-0022。

### Validation

- 文档导航中心标题、首页说明、唯一性、链接、14 条登记与权限回读通过；项目全景说明章节位置、链接目标、原生 Mermaid 白板块、正文和权限回读通过，连续发布两次保持幂等。
- “核心规则”“实时 Context Hub”和“当前状态与任务入口”原位发布最新 Git 源稿，正文回读、自动登记和导航中心回读通过。
- Document Assistant 12 个测试文件 / 36 项测试及真实创建—登记—删除—恢复烟测通过；Workspace Task 23/23、Context 13/13、Memory 35/35 与 Doctor 通过。
- Review 2 要求的两个实现分支已分别合入 main：AI-Workspace `4c2b9b8f`，Document Assistant `b0292c31`。
- Document Assistant 正式 `main` 新启 STDIO MCP 进程的 `tools/list` 已确认包含 `register_document`，healthcheck 通过。

### Boundaries

- Workspace Sync 保持 `ON_DEMAND`，WATCH disabled；未修改 ChatGPT 设置或当前 Cash Frenzy 执行环境；`Subagents: none`。

## [0.15.1] - 2026-08-27

### Added

- TASK-0021 第二阶段新增唯一 `AI Workspace｜Documentation Hub`，作为 Workspace 所有正式飞书文档的导航入口；八个固定分类与统一元数据由 Document Assistant 自动生成。
- 新增 Document Assistant Workflow；Document Capability 增加 `CAP-DOC-REGISTER`，当前 binding 为 `register_document`。

### Changed

- Core Rules、Project Instructions、Global AGENTS 模板、Repository AGENTS 和 Workspace Sync Workflow 统一要求正式文档完成“创建、文档回读、Hub 登记、Hub 回读”。
- TASK-0021 第一阶段 Acceptance 保持有效；第二阶段增强进入 Review。

### Validation

- 历史扫描登记 14 份正式文档并排除 2 份临时连接测试；唯一 Hub、八分类、链接唯一、正文回读和企业内可编辑权限回读通过。
- 真实正式测试文档完成自动登记，删除后 Hub 恢复为 14 条；Document Assistant 构建和 10 个测试文件 / 32 项测试通过。

### Boundaries

- Git 仍是真相源，Documentation Hub 只负责飞书导航且禁止人工维护；Git 不记录 Hub 的独立 ID、token、私有 Registry 或敏感返回值。
- Workspace Sync 保持 `ON_DEMAND`，WATCH disabled；未修改 ChatGPT 设置；`Subagents: none`。

## [0.15.0] - 2026-08-27

### Added

- User 明确批准 Cash Frenzy Collector Feasibility Candidate 后，正式 `task_cli.py promote` 通过 remote-CAS allocator 分配唯一 canonical ID `TASK-0022`。
- 新增 `tasks/TASK-0022-CASH-FRENZY-ANDROID-COLLECTOR-FEASIBILITY-AUDIT.md`；完整规格保留 Candidate provenance，Task 初始状态为 Ready。

### Changed

- `CANDIDATE-20260827-CASH-FRENZY-COLLECTOR-FEASIBILITY` 的 User decision 更新为 `Approved`，状态由 Candidate 更新为 Migrated，并记录实际 canonical 路径。
- Task Registry 由 allocator 自动重建为 9 canonical、2 companion、1 个已 Migrated Candidate record、6 Review、0 collision；当前待决 Candidate 为 0，未手工编辑 Registry。
- 同步 main commit `7eb16b0` 后，按本轮更晚且更具体的 User 指令，将“共用 Research 模拟器”历史说明标记为 superseded；TASK-0022 使用独立 `CashFrenzyResearch`，不修改或复用 `HuuugeResearch`。

### Boundaries

- Task issuance 阶段尚未创建模拟器、拉取 APK、启动 Capture 或访问业务数据；reservation 保持 `pending-main`，待 canonical 进入 main 后执行 `finalize`。
- Workspace Sync 保持 `ON_DEMAND`，WATCH disabled；未修改 Huuuge、SVN、飞书或业务仓库；`Subagents: none`。

## [0.14.1] - 2026-08-27

### Accepted

- TASK-0021 与 ADR-0007 经 ChatGPT Review Round 1 Accepted；正式 Review 记录为 `reviews/TASK-0021-CHATGPT-REVIEW-1.md`。
- Accepted implementation 为 `058887993a5d0aa98df68b814b8adc72477cdaf7`，允许合并 AI-Workspace 分支与 Document Assistant PR #1。

### Validation

- 正式 Registry scan / validate、Task tests 23/23、Context tests 13/13、Memory tests 35/35、PowerShell Task Registry 与 Workspace Context 入口全部通过。
- Registry inventory：8 canonical、2 companion、1 Candidate、6 Review、0 collision；Context refresh 为 56 sources、0 broken link、0 secret issue。

### Boundaries

- Workspace Sync 最终模式保持 `ON_DEMAND`；Acceptance 不授权启用 `WATCH`。
- 现有 Drive Context Hub、文档、权限、provider IDs 和 ChatGPT Project Sources replacement 状态保持不变。
- `Subagents: none`。

## [0.14.0] - 2026-08-27

### Added

- TASK-0021：新增 `CAP-CONTEXT`、ADR-0007、Planner Writing Style、`LIVE_CONTEXT_MANIFEST.json`、Workspace Sync reference implementation、Windows 入口和 ChatGPT/Codex/Generic Agent bindings。
- 建立飞书 Drive Context Hub authority model：Git-authoritative 内容只读发布，协作草稿可编辑但只进入 Candidate/Review；Wiki 因当前 scope Gate 未通过而未采用。

### Changed

- TASK-0020 Accepted implementation 以 merge commit `31475bd` 进入 main；TASK-0021 通过 `637840a` 同步 latest main，语义合并 allocator、Workspace Sync、中文行文和 Memory 规则。
- TASK-0020 与 ADR-0006 状态更新为 Accepted；TASK-0021 更新为 Review。Task Registry 继续由正式 validator 重建。
- Workspace Sync 最终模式保持 `ON_DEMAND`。Project Sources 降级为稳定 Bootstrap / 离线回退，动态状态优先使用 latest Git、Live Context manifest 和 Host-local pack。
- Document Assistant PR [#1](https://github.com/840832144/document-assistant/pull/1) 保持 OPEN，head `29fd9f1a58f2626f180e351133f2cd7571c7b43d`，本轮未修改。

### Validation

- Context Python tests 13/13 与 PowerShell Workspace Context 入口通过；doctor 的 manifest、Git、Secret、path 和行文检查全部通过。
- 正式 Task Registry scan/validate、Task tests 23/23、Memory tests 35/35 与 PowerShell Task Registry 入口通过；真实 inventory 为 8 canonical、2 companion、1 Candidate、5 Review、0 collision。
- ON_DEMAND 本地同步生成 local pack 与 publish plan；因本轮未使用 provider snapshot，状态明确为 stale 6、unavailable 1、disabled 2、conflict 0，没有虚报 Drive 已更新。

### Boundaries

- 现有 Drive Context Hub、7 个唯一标题及 authority-aligned 权限保持不变；没有再次发布、改名或改权限。
- 未启用 WATCH，未执行 Cash Frenzy，未修改 Huuuge、SVN、Collector、Capture、飞书正文、Document Assistant PR 或其他业务仓库；`Subagents: none`。

## [0.13.1] - 2026-08-27

### Fixed

- TASK-0020 Review Round 1：allocation 写操作统一 latest-main / non-main independent linked-worktree gate；remote ref CAS 覆盖跨 clone / Host；reservation 保持到 main 后 finalize；新 canonical 强制 `project_key`；Draft overlap 与 companion 严格分类。
- TASK-0020 Review Round 2：reservation commit 的 tree 与唯一 parent 固定为 latest `origin/main`，requesting branch HEAD 只保留为 SHA metadata，不再通过 reservation ref 推送未合并 branch tree 或 commit graph。

### Validation

- Task disposable tests 23/23、Memory tests 35/35 通过；新增跨 clone sentinel 回归证明未推送 sentinel 文件、commit object 和 ancestry 均不能由 reservation ref 访问，且 reservation parent/tree 等于 `origin/main`。
- Windows PowerShell 5.1 入口、真实 Registry scan/validate 通过；真实仓库保持 8 canonical、2 companion、1 Candidate、5 Review、canonical collision 0。
- Context Manifest、Project Source Pack 与 replacement list 刷新；Project Sources 保持 `manual upload required`，Memory 保持 `ASSISTED`。

### Boundaries

- 未执行 Cash Frenzy Candidate；未修改 TASK-0021、Huuuge Collector、Lottery、Capture、document-assistant、飞书、SVN 或其他业务仓库。
- `Subagents: none`。

## [0.12.1] - 2026-08-27

### Fixed

- TASK-0018 Review Round 1 修改完成：策划优先报告结构、真实货币购买提取、普通筹码下注术语、礼包价值限制与技术附录表述已经统一。
- 原飞书文档使用替换接口原位更新，未创建重复文档；最终回读确认标题唯一、章节完整并保持企业内可编辑。

### Changed

- Huuuge 项目控制面切换到外部证据 commit `4a5dddf7782307c6a8f368c9f1dc6390eec6f65b`，TASK-0018 保持 `Review` 并进入 ChatGPT Review Round 2。
- Lottery Memory 与报告索引补充四次成功购买的脱敏聚合：54.43 SGD、763 张票、235 loyalty points；礼包表观每票成本不得解释为独立票价或长期付费回报。

### Validation

- 外部 Extractor 编译通过，7/7 单元测试通过，四次购买聚合和票务总账复算通过。
- 飞书原文档最终回读 367 blocks、4568 个正文字符、单一标题；权限回读为企业内可编辑。
- 未复制 Raw、decoded values、真实 Session/account/request/product/store/order 标识、绝对余额、完整余额轨迹或 credentials；未修改 Collector、CR、SVN、游戏或服务端状态。

## [0.12.0] - 2026-08-27

### Added

- TASK-0018 Lottery 数值拆解交付索引，固定外部 Git 报告 commit 与企业内可编辑飞书文档。

### Changed

- TASK-0015 从 `Ready` 更新为 `Complete`，TASK-0018 从 `Ready` 更新为 `Review`；TASK-0014 保持 `Accepted`。
- Huuuge Project Status、Memory 和 Knowledge Index 同步 Lottery L3 Runtime Observed 基线；证据分布调整为 L3 × 12、L2 × 3、L1 × 22。
- Lottery 知识明确区分直接 Toss 奖励、阈值返还、购买发放与升级关联产出；升级后的余额变化为 Confirmed，升级因果保持 Estimate。

### Validation

- 外部 `huuuge-android-research@bfed5f30e098522ffb98ef5eb7d63e824d68b1c4` 已推送，报告与 6 份脱敏 CSV 可定位。
- 飞书正文回读 565 blocks，关键 Finalize、升级关联与 CR 章节存在；企业内可编辑权限验证通过。
- 未复制 Raw、decoded values、真实 Session/account ID、绝对余额、付费价格或 credentials；未修改 Collector、CR、SVN、游戏或服务端状态。

## [0.11.2] - 2026-08-27

### Fixed

- TASK-0016 Review Fix 1：新增 repository classification 与 Host-local approved destination contract；Project Private Candidate 只有在 alias、writer、classification、scope、sensitivity、source project 和外部 Git root 全部匹配时写入私有 repository，否则进入 Outbox。
- TASK-0016 Review Fix 2：AUTO canonical promotion 现在要求非 main/master linked worktree、仅允许 Inbox dirty scope，并将 target、Candidate、Archive、index 作为可回滚事务；Git identity/status 变化 fail closed。
- TASK-0016 Review Fix 3：CLI、Event file、Generic Agent 三条 Git Candidate 入口拒绝空值及 `unknown` / `n/a` / `none` / `-` 等占位 provenance。

### Validation

- 34/34 单元测试通过；新增 disposable private Git routing、未批准/无效 Registry、classification/sensitivity mismatch、public alias 冲突、private path 回指 public repository、main/dirty worktree gate 与三入口 provenance 回归。
- 五类 fault injection（target 后、Archive 前、Archive 后、index save、Git status change）均恢复 target/Candidate/Archive/index 执行前状态，`promoted=0`，无 recovery record。
- Round 2 隔离 Pilot：captured 3（其中 approved private Git 1）、promoted 1、review 1、local-only/Outbox 4、OFF suppressed 1、failed 0；最终模式 `ASSISTED`。

### Boundaries

- Private 测试只使用 disposable Git repository；未读取或修改真实 Huuuge、CR、Collector、Capture、SVN、飞书或 Document Assistant。
- 未激活 Hook、Global runtime 或 production AUTO；未修改 TASK-0017 网络脚本、分支或 Codex proxy 配置。

## [0.11.1] - 2026-08-27

### Added

- TASK-0017：新增 Windows PowerShell 5.1 Codex Desktop 网络状态、transport matrix、最小修复、恢复和脚本回归入口。
- 新增脱敏实验记录与可复用 reconnecting-proxy Solution，记录 Aurora / WinINET / WebSocket / HTTPS / TLS 的分层证据。

### Fixed

- Codex 用户配置启用当前版本已验证的 `features.respect_system_proxy = true`，使 Responses WebSocket 经 WinINET loopback proxy 建立 HTTP 101；没有修改 Windows 或 Aurora 全局路由。
- Restore 以 post-fix hash 选择精确恢复或仅撤销本任务键，保留 Codex 后续写入的无关设置，并兼容 Windows PowerShell 5.1 JSON 对象属性扩展；键冲突时 fail-closed，Repair 与 Restore 失败都回到操作前配置。

### Validation

- Baseline 稳定复现 WebSocket timeout 与 HTTPS inference reachable；temporary system-proxy override、explicit proxy 和持久修复均得到 HTTP 101，未观察到 TLS 或 DNS failure。
- 完成 restore exact-hash、保留后续配置的 surgical restore、reapply、Repair 幂等和 PowerShell 5.1 回归。
- 三个新 Codex 任务连续返回完整验证串，每次随后 transport probe 均为 WebSocket HTTP 101、HTTPS ok、TLS ok。
- `feishu-docs` healthcheck 与 Git fetch / branch push 正常。

### Boundaries

- 未修改 TASK-0016 worktree、Huuuge 仓库、Collector、Capture、Aurora 配置、Windows 全局 proxy、TLS trust、Provider 或 MCP 配置。
- 未强制结束当前 Codex Desktop 外壳；新任务和新 CLI 进程已验证配置重载，完整外壳退出重开留给 User 在 Review 后正常执行。

## [0.11.0] - 2026-08-27

### Added

- TASK-0016：新增 Git-backed Memory Capability、治理标准、ADR-0005、Memory Event/Candidate/Review schema、Inbox/Review/Archive/Index 与 Public-safe Solution 目录。
- 新增跨平台 Python 标准库实现和 Windows PowerShell 入口，支持 Capture、Validate、Curate、Refresh、Status 与 OFF/ASSISTED/AUTO 模式切换。
- 新增 ChatGPT Project、Codex、Generic IDE Agent adapters，以及默认禁用的 Codex SessionEnd hook reference。
- 新增 Context Manifest、ChatGPT Project Source Pack、Source replacement list 和隔离 Pilot。

### Changed

- Global/Project AGENTS、ChatGPT 00–03 Sources、AI Team、Architecture、Capability Catalog 和相关 README 加入 source-side Memory Check 与安全路由。
- Reuse-first 结论采用 OpenAI 原生 recall/lifecycle 能力与 Git 真相源的组合；不安装外部 Memory SaaS、数据库或高权限 App。
- Production 和仓库默认模式为 `ASSISTED`；`AUTO` 只在隔离 Pilot 验证受限的低风险新 Solution 晋升。

### Fixed

- 最终回归发现 PowerShell `ValueFromRemainingArguments` 会把省略参数转成空字符串；薄 wrapper 现在构造显式命令数组并以命名参数交给通用 launcher，Status/Mode/Curate/Refresh 一键入口均加入真实回归。

### Validation

- 17/17 单元测试通过，覆盖 schema/fingerprint、Secret、dedup、conflict、concurrency、rollback/no-overwrite、Git gate、dirty sync fail-closed、Windows named parameters 和所有无额外参数的薄 wrapper。
- 隔离 Pilot：captured 2、promoted 1、review 1、local-only/Outbox 3、OFF suppressed 1、conflicts 0、failed 0；未虚构 false-positive 或 missed-capture rate。
- 最终 AI-Workspace refresh：41 public control-plane sources、0 Secret issue、0 broken link、private repositories not read、manual upload required。

### Boundaries

- 未安装或激活 Global hook，未切换 production AUTO，未自动替换 ChatGPT Project Sources，未创建外部服务、私有 Context Hub 或新权限。
- 未修改 Huuuge 仓库、运行中的 Collector、当前 Capture、SVN、飞书云文档、Document Assistant 或其他业务仓库。

## [0.10.1] - 2026-08-27

### Fixed

- TASK-0014 Review Fix：安装器现在先完成并验证 OFF，再创建或替换 Agent 模板；config OFF 失败不会触碰 Agent 目录或输出误导性成功信息。
- Global AGENTS、Bootstrap README、ADR-0004 与 Pilot 明确禁止 MANUAL 和 `--yolo`、Full access、`danger-full-access`、宽松 `/permissions` 或等价父 turn 权限并用。
- `knowledge_retriever` 定位改为读取本地/已提供资料；飞书继续由主 Agent 代读并提供最少、脱敏摘要。

### Validation

- 新增安装失败原子性回归：inline、multiline、config lock 三类 OFF 失败均保持配置字节和既有模板哈希不变，不新增其余模板，不输出 `Installation default: OFF`。
- MANUAL 切换输出明确的权限前提和“无法自动检测 live permission”；本轮宽松权限环境保持 OFF，没有启动 Subagent。
- Windows PowerShell 5.1、幂等安装、配置完整性、Global 模板同步和最终 OFF 状态重新验证通过。

### Boundaries

- 未实现不可靠的 live permission 自动检测，也未在宽松权限环境启用 MANUAL。
- 未修改 Agent 数、并发上限、MCP Server、业务仓库、飞书云文档或 ChatGPT 设置。

## [0.10.0] - 2026-08-27

### Added

- TASK-0014：新增 4 个版本化只读 Codex Agent 模板，分别负责仓库探索、资料检索、证据测试核验和独立 Review。
- 新增 Windows PowerShell 5.1 安装、`OFF` / `MANUAL` 开关、脱敏状态与隔离回归测试脚本。
- 新增 [`ADR-0004`](docs/adr/ADR-0004-Codex-Subagent-Pilot.md)、[`Codex Subagent Bootstrap`](bootstrap/codex/README.md) 与 [`Pilot 记录`](docs/experiments/CODEX_SUBAGENT_PILOT.md)。

### Changed

- Global AGENTS 增加保守 Subagent Policy：默认单 Agent、简单任务不委派、主 Agent 唯一写入、失败自动降级。
- AI Team 和 Architecture 明确 Subagent 只承担独立只读工作，不改变 Capability Discovery、完成标准或外部写入授权。
- 本机安装 4 个 Agent，`config.toml` 只增加/维护 `[agents]` 开关和并发上限；试验结束必须恢复 `OFF`。

### Validation

- 四个 Agent TOML 均通过 `tomllib`，且 `sandbox_mode = "read-only"`；PowerShell 脚本通过 Windows PowerShell 5.1 语法与运行测试。
- 隔离回归覆盖 legacy alias、非 Agent 配置保留、特殊 TOML 形态 fail-closed、同名模板备份、幂等安装和安装后 OFF。
- OFF 新会话无法启动 Subagent，但普通单 Agent 任务成功；MANUAL 新会话成功启动并汇总指定 `repo_explorer`。
- 复杂只读场景并行运行 3 个 Agent；子 Agent 发现的脚本阻断经主 Agent 修复并复测，未发生并行写冲突。
- Reviewer 发现 MCP 继承风险后，当前 Pilot 改为在子 Agent 中禁用 `feishu-docs` 和 `node_repl`；新会话无副作用探针确认二者均不可用。
- 模式补丁器新增独占锁、多行 TOML fail-closed 与并发竞争回归，避免覆盖同时发生的非 Agent 配置更新。
- 最终恢复 `OFF`；新会话确认 Subagent tools 不可用、普通单 Agent 任务仍可完成，四个模板继续保留。
- 当前客户端没有暴露可归因 usage/token 数字，因此没有记录虚构额度对比。

### Boundaries

- 未实现 AUTO、1+8、多 Agent 并行写、Git worktree 调度器或额度系统。
- 未修改 Huuuge Collector、Document Assistant、MCP Server、SVN package、飞书云文档、ChatGPT 设置或其他业务仓库。

## [0.9.0] - 2026-08-26

### Added

- TASK-0013：建立 [`Capability Catalog`](capabilities/README.md)，定义 Capability-first 发现顺序、Catalog schema、契约状态与实现状态分离规则。
- 建立首个共享 [`Document Capability`](capabilities/document/README.md)，定义 7 个结果 Operations、READ/WRITE/ADMIN 等级、成功证据、默认权限、failure semantics 和当前 provider mapping。
- 新增 ADR-0003，正式决定“先发现 Capability，再选择 Implementation Binding 与 Tool”。

### Changed

- Global AGENTS 顶层入口从 Tool-first 调整为 Capability Discovery；Tool 的检查与选择只属于 Capability 实现层。
- `Document Assistant` 从“Capability 本身”校正为 `Document Capability` 的当前实现 provider；Feishu MCP tools 明确为 provider-specific interfaces。
- ADR-0002 标记为 Superseded，由 ADR-0003 取代；历史内容保留，不重写原决策。
- Architecture、Workspace Kernel、Capability Model、AI Team、Manifest、Roadmap、RFC-0002、Document Assistant Roadmap、Feishu Document Skill 与 Bootstrap 统一采用 Capability-first 模型。
- 本机 `C:\Users\admin\.codex\AGENTS.md` 与仓库模板同步更新；公共 AI-Workspace 和现有 First Run 路径保持不变。

### Validation

- 对照 OpenAI 官方 `AGENTS.md` 文档确认 Global 与项目级指令仍按既有顺序叠加；Capability-first 是本 Workspace 的治理契约，不冒充 Codex 内置 resolver。
- `bootstrap/AGENTS.md` 与本机 `~/.codex/AGENTS.md` 的 SHA-256 一致，且没有 Global override 遮蔽。
- Catalog、Document Capability、ADR、Architecture、Kernel 和 Manifest 内部链接、边界与术语验证通过。
- 全仓敏感值、禁用词、diff 和私有新人前置检查通过。

### Boundaries

- 未实现 Capability Registry、resolver、自动选择器或新 Tool。
- 未修改 Document Assistant、MCP 配置、ChatGPT 设置、First Run 飞书文档、采集器、SVN package 或业务功能。

## [0.8.0] - 2026-08-26

### Added

- TASK-0012：新增 `bootstrap/AGENTS.md`，作为 `~/.codex/AGENTS.md` 的版本化 Global Codex 模板。
- 建立 Tool Discovery 规则：读取生效指令、检查当前 Host 实际能力、优先专用接口、区分 READ/WRITE/ADMIN、先确认再修改、失败时不建立未经批准的替代入口。
- 将 Document Assistant 定义为所有项目共享工具，记录实现真相源、非敏感资料入口、工具分级、搜索防重、回读验证和凭据边界。
- 新增 ADR-0002，正式记录 Global Tool Discovery 与 AI-Workspace 职责分离。

### Changed

- 本机安装 `C:\Users\admin\.codex\AGENTS.md`，与仓库模板内容一致；当前没有 `AGENTS.override.md` 遮蔽该文件。
- AI-Workspace 不再承担运行时工具入口职责，只定义 Game Design 的 Capability、Workflow、Skill、Template、项目治理和工具使用契约。
- Architecture、Workspace Kernel、Capability Model、Manifest、Roadmap、RFC-0002、Feishu Document Skill 和 AI Team 统一移除工具目录、安装入口、endpoint、credential 与连接状态职责。
- 新生成云文档的默认企业内可编辑规则提升为 Global Codex 规则；管理员策略失败时保留文档并报告，不重复创建。
- 根据当前权限现实发布 First Run RC4：公共 AI-Workspace 成为新人唯一必需 Git 仓库，私有实现仓库只供维护者追溯，不再作为新人 Clone 或安装前置。
- 将公司 SVN 和管理员预配置的 Document Assistant 加入前三分钟 fail-fast；保留“新策划在新电脑 30 分钟完成采集、Markdown、AI 写飞书”的真实盲测目标，不预填成功或耗时。
- 同一篇飞书 First Run Guide 使用 replace 同步 RC4，保持原 document ID 与既有企业内可编辑权限，不创建副本。

### Validation

- 对照 OpenAI 官方 `AGENTS.md` 发现顺序确认 Global 与项目级叠加规则。
- `bootstrap/AGENTS.md` 与本机 `~/.codex/AGENTS.md` 的 SHA-256 一致。
- First Run 全文检查确认新人主线不再要求访问或 Clone 私有 Git 仓库。
- 飞书回读确认 RC4、30 分钟目标、公共单仓入口和前三分钟预检均存在，两条私有仓库 Clone 指令均不存在。
- 对原飞书 document ID 再次执行公司编辑权限回读，确认 `link_share_entity=tenant_editable`、`verified=true`。
- 全仓检查确认没有 credential、token 或运行时 endpoint 值写入；内部链接、禁用词、diff 与 Workspace 边界验证通过。

### Boundaries

- 未修改 Document Assistant、`feishu-doc-mcp`、MCP 配置、ChatGPT 设置、采集器、SVN package 或业务功能。
- Global 文件只包含稳定规则和公开仓库引用，不包含项目状态、私有 Registry、文档正文或 secrets。

## [0.7.0-rc.3] - 2026-08-26

### Changed

- 将新人首次打开的工作目录从一次性首跑目录统一为长期复用的 `C:\AI-Workspace`。
- 从零提示词新增目录状态判断：空目录 Clone AI-Workspace、已有正确仓库安全更新、非空且不是目标仓库时停止并报告冲突，不得覆盖。
- 明确该目录后续继续承载 Knowledge、Status、Handoff 和其他游戏策划项目，不在首跑后丢弃。
- 飞书原文档使用 replace 同步 RC3，保持同一 document ID 和企业内可编辑权限。

### Boundaries

- 只修改文档和流程；未开发功能，未修改采集器、外部研究仓库、SVN package 或本机环境。

## [0.7.0-rc.2] - 2026-08-26

### Changed

- 根据 User 预验收反馈，将 First Run Guide 从“AI/技术流程说明”重构为新人可直接执行的主线。
- 在文档最前新增 12 个连续步骤：打开 AI、发送从零提示词、完成登录、安装缺失软件、确认专用实例、登录游戏、等待 READY、正常操作、停止、核对结果、检查 Markdown/飞书、最终验收。
- 每一步补充新人应该说什么、AI 应该完成什么、看到什么算通过，以及卡住时可直接发送的回复。
- 新增“新人全过程只需要说的五句话”，后续技术章节保留为 AI 与排障参考。
- 飞书原文档使用 replace 更新，无 conversion warning；回读确认新人主线、第 12 步和五句话均存在。

### Boundaries

- 此反馈来自参与项目的 User，不计入未参与开发策划的独立盲测。
- 未开发新功能，未修改采集器、外部研究仓库、SVN package、BlueStacks 或本机研究实例。

## [0.7.0-rc.1] - 2026-08-26

### Added

- TASK-0011 盲测前版本《Huuuge 新人上手指南（First Run Guide）》，覆盖新电脑准备、仓库 Clone、AI 主导启动、采集、Markdown、Document Assistant、成功验证和常见问题。
- `REPORTS/TASK-0011-FIRST-RUN-VALIDATION.md`，用于真实记录未参与开发策划的卡点、阶段耗时、AI 独立引导能力与后续文档修订。
- 飞书版本 [`Huuuge 新人上手指南（First Run Guide）`](https://gfok27asqq.feishu.cn/docx/Ffibd2Cx2oXFgfxdKnJcE6uUnZf)。

### Changed

- 将 First Run 默认入口设为 Codex 或 Trae + DeepSeek；新人只处理登录、审批和正常游戏操作，AI 处理检查、启动、停止、整理、Markdown 与飞书发布。
- 文档规范新增：面向策划/用户的正文默认使用中文，其他语言只用于必要技术内容。
- 云文档规范新增：除非 User 明确要求其他权限，新生成文档默认企业内可编辑；管理员策略失败不得触发重复创建。
- Huuuge 项目 README、Memory、Workflow、Status 与 Reports Index 接入 First Run Guide、云文档默认权限和验证记录。

### Validation

- `feishu_healthcheck` 通过环境、token、API connectivity 和 Drive permission probe。
- 创建飞书文档无 conversion warning；`get_document` 回读标题、正文、公司编辑规则和盲测章节成功。
- 通过当前 Document Assistant STDIO Server 执行 `grant_company_edit`，回读 `link_share_entity=tenant_editable`、`verified=true`。

### Pending

- 尚未由未参与开发的策划执行盲测，因此真实卡点、耗时和 AI 是否能独立引导仍为 Pending。
- 完成盲测后只允许修订文档和流程，再发布正式 0.7.0 并进入 ChatGPT Review。

### Boundaries

- 未修改 `huuuge-android-research`、采集器、SVN package、BlueStacks 或本机研究实例。
- 未开发任何新功能，也未复制 Raw、decoded values、账号/Session 数据、credential 或完整运行日志。

## [0.6.0] - 2026-08-26

### Added

- TASK-0010：建立 `Huuuge Evidence Standard`，统一 L0 Unverified、L1 Schema、L2 Configured / Visible、L3 Runtime Observed、L4 Triangulated 五级判定标准。
- 定义 Schema、Config、Runtime、UI、Manual 五类引用的合格来源、必填定位信息和单类证据上限。
- 定义 `HGR-YYYYMMDD-TYPE-NNN` Citation ID、完整/紧凑引用格式、claim scope、limits 以及升级、降级、冲突和过期规则。

### Changed

- Knowledge Index 与 Slots、Systems、Events、Others 全部 37 个模块迁移到统一等级：L3 × 11、L2 × 4、L1 × 22、L0/L4 × 0。
- 将模块证据摘要统一为 Runtime、Schema 和 Schema hint，明确 ZPK 文件名命中不能单独提升等级。
- 项目 README、Memory、Workflow、Status 与 Codex/ChatGPT Handoff 接入统一 Evidence Standard。
- TASK-0009 的 E0–E3 临时导航模型由 L0–L4 标准取代；历史 CHANGELOG 保留原始记录。

### Boundaries

- 未修改 `huuuge-android-research`、采集器、module catalog generator、SVN release 或本机研究环境。
- 未虚构或回填当前外部 artifact 尚不存在的 Citation ID，也未把任何模块提升到 L4。
- 未复制 Raw/decoded values、账号/会话数据、截图、完整日志、APK、binary 或 credential。
- 未开发 Evidence Registry、采集、Extractor、Exporter 或报告功能。

## [0.5.0] - 2026-08-26

### Added

- TASK-0009：建立 `Huuge Research Knowledge Index` 作为整个研究知识的统一入口。
- 建立 Slots、Systems、Events、Others 四类导航，覆盖外部 catalog 全部 37 个模块。
- 为每个模块记录 evidence level、live/schema/static 数据来源、结构完成度和 Review 后下一步计划。
- 定义 E3 Primary live、E2 Cross-cutting/config live、E1 Schema-only、E0 Inferred/static 四级知识证据模型。

### Changed

- Huuuge Project README、Memory、Workflow、Status 接入 Knowledge Index，并将当前 milestone 更新为 TASK-0009 Review。
- 将 Huuuge 项目 README 与 Knowledge Index README 的策划入口文案改为中文，同时保留固定模块名和技术文件名。
- Codex/ChatGPT Handoff 更新为 Knowledge Base Review gate。

### Boundaries

- 未修改 `huuuge-android-research`、采集器、module catalog generator、SVN release 或本机研究环境。
- 未复制 Raw/decoded values、账号/会话数据、APK、binary、credential 或完整外部 dossier 正文。
- 未开发新采集、分类器、Extractor、Exporter 或报告功能。

## [0.4.0] - 2026-08-26

### Added

- TASK-0008：从 Workspace Project Template 初始化 `projects/huuuge-android-research/`。
- 建立 Huuuge 项目 Context、Memory、Workflow、Status、Reports 和 Assets 控制面。
- 建立 Battle Pass、Slots、Lottery、Task/Missions 四条稳定研究入口，并锁定外部 evidence baseline commit `0590c2c`。

### Changed

- `projects/README.md` 从“仅提供模板”更新为包含首个正式登记的游戏研究项目。
- Codex/ChatGPT Handoff 更新为 TASK-0008 Review gate。

### Boundaries

- 未迁移或修改 `huuuge-android-research` 的源码、采集器、脱敏产物或运行配置。
- 未复制 Raw/decoded values、账号/会话数据、APK、native/Frida binary、credential 或外部文档正文。
- 未开始新采集、Extractor、报告开发或 Feishu 发布。

## [0.3.0] - 2026-08-26

### Added

- TASK-0007 `Document Assistant Capability Roadmap`，规划公司文档中台的 15 个 Capability、六阶段演进、Review 问题与非目标。
- 新增 `docs/roadmaps/` 作为服务与工具 Capability Roadmap 的索引入口。

### Changed

- 明确 `Document Assistant` 暂不改名，现有实现保持不变，外部仓库继续作为实现真相源。
- 将 Workspace Phase 2 标记为 Planning / Waiting for ChatGPT Review。
- 明确共享公司基础设施可以服务多个使用方，但 AI-Workspace 只治理其 Game Design 使用边界，不导入其他领域业务内容。

### Boundaries

- 未修改 Document Assistant、`feishu-doc-mcp`、MCP 配置或 ChatGPT 设置。
- 未开发 transport、permission、sync、monitoring 或 deployment 功能。
- 未调用 Feishu API，未迁移仓库或文档数据。

## [0.2.0] - 2026-08-26

### Changed

- 将 AI-Workspace 从通用 AI 工作空间正式收敛为 Game Planner AI Workspace。
- 明确目标用户为游戏策划、游戏数值策划、系统策划、活动策划和数据分析，并排除非游戏领域。
- 将 Roadmap 重构为 Workspace Foundation、Document Assistant、Workspace Sync、Planner Toolkit 四阶段。
- 完善 AI Team 的 Decision、Review、Ownership、Tool Ownership、Security 和 Escalation 规则。
- 将项目标准从 Context、Memory、Workflow、Status 四件套扩展为包含 Reports、Assets 的统一游戏项目结构。
- 将项目模板的唯一入口收敛到 `projects/TEMPLATE/`，移除旧的重复四件套模板。

### Added

- 新增 Workspace Kernel，定义 Workspace、Project、Skill、Workflow、Capability、Template、Tool、Agent、Memory、Status 及 Mermaid 关系图。
- 新增 Capability Model，定义 Capability、Skill、Workflow、Template、Tool 的分层关系。
- 新增 Game Analysis、Slot Analysis、Battle Pass、Economy Design、Lottery、Task System、Excel、SQL、Python、Report Writing、Feishu Document 共 11 类 Skill 目录。
- 新增 `projects/TEMPLATE/` 游戏项目标准模板。
- 新增仅作规范示例的 `workspace.yaml.example`。
- 新增 ADR-0001，记录 Game Design 领域收敛决定。

### Boundaries

- 未实现任何业务代码、Skill 运行时、manifest loader 或同步程序。
- 未迁移任何现有仓库或游戏项目。
- 未修改 `feishu-doc-mcp` / `document-assistant`。
- 未加入任何非游戏领域内容。

## [0.1.0] - 2026-08-26

### Added

- 初始化 AI 协作总控仓库，不包含业务代码。
- 建立 RFC、ADR、Skills、Workflows、Templates、Standards、Projects、Handoff 和 Bootstrap 目录。
- 建立 README、AI Team、Architecture、Roadmap、Contributing 和 Agent 入口文档。
- 建立 Workspace Charter、Document Assistant、AI Skill System 三份初始 RFC。
- 建立 ChatGPT 与 Codex 固定交接文档。
- 定义项目 Context、Memory、Workflow、Status 四件套及可复制模板。
- 建立 RFC、ADR、项目和交接模板，以及各目录入口说明。

### Boundaries

- 未实现任何业务代码。
- 未迁移或修改任何现有项目仓库。
- 未修改 `feishu-doc-mcp` / `document-assistant`。
