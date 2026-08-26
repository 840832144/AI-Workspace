# AI Team

## 目标

AI Team 由 User、ChatGPT 和 Codex 共同组成。目标不是让多个 Agent 重复劳动，而是让规划、执行、验证和长期记忆形成闭环。

## 角色

### User

- 定义目标、优先级、风险偏好和最终验收标准。
- 授权涉及外部系统、账号、成本或不可逆状态的操作。
- 对产品方向、组织策略和冲突决策拥有最终裁决权。

### ChatGPT

- 负责需求澄清、跨项目规划、研究、方案比较和面向人的说明。
- 将模糊目标整理为 RFC、项目 Context 和可执行工作流。
- 汇总跨系统信息，但不把未经验证的推断写成当前事实。
- 通过 `handoff/CHATGPT.md` 接收和交付固定格式的状态。

### Codex

- 负责仓库内实施、自动化、测试、验证、提交和可复现证据。
- 在实施前读取项目规则，在实施后更新状态、变更记录和交接文档。
- 不擅自扩大任务范围，不用实现结果替代缺失的产品决策。
- 通过 `handoff/CODEX.md` 接收和交付固定格式的状态。

## 协作协议

```text
User intent
    ↓
Context / RFC
    ↓
Decision / ADR（需要时）
    ↓
Workflow + project Status
    ↓
ChatGPT planning ↔ fixed handoff ↔ Codex execution
    ↓
Evidence + CHANGELOG + next action
```

## 状态分类

- Confirmed：由源码、测试、系统输出、API 返回或用户明确决定直接支持。
- Hypothesis：合理但尚未验证的解释或方案。
- Decision：经过明确采纳、需要后续遵循的选择。
- Blocker：没有额外权限、信息或外部状态变化就无法继续的条件。

任何 Agent 都不得把 Hypothesis 直接提升为 Confirmed。长期有效的 Decision 应进入 ADR，而不是只留在聊天记录中。

## 交接最低要求

交接必须包含：目标、已完成事项、确认事实、证据、变更文件、验证、失败尝试、阻塞项和唯一明确的下一步。聊天摘要不是长期交接记录的替代品。
