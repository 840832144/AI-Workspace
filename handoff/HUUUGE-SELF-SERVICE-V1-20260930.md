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

## 剩余工作与下一步

受保护管理连接、云运行适配、每批TLS自动准备/清理、容量保护、HTTPS面板入口及真实A—F尚待完成。原私网ADB检查超时，原公网ADB鉴权不等于传输加密；不能降低TLS/目标校验或依赖Owner本机持续运行。

先在已核验现有Linux和手机明确最小可实施保护路径；取消SDK后重新核定是否仍需云API身份，不先申请广泛权限。涉及新的身份、网络/IAM、公开入口、费用或共享服务时给出具体改动、影响、回滚并等Owner确认。已授权代码与任务独立服务准备继续，不等待撤销工单。

实际验收包括官方Web＋面板的同事使用、两面板身份分别新批次、单采集任务防重复和下载归属、真实四态、正常停止/回读/下载与本地AI、断线恢复、退出Codex管理会话后仍可运行。User本次登录反馈只覆盖其本人入口，不勾选上述完整验收。

## 代码、发布和路线图

业务代码/部署/验收在huuuge-android-research；治理规格/Task/Status/Handoff及唯一Product Roadmap在AI-Workspace。两仓沿用codex/huuuge-self-service-v1；保留现有实现，不重写采集器或TASK-0031结果，不做本地安装包/SVN镜像。

唯一Product Roadmap Current就地改为官方Web＋采集小面板；多游戏仍Backlog、每人独立手机仍Ideas，不自动创建后续Task。Git和正式文档发布证据分别记录，未回读的发布不得称为完成。

本轮验证：小面板17/17合成检查，原采集器16通过/5项Linux专属跳过，JS语法通过；Registry20/0/valid。正式飞书路线图已定位原文档；企业内可编辑权限回读因本机lark-cli user返回token_missing未完成，因此本轮未改飞书正文或权限，正式同步仍待完成，不阻塞代码/云连接准备。不自动重新授权或切换身份。

业务已提交/推送9b6b21d（保留准备代码）及1c9c364（分离采集面板、停用SDK路径、既有Linux合成CI覆盖）；后续继续该分支。CaptureRuntime现已实现候选，但未部署；最新状态见下方本轮部署审批段，勿开启准入或误报可用。

后续协作入口：[治理Draft PR #13](https://github.com/840832144/AI-Workspace/pull/13)、[业务Draft PR #3](https://github.com/840832144/huuuge-android-research/pull/3)。Linux合成CI run36682709050在1c9c364上42/42通过，无跳过；Windows记录和User本人入口反馈仍分别保留，不计真实云端采集。未请求完整Review或合并。

## 2026-09-30 Runtime实现与具体部署待批准

沿用TASK-0037，原登记Registry20/0collision/valid；WorkspaceSync ON_DEMAND/provider unavailable/stale6/conflicts0。代码候选已补CaptureRuntime、每段Frida TLS/令牌、专用进程与转发收尾、运行容量保护及受鉴权SSE后台页连接，复用原采集器；清理未知不释放采集锁或发布ZIP，准备期停止不再启动decoder。

环境只读回读：Linux OpenSSH8.0支持PermitListen；任务端口空闲、32.8GB可用；安全组已有22/80/443。有效nginx无TLS配置/443监听，纠正先前把注释当证书引用。手机Android12/ARM64、Huuuge当前版本运行，原官方Frida工具存在。尚未运行实际SSH隧道或新采集。

[具体部署清单/影响/回滚](https://github.com/840832144/huuuge-android-research/blob/codex/huuuge-self-service-v1/deploy/self-service/DEPLOY_APPROVAL_20260930.md)：申请两个任务Linux身份、仅回环反向SSH管理通道及Match限制、独立systemd服务/容量上限、既有公网IP的HTTPS证书/续期和nginx精确配置。需要User确认后执行；IP证书公开透明度记录需一并接受。无新资源购买、IAM/安全组/防火墙/端口映射变更；不修改晨会。

本地Windows48通过/6Linux跳过、JS通过；均为局部/合成证据，LinuxCI另记。无V1新包/新计数，真实双标签页、新包本地AI、轮流与异常恢复A—F均未验，不交完整Review。TASK-0031 Accepted及312/312/0保持；User成员登录仅本人实测。飞书待授权，不阻塞开发。Subagents: none。

下一步：User批准具体部署单后由Codex部署与实测，审批拒绝按正常流程停止；手机SSH客户端兼容/host key/最小权限/实际保护路径先通过，随后可信HTTPS与真实新批次，不用原312条替代。

Linux合成CI [run36686925269](https://github.com/840832144/huuuge-android-research/actions/runs/36686925269) 在业务代码5ef40531a2c8e268dce6e98b8fbd158f9f9a1b94通过：controller21＋descriptor4＋panel21＋Runtime8，共54/54、无跳过。包含真实Linux本地进程/回环socket的合成边界测试；不是目标云手机或V1验收。
