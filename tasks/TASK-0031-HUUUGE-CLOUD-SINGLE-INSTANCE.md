# TASK-0031 — Huuuge 单实例云端游戏与采集闭环

- Status: In Progress
- Project key: HUUUGE
- Owner: User
- Executor: Codex
- Priority: P1 / bounded pilot
- Date: 2026-09-15
- Updated: 2026-09-29
- User decision: Approved；按 PR #11 v2-GooglePlay 续接，由 Codex 准备谷歌环境，User 本人负责权限、身份登录和手动游戏操作
- Allocation relationship: new
- Related tasks: TASK-0027
- Subagents: none

## Goal

按 [采集器 Issue #1 v3](https://github.com/840832144/huuuge-android-research/issues/1) 跑通一台云端 Huuuge 环境：策划仅用厂商网页，游戏与采集/解码均在云端，真实新增数据可保存且正常结束。2026-09-15 的“资源未就绪，先准备”是历史状态；2026-09-29 按 [PR #11 v2 方案](https://github.com/840832144/AI-Workspace/blob/5ff7190137f1512f52cddacc0f5d17ce5cc4254e/tasks/support/TASK-0031/CLOUD_DEBUG_PLAN_20260929.md)及[对应交接](https://github.com/840832144/AI-Workspace/blob/5ff7190137f1512f52cddacc0f5d17ce5cc4254e/handoff/HUUUGE-CLOUD-DEBUG-20260929.md)续接，不新建 Task/PR，不接受准备代码作为真实验收。

## 2026-09-29 续接实况

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

## 验收

| 项目 | 必须证据 | 当前结果 |
| --- | --- | --- |
| Google Play/GMS 前置 | 组件前后状态、官方方法、User 登录、商店可用与认证状态 | 三核心包已启用并回读；User已登录；Play新安装已回读；认证无法读取/未确认 |
| 网页游戏 | Google Play 获取/确认 Huuuge 后，User 无探针正常交互 | User可玩；应用ANGLE修复后User“现在好了”，长期稳定性未测 |
| 真实采集解码 | 本轮新增、关联普通手动操作的成功业务解码样本 | 未执行；计数 unknown |
| 正常结束保存 | Stop/flush、进程退出、结果仍可读、捕获/成功/失败数可核对 | 未执行；没有云端 Session |

静态和合成检查单列，仅支持准备工作 Review。云端闭环未通过时不标 Complete/Accepted。

## 交付与下一步

原业务 [PR #2](https://github.com/840832144/huuuge-android-research/pull/2) / 治理 [PR #4](https://github.com/840832144/AI-Workspace/pull/4) 交本轮增量 Review，任务 In Progress，不是 Complete/Accepted。已有代码 `9bb241b` 和 Linux CI 14/14 仅为历史合成准备证据，本轮没有采集代码改动。

**前次单次ADB验证授权**：User 当时授权仅限既有云端 Linux 独立目录安装官方 Android Platform-Tools，使用 User 已建且已核验的公网映射做一次 connect/get-state；server 仅回环，不覆盖共享工具/已有密钥，不替换手机绑定，保留鉴权。本轮禁止 Frida/采集、重启/清数据及资源/映射/安全组/防火墙/IAM/既有服务变更；需要授权/密钥配置交 User 本人。

User委托Codex接手本地管理与云端密钥配置。Workbench经本机CredentialsCmd适配复用原OAuth临时STS，唯一Linux目标只读查询通过；未创建Workbench SSH会话。实际远程执行继续用ECS Cloud Assistant，OpenSSL CMS加密后只下发密文，云端公钥比较一致，匹配私钥已放入独立目录，0700/0600。

User随后明确允许新的一次ADB复验。正常工具审批通过，本次connect实际1次成功，get-state=device/exit0；disconnect与专用server停止均exit0。独立回读保存结果、记录PID不存在/专用监听0；一次性传输材料已清理，原任务key保留、默认root key不存在，手机绑定/安全组规则未变，nginx/sshd仍active。无Frida/采集。

本次连接验证已完成，无需User再找主机、上传密钥或重新绑定。下一阶段明确持续连接与Frida/真实采集范围后继续原验收目标；当前保持停止，真实新增解码、采集正常结束和保存结果回读仍未执行。

无云端Session/真实解码计数。持续采集、正常stop/退出及保存结果回读仍待完成。reservation保持pending-main，Review后canonical合入共享main再finalize。浏览器自动化保持停止，官方API可继续使用；不恢复本机采集或SVN安装包。
