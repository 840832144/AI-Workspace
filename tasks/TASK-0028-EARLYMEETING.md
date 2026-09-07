# TASK-0028 — EarlyMeeting 本机长连接与真实卡片表单回调修复

- Status: Ready
- Project key: EARLYMEETING
- Human alias: 
- Owner: User / ChatGPT
- Executor: Codex
- Priority: P1
- Date: 2026-09-07
- Updated: 2026-09-07
- Candidate provenance: `tasks/candidates/CANDIDATE-20260907-EARLYMEETING-LOCAL-CALLBACK.md`
- Allocation relationship: new
- Related tasks: none

## Goal

在 User 实际 Windows 测试目录定位 SDK_ERROR / UNCLASSIFIED，最小修复长连接并验证现有测试卡片真实表单回调；不保存、不更新公共卡片、不启用定时。

## Scope

本 Task 执行规格唯一入口为 [EarlyMeeting 当前方向](https://github.com/840832144/EarlyMeeting/blob/b18e39365bf95addbff955d09827a9d30e2153fb/docs/CURRENT_DIRECTION.md) 与 [PR #3](https://github.com/840832144/EarlyMeeting/pull/3)。旧 PR #1/#2 已 CLOSED / Superseded，不合并旧业务路线。保留现有「晨会记录」应用、模板和已成功发送流程。

项目声明的结果契约为目标 Windows 本机运行检查、脱敏长连接诊断、现有卡片交互接收及表单传值核对；采用 EarlyMeeting 专属实现与飞书官方 SDK。AI-Workspace 仅存 Task、治理引用和状态，不复制业务实现；不向 Document Assistant 加入本业务。

检查实际目录与依赖，审查后选择复用旧测试代码，复现入口请求/凭据校验/WebSocket 握手失败阶段，按证据作最小修复。只处理指定测试群卡片，持续保持一份接收进程。凭据由 User 在本机安全输入。回调测试提示必须明确未保存、未更新。

## Non-goals

不保存工作内容、不合并成员记录、不更新公共卡片、不实现或启用工作日北京时间 10:00 调度。不新建应用、改模板或改为多维表格，不购买/部署公网服务、不设置自启/系统服务、不改全局代理、防火墙或 TLS。旧完整 MVP 不恢复。

## Deliverables

EarlyMeeting 独立实现分支中的最小修复、必要测试、中文一键启动/检查/停止/回滚说明、目标本机脱敏实测摘要、STATUS 与 Handoff；提交 commit 并推送等待 ChatGPT Review。所有业务交付保留在 EarlyMeeting。

## Acceptance

1. 确认 User 实际测试目录、Node / SDK 版本及同应用进程边界。
2. 有真实 WebSocket 连接成功证据；安装或入口请求成功不代替握手验收。
3. 有指定群现有卡片真实 card.action.trigger 与表单实际传值证据；空表单只算按钮到达。
4. 一键停止后不继续接收；失败能够定位阶段，保留未确认项。
5. 不泄露凭据、内部标识、员工内容、原始回调或完整日志。测试反馈不声称保存。

## Safety

仅允许本机受控输入/受控环境中的凭据；不回显、不写入 Git、不导入旧 .env。输出采用有限字段白名单，禁止原始 SDK 日志及回调。仅授权现有测试卡片的接收和说明未保存的反馈；不发新群消息。系统策略、应用权限或版本发布需要 User 明确决定。Subagents: none / OFF。

## Validation

2026-09-07 AI-Workspace main@1dd6de3：完整 scan / validate 为 13 canonical、0 collision、valid；全部远端分支相关任务目标检索无 EarlyMeeting 同目标条目。既有 TASK-0027 reservation 属于其他项目且保持不动。Approved Candidate 由 remote-CAS allocator 晋升为 TASK-0028，project_key=EARLYMEETING 合法；reservation 保持 pending-main，Review 后 canonical 进入 main 才 finalize。

Workspace Sync：ON_DEMAND、conflicts=0、provider_available=false、stale=6；明确保留云端不可用状态，不改变运行模式。PR #3 基线 b18e393、EarlyMeeting main dfdb6fb。User 已确认本机桌面 EarlyMeeting-local-callback-test 为实际目录，v0.1.0 / Node v24.20.0 / SDK 1.73.3。离线回归与真实连接、真实回调结果分别记录到 EarlyMeeting，尚未验证不得写 Done。

首次 Candidate 日期格式校验拒绝 YYYY-MM-DD，未占号；改为规范 YYYYMMDD 后成功。Registry 只由 scan --write-registry 重建。

## Handoff

准备 Gate：范围已获 User 批准，合法任务已 Ready；本 Task / Registry / Handoff 推送并复验后进入实施。实施完成或现场确有阻塞时，更新本 Task 和 EarlyMeeting STATUS / handoff/CODEX.md，返回业务 branch/commit、根因证据、离线/现场结果、剩余阻塞与唯一下一步，等待 Review；不自行合并 main。Subagents: none。
