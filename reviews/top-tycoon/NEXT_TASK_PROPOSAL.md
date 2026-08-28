# Top Tycoon Next Task Proposal

本文件只提出候选方向，不自动创建或执行 Task。

## Recommended: targeted client-state adapter spike

目标：在不进入全局 ILRuntime trace 的前提下，验证能否从以下两处之一恢复 value-free Spin result schema：

1. `SpinGameLogic.SetSpinRet / CallSpinRet` 的特定 ILRuntime method adapter；
2. `CGSaveUserdata.Value` 在写入 protobuf 前的受限 JSON/structured state boundary。

最小验收：

- 只 Hook 指定 method/object boundary；禁止全局 interpreter trace；
- 先 0-operation baseline，再由 User 最多 3–5 次 manual Spin；
- direct fields 至少包含 result type 与 reward/coin/energy 中一类；
- 0 payload/account values 进入 Git；
- 若仍只得到 opaque `Value` 或需进入新协议/高频 trace，立即 Stop。

## Alternative: static config/module catalog

如果动态 adapter 风险或成本过高，优先整理 YooAsset / hotfix 的 Slots、Building、Attack、Event 配置目录与 type catalog。该方向适合系统结构研究，不宣称 RTP、EV、服务端 RNG 或长期概率。

## Not recommended now

- 不建设完整 Collector；
- 不复制 Huuuge/Cash Frenzy decoder；
- 不做 20-Spin 追加采样来掩盖 direct chain 缺失；
- 不进入 request forgery/replay、余额/奖励修改、反作弊绕过或付费研究。

下一方向需经 Product Roadmap 判断、Candidate 与官方 allocator 创建新的 canonical Task；`TASK-0025` 不自动续写。
