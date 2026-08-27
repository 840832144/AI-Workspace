# ADR-0004: Codex Subagent Pilot

- Status: Accepted for Pilot
- Date: 2026-08-26
- Decision owners: User / ChatGPT
- Executor: Codex
- Related task: [`TASK-0014-Codex-Subagent-Pilot.md`](../../tasks/TASK-0014-Codex-Subagent-Pilot.md)

## Context

复杂的游戏策划研究与工程任务经常同时包含仓库探索、资料检索、证据核验和独立审查，但简单任务不需要额外并发。未经限制地启用多 Agent 会增加额度消耗、协调成本和并行写冲突风险，也会让现有 Codex、MCP 与项目工作流更难排障。

Codex 原生提供 Subagents、自定义 Agent、全局开关和并发上限。本 Workspace 需要先验证一套可一键关闭、失败可降级、不会改变既有 Capability 与实现配置的保守方案。

## Decision

1. 第一阶段采用 1 个主 Agent 加 4 个专职只读 Agent：仓库探索、资料检索、证据测试核验和独立 Review。
2. 安装器必须先完成并验证 `OFF`，再创建或替换 Agent 模板；OFF 失败时配置字节和 Agent 模板均不得改变，也不得输出安装成功。
3. `MANUAL` 的并发上限为 4 个 spawned-agent threads，但是否委派仍由任务复杂度和独立性规则约束。
4. 同一工作区坚持单写入者：只有主 Agent 可以修改文件、配置、Git、云文档或外部系统。
5. 四个自定义 Agent 固定 `sandbox_mode = "read-only"`；当前 Pilot 在子 Agent 中禁用 Document provider 与 `node_repl`，需要的飞书 READ 由主 Agent 代读后提供脱敏摘要，并在各自 instructions 中再次禁止写入。
6. Subagent 不改变 Capability Discovery。主 Agent 先识别 Capability，再决定是否把实现前的只读工作委派出去。
7. `OFF`、Agent 不可用或委派失败时，主 Agent 自动降级为单 Agent；不实现第二套调度器。
8. 本阶段不采用 1+8：尚无实际证据证明额外四个角色的收益能够抵消额度、等待、重复阅读和冲突核对成本。
9. 本阶段不提供 `AUTO`，避免简单任务被无条件并行化。
10. `MANUAL` 严禁与 `--yolo`、Full access、`danger-full-access`、宽松 `/permissions` 或等价父 turn 权限同时使用。官方行为会把 live sandbox/permission override 重新应用到子 Agent，Agent TOML 的 `read-only` 不能抵消该 override。
11. 当前 Host 无法由脚本可靠检测 live permission。状态未知时必须维持 `OFF`，先关闭宽松权限并新建受限会话；MCP deny、developer instructions 与单写入者规则只是纵深防护。

上述父 turn override 行为以 OpenAI 官方 [Codex Subagents](https://developers.openai.com/codex/subagents/) 文档为依据。

## Rationale

### 为什么是 1+4

四个角色覆盖实施前最容易拆分的只读工作，同时保持责任边界清晰。主 Agent 仍拥有最终判断和所有副作用，避免把一个任务拆成多个写入真相源。

### 为什么默认 OFF

安装模板不等于授权消耗额度。默认关闭使升级可逆，也确保现有单 Agent、MCP、配置和项目流程不依赖 Pilot 才能工作。

OFF 同时是安装提交门：模板复制只发生在配置已经切换并验证为 OFF 之后。这样 config 锁定或不支持的 TOML 不会留下本轮新增/替换的可生效模板。

### 为什么单写入者

共享工作树中的并行写入会引入覆盖、脏状态归属和 Git 整合风险。只读 Subagent 可以并行收集证据，主 Agent 在汇总后串行写入，证据收益与状态安全可以同时保留。

### 为什么不立即扩到 1+8

当前没有 usage/token 对比、真实项目周期或返工率证据。先验证 1+4 的可用性和成本，再由 User 决定是否建立后续 Task。

## Consequences

### Positive

- User 可以用一个命令关闭多 Agent，普通任务继续单 Agent。
- 复杂只读工作可并行，主 Agent 不必放弃写入所有权。
- Agent 模型、推理强度和沙箱可以按角色审阅与版本化。
- 现有 MCP、权限、通知、模型和项目配置保持独立。

### Costs and Risks

- 模式切换需要关闭重开 Codex 或新建会话，当前会话不会动态证明新配置已加载。
- Subagent 会消耗额外额度；当前客户端若不暴露 usage/token，就只能记录 Agent 数、模型、时长和返工。
- 只读沙箱、当前 MCP deny、instructions 和主 Agent 复核共同形成纵深约束；MCP server 新增或改名后必须重新审阅，不能仅凭角色名称假设安全。
- 父 turn 的 live permissions 可以覆盖 Agent sandbox 默认值；因此 MANUAL 需要人工确认受限会话，不能和 full-access 类模式并用，也不能声称脚本已经自动检测。
- MANUAL 不等于自动并行，主 Agent 仍需判断工作是否真正独立。

## Review Gate

ChatGPT 审阅 Pilot 结果、配置完整性、模型分工和六类 Validation。Review 前不增加角色、不提高并发、不启用 AUTO，也不为其他 Host 配置同类 Agent。
