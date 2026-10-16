# TASK-0043 — Bingo原客户端与本地服一局可玩闭环

- Status: In Progress
- Project key: BINGO-CLIENT-COMPAT
- Owner: User / ChatGPT
- Executor: Codex；研究协作dsh
- Priority: P0
- Date: 2026-10-16
- User decision: Confirmed；按完整规格连续实施，不逐微步骤等待Review。
- Reservation: remote-CAS pending-main；独立linked worktree正式分配，未finalize。

## Goal

完整执行正文为[EXECUTION_SPEC.md](support/bingo-client-local-round-20261016/EXECUTION_SPEC.md)，来源09f6112/76b6b6c，与User附件逐字一致。交付原客户端大厅→单卡选票→持续叫号/手动填格→至少一种局内道具→合法Bingo→正常结束回大厅→可再次入局；自制合成牌面/本地票，不用JSON样件或自研Unity界面代替。

已接纳10e6aa5的[C4与dsh复用补充](support/TASK-0043/DSH-CONTINUATION-AND-REUSE-20261016.md)及User后续抄送。结果A仍为原客户端完整一局；结果B由dsh并行完成独立Unity单卡/格子/buff/基础道具可编辑样件，必须实际导入、检查引用、修改保存重开及最小交互，不以PNG数量或登录背景代替。保留恢复基线与源对象映射，重建/占位显式标注，TypeTree与代码载体核验并行；不等stub策略批准。Codex负责独立兼容工程、服务/适配、整合、启停、测试和最终交付；dsh继续协议/客户端研究和接入诊断。核实共同受控目录并维护唯一INTEGRATION.md，研究输出与业务代码分开写入。

## Safety与Non-goals

TASK-0039仍User暂停；TASK-0041验证仍暂缓，业务82c2dd9和旧包0.2.1保持原状。新任务测试正常进行，不使用旧线上预算。限定C4范围已由User确认，同范围不再逐次询问；可在现有实例做Root、专属隔离/reverse、目标进程必要地址/启动配置插桩，按补充交接单一控制者。TLS校验关闭、CA、DNS/hosts/代理、APK/签名/完整性/保护组件/SELinux更改仍排除。不修改原APK/安全组件、不携带线上凭据或允许原服回退，不扩权、不线上消费。不自动合并、发布、SVN或finalize。

## Acceptance与Deliverables

按规格§3/§7完成同候选实际原客户端闭环、结构化数据对应、网络隔离/可回滚、自有进程启停与User可复玩入口。至少一次真实局内道具及合法Bingo，返回后新局无残留。交付受控源码/Schema/固定场景、可运行服务、PLAY.md、RESULT.md及证据入口；原APK/Raw不进公共Git。

## Gate 0与Handoff

latest main898358f为祖先；登记前完整scan/validate为19 canonical、0冲突/错误，6既有legacy警告。remote-CAS实际返回TASK-0043，不复用其他分支的TASK-0041/0042。登记后重建Registry校验并推送，再实施。Workspace Sync已运行，ON_DEMAND/provider不可用、6 stale/0 conflict；以本轮Git/附件为准。

[共同接管](../handoff/BINGO-CLIENT-LOCAL-ROUND-20261016.md)；[项目状态](../projects/bingo-client-compat/STATUS.md)。独立治理工作树D:\AI-Workspace-bingo-client-local-round，沿用PR #23。业务D:\BingoClientLocalRound已建独立本地Git，无远端。Subagents: none；dsh为User已有并行研究会话，不由本任务创建。

## 2026-10-16 当前开发检查点

治理登记288ebb0保留，业务8f5d0af在独立本地Git，无远端。原客户端在现有实例的隔离Android测试用户中，实际接受本地性能配置/热更配置/GDS，进入Login as Guest；普通点击的原生HTTP登录topic101已到本地，认证应答仍未实现。尚未大厅、对局、基础道具、Bingo或正常返回，结果A未完成，不提交最终Review。

实际服务HTTP/WebSocket局部回归52项通过。旧bv_ws索引对应编号body被后续覆盖，撤回旧200/200、19 CallBall及第166帧来源归因；保留旧结果并标为失效。改从原始mitm归档直接导出连续前500条：500/500封包、35 CallBall、2 State、2 Join解码，未知字段保留。M2文本来源关联独立于这些body，历史7项检查不升格为当前运行证明。

User的限定C4授权已执行：先隔离再启动，同实例独立Android测试用户复用未改APK；原用户未启动，静态GDS只读复用，未复制原账号凭据/状态或消费。实际仅修改目标进程中已绑定的地址配置字符串，没有Frida/保护代码修改/玩法状态伪造。实例控制由Codex协调，可按补充在共同目录交接给dsh；离线工程工作不停。临时网络状态与回收入口留受控共同目录，不在公共Git登记运行endpoint。

dsh b2/b3及b4 SAMPLE-RUN.md已收到；b4报告场景生成、重载与16项直接方法自检通过，Codex未独立复跑，不等同真实UI输入。按[评论6209187825](https://github.com/840832144/AI-Workspace/pull/23#issuecomment-6209187825)保留骨架，继续原层次、来源文件＋PPtr与依赖解析、关键Sprite及布局恢复，补一次正常打开、真实点击、可见属性修改保存重开。恢复/重建/原本纯色/仍缺失分开记录；COIN_SQUARE和充能阈值未证实部分仅作预览采用规则，不覆盖其他工程。旧“消费链全部闭合、无其他覆盖点”和“MonoScript无方法体因此全脚本重写”结论不采用。两个启动请求已通过共同目录codex-out/ACK-006.md答复，原生Socket地址静态链与实际启动消费分开；dsh负责B样件并持续补A消费者。

下一步连续实现本地合成认证User、原版初始化/局内适配并完成同候选真实一局；dsh连续完成可编辑可交互样件。受控复算与失败入口D:\BingoClientLocalRound\DEVELOPMENT-RESULT.md、artifacts/evidence、runs；历史原APK/资源/数据不上传。旧任务暂停/暂缓、原账本及不合并/发布/SVN/finalize不变。Subagents: none。

此前79ca1c2/2c55072的“尚未授权、尚未启动、ACK待收及200条来源统计”为历史，当前由本节和补充覆盖，旧提交不重写。
