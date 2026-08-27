# TASK-0022 Reuse Matrix

## Baseline

- Huuuge reference：`huuuge-android-research@4a5dddf7782307c6a8f368c9f1dc6390eec6f65b`，Collector 1.0.1。
- 使用方式：只读架构、Houdini bootstrap 与 lifecycle contract 参考；不复制工程、不运行 Huuuge Collector、不读取 Huuuge Session/Raw。
- 最新 User environment decision：多个测试 App 共用 `Pie64_1 / AppResearch`；隔离责任下沉到 package、project root、Session、Raw、manifest 和账号数据。

| Decision | Capability / component | Result | Cash Frenzy boundary |
| --- | --- | --- | --- |
| Adopt | Start → READY → Stop/Finalize lifecycle | baseline、Spin A、Spin B 均验证；0 errors | Cash 专属 local Session，不调用 Huuuge controller |
| Adopt | manifest、state、Raw immutability | 最小本机实现验证 | 数据仅在 `CashFrenzyResearch/local-only` |
| Adopt | Confirmed / Inference / Blocker discipline | 避免把 command 推断或 opaque input 写成已解码 | Git 只保留 schema/aggregate |
| Adopt | Houdini ARM64 Gadget bootstrap mechanism | 成功命中 Cash arm64 namespace | 仅复用通用加载机制；无 Huuuge hook/agent/schema |
| Wrap | BlueStacks / ADB target binding | `Pie64_1 / AppResearch` + package 双重校验 | 不再依赖旧 display name；拒绝前台 package 不匹配 |
| Wrap | Frida server / Gadget lifecycle | 17.17.0 版本匹配；任务后完整清理 | Gadget 临时复制到 Cash app namespace；不写 Huuuge app |
| Wrap | APK/split inventory 与 hash | 4.78 / 478 / base + 3 splits 复核 | 每个版本重新验证 |
| Build | Cash `BLSocket` + UDP Raw adapter | `sendto/recvfrom` 已达到 F2 | 需要 fd/endpoint 归属和稳定 packet framing |
| Build | Lua request schema adapter | Spin request 字段达到 F3 | 只记录字段名/类型；值保持 local-only |
| Build | Inbound decoder / message dispatch hook | 尚未完成 | 必须定位解密后 `BLMessage` 构造或 dispatch |
| Build | Cash module taxonomy | 尚未完成 | Systems/Themes 与 Huuuge domain 不同 |
| Reject | Huuuge Protobuf descriptor / decoder | 协议不匹配 | 禁止套用 Huuuge schema |
| Reject | Huuuge Session / Raw / database / agent.js | 会污染 evidence | 任意跨 App 读写 fail closed |
| Defer | GUI、完整 Collector、RTP/EV、长期概率 | 超出 Feasibility | ChatGPT Review 与新 Task 前不实施 |

## Reuse Outcome

结论为 **Adopt contract + Wrap host binding + Build protocol adapter**。Huuuge Collector 软件本体不可直接复用；真正可复用的是控制面契约、证据纪律与已审计 native-bridge 加载方法。Cash-specific 的 UDP framing、Lua command/schema、inbound decode 和 module mapping 必须独立实现。

## Exit / Rollback

- Capture、shape probe、Frida server、ADB forward 均已停止。
- Cash 专属 Gadget 与 config 已从 Cash app native-lib 目录删除；重装 App 仍是完整兜底恢复方式。
- 预存 Frida server 二进制未删除，避免破坏既有研究环境；仅终止本次进程。
- `AppResearch` 保留为 User 指定的共享研究模拟器；各 App 的 local project root 与 Raw 不合并。
- 不需要回滚 Huuuge repo、Collector、SVN、飞书或业务仓库。
