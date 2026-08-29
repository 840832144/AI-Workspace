# TASK-0026 ChatGPT Review — Round 2

- Decision: **Needs changes**
- Project key: CASH-FRENZY
- Reviewed branch: `codex/collector-1-engineering`
- Reviewed commit: `4e6f0625e2e39dfeb6ebb4dfb2fd6a29d5c1999c`
- Review date: 2026-08-29
- Subagents observed: none

## Passed

- Round 1 cleanup contract 通过：严格 LIFO、幂等、只停止本轮拥有且 PID 与 remote path 精确匹配的 server，停止和残留失败均显式聚合。
- READY、Root、Android 9 Hook/serializer 与 `batch_spin` 六字段冻结继续通过。

## Required Fix — Cleanup 集合返回语义

`run_collector.ps1` 与 `collector/cf_start_frida_server.ps1` 的多个列表函数同时使用 `return ,$array`，调用方再用 `@(...)` 接收，会把空或多项结果包装成嵌套数组。空 PID 因而可能被误判为 ownership residual，空 residual 也可能形成空的 `verify:` 错误。

只修集合返回语义：

1. 列表函数统一移除 `return` 前的一元逗号；
2. 调用方继续使用 `@()`，稳定接收 0/1/N 项；
3. 对实际生产函数补 0/1/2 PID、ADB 行、路径与 residual-error shape 测试；
4. 显式验证空 PID 不触发 ownership residual，空 residual 不生成空的 verify 错误。

## Boundaries

- 保持 LIFO、精确 PID+path、READY、Root、Android 9 Hook/serializer 与六字段不变；
- 不启动模拟器、Frida、Collector，不执行 Spin；
- 不扩大到字段、模块、协议或 runtime 研究；
- 修订后继续等待 ChatGPT Review Round 3，不自动合并 main。

## Resolution submitted for Round 3

- 修订 commit：`CF_collect@4df10ec20e79bb737912c8d1b847fae3659031ae`。
- `run_collector.ps1` 与 helper 的列表函数已移除全部 `return ,`；调用方的 `@()` 保持不变。
- 实际生产函数 shape tests 为 10/10：覆盖 run/helper 的 ADB 行与 exact PID、package PID、远程路径、`cf_*` 路径、0/1/2 residual error、空 PID 与空 verify suppression。
- focused `unittest` 16/16、原 cleanup injection 7/7、PowerShell 5.1 parser 5/5、Python compileall、六字段冻结、privacy scan 与 diff check 全部通过。

## Acceptance for Round 3

- run/helper 不再存在 `return ,`；
- 所有列表调用方使用 `@()` 后稳定得到扁平的 0/1/N 项；
- 空 PID 不产生 ownership residual，空 residual 不产生空 verify error；
- LIFO、精确 PID+path、READY、Root、Hook/serializer 与六字段边界没有其他变化。
