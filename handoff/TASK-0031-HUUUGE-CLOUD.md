# TASK-0031 — Huuuge 单实例云端准备交接

- Updated: 2026-09-15
- Actor: Codex
- Status: Review（准备代码与说明）；真实云端验证待资源
- Task: [TASK-0031](../tasks/TASK-0031-HUUUGE-CLOUD-SINGLE-INSTANCE.md)
- Source: [Issue #1 v3](https://github.com/840832144/huuuge-android-research/issues/1)
- Subagents: none

User 已批准单实例方案，并确认资源尚未就绪，先完成代码和部署准备。已同步两个仓库并完成 Registry 防重、独立 worktree、remote-CAS 登记，15 canonical / 0 collision / valid；TASK-0031 reservation 待 canonical 合入 main 后 finalize。

## 交付与证据

- 业务 [PR #2](https://github.com/840832144/huuuge-android-research/pull/2)，代码 commit `9bb241b`。新增 Linux controller 复用现有 probe/decoder，补配置/版本/ABI/转发校验、独立目录、启停和文件回读；修复同名 Session 覆盖、损坏 wrapper 丢弃及异常停止误报。
- Linux [CI 34957001266](https://github.com/840832144/huuuge-android-research/actions/runs/34957001266) 14/14 合成检查通过，包括真实子进程锁、SIGTERM 和 supervisor 完整路径；本机 11 passed / 3 Linux-only skipped。合成计数不作为真实游戏证据。
- 业务仓库 `deploy/cloud/README.md`、`ACCEPTANCE.md`，以及 CURRENT_STATUS/COLLAB_LOG/TASKS/CHANGELOG/Handoff 已更新。Git 不包含 runtime descriptor，技术须从已核验受控结构文件准备；不搬迁历史数据。
- 三项真实验收均未执行，捕获/成功/失败计数 unknown。未连接云实例、未部署本机采集组件、未购买资源、未触碰晨会。当前未创建本轮云资源，后续资源计费/保留/释放由 User/技术确认。
- Issue v3 明确排除本地安装包，因此本轮未执行 SVN 安装包同步。Workspace Sync ON_DEMAND / provider unavailable / stale 6 / conflicts 0；Git 是本轮依据。

## Review 与唯一下一步

ChatGPT Review 准备代码、停止语义与部署说明。User/技术提供一台云手机、云端 Linux 执行端和受控权限后，继续 TASK-0031，让 User 亲自在厂商网页完成普通游戏操作，核对新增解码及正常停止保存。Review 不等于云端兼容验证；不扩展多人/克隆/平台/本地安装包。

治理分支尚未合入 main；reservation 保持 pending-main，Review/合入后再 finalize。无额外 Agent，Subagents: none。
