# Bingo原客户端本地一局状态

- Task: [TASK-0043](../../tasks/TASK-0043-BINGO-CLIENT-LOCAL-ROUND.md)
- Status: In Progress；Gate 0治理288ebb0已登记校验推送。
- Spec: [完整执行规格](../../tasks/support/bingo-client-local-round-20261016/EXECUTION_SPEC.md)，09f6112/76b6b6c。
- 目标：原客户端单卡持续游玩、基础道具、合法Bingo、正常结束返回并可再开；未接通，不计完成。
- 交换目录：D:\DSH_work\bingo-local-round；Codex维护INTEGRATION.md/codex-out，research-dsh只读，尚未收到双向ACK。
- 业务目录：D:\BingoClientLocalRound，独立本地Git79ca1c2，无远端。服务构建与HTTP/WebSocket 46项通过；历史前200帧200/200、19条CallBall解码、来源归属7项通过，均不替代当前原客户端验收。
- 待完成：原版初始化/动作/道具/判型/正常结束适配、接入与隔离方案、实际一局及复玩入口；当前未可玩，未最终Review。
- 当前实例：User指定现有MuMu index0/Android15，取代未执行的新实例提案。仅只读核对，原账号数据保留；Root/网络/CA/Hook等不由复用实例推定批准。
- 旧任务：TASK-0039暂停；TASK-0041验证暂缓，不覆盖代码/规则/预算。
- Subagents: none。
