# TASK-0027 Phase D — Huuuge Research Laptop Setup

- Date: 2026-09-04
- Result: `Huuuge Research Laptop Ready = Yes`
- Scope: 长期研究环境部署；只验证 Collector 生命周期，不执行 Spin、Win/Reward、RTP/Bet 分析或业务逻辑修改
- Subagents: none / OFF

## 当前环境

| 项目 | 当前状态 |
| --- | --- |
| BlueStacks | BlueStacks 5 `5.22.262.1001`，继续使用现有 Hypervisor/VMP、program path 与 data path |
| 原实例 | `Pie64 / HuuugeResearch-PhaseB / 127.0.0.1:5585 / Root OFF`，保留且未删除 |
| 长期研究实例 | `Pie64_1 / HuuugeResearch / 127.0.0.1:5565 / Root ON` |
| Huuuge | package、version 与 arm64-v8a identity 保持 Phase B 已核验状态；User 的安装和登录数据来自当前本机实例克隆 |
| ADB | Google platform-tools `37.0.1`；controller 固定使用 `127.0.0.1:5565`；最终只有一个 5565 listener |
| Collector | 公司 SVN 正式 `1.0.1`，working copy `C:\HuuugeCollector@r6701`，版本化文件保持 clean |
| Frida | Host/server/Gadget 均为 `17.17.0`；ARM64 Gadget 与 `27043 / on_load=wait` config 已部署到研究实例 |

## 已完成配置

1. 删除此前误建且为空的 `Pie64_1` 后，按 User 明确批准克隆当前已安装 Huuuge 的本机 `Pie64`；BlueStacks 初始分配 `Pie64_2`，在实例关闭状态下将研究 clone 的内部 identity 对齐为正式 contract 的 `Pie64_1`。原 `Pie64` 数据未删除。
2. 将研究实例 ADB 对齐到 `5565`。Windows 动态排除范围曾覆盖该端口；按 User 单独批准，为 `5565` 建立持久 administered exclusion，WinNAT 重启后 5565 可绑定且 BlueStacks listener 为 1。
3. 只为 `Pie64_1` 启用真实 Root。Root 工具源固定到 `BlueStacks-Root-GUI@7002d185522c41a15ea9b184eff24393c5a62a11`；当前 BlueStacks 二进制与研究 VHD 的实际签名先在副本上完成启用、关闭和恢复验证，再应用到 live 环境。`Pie64` 的实例 Root flag 保持 `0`。
4. 安装 Google platform-tools 与隔离 Python `.venv`，准备 Frida `17.17.0` server/Gadget；没有修改 Collector 业务代码、Hook、serializer 或六字段 schema。
5. 正式 bootstrap preflight 通过：`Pie64_1 / 5565 / uid=0(root)`、Android 9、x86_64 + `libnb.so`、Huuuge arm64-v8a、Frida server 与 Gadget/config 均满足正式运行契约。

## 生命周期验收

正式入口以 `-ValidationOnly` 执行：

1. `Start` 成功并创建 Session `20260904_135724`；
2. strict `READY` 成功，证明 Hook 已安装、真实 RPC 已到达、raw 与 decoded JSON 均已落盘；
3. 保持 15 秒短 Session，不执行游戏点击或 Spin；状态为 `ready`，RPC `61`、decoded `61`；
4. `Stop` clean exit，manifest 为 `stopped`；
5. Finalize 为 `finalized`，active state 已移走，validation-only inventory 留在 Collector 本机 `.local`，没有写入业务仓库；
6. 结束后精确停止本轮 root Frida server 与 Huuuge process，移除 ADB forward，并确认 host capture process `0`、临时 residual `0`。Gadget/config 作为长期环境依赖保留。

本结果只证明正式 Collector `1.0.1` 在本机长期研究环境中的生命周期可用，不替代未参与开发策划的 RC4 独立 First Run。正式 RC4 仍为 `Pending`，历史 User 实跑仍为 `Failed/Invalid`，Bet/RTP 继续为 `Unsupported`。

## 遇到的问题

- BlueStacks clone 自动分配了 `Pie64_2`，而正式 Collector 固定 `Pie64_1`；通过关闭实例、备份并一致更新 clone identity 解决，没有复制台式机配置。
- Windows 动态端口排除覆盖 5565；通过 User 批准的单端口 administered exclusion 修复，未停止或修改 MuMu/Nox。
- 第一次 live Root 应用因临时 Python import 绑定错误停止；自动回滚恢复了空 Root 状态，修正运行环境后第二次通过。失败未留半完成状态。
- `start_frida_server.ps1` 调用全局 `py`；本轮仅用进程级 `PYTHONPATH/PATH` 绑定到正式 `.venv`，没有修改 Collector。
- ADB 同时显示 TCP serial 与 emulator alias，但两者指向同一研究 guest；正式 controller 始终使用精确 `127.0.0.1:5565`，主机 5565 listener 仍为 1。

## 修改原因与恢复

| 修改 | 原因 | 如何恢复 |
| --- | --- | --- |
| 新增 `Pie64_1` 研究 clone | 正式 Collector 1.0.1 固定该实例 identity，同时保留原实例 | 先关闭研究实例，再由 BlueStacks Multi-instance Manager 删除研究 clone；原 `Pie64` 始终保留 |
| 5565 administered exclusion | 防止 WinNAT/HNS 动态范围再次占用正式 ADB 入口 | 关闭 BlueStacks 后，以管理员身份删除 5565 exclusion 并重启 WinNAT；原 5585 实例不受影响 |
| 研究实例 Root + host root patch | 满足正式 controller 的 `uid=0(root)` contract | 关闭 Player 与 Manager 后运行本机 `ROLLBACK.sh --apply`，恢复 pre-root-live 的 host binaries、config 与 `Pie64_1` VHD；原实例继续 Root OFF |
| ARM64 Gadget/config | 满足 Houdini arm64 生命周期入口 | app 更新会自然替换 app directory；主动回退时随 pre-root-live VHD 恢复，或在 Root 环境中删除这两个研究实例文件 |
| platform-tools、Frida 与 `.venv` | 提供正式固定依赖 | Collector 停止后删除本机工具目录和 `.venv`；不影响 SVN 版本化文件 |

本机必要备份与可执行回退入口位于 `D:\HuuugeResearch-Laptop\backups\TASK-0027-PhaseD\`。回退脚本默认只 dry-run，实际恢复前要求 Player 与 Manager 均已关闭。

## 结论

`Huuuge Research Laptop Ready = Yes`。环境达到长期可维护的正式 Collector 1.0.1 contract；原实例、MuMu 与 Nox 未被 Root 或重配。下一步只需 User 确认本次 Phase D 结果；未来正式采集仍必须单独遵守对应 Session 范围和 User 操作边界。
