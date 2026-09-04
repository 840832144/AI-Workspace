# TASK-0027 — 笔记本 BlueStacks Environment-ready 验收

- Date: 2026-09-04
- Host role: 笔记本汇报实机演示
- Result: `Environment Ready — BlueStacks / instance / ADB identity`
- Git baseline: `AI-Workspace/main@1dd6de3e244858c44b716cacd72961ea9419f564`
- User authorization: 保留并核验当前 BlueStacks；创建本机 Fresh Pie 64-bit `HuuugeResearch`；启用 ADB；端口冲突后另行批准改为 `5585`
- Final runtime state: BlueStacks Player、Multi-instance Manager 与 ADB client 均已退出；Root、Frida、Collector、Spin 均未启动

## 结论

本机 BlueStacks、专用实例和 ADB identity 已达到本阶段 Environment-ready。BlueStacks 5 `5.22.262.1001` 在当前 Windows Hypervisor / VMP 保持不变的条件下完成正常启动、退出和重启复现；本机安装自动生成的唯一 `Pie64` 实例已命名为 `HuuugeResearch`，没有复制台式机实例、VHD、路径、ADB port 或 Root 配置。

BlueStacks 默认 ADB port `5555` 落入本机 Windows TCP excluded range `5485–5584`，Player 日志明确记录端口转发冲突。User 随后批准只把当前实例的 host ADB port 改为 `5585`。复启后 `127.0.0.1:5585` 只有一个 listener，归属本轮 `HuuugeResearch` Player；`5037` 无 listener/争用，直接 ADB transport probe 成功回读 Android、ABI、shell identity 和 Huuuge package identity。

本结果只固定笔记本运行环境，不证明正式 Collector READY、First Run 成功、Bet/RTP、Reliability Hardening 或现场演示已经完成。正式 Collector 包、本机静态 preflight 和实现修订仍等待下一 Gate。

## 已验收环境

| 项目 | Confirmed 结果 | 验收判断 |
| --- | --- | --- |
| BlueStacks 版本 | App Player `5.22.262.1001`；BlueStacks Services `3.0.9` | 版本已回读 |
| 发行渠道与签名 | config campaign 为 `homepage-dl-button-en`；`HD-Player.exe` Authenticode 为 `Valid / Now.gg, INC` | 记录为官网下载 campaign / 有效发行者签名；不从该字段推导额外组织来源 |
| 安装/data path | Program `C:\Program Files\BlueStacks_nxt\`；data `D:\BS\BlueStacks_nxt\Engine\`；log `D:\BS\BlueStacks_nxt\Logs\` | 本机路径已固定；未套用台式机路径 |
| 磁盘 | D: 最终可用约 `201.5 GB`；Pie64 实例约 `6.83 GB` | 当前汇报环境容量适合，不触发卸载重装 Gate |
| 虚拟化 | 现有 Hypervisor / VMP 保持原状 | BlueStacks 在当前状态启动、退出、重启成功 |
| 专用实例 | 唯一 internal ID `Pie64`；显示名 `HuuugeResearch`；Pie 64-bit；4 CPU / 4096 MB；ABI config `x86,x64,arm,arm64` | 本机 fresh identity 已固定；未 clone 其他实例 |
| ADB | host endpoint `127.0.0.1:5585`；remote access `OFF`；唯一 listener count `1`；5037 count `0` | 唯一 serial/port 已固定 |
| Root | config `enable_root_access=0`；ADB shell 为 `uid=2000(shell)` | Root OFF |
| Huuuge | User 完成安装/登录动作；package `com.huuuge.casino.slots`；versionName `12.08.27100`；versionCode `1786533240`；primary ABI `arm64-v8a` | app identity 已回读；Codex 未安装、登录或执行游戏操作 |
| 共存 | MuMu 保持原运行状态；Nox 保持原状；已观察的 MuMu listeners 不占用 5585/5037 | 未确认 MuMu/Nox 冲突，因此未停止或修改 |

## 启动、退出与重启复现

1. 初始 Player 正常加载后通过 BlueStacks 退出确认完成正常退出。
2. `HD-Player.exe --instance Pie64` 复启后窗口标题为 `HuuugeResearch`，Player 可响应。
3. User 在 BlueStacks Advanced 设置中启用 ADB 后，Player 再次正常退出并重启。
4. 将冲突端口改为 `5585` 后再次执行退出/重启；最终一次窗口在约 `3.2 s` 内出现，等待运行稳定后 listener 与 ADB probe 均通过。
5. 验收结束后正常退出 Player；最终 `HD-Player=0`、`HD-MultiInstanceManager=0`、`HD-Adb=0`、port `5037=0`、port `5585=0`。

## ADB 冲突、修订与残留处理

- 本机 IPv4/IPv6 TCP excluded range `5485–5584` 覆盖默认 `5555–5565`；临时 bind probe 对 5555/5565 返回 access-denied，对 5585 成功。
- BlueStacks `BstkCore.log` 在 5555 配置下记录 `Port forward modify FAIL`；改为 5585 后记录 host port 5585 → guest port 5555，Player 建立唯一 `127.0.0.1:5585` listener。
- BlueStacks 随附 `HD-Adb.exe` 的 server 启动会扫描本机默认 emulator port；在 excluded ports 上出现长时间 `SynSent`，两次验证尝试均按精确 PID 清理，最终 `HD-Adb=0`、`5037=0`，失败没有静默隐藏。
- 为避免把该 CLI 启动行为误报为可用，当前验收使用 host-local、只读 direct ADB transport probe 验证 endpoint。Phase C 必须为正式入口固定可复核的 ADB implementation / timeout / cleanup；在此之前不得启动 Collector。

## 脱敏 ADB 回读

```text
ADB_ENDPOINT=127.0.0.1:5585
ABI=x86_64,x86,arm64-v8a,armeabi-v7a,armeabi
ANDROID=9
SHELL_ID=uid=2000(shell) ...
HUUUGE_PACKAGE=package:com.huuuge.casino.slots
HUUUGE_VERSION_CODE=versionCode=1786533240 minSdk=23 targetSdk=35
HUUUGE_VERSION_NAME=versionName=12.08.27100
HUUUGE_PRIMARY_ABI=primaryCpuAbi=arm64-v8a
RESULT=PASS
```

User 操作游戏期间曾回读 Huuuge `BootActivity` 为 foreground；第二次纯重启后的 foreground 为 BlueStacks Game Center，说明本阶段没有为演示自动启动游戏。现场启动游戏与正常操作继续由 User 执行。

## 回退验证

- 变更前 config hash 已保留；修改只涉及显示名、ADB enabled 与当前实例 ADB port/status port。
- rollback 脚本只接受 hash 与 `MODIFIED_FILE` 一致的指定副本；输入不匹配时 fail closed。
- rollback 已在另一份 copy 上执行，恢复为默认显示名、ADB disabled、port 5555，并通过 Baseline `5/5`。
- live config 与 `MODIFIED_FILE` hash 一致并保持 `HuuugeResearch / ADB enabled / 5585 / Root OFF`；未对 live config 执行回退。
- 回退到 5555 会重新遇到本机 excluded-port 冲突，只用于验证可恢复性，不作为推荐运行状态。

## 边界

- 没有安装、更新或卸载软件；没有修改 Windows feature、Hypervisor/VMP、PATH、防火墙、MuMu 或 Nox。
- 没有 Root，没有启动 Frida、Collector 或 Spin，没有执行游戏内点击、购买、充值、Auto Spin 或采集。
- 没有修改业务仓库、Collector schema、Hook/serializer、六字段、飞书文档或 Codex 配置。
- 没有把账号、Secret、完整日志、完整 config、截图或业务数据写入 Git。
- Subagents: none / OFF。

## 唯一下一步

User 审批 TASK-0027 Phase C Gate：确定正式 Collector 包的本机路径与取得方式，只做版本/hash/依赖/static preflight，并批准围绕笔记本汇报实机演示的 Reliability Hardening；获批前保持 BlueStacks、Root、Frida、Collector 与 Spin 停止。
