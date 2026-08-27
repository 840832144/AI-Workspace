# TASK-0022 Reuse Matrix

## Baseline

- Huuuge reference：`huuuge-android-research@4a5dddf7782307c6a8f368c9f1dc6390eec6f65b`，Collector 1.0.1。
- 使用方式：只读架构与 Workflow 参考，不复制工程、不运行 Collector、不读取 Huuuge Raw。

| Decision | Capability / component | Reason | Cash Frenzy boundary |
| --- | --- | --- | --- |
| Adopt | Start → READY → Stop/Finalize lifecycle contract | 已验证、对游戏无关 | 新实现不得调用 Huuuge runtime |
| Adopt | Session alias、manifest、automatic markers | 可复查采集范围 | 使用 Cash Frenzy 独立 namespace |
| Adopt | Raw immutability、inventory/catalog、sanitized report | 证据与隐私模式通用 | Raw 和 DB 绝不进入 Huuuge 路径 |
| Adopt | Evidence L0–L4 与 Confirmed/Hypothesis discipline | 防止 static 被误写为 live | 当前结论最高 Static L1 / F1 |
| Wrap | BlueStacks/ADB target binding | Host 工具可复用 | 强制 instance=`CashFrenzyResearch`、package 精确匹配 |
| Wrap | APK/split inventory 与 hash | 通用静态步骤 | package/version/ABI 每次现场复核 |
| Wrap | Planner GUI/health-check 模式 | 策划入口可复用 | 不复用 Huuuge 按钮、目录或状态文件 |
| Build | `BLSocket` / TLS plaintext Adapter | Cash Frenzy-specific | 先定位明文边界，不改写请求 |
| Build | LuaJIT command/schema mapping | 未发现业务 descriptor | 只恢复最小 Spin 字段链 |
| Build | Cash Frenzy module taxonomy | Systems/Themes 结构不同 | Slots、Feature、Events、Offers 分开标级 |
| Reject | Huuuge Protobuf descriptor / decoder | 协议与 package 不同 | 禁止套用 Huuuge schema |
| Reject | Huuuge Session / Raw / database / Collector process | 会污染 evidence | 任意跨读写均 fail closed |
| Defer | 完整 Collector、RTP/EV、长期概率 | 超出 Feasibility | ChatGPT Review 与新 Task 前不实施 |

## Exit Cost

若动态证明失败，只保留本次 static inventory 与独立本机目录；不需要回滚 Huuuge、SVN、飞书或业务仓库。若证明成功，后续也应新建 Cash Frenzy Adapter Task，而不是扩大 TASK-0022。
