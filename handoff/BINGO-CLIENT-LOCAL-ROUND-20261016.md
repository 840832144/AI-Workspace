# Bingo原客户端本地一局闭环 — dsh / Codex共同接管

- Kind: handoff。
- Date: 2026-10-16。
- Project key: BINGO-CLIENT-COMPAT。
- User已批准改为单一可玩交付目标；不再只交Schema、样件或可行性报告。
- 完整正文：`tasks/support/bingo-client-local-round-20261016/EXECUTION_SPEC.md`。

## Codex正式登记

remote-CAS已分配[TASK-0043](../tasks/TASK-0043-BINGO-CLIENT-LOCAL-ROUND.md)，Project key BINGO-CLIENT-COMPAT。治理独立linked worktree D:\AI-Workspace-bingo-client-local-round，沿用PR #23；登记校验推送后直接实施。main898358f已同步，登记前19 canonical/0冲突错误；旧任务状态按各自原分支保留。当前[项目状态](../projects/bingo-client-compat/STATUS.md)。Subagents: none。

## 2026-10-16 离线修复与测试交接

User对当前dfd312c恢复样件试玩反馈：“流程没啥问题”。记录为结果B流程暂无明显问题，不扩大为逐项边界、编辑保存重开、原版视觉或结果A通过；没有新增代码或重跑测试。后续仍由User测试，Task保持In Progress。

已接纳[卡点Review 6211006045](../tasks/support/TASK-0043/CHATGPT-BLOCKER-REVIEW-20261016.md)，结论Needs changes，Task保持In Progress。沿c3bc731分工与513f5da/d35c8a0基线继续；dsh优先研究已认证到大厅的整组初始化/SyncCache，并行补实际组件→Sprite→布局映射。七类请求只是起点，不默认全空、不重挖地址和Backpack。Codex推进现有恢复工程及有依据的离线适配；当前未收到新初始化合同，不声明已接入。

业务dfd312c已修CardCandidate普通输入与补填的唯一充能路径、运行时道具绑定、合法Bingo、结束/重置再玩；保留原层次，对已知错图作明确占位，原版呈现仍待实际引用映射。Windows试玩程序已构建。User改变测试分工前18项组件/保存重开检查通过，仍只是局部历史证据；实际鼠标验证因捕获接口失败后User按Esc停止，尚未完成。

**最新User决定：后续测试全部由User承担；Codex负责开发、打包和交接，不再自动运行功能/回归测试或操作试玩。** 成功验收只按实际User反馈登记。试玩入口D:\BingoClientLocalRound\artifacts\card-recovery\BingoCardRecovery.exe；短流程说明在工程PLAY.md和包内试玩说明.md。此候选不等于原版呈现或结果A完整一局通过。

原客户端设备试错仍停止。研究与离线版本就绪后，一次提交复验依据/版本/检查点、明确时长、失败判据与恢复步骤，必须含客户端实际Logout/写盘，由User决定恢复并测试。普通同一卡点约15分钟约束继续，不能换topic/换人重置。既有C4排除项、旧任务暂停/暂缓与不合并/发布/SVN/finalize不变。

本次仅记录开发和交接，无新增测试；Registry身份/Status/Project key未变，最近有效校验仍为ef1839d前的20 canonical、0冲突/错误、6既有legacy警告，不冒称本轮重跑。Subagents: none。

## 历史：ef1839d分工接管检查点

已接纳[f1a4a4b成品收口要求](../tasks/support/TASK-0043/DSH-DELIVERABLE-FIRST-20261016.md)与[c3bc731分工调整](../tasks/support/TASK-0043/ROLE-SPLIT-20261016.md)。**Codex统一负责结果A/B工程实现、UI、交互、测试与打包；dsh主责研究取证和提取/解析/验证脚本。** 旧dsh结果B工程负责人安排仅作历史；两项产品标准与限定C4边界不变。

dsh已冻结并交出CardCandidate完整工程，295条目包级核对通过；Codex在原客户端停止的检查点接收为受控工作副本，业务基线d35c8a0，原ZIP及dsh原目录保留。未另起Demo。随包15项自检/重开/双视口渲染为dsh证据，尚未由Codex完整复跑；普通点击充能绑定、道具监听、结束重置、屏幕输入及精确图片/布局仍待修复，旧“已收口”结论不采用。

业务当前513f5da：本地合成认证、保存令牌续接及六条初始化应答已被原客户端实际接受；Backpack非空修复后实际发出GetProfileState等后续初始化。服务75项局部HTTP/WebSocket回归通过，当前原客户端仍停在加载页，未大厅/一局/结束返回。后续初始化模块及重连缓存消费者尚未闭合；不能以空响应或局部测试冒充完整结果。服务与测试游戏已停，临时隔离/reverse已按owner回收，返回原Android用户且未启动原游戏。受控结果/失败/复现入口D:\BingoClientLocalRound\DEVELOPMENT-RESULT.md与共同目录INTEGRATION.md。

User新增执行约束：普通单一卡点约15分钟未解决即停止该点，报告已试方法、证据与待决策项，等待User Review讨论后决定继续修改或先由dsh研究；不按微步骤改名延长同一阻塞，提前批准测试按约定时长。当前登录初始化卡点已停止并准备整模块研究清单，后续实施等User讨论决策；这是本轮调试约束，不重置原Task/进度或新增阶段审批。

研究增量直接进入research-dsh；正式工程与INTEGRATION/codex-out由Codex写入。REA说明已收到、CLI实测6.5.0；未新装或注册MCP，未将未配置的IDA反编译声称可用。TASK-0039暂停、TASK-0041验证暂缓；不扩权、不合并/发布/SVN/finalize。Subagents: none。

## 历史：8f5d0af结果与旧分工

业务8f5d0af，D:\BingoClientLocalRound独立本地Git，无远端。原客户端实际完成本地性能/热更/GDS加载，进入Login as Guest；原生topic101已到服务，认证仍明确未实现。服务52项局部回归通过，原mitm连续500帧500/500（35 CallBall、2 State、2 Join）。这些不替代结果A完整一局；尚未可玩或最终Review。

来源纠正：旧编号body被后续采集覆盖，旧200/200、19 CallBall、第166帧归因撤回并保留历史。当前ArchiveFrames.py直接从原归档顺序导出；未知字段保留。原始证据和版本/失败入口在受控DEVELOPMENT-RESULT.md、artifacts/evidence、runs。

已接纳[10e6aa5补充](../tasks/support/TASK-0043/DSH-CONTINUATION-AND-REUSE-20261016.md)与后续User抄送，覆盖旧待批说法。同实例独立Android测试用户已运行；限定C4只用于Root、隔离/reverse和必要地址/启动配置路由。实际进程内地址字符串修改有对象绑定，不修改玩法结果；无Frida、CA、TLS/签名/完整性/保护组件改动。原用户、旧账本保持，不联网原服或消费。

Codex负责结果A：原客户端大厅→单卡选择取消/确认→持续叫号手填→基础道具→合法Bingo→正常结果返回→新局。继续合成认证User、WS初始化与所缺必要适配，不等待dsh所有研究齐备。自研样件/合成HTTP不替代原客户端。

dsh负责持续支撑A，并完成结果B：b4 SAMPLE-RUN.md报告场景生成、重载与16项直接方法自检通过，Codex未独立复跑；按评论6209187825保留骨架，继续原层次、来源文件/PPtr依赖、关键Sprite与必要布局恢复，并补真实UI点击和可见属性保存重开。恢复/重建/原本纯色/缺失分别记录；COIN_SQUARE与单格填充、充能阈值未证实部分仅列预览采用规则。TypeTree和实际代码载体并行判断，不静默删缺组件、不生成几千空壳、不再等stub策略批准。

共同受控目录D:\DSH_work\bingo-local-round。Codex唯一维护INTEGRATION.md/codex-out，dsh写research-dsh；b2/b3材料已收，两个启动链问题已答复ACK-006。静态SocketConnect基线不等于当前连接成功。Codex协调实例，可按补充§3完整窗口交给dsh；显式交出/接回，不自动抢占，窗口内不并发改服务/实例。无需User重复批准同范围。

TASK-0039继续暂停；TASK-0041验证暂缓；新任务必要测试继续。保留原件受控本机，无公网业务源码或资源上传。不合并、发布、SVN、finalize。Subagents: none；dsh为User已有独立会话。
