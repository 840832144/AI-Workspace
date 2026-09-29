# TASK-0031 — Huuuge 单实例云端执行交接

- Updated: 2026-09-29
- Actor: Codex
- Owner: User；本人负责权限、账号登录与手动游戏操作
- Status: Changes Requested；v2 已登记，真实云端验收未执行
- Task: [TASK-0031](../tasks/TASK-0031-HUUUGE-CLOUD-SINGLE-INSTANCE.md)
- Source: [Issue #1 v3](https://github.com/840832144/huuuge-android-research/issues/1)
- Subagents: none

User 指定 [PR #11 v2-GooglePlay / 5ff7190](https://github.com/840832144/AI-Workspace/blob/5ff7190137f1512f52cddacc0f5d17ce5cc4254e/tasks/support/TASK-0031/CLOUD_DEBUG_PLAN_20260929.md)取代旧执行顺序，不再等待其他技术对接人。先 Codex 准备 Google Play/GMS，到登录页才通知 User 本人登录，再验证商店、从 Google Play 获取/确认 Huuuge，完成无探针基线后才能真实采集。

## 2026-09-29 实况与阻塞

- 原治理分支安全合入 main `b0a36c8`；保留双方 Changelog，Registry 从 canonical 重建后 19 canonical / 0 collision / valid。Workspace Sync 实测 ON_DEMAND / provider unavailable / stale 6 / conflicts 0。原 PR #4 / 业务 PR #2 保留，未合并共享 main，reservation 保持 pending-main。
- User 更正 Workbench CLI 需要 Codex 安装。已安装阿里云官方 Windows amd64 包 v1.0.1（`86c0aff`），官方 SHA-256 校验通过，version/exec/配置/列表帮助已核验。安装路径与方法见业务部署说明；不把治理仓库变成运行时配置入口。
- 默认 Workbench 配置文件尚不存在；未读取凭据、连接 ECS 或更改安全组。CLI 面向 Linux ECS，不能据此认为云手机已有受控通道；两个目标均须分别核验。
- 浏览器 provider 返回 fetch 失败；桌面窗口列表只能确认“无影云手机”Chrome 窗口存在。Computer Use 因无法可靠识别当前 URL 而停止本轮界面操作，未继续点击或绕过检查。Google 组件/网络/镜像/ABI 未读到，未安装或启用 GMS，未到登录页。
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

## 唯一下一步

恢复能够核验 URL 的云手机浏览器控制，Codex 先检查 Google 组件与手机网络，再按厂商适用方法安装/启用。到 Google 原生登录页停止敏感输出并通知 User 本人登录。Workbench 凭据由 User 在受控本机交互配置，Linux 目标单独核验，不阻止先做手机准备。后续严格按 v2 顺序记录真实结果，最后 Stop → 进程退出 → 保存结果回读，更新业务部署/验收与原 Task/Status/Handoff。当前没有商店、游戏或云端采集成功结论。

治理分支尚未合入 main；reservation 保持 pending-main，Review/合入后再 finalize。无额外 Agent，Subagents: none。
