# TASK-0031 — Huuuge 单实例云端游戏与采集闭环

- Status: Review
- Project key: HUUUGE
- Owner: User / ChatGPT
- Executor: Codex
- Priority: P1 / bounded pilot
- Date: 2026-09-15
- Updated: 2026-09-15
- User decision: Approved；资源尚未就绪，先完成代码与部署准备
- Allocation relationship: new
- Related tasks: TASK-0027
- Subagents: none

## Goal

按 [采集器 Issue #1 v3](https://github.com/840832144/huuuge-android-research/issues/1) 跑通一台云端 Huuuge 环境：策划仅用厂商网页，游戏与采集/解码均在云端，真实新增数据可保存且正常结束。2026-09-15 User 明确资源尚未就绪，本轮先交代码与部署准备，云端成功不得以静态或合成测试代替。

## 前置校验与能力契约

- 同步 AI-Workspace `5b5414c`、业务仓库 `759669b`；两处 main 工作树原本干净，使用独立 linked worktree 和 `codex/huuuge-cloud-single-instance` 分支。
- 完整 Registry scan/validate：14 canonical、0 collision、status=valid；远端预留 TASK-0027/0028/0030，allocator remote-CAS 实际返回 TASK-0031，reservation 保持 pending-main。
- 无同目标云端 Task/Candidate；TASK-0027 是笔记本可靠性任务，本任务不续写、不恢复其本地部署范围；晨会 TASK-0028 与其他研究任务所有权不变。
- 项目能力来源：Huuuge `docs/collector/CURRENT_CAPABILITIES.md` 的被动 RpcMessage 采集、descriptor 解码、READY、Stop/Flush 和 Session 保存。公共 Capability Catalog 已核对，不新增共享平台能力或工具目录。
- 输入：一台由 User/技术提供权限的无影云手机及受控 Linux 执行端、当前版本/ABI、匹配探针/descriptor、独立结果目录。
- 操作：业务仓库 WRITE（必要适配与测试）；云端运行仅在资源授权就绪后执行。权限、购买、开放管理端口属于 User/技术，不由 Agent 扩大。
- 输出：必要云端启停/检查适配、脱敏模板、短中文部署说明、三项验收记录与受控结果交接。
- Workspace Sync：ON_DEMAND、provider unavailable、stale 6、conflicts 0；使用 Git 最新证据，未开启 WATCH。PowerShell 入口受执行策略阻止后，直接运行其原有 Python CLI，未更改执行策略。

## 实施与边界

复用现有 Collector、agent.js、解码器和停止控制文件；仅补 Linux 运行和本轮 Session 验收所必需的适配。云手机 Android/ABI、Root/Frida 权限和 Huuuge 版本由现场验证，不照搬蓝叠/Houdini。现成网页客户端由 User 登录并操作；Agent 不代玩、不自动点击、不修改请求、奖励、余额或服务端。

不做多人、克隆、统一工作台、报告平台、本地安装包、历史数据搬迁或其他游戏；不修改晨会服务和共享主机全局环境。原始数据、标识和日志仅留受控云端；Git 只收代码、模板、计数和状态。

## 验收

| 项目 | 必须证据 | 当前结果 |
| --- | --- | --- |
| 网页游戏 | User 在厂商网页登录自己的账号并正常交互 | 待资源，未执行 |
| 真实采集解码 | 本轮新增、关联普通手动操作的成功业务解码样本 | 待资源，未执行；计数 unknown |
| 正常结束保存 | Stop/flush、进程退出、结果仍可读、捕获/成功/失败数可核对 | 待资源，未执行 |

静态和合成检查单列，仅支持准备工作 Review。云端闭环未通过时不标 Complete/Accepted。

## 交付与下一步

本状态只表示**准备代码与说明 Review**，真实云端闭环仍待资源，不是 Complete/Accepted。

- 实施 [PR #2](https://github.com/840832144/huuuge-android-research/pull/2)，代码 commit `9bb241b`；中文[部署说明](https://github.com/840832144/huuuge-android-research/blob/codex/huuuge-cloud-single-instance/deploy/cloud/README.md)和[验收记录](https://github.com/840832144/huuuge-android-research/blob/codex/huuuge-cloud-single-instance/deploy/cloud/ACCEPTANCE.md)已提交。
- Linux [CI 34957001266](https://github.com/840832144/huuuge-android-research/actions/runs/34957001266) 14/14 合成检查通过：实际 decoder 子进程、损坏 wrapper 保留、断连失败、单运行锁、SIGTERM、supervisor 启停与最终文件回读；没有真实云手机数据。
- 业务 Status/COLLAB_LOG/TASKS/CHANGELOG/Handoff 均已更新。仅在云端部署所需的 Linux controller、配置模板和现有 decoder 异常处理有代码变更，未运行本机采集或修改晨会。
- 缺少资源与受控入口，以及云端当前 build/ABI、匹配 descriptor、网页 User 操作证据。技术提供后继续本 Task 的三项验收，不重新分配。
- reservation 保持 pending-main，待 Review 后 canonical 进入共享 main，再由本独立 worktree 使用本机 reservation 元数据 finalize；不提前释放或伪称已合入 main。
