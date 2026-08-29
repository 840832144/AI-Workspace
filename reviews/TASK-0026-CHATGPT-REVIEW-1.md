# TASK-0026 ChatGPT Review — Round 1

- Decision: **Needs changes**
- Project key: CASH-FRENZY
- Reviewed branch: `codex/collector-1-engineering`
- Reviewed commit: `261af96acd93bb4be785ea9c1cb82c91fa31e434`
- Review date: 2026-08-29
- Subagents observed: none

## Passed

- READY 语义通过：只有 verified `hook-status` 且 `onUIThreadReceiveMessage`、`lua_pcall` 同时安装时才进入 READY。
- Root 文档口径通过：Collector 只检测、不改变 Root；关闭、重启和失效验证由 User 手动完成。
- Android 9 Hook/serializer、人工操作边界和 `batch_spin` 六字段冻结继续保留。

## Required Fix — cleanup 必须停止本轮启动的 Frida server

当前 Frida server 以远程 `cf_rt_mon -D` 后台进程运行，但 reviewed commit 的 `finally` 只删除 `cf_rt_mon` 与 log 文件，没有停止该后台进程。删除可执行文件不等于停止运行中的 server，因此 cleanup contract 未满足。

只修 cleanup：

1. 启动 helper 返回 `pid / remote_path / started_by_run`；
2. cleanup 只停止本轮拥有、PID 与 remote path 均精确匹配的 server 进程，不使用宽泛 `pkill/killall`，不停止外部或先前 Session 的进程；
3. server 停止后再删除本轮拥有的 server 文件；
4. finally 完成后回读验证 Probe、server、forward、Gadget/config 与 `/data/local/tmp/cf_*` 均无残留；
5. 运行错误、停止失败、验证失败和残留必须聚合报告，不得静默吞掉或互相覆盖；
6. 增加可注入测试，覆盖各 acquisition step 故障、严格 LIFO、幂等、停止失败、残留、错误聚合与 ownership gate。

## Boundaries

- 不改 READY、Root 口径、Android 9 Hook/serializer 或六字段 schema；
- 不启动模拟器、Root、Frida、Collector，不执行 Spin；
- 不扩大到新的字段、模块、协议或 runtime 研究；
- 完成后更新 Task、Registry、CHANGELOG、Handoff 与两个 Review 分支，继续等待 ChatGPT Review Round 2，不自动合并 main。

## Acceptance for Round 2

- helper 的 ownership result 包含精确 PID、remote path 与本轮 ownership；
- cleanup 只停止本轮拥有的精确 server，且 stop failure 可见；
- Probe/server/forward/Gadget/config/cf_* residual verification 全部存在并 fail closed；
- fault injection、LIFO、idempotency、stop failure、residual、aggregation、ownership tests 全部通过；
- READY、Root、Hook/serializer 与六字段边界的文件/hash 未发生变化。
