# Top Tycoon Reuse Matrix

| 决策 | 内容 | 本轮结果 | 边界 |
|---|---|---|---|
| Adopt | Session、manifest、Raw、value-free evidence、clean stop/cleanup contract | 已采用；每个探针 Session 有独立目录、状态与 stopped manifest | 不复制其他游戏 Raw、账号或业务 schema |
| Adopt | BlueStacks identity / foreground / package / version guard | 已现场确认 `Pie64_5 / topTycoon / 127.0.0.1:5605` | identity 不一致时 fail closed |
| Wrap | Top Tycoon Unity/IL2CPP + native bridge + arm64 Gadget 生命周期 | 已完成专属 bootstrap、边界探针和确定性清理 | 仅限 `topTycoon` 实例与包 |
| Build | xLua protobuf shape probe | 已验证不适用于核心 Spin；3 次手动 Spin 0 命中 | 不再扩大此路线 |
| Build | managed Google.Protobuf boundary probe | 两个 User-action Session 重复命中协议类型；0 error / 0 truncation | 不记录 payload 或字段值 |
| Build later | ILRuntime 客户端 Spin state adapter 或 `CGSaveUserdata.Value` 受限结构恢复 | 本轮未执行；可能补齐 Result/Reward | 必须新 Task、独立安全预算与 Review |
| Build later | static config / module catalog | Hotfix、YooAsset、Building/Slots 配置入口已定位 | 不做 RTP/EV 或长期概率结论 |
| Do not reuse | Huuuge/Cash Frenzy 的业务 decoder、Raw、账号、schema | 未使用 | 只复用 provider-neutral contract |
| Stop | 20-Spin F4 Gate、全局 ILRuntime trace、完整 Collector | 本轮停止 | 缺少 direct Spin/Result/Reward，增加操作不能消除 blocker |

## 退出成本

本轮新增内容是 Top Tycoon-local 探针和脱敏证据，不改变 Huuuge/Cash Frenzy Collector。若后续不继续，删除本机研究目录即可；Git 只保留审计结论和 schema 摘要。
