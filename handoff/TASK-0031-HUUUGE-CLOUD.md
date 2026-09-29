# TASK-0031 — Huuuge 单实例云端执行交接

- Updated: 2026-09-29
- Actor: Codex
- Owner: User；本人负责权限、账号登录与手动游戏操作
- Status: In Progress；网页 Android 桌面已确认，只读命令结果 unknown；API 凭据/管理接入点待就绪
- Task: [TASK-0031](../tasks/TASK-0031-HUUUGE-CLOUD-SINGLE-INSTANCE.md)
- Source: [Issue #1 v3](https://github.com/840832144/huuuge-android-research/issues/1)
- Subagents: none

User 指定 [PR #11 v2-GooglePlay / 5ff7190](https://github.com/840832144/AI-Workspace/blob/5ff7190137f1512f52cddacc0f5d17ce5cc4254e/tasks/support/TASK-0031/CLOUD_DEBUG_PLAN_20260929.md)取代旧执行顺序，不再等待其他技术对接人。先 Codex 准备 Google Play/GMS，到登录页才通知 User 本人登录，再验证商店、从 Google Play 获取/确认 Huuuge，完成无探针基线后才能真实采集。

## 2026-09-29 实况与阻塞

- 原治理分支安全合入 main `b0a36c8`；保留双方 Changelog，Registry 从 canonical 重建后 19 canonical / 0 collision / valid。Workspace Sync 实测 ON_DEMAND / provider unavailable / stale 6 / conflicts 0。原 PR #4 / 业务 PR #2 保留，未合并共享 main，reservation 保持 pending-main。
- User 更正 Workbench CLI 需要 Codex 安装。已安装阿里云官方 Windows amd64 包 v1.0.1（`86c0aff`），官方 SHA-256 校验通过，version/exec/配置/列表帮助已核验。安装路径与方法见业务部署说明；不把治理仓库变成运行时配置入口。
- 默认 Workbench 配置文件尚不存在；未读取凭据、连接 ECS 或更改安全组。CLI 面向 Linux ECS，不能据此认为云手机已有受控通道；两个目标均须分别核验。
- 最新一次支持流程恢复成功读回同一官方 instanceLayouts URL、原连接窗口及 Android 桌面，证明此前连接已生效；没有重放连接点击。唯一已购实例可用、香港/4c8g32G/Android 12/26.09.1。未读取密码/验证码或 Cookie。
- 控制台远程命令选择唯一实例，填入固定只读脚本并全文核对，只点击一次执行。输出为空，关闭表单时再次报 `js execution timed out; kernel reset, rerun your request`；浏览器自动化停止。命令任务/结果 unknown，先查任务，不重放执行。Google 组件/网络/ABI 尚无真实输出，未安装/启用/清数据/重建，未到 Google 登录页。
- 按 User 授权准备官方 eds-aic RunCommand/DescribeTasks 路径，Aliyun CLI v3.5.1 官方发布包校验并安装管理 Host 用户目录；版本、帮助、脚本 bash -n 和虚构目标离线参数预演通过，没有 API 调用。未发现 API 默认配置/标准凭据环境变量；官方接入点和 CLI 仅列上海/新加坡，香港地域预演报 unknown endpoint，实际目标管理接入点及 AgentType 待核实。Workbench 保留原安装，不对云手机 ID 使用，不新增 ECS/NAT/公网 ADB。
- 本轮业务交付 `60d74e1` 已推送原 PR #2：固定只读检查、官方管理步骤、部署/验收及协作记录；本轮未修改现有采集器。治理原 PR #4 继续交准备增量 Review。
- 已定向阅读业务 `402e0d4` controller → decoder → stop/结果回读调用链；不改写现有采集器，不启动探针。历史 Linux 14/14 合成 CI 仍仅是准备证据。
- 安装时 checksum HTTP 响应为字节数组，首次解析未找到条目便停止；正确 UTF-8 解码后校验成功，未跳过校验。官方脚本注释与实际目录不一致，因此使用同源发布包校验后安装用户目录。
- 合并未完成时 Registry 写入被 latest-main gate 拒绝；本地完成 main 合入、重建后验证通过才继续登记，没有发布冲突文件。
- 本轮无云端 Session，捕获/成功/失败计数 unknown；未创建付费资源、开公网调试端口、启动本机采集或修改晨会。Google 安装仍由 Codex 完成，未转交 User 自行找包。

## 历史准备交付与证据（2026-09-15）

- 业务 [PR #2](https://github.com/840832144/huuuge-android-research/pull/2)，代码 commit `9bb241b`。新增 Linux controller 复用现有 probe/decoder，补配置/版本/ABI/转发校验、独立目录、启停和文件回读；修复同名 Session 覆盖、损坏 wrapper 丢弃及异常停止误报。
- Linux [CI 34957001266](https://github.com/840832144/huuuge-android-research/actions/runs/34957001266) 14/14 合成检查通过，包括真实子进程锁、SIGTERM 和 supervisor 完整路径；本机 11 passed / 3 Linux-only skipped。合成计数不作为真实游戏证据。
- 业务仓库 `deploy/cloud/README.md`、`ACCEPTANCE.md`，以及 CURRENT_STATUS/COLLAB_LOG/TASKS/CHANGELOG/Handoff 已更新。Git 不包含 runtime descriptor，技术须从已核验受控结构文件准备；不搬迁历史数据。
- 三项真实验收均未执行，捕获/成功/失败计数 unknown。未连接云实例、未部署本机采集组件、未购买资源、未触碰晨会。当前未创建本轮云资源，后续资源计费/保留/释放由 User/技术确认。
- Issue v3 明确排除本地安装包，因此本轮未执行 SVN 安装包同步。Workspace Sync ON_DEMAND / provider unavailable / stale 6 / conflicts 0；Git 是本轮依据。

## 下一步与保留的验收目标

User 在本机完成已获准的 STS profile 配置，具体单步入口见业务[只读管理说明](https://github.com/840832144/huuuge-android-research/blob/codex/huuuge-cloud-single-instance/deploy/cloud/GOOGLE_READONLY.md)，不在聊天提供密钥或扩大管理员权限。Codex 核实香港目标对应官方管理接入点后，先用 DescribeTasks 定向查回控制台命令；没有查清前不重发 RunCommand。当前浏览器自动化停止，不能把等待恢复作为唯一后续动作。

取得 Google 组件/Android/必要网络实况后，Codex 按厂商适用方法安装/启用 Google；到原生登录页通知 User 本人登录。Workbench/Linux 状态不作为手机准备前置阻塞。继续商店可用与 Huuuge 来源核验、User 无探针游戏、云端新增采集与解码、正常 Stop → 退出 → 保存结果回读。原 PR #2/#4 交准备增量 Review，任务保持 In Progress，不能把网页桌面或离线预演记为完整验收。

治理分支尚未合入 main；reservation 保持 pending-main，Review/合入后再 finalize。无额外 Agent，Subagents: none。
