# Codex Desktop 在 Windows 系统代理下反复重连

## Problem

Windows Codex Desktop 已能登录并最终通过 HTTPS 工作，但新任务开始或响应流中先出现多次 `Reconnecting`。在使用 loopback WinINET 代理时，这可能是 Responses WebSocket 没有继承系统代理，而不是代理不支持 WebSocket。

不要只根据 `1/5` 判断协议层。先用同一 Codex 版本的 bounded diagnostics 比较 baseline、system proxy 和显式 proxy。

## Verified solution

在 TASK-0017 的 Windows 10 / Codex Desktop 26.820.7780.0 / bundled CLI 0.150.0-alpha.8 / Aurora loopback proxy 环境中：

- baseline WebSocket timeout，但 HTTPS inference reachable；
- temporary system-proxy override 与 explicit proxy 都得到 HTTP 101；
- TLS 与 DNS 无错误；
- 持久启用 `features.respect_system_proxy = true` 后，三个新任务连续完成。

因此最小修复是让 Codex 使用 WinINET system proxy，而不是关闭代理、修改 Provider、降低 retry 或关闭 TLS 校验。

## Commands

从 AI-Workspace 根目录运行：

```powershell
# 脱敏状态
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\bootstrap\codex\network\Get-CodexNetworkStatus.ps1

# 只读 transport matrix
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\bootstrap\codex\network\Test-CodexTransport.ps1 -Mode Baseline
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\bootstrap\codex\network\Test-CodexTransport.ps1 -Mode SystemProxy
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\bootstrap\codex\network\Test-CodexTransport.ps1 -Mode ExplicitProxy

# 预检、备份、修复、验证；失败自动回滚
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\bootstrap\codex\network\Repair-CodexReconnect.ps1

# 精确恢复修改前配置
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\bootstrap\codex\network\Restore-CodexNetworkConfig.ps1
```

Repair 仅在检测到 loopback WinINET proxy、配置结构可安全修改，并且 temporary override 已取得 HTTP 101 时写入：

```toml
[features]
respect_system_proxy = true
```

备份位于 `~/.codex/backups/task-0017-network/`，repair state 位于 `%LOCALAPPDATA%\AI-Workspace\codex-network\repair-state.json`，二者都不进入 Git。Restore 默认核对修复后 hash：未变化时精确恢复备份；有无关后续变化时只撤销本任务键；该键或配置结构发生冲突时 fail-closed。

## Success criteria

- 状态显示 `Responses WebSocket handshake succeeded` 与 `HTTP 101 Switching Protocols`；
- ChatGPT inference HTTPS 仍可达；
- 没有 TLS/CA error；
- 新任务不再完整经历 5 次失败 fallback；
- 本地 stdio MCP 与 Git 正常。

## Boundaries

- 不修改 Aurora 或 Windows 全局 proxy；不要求代理 UI 操作。
- 不设置 shell-only proxy environment，不改变 Provider 或 retries。
- 不使用该方案处理真实 TLS interception；若出现 CA error，应另走官方 `CODEX_CA_CERTIFICATE`。
- `respect_system_proxy` 不是稳定公开配置参考中的常规键。Codex 升级后先重新运行 transport matrix；Repair 的 HTTP 101 preflight 是写入安全门。
- 如果系统代理不是 loopback、配置 section/key 不唯一或 preflight 不成功，脚本停止，不猜测代理设置。

完整证据见 [`docs/experiments/CODEX_PROXY_TRANSPORT_DIAGNOSIS.md`](../../../docs/experiments/CODEX_PROXY_TRANSPORT_DIAGNOSIS.md)。
