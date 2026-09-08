# TASK-0028 — EarlyMeeting 本机回调与本人行同卡填写

- Status: Review
- Project key: EARLYMEETING
- Human alias: 
- Owner: User / ChatGPT
- Executor: Codex
- Priority: P1
- Date: 2026-09-07
- Updated: 2026-09-08
- Candidate provenance: `tasks/candidates/CANDIDATE-20260907-EARLYMEETING-LOCAL-CALLBACK.md`
- Allocation relationship: new
- Related tasks: none

## Goal

在 User 实际 Windows 电脑维护“策划 / 程序”本人行与自动“今日交付”同卡汇总；支持本人删除、醒目分区、提交后普通文字展示及再次编辑，以及多群独立的工作日北京时间 09:45 每群每天一张卡片。当前接入测试群及两个正式群，两个正式群均从 2026-09-08 开始。

## Scope

最新交付 EarlyMeeting@e5f0cbd / [PR #4](https://github.com/840832144/EarlyMeeting/pull/4)（AI核心10be33d）：User 填好本机API Key并限定只对正式群2开放，已热更新该群原卡，8份已提交记录识别ready、提取6项交付、失败及待处理0。测试群和正式群1保持v12手填交付，不调用AI或改变原布局；三群原记录、权限及09:45保留。八脚本语法核对通过，无新增自动测试或模拟操作。原卡恢复、模型及汇总实际结果在EarlyMeeting；升级后真实重提/删除尚未观测，直接使用反馈。Task返回Review，reservation保持pending-main，不标记Done。Subagents: none。

2026-09-08 当前范围：仅正式群2个人每次成功提交或编辑后重提均异步调用DeepSeek抽取今日交付，只收录明确标记的具体事项，按 @原行人员 + 工作汇总；支持前置标题及工作末尾标记，不将整份晨会纳入。替换本人旧汇总，成功空结果或删除个人行则移除；失败保留已保存晨会及旧汇总，过期返回不得覆盖新提交。其他群继续手填交付且不调用AI；保留群隔离、本人权限及并发队列。模型只接收本次个人提交文本，凭据仅本机配置，业务实现与部署证据均在EarlyMeeting。Registry14 canonical / valid，续接本Task，不另占号。Subagents: none。以下为历史迭代记录。

2026-09-08 最新交付：EarlyMeeting@01714fc / PR #4，按 User 截图提议，未提交显示“提交”；成功后普通文字及“编辑”，点击编辑带回原文并再次提交，今日交付采用相同行为。编辑进入独立队列并检查权限、递增版本，保留原记录。已热更新三群原卡，真实 CONNECTED / LAYOUT_UPDATED / MEETING_READY，行数1/11/10；未新发消息或模拟员工点击。三脚本语法检查通过，新编辑→提交真实交互由 User 使用中反馈。两仓库已 fetch，Registry14 canonical / valid，续接本 Task，返回 Review，reservation pending-main。详细说明与脱敏证据均在 EarlyMeeting。Subagents: none。

2026-09-08 当前交付：EarlyMeeting@f9b14ed / PR #4 已修复两个正式群共用的并发提交逻辑。正常处理中接收其他行的有效请求并按本群队列处理；完成保存时保留期间新排入的请求，未知结果保留等待恢复。最小字段仅存本机；本人权限、群/消息/行版本、同卡数据及09:45调度保留，预填关闭。已部署并真实 CONNECTED，三群原消息恢复1/10/9行，无重新发卡。完成两个脚本的语法检查与相关代码路径审查，没有自动测试、哈希比对或模拟群操作；修复后真实同时提交尚未观测，不冒称验收通过。实现、操作和脱敏证据均在 EarlyMeeting；本 Task 返回 Review，reservation pending-main。Subagents: none。

User 新增跨会话开发要求：提前考虑多人并发、重复点击、处理中到达的新请求及失败/重启恢复；验证只围绕具体风险，减少无关测试、重复核对与哈希比对。已按明确授权更新本机全局 `~/.codex/AGENTS.md`，未将本项目事实加入全局。Memory Check：当前事实直接更新 Task/Handoff，不重复创建 Candidate。Idea Check：本次为当前 Task 内的小修复，不新增 Roadmap 条目或 Future Task，也不为此重发产品文档。

2026-09-08 最新决定（EarlyMeeting@839b481）：User 要求正式群2恢复群1规则，并要求在原卡片生效。已将群2设为 prefill=false、submit=owner、delete=owner；当前三个群均仅本人操作个人行，今日交付仍全群共用，群ID、记录和工作日09:45定时保留。短暂重启后 CONNECTED / 三群 owner/owner / MEETING_RESUMED rows=1/8/6，未重新发卡或模拟操作。预填名单匹配及 im:chat:readonly 开通流程已暂停，不再等待权限；可选实现保留但不启用。Registry14 canonical / 0 collision / valid，Task 回到 Review，等待正式代码 Review，不标记 Done。Subagents: none。下方预填授权与权限等待文字为9月7日历史记录。

User 已确认：仅正式群2开放任意行提交与删除；正式名单为策划3人、程序6人（真实姓名及 ID 仅留受控本机）。本次为把已提供姓名对应到现有应用的实际 @ 标识，可通过 EarlyMeeting 官方 SDK 只读核对该群成员；同名、缺失或权限不足时不猜身份，不扩大通讯录权限。此只读核对仅用于名单配置，不恢复已暂停的 10:15 提醒。其他群仍仅本人行可提交/删除。

2026-09-07 追加：正式群2按已提供的策划3人、程序6人预填新卡片空行，并允许本群所有人提交/删除任意行；其他群仍 owner。实现 EarlyMeeting@12c4086 已部署并推送，真实 CONNECTED / groups=3、GROUP_3 submit=all delete=all、GROUP_1/2 owner/owner；原测试群两行保留。名单匹配实际返回 99991672，需 im:chat:readonly，等待 User 开通生效后继续；当前 prefill=false，不冒称已经预建。没有新增自动测试或模拟操作。继续 TASK-0028 / In Progress，Registry 14 canonical / 0 collision / valid，不另占号。Subagents: none。

同轮追加：新增与策划/程序同级的“今日交付”，只含内容和操作两列，直接显示全群共用文本框；User 明确编辑权限向所有人开放。所有群成员可提交或清空共享交付，个人晨会行仍仅本人可操作，更新最近同一张卡片。保存最小内容与版本到现有按群/日期的受控状态，不引入成员名单读取或额外权限。

2026-09-07 最新决定：User 明确当前卡片“这回没问题了”，记录为本轮 UI 用户验收通过；正式代码仍待 Review。发卡从 10:00 改为工作日北京时间 09:45。User 曾提出 10:15 按指定应参加名单 @ 未提交人员，随后明确暂停、后续看需求；本轮不实施或启用提醒，不收集名单、不读取群成员。此次 Registry 14 canonical / 0 collision / valid、远端同目标仅 TASK-0028，继续本 Task，不新占号。以下旧时间及待 UI 验收文字为历史快照。

2026-09-07 本轮 UI 反馈：保存按钮改为“重新保存”，操作移至第三列，内容框默认一行，缩短行距。User 随后明确直接热更新最近一张，不再重新发送，原补发要求已取消；不模拟用户操作，不将“没问题就通过”视为已验收。续接本 Task，Registry 再验 14 canonical / 0 collision / valid。

2026-09-07 最新追加授权优先于下方历史边界：User 确认两区域效果可用，要求本人可删除误建行后重新选区，“策划”“程序”标题放大加粗；增加多群配置和周一至周五北京时间 10:00 调度，各群按日期独立防重。User 明确正式群稍后再发，目前只在既有测试群使用。不增加复杂或多余测试/验收，不模拟员工操作，不启用系统自启或修改全局网络配置。正式 Task 继续 TASK-0028，不另占号。

当前执行增量为下方“User 追加批准的实施范围”，业务唯一入口指向 EarlyMeeting 当前方向及操作说明。以下 PR #3 描述保留初始诊断阶段依据；其“不保存、不更新”约束已被 User 针对指定测试群本人行的追加授权替代，其他群及定时仍不在范围。

本 Task 执行规格唯一入口为 [EarlyMeeting 当前方向](https://github.com/840832144/EarlyMeeting/blob/b18e39365bf95addbff955d09827a9d30e2153fb/docs/CURRENT_DIRECTION.md) 与 [PR #3](https://github.com/840832144/EarlyMeeting/pull/3)。旧 PR #1/#2 已 CLOSED / Superseded，不合并旧业务路线。保留现有「晨会记录」应用、模板和已成功发送流程。

项目声明的结果契约为目标 Windows 本机运行检查、脱敏长连接诊断、现有卡片交互接收及表单传值核对；采用 EarlyMeeting 专属实现与飞书官方 SDK。AI-Workspace 仅存 Task、治理引用和状态，不复制业务实现；不向 Document Assistant 加入本业务。

检查实际目录与依赖，审查后选择复用旧测试代码，复现入口请求/凭据校验/WebSocket 握手失败阶段，按证据作最小修复。只处理指定测试群卡片，持续保持一份接收进程。凭据由 User 在本机安全输入；User 本轮追加授权改为仅本机 JSON，按当前用户/SYSTEM ACL 限制、Git 忽略，禁止回显或上传。回调测试提示必须明确未保存、未更新。

## Non-goals

不扩展到未配置或未经 User 指定的群；两个正式群按已确认的 2026-09-08 起始日期发送，今天不补发。不新建应用、不覆盖原模板、不改为多维表格，不购买/部署公网服务、不设置自启/系统服务、不改全局代理、防火墙或 TLS。旧完整 MVP 不恢复。

## Deliverables

EarlyMeeting 独立实现分支中的最小修复、必要测试、中文一键启动/检查/停止/回滚说明、目标本机脱敏实测摘要、STATUS 与 Handoff；提交 commit 并推送等待 ChatGPT Review。所有业务交付保留在 EarlyMeeting。

## User 追加批准的实施范围（2026-09-07）

当前交付 EarlyMeeting@5634d83 / PR #4（核心实现 590ed0d）：v11 已热更新原卡片为策划、程序、今日交付三个同级区域，保留两条个人记录。今日交付为全群共用文本框，所有群成员可提交或清空；个人行仍仅本人操作。工作日北京时间 09:45 每群每天一张，10:15 提醒暂停。现场 CONNECTED / SCHEDULE_CONFIGURED time=09:45 / LAYOUT_UPDATED / MEETING_READY；未模拟交付提交或清空，新增区域不冒称已经用户验收。代码、说明与脱敏证据保留在 EarlyMeeting。Subagents: none。

两个正式群已启用：User 完成群2本机填写及添加，沿用工作日北京时间 09:45、每群每天一张；两个正式群均从 2026-09-08 开始，测试群保留。按既有配置 ID 排除识别唯一新增群，保留 User 修改的本机群名。实际重启后 CONNECTED / SCHEDULE_CONFIGURED groups=3 scheduled=3 time=09:45，测试群原消息两行恢复，今天未向正式群补发；未来正式群发送未到时实测。Registry 14 canonical / 0 collision / valid，续接本 Task 为 Review，不另占号。真实群名称及标识不进入 Git。以下为历史迭代记录，以本段与最新 User 决定为准。

最新交付 EarlyMeeting@f5aff47 / PR #4：v10 在新行首次成功提交前显示红色“未提交”，点击仍提交本人内容；成功后变为蓝色“提交”。最近原消息已更新，两行保留，没有补发或模拟操作。Task 继续 Review；本轮最终代码、说明、脱敏证据与按钮可见性限制均在 EarlyMeeting。

最终反馈交付：EarlyMeeting@329d0c3 / PR #4，v9 将人员/内容/操作区设为 80/340/92px，按钮最终为“提交 / 删除”，默认一行、达列宽自动换行增高。已更新最近原卡片并保留两行，不重发。User 要求隐藏他人按钮，当前共享卡片模式不支持逐查看者隐藏，明确该项未实现，后端本人归属校验保留；不为此扩大架构。Task Review，等待 User 实际查看，不新增自动测试。Subagents: none。

最新交付：EarlyMeeting@056c216 / PR #4，布局 v6 按 User 要求将“重新保存 / 删除本行”并排移到右侧操作区域，内容默认一行、行距收紧；已热更新最近一张，保留两行，本轮未重新发送。真实删除→再添加→保存已由 User 操作并取得成功状态；新 UI 待 User 查看。Task 回到 Review，不追加自动测试，不把条件式通过当作正式通过。Subagents: none。

本次交付：EarlyMeeting@81ba062 / PR #4 已实现本人行删除、24px 加粗标题、多群独立的工作日北京时间 10:00 每群每天一张；桌面运行目录已升级，只启用测试群，正式群等 User 指定。真实连接和同卡布局更新通过，保留两行；当天已有消息未重复发送。操作说明与脱敏证据在 EarlyMeeting，未新增自动测试或模拟操作；未来 10:00 与删除回调未冒称实测。Task 进入 Review，不标记 Done。下方为需求演变历史，最新授权优先。

本次准备：两仓库与各自远端一致；检索全部 origin 分支，仅发现 TASK-0028 同目标条目。Registry 复验 14 canonical / 0 collision / valid，reservation pending-main。项目 Capability 延续 EarlyMeeting 的本人行与同卡契约，追加本人删除、按配置群与北京时间日期发送；实现仍在 EarlyMeeting，使用官方 SDK，不引入 Document Assistant 业务代码。Subagents: none。

收尾范围：User 明确只实现核心功能，不增加复杂或多余的测试和验收。按最终两区域方案提交现有实现和最小使用说明即可；不以额外多人/手机/压力测试作为交付前置，已完成证据与未运行检查如实记录，等待 Review，使用中有问题再修。

最终 User 决定：取消第二列及自动部门读取，改为“策划”“程序”两个添加区域，各自仅“人员、晨会内容”两列；根据点击哪个区域的加号决定行归属。不再申请部门字段权限、不读取通讯录。此决定替代下文的自动部门阶段，所有实现仍续接 TASK-0028；每人每张卡片一行的既有防重默认保留。

最新 User 验收调整：第二列由手填“职位”改为从实际操作者飞书通讯录自动带入“部门”，员工只填写晨会内容；允许现有应用按需读取本人部门关联与部门名称，不枚举或导出员工通讯录。权限缺少时由 User 在现有应用后台开启必要读取项并发布，不绕过可用范围/通讯录范围，不猜部门。User 要求停止自动测试，改为直接群内验收、边验边改；未验收项据实保留。

User 已确认本人行交互示意“没问题，我要的就是这个效果”，预计 10～20 人，逐行向下排列。续接本 Task，不另占编号。此批准将诊断阶段的“不保存、不更新”扩大为：仅在本机配置的测试群，手动创建本轮动态卡片并更新同一条消息；保存操作者本人提交的职位、内容和最小关联标识到受控本机目录。保留现有应用、原模板和原发送入口；新增布局由 EarlyMeeting 专属代码构建，不擅自发布或覆盖原模板。

追加验收：初始零记录行；真实操作者自动填人员；每人每张卡片一行，重复点击防重；同一表单提交职位和内容；服务端拒绝代改他人行、其他群或其他消息；新增或保存只更新对应组件；重启继续原消息与已有记录；双人并发和未提交输入保留需真实客户端验证。离线结果与实测分开记录，不把未验收项写 Done。操作说明、约束与证据仅在 EarlyMeeting。

本次重新 fetch 两仓库并核对远端同目标 Task，只有 TASK-0028；Registry 14 canonical / 0 collision / valid，reservation 继续 pending-main。项目 Capability 由 EarlyMeeting 当前方向声明，官方 SDK 为实现绑定。新增应用权限或应用版本发布仍由 User 在现有应用后台操作。Subagents: none。

## Acceptance

1. 确认 User 实际测试目录、Node / SDK 版本及同应用进程边界。
2. 有真实 WebSocket 连接成功证据；安装或入口请求成功不代替握手验收。
3. 有指定群卡片真实 card.action.trigger 与表单实际传值证据，在所选策划 / 程序区域建本人行，新增/保存更新同一消息且拒绝代改；姓名来自真实操作者，不读取部门。
4. 一键停止后不继续接收；失败能够定位阶段，保留未确认项。
5. 不泄露凭据、内部标识、员工内容、原始回调或完整日志。处理中或结果未知不声称保存成功；本轮诊断模式仍提示未保存。

## Safety

仅允许本机受控输入/受控环境中的凭据；不回显、不写入 Git、不导入旧 .env。输出采用有限字段白名单，禁止原始 SDK 日志及回调。User 在本轮追加要求“一键发送”：允许使用现有应用、现有模板和本机配置的指定测试群，手动补发本轮一张测试卡片；不自动重发成功请求，结果不明确时保留同一请求防重。接收反馈说明未保存、未更新，不扩展到其他群、公共卡片更新或定时。系统策略、应用权限或版本发布需要 User 明确决定。Subagents: none / OFF。

## Validation

2026-09-07 AI-Workspace main@1dd6de3：完整 scan / validate 为 13 canonical、0 collision、valid；全部远端分支相关任务目标检索无 EarlyMeeting 同目标条目。既有 TASK-0027 reservation 属于其他项目且保持不动。Approved Candidate 由 remote-CAS allocator 晋升为 TASK-0028，project_key=EARLYMEETING 合法；reservation 保持 pending-main，Review 后 canonical 进入 main 才 finalize。

Workspace Sync：ON_DEMAND、conflicts=0、provider_available=false、stale=6；明确保留云端不可用状态，不改变运行模式。PR #3 基线 b18e393、EarlyMeeting main dfdb6fb。User 已确认本机桌面 EarlyMeeting-local-callback-test 为实际目录，v0.1.0 / Node v24.20.0 / SDK 1.73.3。离线回归与真实连接、真实回调结果分别记录到 EarlyMeeting，尚未验证不得写 Done。

首次 Candidate 日期格式校验拒绝 YYYY-MM-DD，未占号；改为规范 YYYYMMDD 后成功。Registry 只由 scan --write-registry 重建。

## Handoff

准备 Gate：范围已获 User 批准，合法任务已 Ready；本 Task / Registry / Handoff 推送并复验后进入实施。实施完成或现场确有阻塞时，更新本 Task 和 EarlyMeeting STATUS / handoff/CODEX.md，返回业务 branch/commit、根因证据、离线/现场结果、剩余阻塞与唯一下一步，等待 Review；不自行合并 main。Subagents: none。

## 实施进展（2026-09-07）

- 最新增量：新版空卡片已实际发送；User 新增一行并共同保存旧职位/内容，UI 反馈后已修正三列对齐，随后改为自动部门。①基本通讯录与③部门基础权限生效后，API code=0 但部门所属字段缺失；仍需②字段权限。User 仅要求部门名称、未授权手填替代，不绕过审核。具体实现、脱敏证据及操作入口见 EarlyMeeting PR #4 的 MEETING.md / MEETING_ACCEPTANCE.md。User 要求直接验收后不再追加自动测试或模拟操作，Task 保持 In Progress、交付 commit 等待 Review，不标记 Done。

- 正式准备 commit a68b663 已推送；Registry 14 canonical / 0 collision / valid，remote reservation pending-main。
- 唯一 Product Roadmap 已按 EarlyMeeting PR #3 Idea Handoff 原位更新：正文回读通过，企业内可编辑 verified，自动登记/导航中心回读通过；Hub 31 项、unique_links=true。未修改 Document Assistant 实现。
- Context refresh：72 sources / 0 broken link / 0 secret issue；Doctor ok；保持 ON_DEMAND。
- EarlyMeeting 已在 User 实际 Windows 电脑使用受控本机 JSON 启动，入口与真实长连接成功。后续重启已复现入口成功后的握手失败；SDK 丢弃底层错误对象已确认，增加传输观察器后再次连接，底层间歇原因尚未确认。
- 下一动作：ChatGPT Review 已提交的最小修复、独立文本回调与停止证据，保留三列整组表单及间歇网络根因未验收；具体业务证据仅留在 EarlyMeeting。

- 业务实现最终提交 EarlyMeeting@878f42a，[PR #4](https://github.com/840832144/EarlyMeeting/pull/4) 等待 Review；43 组检查与 8 项新增测试通过，真实 HTTP 101 / CONNECTED、手动发卡及成功防重、两次独立文本回调和 STOP_VERIFIED / NOT_RUNNING 已取得。
- User 最终确认漏加 card.action.trigger；补配后真实输入回传通过。现有模板只有单行独立输入，form_value 字段数 0，Acceptance 3 中整组表单仍未验收；间歇握手的底层网络原因也未确认。不得将 Review 写成 Done 或完整业务验收。
- User 澄清多人同卡汇总目标，业务范围与最小方案见 [EarlyMeeting 后续产品目标](https://github.com/840832144/EarlyMeeting/blob/codex/task-0028-local-callback/docs/CURRENT_DIRECTION.md#后续产品目标澄清)。不自动扩大本 Task 到保存、模板布局改动、公共卡片更新或 10:00 定时，不新建 Future Task。Subagents: none。
