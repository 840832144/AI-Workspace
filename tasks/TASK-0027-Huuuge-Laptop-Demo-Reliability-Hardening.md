# TASK-0027 — Huuuge Laptop Demo Reliability Hardening

- Status: In Progress
- Project key: HUUUGE
- Human alias: HUUUGE-LAPTOP-DEMO-RELIABILITY
- Owner: User / ChatGPT
- Executor: Codex
- Priority: P0
- Date: 2026-09-04
- Updated: 2026-09-04
- User authorization: User approved P0 Reliability Hardening for the minimum “笔记本汇报实机演示” scope
- Allocation method: `task_cli.py next` / remote-CAS reservation
- Allocation relationship: new
- Related tasks: TASK-0019

## Goal

把 Huuuge First Run 从“正式 RC4 `Pending`、User 实跑 `Failed/Invalid`、正式 Collector READY 未被可复核证明”的状态，收敛为适合笔记本现场汇报的最小、可复查、可回退演示路径。

本 Task 已获 User 批准，但执行分阶段授权：Phase A 只读 Readiness Audit 与 Phase B BlueStacks Environment-ready 已完成；正式 Collector 包、静态 preflight、Reliability Hardening、Collector 启动和现场演示分别受后续 Gate 约束。

## Decision and current gate

- P0 Reliability Hardening 已由 Decision proposal 转为正式 canonical Task。
- Phase A - Laptop Readiness Audit：已完成，只读检查结果见 [`tasks/support/TASK-0027/LAPTOP_READINESS_AUDIT.md`](support/TASK-0027/LAPTOP_READINESS_AUDIT.md)。
- Phase B - BlueStacks Environment-ready：User 批准保留当前安装、验证启动/退出/重启、创建本机 Fresh Pie 64-bit `HuuugeResearch`、启用 ADB，并在确认 5555 冲突后单独批准改用 5585；本阶段已完成，验收见 [`ENVIRONMENT_READY_ACCEPTANCE.md`](support/TASK-0027/ENVIRONMENT_READY_ACCEPTANCE.md)。
- Current Gate：等待 User 审批 Phase C 的正式 Collector 包路径/取得方式、静态 preflight 与最小 Reliability Hardening；获批前不启动 Collector、Root、Frida 或 Spin。

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

### Phase C - Collector package preflight and Reliability Hardening（等待 User Gate）

最小目标仅围绕“笔记本汇报实机演示”建立：

- 从公司 SVN 取得 User 批准版本到 User 批准的本机路径，记录 revision/version/hash/依赖，只运行不会启动 Collector 的静态 preflight；
- 可复核的 preflight 与目标实例/package/foreground gate；
- Collector READY 证据，而不是仅凭进入 User 操作阶段推断 READY；
- 启动失败、临时 SSL 捕获、ADB/forward、进程和 cleanup 的显式错误；
- 单一短入口、停止/回退路径和最少现场操作；
- 不改变 Huuuge schema、报告范围、游戏请求、返回、余额或奖励。

具体实现文件、仓库和测试矩阵必须在 User 批准本 Gate 后写入本 Task，再进入修改。

### Phase D - Laptop live-demo acceptance（未来 Gate）

- User 负责登录和游戏内正常操作；
- Codex 只执行已批准的一键入口、读取脱敏状态并停止/清理；
- 演示不得包含 Auto Spin、购买、充值、请求/返回修改或后台挂机；
- 只有完整 preflight、READY、User 操作边界、finalize、cleanup 和残留检查均有本轮证据时，才可将演示标记为成功。

## Current environment result

- Environment-ready：BlueStacks 5 `5.22.262.1001` / Services `3.0.9`；program `C:\Program Files\BlueStacks_nxt\`；data `D:\BS\BlueStacks_nxt\Engine\`；唯一本机 `Pie64 / HuuugeResearch`；ADB `127.0.0.1:5585`；Root OFF；启动、退出、重启和最终关闭均已复现。
- Huuuge identity：User 完成安装/登录；package `com.huuuge.casino.slots`、versionName `12.08.27100`、versionCode `1786533240`、primary ABI `arm64-v8a` 已只读回读。Codex 未安装、登录或执行游戏操作。
- ADB 冲突已显式处理：Windows TCP excluded range `5485–5584` 覆盖默认 5555；User 批准改用 5585。唯一 Player listener 和 direct ADB transport probe 通过；5037 无争用。BlueStacks 随附 `HD-Adb.exe` 在 excluded-port 扫描上发生长等待，精确清理后无残留，作为 Phase C Reliability Hardening 输入保留。
- 共存结果：MuMu 继续运行、Nox 保持原状；未确认二者与 5585/5037 冲突，因此没有停止或修改。
- 路径事实：当前权威 Workspace 是 `D:\AI-Workspace`；旧指南的 `C:\AI-Workspace` 不能自动套用。本机正式包目标路径也尚未获批。
- 当前结论：Phase B BlueStacks Environment-ready 通过；正式 Collector package/static preflight 与 Reliability Hardening 尚未获批，不能启动 Collector 或现场演示。

## Non-goals

- 不安装、更新或卸载任何软件；
- 只启停已批准的 BlueStacks `HuuugeResearch` 并验证 ADB；不停止或修改 MuMu/Nox；
- 不 clone/删除模拟器实例，不改 Windows 可选功能、启动项、服务、驱动、PATH 或防火墙；
- 不 Root、不注入、不执行 Spin；游戏安装、登录和正常启动只由 User 完成；Codex 不访问账号数据；
- 不复制台式机配置、VHD、实例、采集 Session、Raw、Secret 或 `.local`；
- 不修改 Huuuge 业务仓库、Collector 实现、schema、Hook、serializer 或飞书文档；
- 不把“Hypervisor 已运行”误写成“BlueStacks 已兼容/实例已可用”。

## Deliverables

- canonical Task：本文件；
- 第一阶段审计：[`LAPTOP_READINESS_AUDIT.md`](support/TASK-0027/LAPTOP_READINESS_AUDIT.md)；
- 第二阶段验收：[`ENVIRONMENT_READY_ACCEPTANCE.md`](support/TASK-0027/ENVIRONMENT_READY_ACCEPTANCE.md)；
- 更新 Huuuge Project Status、Product Roadmap、Workspace Progress、CHANGELOG 和两个 Handoff；
- Task Registry 由正式扫描重建并通过 validator；
- User 批准 Phase C 后，在本 Task 中补充正式包路径、static preflight、实现文件和测试矩阵。

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
7. 正式 SVN 包和 static preflight 转入下一 Gate，Collector 仍未启动。

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
- BlueStacks 启动/退出/重启复现通过；`127.0.0.1:5585` listener count 1、5037 count 0；ADB probe 回读 Android 9、shell uid 2000、Huuuge package/version/ABI；
- 默认 5555 冲突与两次 `HD-Adb.exe` 长等待均显式记录，run-owned PID 精确清理后 `HD-Adb=0`、5037=0；
- config Baseline 5/5、Modified 7/7、rollback copy Baseline 5/5；live config 与 `MODIFIED_FILE` SHA-256 一致并保持批准状态；
- `feishu_healthcheck` 仅记录 token/API/Drive 三项安全状态，不记录凭据值；
- Registry 已重建并验证为 14 canonical / 0 collision / valid；
- Task 23/23、Context 13/13、Memory 44/44 回归通过；Context refresh 为 73 sources / 0 broken link / 0 secret issue；
- TASK-0027 定向断言 18/18、changed-document scan 13 files / 0 unexpected path / 0 broken link / 0 secret assignment / 0 stale current state 通过；Workspace Doctor 与 `git diff --check` 通过；
- Handoff 必须记录 `Subagents: none / OFF`。

## Handoff

提交并 push 本分支后停止。唯一下一步是 User 审批 Phase C：正式 Collector 包的本机路径/取得方式、版本/hash/依赖/static preflight，以及最小 Reliability Hardening 实施。未获批准不启动 BlueStacks、Root、Frida、Collector 或 Spin。
