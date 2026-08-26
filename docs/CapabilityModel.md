# Capability Model

Capability Model 定义 Game Planner AI Workspace 如何从“策划结果”分解到“可复用方法与执行接口”。本阶段只建立概念模型，不实现注册器、调度器或运行时。

## 五层定义

| 概念 | 回答的问题 | 定义 | 不是什么 |
| --- | --- | --- | --- |
| Capability | 能完成什么？ | 面向游戏策划结果的稳定能力契约 | 具体脚本、单次提示词或工具品牌 |
| Skill | 如何复用方法？ | 可独立审阅、验证和版本化的方法单元 | 跨步骤项目计划或无边界知识集合 |
| Workflow | 如何协同完成？ | 将 Agent、Skill、Template、Tool 按顺序和关卡编排 | 单个 Skill 或执行工具 |
| Template | 输入输出长什么样？ | Context、分析表、报告、决策记录等结构契约 | 执行逻辑或 Capability 本身 |
| Tool | 通过什么执行？ | 对计算、查询、文档或版本系统的受控接口 | 策划判断或可交付结果 |

## 关系

```mermaid
flowchart LR
    C[Capability<br/>结果契约] -->|decomposes into| S[Skill<br/>复用方法]
    W[Workflow<br/>过程编排] -->|selects and orders| S
    W -->|applies| T[Template<br/>结构契约]
    S -->|operates through| O[Tool<br/>执行接口]
    S -->|reads or produces| T
```

关系规则：

1. 一个 Capability 可以由多个 Skill 共同实现，同一 Skill 也可以支持多个 Capability。
2. Workflow 面向具体目标和项目情境选择 Skill；它负责顺序、责任、审阅关卡、失败处理和交接。
3. Template 约束信息结构，不负责执行；Skill 或 Workflow 可以读取和产出 Template 实例。
4. Tool 可以被替换，只要 Skill 的输入、输出、安全和验证契约不变。
5. Agent 通过 Workflow 获得任务，通过角色所有权和权限规则使用 Tool。

## 游戏策划示例（仅模型）

以“评估 Battle Pass 经济设计”为例：

- Capability：评估一套 Battle Pass 是否满足成长、付费与奖励目标。
- Skills：Battle Pass、Economy Design、Excel、SQL、Report Writing。
- Workflow：收集 Context → 验证数据 → 建模 → 评审假设 → 形成报告 → 更新 Status。
- Templates：项目 Context、分析记录、策划报告、决策记录。
- Tools：Excel、SQL、Python、Feishu Document。

该示例只说明对象如何组合，不表示相关 Skill、连接器或自动化已经实现。

## 设计检查

新增模型项时应先回答：

- 它交付的是结果、方法、过程、结构还是执行接口？
- 是否属于 Game Design 默认领域？
- 是否有明确输入、输出、安全边界和验证方式？
- 是否与现有 Capability 或 Skill 重复？
- Tool 被替换后，上层契约是否仍然成立？
