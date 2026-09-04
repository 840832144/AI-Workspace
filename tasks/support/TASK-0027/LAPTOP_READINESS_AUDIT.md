# TASK-0027 — 笔记本汇报实机演示 Readiness Audit

- Date: 2026-09-04
- Host role: 笔记本汇报实机演示
- Method: 只读检查；未安装、启停或修改任何软件、服务、模拟器、实例、ADB、Collector、Root 或游戏状态
- Git baseline: `AI-Workspace/main@1dd6de3e244858c44b716cacd72961ea9419f564`
- Audit markers: `BlueStacks 5 runtime: Present-unverified` / `HuuugeResearch: Missing` / `Document Assistant: Available`
- Path rule: `Do not reuse desktop path`

## 结论

当前笔记本具备 Windows/硬件、Git、Python、SVN 与 Document Assistant 基础。审计过程中先检测到两个 BlueStacks Installer 进程；最终只读回查时安装器已退出，BlueStacks 5 `5.22.262.1001` runtime 与 `HD-Adb.exe` 已出现在 `C:\Program Files\BlueStacks_nxt`，并出现 BlueStacks 与 BlueStacks Services 卸载项。下载器、`HD-Player.exe`、Multi-instance Manager 和 BlueStacks Services 的 Authenticode 均为 `Valid / Now.gg, INC`。Codex 未启动、点击、停止或安装这些组件，也未启动 BlueStacks。当前仍缺 **data/config、专用 `HuuugeResearch`、可验证 ADB 目标、Huuuge 实装 identity 和正式 Collector 本机包**，因此环境状态仍是 **Not Ready / awaiting approved environment changes**。

本轮只完成事实盘点。`All actions below require User approval`：下列安装、配置、停止其他模拟器、创建实例、启用 ADB、选择正式包路径和登录动作均未执行。

## 已具备项

| 项目 | 本机事实 | 判断 |
| --- | --- | --- |
| Windows | Windows 11 家庭版 x64，build 26200 | 满足 BlueStacks 5 Windows 11 基础平台 |
| CPU / RAM | Intel Core i7-13700H，14 核 / 20 逻辑处理器；31.7 GB RAM | 容量充足 |
| GPU | Intel Iris Xe + AMD Radeon RX 7600M XT；设备状态均为 OK | 具备双显卡基础；安装后仍需现场验证实际渲染器和驱动兼容性 |
| 磁盘 | C: 可用 27.2 GB；D: 可用 214.0 GB | 高于 BlueStacks 官方 5 GB 最低值；正式安装前仍需确定程序/data/备份路径，优先利用 D: 空间 |
| Hypervisor | `HypervisorPresent=True`；`systeminfo` 报告已检测到 hypervisor；`hypervisorlaunchtype=Auto`；VirtualMachinePlatform=Enabled；VBS status=2 | Windows hypervisor 当前运行；无需先改虚拟化设置 |
| 权限 | 当前审计进程为 elevated；本机存在 Hyper-V Administrators 组，当前用户不在该组 | 安装时可能需要管理员确认；是否加入组必须单独批准和重启后验证 |
| Git | 2.55.0.windows.3 | 可用 |
| Python | `python` 3.11.15；`py` 可发现 3.12 与 3.11 | 可用；正式 SVN 包到位后再核对它自己的版本/依赖约束 |
| SVN | SVN CLI 1.14.2；TortoiseSVN 1.14.5.29465，command line tools 存在 | 客户端可用；公司 SVN 认证和正式包访问未在本轮触发 |
| AI-Workspace | `D:\AI-Workspace` 为干净 `main@1dd6de3e244858c44b716cacd72961ea9419f564`；本 Task 使用独立 linked worktree | 可用；当前事实路径是 D:，不是旧电脑/旧指南的 C: 路径 |
| Workspace Sync | `ON_DEMAND`；provider unavailable；stale 6；conflicts 0 | Git canonical 可继续使用；不能把 Document Assistant Available 当成 Sync provider 可用 |
| Document Assistant | Provider 可发现；healthcheck `ok=true`，token/API connectivity/Drive permission 均为 `ok` | 可用；未读取或输出凭据值 |
| BlueStacks static runtime | `C:\Program Files\BlueStacks_nxt\HD-Player.exe` 与 Multi-instance Manager 显示 `5.22.262.1001`；`HD-Adb.exe` 存在；卸载项显示 BlueStacks `5.22.262.1001` / BlueStacks Services `3.0.9`；下载器和关键 EXE Authenticode 均为 `Valid / Now.gg, INC` | 证明签名、安装文件与登记存在；未获 User 批准前不启动，不视为 Hyper-V、实例或 ADB Ready |

### 虚拟化读数说明

`Win32_Processor` 在 hypervisor 已运行时返回 `VirtualizationFirmwareEnabled=False`、`SLAT=False`、`VMMonitorModeExtensions=False`，但 `systeminfo` 明确报告“已检测到 hypervisor”，且 HypervisorPresent、VMP 与 boot setting 相互一致。因此这些 CPU 布尔值在当前状态下视为被 hypervisor 屏蔽的非决定性读数，**不能据此宣称 BIOS 虚拟化关闭**。安装后应以 BlueStacks 实际启动和官方诊断为最终兼容性证据。

## 缺失项与当前阻塞

| 项目 | 只读证据 | 影响 |
| --- | --- | --- |
| BlueStacks runtime readiness | 程序文件和卸载项已出现，数字签名有效，但未启动，未验证 hypervisor 兼容、渲染器或重启复现；未发现 Windows 产品服务 | User 必须先决定保留核验或批准卸载；不能把静态安装计为 Ready |
| BlueStacks ADB target | `HD-Adb.exe` 已存在，但 PATH 中无 `adb`，无 ADB 进程或 5037 listener，也无实例 serial/port | 工具文件存在，目标连接与唯一性仍不可验证 |
| `HuuugeResearch` | 无 BlueStacks Engine/config/instance 目录 | 专用实例不存在；历史 `Pie64_1` 不能复用为本机 identity |
| Huuuge app identity | 没有目标实例，未启动其他模拟器查询 | package/version/ABI/login/foreground 均未验证 |
| 正式 Collector 包 | `C:\HuuugeCollector` 与 `D:\HuuugeCollector` 均不存在 | 无法做包版本/hash、依赖和静态 preflight；本轮也未访问公司 SVN |
| Huuuge 维护工作区 | 已检查的 `C:\huuuge-research`、`D:\huuuge-research` 不存在 | 不阻塞新人演示；RC4 规定私有实现仓库不是新人前置。若后续要改 Collector，实现仓库位置和权限需另行确认 |
| 持久 Workspace 路径 | 当前为 `D:\AI-Workspace`；旧指南写 `C:\AI-Workspace` | 不能复制旧电脑路径。安装前必须决定保留 D: 并验证脚本可配置，或另行批准迁移；本 Task 不自动移动/复制 |

## 共存风险

- 下载目录与当前用户 Temp 中曾各有一个 BlueStacks Installer 进程，启动时间均为 2026-09-04 11:20；最终回查时两者已退出，并出现 runtime 文件与卸载项。该并发安装不是 Codex 发起或操作，来源/签名和保留决定仍待 User 审批。
- MuMu 模拟器 5.27.6.3562 已安装，相关主进程和 `MuMuRemoteService` 当前运行；本轮未停止。
- NoxPlayer 7.0.6.2 已安装，未发现运行进程/服务；本轮未修改。
- MuMu/Nox 各自带有 ADB 可执行文件，但不在 PATH，且属于其他模拟器。它们不能直接当作 BlueStacks 演示 ADB；安装/验证 BlueStacks 时需要检查 5037、虚拟化驱动和后台服务冲突。
- 当前 5037 无 listener。该结果只说明审计时无 ADB server，不等于安装后不会冲突。

## 推荐安装/配置动作

以下动作全部等待 User 逐项批准；建议按顺序执行，每步失败即停：

1. **处理已完成安装 Gate**：User 决定保留当前 BlueStacks 5/BlueStacks Services，或批准按回退清单卸载。数字签名已验证有效；若保留，仍需由 User 确认下载来源获得组织批准，并确认版本、程序/data 路径和卸载边界；Codex 不在未批准状态启动或重装。
2. **冻结路径决定**：保留 `D:\AI-Workspace` 作为治理仓库，不复制旧电脑 `C:\AI-Workspace`。为 Collector 选择一个新的 User 批准目录；创建前记录目标、磁盘、权限和删除/保留规则。
3. **记录共存基线**：保存 MuMu/Nox 当前版本、进程、服务和 5037 状态。安装/首次验证窗口内只临时停止冲突进程；不自动卸载，验证结束按基线恢复。
4. **核验或回退 BlueStacks 5**：若 User 批准保留，仅按 [BlueStacks 官方要求](https://support.bluestacks.com/hc/en-us/articles/4415238471053-System-requirements-for-BlueStacks-5-on-Hyper-V-enabled-Windows-10-and-11) 核验当前 `5.22.262.1001`；官方说明 5.20+ 可在 Hyper-V 开/关状态运行，本机优先保持现有 hypervisor/VMP，不先修改 Windows feature。若来源/签名/版本不获批准，则按第 2 节快照边界卸载本次新出现的 BlueStacks 与 BlueStacks Services，不自动改装其他版本。
5. **确定存储与管理员变更**：安装前确认程序/data/备份落点和空间。若安装器要求 Hyper-V Administrators 组或重启，先单独列出命令、影响和恢复方式，再让 User 批准。
6. **新建专用实例**：通过官方 Multi-instance Manager 新建 **Fresh Pie 64-bit** 实例，显示名 `HuuugeResearch`。官方入口见 [Pie 64-bit 指南](https://support.bluestacks.com/hc/en-us/articles/4406032772877-How-to-use-Pie-64-bit-on-BlueStacks-5) 与 [Multi-instance Manager](https://support.bluestacks.com/hc/en-us/articles/360052834092-How-to-create-and-manage-instances-using-the-Multi-instance-Manager-on-BlueStacks-5)。不克隆日常/其他电脑实例，不预设 internal ID。
7. **启用最小 ADB**：只在 `HuuugeResearch` 的 Advanced 设置启用 ADB，并按 [BlueStacks 官方 ADB 指南](https://support.bluestacks.com/hc/en-us/articles/23925869130381-How-to-enable-Android-Debug-Bridge-on-BlueStacks-5) 回读端口。先验证目标唯一，再运行任何 package 查询；不 Root。
8. **User 完成登录**：User 在专用实例完成 Google Play/Huuuge 登录，在 TortoiseSVN 完成公司认证。Codex 不读取、复制或保存密码/token。
9. **取得正式包但不运行**：从公司 SVN 获取批准版本到选定目录，记录 revision、包版本、hash、说明和 Python 依赖；只运行不会启动 Collector 的静态 preflight。
10. **Environment-ready Review**：将实际 BlueStacks 版本、路径、新 internal ID、ADB serial/port、Huuuge package/version/ABI、SVN 包版本/hash和共存验证写回 TASK-0027。全部通过后，再请求进入 Reliability Hardening。

## 成功标准

环境只有同时满足以下条件才可标记 `Environment Ready`：

1. BlueStacks 当前版本在现有 Windows hypervisor 模式下稳定启动，并能在重启后复现；
2. 唯一专用实例显示名为 `HuuugeResearch`，本机 internal ID 新生成且已记录；日常/其他模拟器未被修改；
3. 实例为 Pie 64-bit，资源、ABI、data path 与备份边界可回读；
4. ADB 只连接目标实例，serial/port 稳定，5037 无争用，其他 emulator device 不混入；
5. Huuuge 的实际 package、version、versionCode、ABI 与 foreground 由本机回读；登录由 User 完成；
6. 正式 Collector 包的 SVN revision/版本/hash/说明/依赖明确，静态 preflight 通过，但 Collector 尚未启动；
7. Workspace 路径由 User 确认，脚本不依赖台式机绝对路径；
8. Document Assistant healthcheck 继续为 token/API/Drive `ok`；
9. 回退清单覆盖每项实际变更，且 User 明确批准进入下一阶段。

该 Gate 通过也只表示“笔记本环境可进入 Reliability Hardening”，不表示 Collector READY、First Run 通过或实机演示成功。

## Rollback / 回退方案

1. **当前快照**：记录 Windows feature、`hypervisorlaunchtype`、BlueStacks/其他模拟器卸载项、进程、服务、5037、PATH、程序/data 目录和磁盘空间；保留审计前“无 BlueStacks 产品目录/卸载项”的证据。
2. **BlueStacks**：若 User 不批准保留当前并发安装，或后续核验失败，只在 User 明确批准后卸载本轮新出现的 BlueStacks `5.22.262.1001` 与 BlueStacks Services `3.0.9`；删除动作仅针对本轮新建且已确认无 User 数据的 `HuuugeResearch`。不触碰 MuMu/Nox 数据。
3. **Windows/组成员**：优先不改现有 VMP/hypervisor。若 User 批准后确有修改，按快照恢复原值（VMP Enabled、`hypervisorlaunchtype=Auto`、当前组成员关系）并重启复验。
4. **ADB/PATH**：删除本轮新增的 PATH 项、forward 或 ADB 配置；停止本轮启动的精确 ADB 进程，恢复安装前 5037 状态，不终止其他产品拥有的进程。
5. **其他模拟器**：若为验证临时停止 MuMu/Nox，只恢复安装前存在且原本运行的服务/进程；不改版本、不卸载。
6. **正式包目录**：只清理本轮新建、路径已核对且无 User 修改的目录；存在 User 文件或来源不确定时保留并报告，不递归覆盖/删除。
7. **Workspace**：`D:\AI-Workspace` 和 Task worktree不迁移、不删除；任何失败都保留 Task、审计和脱敏日志用于复核。

## 当前唯一下一步

User 决定保留并批准核验当前 BlueStacks 安装，或批准卸载 BlueStacks/BlueStacks Services；随后审批第 2–10 项环境变更，特别是路径、是否临时停止 MuMu、是否允许管理员组/重启、`HuuugeResearch` 新建和正式 Collector 包目录。批准前不启动 BlueStacks，不进入安装配置或 Reliability Hardening。
