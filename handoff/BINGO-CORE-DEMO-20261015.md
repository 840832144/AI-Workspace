# Bingo核心玩法本地Demo — 正式启动接管入口

- Kind: handoff。
- User decision: Confirmed；2026-10-15明确要求“现在任务正式开始吧”。
- Project key: BINGO-CORE-DEMO；独立新任务，不使用TASK-0039编号。
- 当前阶段：TASK-0041 Review；User已试玩0.2.1并要求整理交ChatGPT，初步无明显问题；完整边界验收缺口仍保留，未Accepted。

## 2026-10-16 当前Review入口

优先读取[首版交付与Review交接](../tasks/support/bingo-core-demo-20261015/CHATGPT-REVIEW-HANDOFF-20261016.md)，以及User手动上传的TASK-0041-Review-0.2.1-20261016.zip。业务08529d8，原生0.2.1；47项规则、Unity导入/构建、真实启动和49条User试玩复算通过。User原话“看起来没啥太大问题”只计初步体验；新版完整HTTP、其他卡数UI/返回再开、断外网、dsh核验仍待补。未附源码ZIP时不能声称已Review业务代码。下文为历史过程，冲突状态以本节为准；继续原PR #21，不新任务、不合并或finalize。

## 2026-10-15 Codex正式登记

remote-CAS已分配[TASK-0041](../tasks/TASK-0041-BINGO-CORE-DEMO.md)，最初Ready登记，现In Progress；登记校验d65039f推送后已实施。独立业务路径D:\BingoCoreDemo，规则/服务/Unity不入公共治理树。User已批准安装缺失Unity。原TASK-0039暂停记录在原PR #17，不继承线上预算。

## 2026-10-15 实施与试玩交接

见[阶段实测](../tasks/support/bingo-core-demo-20261015/IMPLEMENTATION-PROGRESS-20261015.md)：最新业务fefe61a，官方Unity CLI已接入，User安装的6000.6.5f1实际完成47项核心测试、Unity/.NET导入一致性及Windows构建。原生候选包0.2.0已整理，User接手普通窗口试玩；此前浏览器包和39项HTTP成绩保留，新版HTTP回归被自动审批拒绝，未混版计通过。原TASK-0039暂停已推af46b8b，不恢复。

## 唯一执行正文

### 原生窗口已交User试玩

User反馈0.2.0启动失败并要求直接打开。旧0.1.0占端口已通过自有Stop入口关闭且保留记录。但随后“窗口响应/服务Lobby等于客户端已连接”的判断错误：零session/catalog请求、Unity连到系统代理29290及User截图证明连接失败，撤回ce87d64的客户端成功结论，保留native-startup-handoff.json。

已在业务08529d8修复Unity本地直连，并让Launch/Check验证当前自有客户端完成session/catalog/state，未改系统代理。0.2.1新包真实Launch/Check退出0，客户端READY Lobby、服务记录1次session/1次catalog/167次state，窗口存在且响应，已留给User试玩。没有替User开局；完整玩法体验仍待反馈。受控结果D:\BingoCoreDemo\artifacts\evidence\native-startup-fixed.json；试玩包BingoCoreDemo-0.2.1-unity-preview.zip，源码BingoCoreDemo-source-08529d8.zip。47项规则、Unity一致性及原生构建重新通过。

读取[完整EXECUTION_SPEC.md](../tasks/support/bingo-core-demo-20261015/EXECUTION_SPEC.md)，规格提交`330f754bc55f9487a37a796e26a6b87c32ecdada`。三份旧讨论稿仅供溯源，与本规格冲突的“目标不足整卡不执行”“buff可放已有buff格”“使用补填道具直接加次数”等内容均失效。

最新规则：双格填充只剩1格仍填1格；新增buff仅选未填、非FREE、无buff格；无目标不放置但道具已使用，不退回或重抽；补填改为每卡放补填buff，填中才累积结算补填次数。不能只复制旧提案开工。

## Codex首步及连续执行

1. 安全同步最新main及相关分支，读取四份项目来源、Workspace Memory、AGENTS、行文规范与Task README；完整Registry预检/同目标防重后，在独立linked worktree用现有remote-CAS分配器登记Ready Task，Project key=BINGO-CORE-DEMO。重建验证Registry并推送，然后直接实施，不再次索取产品目标批准。
2. 将TASK-0039的User暂停同步到其原Task/Status/Handoff及PR #16/#17，保留历史与账本，不恢复旧十局、不挪旧线上额度。真实停止行为以本机核对为准，本Handoff不声称操作了设备。
3. 新任务沿用本规格，选择团队可复用Unity模板，建立独立C#核心与本地服务；按单卡完整循环→1/2/4/6卡及九道具→Windows一键试玩包和Unity移交验证推进。治理留AI-Workspace，业务实现落实际受控业务工程，记录明确入口。
4. dsh优先核验现有资料；建立唯一RULES.md/QUESTIONS.md。未考证规则用User暂定值或明确标注的工程临时值；真正需User回答的分歧集中列出，其余开发不停。没有直接dsh入口则准备DSH-VERIFY.md交接，不假称已联系或收到结果。
5. 完成后交付真实Task、治理/业务commit、可玩包、九道具和各卡数测试、原版已确认与Demo暂定差异、回滚和Review入口。原客户端兼容、特效迁移与数字Auto Play/GM只记录，不启动；不自动合并、发布、提交SVN或finalize。

## 规格交接时的历史核对与限制

本轮main=`898358ffccbfa4d9b909d43de48ae794a7129718`；旧实现PR #16=`f95ba94ad56c49a271ab6d6d99d295ebd8f7df46`；旧治理PR #17=`62db0f832120adc128139557ff3639131e21fc4b`。旧canonical仍是自动玩记录，不能当新Demo Task。

ChatGPT已通过GitHub读取最新Task/Status/Handoff和支持稿。本容器Git直连失败，未运行完整Registry validator、allocator或Workspace Sync，未分配TASK编号，也未连接Windows、Unity或模拟器。Codex首步负责正式登记与暂停状态同步；不得把支持文档或新PR编号当成canonical Task编号。

开发授权已明确，普通代码/本地测试/阶段转换连续推进；新外部付费、线上消费或权限变更仅限制相关操作，不让无关的本地Demo停工。
