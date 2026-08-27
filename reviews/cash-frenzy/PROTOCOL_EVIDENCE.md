# TASK-0022 Protocol Evidence

## Confirmed Static Signals

1. `assets/src64/Utils/Protocol.luac` 包含业务 command map，例如 `BATCH_SPIN`、`ENTER_THEME`、`KEEP_ALIVE`、`RECONNECT`、`JACKPOT_DATA` 和 reward/gift commands。
2. `assets/src64/Network.luac` 包含 `BLSocket`、socket open/message state、server/port、keepalive、reconnect、send support 与 command dispatch。
3. `assets/src64/HttpRequestController.luac` 负责资源下载、hash/cache、JSON POST 与 retry queue；它不能单独证明 Spin 走 HTTP。
4. `libcocos2dlua.so` 包含 `SSL_read`、`SSL_write`、LuaSocket、WebSocket、TCP/UDP/TLS、XXTEA、Protobuf 与 `setFixProtocolParseError` 静态符号。
5. `libEncryptorP.so` 和 `libsigner.so` 分别提供 encryption 与 signing/SHA 候选边界。
6. network security config 对 loopback/部分私网开发地址允许 cleartext，并在 debug override 中声明 user/system trust anchors；这只说明配置能力，不证明生产流量可由系统代理直接观察。

## Current Interpretation

**Hypothesis**：核心游戏动作更可能经过自定义 `BLSocket` 二进制协议，LuaJIT command map 提供 command 名，native 层负责 socket、加密/签名和可能的 Protobuf 编解码。HTTP/JSON 主要信号更偏资源下载和 SDK；WebSocket/Ktor/OkHttp 还可能来自第三方 SDK，不能直接归因于 Spin。

**Static blocker**：没有游戏业务 `.proto`、descriptor set 或可直接读取的 Lua source。仅凭 `protobuf` 字符串不能确认 wire schema，更不能确认 bet/result/win/balance 字段。

## Minimal Dynamic Targets

按最小副作用顺序验证：

1. 先观察独立实例的 socket/TLS connection 与 package PID，不安装代理证书、不改系统信任。
2. 若普通代理不可见，优先在 app 明文边界被动复制 `BLSocket` send/recv 或 `SSL_write`/`SSL_read` buffer；不改参数和返回值。
3. 将一次 User Spin 的 command、方向、长度、时间与 UI action 对齐。
4. 只有成功恢复稳定字段后才建立 schema mapping；未知 bytes 原样留 local Raw。

## Evidence Level

当前全部为 **Static L1 / Feasibility F1**。没有 Runtime capture，不得写成“协议已解码”或“Spin 使用 Protobuf”。
