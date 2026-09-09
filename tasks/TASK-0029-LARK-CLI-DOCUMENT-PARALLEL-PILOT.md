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

User 已在浏览器创建新应用，官方 CLI 初始化完成；独立 LARKSUITE_CLI_CONFIG_DIR 的凭据为系统 keychain 引用。auth scopes 的 userScopes 当前仅 offline_access；用户登录仍 missing。此查询不覆盖应用身份权限、企业或可用范围，后台仅本人可用和建议名称仍待回读确认。尚未创建临时文档。

创建向导在内置浏览器/Chrome 读取失败（timeout / Debugger unattached）；只核实模板源码，未伪称页面权限已全部核清。实施记录为 document-assistant `docs/LARK_CLI_PILOT.md`，commit `cf8b9414a9feac547c2f7c94a14f80bff847107a`，secret scan 通过。旧 feishu-docs 配置及原 checkout 图片改动保持原状。

续跑结果：User 完成浏览器授权，Codex 完成 device-code 登录；verify 确认 identity=user / ready / token valid。实际返回 90 项 scope，相对请求多 84 项、缺 search:docs:read。User 明确这些权限由自己一键开启全部免审项，保留该决定，操作仍只限本次文档试用。真实标题查重返回 missing_scope，尚未创建或修改临时文档。

User 后续明确选择「补齐文档与云空间全部权限，含需审核项」，未选择 CLI 全业务域。按官方当前 docs / drive 权限目录去重共 40 项，加 offline_access 认证项形成固定申请集合；相对当前已授予集合仅缺 search:docs:read 与 space:document:retrieve。保留 User 已开启的免审权限，不新增邮箱、群聊、审批业务授权。原单项搜索补授权流程被本次选择取代，不再恢复其 device-code。

User 后续说明未扫描二维码，而是在后台手动添加权限。实际回读 app userScopes=172；space:document:retrieve 已开启，search:docs:read 仍未开启，已有 drive:drive.search:readonly。当前有效用户 token 仍为原 90 项，应用权限变更不等于 OAuth grant 更新。

本次按已开启权限继续：固定文档/云空间集合中的 search:docs:read 改为已有的 drive:drive.search:readonly，其余保持；标题查重与创建后查找使用 user 身份 drive.files.list，在目标位置按精确标题匹配。CLI v2 +search 保留为未通过项，不反复索要同名不同 scope，不扩大后台权限。

唯一下一步：User 点击新的已开启权限集合授权链接（无需扫码），Codex 完成新 device-code 流程并核验后，列表查重并继续唯一文档验证。虚构 XML 本机 parse 已 passed，尚未创建云文档。
