# TASK-0027 — Huuuge Research Laptop Reliability Hardening

- Status: Accepted
- Project key: HUUUGE
- Human alias: HUUUGE-RESEARCH-LAPTOP-RELIABILITY
- Owner: User / ChatGPT
- Executor: Codex
- Priority: P0
- Date: 2026-09-04
- Updated: 2026-09-04
- User authorization: User approved P0 Reliability Hardening, Scheme C, Phase D engineering deployment, the presentation rehearsal, and final rehearsal acceptance
- Allocation method: `task_cli.py next` / remote-CAS reservation
- Allocation relationship: new
- Related tasks: TASK-0019

## Goal

建立长期可用、可维护、可回退的 Huuuge Research Laptop，使本机 BlueStacks 研究实例满足正式 Collector 1.0.1 的 `Pie64_1 / 127.0.0.1:5565 / uid=0(root)` 运行契约，并用最小生命周期证明 `Start → READY → short Session → Stop → Finalize`。

本 Task 按分阶段授权执行：Phase A 只读 Readiness Audit、Phase B BlueStacks Environment-ready、Phase C 正式包/static preflight、Phase D 长期环境部署与汇报彩排均已完成并由 User 接受。没有修改 Collector 业务逻辑或六字段 schema。

## Decision and current gate

- P0 Reliability Hardening 已由 Decision proposal 转为正式 canonical Task。
- Phase A - Laptop Readiness Audit：已完成，只读检查结果见 [`tasks/support/TASK-0027/LAPTOP_READINESS_AUDIT.md`](support/TASK-0027/LAPTOP_READINESS_AUDIT.md)。
- Phase B - BlueStacks Environment-ready：User 批准保留当前安装、验证启动/退出/重启、创建本机 Fresh Pie 64-bit `HuuugeResearch`、启用 ADB，并在确认 5555 冲突后单独批准改用 5585；本阶段已完成，验收见 [`ENVIRONMENT_READY_ACCEPTANCE.md`](support/TASK-0027/ENVIRONMENT_READY_ACCEPTANCE.md)。
- Phase C - Collector package/static preflight：User 已批准。正式包已从公司 SVN 取得到 `C:\HuuugeCollector`，版本、SVN revision、source revision、ZIP/manifest hash 和依赖已核验；结论见 [`PHASE_C_PREFLIGHT_ACCEPTANCE.md`](support/TASK-0027/PHASE_C_PREFLIGHT_ACCEPTANCE.md)。
- Phase D - Huuuge Research Laptop Setup：User 选择 Scheme C 并批准工程部署，使笔记本匹配正式 contract。研究 clone、5565、Root、Frida/Gadget 与正式生命周期已完成，见 [`PHASE_D_LAPTOP_SETUP.md`](support/TASK-0027/PHASE_D_LAPTOP_SETUP.md)。
- Presentation rehearsal：User 批准后，正式入口创建 Session `20260904_142442`；READY 时 RPC/decoded `63/63`，User 按最小彩排脚本完成操作后为 `123/123`。Stop/Finalize 与最终 cleanup 通过，User 随后明确给出 `彩排 Accepted`。
- Current Gate：TASK-0027=`Accepted`，`Huuuge Research Laptop Ready = Yes`，汇报彩排已通过。正式汇报仍是单独 Session Gate，不由本 Task 自动启动。

## Scope

### Phase A - Laptop Readiness Audit（本次已完成）

只读检查当前笔记本的：

- Windows、CPU、内存、GPU、磁盘和虚拟化/Hypervisor 状态；
- BlueStacks 安装、服务、进程、静态配置与实例目录；
- ADB 命令、BlueStacks ADB、ADB 进程与 5037 监听；
- 专用 `HuuugeResearch` 实例是否存在；
- Git、Python、TortoiseSVN/SVN CLI、Document Assistant；
- 当前 AI-Workspace、正式采集器包和 Huuuge 相关工作区；
- 可能影响 BlueStacks 的其他 Android 模拟器，只记录状态，不停止、不卸载。

### Phase B - Approved BlueStacks environment preparation（已完成）

User 已批准并完成以下本机环境动作：

1. 保留并核验 BlueStacks 5 `5.22.262.1001`、Now.gg 有效签名、官网下载 campaign、程序/data 路径和当前 hypervisor/VMP 启动兼容性；未重复安装；
2. 使用本次安装本机生成的唯一 internal ID `Pie64`，显示名固定为 `HuuugeResearch`；未 clone 其他实例；
3. 仅为该实例启用 ADB；默认 5555 被 Windows excluded range 覆盖后，User 单独批准本机端口 5585，验证唯一 `127.0.0.1:5585`；
4. User 完成 Huuuge 安装/登录与游戏启动；Codex 只读回读 package/version/ABI/foreground identity，不执行游戏操作；
5. 正常退出并重启复现后，结束时关闭 BlueStacks 与本轮 ADB client，保持 5037/5585 无残留 listener。

不得复制台式机的 BlueStacks 数据目录、VHD、实例 ID、ADB port、Root 状态、Collector `.local`、账号或绝对路径。`Pie64_1` 只属于历史证据，不预设为本机 identity。

### Phase C - Collector package preflight and Reliability Hardening（静态完成，动态阻断）

User 已批准本 Gate，实际完成：

- Installer URL：`trunk/HuuugeCollector/release/HuuugeCollector_Installer.zip`；文件 last-changed revision `6624`，SVN repository/working-copy revision `6701`；
- 安装器版本 `1.0.1`，manifest 声明 clean source revision `77e0339fa73da2ab02fcbb6cff125604a9a8abd5`；ZIP SHA-256 `ACAC144B3CB58E861345D33F6CEEB95ACA0E1CE3CF8B49211C6E7AFB260A958A`，下载件与工作副本 release 文件一致，manifest allowlist `3/3`；
- 正式工作副本路径 `C:\HuuugeCollector`，SVN status clean；PowerShell parser `9/9`、Python AST `5/5`；
- 依赖声明为 Python、SVN、`frida`、`frida-tools`、`protobuf`、`lz4`、`grpcio-tools`，并要求固定 ADB、root Frida server、Gadget/config 与专用实例；
- 启动前 fail-closed：本机没有 `C:\platform-tools\adb.exe`、没有固定 Frida server、没有 `Pie64_1`；正式 controller 固定 `127.0.0.1:5565` 且启动路径调用 `Assert-ResearchRoot` 验证 `uid=0(root)`。本机仅有 `Pie64 / HuuugeResearch / 127.0.0.1:5585 / Root OFF`。

因此未启动 BlueStacks、Collector、Frida 或 Session，没有伪造 `READY`、Stop/Finalize 结果。继续动态验收需要扩大为 Collector 实现适配或改变 Root/实例边界，必须由 User 重新决策。

### Phase D - Huuuge Research Laptop Setup（已完成）

- 保留原 `Pie64`，删除经 User 批准的空白 `Pie64_1`，再克隆当前已安装 Huuuge 的本机实例；不复制台式机黑盒配置；
- 将研究 clone 对齐为 `Pie64_1 / HuuugeResearch / 127.0.0.1:5565`，Root 只在研究实例生效；
- 安装固定 ADB 与 Frida 依赖，部署 ARM64 Gadget/config，不改 Collector 实现；
- 以 `-ValidationOnly` 验证 Start、strict READY、15 秒无操作 Session、clean Stop 与 Finalize；
- 不执行 Spin、Win/Reward、RTP/Bet 分析，不新增字段，不触碰 MuMu/Nox。

## Current environment result

- Environment-ready：BlueStacks 5 `5.22.262.1001` / Services `3.0.9`；program `C:\Program Files\BlueStacks_nxt\`；data `D:\BS\BlueStacks_nxt\Engine\`。原 `Pie64 / HuuugeResearch-PhaseB / 5585 / Root OFF` 保留；长期研究实例为 `Pie64_1 / HuuugeResearch / 5565 / Root ON`。
- Huuuge identity：User 完成安装/登录；package `com.huuuge.casino.slots`、versionName `12.08.27100`、versionCode `1786533240`、primary ABI `arm64-v8a` 已只读回读。Codex 未安装、登录或执行游戏操作。
- ADB 冲突已显式处理：Phase B 的 5585 保留；Phase D 发现 Windows 动态 excluded range 覆盖正式 5565，经 User 单独批准后建立 5565 administered exclusion。最终 `127.0.0.1:5565` listener count 1，正式 controller 使用精确 TCP serial。
- 共存结果：MuMu/Nox 保持原状；没有停止、Root 或重配。
- 路径事实：当前权威 Workspace 是 `D:\AI-Workspace`；正式 Installer 声明的本机 Collector 默认路径为 `C:\HuuugeCollector`，本轮已按批准 Gate 取得 clean SVN working copy。
- Phase C package/static preflight：正式 SVN 包 `1.0.1` 已取得并通过来源/hash/manifest/parser 检查；当时发现的 contract mismatch 已由 User 批准的 Scheme C 环境迁移解决，没有修改 Collector。
- Phase D lifecycle：Session `20260904_135724` 达到 strict `READY`；15 秒短 Session 为 RPC `61` / decoded `61`；manifest `stopped`、controller `finalized`。随后本轮 Collector、root Frida process、Huuuge process 与 ADB forward 均停止；长期 Gadget/config 保留。
- Presentation rehearsal：Session `20260904_142442` 从 READY RPC/decoded `63/63` 增至 User 操作完成后的 `123/123`；Stop exit `0`，manifest=`stopped`、controller=`finalized`、active state absent。Frida/game PID、ADB forward、host capture process 与临时 residual 最终均为 0，Gadget/config 保留。
- 当前结论：`Huuuge Research Laptop Ready = Yes`。该结论不把正式 RC4 `Pending` 或历史 User 实跑 `Failed/Invalid` 改写为独立策划 First Run 通过；Bet/RTP 保持 `Unsupported`。

## Non-goals

- 不修改 Windows Hypervisor/VMP、启动项、驱动、防火墙、MuMu 或 Nox；
- 不删除原 `Pie64` 或 User 数据；研究 clone 与 Root 只用于 Huuuge；
- 除 User 在获批彩排中手动完成 3 次单次 Spin 外，Codex 不执行游戏操作；不使用 Auto Spin，不购买、充值、修改请求/返回、执行 Win/Reward、RTP/Bet 分析或后台挂机；
- 不复制台式机配置、VHD、实例、采集 Session、Raw、Secret 或 `.local`；
- 不修改 Huuuge 业务仓库、SVN 工作副本、Collector 实现、schema、Hook、serializer 或飞书文档；
- 不把生命周期 Ready 误写成 RC4 独立 First Run 已通过。

## Deliverables

- canonical Task：本文件；
- 第一阶段审计：[`LAPTOP_READINESS_AUDIT.md`](support/TASK-0027/LAPTOP_READINESS_AUDIT.md)；
- 第二阶段验收：[`ENVIRONMENT_READY_ACCEPTANCE.md`](support/TASK-0027/ENVIRONMENT_READY_ACCEPTANCE.md)；
- 第三阶段静态验收：[`PHASE_C_PREFLIGHT_ACCEPTANCE.md`](support/TASK-0027/PHASE_C_PREFLIGHT_ACCEPTANCE.md)；
- 第四阶段长期环境部署：[`PHASE_D_LAPTOP_SETUP.md`](support/TASK-0027/PHASE_D_LAPTOP_SETUP.md)；
- 更新 Huuuge Project Status、Product Roadmap、Workspace Progress、CHANGELOG 和两个 Handoff；
- Task Registry 由正式扫描重建并通过 validator；
- Phase C 正式包路径、static preflight、缺陷和动态 Stop Gate 已写入本 Task 与第三阶段验收。
- Phase D 配置、问题、恢复方式和生命周期结果已写入第四阶段记录。

## Acceptance

### Phase A acceptance（本次）

1. 只读识别 BlueStacks/虚拟化/ADB/实例/演示依赖/现有工作区；
2. 明确区分“已具备”“缺失”“待审批动作”和“当前不能验证”；
3. 不把台式机路径、实例 ID 或旧 READY 状态当作本机事实；
4. 给出安装/配置成功标准和逐项回退方案；
5. 没有启动模拟器、Collector、Root、Frida 或 Spin，没有修改业务环境。

### Environment-ready acceptance（本次通过）

1. BlueStacks 实际版本、发行 campaign、签名、安装/data 路径和当前 Hypervisor/VMP 启动结果已回读；
2. 仅使用本机 fresh `HuuugeResearch`，internal ID `Pie64`、Pie 64-bit、ABI、资源和 data boundary 明确；
3. ADB 只命中 `127.0.0.1:5585`，唯一 listener、direct transport 与 5037 无争用已验证；
4. Huuuge package/version/ABI/foreground 曾由 User 启动后的实机只读回读；
5. MuMu/Nox、Workspace 和 User 文件未改变，最终 BlueStacks/ADB client 已退出；
6. 回退在另一份 copy 上恢复 Baseline 5/5；live config 保持批准的 5585；
7. Phase B 验收时正式 SVN 包和 static preflight 转入下一 Gate，Collector 当时仍未启动；Phase C 结果另见第三阶段验收。

### Phase C acceptance（静态通过，动态阻断）

1. 正式包 URL、SVN revision、version、source revision、ZIP SHA-256、manifest allowlist 与依赖已核验；
2. `C:\HuuugeCollector` 为 clean SVN working copy；PowerShell/Python 静态解析通过；
3. Root 保持 OFF，未修改 Collector 业务逻辑、Hook/serializer 或字段；
4. 静态 preflight 明确阻断 `Pie64_1 / 5565 / uid=0(root)` 与 `Pie64 / 5585 / Root OFF` 的 contract mismatch；
5. 因继续需要扩大范围，未执行启动、READY、短 Session、Stop 或 Finalize；Demo Ready=`No`。

### Phase D acceptance（通过）

1. 原 `Pie64 / 5585 / Root OFF` 保留；独立研究 clone 对齐为 `Pie64_1 / 5565 / Root ON`，MuMu/Nox 未改变；
2. 正式 Collector 1.0.1 的 ADB、Root、Frida server 与 ARM64 Gadget/config preflight 全部通过；
3. `Start → READY → 15 秒无操作 Session → Stop → Finalize` 全链通过，RPC/decoded 为 `61/61`；
4. Stop 后 manifest=`stopped`、controller=`finalized`、active state absent；run-owned process、Frida server、forward 与临时 residual 均为 0；
5. 没有 Spin、Win/Reward、RTP/Bet 分析、字段扩展或 Collector 业务修改；
6. 必要变更均有“修改内容 / 修改原因 / 如何恢复”；Root/Gadget 回退已在另一份 copy 验证，live 环境保持长期研究状态。

### Presentation rehearsal acceptance（通过）

1. User 明确批准进入汇报彩排，并在 Huuuge 大厅就位后由 Codex 启动正式 Collector；
2. Session `20260904_142442` 达到 strict READY，READY 时 RPC/decoded 为 `63/63`；
3. User 按最小彩排脚本完成游戏内操作后，RPC/decoded 为 `123/123`；本 Task 不对 Spin、Win/Reward、Bet 或 RTP 作业务分析；
4. Stop/Finalize 成功，manifest=`stopped`、controller=`finalized`、active state absent；
5. 精确 cleanup 后 Frida/game PID 为空，ADB forward、host capture process 与临时 residual 均为 0；长期 Gadget/config 保留；
6. User 明确给出 `彩排 Accepted`，TASK-0027 收口为 `Accepted`。

## Safety

- User 决定所有安装、管理员确认、Windows/BlueStacks 配置、游戏/SVN 登录与业务运行；
- 任何环境变更前先列出目标、影响、备份/恢复和停止条件，再等待批准；
- 只修改本机新建的 `HuuugeResearch`，不使用或修改日常模拟器实例；
- Secret、账号、完整日志、Raw、APK/SO 和本机私有配置不进入 Git、Handoff 或聊天；
- 发现 identity、路径、端口、权限或回退边界不唯一时 fail closed。

## Validation

- Task allocator：remote-CAS reservation `TASK-0027`，state `pending-main`；token 只留本机受控状态，不写 Git/Handoff；
- Phase A 使用系统、注册表、文件、进程、服务和命令版本的只读检查；
- Phase B 使用 BlueStacks UI、注册表/config、Player/Core 日志、listener ownership 与只读 direct ADB transport probe；不保存账号或完整日志；
- Phase C 只使用 SVN info/checkout/status、ZIP/manifest hash、PowerShell parser、Python AST 和配置/路径静态检查；没有运行 Bootstrap、controller 或 Collector；
- BlueStacks 启动/退出/重启复现通过；`127.0.0.1:5585` listener count 1、5037 count 0；ADB probe 回读 Android 9、shell uid 2000、Huuuge package/version/ABI；
- 默认 5555 冲突与两次 `HD-Adb.exe` 长等待均显式记录，run-owned PID 精确清理后 `HD-Adb=0`、5037=0；
- config Baseline 5/5、Modified 7/7、rollback copy Baseline 5/5；live config 与 `MODIFIED_FILE` SHA-256 一致并保持批准状态；
- `feishu_healthcheck` 仅记录 token/API/Drive 三项安全状态，不记录凭据值；
- Registry 已重建并验证为 14 canonical / 0 collision / valid；
- Task 23/23、Context 13/13、Memory 44/44 回归通过；Context refresh 为 73 sources / 0 broken link / 0 secret issue；
- Phase C 定向断言 20/20、changed-document allowlist 12/12、Task 23/23、Context 13/13、Memory 44/44、Registry 14 canonical / 0 collision / valid 通过；Context refresh 74 sources / 0 broken link / 0 secret issue，Workspace Doctor 与 `git diff --check` 通过；
- Phase D formal bootstrap 无 action item；正式 Start exit `0`、READY RPC/decoded `61/61`，Stop exit `0`，manifest stopped、last finalized、active absent、finalized evidence present；
- final cleanup：host capture process `0`、guest temporary residual `0`、Frida server stopped、Huuuge stopped、ADB forward empty；5565 listener count `1`，`Pie64` Root flag `0`、`Pie64_1` Root flag `1`；
- 本机 rollback fixture 从 MODIFIED 恢复为 pre-root-live BASELINE，SHA-256 完全一致；live MODIFIED state 保持不变；
- Phase D 仓库回归：Task 23/23、Context 13/13、Memory 44/44；Registry 14 canonical / 0 collision / valid；Context refresh 75 sources / 0 broken link / 0 secret issue；changed-document scan 13 files / 0 broken link / 0 secret assignment；Workspace Doctor 与 `git diff --check` 通过；
- 汇报彩排：Session `20260904_142442` READY `63/63`，User 操作后 `123/123`，Stop/Finalize exit `0`；最终 active absent、Frida/game PID 空、ADB forward `0`、host capture process `0`、临时 residual `0`、Gadget/config `2`；User `彩排 Accepted`；
- Accepted closeout：Task 23/23、Context 13/13、Memory 44/44、Registry 14 canonical / 0 collision / valid；Context refresh 75 sources / 0 broken link / 0 secret issue；changed-document scan 12 files / 0 broken link / 0 secret assignment；Workspace Doctor 与 `git diff --check` 通过；
- Handoff 必须记录 `Subagents: none / OFF`。

## Handoff

提交并 push 本分支后停止。TASK-0027 已 Accepted；唯一下一步是正式汇报前由 User 明确开启当次 Session Gate，不由本 Task 自动运行 Collector。
