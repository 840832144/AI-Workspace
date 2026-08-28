# Top Tycoon Protocol Evidence

## Confirmed live boundary

ARM64 Gadget 内对 `Google.Protobuf.MessageExtensions.ToByteArray(IMessage)` 的受限 Hook 可直接读取 ILRuntime adaptor 包装的实际 protobuf full name，并只记录输出字节长度。探针不读取 payload bytes、字符串值、账号、token 或绝对余额。

两个独立 User-action Session 均命中：

| Message | Direction | Static field schema | Field types | Live evidence |
|---|---|---|---|---|
| `Protos.House.CGUploadCoin` | encode / outbound | `Coin`, `Energy`, `Estate` | `Int64`, `Int64`, `Int64` | 两个 Session 各 1 条，encoded length 5 |
| `Protos.Xxxgame.CGSaveUserdata` | encode / outbound | `Key`, `Value`, `Version` | `String`, `String`, `Int64` | Session A 4 条；Session B 4 条；长度变化只保留本机 |

字段类型来自 extracted hotfix assembly 的 generated protobuf getter signature，不是按名称猜测。

## Boundary sequence

```text
User manual Spin
  → client Spin / result / resource logic
  → CGUploadCoin(Coin, Energy, Estate)
  → CGSaveUserdata(Key, Value, Version)
  → Google.Protobuf MessageExtensions.ToByteArray
```

前两步之间的调用关系为 Derived：静态类与 live timestamp 支持该判断，但本轮没有直接 Hook `SpinGameLogic.Spin` 或读取对象值。

## Negative evidence

- xLua `lpb_encode / lpb_decode / lpb_decode_ex`：首轮 3 次 User manual Spin 为 0 event、0 error、0 truncation；该边界不承载核心老虎机流。
- managed `MessageParser.ParseFrom`：两个 User-action Session 0 decode event；没有恢复 direct inbound result/reward。
- 没有观察到独立 Spin request protobuf type。
- 没有恢复 direct Result、Reward、Win、reel/deck 或 post-Spin Balance object。

## F3 interpretation

`CGUploadCoin` 是 direct structured resource/state upload，`CGSaveUserdata` 是 direct structured envelope；它们足以达到 F3“实时结构化字段已恢复”。但 `CGSaveUserdata.Value` 内容未采集，不能据此声称 result/reward direct recovered。F4 的核心 direct chain 不成立。

## Protection / risk

- release app 不支持 `run-as`；arm64 namespace 需要隔离实例 Root + native bridge Gadget。
- Root/Frida/Gadget 仅用于被动读取已序列化边界；没有修改、伪造或重放请求/响应。
- 没有使用全局高频 `il2cpp_runtime_invoke` 或 ILRuntime interpreter trace。
- 新协议层或全局 ILRuntime trace 超出本日 bounded audit，触发 Stop condition。
