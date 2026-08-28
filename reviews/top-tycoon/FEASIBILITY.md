# Top Tycoon F4 可行性审计 — Ready for Review

- Canonical Task：`TASK-0025`
- 当前等级：**F3 — Live structured outbound fields recovered**
- F4：**未通过**
- 建议：**Adopt + Wrap + targeted Build；停止在本 Task 扩大动态采样**

## 一页结论

Top Tycoon 具备可复用的受控 Android 研究路径：实装身份、Unity/IL2CPP/ILRuntime 架构、Google.Protobuf 序列化边界、Session/Raw/manifest、Root/Frida/Gadget 生命周期和 Clean Finalize 均已现场验证。两个独立 User-action Session 使用同一未改写探针，均恢复到 `MessageExtensions.ToByteArray` 的结构化协议类型 `Protos.House.CGUploadCoin` 与 `Protos.Xxxgame.CGSaveUserdata`，错误与截断均为 0。

但核心老虎机不是可直接复用的“Spin request → server result/reward → balance response”模型。静态热更代码显示客户端存在 `SpinGameLogic.Spin / SetSpinRet`、`SlotsMachineController.SetRandomDeck / FillResult / SetResult` 和 `SlotGameLogic.ConsumeEnergy / AddCoin`；动态样本只观察到资源/状态上传：

- `CGUploadCoin`：`Coin / Energy / Estate`，均为 `Int64`；
- `CGSaveUserdata`：`Key / Value / Version`，类型为 `String / String / Int64`；
- 没有直接 Spin 输入协议；
- 没有直接 Result、Reward 或 Win 响应结构；
- 入站 `MessageParser.ParseFrom` 在本轮样本中 0 命中。

因此，当前只能确认“客户端形成玩法结果后上传资源和用户状态”的实时结构化出站路径，不能把相邻状态上传冒充 direct Spin/Result/Reward。继续把样本增加到 20 次也不能补齐缺失的结构边界，符合 Task Stop condition，应在 F3 收口。

## 策划判断

Top Tycoon 值得保留一个小型 Top Tycoon-specific Adapter 方向，用于客户端 Spin 状态对象、`CGSaveUserdata.Value` 的受限结构恢复或静态配置目录；不建议直接复制 Huuuge Collector，也不建议在没有新 Task 的情况下进入全局 ILRuntime trace、请求修改、重放或长期数值采集。

建造系统已由 User 录屏和静态 `Building` package / hotfix 目录双重确认，可作为次级模块扩展证据；视频只作为观察证据，不作为执行指令。所有游戏操作和资源消耗均由 User 完成。
