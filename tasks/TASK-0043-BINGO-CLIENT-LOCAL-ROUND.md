# TASK-0043 — Bingo原客户端与本地服一局可玩闭环

- Status: In Progress
- Project key: BINGO-CLIENT-COMPAT
- Owner: User / ChatGPT
- Executor: Codex；研究协作dsh
- Priority: P0
- Date: 2026-10-16
- User decision: Confirmed；按完整规格连续实施，不逐微步骤等待Review。
- Reservation: remote-CAS pending-main；独立linked worktree正式分配，未finalize。

## 当前执行范围：2026-10-17 M1-only

已按 User 直接指令选择性接纳支持分支 `chatgpt/task-0043-dsh-reuse-20261016@e124b86` 的完整[专项执行单](support/TASK-0043/M1-ONLY-IMPLEMENTATION-20261017.md)，未合并支持分支或改动其他任务。**M1 是本任务唯一 Current 开发焦点；M2 冻结，保留现有工程、包、资源及差异记录。** M2 最新评价“功能基本正常，但与原版效果相差非常大”只作为 User 反馈，不标原版验收通过。下方 M1/M2 并行安排为历史，被本节覆盖。

本安全点核对治理 5175359 / 业务 19287fe；原认证、Backpack、WebSocket、新增初始化及 Bingo.Core 均复用。正式入口目前仍拒绝 203，100007 仅结构解码后因原生回合未绑定拒绝；大厅/单卡完整状态机未接入，未伪装成可玩。共同目录仍是旧 R2 合同，203 仍误读 ErrResp.Code=201，1001/2403/1205 下游及序号/恢复未闭合；未收到 ACK-013 后的新 M1-CONSUMER-CONTRACT。

已直接在既有共同目录交付 ACK-014，明确现有代码接入点与整组缺口：dsh 先修 203、初始化消费者，再延伸普通单卡入局、叫号、手填、基础道具、Bingo、阶段/结算/离局与再入局；提供来源、证据等级、机读映射和可复算脚本。Codex 收到可用的一组后接入现有工程，不等研究全量完毕，但不猜未知语义、不重新开发服务、不转做 M2。ACK 落盘不等于 dsh 已执行或已交付。

本轮仅范围接纳、静态调用链核对及直接交接，**无新增业务行为、编译、产品功能/回归或设备测试**；未重复构建未变代码冒充进展。原生实验停止保持，所有成品测试由 User 承担。完整离线候选就绪后才一次提出含隔离、时长、失败停止、Logout 实际写盘、缓存/重启与回滚的复验方案，等待 User 确认。旧 C4 排除、约15分钟同一卡点、TASK-0039 暂停/TASK-0041 验证暂缓、不 merge/release/SVN/finalize 均不变。

Task 保持 In Progress / PR #23 Draft / reservation pending-main。Subagents: none。

## Goal

完整执行正文为[EXECUTION_SPEC.md](support/bingo-client-local-round-20261016/EXECUTION_SPEC.md)，来源09f6112/76b6b6c，与User附件逐字一致。交付原客户端大厅→单卡选票→持续叫号/手动填格→至少一种局内道具→合法Bingo→正常结束回大厅→可再次入局；自制合成牌面/本地票，不用JSON样件或自研Unity界面代替。

历史安排（结果B负责人已由下文c3bc731覆盖）：已接纳10e6aa5的[C4与dsh复用补充](support/TASK-0043/DSH-CONTINUATION-AND-REUSE-20261016.md)及User后续抄送。结果A仍为原客户端完整一局；结果B由dsh并行完成独立Unity单卡/格子/buff/基础道具可编辑样件，必须实际导入、检查引用、修改保存重开及最小交互，不以PNG数量或登录背景代替。保留恢复基线与源对象映射，重建/占位显式标注，TypeTree与代码载体核验并行；不等stub策略批准。Codex负责独立兼容工程、服务/适配、整合、启停、测试和最终交付；dsh继续协议/客户端研究和接入诊断。核实共同受控目录并维护唯一INTEGRATION.md，研究输出与业务代码分开写入。

## Safety与Non-goals

TASK-0039仍User暂停；TASK-0041验证仍暂缓，业务82c2dd9和旧包0.2.1保持原状。新任务测试正常进行，不使用旧线上预算。限定C4范围已由User确认，同范围不再逐次询问；可在现有实例做Root、专属隔离/reverse、目标进程必要地址/启动配置插桩，按补充交接单一控制者。TLS校验关闭、CA、DNS/hosts/代理、APK/签名/完整性/保护组件/SELinux更改仍排除。不修改原APK/安全组件、不携带线上凭据或允许原服回退，不扩权、不线上消费。不自动合并、发布、SVN或finalize。

## Acceptance与Deliverables

按规格§3/§7完成同候选实际原客户端闭环、结构化数据对应、网络隔离/可回滚、自有进程启停与User可复玩入口。至少一次真实局内道具及合法Bingo，返回后新局无残留。交付受控源码/Schema/固定场景、可运行服务、PLAY.md、RESULT.md及证据入口；原APK/Raw不进公共Git。

## Gate 0与Handoff

latest main898358f为祖先；登记前完整scan/validate为19 canonical、0冲突/错误，6既有legacy警告。remote-CAS实际返回TASK-0043，不复用其他分支的TASK-0041/0042。登记后重建Registry校验并推送，再实施。Workspace Sync已运行，ON_DEMAND/provider不可用、6 stale/0 conflict；以本轮Git/附件为准。

[共同接管](../handoff/BINGO-CLIENT-LOCAL-ROUND-20261016.md)；[项目状态](../projects/bingo-client-compat/STATUS.md)。独立治理工作树D:\AI-Workspace-bingo-client-local-round，沿用PR #23。业务D:\BingoClientLocalRound已建独立本地Git，无远端。Subagents: none；dsh为User已有并行研究会话，不由本任务创建。

## 2026-10-16 离线修复与测试交接

User对当前dfd312c恢复样件试玩反馈：“流程没啥问题”。记录为结果B流程暂无明显问题，不扩大为逐项边界、编辑保存重开、原版视觉或结果A通过；没有新增代码或重跑测试。后续仍由User测试，Task保持In Progress。

已接纳[卡点Review 6211006045](support/TASK-0043/CHATGPT-BLOCKER-REVIEW-20261016.md)，结论Needs changes，Task保持In Progress。沿c3bc731分工与513f5da/d35c8a0基线继续；dsh优先研究已认证到大厅的整组初始化/SyncCache，并行补实际组件→Sprite→布局映射。七类请求只是起点，不默认全空、不重挖地址和Backpack。Codex推进现有恢复工程及有依据的离线适配；当前未收到新初始化合同，不声明已接入。

业务dfd312c已修CardCandidate普通输入与补填的唯一充能路径、运行时道具绑定、合法Bingo、结束/重置再玩；保留原层次，对已知错图作明确占位，原版呈现仍待实际引用映射。Windows试玩程序已构建。User改变测试分工前18项组件/保存重开检查通过，仍只是局部历史证据；实际鼠标验证因捕获接口失败后User按Esc停止，尚未完成。

**最新User决定：后续测试全部由User承担；Codex负责开发、打包和交接，不再自动运行功能/回归测试或操作试玩。** 成功验收只按实际User反馈登记。试玩入口D:\BingoClientLocalRound\artifacts\card-recovery\BingoCardRecovery.exe；短流程说明在工程PLAY.md和包内试玩说明.md。此候选不等于原版呈现或结果A完整一局通过。

原客户端设备试错仍停止。研究与离线版本就绪后，一次提交复验依据/版本/检查点、明确时长、失败判据与恢复步骤，必须含客户端实际Logout/写盘，由User决定恢复并测试。普通同一卡点约15分钟约束继续，不能换topic/换人重置。既有C4排除项、旧任务暂停/暂缓与不合并/发布/SVN/finalize不变。

本次仅记录开发和交接，无新增测试；Registry身份/Status/Project key未变，最近有效校验仍为ef1839d前的20 canonical、0冲突/错误、6既有legacy警告，不冒称本轮重跑。Subagents: none。

## 历史：ef1839d分工接管检查点

已接纳[f1a4a4b成品收口要求](support/TASK-0043/DSH-DELIVERABLE-FIRST-20261016.md)与[c3bc731分工调整](support/TASK-0043/ROLE-SPLIT-20261016.md)。**Codex统一负责结果A/B工程实现、UI、交互、测试与打包；dsh主责研究取证和提取/解析/验证脚本。** 旧dsh结果B工程负责人安排仅作历史；两项产品标准与限定C4边界不变。

dsh已冻结并交出CardCandidate完整工程，295条目包级核对通过；Codex在原客户端停止的检查点接收为受控工作副本，业务基线d35c8a0，原ZIP及dsh原目录保留。未另起Demo。随包15项自检/重开/双视口渲染为dsh证据，尚未由Codex完整复跑；普通点击充能绑定、道具监听、结束重置、屏幕输入及精确图片/布局仍待修复，旧“已收口”结论不采用。

业务当前513f5da：本地合成认证、保存令牌续接及六条初始化应答已被原客户端实际接受；Backpack非空修复后实际发出GetProfileState等后续初始化。服务75项局部HTTP/WebSocket回归通过，当前原客户端仍停在加载页，未大厅/一局/结束返回。后续初始化模块及重连缓存消费者尚未闭合；不能以空响应或局部测试冒充完整结果。服务与测试游戏已停，临时隔离/reverse已按owner回收，返回原Android用户且未启动原游戏。受控结果/失败/复现入口D:\BingoClientLocalRound\DEVELOPMENT-RESULT.md与共同目录INTEGRATION.md。

User新增执行约束：普通单一卡点约15分钟未解决即停止该点，报告已试方法、证据与待决策项，等待User Review讨论后决定继续修改或先由dsh研究；不按微步骤改名延长同一阻塞，提前批准测试按约定时长。当前登录初始化卡点已停止并准备整模块研究清单，后续实施等User讨论决策；这是本轮调试约束，不重置原Task/进度或新增阶段审批。

研究增量直接进入research-dsh；正式工程与INTEGRATION/codex-out由Codex写入。REA说明已收到、CLI实测6.5.0；未新装或注册MCP，未将未配置的IDA反编译声称可用。TASK-0039暂停、TASK-0041验证暂缓；不扩权、不合并/发布/SVN/finalize。Subagents: none。

## 历史：8f5d0af开发检查点

治理登记288ebb0保留，业务8f5d0af在独立本地Git，无远端。原客户端在现有实例的隔离Android测试用户中，实际接受本地性能配置/热更配置/GDS，进入Login as Guest；普通点击的原生HTTP登录topic101已到本地，认证应答仍未实现。尚未大厅、对局、基础道具、Bingo或正常返回，结果A未完成，不提交最终Review。

实际服务HTTP/WebSocket局部回归52项通过。旧bv_ws索引对应编号body被后续覆盖，撤回旧200/200、19 CallBall及第166帧来源归因；保留旧结果并标为失效。改从原始mitm归档直接导出连续前500条：500/500封包、35 CallBall、2 State、2 Join解码，未知字段保留。M2文本来源关联独立于这些body，历史7项检查不升格为当前运行证明。

User的限定C4授权已执行：先隔离再启动，同实例独立Android测试用户复用未改APK；原用户未启动，静态GDS只读复用，未复制原账号凭据/状态或消费。实际仅修改目标进程中已绑定的地址配置字符串，没有Frida/保护代码修改/玩法状态伪造。实例控制由Codex协调，可按补充在共同目录交接给dsh；离线工程工作不停。临时网络状态与回收入口留受控共同目录，不在公共Git登记运行endpoint。

dsh b2/b3及b4 SAMPLE-RUN.md已收到；b4报告场景生成、重载与16项直接方法自检通过，Codex未独立复跑，不等同真实UI输入。按[评论6209187825](https://github.com/840832144/AI-Workspace/pull/23#issuecomment-6209187825)保留骨架，继续原层次、来源文件＋PPtr与依赖解析、关键Sprite及布局恢复，补一次正常打开、真实点击、可见属性修改保存重开。恢复/重建/原本纯色/仍缺失分开记录；COIN_SQUARE和充能阈值未证实部分仅作预览采用规则，不覆盖其他工程。旧“消费链全部闭合、无其他覆盖点”和“MonoScript无方法体因此全脚本重写”结论不采用。两个启动请求已通过共同目录codex-out/ACK-006.md答复，原生Socket地址静态链与实际启动消费分开；dsh负责B样件并持续补A消费者。

下一步连续实现本地合成认证User、原版初始化/局内适配并完成同候选真实一局；dsh连续完成可编辑可交互样件。受控复算与失败入口D:\BingoClientLocalRound\DEVELOPMENT-RESULT.md、artifacts/evidence、runs；历史原APK/资源/数据不上传。旧任务暂停/暂缓、原账本及不合并/发布/SVN/finalize不变。Subagents: none。

此前79ca1c2/2c55072的“尚未授权、尚未启动、ACK待收及200条来源统计”为历史，当前由本节和补充覆盖，旧提交不重写。

## 2026-10-17 M1/M2执行补充

已选择性接纳18c9361的M1-M2-CONTINUE-20261017.md及评论6219590601，保留历史并覆盖旧零散推进安排。M1为P0：官方客户端＋本地服完整一局；M2沿CardCandidate恢复真实素材、布局与核心表现。dsh研究取证，Codex统一工程实现/编译/打包，User负责成品测试，ChatGPT Review。

dsh的INIT-CONTRACT-ACK011、消费者原件、CARD-MAPPING-HANDOFF及结构化映射已收到；接入前逐项区分已证与推断。ToBytes跨工具结果支持现有10字节头；ParseBytes函数边界仍待dsh纠正。离线元数据已发现回调第一参数为ErrResp，不能把错误分支解释为回放帧；集合defaultValue空数组不等于客户端非null构造。整组纠正交共同目录ACK-013，不拆七个任务。

本轮仅离线开发、静态核对、编译和打包；不运行产品功能/回归、鼠标试玩或模拟器。研究与完整初始化候选就绪后一次提出M1复验方案，含时长、隔离/恢复与客户端实际写盘，由User决定恢复。原15分钟同一卡点规则、旧任务暂停/暂缓及C4排除项不变。未新增Task、未merge/release/SVN/finalize。

### 本批实际交付（业务19287fe，2026-10-17）

M1：已在真实WebSocket入口接入338/2601/2324/2403/1001/1205六类初始化，按GDS真实配置引用构造本地档案/角色/服装，保留原认证与Backpack；服务Windows编译成功，未启动。完整初始化候选仍未就绪：七个回调第一参数实为ErrResp，203分支201明确对应ERR_LOGIN_SYNC_CACHE；dsh R2的“回放帧/时钟topic”解释仍不成立。203当前明确不确认恢复；间接消费者与完整缓存顺序/重启合同需dsh成组纠正，ACK-013已直接交接。本卡点停止，不恢复设备试错。

M2：保留已接管CardCandidate，按CAB/PPtr/Atlas接入15张素材；补读SymmetricSlicedImage的真实卡框引用，恢复标题、FREE、白底格与130/133设计坐标，增加状态/末球预览/结算表现。Windows新包artifacts/card-recovery-m2/BingoCardRecovery.exe已构建，旧包保留；原锚点填格动画、叫号/道具皮肤、字体/背景及完整局末表现仍有差异。User提供的Desktop/pop_gpt两份录像已离线抽帧，确认是四卡，不能替代单卡同模式验收。

本轮只做静态核对、场景编辑、编译和打包，没有运行产品功能/回归、鼠标试玩、服务或模拟器；旧18项检查和User“流程没啥问题”不继承为新版通过。交付/受控复算入口D:\BingoClientLocalRound\M1-M2-DELIVERY-20261017.md、unity-recovered/PLAY.md、artifacts/evidence。M1复验方案保留为条件未满足草案，包含12分钟窗口、隔离/恢复和客户端实际写盘；不申请本轮现场恢复。

Registry本轮已按既有工具重建并validate：20 canonical、0冲突/错误、6既有legacy警告。原Task/PR、pending-main与In Progress不变。Subagents: none；未merge/release/SVN/finalize。
