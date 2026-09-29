# Huuuge 单实例云端调试任务（修订版 v2）

- Kind: execution-support；不是第二个 canonical Task，不分配新编号。
- Date / Updated: 2026-09-29
- Revision: v2 — 补齐 Google Play / GMS 安装、本人登录和商店安装游戏的必需前置。
- Actor: ChatGPT
- Owner / 资源与操作人: User 本人；不等待另一位技术对接人。
- Executor: 原 Codex 会话，继续作为唯一实现与运行执行者。
- Canonical: [TASK-0031（现有任务分支）](https://github.com/840832144/AI-Workspace/blob/codex/huuuge-cloud-single-instance/tasks/TASK-0031-HUUUGE-CLOUD-SINGLE-INSTANCE.md)
- Governance: [AI-Workspace PR #4](https://github.com/840832144/AI-Workspace/pull/4)
- Implementation: [业务 PR #2](https://github.com/840832144/huuuge-android-research/pull/2)
- Plan PR: [AI-Workspace PR #11](https://github.com/840832144/AI-Workspace/pull/11)
- Scope: 已批准的一台云端 Huuuge 游戏与被动采集闭环；不扩大为多人平台。
- Plan status: User 要求修订后重新下发；不是 Google Play 已安装的回执、准备代码 Accepted Review 或云端验收通过。

## 一、本次修订与唯一执行链路

User 指出上一版漏掉谷歌商店安装，要求重新出任务。原版从 Android 桌面直接跳到游戏安装/试跑不完整。本版原位替代旧执行顺序，并保留已有连接、采集、停止与数据安全要求。

```text
确认本次云手机与管理入口
→ 检查并安装/启用 Google Play 商店及配套 GMS
→ User 本人登录 Google，验证商店可用
→ 从 Google Play 安装/确认 Huuuge
→ 无 Frida 探针的游戏登录与运行基线
→ 云端 Linux 到云手机的受控连接
→ 真实新增采集及解码
→ 正常结束、保存与回读
```

**Google Play 是本轮交付的一部分，不是交给 User 自己补齐的部署前提。** Codex 负责检测、安装/启用、必要的正常更新、安装来源核验和排障；User 仅亲自完成 Google/游戏身份登录、验证码与授权决定、普通游戏操作。

不得只把某个 Huuuge APK 装进去就绕过商店验收；不得只出现 Play 图标就宣称 GMS 完成。商店安装链路与游戏/采集依赖有阻塞时，分别记明，不能静默缩减目标。已安装的正常组件和已有游戏数据优先保留，不为测试强制重装。

## 二、当前依据与证据边界

2026-09-29 User 已提供云手机网页 Android 桌面及终端截图，并报告相关工具已安装。本轮 User 又明确补充谷歌商店安装要求。桌面可见不证明商店缺失或已安装，不证明 CLI 已认证、终端属于独立 Linux ECS，也不证明 Huuuge 已可玩。截图、账号、实例 ID、主机名和会话标识不复制到 Git。

本次重读基线：AI-Workspace main `b0a36c8e1b75299814b3354530a58bbf59518714`；正式任务/原 Handoff 分支 `872e2dca713d1166c8aad479944a32116474f2ae`；业务准备 PR #2 `402e0d4a6fe33e741b5388949d5e1826252ccb35`；旧调试方案 PR #11 `f37f3a6c6c0f8edf4887ee7d57ff493e2ccc12bb`。Task 与业务 Status 仍只登记准备 Review，没有本轮 GMS、商店、游戏或采集现场通过证据。

原 Codex 先安全同步最新 main 和自己的任务分支，保护未提交改动；核对当前 PR/评论、Task、Status、Handoff。准备 PR 当前未合并，冲突按内容解决，不强推、不自动合并、不覆盖其他任务。将本次 User 修订同步为原任务的 Changes Requested/后续实际执行状态，按既有 Registry validator 重建验证，不分配新 ID。本次 ChatGPT 只修订支持文档和交接，未运行 Workspace Sync/Registry validator，也未更改 canonical Task 状态或 Registry。

### 已查到的官方能力，不等于本实例已经可用

- 阿里云官方 FAQ 表示云手机默认支持 GMS（Google Play），但须能连接 Google Play 服务。[S6]
- Android 12 镜像发布说明的 V25.10.3 提到 GMS 一键配置，V26.09.1 提到 GMS 兼容优化。[S7] 这是优先复用厂商能力的依据，不是本实例已安装商店、已获 Google 认证或已找到具体安装命令的证明。
- 本次未取得适用于 User 实际镜像的完整 GMS 安装按钮/命令说明。Codex 要从实际系统、厂商入口及对应官方操作说明确定，不编造按钮、包下载地址、setprop 命令或固定 APK 安装顺序。
- Huuuge 当前官方商店页对应 `com.huuuge.casino.slots`，开发者显示为 Huuuge Games - Play Together。[S9] 可用地区、设备适配和实际安装版本以 User 云手机商店的现场结果为准。

## 三、保持两类连接分开

```text
User 浏览器 → 厂商网页 → Android 云手机：Google Play/GMS、Huuuge、设备端探针
Codex 管理电脑 → Workbench CLI/已授权管理通道 → 云端 Linux 采集执行端
云端 Linux 采集执行端 → 带认证的受控数据连接 → Android 云手机
```

Workbench CLI 的官方文档和 Skill 以 Linux ECS 为对象；页面出现 Workbench 终端不证明 CLI 可接受云手机 ID。[S1][S2] 管理电脑可运行 Codex/CLI，但生产采集、解码和必需常驻转发必须在云端。Android 使用 Linux 内核，不能只凭 `uname` 输出 Linux 就把它当作通用 Linux 执行端。

独立 Linux 执行端尚未确定时，可以先用本次已授权的云手机网页/系统命令入口完成 GMS、商店和游戏准备。缺哪项只报告哪项，不让云端服务器准备阻塞可独立完成的商店安装。不得擅自购买 ECS、在未知厂商宿主机操作或用本地蓝叠代替。

## 四、分步执行

### 第 1 步：确认当前云手机、系统和 Google 组件现状

**做什么**

原 Codex 检查已装 CLI 的 `workbench version`、`workbench --help`、`workbench exec --help`；不重复安装，不输出 `workbench config get`、凭据文件或环境变量全集。实际凭据由 User 通过受控配置提供，不向聊天索要主账号 AccessKey。

在已确认属于本次云手机的授权入口，只读记录实际 Android/镜像版本、设备 ABI、可用存储、日期时间是否正确、互联网及 Google 服务连接状态。香港地域和网页桌面可见都不能替代手机自身联网实测。只检查必要字段，不导出设备标识、Google账号数据、完整属性表或全量日志。

检查应用抽屉/系统应用及实际包状态，区分“没有桌面快捷图标”“已装未启用”“只装商店”“配套服务缺失”。核对 Play 商店、Google Play 服务、Google 服务框架及本镜像需要的账号/下载组件；包名和需要哪些组件按本机及官方方案确认，不把网上的三件套/四件套固定为适用于所有镜像。

**成功表现**

分别记录云手机目标已确认、实际系统版本、Google组件已装/停用/缺失和 Google 网络状态。尚未登录是正常中间状态，不能写成安装失败。

**失败怎么办**

目标不明或权限不足时只处理该入口。若 CLI 未证实支持手机，使用厂商已有网页 SSH/远程命令或官方控制入口，不猜资源ID/参数。首次 CLI 连接可能有安全组副作用，先确认目标和变更授权；不要为读取状态自动创建角色、扩大权限或关闭其他会话。[S1]

### 第 2 步：真正完成 Google Play / GMS 安装或启用

**做什么**

优先顺序为：复用完整的内置组件 → 按官方方式启用已有组件 → 使用当前镜像支持的厂商 GMS 配置/安装入口 → 缺少明确入口时获取厂商针对本版本的安装步骤。不能仅因 FAQ 写“支持”就跳过本步骤。

在本实例内，Codex 执行已核验来源、与实际 Android/ABI 匹配的正常安装/启用及必要更新；记录修改前后组件和版本、使用的官方入口/文档及结果。已正常工作的组件不重复覆盖。需要 APK 时先确认厂商或权利人认可的获取方式、签名和版本；不使用来历不明的“一键谷歌安装器”、修改包或随机镜像站拼装 GMS。

未证实官方安装方法时，准确给出缺少的组件与需要厂商确认的一个具体问题，而不是让 User 去网上找安装包。若配置会重启、改系统分区、清应用数据或重建镜像，先说明影响和可恢复方式，经 User 确认后再执行。新付费快照、换镜像/实例、关闭安全机制、卸载已有应用均不默认授权。

**成功表现**

必要 Google 组件已安装且可用，云手机中能打开 Google Play 到正常登录入口或已登录首页，无持续服务崩溃。这里只算“组件/入口准备完成”；商店完整通过仍需第 3 步的登录与第 4 步的应用安装/确认。

**失败怎么办**

分别定位官方入口不存在、组件缺失/停用、包签名或版本冲突、系统权限/镜像不适配、服务崩溃、下载连接失败。不得无限尝试不同版本 APK。仅装 Play Store 图标或安装器返回 success 不能算通过。禁止默认执行 remount、关闭 SELinux、隐藏 Root、修改设备指纹或安装认证绕过模块来宣称成功。

### 第 3 步：User 本人登录 Google，确认商店实际可用

**做什么**

Codex 把云手机准备到原生 Google 登录页面后暂停敏感操作，并明确提示“现在请你在云手机里登录 Google”。User 自行选择适合本试点的账号，亲自输入密码、验证码、两步验证及必要授权。Google 登录与稍后的 Huuuge 登录是两个独立节点，不互相代替。

此阶段不启动采集探针，不截图/录制账号页面、不转储 UI 中的身份字段，不读取账号数据库、cookies、token、恢复码或验证码；交接只写“待本人登录/本人确认登录完成”，不写邮箱。登录阶段不依赖 AI 代操作，不要求 User 把密码或验证码发给 Codex/ChatGPT。

登录后通过云手机里的 Play 商店确认首页和搜索可用，并记录 Play Protect 认证页面实际状态（认证/未认证/无法读取），不要将有 Root、能启动商店、Widevine 等其他状态当作 Google 认证结论。认证相关报错按 Google/厂商适用说明诊断，不默认去除 Root或关闭保护来“修复”。

**成功表现**

User 完成本人登录；云手机商店可正常加载并打开应用详情。Google 登录完成、商店可用、认证状态三项分别记录，不输出账号信息。

**失败怎么办**

区分网络/DNS/TLS/时间问题、组件问题、验证码或登录验证、账号限制、设备认证问题。验证码由 User 本人在已有验证设备处理，不把云手机当作必须能收短信的手机，也不反复重试触发账号锁定。仅记录最小脱敏错误。缺少本实例具体官方操作资料时保持未验证，不编造已解决结论。

### 第 4 步：通过 Google Play 获取并确认 Huuuge

**做什么**

在云手机 Play 商店定位 [Huuuge 官方详情页](https://play.google.com/store/apps/details?id=com.huuuge.casino.slots)，核对包名和开发者，避免装到名称相近游戏。[S9] 按 User 已批准的安装目标完成正常商店下载、安装；需要 User 点击授权或商店操作时给一个明确按钮动作，不让 User 重做环境部署。不开启自动代玩、不购买礼包/付费项目。

若已经安装目标游戏，先核对包名、版本、安装来源和商店识别结果；不为证明安装强制卸载。若有正常官方更新需要，说明实际版本变更后处理；无新安装/更新发生时在回执注明“已安装复用，未新测下载”，不能捏造商店下载通过。

商店未展示游戏、显示地区不可用或设备不兼容时，分开核对 User 可见的 Play 国家/地区、设备适配和官方游戏可用性。Google Play 内容受账号的国家/地区影响；香港云资源不等于账号自动变为香港。[S8] 不自动改账号地区、绑定支付方式、伪造所在地或另建账号。第三方 APK/旧本地包不能默默替代本次明确要求的 Google Play 安装链路；另用来源必须单独提议获批，且商店步骤仍保留真实失败/未测状态。

安装后只读记录当前 game versionName/versionCode、实际游戏 ABI、安装/更新来源；固定本轮版本，若运行中发生自动升级则重新核对探针/descriptor和基线，不盲目降级到旧采集版本。

**成功表现**

正确的 Huuuge 已安装、可从云手机打开，商店能识别这份应用；本次新安装/更新或已装复用明确区分。仍不等同游戏已可玩或采集已成功。

**失败怎么办**

区分商店未登录、地区/设备不可用、一直等待下载、空间不足、系统安装错误或签名冲突。先修本项，暂停依赖游戏安装的试跑；不下载不明安装器，不清除 Google/Huuuge数据来反复试错。商店可访问但下载失败单独记录，不能一律归因于 GPU。

### 第 5 步：不接探针，建立游戏基线

**做什么**

确认前面的 Play/GMS路径已经实际准备并记录。User 在云手机网页中亲自完成 Huuuge 登录和必要资源加载，进入大厅及一个可访问 Slots 机台，确认画面与输入基本正常。此阶段不启动 Frida，记录“未插桩基线”。不做自动点击、购买、充值、Auto Spin或代填身份验证。

**成功表现**

目标游戏在云手机内能启动、登录、进入机台并响应普通操作，取得 User 明确反馈。Android 桌面、Play 首页或游戏启动图都不能代替本项。

**失败怎么办**

分别标记 Google服务依赖、游戏资源下载/网络、游戏登录、图形黑屏/闪退。按有限错误摘要诊断，不输出完整 logcat。游戏未插桩就失败时不先修改采集器、不直接升配。重装、清数据、重建镜像或重启需 User 明确确认。

### 第 6 步：连接云端执行端与唯一云手机

**做什么**

现场确认实际网络类型、连接入口、密钥绑定和授权范围。复用已有部署说明的私网/受控路线，在云端 Linux 独立用户下准备专用 ADB key、独立 server port，连接本次唯一手机。分别验证管理电脑→Linux和Linux→Android，不借助管理电脑的常驻转发冒充全云端。

绑定key、网络映射、安全组和隧道等变更先说明目标与影响，经User授权后执行。不照抄官方示例中的全网放行或全局 adb kill-server。[S4] 核对实际 Root UID、设备/游戏ABI、Android/镜像/游戏版本；官方的 Root能力说明不能代替现场实读。[S5]

**成功表现**

云端Linux连接正确的Android目标，状态为device，批准的Root检查返回UID 0，真实版本/ABI与配置相符；独立Linux执行端归属已确认。

**失败怎么办**

区分路由、认证、端口占用和目标错误。现有controller仅接受私网IPv4及设备/游戏原生ARM64；实际不符则提出最小契约适配，不能冒填地址或删校验。标准网络公网映射、额外NAT/EIP/ECS和新隧道均不自动授权。Google步骤可在已授权手机入口独立推进，不因独立Linux尚缺失而跳过Google准备。

### 第 7 步：复用采集代码并证明真实新增业务数据

**做什么**

对业务PR #2的必要准备代码定向审阅，关注目标/版本检查、进程与转发所有权、独立Session、正常停止及敏感输出。不做大规模重构。在云端独立环境复用 `scripts/cloud_capture.py`、`artifacts/live_probe/live_decode.py` 与 `agent.js`。

从已批准受控来源准备匹配当前游戏版本的纯结构 `huuuge_descriptors.pb`；Git不包含该运行时文件，不搬历史Session。主机/设备Frida版本一致；17.17.0仅为旧准备基线，不是云端兼容保证。选择实际架构，不照搬蓝叠Houdini；设备端专用目录、回环监听及PID，转发只使用本次资源。

Google和游戏身份登录完成后才开始本次采集，只观察目标游戏的已授权业务，不采集Google登录过程。按照现有controller执行：[R1]

```text
check → probe → run → status/ready
→ 根据User反馈记录play-start
→ User在网页手动进行普通Slots操作
→ 根据User反馈记录play-end
→ stop → 子进程退出 → status/回读
```

`check/probe`只证明前置检查；hook安装、本轮真实RPC和解码数据实际增长后才接受ready。`play-start/end`不模拟游戏操作。无额外Spin配额，取能说明对应关系的最小自然样本。

**成功表现**

本轮操作窗口内出现与手动操作对应的真实新增、成功解码业务响应；捕获/成功/失败数可核对，不是心跳、旧文件、合成回放。未知消息保留失败原因，不要求全协议100%解码，不从单次样本推导RTP/概率。

**失败怎么办**

缺符号、版本漂移、无业务数据、解码失败和插桩后崩溃分开记录。未插桩正常而插桩后崩溃时先停止本次探针再复查基线；不把它与商店安装或GPU问题混为一谈，不让User大量消耗筹码。不能修改请求/返回/奖励/余额，也不扩大到全局高频Hook来凑结果。重新登录时先停止相关采集，敏感身份步骤仍由User完成。

### 第 8 步：正常结束、回读与本次资源清理

**做什么**

使用原stop路径等待进程退出和flush，再读取manifest、生命周期、计数及摘要。`stop-requested`不等于保存完成；只有当前契约满足才标finalized。异常、断连、超时、缺退出码保留failed/incomplete，不手改结果。

核对所有权后只移除本次ADB forward和设备端Frida进程，不停共享ADB、Workbench全部会话、晨会或其他服务。原始数据仅留本次受控云端目录；聊天/Git仅发必要脱敏计数和状态。关闭管理终端后仍能读取已存云端结果；本轮不额外增加长期挂机/多人压力测试。

**成功表现**

Google Play/GMS准备与商店获取游戏路径有真实记录；网页游戏、真实新增解码、正常结束保存三项通过，User可查看本轮摘要。尚未发生的新下载/稳定性/其他游戏等仍明确未测。

**失败怎么办**

保留失败Session与必要受控日志，处理本次专用进程；不清空状态重新拼一次成功。实例/磁盘/带宽保留与释放由User决定，停止采集不等于停止计费，不自动删资源或Google/游戏登录数据。

## 五、Workbench和敏感步骤限制

1. 以实际安装版本help确定命令，官方Skill/帮助页对持久连接和无状态exec的描述分开对待。不得猜造云手机参数或通用转发选项。[S1][S2][S3]
2. exec默认短超时不承载整轮持续采集；使用云端已核验的稳定会话，正常结束仍由controller负责。每次独立exec所需cd/环境在同一次命令准备。[S3]
3. upload/download经OSS中转；默认仅传源码、无秘密模板及已批准结构文件，不传Google/游戏登录态、密钥、raw或完整日志。文件覆盖先检查授权，原始JSON反馈不等于已脱敏。[S1][S2]
4. 不额外启动厂商AI与原Codex双写。Google登录时暂停截图、录屏、UI转储与诊断输出；验证码和账号恢复由User本人处理。
5. 安装/启用官方Google组件是本次修订的工作，不默认为必须新增云资源。镜像重建、认证/指纹修改、系统分区修改、清数据、网络权限扩大与付费行为不自动授权；尤其不能把Play认证问题的“修复”变成未经确认地改变Root采集环境。

## 六、交付与回执

Codex必须把**实际可复现的Google/GMS安装或启用入口、组件前后状态、本人登录交接点、商店安装/更新/复用结果、对应失败处理**写回业务仓库 `deploy/cloud/README.md` 和 `ACCEPTANCE.md`，并更新原Task/Status/Handoff。不能只将此任务转述给User而不实施，也不能交付只涵盖Frida的部署说明。

适合自动化的只读检查/已确认安装步骤优先接入已有检查入口，未知Google安装命令不编写；不为本轮新造GMS平台、安装器、账户管理系统或本地发行包。现有采集代码、14项合成检查和真正现场结果分开记录。

```text
任务：TASK-0031；调试任务版本：v2-GooglePlay；业务commit：<实读>
网页桌面：已确认/待确认；Android/镜像/ABI：<实读>
Google组件：原有可用/已启用/新安装/缺失/失败；方法及版本：<实测>
Google服务连接：通过/失败/未执行；本人登录：已完成/待本人/失败
Play商店：入口/首页搜索/应用详情各自状态；Play Protect认证：<实际或未知>
Huuuge：Play新安装/Play更新/已装复用/阻塞；版本/安装来源：<实读>
本轮新下载验证：通过/失败/未执行（不能把已装复用写成新下载通过）
无探针游戏：通过/失败/未执行；云端执行端/受控连接：<实测或缺失>
新增业务采集：通过/失败/未执行；捕获/解码成功/失败：<实测或未知>
正常结束：finalized/failed/incomplete/未执行；退出后结果回读：<实测>
需User动作：<最多一个当前动作>；资源：保留/待确认；新增费用：无/已批准项
```

本次重发不分配新任务、不重置已有工作、不代表ChatGPT已安装商店或接受代码Review。原Codex纳入此v2后按既有任务治理流程继续，不用静态方案替代真实验证。Subagents: none。

## 来源与复用索引

GMS/商店公开资料于2026-09-29重新核对；Workbench相关约束沿用上一版已读官方资料，执行参数仍按本机版本核实。以下资料只支持各自功能说明，不保证User实例当前可用。阶段安排及安全边界是本任务设计。

- [S1 Workbench CLI连接与限制](https://help.aliyun.com/zh/ecs/user-guide/connect-to-an-instance-through-workbench-cli/)
- [S2 阿里云官方Workbench Skill](https://github.com/aliyun/alibabacloud-aiops-skills/blob/master/skills/developertools/solutions/alibabacloud-workbench-cli/SKILL.md)，上一版核对blob `e013125bdb156167eba9dcc4f037747bc4c1511c`。
- [S3 Workbench命令与会话](https://help.aliyun.com/zh/ecs/user-guide/use-workbench-cli-to-manage-ecs-instances)
- [S4 云手机ADB连接](https://help.aliyun.com/zh/ecp/how-to-connect-cloud-phone-via-adb)
- [S5 实例版Root说明](https://help.aliyun.com/zh/ecp/faq-how-to-get-root-permission)
- [S6 云手机官方FAQ：是否支持gms（Google Play）](https://help.aliyun.com/zh/ecp/cloud-phone-faq)，只支持“默认支持且需要服务连通”的判断，未提供当前镜像的具体安装操作。
- [S7 实例版镜像发布说明](https://help.aliyun.com/zh/ecp/release-note-of-cloud-phone-system-image)，V25.10.3 / V26.09.1；版本说明不等于现场安装与认证证明。
- [S8 Google Play国家/地区说明](https://support.google.com/googleplay/answer/7431675?hl=en)，仅用于解释内容可用性，非授权变更账号地区。
- [S9 Huuuge官方Google Play页面](https://play.google.com/store/apps/details?id=com.huuuge.casino.slots)
- [R1 既有云端部署说明](https://github.com/840832144/huuuge-android-research/blob/402e0d4a6fe33e741b5388949d5e1826252ccb35/deploy/cloud/README.md)
- [R2 当前业务准备状态](https://github.com/840832144/huuuge-android-research/blob/402e0d4a6fe33e741b5388949d5e1826252ccb35/CURRENT_STATUS.md)
- [R3 既有任务交接](https://github.com/840832144/AI-Workspace/blob/872e2dca713d1166c8aad479944a32116474f2ae/handoff/TASK-0031-HUUUGE-CLOUD.md)
