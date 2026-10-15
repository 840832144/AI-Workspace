# Bingo核心玩法本地Demo — 正式启动接管入口

- Kind: handoff。
- User decision: Confirmed；2026-10-15明确要求“现在任务正式开始吧”。
- Project key: BINGO-CORE-DEMO；独立新任务，不使用TASK-0039编号。
- 当前阶段：已批准执行规格入Git，正式编号及本机实施由Codex首步完成。不是待User再次确认的方案讨论。

## 2026-10-15 Codex正式登记

remote-CAS已分配[TASK-0041](../tasks/TASK-0041-BINGO-CORE-DEMO.md)，Ready；登记校验推送后连续实施。独立业务路径D:\BingoCoreDemo，规则/服务/Unity不入公共治理树。User已批准安装缺失Unity。原TASK-0039暂停记录在原PR #17，不继承线上预算。

## 唯一执行正文

读取[完整EXECUTION_SPEC.md](../tasks/support/bingo-core-demo-20261015/EXECUTION_SPEC.md)，规格提交`330f754bc55f9487a37a796e26a6b87c32ecdada`。三份旧讨论稿仅供溯源，与本规格冲突的“目标不足整卡不执行”“buff可放已有buff格”“使用补填道具直接加次数”等内容均失效。

最新规则：双格填充只剩1格仍填1格；新增buff仅选未填、非FREE、无buff格；无目标不放置但道具已使用，不退回或重抽；补填改为每卡放补填buff，填中才累积结算补填次数。不能只复制旧提案开工。

## Codex首步及连续执行

1. 安全同步最新main及相关分支，读取四份项目来源、Workspace Memory、AGENTS、行文规范与Task README；完整Registry预检/同目标防重后，在独立linked worktree用现有remote-CAS分配器登记Ready Task，Project key=BINGO-CORE-DEMO。重建验证Registry并推送，然后直接实施，不再次索取产品目标批准。
2. 将TASK-0039的User暂停同步到其原Task/Status/Handoff及PR #16/#17，保留历史与账本，不恢复旧十局、不挪旧线上额度。真实停止行为以本机核对为准，本Handoff不声称操作了设备。
3. 新任务沿用本规格，选择团队可复用Unity模板，建立独立C#核心与本地服务；按单卡完整循环→1/2/4/6卡及九道具→Windows一键试玩包和Unity移交验证推进。治理留AI-Workspace，业务实现落实际受控业务工程，记录明确入口。
4. dsh优先核验现有资料；建立唯一RULES.md/QUESTIONS.md。未考证规则用User暂定值或明确标注的工程临时值；真正需User回答的分歧集中列出，其余开发不停。没有直接dsh入口则准备DSH-VERIFY.md交接，不假称已联系或收到结果。
5. 完成后交付真实Task、治理/业务commit、可玩包、九道具和各卡数测试、原版已确认与Demo暂定差异、回滚和Review入口。原客户端兼容、特效迁移与数字Auto Play/GM只记录，不启动；不自动合并、发布、提交SVN或finalize。

## 当前在线核对与本会话限制

本轮main=`898358ffccbfa4d9b909d43de48ae794a7129718`；旧实现PR #16=`f95ba94ad56c49a271ab6d6d99d295ebd8f7df46`；旧治理PR #17=`62db0f832120adc128139557ff3639131e21fc4b`。旧canonical仍是自动玩记录，不能当新Demo Task。

ChatGPT已通过GitHub读取最新Task/Status/Handoff和支持稿。本容器Git直连失败，未运行完整Registry validator、allocator或Workspace Sync，未分配TASK编号，也未连接Windows、Unity或模拟器。Codex首步负责正式登记与暂停状态同步；不得把支持文档或新PR编号当成canonical Task编号。

开发授权已明确，普通代码/本地测试/阶段转换连续推进；新外部付费、线上消费或权限变更仅限制相关操作，不让无关的本地Demo停工。
