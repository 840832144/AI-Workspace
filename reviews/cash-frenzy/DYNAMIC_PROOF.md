# TASK-0022 Dynamic Proof

- Status: **Complete — Ready for ChatGPT Review**
- Current level: **F3 Live structured outbound fields recovered**
- Environment: `Pie64_1 / AppResearch`
- Package: `slots.pcg.casino.games.free.android` 4.78 / 478 / arm64-v8a
- User action budget: 5 / 5 ordinary Spin used；无自然 Feature

## Environment Decision and Isolation

Task 启动时建议独立 `CashFrenzyResearch` 实例。动态门槛处 User 明确将原 `HuuugeResearch` 重命名为共享 `AppResearch`，并指定后续测试 App 共用该实例；这是本轮最新决定。

共享实例不等于共享数据：Cash Frenzy 的 APK/SO/static、probe、Session、Raw、manifest 与账号数据只存在于 Host-local `CashFrenzyResearch/local-only`。没有写入 Huuuge Session、Raw、database、Collector 或业务仓库。

## Preconditions

- Android 9；ADB alias `emulator-5564`；x86_64 Host ABI + `libnb.so` arm64 native bridge。
- Root 返回 `uid=0(root)`；Host/server/Gadget Frida 均为 17.17.0。
- App package、version、split、ABI 与 foreground activity 全部现场复核。
- Outer x64 attach 无法看到 `libcocos2dlua.so`；通用 Houdini bootstrap 在 Cash 自身 namespace 中临时加载 Gadget 后，arm64 module view 成功。

## Lifecycle Regression

首次后台 READY 测试暴露 Windows manifest reader/atomic replace 的短暂文件锁冲突。该 Session 以 0 Raw / 0 errors Clean Stop；本机 probe 加入有限重试，并改为轮询 append-only READY log。后续 baseline、3-Spin、2-Spin Session 均正常 READY/Stop，未再复现。

## Baseline

15 秒无操作 baseline：

| Direction | Records | Bytes | Unique hashes | Shape |
| --- | ---: | ---: | ---: | --- |
| outbound | 5 | 207 | 3 | opaque binary |
| inbound | 5 | 378 | 3 | opaque binary |

双向记录均非 JSON、gzip、zlib 或 zip；BLSocket heartbeat 与 UDP `sendto/recvfrom` 次数对齐。

## User Actions

- 机台：金猪主题机台；User 未完整记录正式名称。
- Bet：10000（User 现场报告）。
- 第一次：3 次普通手动 Spin，无 Auto Spin、购买或 Feature。
- 第二次：2 次普通手动 Spin，Bet 保持不变，无 Auto Spin、购买或 Feature。
- 合计 5 次，达到 Task 上限；未再要求游戏操作。

## 3-Spin Raw Proof

| Direction | Records | Bytes | Unique hashes |
| --- | ---: | ---: | ---: |
| outbound | 36 | 2,048 | 17 |
| inbound | 38 | 14,793 | 20 |

- 相比 heartbeat baseline，74 条记录中 36 条为 novel records、35 个 novel hashes。
- 恰好 3 个 novel outbound packet 均为 255 bytes，与 3 次 Spin 数量一致。
- 后续出现 1,159–2,526 bytes 的 novel inbound bursts。
- 证据证明 Spin 与双向 network activity 相关，但入站内容仍未解码。

## 2-Spin Structured Proof

| Direction | Records | Bytes | Notes |
| --- | ---: | ---: | --- |
| outbound | 31 | 1,617 | 恰好 2 个 255-byte Spin-correlated packet |
| inbound | 34 | 9,960 | opaque binary；最大 2,260 bytes |

schema-only Lua hook 捕获 13 个 outbound shapes、3 种唯一形态、0 errors；其中 2 个与 2 次 Spin 一一对应：

```text
[1] command-string (length only)
[2] payload-table
    autoSpin: number
    bet: number
    client_coins: number
    free_spins: number
    lines: number
    spin_count: number
    turbo: number
[3] metadata-table
    _timestamp: number
```

只记录字段名、类型和 command length，不记录值。`BLMessage.getObj` 在该 Session 中为 0 次，因此没有 inbound field schema。

## Result

**Confirmed**：F2 live Raw 和 F3 outbound Spin structure 均已达到；start/READY/stop 可重复，User action 与 packet/schema 数量对齐。

**Inference**：command length 10 + static `BATCH_SPIN` + Spin fields + 两次动作关联，高置信推断为 `BATCH_SPIN`，但未直接读取 command value。

**Blocker**：没有 inbound result/win/balance/update schema，无法证明完整数值链、真实余额变化或 F4 decoder。

## Clean Finalize

- 所有 Raw 与 Lua shape Session 均 `stopped`；0 capture/shape errors；0 残留 probe process。
- Cash app force-stop；Cash 专属 Gadget/config 删除；ADB 27043 forward 删除；临时 Frida server process 停止。
- 预存 Frida server binary 未删除；`AppResearch` 保留为 User 指定共享研究实例。
- Huuge repo clean；Huuge Collector、Session、Raw、SVN、飞书和业务仓库未修改。
