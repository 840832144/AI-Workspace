# TASK-0037 — Huuuge 自助研究工作台 V1

- Status: In Progress
- Project key: HUUUGE
- Owner: User
- Executor: Codex
- Priority: P1 / 本阶段完整产品交付
- Date: 2026-09-30
- Updated: 2026-09-30
- User decision: Approved
- Allocation relationship: successor
- Related tasks: TASK-0031
- Subagents: none
- Source: [PR #12 / a91bf39](https://github.com/840832144/AI-Workspace/pull/12)；2026-09-30 User范围调整（官方Web＋独立小面板）。
- Specification: [唯一完整规格](../docs/plans/HUUUGE-SELF-SERVICE-V1-20260930.md)
- Handoff: [唯一执行交接](../handoff/HUUUGE-SELF-SERVICE-V1-20260930.md)
- Draft PRs: [治理 #13](https://github.com/840832144/AI-Workspace/pull/13) / [业务 #3](https://github.com/840832144/huuuge-android-research/pull/3)；不是完整V1 Review。

## 登记与依赖

同步治理main b0a36c8、业务main6cdb1d6及在途分支；原TASK-0031正式Round1 Accepted已落库，原312/312/0快照保持。原PR未合并，不自动合并或finalize其reservation。业务新分支依赖受评52477c8及只含Accepted记录的4572b78；治理新分支依赖08ca95b，并引用PR12原规格a91bf39。新功能只在独立worktree/分支codex/huuuge-self-service-v1交付，不追加到旧试点PR。

全量Registry校验19 canonical/0 collision/valid；检索Task/Candidate/在途Huuuge分支无同目标活动Task。TASK-0036是其他方向预留，本次remote-CAS实际分配TASK-0037，reservation pending-main。登记后重建Registry并再次校验，通过后才实施。Workspace Sync ON_DEMAND、provider unavailable、stale6、conflicts0；使用最新Git来源。

## Goal

复用Huuuge项目已登记的被动RPC采集、解码、READY、Stop/Flush与结果能力，按已批准PR12扩展为单台固定游戏账号的自助网页工作台。实施及运行证据在huuuge-android-research；AI-Workspace仅保存规格、Task、Review、Status/Handoff及唯一路线图。

官方Web成员账号玩游戏＋独立采集小面板，分别登录。可信同事约定轮流；保留基本鉴权、单采集任务防重复、自动采集、四态面板、按批次停止保存/下载和现有本地AI读包。后台云端常驻；不内嵌SDK、不统一登录、不强制手机控制权交接/防重连/旧凭证撤销，不把采集锁说成手机控制锁。

四态严格为开始灰、采集中绿、错误红、结束红；正常结束通过停止图标和“已保存”文案区分错误。准备/收尾是灰色子进度；真实健康与计数驱动状态，2秒刷新、10秒状态陈旧提示、3分钟重连宽限按规格验证。

## 授权与隔离

代码、定向测试、任务独立依赖/回环服务/常驻监督及本台采集实现已批准。新增费用、公共入口、IAM/安全组/防火墙/共享nginx或其他共享服务变更，必须先提交具体最小变更、影响与回滚，由User确认。不得将Owner短期全账户OAuth复制成永久服务身份。

管理控制与采集数据通道分别验证；保留加密/TLS/鉴权、目标/版本/ABI和专用进程清理校验。取消旧Ticket撤销与SDK作为准入条件，不再等待厂家工单。官方Web手机控制沿用User成员账号；原公网ADB不等于受保护长期管理面。

密码、令牌、真实地址、设备/账号标识、SDK受限整包、原始采集和完整响应不进公共Git。原312条永久保留；不擅自删除新数据或为下载读取旧试点数据冒充新验收。

## 本阶段验收（全部完成才交完整Review）

- [ ] A：未参与开发的策划通过官方Web成员账号＋独立小面板，仅浏览器完成入口；User本人已到Android桌面/Huuuge大厅单列通过，不等于同事盲测。
- [ ] B：开始自动采集，灰→绿→红结束及独立红色错误符合真实状态；计数、时长、刷新与健康实测。
- [ ] C：本轮新数据结束下载/复下；manifest、数值、请求响应关联一致；现有本地AI无需云连接/采集环境回答覆盖范围及一项游戏体验问题并指出证据。
- [ ] D：两个面板身份按约定轮流各采一轮；只允许一个采集任务，批次隔离，越权停止/下载失败，游戏账号固定。不要求厂商旧凭证撤销、防重连或强制控制权交接。
- [ ] E：刷新/短断线、宽限超时、worker停止或游戏退出、结束/打包/下载重试；错误可见、片段缺口保留、结果不覆盖、无重复进程。
- [ ] F：退出Codex管理会话后网页再跑一轮；定向重启本任务服务验证持久化和恢复，不重启共享主机；交付启停/检查/更新/回滚说明。
- [ ] 安全：未登录、管理接口、越权下载、任意目标/路径、重复开始/结束、过期凭证、TLS失败及导出泄露定向验证。

组件已部分实现，完整V1仍未完成/未验收；不得用合成用户当真人盲测或用旧312条计入V1。人员、权限、入口缺口分别报告，面板/下载/自助使用不推迟至下阶段。

## 2026-09-30 范围调整、实测与剩余工作

- 沿用TASK-0037及既有独立分支；Registry 20 canonical/0 collision/valid，无新分配。TASK-0031 Accepted及312/312/0、8条Slots原结果不变。
- User成员账号实测通过：已创建/绑定现有手机，官方Web登录并到Android桌面及Huuuge大厅。来源为User本人反馈；没有扩大为同事盲测、Android客户端或V1采集验收。
- 本版改为官方Web游戏＋独立采集面板。SDK内嵌、统一登录、强制防重连、旧Ticket撤销和强制控制交接退出本版验收；旧SDK实验和代码保留历史，厂家咨询不再待办/阻塞。
- 保留现有登录、SQLite状态/采集锁、面板、片段编排、导出和原内核心跳；取消控制凭证链路的活动依赖，单采集任务锁不代表手机控制锁。代码与合成证据不代表已部署。
- 仍需完成受保护管理通道、云运行适配、TLS自动轮换/专用进程清理、容量保护、受控HTTPS入口及真实A—F。既有私网ADB检查超时；无V1新增采集批次。
- 新费用、公开入口、网络/IAM或共享服务变更按原边界先确认。本轮未作这些变更，无晨会修改。
- 下一步：在现有Linux/手机明确可部署的受保护采集通道及其最小身份需求，提交实际需要的精确变更与回滚；继续完成云端常驻/真实启停和新包验收。保持In Progress。
- 验证：小面板17/17合成检查，原采集器16通过/5项Linux专属跳过，JS语法通过；不计云端V1验收。路线图Git已同步；正式飞书权限回读返回user token_missing，本轮未发布，不把文档授权作为采集实现前置。
- 业务提交：9b6b21d保留原准备代码；1c9c364分离官方Web与采集面板并接入既有Linux合成CI。云运行绑定尚未实现；保持Draft准备，不作为完整Review。
- Linux合成CI：[run36682709050](https://github.com/840832144/huuuge-android-research/actions/runs/36682709050)，源码1c9c364，controller21＋descriptor4＋panel17共42/42通过、无跳过；仍不计真实手机/V1验收。

## 交付与收尾

完整代码、独立部署与升级/回退入口、脱敏配置、中文使用页、维护说明、A—F实测记录与脱敏样例包；原Task/Status/Handoff和唯一Product Roadmap同步。所有验收完成才交ChatGPT Review，未完成保留In Progress并清楚记录缺口。合并仍由User决定；canonical进入main后finalize本reservation。

## 2026-09-30 Runtime实现与具体部署待批准

沿用TASK-0037，原登记Registry20/0collision/valid；WorkspaceSync ON_DEMAND/provider unavailable/stale6/conflicts0。代码候选已补CaptureRuntime、每段Frida TLS/令牌、专用进程与转发收尾、运行容量保护及受鉴权SSE后台页连接，复用原采集器；清理未知不释放采集锁或发布ZIP，准备期停止不再启动decoder。

环境只读回读：Linux OpenSSH8.0支持PermitListen；任务端口空闲、32.8GB可用；安全组已有22/80/443。有效nginx无TLS配置/443监听，纠正先前把注释当证书引用。手机Android12/ARM64、Huuuge当前版本运行，原官方Frida工具存在。尚未运行实际SSH隧道或新采集。

[具体部署清单/影响/回滚](https://github.com/840832144/huuuge-android-research/blob/codex/huuuge-self-service-v1/deploy/self-service/DEPLOY_APPROVAL_20260930.md)：申请两个任务Linux身份、仅回环反向SSH管理通道及Match限制、独立systemd服务/容量上限、既有公网IP的HTTPS证书/续期和nginx精确配置。需要User确认后执行；IP证书公开透明度记录需一并接受。无新资源购买、IAM/安全组/防火墙/端口映射变更；不修改晨会。

本地Windows48通过/6Linux跳过、JS通过；均为局部/合成证据，LinuxCI另记。无V1新包/新计数，真实双标签页、新包本地AI、轮流与异常恢复A—F均未验，不交完整Review。TASK-0031 Accepted及312/312/0保持；User成员登录仅本人实测。飞书待授权，不阻塞开发。Subagents: none。

下一步：User批准具体部署单后由Codex部署与实测，审批拒绝按正常流程停止；手机SSH客户端兼容/host key/最小权限/实际保护路径先通过，随后可信HTTPS与真实新批次，不用原312条替代。

Linux合成CI [run36686925269](https://github.com/840832144/huuuge-android-research/actions/runs/36686925269) 在业务代码5ef40531a2c8e268dce6e98b8fbd158f9f9a1b94通过：controller21＋descriptor4＋panel21＋Runtime8，共54/54、无跳过。包含真实Linux本地进程/回环socket的合成边界测试；不是目标云手机或V1验收。
