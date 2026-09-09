# TASK-0029 — 官方飞书 CLI 文档能力并行试用

- Status: In Progress
- Project key: WORKSPACE
- Owner: User / ChatGPT
- Executor: Codex
- Priority: P1 / bounded pilot
- Date: 2026-09-09
- Updated: 2026-09-09
- User decision: Approved
- Allocation relationship: new
- Related tasks: TASK-0020, TASK-0021
- Subagents: none

## Goal

在当前 Windows Codex 中接入官方 CLI 与匹配的文档 Skills，以隔离配置完成一份虚构临时文档的创建、查找、局部读取、修改和回读，保留原链接与非目标内容，并保留现有 feishu-docs。

## 授权与来源

- User 于 2026-09-09 明确要求开始有限并行试用；应用选择、授权链接仍交 User 确认，Secret 不进入聊天。
- User 暂停讨论后明确恢复本 Task，选择在当前企业新建独立企业自建应用，建议名称「AI Workspace CLI（试用）」；初期可用范围仅 User 本人。此决定不新建任务、不修改旧文档助手或晨会应用。
- 创建向导默认权限必须先核对；只申请文档试用及必要认证权限，不接受全量推荐。官方链接和二维码交 User 完成浏览器确认，额外权限或管理员审批单独说明，不自行扩大或切回旧应用。
- [AI-Workspace PR #3](https://github.com/840832144/AI-Workspace/pull/3)，已读研究、评论与交接，来源 head `49e843b91744e1c86935391d09fb26927e9e534b`。
- 完整执行边界与验收：[LARK_CLI_PILOT_HANDOFF.md](../docs/experiments/LARK_CLI_PILOT_HANDOFF.md)。
- Capability：CAP-DOC-DISCOVER / READ / CREATE / UPDATE；共享仅按文档试用需要及 User 批准处理。
- 治理与实施分支均为 `codex/lark-cli-document-pilot`；实施记录留在 document-assistant，第三方程序和凭据仅存受控 Host。

## Task Gate

- 同步 AI-Workspace `main@1dd6de3e244858c44b716cacd72961ea9419f564` 与 document-assistant `main@e80fd8a7cb24edde876b492b9b575e2c092d06ab`。
- Registry scan / validate：13 canonical、0 collision、valid；已枚举全部远端 heads 并搜索 tasks 与唯一 Roadmap，未发现同目标 active Task。
- TASK-0027 与 TASK-0028 的远端 reservation 属于其他目标，保持不动。
- 在包含最新 main 的独立非 main linked worktree，正式 remote-CAS allocator 返回 TASK-0029；reservation 保持 pending-main，进入 main 后才能 finalize。
- 本 Task 与自动重建 Registry 校验、提交并 push 后才开始安装。
- Workspace Sync：ON_DEMAND、provider unavailable、6 stale、0 conflict；以最新 Git 为本次依据，不把旧 Context 当现场事实。

## Scope

1. 核对官方 release、固定 CLI 与三个 Skills 的同一版本，回验二进制版本、help 和 Codex 发现结果。
2. 仅接入 lark-shared、lark-doc、lark-drive 及必要 references；采用项目范围，保留原 Skills 和 MCP 配置。
3. 隔离应用、配置与登录状态；显式 user 身份，列出精确最小 scopes，应用选择与 OAuth 授权交 User 确认。
4. 一份标记 temporary 的虚构文档，创建前查重；创建后保存原关联，局部读改后验证原链接及非目标内容。
5. 维护 Task、Handoff、实施试用记录、版本固定与回退说明，提交并 push 独立分支等待 Review。

## Non-goals

不改 EarlyMeeting、正式飞书文档或导航中心；不卸载或重配旧 MCP；不新增 MCP Server、框架、回调或 Webhook；不接 Sheets/Base/Wiki；不全量迁移；不修改其他未提交变更。真实身份、授权链接、device_code、文档标识、凭据及原始响应不进公共 Git。

## Acceptance

- CLI 真实版本与 Skills tag/commit 对齐；Codex 实际发现并读取三个 Skills。
- 仅文档所需 scopes 经 User 确认，隔离配置身份和有效授权经本机核验。
- 创建、按标题查找、局部读取、目标段修改与回读全部成功；顶层 ok、退出码、result 和 warnings 无未处理 partial_success。
- 文档 ID/链接稳定，非目标内容完整保留；结果未知先查原资源，不重建、不盲重试。
- 现有 feishu-docs 健康及配置保留有证据；不把安装完成等同于实测完成。

## 当前结果与唯一下一步

正式登记 commit `efacc34a4677c6d1ffe080c635c035ce400fab82` 已推送；本次恢复执行前 Registry 为 14 canonical / 0 collision / valid。reservation 保持 pending-main。

CLI 已安装并真实回验为 1.0.94，Windows 发布包与官方 checksums 一致；三个 Skills 同取 v1.0.94 / `f065bf5b645af381f9b7475ce721451e6ca36a23`。当前 Codex 0.153.4 的 skills/list 已返回三项 repo scope / enabled / 0 error，本轮会话也已自动加载。

配置采用独立的 LARKSUITE_CLI_CONFIG_DIR；尚未创建应用、完成用户登录或写入临时文档。旧 feishu-docs 前次认证、API、Drive healthcheck 通过；实施原 checkout 的图片未提交改动保持原状。

唯一下一步：核对官方创建向导默认权限，并展示真实创建链接及二维码，让 User 在当前企业确认独立应用和仅本人可用范围。
