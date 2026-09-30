# Huuuge V1 — TASK-0037 执行交接

- Updated: 2026-09-30；Actor: Codex；Owner: User；Subagents: none。
- Status: In Progress；唯一任务[TASK-0037](../tasks/TASK-0037-HUUUGE-SELF-SERVICE-V1.md)，后继TASK-0031 Accepted；不新建任务。
- 唯一规格：[HUUUGE-SELF-SERVICE-V1-20260930.md](../docs/plans/HUUUGE-SELF-SERVICE-V1-20260930.md)。原来源PR12/a91bf39，本次User范围调整已就地同步，优先于旧内嵌方案。

## 当前决策

官方Web成员账号玩Huuuge＋独立采集小面板，允许分别登录。可信同事约定轮流，不强制手机控制交接、防重连或旧厂商凭证撤销；不要求Web SDK内嵌及统一登录。采集锁仅防重复采集，不能称为手机控制锁。

保留基本鉴权、本人批次启停/下载权限、按批次与片段保存、重复请求保护、云端独立常驻、受保护连接、TLS及真实四态：开始灰、采集中绿、错误红、结束红；正常结束显示停止图标与“已保存”。正常结束下载脱敏含值AI包，用已有本地AI分析。本阶段全部完成才Review，不接其他游戏。

## 已确认及证据边界

- User成员账号实测通过：已创建成员账号并绑定现有云手机，官方Web成功登录，到Android桌面及Huuuge大厅。仅为User本人反馈；不是Codex独立复测、同事盲测、Android客户端或V1采集验收。
- 原TASK-0031正式Accepted已落库，治理08ca95b/业务4572b78；312/312/0和8条Slots响应及原结果保留。原PR未获合并授权，新功能只在后继分支。
- TASK-0037既有独立worktree、remote-CAS登记；reservation pending-main。当前Registry20/0/valid；Workspace Sync ON_DEMAND，provider unavailable、stale6、conflicts0，Git为真相源。不得再分配编号。
- 已有登录/采集状态/面板/导出/片段编排及合成检查。旧SDK onConnected/断连后旧Ticket重连/2507是历史事实，不能改写成撤销通过，也不再阻塞V1。厂商咨询未发送且退出当前待办。

## 2026-09-30 — TASK-0037本人Web闭环及短恢复实测

Status: **In Progress / 已可Web使用，User本轮闭环通过**。User确认“流程完成，已保存并下载”，提交的新包与云端同批及再次HTTPS下载一致：**370捕获/370解码成功/0失败**，约91秒，1段finalized、无记录缺口、complete=1、lease=0。含25对Spin和2对FreeSpin；本地AI已从新包回答下注字段、免费转及Jackpot标记问题并提供片段/序号，未计算未经证实的RTP/净收益。

User明确本次就验收这一时长，不再追加三分钟测试。规格已同步为本次约91秒短流程验收；较长后台稳定性未测，代码中原3分钟断线宽限不变。不是同事盲测或Android客户端结果。

独立短API恢复检查：两非管理员面板身份顺序新采，重复开始409、越权停止/下载404、错误页面停止409；任务worker被定向中断后systemd恢复并开新片段，旧缺口保留；过期采集页11秒后可claim，旧页停止409。该测试新批次14/14/0、两片段，明确incomplete/error且可下载，正常收尾后锁释放；未伪装为完整。最后回读当前采集0、专用ADB/Frida监听0，云端任务服务及限定SSH隧道保持运行。

实际代码216b298，已批准部署与入口说明见[部署实况](https://github.com/840832144/huuuge-android-research/blob/codex/huuuge-self-service-v1/deploy/self-service/DEPLOY_RESULT_20260930.md)，最少结果见[脱敏回执](https://github.com/840832144/huuuge-android-research/blob/codex/huuuge-self-service-v1/deploy/self-service/RESULT_USER_20260930.json)。原TASK-0031 Accepted及312/312/0不变，10/10/0的早期API冒烟也与User370条分开。代理例外仅User批准的面板地址，默认网络及User网页均通过；浏览器工具错误后保持停止，没有代验UI。

完整V1剩余：独立同事使用、实际浏览器短断线/下载异常重试、退出Codex管理会话后的新轮等，按原A—F单列。未要求User再做三分钟测试，未标完整Review/Done；原Draft PR继续。飞书待授权不阻塞。Subagents: none。

## 代码、发布和路线图

业务代码/部署/验收在huuuge-android-research；治理规格/Task/Status/Handoff及唯一Product Roadmap在AI-Workspace。两仓沿用codex/huuuge-self-service-v1；保留现有实现，不重写采集器或TASK-0031结果，不做本地安装包/SVN镜像。

唯一Product Roadmap Current就地改为官方Web＋采集小面板；多游戏仍Backlog、每人独立手机仍Ideas，不自动创建后续Task。Git和正式文档发布证据分别记录，未回读的发布不得称为完成。

本轮验证：小面板17/17合成检查，原采集器16通过/5项Linux专属跳过，JS语法通过；Registry20/0/valid。正式飞书路线图已定位原文档；企业内可编辑权限回读因本机lark-cli user返回token_missing未完成，因此本轮未改飞书正文或权限，正式同步仍待完成，不阻塞代码/云连接准备。不自动重新授权或切换身份。

业务已提交/推送9b6b21d（保留准备代码）及1c9c364（分离采集面板、停用SDK路径、既有Linux合成CI覆盖）；后续继续该分支。CaptureRuntime已在216b298真实部署并通过TLS/清理及API冒烟；准入已开启，最新边界见上方部署实况。

后续协作入口：[治理Draft PR #13](https://github.com/840832144/AI-Workspace/pull/13)、[业务Draft PR #3](https://github.com/840832144/huuuge-android-research/pull/3)。Linux合成CI run36682709050在1c9c364上42/42通过，无跳过；Windows记录和User本人入口反馈仍分别保留，不计真实云端采集。未请求完整Review或合并。

## 历史：2026-09-30部署批准前的Runtime准备

沿用TASK-0037，原登记Registry20/0collision/valid；WorkspaceSync ON_DEMAND/provider unavailable/stale6/conflicts0。代码候选已补CaptureRuntime、每段Frida TLS/令牌、专用进程与转发收尾、运行容量保护及受鉴权SSE后台页连接，复用原采集器；清理未知不释放采集锁或发布ZIP，准备期停止不再启动decoder。

环境只读回读：Linux OpenSSH8.0支持PermitListen；任务端口空闲、32.8GB可用；安全组已有22/80/443。有效nginx无TLS配置/443监听，纠正先前把注释当证书引用。手机Android12/ARM64、Huuuge当前版本运行，原官方Frida工具存在。尚未运行实际SSH隧道或新采集。

[具体部署清单/影响/回滚](https://github.com/840832144/huuuge-android-research/blob/codex/huuuge-self-service-v1/deploy/self-service/DEPLOY_APPROVAL_20260930.md)：申请两个任务Linux身份、仅回环反向SSH管理通道及Match限制、独立systemd服务/容量上限、既有公网IP的HTTPS证书/续期和nginx精确配置。需要User确认后执行；IP证书公开透明度记录需一并接受。无新资源购买、IAM/安全组/防火墙/端口映射变更；不修改晨会。

本地Windows48通过/6Linux跳过、JS通过；均为局部/合成证据，LinuxCI另记。无V1新包/新计数，真实双标签页、新包本地AI、轮流与异常恢复A—F均未验，不交完整Review。TASK-0031 Accepted及312/312/0保持；User成员登录仅本人实测。飞书待授权，不阻塞开发。Subagents: none。

下一步：User批准具体部署单后由Codex部署与实测，审批拒绝按正常流程停止；手机SSH客户端兼容/host key/最小权限/实际保护路径先通过，随后可信HTTPS与真实新批次，不用原312条替代。

Linux合成CI [run36686925269](https://github.com/840832144/huuuge-android-research/actions/runs/36686925269) 在业务代码5ef40531a2c8e268dce6e98b8fbd158f9f9a1b94通过：controller21＋descriptor4＋panel21＋Runtime8，共54/54、无跳过。包含真实Linux本地进程/回环socket的合成边界测试；不是目标云手机或V1验收。
