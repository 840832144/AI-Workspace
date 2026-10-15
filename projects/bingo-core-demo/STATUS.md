# Bingo核心玩法本地Demo 状态

- Task: [TASK-0041](../../tasks/TASK-0041-BINGO-CORE-DEMO.md)
- Status: In Progress；Gate 0登记/Registry验证已推送d65039f。
- 规格：完整EXECUTION_SPEC.md f42e249/330f754，最新四项规则修正生效。
- 治理：独立linked worktree `D:\AI-Workspace-bingo-core-demo`，沿用PR #21。
- 业务工程：已建 `D:\BingoCoreDemo`；无批准远端，先本地Git。
- 环境：初查未发现Unity Editor/团队模板；有.NET6运行时但无SDK。User已明确允许安装缺失Unity。模板/团队版本仍待提供，不阻断核心和本地服务。
- 阶段实测：最新426b145纯C#规则47项通过；此前c31f0c8已发布自包含本地服务，HTTP集成39项通过，含1/2/4/6卡完整循环。Unity源码已完成，Editor安装/原生构建与导入一致性待验证。
- User接手普通人工试玩；Codex负责规则、协议、复算与启停等专业测试，人工结果单独记录。
- 环境更新：已安装独立.NET SDK 10.0.402；Unity 6000.3.25f1官方安装包下载超时；官方Hub签名包下载/安装进行中（WinGet远程安装下载停滞已取消），未声称Editor可用。
- TASK-0039：User暂停，原账本保留，不恢复原实例/采集/自动玩。
- Subagents: none。

- 详情：[阶段实测](../../tasks/support/bingo-core-demo-20261015/IMPLEMENTATION-PROGRESS-20261015.md)；原生/人工验收未完成，Task继续In Progress。

- 版本边界：已交浏览器试玩包c31f0c8不变；最新426b145独立端口HTTP复测被自动审批拦截，保留待验证，不混用成绩。

- 最新安装实测：Unity Hub 3.22.3.65535已安装，Appx状态Ok，官方包SHA256及Unity签名Valid。Editor6000.3.25f1继续后台有界续传；完成后只有长度/官方签名通过才静默安装。状态入口D:\Apps\BingoBuildDownloads\unity-install-status.json。当前仍未完成Editor/原生构建。User需登录Hub确认可用许可证。
