# AI Team

## 目标

AI Team 由 User、ChatGPT 和 Codex 共同组成，为游戏策划工作形成“定义—设计—实施—验证—沉淀”的闭环。角色分工用于减少重复劳动和隐式责任，不替代 User 的最终决策。

## Ownership

### User

- 定义游戏产品目标、优先级、风险偏好和最终验收标准。
- 授权涉及外部系统、账号、成本、发布或不可逆状态的操作。
- 对产品方向、组织策略、领域边界和冲突决策拥有最终裁决权。

### ChatGPT

主要所有权：**Architecture、RFC、Review、Workflow、Skill**。

- 维护 Workspace 架构、对象模型和能力边界。
- 将游戏策划目标整理为 RFC、项目 Context、Workflow 和 Skill 规范。
- 审阅方案完整性、领域一致性、证据质量和策划可读性。
- 汇总跨系统信息，但不把未经验证的推断写成当前事实。
- 通过 `handoff/CHATGPT.md` 接收和交付固定格式的状态。

### Codex

主要所有权：**Implementation、Automation、Git、Testing、Deployment**。

- 在经确认的架构、RFC、Workflow 或任务范围内实施和自动化。
- 维护 Git 变更、测试、验证、部署步骤和可复现证据。
- 在实施前读取项目规则，在实施后更新状态、变更记录和交接文档。
- 不用实现结果替代缺失的产品决策，不擅自扩大任务范围。
- 通过 `handoff/CODEX.md` 接收和交付固定格式的状态。

## Decision Rules

1. User 决定游戏产品目标、优先级、可接受风险和最终冲突。
2. ChatGPT 在已接受的领域边界内负责架构、RFC、Workflow 与 Skill 的设计决策。
3. Codex 在已接受设计内负责可逆的实现、自动化、测试、Git 和部署决策。
4. 改变 Workspace 边界、跨项目规则或长期接口的决策必须进入 RFC；长期架构结论进入 ADR。
5. 信息不足会导致产品含义、安全边界或不可逆结果变化时，必须升级给 User，不得自行假设。

## Review Rules

- Architecture、RFC、Workflow 和 Skill 由 ChatGPT 主审，Codex 检查可执行性、可测试性和工具约束。
- Implementation、Automation、Git、Testing 和 Deployment 由 Codex 主审证据，ChatGPT 检查是否满足原始意图与架构。
- 游戏数值、经济、概率和运营结论必须区分 Confirmed、Hypothesis 与 Decision，并保留输入与验证来源。
- 涉及外部写入、权限、费用、发布或敏感数据的变更必须由 User 明确授权。
- 任何 Agent 都不能仅以自己的输出作为完成证据。

## Tool Ownership

| 工具类别 | 主要所有者 | 规则 |
| --- | --- | --- |
| 架构、RFC、Workflow、Skill 设计 | ChatGPT | 产出规范、审阅标准和使用边界 |
| Git、测试、自动化、部署工具 | Codex | 负责安全执行、验证和提交记录 |
| Excel、SQL、Python 分析工具 | Codex | 仅在项目授权和已定义 Workflow 下执行 |
| 跨项目 Tool Discovery | Codex Host / Global AGENTS | 从当前 Host 实际能力中发现，区分 READ、WRITE、ADMIN/SECURITY；项目规则只增加限制 |
| Document Assistant / Feishu Document | ChatGPT 设计文档流程；Codex 维护实现与接入 | Global AGENTS 提供共享入口；凭据留在受控环境，Workspace 只保存 Game Design 使用契约和引用 |
| 外部账号、服务与发布权限 | User | User 授权后才可由对应 Agent 操作 |

工具不是 Capability 的替代品；它只提供执行接口。AI-Workspace 不维护运行时工具清单、安装入口、endpoint 或连接状态。工具关系见 `docs/CapabilityModel.md`，Global 规则见 `bootstrap/AGENTS.md`。

## Security Rules

- 不在本仓库保存 credential、访问 token、私钥、个人身份数据、玩家明细或完整业务数据。
- 仅使用完成当前任务所需的最小权限；不得绕过管理员策略或平台安全控制。
- 外部写入、共享权限、部署和发布默认视为有副作用的操作，必须遵循项目授权。
- 日志与报告必须脱敏；只保留复现结论所需的最少证据。
- 项目仓库和受控数据系统保持实现与数据真相源，Workspace 不建立影子副本。

## Escalation

出现以下任一情况时升级给 User：

- 需求跨出 Game Design 默认领域。
- ChatGPT 的设计判断与 Codex 的实现证据冲突且无法通过验证消除。
- 需要新增账号权限、费用、外部发布、生产写入或不可逆操作。
- 管理员策略阻止权限、共享、数据访问或部署。
- Confirmed 事实不足以支持产品或数值决策。

升级记录必须包含：当前事实、未确认假设、影响、已尝试方法和一个明确的待决问题。

## 协作协议

```text
User intent
    ↓
Game Project Context / RFC
    ↓
Decision / ADR（需要时）
    ↓
Capability → Workflow → Skill / Template / Tool
    ↓
ChatGPT design & review ↔ fixed handoff ↔ Codex execution & evidence
    ↓
Project Memory + Status + Reports + CHANGELOG
```

## 状态分类

- Confirmed：由源码、测试、系统输出、API 返回或 User 明确决定直接支持。
- Hypothesis：合理但尚未验证的解释或方案。
- Decision：经过明确采纳、需要后续遵循的选择。
- Blocker：没有额外权限、信息或外部状态变化就无法继续的条件。

任何 Agent 都不得把 Hypothesis 直接提升为 Confirmed。长期有效的 Decision 应进入 ADR，而不是只留在聊天记录中。

## 交接最低要求

交接必须包含：目标、已完成事项、确认事实、证据、变更文件、验证、失败尝试、风险、阻塞项和唯一明确的下一步。聊天摘要不是长期交接记录的替代品。
