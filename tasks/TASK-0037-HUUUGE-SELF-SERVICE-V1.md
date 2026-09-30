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
- Source: [PR #12 / a91bf39](https://github.com/840832144/AI-Workspace/pull/12)
- Specification: [唯一完整规格](../docs/plans/HUUUGE-SELF-SERVICE-V1-20260930.md)
- Handoff: [唯一执行交接](../handoff/HUUUGE-SELF-SERVICE-V1-20260930.md)

## 登记与依赖

同步治理main b0a36c8、业务main6cdb1d6及在途分支；原TASK-0031正式Round1 Accepted已落库，原312/312/0快照保持。原PR未合并，不自动合并或finalize其reservation。业务新分支依赖受评52477c8及只含Accepted记录的4572b78；治理新分支依赖08ca95b，并引用PR12原规格a91bf39。新功能只在独立worktree/分支codex/huuuge-self-service-v1交付，不追加到旧试点PR。

全量Registry校验19 canonical/0 collision/valid；检索Task/Candidate/在途Huuuge分支无同目标活动Task。TASK-0036是其他方向预留，本次remote-CAS实际分配TASK-0037，reservation pending-main。登记后重建Registry并再次校验，通过后才实施。Workspace Sync ON_DEMAND、provider unavailable、stale6、conflicts0；使用最新Git来源。

## Goal

复用Huuuge项目已登记的被动RPC采集、解码、READY、Stop/Flush与结果能力，按已批准PR12扩展为单台固定游戏账号的自助网页工作台。实施及运行证据在huuuge-android-research；AI-Workspace仅保存规格、Task、Review、Status/Handoff及唯一路线图。

简单账号密码+安全记住登录；多个工作台身份轮流独占；内嵌厂商游戏画面；开始自动采集；实时面板；结束封存下载脱敏含值AI包；用现有本地AI读包。后台在现有云端常驻，不依赖策划电脑或Codex会话。不切换Google/Huuuge账号，不接其他游戏，不重写采集内核。

四态严格为开始灰、采集中绿、错误红、结束红；正常结束通过停止图标和“已保存”文案区分错误。准备/收尾是灰色子进度；真实健康与计数驱动状态，2秒刷新、10秒状态陈旧提示、3分钟重连宽限按规格验证。

## 授权与隔离

代码、定向测试、任务独立依赖/回环服务/常驻监督及本台采集实现已批准。新增费用、公共入口、IAM/安全组/防火墙/共享nginx或其他共享服务变更，必须先提交具体最小变更、影响与回滚，由User确认。不得将Owner短期全账户OAuth复制成永久服务身份。

管理控制与采集数据通道分别验证。先确认既有手机Web SDK/便捷账号可用与旧控制凭证撤销；不能验证撤销则保持占用。原公网ADB不等于受保护长期管理面；不关闭TLS/鉴权、不重建手机、不假装UI隐藏实现授权。

密码、令牌、真实地址、设备/账号标识、SDK受限整包、原始采集和完整响应不进公共Git。原312条永久保留；不擅自删除新数据或为下载读取旧试点数据冒充新验收。

## 本阶段验收（全部完成才交完整Review）

- [ ] A：未参与开发的策划，仅浏览器简单登录并进入可玩画面，不进云控制台或要求后台代操作。
- [ ] B：开始自动采集，灰→绿→红结束及独立红色错误符合真实状态；计数、时长、刷新与健康实测。
- [ ] C：本轮新数据结束下载/复下；manifest、数值、请求响应关联一致；现有本地AI无需云连接/采集环境回答覆盖范围及一项游戏体验问题并指出证据。
- [ ] D：两个真实工作台身份各采一轮；并发只有一个控制者，数据隔离；越权停止/下载失败，旧Ticket/标签不能干扰下一人，游戏账号固定。
- [ ] E：刷新/短断线、宽限超时、worker停止或游戏退出、结束/打包/下载重试；错误可见、片段缺口保留、结果不覆盖、无重复进程。
- [ ] F：退出Codex管理会话后网页再跑一轮；定向重启本任务服务验证持久化和恢复，不重启共享主机；交付启停/检查/更新/回滚说明。
- [ ] 安全：未登录、管理接口、越权下载、任意目标/路径、重复开始/结束、过期凭证、TLS失败及导出泄露定向验证。

当前未实现/未验收；不得用合成用户当真人盲测或用旧312条计入V1。人员、权限、入口缺口分别报告，面板/下载/自助使用不推迟至下阶段。

## 交付与收尾

完整代码、独立部署与升级/回退入口、脱敏配置、中文使用页、维护说明、A—F实测记录与脱敏样例包；原Task/Status/Handoff和唯一Product Roadmap同步。所有验收完成才交ChatGPT Review，未完成保留In Progress并清楚记录缺口。合并仍由User决定；canonical进入main后finalize本reservation。
