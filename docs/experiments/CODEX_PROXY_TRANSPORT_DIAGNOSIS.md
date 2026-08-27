# Codex Desktop Proxy / WebSocket 诊断记录

- Date: 2026-08-27
- Task: TASK-0017
- Result: Confirmed
- Final transport: Responses WebSocket through Aurora WinINET proxy
- Subagents: none

## 结论

确认根因不是 Aurora 不支持 WebSocket，也不是 TLS、DNS、ChatGPT 登录或服务端整体不可达，而是当前 Codex Desktop / bundled CLI 默认没有把 Windows WinINET 系统代理用于 Responses WebSocket。结果是 WebSocket 直连握手超时，HTTPS 仍可达，因此表现为先重连、后回退。

将当前版本已经实现并经本机预检验证的 `features.respect_system_proxy = true` 写入 Codex 用户配置后，WebSocket 经 Aurora loopback proxy 获得 `HTTP 101 Switching Protocols`。没有修改 Aurora、Windows 全局代理、Provider、TLS 信任、环境变量、MCP 或其他应用路由。

`stream_max_retries` 的默认值 5 只描述 SSE stream interruption retry，单独看到 `1/5` 不能证明失败层是 WebSocket。本结论来自 transport matrix 与 `doctor --all` 的握手结果，不是从重试数字反推。

## 环境快照

| 项目 | 已确认事实 |
| --- | --- |
| Windows | Windows 10 Pro 10.0.19045 / build 19045 |
| Codex Desktop | AppX 26.820.7780.0；诊断时发现 26.820.9563.0 可用，但未升级以避免叠加变量 |
| bundled CLI | `codex-cli 0.150.0-alpha.8` |
| Auth / model | ChatGPT login；`gpt-5.6-sol`；未读取或输出 token |
| Proxy | WinINET enabled，loopback port 29290，监听进程 `Aurora`；User 确认代理应用为 Aurora；版本未从进程元数据确认 |
| WinHTTP | Direct |
| Proxy env | `HTTP_PROXY` / `HTTPS_PROXY` / `ALL_PROXY` / `NO_PROXY` 均未设置 |
| TLS env | `CODEX_CA_CERTIFICATE` / `SSL_CERT_FILE` 均未设置 |
| TUN | 未检测到 TUN-like adapter |
| 原配置 hash | `77EB21BD465DF06849368AF788CF5611C7E666DAE4FC687DB85D6571A715BC51` |
| 首次修复后配置 hash | `508E29B64454090DC68D4E92EA93D755F9B289BE47A3466BC0B30E94DE2F3AA6` |
| 三次新任务及后续 Codex 设置写入后的最终 hash | `2911B97BB9E66AA0A9959AEDE3BC6DB29EB4D5CF43C9E69CAA5AB86D20C5E08D` |

配置只记录非敏感键与 hash。没有复制完整日志、代理节点、订阅、Cookie、Authorization 或 token。

## 日志与 transport 证据

Codex Desktop bounded logs 位于 `%LOCALAPPDATA%\Codex\Logs`，本次只确认了 app-server stdio 生命周期，未发现足够精确的 model transport 事件。因此采用当前 bundled CLI 的 `codex doctor --all --json` 作为同版本、可脱敏的 transport 诊断来源。

| 模式 | WebSocket | HTTPS inference | CDN | TLS | 解释 |
| --- | --- | --- | --- | --- | --- |
| Baseline：无 proxy env，feature disabled | timeout，无 HTTP 101 | reachable，HTTP 405 探针 | HTTP 200 | 无证书错误 | WebSocket 未走 WinINET；HTTPS fallback 可用 |
| Temporary system-proxy override | HTTP 101 | reachable | HTTP 200 | 无证书错误 | 同一 Aurora 路径可承载 WebSocket |
| Process-only explicit loopback proxy env | HTTP 101 | reachable | 一次瞬时 timeout，后续正常 | 无证书错误 | 显式代理同样修复握手；不选择环境变量作为持久方案 |
| Persisted current config | HTTP 101 | reachable | HTTP 200 | 无证书错误 | 最小 Codex-only 修复稳定生效 |

DNS 探针得到 1 个 IPv4、0 个 IPv6，未出现 DNS failure。ChatGPT inference HTTPS 始终可达，排除账号、服务端整体不可达和 TLS trust failure。显式代理与 system-proxy override 都能通过 Aurora 完成 101，排除 Aurora 不支持 WebSocket。

## 修复选择

采用 Option 1：修复 WebSocket route。

```toml
[features]
respect_system_proxy = true
```

选择理由：

1. 临时 override 在写配置前已证明当前版本支持该 feature 并得到 HTTP 101；
2. 修改只作用于 Codex，避免调整 Aurora 或 Windows 全局路由；
3. 不伪造 built-in provider，不减少 retry，不关闭 TLS 校验；
4. 可用原始配置备份和 hash gate 精确恢复。

该 feature 在当前安装版本和上游源码中存在，但未列入稳定公开配置参考，因此升级 Codex 后应重新运行 transport test；若消失或行为改变，Repair 会在预检失败时停止而不写配置。

## 回滚演练

首次 Restore 运行暴露 PowerShell 5.1 `ConvertFrom-Json` 对象不能直接新增属性的问题。脚本 catch 已恢复修复前快照，实际 Codex 配置没有丢失；随后改为 `Add-Member -Force` 并加入回归测试。

最终演练结果：

1. 修复状态 hash：`508E...3AA6`；
2. Restore 成功，hash 精确回到原值 `77EB...C51`；
3. 恢复后 baseline 再次复现 WebSocket timeout，同时 HTTPS inference reachable；
4. Repair 重新应用成功，WebSocket 回到 HTTP 101；
5. 再次 Repair 返回“已应用，无需重复修改”，确认幂等。

三个新任务完成后，Codex Desktop 在本任务键保持 `true` 的同时写入了 6 个新的配置结构项，配置 hash 因而从 `508E...3AA6` 变为 `2911...E08D`。Restore 没有覆盖这些后续设置，而是以 `surgical-preserve-later-changes` 模式只移除本任务键；baseline timeout 再次出现。随后 Repair 基于保留后的配置重新备份并应用，最终 hash 回到 `2911...E08D`。这验证了恢复命令在并发配置演进下不要求危险的 `-Force`。

另一次早期实现中 `.NET File.Replace` 的空 backup 参数在本机失败；Repair 自动回滚并保持原配置 hash。原子写 helper 后改为同目录临时备份路径并验证通过。

## 连续三个新任务

修复重新应用后，按顺序创建三个 projectless 新任务。每个任务只返回固定完整内容，随后立即运行 current transport probe。

| # | Thread | 完整响应 | 随后 transport |
| --- | --- | --- | --- |
| 1 | `01a04187-2548-7601-9279-2f6df193b4e0` | `TASK-0017 validation #1 OK` | WebSocket HTTP 101；HTTPS ok；TLS ok |
| 2 | `01a04187-8458-75d2-8420-c3cbedb399fe` | `TASK-0017 validation #2 OK` | WebSocket HTTP 101；HTTPS ok；TLS ok |
| 3 | `01a04187-e143-7f20-8be0-923462754c5d` | `TASK-0017 validation #3 OK` | WebSocket HTTP 101；HTTPS ok；TLS ok |

三次均未出现完整 5 次失败后 fallback；响应内容完整，不只是 TCP connect。新任务与每次新 CLI doctor 进程也证明配置会被新进程重新读取。为避免中断当前 TASK-0017 和其他用户工作，没有强制结束整个 Codex Desktop Electron 进程；User 可在 Review 后正常退出并重开一次，随后运行状态命令作为最终外壳重启确认。

## 旁路与不受影响项

- `feishu-docs` healthcheck：environment、token、API connectivity、Drive permission 均为 `ok`；它使用 stdio，本地进程链路不经过 HTTP proxy。
- Git：`fetch origin main` 正常；最终独立分支 push 另行记录于 Handoff。
- TASK-0016 worktree、Huuuge 仓库、Collector、Capture、Aurora 配置和 Windows proxy 均未修改或重启。
- Subagents: none。当前父会话为宽松权限，按治理规则保持 OFF。

## References

- [Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
- [Codex environment variables](https://learn.chatgpt.com/docs/config-file/environment-variables)
- [Upstream Windows system-proxy WebSocket issue #29958](https://github.com/openai/codex/issues/29958)
- [Upstream WebSocket fallback tests](https://github.com/openai/codex/blob/main/codex-rs/core/tests/suite/websocket_fallback.rs)
