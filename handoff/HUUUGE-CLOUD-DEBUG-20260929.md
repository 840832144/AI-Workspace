# Huuuge 云端调试方案交接

- Date: 2026-09-29
- Actor: ChatGPT
- Executor: 原 Codex 会话
- 关联正式任务：[TASK-0031](https://github.com/840832144/AI-Workspace/blob/codex/huuuge-cloud-single-instance/tasks/TASK-0031-HUUUGE-CLOUD-SINGLE-INSTANCE.md)
- 完整方案：[CLOUD_DEBUG_PLAN_20260929.md](../tasks/support/TASK-0031/CLOUD_DEBUG_PLAN_20260929.md)
- 性质：现有任务的调试细化与交接，不是新任务，不是准备代码Accepted Review，不是云端实测报告。

## 当前事实

User本人负责试点全程，已提供云手机网页Android桌面截图，并报告相关工具已安装。只确认网页桌面可见；CLI具体版本/登录、目标终端归属、独立Linux执行端、Huuuge可玩及真实采集仍需现场核验。禁止继续把“技术对接人未提供资源”作为笼统阻塞；缺什么具体报告什么。

读取基线：AI-Workspace main b0a36c8；现有任务/专用Handoff分支872e2dc；业务PR #2 / CURRENT_STATUS / 部署说明402e0d4。两条准备PR仍OPEN、未合并，查询显示mergeable=false；不要自动合并、强推或覆盖他人工作。先读取最新main和原分支，按现有流程协调冲突及任务状态。

## 执行顺序

先核验已安装CLI与实际运行对象，再不接探针试跑游戏；确认云端Linux到手机的受控连接后，复用既有check/probe/run及play-start/play-end/stop/status完成真实新增采集、正常结束和文件回读。User只在凭据/权限确认、游戏登录与手动操作、资源变更及最终验收时参与。

Workbench CLI资料明示Linux ECS，并不证明可以直接管理云手机实例；厂商网页SSH可用也不等于独立Linux执行端存在。不猜资源ID和转发参数。首次CLI连接可能改变安全组，upload/download经OSS中转；先核对权限与数据边界。短exec不能直接承载会被超时终止的整轮采集。原生ARM64、私网、Root、descriptor前提必须实测，不能为了通过校验随意删改。

## 原Codex会话的下一动作

读取完整方案，先确认准备代码的定向审阅状态并把本次User确认的资源变化同步到已有Task/Status/Handoff，沿用现有Registry流程，不分配新ID。先返回CLI是否可用、Android与Linux对象是否已确认、游戏是否已装三个最小事实；据此推进可独立完成的游戏基线，不先增加付费资源。需要网络/系统权限变更或新增资源时只提出一个具体待User确认项。

业务适配、测试和实际运行证据写回huuuge-android-research；治理状态写回AI-Workspace。新方案分支只新增文档，不改原Codex实施分支或代码；纳入时按路径选择性合并/复用，不制造第二个执行者。

本轮ChatGPT只完成来源读取、调试方案与Git交接，没有连接云环境、运行采集、执行Workspace Sync/Registry validator或接受现有代码Review。静态方案不代替三项真实验收。Subagents: none。
