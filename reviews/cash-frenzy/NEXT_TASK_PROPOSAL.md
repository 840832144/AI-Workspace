# TASK-0022 Next Task Proposal — Draft Only

当前不创建新 Task、不分配 ID、不自动执行。

## Recommended Direction

若 ChatGPT 接受 TASK-0022，建议由 User 决定是否建立 **Cash Frenzy Inbound Protocol Decoder and Passive Collector Adapter** Candidate，先做 decoder，再决定完整 Collector。

建议范围：

- Wrap `Pie64_1 / AppResearch` + exact package binding，保持每 App 独立 project root / Session / Raw。
- 固化 Houdini ARM64 bootstrap、Frida version gate、Cash Gadget staging 与可验证 cleanup。
- 保留 UDP `sendto/recvfrom` Raw 与 BLSocket/Lua request schema hook。
- 定位 `BLMessage` construction、decode 或 UI dispatch 的解密后入站边界。
- 恢复最小 `BATCH_SPIN` request → result/update → win/balance field chain；值只留 local Raw，Git 只保存 schema。
- 建立 Cash 专属 manifest、index、sanitized inventory 与 Clean Finalize；不得调用 Huuge Session/decoder/agent。

## F4 Acceptance Gate

只有同时满足以下条件才可宣称 F4：

1. 至少两个独立 Session 可重复捕获同一 Spin request/result schema。
2. inbound result/win/balance/update 至少恢复一种稳定结构，且与 User action 对齐。
3. unknown/undecoded bytes fail-open 保存到 local Raw，不能丢失。
4. package/instance/version/Frida/Gadget preflight 与 cleanup 可自动验证。
5. Huuge Collector、Session、Raw、SVN 和业务仓库保持不变。

## Explicit Non-goals

- 不做 RTP/EV、长期概率、自动 Spin 或批量资源消耗。
- 不修改请求、返回值、余额、奖励或服务端状态。
- 不发布飞书正式报告、GUI 或 SVN 包，除非未来独立 Task 明确批准。
- 不从 `client_coins` 字段存在推断真实余额，也不把 command inference 写成 directly observed。
