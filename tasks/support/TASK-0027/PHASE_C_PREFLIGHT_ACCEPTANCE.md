# TASK-0027 — Phase C Collector Preflight 验收

- Date: 2026-09-04
- Result: `Static preflight PASS / Dynamic lifecycle BLOCKED BEFORE START`
- Demo Ready: `No`
- Subagents: none / OFF

## 结论

公司 SVN 正式 Collector 包的来源、revision、version、source revision、ZIP/hash、manifest allowlist、依赖和脚本静态可解析性已经核验。正式工作副本位于 `C:\HuuugeCollector`，SVN status clean。

动态验收未启动。正式 controller 固定 `Pie64_1 / 127.0.0.1:5565` 并在启动时强制验证 `uid=0(root)`；本机获批环境是 `Pie64 / HuuugeResearch / 127.0.0.1:5585 / Root OFF`。继续执行会修改 Collector 实现或改变 Root/实例边界，均超出本轮范围，因此按 Gate 要求在启动前停止。

## 正式包核验

| 项目 | 已验证结果 |
| --- | --- |
| Installer | `trunk/HuuugeCollector/release/HuuugeCollector_Installer.zip` |
| SVN repository/working-copy revision | `6701` |
| Installer/tree last-changed revision | `6624` |
| Working copy | `C:\HuuugeCollector`；status clean |
| Version | `1.0.1` |
| Source revision | `77e0339fa73da2ab02fcbb6cff125604a9a8abd5`；manifest 标记 `source_dirty=false` |
| ZIP SHA-256 | `ACAC144B3CB58E861345D33F6CEEB95ACA0E1CE3CF8B49211C6E7AFB260A958A` |
| ZIP comparison | 单文件 export 与 working-copy `release` ZIP hash 一致 |
| Manifest | allowlist `3/3` hash/size 一致；无路径穿越项 |
| Static parse | PowerShell `9/9`、Python AST `5/5` |
| Declared Python packages | `frida`、`frida-tools`、`protobuf`、`lz4`、`grpcio-tools` |

## 启动前 preflight

| Gate | 本机事实 | 结果 |
| --- | --- | --- |
| Target instance | 正式 controller=`Pie64_1`；本机=`Pie64 / HuuugeResearch` | Blocked |
| ADB serial | 正式 controller=`127.0.0.1:5565`；本机批准=`127.0.0.1:5585` | Blocked |
| Root | controller 调用 `Assert-ResearchRoot` 并要求 `uid=0(root)`；本机 Root flag=`0` | Blocked |
| ADB dependency | 固定 `C:\platform-tools\adb.exe` 不存在 | Missing |
| Frida dependency | 固定 `C:\huuuge_research\tools\frida-17.17.0\frida-server-17.17.0-android-x86_64` 不存在 | Missing |
| Python/SVN | Python `3.11.15`、SVN `1.14.2` | Present |
| Collector virtualenv | `.venv` 未创建；未运行 Bootstrap 安装依赖 | Not installed |

## 缺陷列表

1. **P0 — Root contract 冲突**：正式 Start 路径要求真实 `uid=0(root)`；User 要求 Root OFF。当前实现不可能在该边界内到达 READY。
2. **P0 — instance/serial 固定值不兼容**：正式包固定 `Pie64_1 / 5565`，本机唯一目标是 `Pie64 / 5585`；直接启动会命中错误目标或失败。
3. **P1 — ADB 依赖固定路径缺失**：正式包不接受已验证的 direct `5585` transport，且固定 `C:\platform-tools\adb.exe` 当前不存在。
4. **P1 — Frida runtime 缺失且依赖 Root**：固定 x86_64 server、ARM64 Gadget/config 与 root-controlled staging 均未部署；在 Root OFF 下不能按当前 contract 补齐。
5. **P1 — 当前包没有参数化 Root-OFF demo path**：满足要求需要修改实现或改变环境边界，不属于“只做最小 Reliability Hardening”。

## 动态生命周期结果

| 阶段 | 结果 |
| --- | --- |
| Start | Not run；blocked before start |
| READY | Not proven |
| Short Session | Not created |
| Stop | Not run |
| Finalize | Not run |

未执行 Win/RTP/Bet 分析，未新增字段，未修改 Collector、SVN 工作副本、Huuuge 业务仓库、游戏请求/返回、余额或奖励。

## 验证

- Package manifest `3/3`、PowerShell parser `9/9`、Python AST `5/5`；
- TASK-0027 focused `20/20`、changed-document allowlist `12/12`；
- Task `23/23`、Context `13/13`、Memory `44/44`；
- Registry `14 canonical / 0 collision / valid`；
- Context refresh `74 sources / 0 broken link / 0 secret issue`；
- Workspace Doctor、PowerShell Context entry 与 `git diff --check` 通过。PowerShell wrapper 首次使用默认 TEMP 时只在测试临时目录 teardown 遇到 WinError 32；显式设置 ASCII `TEMP/TMP/TMPDIR` 后 `13/13` 通过，未修改测试或产品代码。

## 最终状态与唯一下一步

静态 preflight 完成后 BlueStacks、Collector、Frida、ADB client 和相关端口均保持停止；Root 仍为 OFF。Demo Ready=`No`。

唯一下一步：User 决定是否另行授权 Collector 工程适配，使正式入口支持本机 `Pie64 / 5585 / Root OFF`；未授权前不继续动态运行。
