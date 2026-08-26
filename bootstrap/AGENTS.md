# Global Codex Instructions

## 适用范围

本文件是所有 Codex 项目共享的稳定基线。项目仓库中的 `AGENTS.md` 可以补充领域、流程和验证规则；离当前目录更近的项目规则可以细化本文件，但不得降低安全、凭据和外部写入要求。

- 全局长期规则保存在 `~/.codex/AGENTS.md`。
- `~/.codex/AGENTS.override.md` 只用于明确的临时全局覆盖；存在时 Codex 不会同时读取同级 `AGENTS.md`。
- 项目专属事实、命令和状态留在对应仓库，不写入全局文件。

## Tool Discovery

任务需要外部能力时，按以下顺序发现和选择工具：

1. 先读取当前生效的全局与项目级 Agent 指令，确定目标、权限、副作用和项目真相源。
2. 检查当前 Host/会话实际暴露的 MCP tools、Connectors、Skills、Plugins 和内置工具；不得根据旧会话或文档假定工具可用。
3. 优先使用已批准、面向该系统的专用接口；同一能力可用时，优先级为受控 Connector/MCP、现有 Skill/Workflow、仓库已有脚本，最后才是通用 shell 或新代码。
4. 调用前区分 `READ`、`WRITE`、`ADMIN/SECURITY`。工具可见不等于已获得写入、授权、发布或管理员操作许可。
5. 先读取再修改；先搜索和确认目标再创建，避免重复对象。任何有副作用的调用都要验证结果，并保留最少、脱敏、可复查的证据。
6. 专用工具不可用时，先检查当前项目可访问的公开接入文档，准确报告缺失的能力或配置。只有已获权限的维护者才检查私有源码仓库；新人不得把访问私有仓库作为开始任务的前置条件。不得擅自安装替代服务、拼接原始 API 请求、复制凭据或绕过组织策略。
7. 项目级 `AGENTS.md` 负责声明该项目允许使用哪些能力及附加限制，不复制共享工具实现，也不把项目仓库变成全局工具目录。

## Shared Document Assistant

`Document Assistant` 是所有项目可复用的公司文档能力，不属于某个业务 Workspace。策划使用已配置的 Tool 即可，不需要读取、Clone 或安装其私有实现仓库。

- 已授权维护者的实现真相源：`https://github.com/840832144/document-assistant.git`
- 已授权维护者的非敏感工作日志：`https://github.com/840832144/larkdoc_bot.git`
- 公共新人入口：`https://github.com/840832144/AI-Workspace.git`
- `READ`：`feishu_healthcheck`、`get_document`、`list_folder`、`search_documents`
- `WRITE`：`create_document`、`append_document`、`replace_document`、`create_folder`
- `ADMIN/SECURITY`：`grant_company_edit`、`grant_group_edit`、`grant_user`

使用规则：

1. 只有任务需要读取、创建、维护或发布公司文档时才调用；普通仓库工作不自动产生云文档。
2. 创建前按标题和目标目录搜索；目标已存在时先确认并更新，不通过重试制造同名文档。
3. 新生成的云文档默认在创建后立即授予企业内可编辑权限，除非 User 明确要求私有、只读或不授予编辑权限。
4. 如果管理员策略阻止共享，保留已创建文档，报告文档标识和权限失败；不得绕过策略，也不得重复创建。
5. 写入后回读正文或元数据；权限变更后回读权限状态。只记录必要结果，不记录完整正文、私有 Registry 或敏感返回值。
6. `FEISHU_APP_SECRET`、tenant access token、用户凭据和其他 secrets 只能存在于受控环境，不得写入源码、Git、Agent 指令、提示词或日志。
7. Tool 名称、参数或能力与当前会话不一致时，以实际 tool schema 和实现仓库为准；停止猜测并报告差异。
8. 新人流程若检测不到 Document Assistant，应在开始采集前尽早报告“共享工具尚未由管理员配置”；不得要求新人申请私有源码权限、Clone 私有仓库或自行配置 secret。

## 文档语言

- 面向策划和用户的文档默认使用中文。
- 其他语言只用于专有名词、命令、文件名、稳定技术术语或必要的对照解释。

## 安全与仓库纪律

- 遵守当前仓库更具体的 `AGENTS.md`、`CONTRIBUTING.md`、状态和交接规则。
- 不覆盖无关的 User 或 Agent 变更，不使用破坏性 Git 操作，不重写共享分支历史。
- 不把 credential、token、私钥、个人数据、完整业务数据或完整运行日志写入 Git。
- 外部写入、共享、发布、部署和权限变更必须处于 User 任务范围与组织策略内。

## Global 与 Workspace 边界

- Tool Discovery、共享 Document Assistant 入口和跨项目安全基线属于 Global Codex 层。
- AI-Workspace 只负责 Game Design 的架构、Capability、Workflow、Skill、Template、项目状态和交接；它可以引用工具能力，但不承担运行时工具目录、安装入口、endpoint、凭据或连接状态管理。
