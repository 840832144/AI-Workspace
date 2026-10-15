# Bingo核心玩法本地Demo 状态

- Task: [TASK-0041](../../tasks/TASK-0041-BINGO-CORE-DEMO.md)
- Status: In Progress；Gate 0登记/Registry验证已推送d65039f。
- 规格：完整EXECUTION_SPEC.md f42e249/330f754，最新四项规则修正生效。
- 治理：独立linked worktree `D:\AI-Workspace-bingo-core-demo`，沿用PR #21。
- 业务工程：已建 `D:\BingoCoreDemo`；无批准远端，先本地Git。
- 环境：初查未发现Unity Editor/团队模板；有.NET6运行时但无SDK。User已明确允许安装缺失Unity。模板/团队版本仍待提供，不阻断核心和本地服务。
- 阶段实测：最新fefe61a纯C#规则47项、Unity6000.6.5f1同核心导入结果一致及Windows原生构建通过；此前c31f0c8实际服务HTTP集成39项通过。新原生包真实窗口、包入口与新版HTTP仍待验证，未混用旧包成绩。
- User接手普通人工试玩；Codex负责规则、协议、复算与启停等专业测试，人工结果单独记录。
- 环境更新：已安装独立.NET SDK 10.0.402；Unity 6000.3.25f1官方安装包下载超时；官方Hub签名包下载/安装进行中（WinGet远程安装下载停滞已取消），未声称Editor可用。
- TASK-0039：User暂停，原账本保留，不恢复原实例/采集/自动玩。
- Subagents: none。

- 详情：[阶段实测](../../tasks/support/bingo-core-demo-20261015/IMPLEMENTATION-PROGRESS-20261015.md)；原生/人工验收未完成，Task继续In Progress。

- 版本边界：已交浏览器试玩包c31f0c8不变；最新426b145独立端口HTTP复测被自动审批拦截，保留待验证，不混用成绩。

- 最新环境实测：Hub3.22.3.65535保留；旧6.3下载已以curl56停止且未安装，User另在Hub安装的6000.6.5f1已通过CLI结构检查和真实构建。官方Unity CLI1.0.0-beta.13已安装，构建脚本按项目版本查询已安装Editor，未重复下载/安装。首次CLI许可查询失败，但随后Editor实际取得许可并退出0，不再将许可证作为当前阻塞。
- 原生试玩入口：D:\BingoCoreDemo\artifacts\packages\BingoCoreDemo-0.2.0-unity-preview.zip（fefe61a）；独立于此前浏览器包，人工体验待反馈。受控证据见业务artifacts/evidence/unity-cli-build-summary.json及unity-build.log。没有安装Pipeline/MCP/全局Agent插件，没有创建Unity Cloud项目。
- User反馈启动失败后，实测复现旧0.1.0服务占用18741，新包按预期拒绝接管。旧局已在Result；按User“起开然后我玩”通过旧包Stop入口关闭自有服务，再用0.2.0 Launch入口启动成功，原生窗口存在且响应、健康检查Lobby、客户端持续请求状态。已交User试玩，不再操作对局；不计完整人工验收。证据：artifacts/evidence/native-startup-handoff.json。
