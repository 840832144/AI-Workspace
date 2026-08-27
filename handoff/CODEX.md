# Codex Handoff

- Updated: 2026-08-27
- Task: TASK-0017
- Branch: `main`
- Current state: complete; User approved and fast-forward merged to `main` at `45ee2bc`
- Root cause: Confirmed
- Final transport: Responses WebSocket through Aurora WinINET proxy
- Subagents: none

## Outcome

TASK-0017 已完成真实分层诊断、最小可回滚修复、回滚演练、连续三个新任务验证和本地集成检查。确认 Codex 默认未将 Aurora 的 WinINET loopback proxy 用于 Responses WebSocket，导致 WebSocket timeout 后 HTTPS fallback；Aurora 本身可以完成 WebSocket HTTP 101，TLS、DNS、登录和 HTTPS inference 正常。

## Environment and Evidence

- Windows 10 Pro 10.0.19045 / build 19045。
- Codex Desktop 26.820.7780.0；bundled CLI `0.150.0-alpha.8`。
- Proxy：WinINET loopback port 29290，监听进程 Aurora；版本未确认。WinHTTP Direct；无 proxy env；无 CA env。
- Baseline：WebSocket timeout，无 101；HTTPS inference reachable；CDN HTTP 200；无 TLS error。
- Temporary `respect_system_proxy` override：WebSocket HTTP 101。
- Process-only explicit proxy：WebSocket HTTP 101。
- Persisted fix：WebSocket HTTP 101，HTTPS inference 与 CDN 正常，无 TLS error。

详细证据：`docs/experiments/CODEX_PROXY_TRANSPORT_DIAGNOSIS.md`。

## Fix and Commands

实际配置修改只有：

```toml
[features]
respect_system_proxy = true
```

```powershell
# 状态
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\bootstrap\codex\network\Get-CodexNetworkStatus.ps1

# 修复（幂等；预检、备份、验证、失败回滚）
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\bootstrap\codex\network\Repair-CodexReconnect.ps1

# 恢复修改前配置（默认 hash gate）
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\bootstrap\codex\network\Restore-CodexNetworkConfig.ps1
```

不需要 User 修改 Aurora UI。当前配置处于修复后状态。可在方便时正常退出并重新打开 Codex，再运行状态命令；不要强制结束 Collector、模拟器或其他任务进程。

## Validation

- Windows PowerShell 5.1 syntax/config/state regression：PASS。
- Restore：首次修复后 hash `508E...3AA6` 精确恢复到原 hash `77EB...C51`；三个新任务导致 Codex 写入无关设置后，surgical restore 又只撤销本任务键并保留 6 个新结构项；两种恢复都重现 baseline timeout，reapply 后 101；重复 Repair 幂等。当前最终 hash 为 `2911...E08D`。
- New task 1：`01a04187-2548-7601-9279-2f6df193b4e0`，完整返回 `TASK-0017 validation #1 OK`；随后 101。
- New task 2：`01a04187-8458-75d2-8420-c3cbedb399fe`，完整返回 `TASK-0017 validation #2 OK`；随后 101。
- New task 3：`01a04187-e143-7f20-8be0-923462754c5d`，完整返回 `TASK-0017 validation #3 OK`；随后 101。
- `feishu-docs`：environment/token/API/Drive permission healthcheck 全部 ok；stdio 不走 HTTP proxy。
- Git：`fetch origin main` 正常；branch push 在最终提交后验证。

## Safety and Known Limits

- 未修改 TASK-0016 worktree、Huuuge 仓库、Collector、Capture、Aurora 配置、Windows proxy、TLS trust、Provider 或 MCP 配置。
- Desktop bounded logs 没有足够精确的 model transport 事件；使用同版本 bundled CLI 的 `doctor --all --json` 取得 protocol-level 证据。
- 当前配置 feature 在安装版本有效，但不属于稳定公开 config reference；Codex 升级后应重跑 transport matrix。上游 Windows system-proxy WebSocket issue #29958 仍是相关风险。
- 为避免中断当前工作，没有强杀 Codex Desktop 外壳；三个新任务和每次新 CLI 进程已验证配置由新进程读取。

## Completion

- User 于 2026-08-27 明确批准合并 `main`。
- 合并前复验 PowerShell 5.1 脚本回归、`git diff --check`、凭据模式扫描和当前 transport 状态；结果均通过。
- `main` 已 fast-forward 到 `45ee2bc`，TASK-0016 的未提交 `tools/memory/memory_cli.py` 改动保持未变。
- 唯一后续：User 在方便时正常重启 Codex Desktop，然后运行状态命令完成外壳重启确认。
