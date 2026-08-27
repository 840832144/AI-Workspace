# Workspace Live Context Feasibility Audit

- Date: 2026-08-27
- Scope: TASK-0021 Phase 0
- Decision: Feishu Drive Context Hub

## 结论

当前应用不满足飞书 Wiki Gate，因此采用飞书 Drive 文件夹 + 原生 Docx。该方案复用现有 Document Assistant，不要求 User 新增权限或知识空间，也不回退到人工下载/上传 Markdown。

## Feasibility Matrix

| Candidate | Current Evidence | Required Permission / Resource | Host Reachability | Conflict / Revision | Exit Cost | Decision |
| --- | --- | --- | --- | --- | --- | --- |
| Feishu Wiki | 官方提供空间列表、节点列表、节点信息和创建节点 API；当前租户实测空间列表 HTTP 400，应用缺少 Wiki scope | 至少 `wiki:wiki`、`wiki:wiki:readonly` 或 `wiki:space:retrieve`；还需可访问知识空间 | Codex 可经本地 Provider；ChatGPT 直连仍受平台地区限制 | 理论上可用 node/object 标识，但当前无法读取，不能验证 revision 闭环 | 中 | 不满足 Gate，暂不采用 |
| Feishu Drive Folder + Docx | `create_folder/list_folder/create/get/replace` 与 Drive 权限已实现；healthcheck、Docx、`tenant_readable` 与 `tenant_editable` 均有真实回读 | 当前 `drive:drive` 与 Docx scopes 已满足；无需新资源 | Codex 可写；ChatGPT/Generic Agent 通过 Git mirror/local pack | Document ID、Registry updated time、内容 fingerprint 与 Workspace baseline 可组合判断 | 低 | 采用 |
| 其他协作平台 | 当前未登记 Capability binding，也没有批准账号、权限或运维证据 | 新 provider、账号与治理 | 未验证 | 未验证 | 高 | 不引入 |

## 官方与实测证据

- 飞书官方：[获取知识空间列表](https://open.feishu.cn/document/server-docs/docs/wiki-v2/space/list)、[获取知识空间子节点列表](https://open.feishu.cn/document/server-docs/docs/wiki-v2/space-node/list)、[获取知识空间节点信息](https://open.feishu.cn/document/server-docs/docs/wiki-v2/space-node/get_node)、[创建知识空间节点](https://open.feishu.cn/document/server-docs/docs/wiki-v2/space-node/create)。
- 飞书官方：[新建文件夹](https://open.feishu.cn/document/server-docs/docs/drive-v1/folder/create_folder)、[获取文件夹中的文件清单](https://open.feishu.cn/document/server-docs/docs/drive-v1/folder/list)。
- 当前 Host：`feishu_healthcheck` 的 environment、tenant token、API connectivity 和 `drive:drive` probe 均通过。
- Wiki live probe：`GET wiki/v2/spaces` 被官方 API 拒绝，错误只表明缺少 Wiki 应用身份 scope；未记录应用标识、申请链接、token 或空间信息。
- Drive live Pilot：唯一文件夹内回读 7 个唯一标题；正文与原生表格可读；权限 GET 为 6 份 Git-authoritative `tenant_readable` 和 1 份协作草稿 `tenant_editable`。

## 切换到 Wiki 的条件

只有 User 以后明确要求切换，且管理员一次性完成 Wiki scope 发布、应用安装和可访问知识空间准备后，才重新执行 Gate。重新验证必须覆盖空间/节点 list/get/create、关联 Docx 读写、稳定 node/object 标识、revision/fingerprint、权限与回滚；任一项失败继续使用 Drive Hub。
