# Contributing

## 适用范围

所有 User、ChatGPT、Codex 对本仓库的修改都必须遵循本规范。

## 开始前

1. 使用安全方式同步 `main`，不得 force-push 或重写他人历史。
2. 阅读 `AI_TEAM.md`、`ARCHITECTURE.md` 和相关 handoff。
3. 确认修改属于治理、协作、标准、模板或项目控制面，而不是业务实现。
4. 检查相关 RFC、ADR、项目 Status 和 CHANGELOG，避免重复或冲突。

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

## 项目记录

每个 `projects/<project>/` 必须包含：

- `CONTEXT.md`
- `MEMORY.md`
- `WORKFLOW.md`
- `STATUS.md`

项目实现细节应以链接或 commit 引用方式指向业务仓库，不复制源代码和敏感数据。

## 文档质量

- 首段说明目的和受众。
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
