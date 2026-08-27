# TASK-0022 Protocol Evidence

## Confirmed Static Signals

1. `assets/src64/Utils/Protocol.luac` 含 `BATCH_SPIN`、`ENTER_THEME`、`KEEP_ALIVE`、`RECONNECT`、`JACKPOT_DATA` 等业务 command map。
2. `assets/src64/Network.luac` 含 `BLSocket`、open/message state、server/port、keepalive、reconnect、send support 与 dispatch。
3. `libcocos2dlua.so` 导出 `BLSocket::sendMsg/sendTable/onSocketCallback/onUIThreadReceiveMessage`、`SSL_read/write`、BIO、LuaSocket、WebSocket 与 Protobuf parse/serialize symbols。
4. `libEncryptorP.so`、`libsigner.so`、XXTEA/OpenSSL symbols 是 encryption/signing 候选；APK 内 23 个 proto/textproto 均属于 SDK 范围，没有游戏业务 descriptor。

## Confirmed Runtime Boundary

- Outer root Frida process view 为 x64，只看到系统 crypto/TLS；arm64 `libcocos2dlua.so` 必须通过 Houdini namespace 中的 Frida Gadget 观察。
- arm64 module view 中 `libcocos2dlua.so` 与 `libsigner.so` 可见；所有目标 symbols 均可 Hook。
- 大厅 20 秒边界计数：`BLSocket::sendMsg` 8、`sendTable` 3、`sendTickMsg` 5、`onSocketCallback` 16、`onUIThreadReceiveMessage` 8；同期间 `SSL_read/write`、BIO、LuaSocket 与 WebSocket 均为 0。
- 同期 process syscall 为 `sendto` 5 / 139 bytes、`recvfrom` 5 / 291 bytes，`send/recv` 为 0；次数与 BLSocket heartbeat 对齐，确认核心 live socket 为 UDP path。
- 15 秒基线 capture 得到 outbound 5、inbound 5、585 bytes、0 errors；均为 opaque binary，不是 JSON、gzip、zlib 或 zip。

## Confirmed Spin Correlation

- User 累计 5 次普通 Spin，Bet 10000，无 Feature。
- 3-Spin Session：36 outbound / 2,048 bytes，38 inbound / 14,793 bytes；恰好 3 个新的 255-byte outbound packet，随后出现 1.1–2.5 KB inbound bursts。
- 2-Spin schema Session：31 outbound / 1,617 bytes，34 inbound / 9,960 bytes；恰好 2 个 255-byte outbound packet，并捕获 2 个同构 Lua request shape。
- Lua request stack 为 `userdata + table`；table 是 `[1]=command string`、`[2]=payload table`、`[3]=metadata table`。
- 两个 Spin-correlated shape 的 payload fields：`autoSpin:number`、`bet:number`、`client_coins:number`、`free_spins:number`、`lines:number`、`spin_count:number`、`turbo:number`；metadata field：`_timestamp:number`。
- 无操作 shape 还确认 `theme_id:number`；这证明 schema hook 能区分 command payload，而非只观察固定 packet header。

## Inference

Spin-correlated command string 长度为 10；结合 static command map 中的 `BATCH_SPIN`、字段集合、恰好两次 User 动作和两个同构 request，推断 command 为 `BATCH_SPIN`，置信度高。本任务故意不读取 command 值，因此仍标为 Inference。

## Blocker

- 入站 UDP Raw 仍是不透明二进制；未确认 framing、compression、encryption 或业务 serialization。
- Spin proof 中 `BLMessage.getObj` 未触发，说明当前 Lua getter 不是 inbound business object 的稳定边界。
- 尚未恢复 `result`、`win`、`balance`、reel/stop、feature/update 字段，不能建立 request → result → balance change 数值闭环。
- 不能仅凭 native Protobuf symbols 宣称游戏协议为 Protobuf，也不能从 outbound `client_coins` 字段存在推导真实余额值。

## Evidence Level

当前为 **Feasibility F3**：真实 Spin 的 outbound structured fields 已恢复，Raw path 可重复 start/READY/stop；inbound structured decode 和 F4 Huuuge-like collection path 尚未证明。
