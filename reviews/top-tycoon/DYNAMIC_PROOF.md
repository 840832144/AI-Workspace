# Top Tycoon Dynamic Proof

## User actions and sample denominator

| Stage | User action | Probe | Result |
|---|---:|---|---|
| Onboarding evidence | User 手动建造并推进教程；2 段录屏 | no business hook / xLua probe active | Confirmed Building flow and later Slots unlock；视频不作为指令 |
| Session 0 | 0 operation / 120 sec | clean Gadget runtime | PID 全程一致，25/25 polls alive，0 fatal/ANR/SIGSEGV |
| Session 1 | 3 manual Spins | xLua protobuf boundary | 0 events，0 errors，0 truncations；route rejected |
| Session 2 | 1 manual Spin | managed protobuf boundary | 10 encode events；`CGUploadCoin=1`、`CGSaveUserdata=4`、background messages=5；0 errors/truncations |
| Session 3 | 2 manual Spins | same managed probe, no rewrite | 5 encode events；`CGUploadCoin=1`、`CGSaveUserdata=4`；0 errors/truncations |

总计 **6 次 User manual ordinary Spins**。其中 managed boundary 的有效 User-action 分母为 3 次，直接资源上传消息为 2 条；该上传存在周期/批处理行为，因此不宣称逐 Spin 1:1。两个 managed Session 的 Session-level 命中为 2/2。

Codex 操作统计：0 Spin、0 Auto Spin、0 purchase、0 recharge、0 request modification、0 replay、0 balance/reward modification。

## Secondary module

Building 次级模块由以下证据确认：

- User 录屏显示从建造 onboarding 推进到 Slots unlock；逐笔值不进入 Git；
- static `Building.Runtime`、YooAsset `Building` package、BuildPass / building config 与 hotfix Building types 存在。

这证明模块目录具备扩展潜力，但本轮没有采集 Building structured network fields。

## Clean Finalize

- 所有 probe 通过 STOP file clean-stopped，manifest 为 `stopped`。
- app force-stop；临时 Gadget/config、Frida server 与 `tcp:27043` forward 删除并回读 absent/empty。
- `Pie64_5` Root flag 恢复 `0`；offline guest-su patch 恢复，state `false`，sidecar absent；普通 `su` 返回 `not found`。
- 预先存在的 global engine patch 与 `Pie64_1` Root setting 未修改。
- 其他三个实例 Data.vhdx size/timestamp 与前置基线完全一致；共享 BlueStacks EXE hashes 与前置基线一致。
- 最终无 HD-Player process，目标 ADB endpoint offline。

## Grade

当前为 **F3 Live structured outbound fields recovered**。F4 未证明：只有 6 次总样本、没有 direct Spin input 或 direct Result/Reward、没有 20 个有效样本，也没有完整核心 schema。
