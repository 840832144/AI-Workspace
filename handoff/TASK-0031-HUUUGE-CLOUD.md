# TASK-0031 — Huuuge 单实例云端执行交接

- Updated: 2026-09-29
- Actor: Codex
- Owner: User；本人负责权限、账号登录与手动游戏操作
- Status: In Progress；Google/Play 安装及无探针游戏已取得真实证据；云端一次 ADB 验证返回 unauthorized，已断开并停止专用 server；真实采集与停止保存未执行
- Task: [TASK-0031](../tasks/TASK-0031-HUUUGE-CLOUD-SINGLE-INSTANCE.md)
- Source: [Issue #1 v3](https://github.com/840832144/huuuge-android-research/issues/1)
- Subagents: none

User 指定 [PR #11 v2-GooglePlay / 5ff7190](https://github.com/840832144/AI-Workspace/blob/5ff7190137f1512f52cddacc0f5d17ce5cc4254e/tasks/support/TASK-0031/CLOUD_DEBUG_PLAN_20260929.md)取代旧执行顺序，不再等待其他技术对接人。先 Codex 准备 Google Play/GMS，到登录页才通知 User 本人登录，再验证商店、从 Google Play 获取/确认 Huuuge，完成无探针基线后才能真实采集。

## 2026-09-29 实况与阻塞

- 原 Task/PR 保留，按 PR #11 v2-GooglePlay / `5ff7190` 续接；业务 main `6cdb1d6`、治理 main `b0a36c8` 已同步。Registry 19 canonical / 0 collision / valid，reservation pending-main；Subagents: none。
- User 已完成 official-cli OAuth，GetCallerIdentity=Account；User 明确“你先用这个调试”，继续使用已有授权身份，不再要求切换 RAM。未改 IAM。Workbench v1.0.1 与 Aliyun CLI v3.5.1 复用不重装；Workbench 未认证/连接，未用于云手机 ID。
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

## 历史准备交付与证据（2026-09-15）

- 业务 [PR #2](https://github.com/840832144/huuuge-android-research/pull/2)，代码 commit `9bb241b`。新增 Linux controller 复用现有 probe/decoder，补配置/版本/ABI/转发校验、独立目录、启停和文件回读；修复同名 Session 覆盖、损坏 wrapper 丢弃及异常停止误报。
- Linux [CI 34957001266](https://github.com/840832144/huuuge-android-research/actions/runs/34957001266) 14/14 合成检查通过，包括真实子进程锁、SIGTERM 和 supervisor 完整路径；本机 11 passed / 3 Linux-only skipped。合成计数不作为真实游戏证据。
- 业务仓库 `deploy/cloud/README.md`、`ACCEPTANCE.md`，以及 CURRENT_STATUS/COLLAB_LOG/TASKS/CHANGELOG/Handoff 已更新。Git 不包含 runtime descriptor，技术须从已核验受控结构文件准备；不搬迁历史数据。
- 三项真实验收均未执行，捕获/成功/失败计数 unknown。未连接云实例、未部署本机采集组件、未购买资源、未触碰晨会。当前未创建本轮云资源，后续资源计费/保留/释放由 User/技术确认。
- Issue v3 明确排除本地安装包，因此本轮未执行 SVN 安装包同步。Workspace Sync ON_DEMAND / provider unavailable / stale 6 / conflicts 0；Git 是本轮依据。

## 下一步与保留的验收目标

**本轮授权与结果**：User 新授权仅限既有云端 Linux 独立目录安装官方 Android Platform-Tools，使用 User 已建且已核验的公网映射做一次 connect/get-state；server 仅回环，不覆盖共享工具/已有密钥，不替换手机绑定，保留鉴权。本轮禁止 Frida/采集、重启/清数据及资源/映射/安全组/防火墙/IAM/既有服务变更；需要授权/密钥配置交 User 本人。

本轮获准的一次 ADB 验证已结束，当前阻塞是设备鉴权，不再是审批。下一步由 User 本人完成设备授权或在受控环境配置与现有绑定匹配的密钥；不在聊天/Git提供密钥，不替换手机现有绑定，不再自动连接。后续如需再验证须重新明确范围；原真实采集/解码/正常停止保存目标保留，本轮不实施。

保留原闭环：网页登录/无探针正常玩 → 云端新增数据并解码 → 正常Stop/退出/flush/保存回读。目前第一项取得User反馈和图形修复证据；后两项未执行，无Session，不能沿用历史合成结果。

实际部署/图形回滚/连接方案及验收见业务 deploy/cloud/README.md、ACCEPTANCE.md。原PR #2/#4交增量Review，未合入main，reservation pending-main。Subagents: none。
