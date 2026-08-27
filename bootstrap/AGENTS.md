# Global Codex Instructions

## 适用范围

本文件是所有 Codex 项目共享的稳定基线。项目仓库中的 `AGENTS.md` 可以补充领域、流程和验证规则；离当前目录更近的项目规则可以细化本文件，但不得降低安全、凭据和外部写入要求。

- 全局长期规则保存在 `~/.codex/AGENTS.md`。
- `~/.codex/AGENTS.override.md` 只用于明确的临时全局覆盖；存在时 Codex 不会同时读取同级 `AGENTS.md`。
- 项目专属事实、命令和状态留在对应仓库，不写入全局文件。

## Capability Discovery

收到任务后，先识别要交付的 Capability，再进入实现层：

1. 读取当前生效的全局与项目级 Agent 指令，从 User 目标提取期望 Outcome、对象、操作等级、副作用和成功证据。
2. 先检查当前项目声明的 Capability 与限制，再查公共 [AI-Workspace Capability Catalog](https://github.com/840832144/AI-Workspace/blob/main/capabilities/README.md)。
3. 匹配一个或多个已登记 Capability，确认其输入、输出、`READ` / `WRITE` / `ADMIN/SECURITY` 等级、安全边界和状态。
4. 选择适用 Workflow 与 Skill；如果 Catalog 没有匹配项，报告 `Unknown capability` 并澄清目标，不从可见工具反推或虚构能力。
5. Capability 确定后，才检查当前 Host/会话实际暴露的 MCP tools、Connectors、Skills、Plugins、仓库脚本和内置工具，将其作为 Implementation Binding 候选。
6. 优先使用已批准、面向该系统的专用实现；同一 Capability 有多个实现时，按项目规则、安全边界、可验证性和最小副作用选择。
7. Capability 已登记但当前 Host 没有可用实现时，报告 `Implementation unavailable`；不得把它误报为 Capability 不存在，也不得擅自安装替代服务、拼接原始 API、复制凭据或绕过组织策略。
8. 执行后按 Capability contract 验收，而不是只确认 Tool 返回成功。先读取再修改，先搜索确认再创建，并保留最少、脱敏、可复查的证据。
9. 项目级 `AGENTS.md` 可以增加 Capability 和限制，但不得复制共享实现或把项目仓库变成运行时工具目录。

Tool 的检查和选择只属于 Capability 的实现层，不建立独立的 Tool Discovery。

## Subagent Policy

- 默认使用单 Agent。只有 User 明确要求、Task 明确允许，或存在至少两个真正独立、可并行、读多写少的工作流时，才考虑 Subagents。
- 简单任务、单文件修改、短文档更新和明确命令不启动 Subagent。
- 同一工作区始终只有主 Agent 可以修改代码、文档、配置和 Git；`repo_explorer`、`knowledge_retriever`、`evidence_test_verifier`、`reviewer` 全部只读。
- 子 Agent 不得调用 Document Capability 的 `WRITE` 或 `ADMIN/SECURITY` Operation，不得修改飞书、权限、配置或其他外部系统。
- 当前 Pilot 的版本化 Agent 模板在子 Agent 中完全禁用 `feishu-docs` 与 `node_repl`；飞书 READ 也由主 Agent 代读后提供最少必要资料。新增或改名 MCP server 后必须重新审阅，不能只依赖文字约束。
- `MANUAL` 严禁与 `--yolo`、Full access、`danger-full-access`、宽松 `/permissions` 或其他等价的父 turn 权限同时使用。Codex 会把父 turn 的 live sandbox/permission override 重新应用到子 Agent，模板中的 `sandbox_mode = "read-only"` 不是这类 override 下的绝对隔离。
- 当前 Host 不能由模式脚本可靠检测 live permission。无法确认父会话保持受限权限时必须维持 `OFF`，先关闭宽松权限并新建受限会话；不得以提示词或 MCP deny 代替 sandbox 前提。
- 主 Agent 必须等待相关子 Agent 完成，核对证据、冲突和未确认项后，独立作出最终判断并执行写入。
- 子 Agent 只返回简洁结论、证据位置、风险和未确认项，不回传大段日志。
- Multi-agent 为 `OFF`、Agent 不可用或委派失败时，主 Agent 继续以单 Agent 完成任务并报告降级；不得另建调度器或把缺少 Subagent 作为阻塞。
- 最终 Handoff 必须记录实际使用的 Agent；未使用时明确写 `Subagents: none`。
- 本 Pilot 只支持 `OFF` 与保守 `MANUAL`，不支持 `AUTO`。模式由 `bootstrap/codex/Set-CodexSubagentMode.ps1` 管理，切换后需要关闭重开 Codex 或新建会话。

## Shared Document Capability

`Document Capability` 是所有项目可复用的公司文档结果契约，公共定义见 [Document Capability](https://github.com/840832144/AI-Workspace/blob/main/capabilities/document/README.md)。`Document Assistant` 是当前批准的实现 provider，不是 Capability 本身。策划使用已配置的 provider 即可，不需要读取、Clone 或安装其私有实现仓库。

- 已授权维护者的实现真相源：`https://github.com/840832144/document-assistant.git`
- 已授权维护者的非敏感工作日志：`https://github.com/840832144/larkdoc_bot.git`
- 公共新人入口：`https://github.com/840832144/AI-Workspace.git`
- 当前 `READ` 实现：`feishu_healthcheck`、`get_document`、`list_folder`、`search_documents`
- 当前 `WRITE` 实现：`create_document`、`append_document`、`replace_document`、`create_folder`
- 当前 `ADMIN/SECURITY` 实现：`grant_company_edit`、`grant_group_edit`、`grant_user`

使用规则：

1. 只有任务需要读取、创建、维护或发布公司文档时才调用；普通仓库工作不自动产生云文档。
2. 创建前按标题和目标目录搜索；目标已存在时先确认并更新，不通过重试制造同名文档。
3. 新生成的云文档默认在创建后立即授予企业内可编辑权限，除非 User 明确要求私有、只读或不授予编辑权限。
4. 如果管理员策略阻止共享，保留已创建文档，报告文档标识和权限失败；不得绕过策略，也不得重复创建。
5. 写入后回读正文或元数据；权限变更后回读权限状态。只记录必要结果，不记录完整正文、私有 Registry 或敏感返回值。
6. `FEISHU_APP_SECRET`、tenant access token、用户凭据和其他 secrets 只能存在于受控环境，不得写入源码、Git、Agent 指令、提示词或日志。
7. Tool 名称、参数或实现范围与当前会话不一致时，以实际 schema 和实现仓库为准；不得反向修改 Capability contract 来迁就某个 Tool。
8. 新人流程若检测不到 Document Assistant，应在开始采集前尽早报告 `Implementation unavailable`；不得要求新人申请私有源码权限、Clone 私有仓库或自行配置 secret。

## 文档语言

- 面向策划和用户的文档默认使用中文。
- 其他语言只用于专有名词、命令、文件名、稳定技术术语或必要的对照解释。

## 安全与仓库纪律

- 遵守当前仓库更具体的 `AGENTS.md`、`CONTRIBUTING.md`、状态和交接规则。
- 不覆盖无关的 User 或 Agent 变更，不使用破坏性 Git 操作，不重写共享分支历史。
- 不把 credential、token、私钥、个人数据、完整业务数据或完整运行日志写入 Git。
- 外部写入、共享、发布、部署和权限变更必须处于 User 任务范围与组织策略内。

## Global 与 Workspace 边界

- Capability Discovery、保守 Subagent Policy、共享 Document Capability 和跨项目安全基线属于 Global Codex 层。
- AI-Workspace 维护可审阅的 Capability Catalog 和 Game Design 治理；它可以记录 provider-neutral contract 与实现绑定引用，但不承担运行时工具目录、安装入口、endpoint、凭据或连接状态管理。
