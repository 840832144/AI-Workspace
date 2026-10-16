# TASK-0043 — Bingo原客户端与本地服一局可玩闭环

- Status: Ready
- Project key: BINGO-CLIENT-COMPAT
- Owner: User / ChatGPT
- Executor: Codex；研究协作dsh
- Priority: P0
- Date: 2026-10-16
- User decision: Confirmed；按完整规格连续实施，不逐微步骤等待Review。
- Reservation: remote-CAS pending-main；独立linked worktree正式分配，未finalize。

## Goal

唯一执行正文为[EXECUTION_SPEC.md](support/bingo-client-local-round-20261016/EXECUTION_SPEC.md)，来源09f6112/76b6b6c，与User附件逐字一致。交付原客户端大厅→单卡选票→持续叫号/手动填格→至少一种局内道具→合法Bingo→正常结束回大厅→可再次入局；自制合成牌面/本地票，不用JSON样件或自研Unity界面代替。

Codex负责独立兼容工程、服务/适配、整合、启停、测试和最终交付；dsh负责既有获准资料的协议/客户端研究和接入诊断。核实共同受控目录并维护唯一INTEGRATION.md，研究输出与业务代码分开写入。

## Safety与Non-goals

TASK-0039仍User暂停；TASK-0041验证仍暂缓，业务82c2dd9和旧包0.2.1保持原状。新任务测试正常进行，不使用旧线上预算。未获准的实例、DNS/hosts/代理/CA/Hook等环境变更按规格§6集中提出，其他本地开发继续。不修改原APK/安全组件、不携带线上凭据或允许原服回退，不扩权、不线上消费。不自动合并、发布、SVN或finalize。

## Acceptance与Deliverables

按规格§3/§7完成同候选实际原客户端闭环、结构化数据对应、网络隔离/可回滚、自有进程启停与User可复玩入口。至少一次真实局内道具及合法Bingo，返回后新局无残留。交付受控源码/Schema/固定场景、可运行服务、PLAY.md、RESULT.md及证据入口；原APK/Raw不进公共Git。

## Gate 0与Handoff

latest main898358f为祖先；登记前完整scan/validate为19 canonical、0冲突/错误，6既有legacy警告。remote-CAS实际返回TASK-0043，不复用其他分支的TASK-0041/0042。登记后重建Registry校验并推送，再实施。Workspace Sync已运行，ON_DEMAND/provider不可用、6 stale/0 conflict；以本轮Git/附件为准。

[共同接管](../handoff/BINGO-CLIENT-LOCAL-ROUND-20261016.md)；[项目状态](../projects/bingo-client-compat/STATUS.md)。独立治理工作树D:\AI-Workspace-bingo-client-local-round，沿用PR #23。业务拟建D:\BingoClientLocalRound，发现既有目录则先核对，不覆盖旧工程。Subagents: none；dsh为User已有并行研究会话，不由本任务创建。
