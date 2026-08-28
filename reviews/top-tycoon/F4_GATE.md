# Top Tycoon F4 Gate

| Gate | Result | Evidence / blocker |
|---|---|---|
| 两个独立且包含真实 User 操作的 Session | Pass | managed Session 2（1 Spin）与 Session 3（2 Spins）均 clean-stopped |
| 两个 Session 恢复同一核心 Spin schema | **Fail** | 两边只重复恢复 `CGUploadCoin + CGSaveUserdata`；不是 direct Spin input/result schema |
| 累计目标 20 个有效普通样本 | **Fail** | User manual total 6；managed valid denominator 3；Task Stop condition 已触发 |
| direct Spin input + Result/Reward/Balance 可关联字段 | **Fail** | direct resource upload present；Spin input、Result、Reward/Win 不存在于已恢复边界 |
| 次级模块目录或结构边界 | Pass | Building static package/type directory + User onboarding video；无逐笔值入 Git |
| package/version/foreground preflight | Pass | `Pie64_5 / topTycoon / com.monopoly.dream.idle.king / 1.0.12 (12)` live verified |
| Session/Raw/manifest/inventory | Pass | local-only directories and stopped manifests；Git 仅保存 value-free aggregate |
| 确定性 start / capture / stop / cleanup | Pass | same managed probe reused without rewrite；Gadget/server/forward/Root all restored |
| 跨 Session 无临时业务逻辑改写 | Pass | Session 2 → 3 使用同一脚本与同一边界 |
| Raw / identity / account privacy | Pass | APK/SO/Raw/values local-only；Git secret/value scan 通过 |

## Decision

**F4 = Fail；当前 F3。**

F4 的失败不是单纯样本不足：核心 blocker 是 Top Tycoon 本轮可见架构没有 direct server Spin request/result/reward chain。继续增加 Spin 只会重复状态上传，不能把 Derived client state 变成 direct fields。按 Task Stop condition 停止，禁止以更多资源消耗或无界 trace 强行提高等级。
