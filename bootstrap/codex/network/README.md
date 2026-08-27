# Codex Desktop 网络诊断与恢复

本目录用于 Windows Codex Desktop 在 WinINET 本机代理下出现 WebSocket timeout / `Reconnecting 1/5 … 5/5` 时的脱敏诊断。默认不修改 Windows 全局代理、不关闭代理、不修改 provider、不降低 TLS 校验。

## 一键入口

```powershell
# 查看当前状态
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\bootstrap\codex\network\Get-CodexNetworkStatus.ps1

# 对比基线、系统代理和显式 loopback 代理
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\bootstrap\codex\network\Test-CodexTransport.ps1 -Mode Baseline
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\bootstrap\codex\network\Test-CodexTransport.ps1 -Mode SystemProxy
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\bootstrap\codex\network\Test-CodexTransport.ps1 -Mode ExplicitProxy

# 应用最小修复
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\bootstrap\codex\network\Repair-CodexReconnect.ps1

# 恢复修改前配置
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\bootstrap\codex\network\Restore-CodexNetworkConfig.ps1
```

## 修复内容

修复脚本只在以下条件全部满足时写入 `~/.codex/config.toml`：

1. WinINET 正在使用 loopback proxy；
2. 当前 bundled CLI 接受 `features.respect_system_proxy=true`；
3. 临时 override 的 doctor probe 得到 WebSocket `HTTP 101 Switching Protocols`；
4. 配置结构唯一、可安全补丁。

实际写入只有：

```toml
[features]
respect_system_proxy = true
```

脚本先保存时间戳备份，原子替换后再次运行脱敏 doctor probe；失败自动回滚。Restore 在配置 hash 未变化时精确恢复备份；若 Codex 后来写入了其他设置，则只撤销 `respect_system_proxy` 并保留后续配置。该键本身被其他写入者改变或配置结构不唯一时仍会 fail-closed。

## 成功表现

- `WebSocket握手` 为 `HTTP 101 Switching Protocols`；
- HTTPS/SSE endpoint 仍可达；
- 不再完整经历 5 次失败后才 fallback；
- MCP 若为 stdio，不经过 HTTP proxy；
- Git fetch / push 正常。

配置由新 app-server / CLI 进程读取。若状态显示“需要重启 Codex”，先完成当前工作，再正常退出并重新打开 Codex；不要结束 Collector、模拟器或其他项目进程。

## 失败怎么办

- Repair preflight 失败：不修改配置，保留诊断输出。
- Repair 写入后验证失败：自动恢复备份。
- Restore 报告配置冲突：说明 `respect_system_proxy` 本身或配置结构已被其他写入者改变；先人工审阅差异，不要直接 `-Force`。
- 任意 TLS/CA error：停止使用本修复，按官方 `CODEX_CA_CERTIFICATE` 路线单独处理；不得关闭证书校验。
