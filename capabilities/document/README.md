# Document Capability

- ID: `CAP-DOC`
- Status: Registered / Waiting for ChatGPT Review
- Scope: Shared platform capability
- Contract owner: ChatGPT
- Implementation owner: Codex / Document Assistant repository
- Related RFC: [`RFC-0002-Document-Assistant.md`](../../docs/rfc/RFC-0002-Document-Assistant.md)
- Related ADR: [`ADR-0003-Capability-First-Discovery.md`](../../docs/adr/ADR-0003-Capability-First-Discovery.md)

## Outcome

Document Capability 让 Agent 在受控权限下发现、读取、创建、维护、发布和授权公司文档，并以回读结果证明交付完成。契约不绑定 Feishu、MCP transport、具体 Tool 名称或某个 Host。

`Document Assistant` 是当前批准的实现 provider，不是 Capability 本身。Feishu MCP tools 是该 provider 在特定 Host 上暴露的实现接口。

## Operations

| Operation ID | Outcome | Class | Required input | Success evidence |
| --- | --- | --- | --- | --- |
| `CAP-DOC-DISCOVER` | 按标题、项目或目录找到目标文档 | READ | 查询条件或目录 | 返回稳定 document/folder identifier，或明确无结果 |
| `CAP-DOC-READ` | 读取指定文档内容和必要结构 | READ | 稳定 identifier 或 URL | 标题、正文/结构与目标一致 |
| `CAP-DOC-CREATE` | 创建一篇新文档 | WRITE | 标题、正文、可选目录/项目 | 返回稳定 identifier；回读标题和正文成功 |
| `CAP-DOC-UPDATE` | 追加或整篇替换现有文档 | WRITE | 目标 identifier、更新内容、更新模式 | 原 identifier 保持；更新后回读成功 |
| `CAP-DOC-ORGANIZE` | 浏览或创建文档目录 | READ / WRITE | 目录 identifier 或名称 | 目录列表或新 folder identifier 可回读 |
| `CAP-DOC-PUBLISH` | 将已审阅产物发布到公司文档系统 | WRITE | 来源、目标、发布策略 | 搜索防重、写入、回读和来源引用全部通过 |
| `CAP-DOC-SHARE` | 在组织策略允许时授予编辑权限 | ADMIN/SECURITY | 文档、principal、权限模式 | 权限 API 成功且回读匹配；失败时保留原文档 |

## Capability Discovery

以下 User 目标应先匹配本 Capability，而不是直接匹配 Tool 名称：

- “帮我找/读这篇公司文档” → `CAP-DOC-DISCOVER` + `CAP-DOC-READ`
- “把报告写入飞书” → `CAP-DOC-PUBLISH`
- “更新原来的报告” → `CAP-DOC-DISCOVER` + `CAP-DOC-UPDATE`
- “新建目录并整理文档” → `CAP-DOC-ORGANIZE`
- “让公司/群/用户可编辑” → `CAP-DOC-SHARE`

选择 Operation 后，再检查当前 Host 是否有批准的 Implementation Binding。Capability 已登记但 provider 不可用时，状态应报告为 `Implementation unavailable`，不得要求新人访问私有源码、输入 secret 或自行拼接 API。

## Current Implementation Binding

下表是当前 provider 映射，不属于稳定 Capability contract。实际调用必须以当前 Host 暴露的 tool schema 为准。

| Capability operation | Provider | Current Tool implementation |
| --- | --- | --- |
| Implementation preflight（非 Capability Operation） | Document Assistant | `feishu_healthcheck` |
| `CAP-DOC-DISCOVER` | Document Assistant | `search_documents`、`list_folder` |
| `CAP-DOC-READ` | Document Assistant | `get_document` |
| `CAP-DOC-CREATE` | Document Assistant | `create_document` |
| `CAP-DOC-UPDATE` | Document Assistant | `append_document`、`replace_document` |
| `CAP-DOC-ORGANIZE` | Document Assistant | `list_folder`、`create_folder` |
| `CAP-DOC-PUBLISH` | Document Assistant + approved Workflow | search → create/update → get → permission verify |
| `CAP-DOC-SHARE` | Document Assistant | `grant_company_edit`、`grant_group_edit`、`grant_user` |

实现真相源只供已授权维护者使用：`https://github.com/840832144/document-assistant.git`。公共策划入口为 `https://github.com/840832144/AI-Workspace.git`。

## Default Policies

1. 创建前先搜索标题和目标目录；已存在时确认后更新，不重复创建。
2. 新生成的云文档默认企业内可编辑，除非 User 明确要求私有、只读或不授予编辑权限。
3. 管理员策略阻止共享时，保留已创建文档并报告权限失败；不得绕过策略或创建副本重试。
4. 写入后回读正文/元数据，授权后回读权限状态。
5. 面向策划和用户的正文默认中文；其他语言只用于必要技术内容。
6. credential、token、私有 Registry、完整文档正文和敏感返回值不得进入 Git、Agent 指令或日志。

## Failure Semantics

| Condition | Capability result |
| --- | --- |
| Catalog 没有匹配项 | `Unknown capability`；澄清目标或建立提案 |
| Capability 已登记，但当前 Host 无 provider/Tool | `Implementation unavailable`；报告管理员待办 |
| 文档已创建，权限被管理员策略拒绝 | `Partial success`；保留 document ID，权限待处理 |
| Tool 调用成功，但回读不一致 | Capability 未完成；停止并报告验证失败 |
| 搜索命中多个候选 | Capability 暂停；先让 User/Workflow 确认目标 |

## Non-goals

- 不在 AI-Workspace 实现 MCP、Connector、transport、认证或文档转换器。
- 不登记运行时 endpoint、credential、安装状态或连接状态。
- 不把 Tool 可用性当作 Capability contract。
- 不绕过企业管理员策略。
