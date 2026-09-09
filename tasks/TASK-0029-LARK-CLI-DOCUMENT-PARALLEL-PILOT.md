# TASK-0029 — 官方飞书 CLI 文档能力并行试用

- Status: Accepted
- Project key: WORKSPACE
- Owner: User / ChatGPT
- Executor: Codex
- Priority: P1 / bounded pilot
- Date: 2026-09-09
- Updated: 2026-09-09
- User decision: Accepted
- Allocation relationship: new
- Related tasks: TASK-0020, TASK-0021
- Subagents: none

## Goal

在当前 Windows Codex 中接入官方 CLI 与匹配的文档 Skills，以隔离配置完成一份虚构临时文档的创建、查找、局部读取、修改和回读，保留原链接与非目标内容，并保留现有 feishu-docs。

## 授权与来源

- User 于 2026-09-09 明确批准有限并行试用；暂停后恢复同一 Task，选择在当前企业新建独立企业自建应用，建议名称「AI Workspace CLI（试用）」，初期可用范围仅本人。
- 应用创建、后台权限与 OAuth 均由 User 在浏览器确认，Secret 不进入聊天。最初仅申请文档必要项；User 随后明确保留自己一键开启的全部免审权限，并批准补齐文档与云空间全部权限（含需审项）。此决定不授权其他业务操作或 CLI 全业务域。
- [AI-Workspace PR #3](https://github.com/840832144/AI-Workspace/pull/3) 的研究、评论与交接已读，来源 head `49e843b91744e1c86935391d09fb26927e9e534b`；原 PR 分支未修改。
- 完整边界与交接：[LARK_CLI_PILOT_HANDOFF.md](../docs/experiments/LARK_CLI_PILOT_HANDOFF.md)。
- Capability：CAP-DOC-DISCOVER / READ / CREATE / UPDATE；单份新样例按 User 的默认规则授予企业内可编辑并回读。
- 两仓库实施分支均为 `codex/lark-cli-document-pilot`。第三方程序、配置、凭据及原始运行证据仅在受控 Host，实施说明在 document-assistant。

## Task Gate

- 安装前同步 AI-Workspace `main@1dd6de3e244858c44b716cacd72961ea9419f564` 与 document-assistant `main@e80fd8a7cb24edde876b492b9b575e2c092d06ab`，枚举全部远端 heads 并核对 Task / 唯一 Roadmap。
- 分配前 Registry：13 canonical / 0 collision / valid，无同目标 active Task。TASK-0027 / TASK-0028 的其他 reservation 保持不动。
- 独立非 main linked worktree 的 remote-CAS allocator 正式返回 TASK-0029。正式 Task 与自动 Registry 的提交 `efacc34a4677c6d1ffe080c635c035ce400fab82` 已 push 后才安装。
- User 已明确验收通过；[正式验收记录](../reviews/TASK-0029-USER-ACCEPTANCE.md)关联本轮交付 commits。reservation 在 canonical Task 合入 main 后由 allocator finalize，不另分配或提前 release。
- 收尾再次 fetch 两仓库；治理分支合入最新 `main@5db0beb1976f5a0ae50e85a98e1756b55eaf871b`，实施 main 未变化。Registry 重建并校验 14 canonical / 0 collision / valid。
- Workspace Sync 保持 ON_DEMAND；准备时 provider unavailable、6 stale、0 conflict，以最新 Git 为依据，不把旧 Context 当现场事实。

## Scope 与验收结果

| 项目 | 实际结果 |
| --- | --- |
| 版本固定 | CLI 实际 1.0.94；三个 Skills 同 tag / commit `f065bf5b645af381f9b7475ce721451e6ca36a23`，Windows 发布包 checksums 核对通过 |
| Codex 发现 | Codex 0.153.4 的 skills/list 返回 lark-shared / lark-doc / lark-drive 三项 repo / enabled / 0 error，当前会话已读取 |
| 独立应用和身份 | User 创建新应用；独立配置、keychain 凭据引用；本次 device-code exit 0，verify 为 user / ready / valid / verified |
| 应用可用范围 | 已发布版本 1.0.1：审核通过、当前企业、部分成员且仅 User 一人；禁止外部群和外部用户单聊 |
| 用户权限 | 固定申请的文档/云空间与认证集合 41 项缺项为 0；最终 token 92 项，保留 User 原来选择的 90 项，新增旧搜索和列表读取两项 |
| 创建和查找 | user Drive 根目录直接子项按精确临时标题查重为 0；只创建一份，创建后匹配为 1，关联一致 |
| 局部读取和修改 | keyword 返回单个目标段；按已读 revision 3 用 str_replace 将虚构数值 100 改为 120，revision 4 / result=success / warnings=[] |
| 保留性 | 改后回读共 9 块，仅目标 1 块变化，8 个非目标块及参考超链接保持一致，document ID / URL 不变 |
| 默认共享 | 仅该样例预览后设置企业内获得链接者可编辑，GET 回读 tenant_editable |
| 旧实现共存 | feishu-docs healthcheck 的环境、token、API 和 Drive 均通过，旧配置及环境变量未修改 |

## 限制与未采用范围

- CLI v2 `drive +search` 所需 `search:docs:read` 未开启，真实尝试失败。本次发现采用已授权的 `drive.files.list` 在已确认创建位置精确匹配，不等同于全云空间或 v2 快捷搜索通过。
- User 在后台手动开 scope 不等于当前 user token 已获授权；后续已由 User 确认新 OAuth，Codex 完成 device-code 并验证。旧补授权流程不再使用。
- 创建前页面读取曾失败，无法追溯证明默认权限在提交前完整核清；保留 User 后续明确权限选择。最终后台可用范围已回读，不再列为待确认。
- 应用实际仍为向导生成名称，建议名称未应用；后台还有修改待发布提示，本轮未自行发布新版本，实测所需权限有效。
- 不改 EarlyMeeting、旧应用、正式飞书文档或导航中心，不卸载/重配旧 MCP、不建新框架、不迁移、不操作 Sheets/Base/Wiki、不触碰原 checkout 无关修改。
- 样例保留供 Review，不登记正式 Hub；真实身份、应用/文档标识、授权链接、凭据、完整正文与原始响应不进公共 Git。

## 交付与唯一下一步

实施真相源为 document-assistant `docs/LARK_CLI_PILOT.md`，交付 commit `7332be4f6308374cd955d029d0f1d0a4cde142ca` 已推送，包含固定版本、操作步骤、本机证据索引、历史权限缺口及回退方式。Registry、变更文档链接/敏感标识检查、diff check 与实施 secret scan 均通过。治理与实施记录在各自独立分支交付；本轮是可复查的有限试用结果，不是正式发布能力完整验收或默认 Provider 切换。

User 于 2026-09-09 明确回复「可以，验收通过了」，有限并行试用状态为 Accepted。唯一下一步：完成两仓库 main 合入及 reservation finalize 后归档本轮；后续生产采用、全量迁移或新业务范围仍需单独批准。
