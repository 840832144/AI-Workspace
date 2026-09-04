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

本 Task 已获 User 批准，但执行分阶段授权：第一阶段只做当前笔记本的只读 Readiness Audit；任何安装、BlueStacks/Windows 配置变更、专用实例创建、Huuuge 登录、Collector 启动或 Reliability Hardening 实施都必须等待下一次 User 明确批准。

## Decision and current gate

- P0 Reliability Hardening 已由 Decision proposal 转为正式 canonical Task。
- Phase A - Laptop Readiness Audit：已完成，只读检查结果见 [`tasks/support/TASK-0027/LAPTOP_READINESS_AUDIT.md`](support/TASK-0027/LAPTOP_READINESS_AUDIT.md)。
- Environment Change Approval Gate：当前停在此 Gate，等待 User 审批拟安装软件、配置动作、目标路径、影响和回退方案。
- 未通过该 Gate 前，不进入安装、Root、Collector、Spin 或业务运行。

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

### Phase B - Approved environment preparation（待 User 审批）

User 批准具体变更后，才允许：

1. User 决定保留或回退审计期间在本机完成的 BlueStacks 5 安装；若保留，先核验来源、签名、版本、安装/data 路径和现有 hypervisor 兼容性，不重复安装；
2. 新建本机专属的 Pie 64-bit 实例，显示名固定为 `HuuugeResearch`，记录本机新生成的 internal instance ID；
3. 只在专用实例启用 ADB，验证唯一目标 serial/port；
4. 由 User 完成 Huuuge Casino 与公司 SVN 的登录/认证；
5. 把正式 SVN 包放入 User 批准的本机路径，记录版本和 hash，但不启动 Collector；
6. 运行不启动 Collector 的静态 preflight，确认依赖、端口、路径和权限边界。

不得复制台式机的 BlueStacks 数据目录、VHD、实例 ID、ADB port、Root 状态、Collector `.local`、账号或绝对路径。`Pie64_1` 只属于历史证据，不预设为本机 identity。

### Phase C - Reliability Hardening（Phase B 验收后另行执行）

最小目标仅围绕“笔记本汇报实机演示”建立：

- 可复核的 preflight 与目标实例/package/foreground gate；
- Collector READY 证据，而不是仅凭进入 User 操作阶段推断 READY；
- 启动失败、临时 SSL 捕获、ADB/forward、进程和 cleanup 的显式错误；
- 单一短入口、停止/回退路径和最少现场操作；
- 不改变 Huuuge schema、报告范围、游戏请求、返回、余额或奖励。

具体实现文件、仓库和测试矩阵必须在 Phase B 环境 identity 固定后写入本 Task，再进入修改。

### Phase D - Laptop live-demo acceptance（未来 Gate）

- User 负责登录和游戏内正常操作；
- Codex 只执行已批准的一键入口、读取脱敏状态并停止/清理；
- 演示不得包含 Auto Spin、购买、充值、请求/返回修改或后台挂机；
- 只有完整 preflight、READY、User 操作边界、finalize、cleanup 和残留检查均有本轮证据时，才可将演示标记为成功。

## Current audit result

- 已具备：Windows 11 x64、Hypervisor 运行、31.7 GB RAM、Git、Python、SVN CLI/TortoiseSVN、AI-Workspace latest main、Document Assistant healthcheck；最终复核还发现 BlueStacks 5 `5.22.262.1001` runtime 与 `HD-Adb.exe` 已落在 `C:\Program Files\BlueStacks_nxt`，下载器与关键已安装 EXE 的 Authenticode 均为 `Valid / Now.gg, INC`，但本轮未启动 runtime。
- 缺失：BlueStacks data/config 与专用 `HuuugeResearch`、可验证的目标 ADB serial/port、Huuuge 实装 identity、正式 `HuuugeCollector` 本机包。审计期间先出现两个 Installer 进程，随后进程退出并出现 BlueStacks/BlueStacks Services 卸载项；Codex 未启动、点击、停止或安装这些组件。
- 冲突风险：MuMu 已安装且相关进程/服务正在运行；NoxPlayer 已安装。它们本轮未被停止或修改。
- 路径事实：当前权威 Workspace 是 `D:\AI-Workspace`；旧指南的 `C:\AI-Workspace` 不能自动套用。本机正式包目标路径也尚未获批。
- 当前结论：Phase A 完成；环境未达到演示 Ready，不能启动 Reliability Hardening 或业务运行。

## Non-goals

- 本阶段 Codex 不安装、更新或卸载任何软件；审计期间出现的并发外部安装只记录事实，不继续操作；
- 不启停 BlueStacks、MuMu、Nox、ADB daemon、Collector、Frida server 或游戏；
- 不创建/克隆/删除模拟器实例，不改 Windows 可选功能、启动项、服务、驱动、PATH 或防火墙；
- 不 Root、不注入、不执行 Spin、不登录游戏、不访问账号数据；
- 不复制台式机配置、VHD、实例、采集 Session、Raw、Secret 或 `.local`；
- 不修改 Huuuge 业务仓库、Collector 实现、schema、Hook、serializer 或飞书文档；
- 不把“Hypervisor 已运行”误写成“BlueStacks 已兼容/实例已可用”。

## Deliverables

- canonical Task：本文件；
- 第一阶段审计：[`LAPTOP_READINESS_AUDIT.md`](support/TASK-0027/LAPTOP_READINESS_AUDIT.md)；
- 更新 Huuuge Project Status、Product Roadmap、Workspace Progress、CHANGELOG 和两个 Handoff；
- Task Registry 由正式扫描重建并通过 validator；
- User 批准后，在本 Task 中补充精确环境变更清单和 Phase B 实施证据。

## Acceptance

### Phase A acceptance（本次）

1. 只读识别 BlueStacks/虚拟化/ADB/实例/演示依赖/现有工作区；
2. 明确区分“已具备”“缺失”“待审批动作”和“当前不能验证”；
3. 不把台式机路径、实例 ID 或旧 READY 状态当作本机事实；
4. 给出安装/配置成功标准和逐项回退方案；
5. 没有启动模拟器、Collector、Root、Frida 或 Spin，没有修改业务环境。

### Environment-ready acceptance（User 批准后）

1. BlueStacks 实际版本、安装/data 路径和 Hyper-V 兼容模式可回读；
2. 新建且仅使用本机 `HuuugeResearch`，internal ID、Pie 64-bit、ABI、资源配置和备份边界明确；
3. ADB 只命中目标实例，serial/port 稳定，无其他模拟器设备或 5037 冲突；
4. Huuuge package/version/ABI/foreground 由实机回读；
5. 正式 SVN 包版本/hash、Python 依赖和静态 preflight 通过，但 Collector 仍未启动；
6. 日常实例、其他模拟器、现有 Workspace 和 User 文件未改变；
7. 回退步骤经过非破坏性验证，所有环境变更均有 User 授权记录。

## Safety

- User 决定所有安装、管理员确认、Windows/BlueStacks 配置、游戏/SVN 登录与业务运行；
- 任何环境变更前先列出目标、影响、备份/恢复和停止条件，再等待批准；
- 只修改本机新建的 `HuuugeResearch`，不使用或修改日常模拟器实例；
- Secret、账号、完整日志、Raw、APK/SO 和本机私有配置不进入 Git、Handoff 或聊天；
- 发现 identity、路径、端口、权限或回退边界不唯一时 fail closed。

## Validation

- Task allocator：remote-CAS reservation `TASK-0027`，state `pending-main`；token 只留本机受控状态，不写 Git/Handoff；
- Phase A 使用系统、注册表、文件、进程、服务和命令版本的只读检查；
- `feishu_healthcheck` 仅记录 token/API/Drive 三项安全状态，不记录凭据值；
- Registry 已重建并验证为 14 canonical / 0 collision / valid；
- Task 23/23、Context 13/13、Memory 44/44 回归通过；Context refresh 为 72 sources / 0 broken link / 0 secret issue；
- TASK-0027 定向断言 12/12、changed-document scan 13 files / 0 unexpected path / 0 broken link / 0 secret assignment 通过；Workspace Doctor 与 `git diff --check` 通过；
- Handoff 必须记录 `Subagents: none / OFF`。

## Handoff

提交并 push 本分支后停止。唯一下一步是 User 决定保留并批准核验当前 BlueStacks 安装，或批准按回退清单卸载本轮新出现的 BlueStacks/BlueStacks Services；随后再审批 [`LAPTOP_READINESS_AUDIT.md`](support/TASK-0027/LAPTOP_READINESS_AUDIT.md) 中的其余环境变更。未获批准不启动 BlueStacks，也不进入 Reliability Hardening。
