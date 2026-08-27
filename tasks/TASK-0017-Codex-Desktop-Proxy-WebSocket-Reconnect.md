# TASK-0017 — Codex Desktop 代理 / WebSocket 重连诊断与修复

- Status: Review
- Owner: User / ChatGPT
- Executor: Codex
- Priority: P0 / operational reliability
- Date: 2026-08-27
- User authorization: 已明确要求诊断并修复
- Concurrency: TASK-0016 正在进行；本任务必须使用独立 Git worktree / branch，禁止覆盖 TASK-0016 的工作区或未提交变更

## Goal

解决 Windows Codex Desktop 在代理开启时，经常在任务开始或响应流中出现：

```text
正在重新连接 1/5
...
正在重新连接 5/5
```

随后才通过 HTTP 继续工作的现象。

最终目标：

1. 证明失败的是哪一层：WebSocket、代理继承、TLS、DNS、Codex startup prewarm、服务端关闭或其他原因；
2. 选择最小、可回滚、Codex 专用的修复，不粗暴关闭全局代理；
3. 新会话不再等待完整 5 次重连后才进入 HTTP；
4. 保持 ChatGPT 登录、MCP、Git、TASK-0016 和正在运行的 Huuuge Capture 不受影响；
5. 形成一键诊断、修复、查看状态和恢复方案。

## Current Hypothesis — must verify, not assume

当前现象高度符合：

```text
Codex 首先尝试 Responses WebSocket
→ 当前代理路径无法完成或稳定保持 WebSocket
→ Codex 按默认 stream retry 重试 5 次
→ 重试耗尽后 fallback 到 HTTPS / SSE
→ 后续请求恢复
```

官方依据：

- Codex Configuration Reference：`stream_max_retries` 默认 5；Provider 可声明 `supports_websockets`。
- OpenAI Codex 源码测试 `websocket_fallback.rs`：WebSocket 重试耗尽后回放为 HTTP，且当前 Session 的 fallback 会保持。
- OpenAI Codex issues #22634、#21880、#23665 记录了 Windows / 代理环境中相似的 `Reconnecting 1/5 ... 5/5` 和 HTTPS fallback。

但也可能是 startup prewarm、服务端关闭、桌面进程未继承代理、TLS 拦截或当前版本 Bug。必须先读取本机日志确认。

Official / primary references:

- https://developers.openai.com/codex/config-reference/
- https://learn.chatgpt.com/docs/config-file/environment-variables
- https://github.com/openai/codex/blob/main/codex-rs/core/tests/suite/websocket_fallback.rs
- https://github.com/openai/codex/issues/22634
- https://github.com/openai/codex/issues/21880
- https://github.com/openai/codex/issues/23665

## Safety and scope

- 不修改 OpenAI Codex 二进制或上游源码。
- 不使用第三方未审阅“修复器”直接改系统。
- 不上传或打印 access token、Cookie、Authorization、代理订阅、节点地址、完整日志或账号信息。
- 日志只保留错误类型、协议、时间、版本、redacted host/port 和结果。
- 不关闭或重启 Huuuge Collector、模拟器、Frida、当前 Capture 或 Document Assistant。
- 不修改 TASK-0016 的文件、分支、Memory Outbox 或未提交变更。
- 不直接改变全局代理路由；优先 Codex 专用、可撤销设置。需要调整代理应用 UI 时，先向 User 给出明确操作和影响。
- 所有配置修改前备份；失败自动回滚。

## Worktree / branch requirement

在 AI-Workspace 之外建立独立 worktree，例如：

```text
branch: task-0017-codex-network
worktree: C:\Users\admin\Documents\Codex\AI-Workspace-task-0017
```

本任务完成前不要直接 push `main`。提交到独立 branch，等待 ChatGPT Review；本机网络修复可先验证，但必须保留恢复命令。

## Phase A — Diagnose first

### A1. Snapshot current state

只记录非敏感信息：

- Codex Desktop version、bundled CLI / app-server version（可读取时）；
- Windows version；
- Auth mode：ChatGPT login / API key（不读取 token）；
- Model / provider；
- `%USERPROFILE%\.codex\config.toml` 的相关非敏感键与 SHA-256；
- Codex App 启动方式；
- 代理应用名称、版本、当前模式（System / TUN / Mixed / HTTP / SOCKS 等）和本机端口；端口可记录，节点与订阅不可记录；
- Windows WinINET/System Proxy、WinHTTP Proxy；
- 当前进程可见的 `HTTP_PROXY`、`HTTPS_PROXY`、`ALL_PROXY`、`NO_PROXY` 是否存在，只记录变量名和 redacted host/port；
- `CODEX_CA_CERTIFICATE` / `SSL_CERT_FILE` 是否设置，只记录存在性和文件是否可读；
- `localhost` / `127.0.0.1` 是否被错误送入代理。

### A2. Reproduce and inspect logs

在不影响 TASK-0016 的临时新线程中，复现一次最短请求并记录墙钟时间。

优先读取 Codex 本机 bounded diagnostics、app-server logs 或经批准的临时 plaintext log。搜索但不限于：

```text
responses_websocket
startup websocket prewarm
Reconnecting
stream disconnected
websocket closed
Falling back from WebSockets to HTTPS
HTTP/SSE
timeout waiting for child process to exit
proxy
TLS / certificate / handshake
```

如果可调用 `codex doctor --all`，使用它；若 WindowsApps / Desktop bundled CLI 不可直接执行，记录限制，不为此修改安装。

### A3. Transport matrix

使用最小无副作用测试，比较：

1. 当前代理配置；
2. 当前代理但使用其 WebSocket 兼容的 HTTP / Mixed / TUN 路径；
3. Codex 专用 bypass / direct（仅在当前网络允许且 User 不会失去访问时）；
4. 官方 / 当前版本支持的 HTTPS-SSE-only 方式；
5. `localhost` 直连，验证本地 MCP 不经过代理。

测试目标 host / endpoint 必须从本机 Codex 日志或当前官方实现确认，不得凭旧博客硬编码。

至少验证：TLS handshake、WebSocket upgrade / keepalive、HTTPS Responses stream、DNS、代理继承和回退行为。

## Phase B — Select one evidence-based fix

按以下优先级选择，不能同时堆多套修复：

### Option 1 — Fix WebSocket route（优先）

若代理存在可正常承载 WebSocket 的 TUN、Mixed 或 HTTP CONNECT 模式：

- 让 Codex Desktop 稳定使用该路径；
- 解决 Desktop 进程没有继承 shell-only proxy 的问题；
- 保留 `NO_PROXY` / bypass：`localhost,127.0.0.1`；
- 不更改其他应用的路由，除非 User 明确批准。

### Option 2 — Start directly with HTTPS / SSE

若当前代理稳定支持 HTTPS/SSE，但确实不支持 Responses WebSocket：

- 使用当前已安装 Codex 版本**正式支持且可验证**的方式关闭该 Provider 的 WebSocket；
- 自定义 Provider 可评估 `supports_websockets = false`；
- built-in `openai` Provider 不得伪造 `[model_providers.openai]` 覆盖，因为 reserved provider 不能这样重定义；
- 旧版 / removed feature flag 只有在当前版本源码和实际日志证明仍生效时才可使用；不得照抄过时社区配置；
- 不以“把重试次数改小”代替真正修复。

### Option 3 — TLS trust repair

只有日志证明存在企业 TLS interception / unknown CA 时：

- 使用官方 `CODEX_CA_CERTIFICATE`，其次 `SSL_CERT_FILE`；
- 不关闭证书校验；
- 不把证书文件提交 Git。

### Option 4 — Upstream bug workaround

若代理关闭、WebSocket handshake、HTTPS/SSE 和证书都正常，但仍稳定复现：

- 记录 Codex version、最小复现和脱敏日志；
- 尝试当前官方版本升级 / 回退到已验证版本；
- 使用 `/feedback` 或 GitHub issue 提供 thread ID / sanitized evidence；
- 临时采用已验证的 HTTPS/SSE path，等待上游修复。

## Deliverables

在独立 branch 建立：

```text
bootstrap/codex/network/
├── README.md
├── Get-CodexNetworkStatus.ps1
├── Test-CodexTransport.ps1
├── Repair-CodexReconnect.ps1
└── Restore-CodexNetworkConfig.ps1

docs/experiments/CODEX_PROXY_TRANSPORT_DIAGNOSIS.md
solutions/codex/reconnecting-proxy/README.md
```

脚本要求：

- Windows PowerShell 5.1 可运行；
- 一键执行，输出中文；
- 写清“做什么、成功表现、失败怎么办”；
- 幂等、最小修改、时间戳备份、失败回滚；
- 不输出 Secret；
- 不假定具体代理应用，能够检测后给出对应分支；
- 若必须手动修改代理 UI，只输出精确步骤，不模拟点击；
- 状态输出至少包括：当前 transport 判断、proxy source、WebSocket、HTTPS/SSE、本地 bypass、修复模式、配置来源、是否需重启 Codex。

## Validation

至少完成：

1. **Before**：代理开启时可复现一次 1/5 → 5/5 或日志等价证据；
2. **After fresh thread ×3**：三个新线程不再完整经历 5 次重连；
3. 若选择 WebSocket fix：日志显示 WebSocket 正常建立并完成 response；
4. 若选择 HTTPS/SSE-only：日志显示不再先发起失败的 WebSocket 链路，直接使用 HTTP/SSE；
5. 响应内容完整，不只验证 TCP connect；
6. `feishu-docs` 本地 MCP healthcheck 正常，`localhost` 未经代理；
7. Git fetch / push 正常；
8. Codex 重启后仍生效；
9. Restore 后可以回到修改前配置；
10. TASK-0016、Huuuge Collector 和 Capture 未被修改或中断。

不要把固定“首字时间”当唯一验收，因为模型和服务端负载会变化；核心验收是没有完整 5 次失败回退、最终 transport 有日志证据且连续 3 次稳定。

## Completion and handoff

完成后返回：

- Root cause：Confirmed / Probable / Unconfirmed；
- Codex / proxy / Windows 版本；
- Before / After 证据摘要；
- 最终 transport：WebSocket 或 HTTPS/SSE；
- 实际修改的非敏感配置项；
- 一键状态、修复和恢复命令；
- 独立 branch 与 commit；
- 是否需要 User 在代理 UI 做一步手动操作；
- 未解决风险和上游 issue；
- `Subagents: none`，除非本任务在受限权限下由 User 明确启用。

等待 ChatGPT Review 后再合并到 `main`。

## Execution Result — 2026-08-27

- Root cause: **Confirmed**。Codex 默认未将 Aurora 的 WinINET loopback proxy 用于 Responses WebSocket；baseline 握手 timeout，但 HTTPS inference 可达。临时 system-proxy override 与 explicit proxy 均得到 HTTP 101，排除 Aurora WebSocket、TLS、DNS 和服务端整体可达性问题。
- Fix: 只在预检成功后为 Codex 用户配置增加 `features.respect_system_proxy = true`；未修改 Aurora、Windows 全局 proxy、Provider、TLS trust、MCP 或其他仓库。
- Restore: exact-hash 恢复到原配置已演练；Codex 后续写入无关设置时，surgical restore 只撤销本任务键并保留新设置；恢复后重新复现 baseline，再应用修复成功；重复 Repair 幂等。
- Fresh threads: 连续 3 个新任务返回完整 `TASK-0017 validation #1/#2/#3 OK`，每次随后 transport probe 均为 WebSocket HTTP 101、HTTPS ok、TLS ok。
- Local integrations: `feishu-docs` stdio healthcheck 全部 ok；Git fetch 正常，独立 branch push 由最终提交完成。
- Evidence: `docs/experiments/CODEX_PROXY_TRANSPORT_DIAGNOSIS.md`。
- Reusable solution: `solutions/codex/reconnecting-proxy/README.md`。
- Subagents: none。
- Next action: ChatGPT Review 本任务诊断、最小修复、回滚与三次新任务证据；Review 前不合并 `main`。
