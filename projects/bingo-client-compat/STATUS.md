# Bingo原客户端本地一局状态

- Task: [TASK-0043](../../tasks/TASK-0043-BINGO-CLIENT-LOCAL-ROUND.md)，In Progress；沿用PR #23，pending-main，不finalize。
- 已接纳[成品要求f1a4a4b](../../tasks/support/TASK-0043/DSH-DELIVERABLE-FIRST-20261016.md)与[分工c3bc731](../../tasks/support/TASK-0043/ROLE-SPLIT-20261016.md)。Codex统一工程实现；dsh主责研究取证，不再并发改成品场景/交互。
- 结果A：业务513f5da，原客户端实际接受本地合成认证、保存令牌续接、六条初始化；空Backpack修复后进入后续资料初始化，仍未大厅/完整一局。服务75项局部回归通过，不冒充原客户端验收。
- 当前卡点：[6211006045 Review](../../tasks/support/TASK-0043/CHATGPT-BLOCKER-REVIEW-20261016.md)为Needs changes。已批准继续离线工程，dsh研究完整初始化/SyncCache合同和P11实际映射；现场停止不解除。整组版本就绪后一次提出复验计划，由User决定恢复。
- 结果B：保留d35c8a0接收基线，业务dfd312c修复普通填格/补填充能、道具事件、Bingo与结束重置，Windows程序已构建。User接手前18项组件/保存重开回归通过；User最新试玩反馈“流程没啥问题”，记录为当前流程暂无明显问题。逐项边界/编辑保存重开未获User反馈，图片/原版布局待dsh映射，未完整验收。
- 最新测试分工：后续测试全部由User负责；Codex继续开发/打包/交接，不再自动运行回归或操作试玩。试玩入口与短流程见受控unity-recovered/PLAY.md。
- 环境：测试游戏/服务已停止，自有隔离/reverse已回收，原Android用户恢复但原游戏未启动。限定C4、原用户数据及既有排除项不变。
- 共同目录D:\DSH_work\bingo-local-round。Codex写INTEGRATION/codex-out及正式工程；dsh写research-dsh和研究工具。工程接收ACK-010，整模块缺口由后续共享清单记录。
- 历史来源纠正保留：原mitm连续500帧500/500、35 CallBall/2 State/2 Join；旧200/19归因撤回，不作为当前运行成绩。
- TASK-0039暂停；TASK-0041验证暂缓。原件与恢复素材仅受控本机；未合并/发布/SVN/finalize。Subagents: none。

本轮未重跑测试或Registry验证；Task身份/状态未变，最近Registry有效结果沿用ef1839d检查点，不记为新通过。

## 2026-10-17 M1/M2执行补充

已选择性接纳18c9361的M1-M2-CONTINUE-20261017.md及评论6219590601，保留历史并覆盖旧零散推进安排。M1为P0：官方客户端＋本地服完整一局；M2沿CardCandidate恢复真实素材、布局与核心表现。dsh研究取证，Codex统一工程实现/编译/打包，User负责成品测试，ChatGPT Review。

dsh的INIT-CONTRACT-ACK011、消费者原件、CARD-MAPPING-HANDOFF及结构化映射已收到；接入前逐项区分已证与推断。ToBytes跨工具结果支持现有10字节头；ParseBytes函数边界仍待dsh纠正。离线元数据已发现回调第一参数为ErrResp，不能把错误分支解释为回放帧；集合defaultValue空数组不等于客户端非null构造。整组纠正交共同目录ACK-013，不拆七个任务。

本轮仅离线开发、静态核对、编译和打包；不运行产品功能/回归、鼠标试玩或模拟器。研究与完整初始化候选就绪后一次提出M1复验方案，含时长、隔离/恢复与客户端实际写盘，由User决定恢复。原15分钟同一卡点规则、旧任务暂停/暂缓及C4排除项不变。未新增Task、未merge/release/SVN/finalize。

### 本批实际交付（业务19287fe，2026-10-17）

M1：已在真实WebSocket入口接入338/2601/2324/2403/1001/1205六类初始化，按GDS真实配置引用构造本地档案/角色/服装，保留原认证与Backpack；服务Windows编译成功，未启动。完整初始化候选仍未就绪：七个回调第一参数实为ErrResp，203分支201明确对应ERR_LOGIN_SYNC_CACHE；dsh R2的“回放帧/时钟topic”解释仍不成立。203当前明确不确认恢复；间接消费者与完整缓存顺序/重启合同需dsh成组纠正，ACK-013已直接交接。本卡点停止，不恢复设备试错。

M2：保留已接管CardCandidate，按CAB/PPtr/Atlas接入15张素材；补读SymmetricSlicedImage的真实卡框引用，恢复标题、FREE、白底格与130/133设计坐标，增加状态/末球预览/结算表现。Windows新包artifacts/card-recovery-m2/BingoCardRecovery.exe已构建，旧包保留；原锚点填格动画、叫号/道具皮肤、字体/背景及完整局末表现仍有差异。User提供的Desktop/pop_gpt两份录像已离线抽帧，确认是四卡，不能替代单卡同模式验收。

本轮只做静态核对、场景编辑、编译和打包，没有运行产品功能/回归、鼠标试玩、服务或模拟器；旧18项检查和User“流程没啥问题”不继承为新版通过。交付/受控复算入口D:\BingoClientLocalRound\M1-M2-DELIVERY-20261017.md、unity-recovered/PLAY.md、artifacts/evidence。M1复验方案保留为条件未满足草案，包含12分钟窗口、隔离/恢复和客户端实际写盘；不申请本轮现场恢复。

Registry本轮已按既有工具重建并validate：20 canonical、0冲突/错误、6既有legacy警告。原Task/PR、pending-main与In Progress不变。Subagents: none；未merge/release/SVN/finalize。
