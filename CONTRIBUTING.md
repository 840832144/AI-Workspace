# Contributing

## 适用范围

所有 User、ChatGPT、Codex 对本仓库的修改都必须遵循本规范。本仓库只接受 Game Design / 游戏策划领域的治理、模型、Skill、Workflow、Template 和项目控制面内容。

## 开始前

1. 使用安全方式同步 `main`，不得 force-push 或重写他人历史。
2. 阅读 `AI_TEAM.md`、`ARCHITECTURE.md` 和相关 handoff。
3. 确认修改属于游戏策划治理、协作、标准、模板或项目控制面，而不是业务实现或非游戏领域内容。
4. 检查相关 RFC、ADR、项目 Status 和 CHANGELOG，避免重复或冲突。
5. 需要共享能力时遵循 Global Codex Capability Discovery：先匹配 Capability contract，再选择实现；不得在本仓库新增运行时工具目录、安装入口、endpoint、credential 或连接状态。

## 变更分类

- `docs:` 核心文档、说明、交接和项目控制面。
- `rfc:` 新建或更新 RFC。
- `adr:` 新建或 supersede ADR。
- `standards:` 横向规范变更。
- `workflow:` 工作流变更。
- `skills:` Skill 规范或索引变更。
- `chore:` 不改变协作语义的仓库维护。

推荐 commit 格式：`<type>: <imperative summary>`。

## RFC 流程

1. 从 `templates/RFC.md` 创建下一个连续编号。
2. 写明状态、作者/Actor、日期、目标、非目标、方案、风险和未决问题。
3. 涉及体系边界或多个项目的变化必须先走 RFC。
4. Accepted RFC 若包含长期架构决策，应进一步创建 ADR。

## ADR 流程

1. ADR 编号连续且不可复用。
2. 只记录一个已作出的决策。
3. 不直接修改历史结论；用新 ADR 标记 Supersedes/Superseded by。
4. ADR 必须链接相关 RFC 和受影响项目。

## Task identity 与分配

1. canonical Task 使用全局唯一 `TASK-XXXX`，新 Task 必须显式提供格式合法的 `Project key`；仅审计 grandfather 集合可缺省。可选 human alias 只用于阅读，不能替代 canonical ID。
2. Task Markdown 是真相源，`tasks/TASK_REGISTRY.yaml` 只能由 `python tools/tasks/task_cli.py scan --write-registry` 重建，不手工修改。
3. 新方向在 User 明确批准前进入 `tasks/candidates/`，不占 ID、不可执行。
4. 新 ID 在 non-main independent linked worktree 使用 `task_cli.py next` 完整验证并以 remote CAS 保留；Candidate 使用 `promote` 晋升。reservation 保持到 canonical 进入 main 后 `finalize`，未创建 Task 的放弃场景才 `release`。相同 active（含 Draft）目标必须明确继续已有 Task 或子任务关系。
5. duplicate、解析失败、Registry 漂移、非最新 `origin/main`、main checkout、并发 lock/reservation 冲突全部 fail closed。
6. companion、authorization 和 review 可以关联 canonical ID，但 companion 必须显式分类并引用存在、同 ID 的 canonical，不能成为第二个执行入口。
7. Task / Candidate / Review 变更后重建 Registry、再次 `validate`，再提交和 push；不同 Host/clone 由 remote reservation ref first-writer CAS 排他，Review/merge 前仍需基于最新 main 复验。

操作说明见 [`tools/tasks/README.md`](tools/tasks/README.md)，长期决策见 [`ADR-0006`](docs/adr/ADR-0006-Task-Identity-and-Allocation.md)。

## 项目记录

每个 `projects/<project>/` 必须包含：

- `README.md`
- `CONTEXT.md`
- `MEMORY.md`
- `WORKFLOW.md`
- `STATUS.md`
- `REPORTS/`
- `ASSETS/`

项目实现细节应以链接或 commit 引用方式指向业务仓库，不复制源代码和敏感数据。

## 文档质量

- 首段说明目的和受众。
- 面向策划和用户的文档默认使用中文；其他语言仅用于专有名词、命令、文件名、稳定技术术语或必要的对照解释。
- 新生成的云文档默认授予企业内可编辑权限；只有 User 明确要求私有、只读或不授予编辑权限时才例外。管理员策略阻止时保留已创建文档并报告失败，不得通过重复创建重试。
- 明确区分 Confirmed、Hypothesis、Decision 和 Blocker。
- 使用绝对日期，例如 `2026-08-26`。
- 对外部事实提供可复查的链接、commit、命令结果或 artifact 引用。
- 使用相对链接连接本仓库文档。
- 不保留“稍后处理”而没有责任人或下一动作的模糊状态。

## 安全检查

提交前确认：

- 没有 secret、token、私钥、个人数据或完整业务数据。
- 没有复制其他仓库业务代码。
- 没有把假设写成事实。
- 没有覆盖无关用户或 Agent 变更。

## 完成标准

1. 所有相关文档一致且内部链接有效。
2. 项目 Status 或 handoff 已反映共享状态变化。
3. CHANGELOG 已记录用户可见或工作流可见的变化。
4. Git diff 已审阅，工作树没有意外文件。
5. 变更已提交并推送到共享 `main`。
