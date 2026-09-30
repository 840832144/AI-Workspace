# TASK-0031 — Huuuge 单实例云端游戏与采集闭环

## 2026-09-30 — TASK-0031 真实云端闭环完成，交 Review

- 本轮一台既有云手机、一个新批次；真实捕获 **312**、解码成功 **312**、失败 **0**。User 手动窗口内回读 **8 条 SlotsGameServer.Spin 响应**，业务字段非空；User 确认“操作完成，游戏正常”。
- 采集时间 2026-09-30 10:59:50.285—11:03:22.133（UTC+8）；play-end/stop/子进程均 exit0，`finalized` / `ready-for-human-review`。清理后独立回读 index、Raw、JSON、manifest 与计数一致，无 active Session。
- 实际运行源码 `03fb399201d08c878c74322347b652bc8e8a2414`；既有 Python3.11.13 独立 venv、Frida17.17.0、protobuf7.36.2、lz4 4.4.5，当前 APK 静态提取40-file descriptor。云端 Linux **24/24 合成检查**与上述真实采集分开记录。
- 原 controller 最小适配显式公网 ADB + Frida TLS、准确包名/PID、当前 descriptor 预检与一次受限启动重试，目标/版本/ABI/Root/forward 校验保留。真实 TLS1.3、固定手机证书、错误证书/令牌拒绝及正确令牌鉴权通过。传统公网 ADB 本身仍未加密；业务数据由 Frida TLS 保护。
- 首次 decoder 在创建 Session/挂接前因内置 descriptor 版本冲突退出；修复后只对同一已分配批次重试一次，保留原失败状态、日志及启动摘要。没有第二个采集批次，没有用旧结构替代当前结构。
- 本次 Frida、采集进程、专用 ADB server 已退出，精确 forward 已移除，专用监听为0；临时 TLS 私钥/令牌已清理。原匹配 ADB key 保留；手机 RUNNING、绑定/公网映射及4条安全组入站规则未变，nginx/sshd active，系统 Python3.6.8 未替换。没有新增资源/费用、网络/IAM变更或晨会修改。
- Google 三个内置包已按 Android 官方 pm enable 方法启用，User 登录并从 Play 安装 Huuuge；原无探针图形修复和可玩反馈保留。本轮 Huuuge12.09.27229/1789041595、Android12/ARM64；Play Protect 认证仍未确认，长期稳定性未测。
- 当前无执行阻塞；等待原业务 PR #2 / 治理 PR #4 Review，不标 Complete/Accepted。真实数据、配置、地址与密钥只留受控环境；本机不持续采集。Subagents: none。

- Status: Review
- Project key: HUUUGE
- Owner: User
- Executor: Codex
- Priority: P1 / bounded pilot
- Date: 2026-09-15
- Updated: 2026-09-30
- User decision: Approved；按 PR #11 v2-GooglePlay 续接，由 Codex 准备谷歌环境，User 本人负责权限、身份登录和手动游戏操作
- Allocation relationship: new
- Related tasks: TASK-0027
- Subagents: none

## Goal

按 [采集器 Issue #1 v3](https://github.com/840832144/huuuge-android-research/issues/1) 跑通一台云端 Huuuge 环境：策划仅用厂商网页，游戏与采集/解码均在云端，真实新增数据可保存且正常结束。2026-09-15 的“资源未就绪，先准备”是历史状态；2026-09-29 按 [PR #11 v2 方案](https://github.com/840832144/AI-Workspace/blob/5ff7190137f1512f52cddacc0f5d17ce5cc4254e/tasks/support/TASK-0031/CLOUD_DEBUG_PLAN_20260929.md)及[对应交接](https://github.com/840832144/AI-Workspace/blob/5ff7190137f1512f52cddacc0f5d17ce5cc4254e/handoff/HUUUGE-CLOUD-DEBUG-20260929.md)续接，不新建 Task/PR，不接受准备代码作为真实验收。

## 2026-09-29 历史续接实况

- 原 Task/PR 保留，按 PR #11 v2-GooglePlay / `5ff7190` 续接；业务 main `6cdb1d6`、治理 main `b0a36c8` 已同步。Registry 19 canonical / 0 collision / valid，reservation pending-main；Subagents: none。
- User 已完成 official-cli OAuth，GetCallerIdentity=Account；User 明确“你先用这个调试”，继续使用已有授权身份，不再要求切换 RAM。未改 IAM。Workbench v1.0.1 与 Aliyun CLI v3.5.1 复用不重装；Workbench 已通过 CredentialsCmd 复用现有 OAuth 临时凭据并查询匹配Linux；未创建SSH会话，未用于云手机ID。
- 云手机实际管理通道为官方 eds-aic/2023-09-30 上海接入点 + 香港 BizRegionId，经精确唯一实例校验；EdsAgent RunCommand → DescribeTasks 已真实通过。浏览器先前恢复已核验官方 URL/原连接窗口；后续超时仍停止自动化，旧控制台命令 unknown，不重放点击。
- Android 12 / SDK31 / arm64-v8a / 镜像26.09.1。Play/GMS/GSF 原存在但禁用；以 Android 官方 `pm enable --user 0` 启用三个内置包，均 exit0 且回读 enabled=yes/disabled=no。两个 Google 官方域名 HEAD=302/exit0。未侧载、清数据、重建或修改认证。
- Play 启动成功后 User 亲自 Google 登录。Huuuge 首次未安装，User 经官方详情完成新安装并反馈“打开”；包管理器回读 installer=com.android.vending、12.09.27229 / 1789041595、arm64-v8a。商店详情与下载安装可用；首页/搜索未单独验证。Play Protect 认证记录“无法读取/未确认”（User 暂未找到该项），不宣称已认证，也不反复要求查找。
- User 无探针游戏反馈“能玩，画面有点问题”，截图存在错位/缺字。实读 CPU 渲染、GLES SwiftShader、内置 com.android.angle，两项应用 ANGLE 设置原为 null。仅为 Huuuge 设置 angle 后重启该应用；通用 launcher intent 报无法解析，查真实 launcher 后以 com.huuuge.casino.BootActivity 启动，Status=ok。限定该进程日志确认 ANGLE/Vulkan SwiftShader 生效；User 随后确认“现在好了”。本轮无探针网页可玩/图形恢复有真实证据，长期稳定性未测。
- 按 User 要求自行核实到已有香港 Linux ECS；官方 ECS Cloud Assistant 状态正常，并用 ECS RunCommand → DescribeInvocationResults 实读 Alibaba Cloud Linux3、x86_64、2CPU/约7.4GiB内存、根盘约31GiB可用、Python3.6.8。PATH 未找到 adb/git，任务目录不存在；nginx 在运行，未修改/重启既有服务。没有新增 ECS/NAT/EIP。
- 原私网 phone:5555 从该 Linux 单次 TCP 检查超时；未证实同 VPC，默认/任务路径 ADB key 均未发现，手机现有 keypair 绑定已记录但未替换。手机未发现 ssh/ssh-keygen 命令，因此反向 SSH 仅为未实施备选，不宣称已具备通道。
- User 随后提供控制台新建公网 ADB 映射及 connect 命令。官方 ListInstanceAdbAttributes 返回唯一匹配手机，外部10001→内部5555；从已有 Linux 单次 TCP 连接成功。该映射由 User 建立，Codex 未创建映射、改安全组或导出 Cookie；真实 IP/实例标识不入 Git。
- 前次自动审批拒绝（blocked by policy）属于历史；User 明确收窄授权后，本次正常默认审批已放行，没有关闭审批或换工具绕过。User 新授权仅限既有云端 Linux 独立目录安装官方 Android Platform-Tools，使用 User 已建且已核验的公网映射做一次 connect/get-state；server 仅回环，不覆盖共享工具/已有密钥，不替换手机绑定，保留鉴权。本轮禁止 Frida/采集、重启/清数据及资源/映射/安全组/防火墙/IAM/既有服务变更；需要授权/密钥配置交 User 本人。
- 正常工具默认审批本次已放行，经 ECS Cloud Assistant 在任务独立目录安装官方 Platform-Tools；实读 ADB1.0.41 / 37.0.1-15733141。首次 server 因监听参数写法报错退出、未执行 connect；改为官方 localhost 语法后实核仅回环监听。connect 实际调用一次，输出 failed to authenticate；get-state exit1 / device unauthorized。connect 自身 exit0 不能记为成功。
- 已对唯一目标 disconnect(exit0)，仅停止自己启动的专用 server(exit0)，进程正常退出。另起只读任务回读云端 result-connect.json：connect_attempts=1、记录的进程不存在、专用监听数0；任务目录0700、任务新生 ADB key0600、默认 root key仍不存在。官方手机 API 回读原 keypair 绑定未变、手机RUNNING；nginx/sshd保持active。未读取/输出密钥内容。
- 原 controller 仅允许私网/loopback transport，校验保持不变，不用代理伪装公网地址。User 本轮授权仅限既有入口的一次连接验证，不包含持续采集；如后续采用公网采集，仍需独立明确范围并最小适配/Review。无 Frida、采集 Session 或新增解码计数，正常停止/保存回读仍未执行。

**前次单次ADB验证授权**：User 当时授权仅限既有云端 Linux 独立目录安装官方 Android Platform-Tools，使用 User 已建且已核验的公网映射做一次 connect/get-state；server 仅回环，不覆盖共享工具/已有密钥，不替换手机绑定，保留鉴权。本轮禁止 Frida/采集、重启/清数据及资源/映射/安全组/防火墙/IAM/既有服务变更；需要授权/密钥配置交 User 本人。

User委托Codex接手本地管理与云端密钥配置。Workbench经本机CredentialsCmd适配复用原OAuth临时STS，唯一Linux目标只读查询通过；未创建Workbench SSH会话。实际远程执行继续用ECS Cloud Assistant，OpenSSL CMS加密后只下发密文，云端公钥比较一致，匹配私钥已放入独立目录，0700/0600。

User随后明确允许新的一次ADB复验。正常工具审批通过，本次connect实际1次成功，get-state=device/exit0；disconnect与专用server停止均exit0。独立回读保存结果、记录PID不存在/专用监听0；一次性传输材料已清理，原任务key保留、默认root key不存在，手机绑定/安全组规则未变，nginx/sshd仍active。无Frida/采集。

本次连接验证已完成，无需User再找主机、上传密钥或重新绑定。下一阶段明确持续连接与Frida/真实采集范围后继续原验收目标；当前保持停止，真实新增解码、采集正常结束和保存结果回读仍未执行。

实际方法、回滚和分项结果见业务 [部署说明](https://github.com/840832144/huuuge-android-research/blob/codex/huuuge-cloud-single-instance/deploy/cloud/README.md) / [验收记录](https://github.com/840832144/huuuge-android-research/blob/codex/huuuge-cloud-single-instance/deploy/cloud/ACCEPTANCE.md)。

## 初始登记与能力契约（2026-09-15；续接状态见上节）

- 同步 AI-Workspace `5b5414c`、业务仓库 `759669b`；两处 main 工作树原本干净，使用独立 linked worktree 和 `codex/huuuge-cloud-single-instance` 分支。
- 完整 Registry scan/validate：14 canonical、0 collision、status=valid；远端预留 TASK-0027/0028/0030，allocator remote-CAS 实际返回 TASK-0031，reservation 保持 pending-main。
- 无同目标云端 Task/Candidate；TASK-0027 是笔记本可靠性任务，本任务不续写、不恢复其本地部署范围；晨会 TASK-0028 与其他研究任务所有权不变。
- 项目能力来源：Huuuge `docs/collector/CURRENT_CAPABILITIES.md` 的被动 RpcMessage 采集、descriptor 解码、READY、Stop/Flush 和 Session 保存。公共 Capability Catalog 已核对，不新增共享平台能力或工具目录。
- 输入：User 本人确认权限的一台无影云手机及独立核验的云端 Linux 执行端、当前版本/ABI、匹配探针/descriptor、独立结果目录。
- 操作：业务仓库 WRITE（必要适配与测试）；云端运行仅在资源授权就绪后执行。User 负责权限确认；不购买资源、不开放公网调试端口，不自动接受 Workbench 首次连接可能产生的安全组变更。
- 输出：必要云端启停/检查适配、脱敏模板、短中文部署说明、三项验收记录与受控结果交接。
- Workspace Sync：ON_DEMAND、provider unavailable、stale 6、conflicts 0；使用 Git 最新证据，未开启 WATCH。PowerShell 入口受执行策略阻止后，直接运行其原有 Python CLI，未更改执行策略。

## 实施与边界

复用现有 Collector、agent.js、解码器和停止控制文件；仅补 Linux 运行和本轮 Session 验收所必需的适配。云手机 Android/ABI、Root/Frida 权限和 Huuuge 版本由现场验证，不照搬蓝叠/Houdini。现成网页客户端由 User 登录并操作；Agent 不代玩、不自动点击、不修改请求、奖励、余额或服务端。

不做多人、克隆、统一工作台、报告平台、本地安装包、历史数据搬迁或其他游戏；不修改晨会服务和共享主机全局环境。原始数据、标识和日志仅留受控云端；Git 只收代码、模板、计数和状态。

## 验收与交付

| 项目 | 当前结果 |
| --- | --- |
| Google/无探针网页基线 | 原Google内置组件启用、User登录、Play安装与ANGLE修复证据保留；认证未确认 |
| 网页正常玩 | 本轮User大厅待命，READY后普通Slots，确认游戏正常 |
| 新增采集解码 | 312捕获/312成功/0失败，手动窗口8条Slots响应 |
| 正常停止与保存回读 | play-end/stop/子进程exit0，finalized；清理后独立文件回读一致 |
| 清理与隔离 | 本次进程/forward/监听和临时秘密已清理；原绑定/映射/SG及既有服务保持 |

详细[部署说明](https://github.com/840832144/huuuge-android-research/blob/codex/huuuge-cloud-single-instance/deploy/cloud/TLS_TRANSPORT.md)、[真实验收记录](https://github.com/840832144/huuuge-android-research/blob/codex/huuuge-cloud-single-instance/deploy/cloud/ACCEPTANCE.md)与脱敏结果位于原业务仓库；原始数据/配置/地址/密钥不进公共治理仓库。

原业务[PR #2](https://github.com/840832144/huuuge-android-research/pull/2) / 治理[PR #4](https://github.com/840832144/AI-Workspace/pull/4)交Review；本轮执行目标已得到真实证据，正式Review未完成，不标Complete/Accepted。reservation保持pending-main，canonical合入共享main后再finalize。无新增Task；Subagents: none。
