# Huuuge 单实例云端调试方案

- Kind: execution-support；不是第二个 canonical Task，不分配新编号。
- Date: 2026-09-29
- Actor: ChatGPT
- Owner / 资源与操作人: User 本人；不等待另一位技术对接人。
- Executor: 原 Codex 会话。
- Canonical: [TASK-0031（现有任务分支）](https://github.com/840832144/AI-Workspace/blob/codex/huuuge-cloud-single-instance/tasks/TASK-0031-HUUUGE-CLOUD-SINGLE-INSTANCE.md)
- Governance: [AI-Workspace PR #4](https://github.com/840832144/AI-Workspace/pull/4)
- Implementation: [业务 PR #2](https://github.com/840832144/huuuge-android-research/pull/2)
- Scope: 已获批准的一台云端 Huuuge 游戏与被动采集闭环；本文件细化调试，不扩大为多人平台。
- Plan status: 调试方案已编写；未由 ChatGPT 连接或执行云端命令，不是代码 Accepted Review，也不是云端验收结果。

## 一、当前依据与证据边界

2026-09-29 User 提供云手机控制台截图和 Workbench CLI 官方资料，表示“已经安装上了，开始写调试方案”。截图可确认网页已展示 Android 桌面及云端终端界面；不能由桌面或 root 提示符推断 Huuuge 已安装、可玩、Root 实际权限正确或采集已完成。CLI 安装按 User 报告记录，具体版本、认证与连接仍待命令验证。截图、账号、实例 ID、主机名和会话标识不复制到本文件。

本轮通过 GitHub 直接核对：

| 来源 | 读取基线 | 支持的事实 |
| --- | --- | --- |
| AI-Workspace 最新 main | b0a36c8e1b75299814b3354530a58bbf59518714 | 治理最新主线；本调试文档基于此主线独立分支，不覆盖其他任务 |
| TASK-0031 / 专用 Handoff / PR #4 | 872e2dca713d1166c8aad479944a32116474f2ae | 现有任务仍为准备 Review，真实验证尚未登记完成；不新建任务 |
| 业务 PR #2 / CURRENT_STATUS / deploy/cloud/README.md | 402e0d4a6fe33e741b5388949d5e1826252ccb35 | 已有 Linux controller、配置校验、启停、观察窗口与结果回读；真实云端仍待验证 |
| User 本次截图及安装陈述 | 本次会话 | 云手机网页桌面可见；不是 Huuuge 可运行证明，也不是独立 Linux 执行端已具备证明 |

旧文档的“资源完全未就绪”需细化为“云手机网页可用；CLI、云端 Linux 执行端、执行端到手机连接、游戏与采集待核验”。不得把所有资源同时改成 Ready。

执行者先安全同步最新 main 与原任务分支，读 TASK-0031、Handoff、PR 评论和当前代码；保护未提交工作。PR 查询显示两条准备分支尚未合并且存在合并冲突，处理冲突时保留其他项目变更，不自动合并、强推或覆盖 Registry。本方案由原 Codex 会话纳入现有 Task/Handoff，再更新其实际执行状态；沿用现有 validator，不分配新 ID。ChatGPT 本轮未运行 Workspace Sync 或 Registry validator，不冒称校验通过。

## 二、先厘清 Workbench CLI 与云手机的关系

User 提供的官方帮助文档与官方 Skill 均以 Linux ECS 为对象。可复用它们进行云端命令执行和文件传输，但不能从云手机页面出现 Workbench 终端就推导出 CLI 可直接接受云手机实例 ID。[S1][S2]

本方案采用以下三段，三段分别验证：

```text
User 浏览器 ── 厂商网页 ── Android 云手机：Huuuge + 设备端探针

Codex 管理电脑 ── Workbench CLI / 已授权管理通道 ── 云端 Linux 采集执行端

云端 Linux 采集执行端 ── 已确认、带认证的受控连接 ── Android 云手机
```

管理电脑可以运行 Codex 和 Workbench CLI，也可发送启动/停止命令；不得在管理电脑运行生产采集器、解码器或承载必须常驻的手机数据转发，来冒充全云端。

截图中的终端可能属于 Android，也可能属于连接服务或另一台主机。先辨认对象和授权范围，只在已确认属于本次实例的环境操作；不尝试访问厂商宿主机、未知容器或其他用户资源。Android 使用 Linux 内核，单独看到 uname 输出 Linux 不能证明它是可部署现有 Python controller 的通用 Linux 执行端。

若暂无独立 Linux 执行端，先完成网页游戏基线及手机只读检查，准确报告缺少这一项；不擅自购买 ECS，不盲目在 Android 中安装 Docker/系统 Python，也不悄悄回退本地采集。后续可复用已有、获授权的云端 Linux；另购资源须由 User 单独确认。

## 三、调试顺序

每一步都先记录实际结果，再进入依赖它的下一步。不因某个管理工具不支持云手机而阻塞可独立完成的网页游戏试跑。

### 第 1 步：只读核对管理入口与运行对象

**做什么**

- 原 Codex 会话读取官方 Skill，不重复安装 User 已安装的 CLI；先执行 `workbench version`、`workbench --help`、`workbench exec --help`，记录可用版本与实际参数。
- 复用 User 在本机受控配置的凭据。不要输出 `workbench config get`、整个配置文件、环境变量全集或凭证；缺少凭据时由 User 在自己的受控终端配置，优先最小权限/短期凭据，不索要主账号 AccessKey 到聊天。
- 先确认具体目标是否为本次可管理的 Linux ECS，云手机与 ECS 标识分开保存在受控配置，不凭截图内标识猜测资源关系。只有官方接口与实测确认支持的目标才能交给 CLI。
- 在现有已授权终端内做小范围只读身份检查：Android 端检查 `id -u`、指定的 Android 版本及 ABI 属性；Linux 端检查发行版 ID、CPU 架构、Python 是否存在、可用内存和磁盘。只返回必要字段，不转储账户、全部属性、完整进程命令行或网络配置。
- `exec` 每次是独立 shell；命令使用完整路径，或把必要的 cd 与实际命令放在同一次调用。短命令检查 CLI 返回与远端退出码，结构化 JSON 不等于自动脱敏。[S3]

**成功表现**

得到三项分别标记的结果：CLI 版本/可调用状态、Android 目标身份、Linux 执行端身份。能够对已授权 Linux 执行端执行一次无敏感信息的只读命令。云手机命令入口是否可复用单独标记，不把 ECS 可连接写成手机可连接。

**失败怎么办**

参数不支持先对照本机 help；找不到资源先核对产品类型和地域；认证失败只补需要的受控权限。CLI 官方文档提示首次连接可能自动增加内网 TCP 22 安全组规则，连接前必须向 User 说明并取得对应权限变更确认，不能把首次 connect/exec 全当成无副作用读取。[S1] 不为验证 CLI 自动创建服务角色、扩大到管理员权限或关闭其他会话。

若 CLI 未证实支持云手机，使用厂商现有网页 SSH/远程命令或已批准的云手机控制接口做必要检查；不猜造 Workbench 的云手机参数或端口转发命令。官方 Skill 提到了转发，但本次读到的命令表没有给出可直接使用的通用转发参数，必须以已安装版本 help 和实际支持范围核对。[S2]

### 第 2 步：不接探针，先跑游戏基线

**做什么**

- 先检查本实例是否已装 `com.huuuge.casino.slots`；已安装就读取当前版本、ABI和状态，不先卸载或覆盖。
- 尚未安装时使用 User 批准的官方渠道准备当前可运行版本；需要使用既有受控安装文件时先确认来源、签名和 split 完整性，不使用陌生修改包或把 APK 传到公开仓库。
- User 在网页亲自登录自己的游戏账号，完成必要资源加载，进入大厅及一个可访问 Slots 机台，确认画面与输入基本正常。此阶段不启动 Frida，记录“未插桩基线”。
- 用户登录及自然游戏动作由本人完成；不做自动点击、购买、充值、Auto Spin 或代填身份验证。若用户已说安装的是游戏，仍只读确认版本，不重复安装。

**成功表现**

游戏可在云手机中启动、登录、进入机台；必要画面可显示、交互可响应，并取得 User 明确反馈。不把 Android 桌面可见当作本项通过。

**失败怎么办**

分开标记安装/ABI、资源下载/DNS/TLS、登录/服务错误、图形黑屏/闪退四类。只在受控环境采集最小相关诊断，不输出完整 logcat。游戏未接探针就失败时，先解决游戏基线；不要通过换大内存、重复换镜像或修改采集代码掩盖问题。任何重装、清应用数据、重建镜像或新增付费资源先经 User 确认。

### 第 3 步：云端采集执行端连接唯一云手机

**做什么**

- 现场确认当前实际网络类型、可用连接入口、密钥绑定和访问范围，不套用前面讨论中的假定 IP、VPC 或映射方式。
- 复用当前部署说明的私网/受控路线。只在云端 Linux 的独立用户与目录配置专用 ADB key、独立 ADB server port，并连接唯一已授权手机。
- 分开验证管理电脑→Linux 的 Workbench 通道与 Linux→手机的数据通道。前者连通不保证后者能访问手机内网。
- 绑定 key、创建新映射、安全组或隧道都属于外部配置变更，先向 User 报目标和影响。官方 ADB 文档中的全网放行、全局 adb kill-server 示例不直接照抄；本项目要求认证、范围限制和只处理本次独立 ADB。[S4]
- 读取实际 Android 版本、镜像版本、设备/游戏 ABI、Root UID，以及目标游戏版本。官方实例版说明 ADB/远程命令默认 Root，但仍以本机实读为准。[S5]

**成功表现**

从云端 Linux 连接到目标，ADB 状态为 device，授权的 Root 检查返回 UID 0，版本/ABI 与配置一致；能证明不是本地蓝叠、别的实例或厂商宿主。

**失败怎么办**

先区分无路由、认证失败、端口被占、目标错误，不盲开公网。当前 controller 只接受私网 IPv4、设备与游戏原生 ARM64，不能为通过检查把实际公网地址冒填成私网或删除安全校验。若标准网络只提供公网映射，或实际 ABI 不同，输出明确差异和最小调整方案，由 User 确认再修改配置契约/适配代码；这不是“改个参数就已支持”。额外 NAT/EIP/ECS 与新隧道不在本次自动授权中。

### 第 4 步：复用准备代码，建立最小探针与解码链路

**做什么**

- 对业务 PR #2 与当前差异做定向审阅：真实目标/版本校验、只操作本次进程与转发、独立 Session、正常停止与异常状态、敏感输出。该审阅服务于本次云端调试，不扩展为大规模重构。
- 在云端执行端使用独立虚拟环境和受控配置；复用 `scripts/cloud_capture.py`、`artifacts/live_probe/live_decode.py` 和 `agent.js`，不重写 Collector。
- 准备匹配游戏版本的纯结构 `huuuge_descriptors.pb`。现有 Git 不包含此 runtime 文件；从已批准受控来源取得并核对，不能搬整个旧 Session。缺失则先报告，不用历史解码结果替代。
- 当前 Frida 17.17.0 是已有代码基线，主机端与Android设备端版本须一致；CPU架构按实测选择。不照搬蓝叠 Houdini bootstrap，不在原生ARM64环境加载错误架构组件。
- 设备端探针进程使用专用目录、回环监听和本次PID；云端只创建自己拥有的转发。启动前核对路径与端口，退出只清理本轮资源。
- 执行现有 `check → probe`，明确二者只代表配置/权限/身份检查。随后在云端稳定会话内启动 `run`；新增 hooks、真实新增RPC及解码文件增长后才接受 ready。[R1]

**成功表现**

既有准备代码在真实云环境通过前置核验，并建立本次独立 Session；捕获与解码实际新增，探针状态和数据来源一致。

**失败怎么办**

“游戏未插桩正常、插桩后崩溃”单列为插桩兼容；停止本次探针后复查基线，不混成网络或GPU问题。缺符号、版本漂移、无数据、解码失败分别定位。不得改请求、返回、奖励、余额或扩大到全局高频Hook来凑结果；需要改变现有被动观测范围时先交范围评审。

### 第 5 步：User 手动操作，证明真实新增业务采集

**做什么**

按已有 controller 命令执行，命令在云端已确认的仓库路径和配置下运行：

```text
check → probe → run
                ↓
              status / ready
                ↓
             play-start
                ↓
       User 在网页进行普通 Slots 操作
                ↓
             play-end
                ↓
               stop
                ↓
              status
```

`play-start` / `play-end` 由 Codex 根据 User 明确反馈记录，不模拟User行为。没有额外Spin配额；以足够证明本次操作与业务响应相符的最小自然样本为准。[R1]

**成功表现**

操作窗口中有对应的本次新增且成功解码的业务样本，捕获总数、成功数、失败数及来源可核对。结构能与目标 Slots 操作对应，不是仅有心跳、旧文件或合成回放。存在未知消息时保留失败原因，不要求全协议100%解码，也不从单次样本推导概率、RTP或数值结论。

**失败怎么办**

收到 ready 但只有背景消息时继续定位目标Hook/请求对应关系；不直接宣布成功，也不让User持续大量消耗筹码。配置或网络变化后必须重新确认目标与本轮Session边界，不混用旧证据。

### 第 6 步：正常结束、回读结果与释放本次进程

**做什么**

- 使用现有 stop 路径等待采集子进程退出并flush，再从磁盘读取manifest、计数、生命周期和摘要。
- `stop-requested` 只代表发出停止请求；只有文件和进程均满足当前契约才记 finalized。断连、超时、退出码缺失或异常结束记录 failed/incomplete，不手改为成功。
- 移除本次ADB转发，核对PID与可执行路径后停止本次设备端Frida；不停止共享ADB、晨会服务、其他进程或Workbench全部会话。
- 原始数据仅留本次受控云目录，聊天/Git只给脱敏计数、状态和必要定位结论。User需要查看原始结果时走受控访问。
- 关闭管理终端后结果仍可从云端读取即可；本轮不新增长期稳定性或断网恢复验收。实例、磁盘、带宽是否保留由User决定，停止采集不自动等于停止云账单。

**成功表现**

本轮真实游戏可用、真实新增解码、正常结束保存三项全部通过，且User可查看脱敏摘要。其余能力仍标未验证。

**失败怎么办**

保留失败Session和必要受控日志，只处理当前专用进程。禁止清空状态重新伪造一次成功，不自动删除资源或结果。

## 四、Workbench 使用的额外限制

1. 官方 Skill 与帮助页在交互会话描述上有差异：Skill 将exec描述为无状态，帮助页另列持久connect。以已安装版本help和实际行为为准，不误认为所有CLI调用都持久或都无状态。[S2][S3]
2. `workbench exec` 默认有30秒超时，适合短预检与状态命令；不要直接用一次短exec承载整轮前台采集并让其被超时终止。复用云端已有tmux等受控持久会话，或经验证的connect/detach；采集停止必须仍由原controller控制，不默认关闭终端会自动finalize。[S3]
3. `upload/download` 经OSS中转；默认只传源码、无秘密模板和经批准的纯结构文件。密钥、账号登录态、raw采集、完整日志不通过便利命令隐式中转到未经确认的数据位置。目标已存在先检查，必要覆盖须明确授权。[S1][S2]
4. 不启用第二个Workbench内置AI会话与Codex同时写同一环境；继续由原Codex作为唯一执行者。Agent工具反馈也可能含原始结果，远端命令须预先限缩输出，不依赖事后删除聊天。
5. 安装成功、认证成功、SSH成功、ADB成功、Root成功、游戏成功和采集成功分别记录；前一项不能代替后一项。

## 五、权限与User只需参与的节点

User已经批准本项目单实例验证，且已自行准备云手机；本方案不代表Agent获准继续购买资源。Codex先做受控只读检查，待目标、访问权限及准备代码核验清楚，再按已批准范围部署专用组件。

需要User本人参与：凭据/权限的安全配置与确认；游戏账号登录；收到ready后进行自然游戏操作并反馈开始结束；决定新增费用、变更网络策略、重启/重建/卸载及最终资源保留。日常策划仍只用浏览器，不要求本地部署采集工具链。

## 六、回执模板

仅填实际结果，未做填“未执行”，未知填“未知”，失败给最小原因；不得猜数值。

```text
任务：TASK-0031；业务commit：<实读>
网页桌面：已确认/待确认
CLI版本与目标类型：<版本；Linux ECS/Android/未知；不含真实ID>
Linux执行端：已确认/缺失；手机受控通道：已确认/阻塞
Android/镜像/设备ABI/游戏ABI/游戏版本：<实读>
未插桩游戏基线：通过/失败/未执行
新增真实业务采集：通过/失败/未执行；捕获/解码成功/失败：<实测或未知>
正常结束：finalized/failed/incomplete/未执行；进程退出与结果回读：<实测>
需User动作：<最多一个当前阻塞动作>
资源：本次保留/待确认；未新增费用项或已明确批准项
```

完整运行证据和真实位置留受控系统；业务部署细节与实测记录更新业务仓库，Task/Status/Handoff同步AI-Workspace。本文是本任务内的调试细化，不产生新Product Roadmap方向、不创建Future Task、不把准备Review写成Accepted。

## 来源与复用索引

来源核对日为2026-09-29。S项为官方资料支持的工具行为，R项为已读项目实现说明；本方案的阶段安排、成功/失败处理与范围约束为本次设计，不冒称厂商保证Huuuge兼容。

- [S1 Workbench CLI连接与限制](https://help.aliyun.com/zh/ecs/user-guide/connect-to-an-instance-through-workbench-cli/)
- [S2 阿里云官方Workbench Skill](https://github.com/aliyun/alibabacloud-aiops-skills/blob/master/skills/developertools/solutions/alibabacloud-workbench-cli/SKILL.md)，本次读取blob `e013125bdb156167eba9dcc4f037747bc4c1511c`；[User提供的Skill门户](https://skills.aliyun.com/skills/alibabacloud-workbench-cli)本次未返回可解析正文，以官方Git正文为依据。
- [S3 Workbench命令、超时与会话行为](https://help.aliyun.com/zh/ecs/user-guide/use-workbench-cli-to-manage-ecs-instances)
- [S4 云手机ADB连接与密钥](https://help.aliyun.com/zh/ecp/how-to-connect-cloud-phone-via-adb)，不是当前标准网络一定可连接的证明，也不是授权使用其全网开放示例。
- [S5 实例版Root说明](https://help.aliyun.com/zh/ecp/faq-how-to-get-root-permission)，仍须现场核验。
- [R1 既有云端部署说明](https://github.com/840832144/huuuge-android-research/blob/402e0d4a6fe33e741b5388949d5e1826252ccb35/deploy/cloud/README.md)
- [R2 当前业务状态](https://github.com/840832144/huuuge-android-research/blob/402e0d4a6fe33e741b5388949d5e1826252ccb35/CURRENT_STATUS.md)
- [R3 既有任务交接](https://github.com/840832144/AI-Workspace/blob/872e2dca713d1166c8aad479944a32116474f2ae/handoff/TASK-0031-HUUUGE-CLOUD.md)
