# TASK-0031 — Huuuge 单实例云端执行交接

- Updated: 2026-09-30
- Actor: Codex
- Owner: User；本人负责权限、账号登录与手动游戏操作
- Status: Review
- Task: [TASK-0031](../tasks/TASK-0031-HUUUGE-CLOUD-SINGLE-INSTANCE.md)
- Source: [Issue #1 v3](https://github.com/840832144/huuuge-android-research/issues/1)；[PR #11 v2-GooglePlay / 5ff7190](https://github.com/840832144/AI-Workspace/blob/5ff7190137f1512f52cddacc0f5d17ce5cc4254e/tasks/support/TASK-0031/CLOUD_DEBUG_PLAN_20260929.md)
- Subagents: none

## 2026-09-30 — TASK-0031 真实云端闭环完成，交 Review

- 本轮一台既有云手机、一个新批次；真实捕获 **312**、解码成功 **312**、失败 **0**。User 手动窗口内回读 **8 条 SlotsGameServer.Spin 响应**，业务字段非空；User 确认“操作完成，游戏正常”。
- 采集时间 2026-09-30 10:59:50.285—11:03:22.133（UTC+8）；play-end/stop/子进程均 exit0，`finalized` / `ready-for-human-review`。清理后独立回读 index、Raw、JSON、manifest 与计数一致，无 active Session。
- 实际运行源码 `03fb399201d08c878c74322347b652bc8e8a2414`；既有 Python3.11.13 独立 venv、Frida17.17.0、protobuf7.36.2、lz4 4.4.5，当前 APK 静态提取40-file descriptor。云端 Linux **24/24 合成检查**与上述真实采集分开记录。
- 原 controller 最小适配显式公网 ADB + Frida TLS、准确包名/PID、当前 descriptor 预检与一次受限启动重试，目标/版本/ABI/Root/forward 校验保留。真实 TLS1.3、固定手机证书、错误证书/令牌拒绝及正确令牌鉴权通过。传统公网 ADB 本身仍未加密；业务数据由 Frida TLS 保护。
- 首次 decoder 在创建 Session/挂接前因内置 descriptor 版本冲突退出；修复后只对同一已分配批次重试一次，保留原失败状态、日志及启动摘要。没有第二个采集批次，没有用旧结构替代当前结构。
- 本次 Frida、采集进程、专用 ADB server 已退出，精确 forward 已移除，专用监听为0；临时 TLS 私钥/令牌已清理。原匹配 ADB key 保留；手机 RUNNING、绑定/公网映射及4条安全组入站规则未变，nginx/sshd active，系统 Python3.6.8 未替换。没有新增资源/费用、网络/IAM变更或晨会修改。
- Google 三个内置包已按 Android 官方 pm enable 方法启用，User 登录并从 Play 安装 Huuuge；原无探针图形修复和可玩反馈保留。本轮 Huuuge12.09.27229/1789041595、Android12/ARM64；Play Protect 认证仍未确认，长期稳定性未测。
- 当前无执行阻塞；等待原业务 PR #2 / 治理 PR #4 Review，不标 Complete/Accepted。真实数据、配置、地址与密钥只留受控环境；本机不持续采集。Subagents: none。

## 管理与部署交接

手机使用官方eds-aic/2023-09-30 EdsAgent RunCommand→DescribeTasks；Linux使用现有ECS Cloud Assistant RunCommand→DescribeInvocationResults。复用User已授权OAuth。Workbench1.0.1已配置并做Linux只读查询，未建立SSH会话、未用于云手机ID。浏览器自动化保持停止，不重放历史未知点击；User在厂商网页正常操作。

原Google三个包存在但禁用，使用Android官方pm enable启用并回读；User亲自登录，从Play安装Huuuge（installer=com.android.vending）。无探针图形问题只为Huuuge启用镜像内置ANGLE解决，User“现在好了”；本轮沿用。完整历史见原Task及业务部署说明，不用旧“未采集”状态覆盖当前结果。

本轮Linux独立venv/Frida官方版本、手机独立OpenSSL工具、静态descriptor及端到端TLS方法见[部署说明](https://github.com/840832144/huuuge-android-research/blob/codex/huuuge-cloud-single-instance/deploy/cloud/TLS_TRANSPORT.md)。结果/日志只留原受控云端任务目录；受控本机记录保存官方管理任务的提交与回读。Git只发布[验收记录](https://github.com/840832144/huuuge-android-research/blob/codex/huuuge-cloud-single-instance/deploy/cloud/ACCEPTANCE.md)与脱敏统计，不复制运行时秘密或业务值。

## 下一步

1. Review原业务PR #2的连接适配、descriptor预检/一次启动重试边界、24项检查及真实312/312/0证据。
2. Review原治理PR #4中的授权、执行事实及Task/Status一致性；无待User操作的执行阻塞。
3. 正式Review与合入main后再finalize原reservation；当前不标Accepted/Complete。若继续新批次，需新的任务范围，并重新准备已清理的短期TLS材料及前置检查。

不新增任务/资源/端口映射，不恢复本机持续采集或SVN安装包，不触碰晨会。Workspace Sync沿用ON_DEMAND，Git为真相源。
