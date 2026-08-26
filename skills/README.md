# Game Planner Skill Tree

本目录定义 Game Planner AI Workspace 的 Skill Tree。当前只建立分类、边界和未来登记入口，不包含可执行 Skill、提示词、脚本或工具配置。

## Skill 分类

| 分类 | 目录 | 规划范围 |
| --- | --- | --- |
| Game Analysis | `game-analysis/` | 核心循环、系统结构、玩家目标、竞品与体验分析 |
| Slot Analysis | `slot-analysis/` | Slot 机制、数学结构、特性与体验分析 |
| Battle Pass | `battle-pass/` | 赛季通行证结构、进度、奖励和付费设计 |
| Economy Design | `economy-design/` | 货币、产消、成长、定价与经济平衡 |
| Lottery | `lottery/` | 抽奖、卡池、概率、保底和奖励期望分析 |
| Task System | `task-system/` | 任务结构、条件、奖励、节奏与生命周期 |
| Excel | `excel/` | 策划表格建模、校验和结构化分析方法 |
| SQL | `sql/` | 面向策划问题的数据提取与口径验证方法 |
| Python | `python/` | 可复现分析、模拟和数据处理方法 |
| Report Writing | `report-writing/` | 策划分析、评审和决策报告结构 |
| Feishu Document | `feishu-document/` | 飞书文档创建、读取、维护与交付流程规范 |

## 分层规则

- 领域 Skill：Game Analysis、Slot Analysis、Battle Pass、Economy Design、Lottery、Task System。
- 分析工具 Skill：Excel、SQL、Python。
- 交付 Skill：Report Writing、Feishu Document。
- Skill 是实现 Capability 的方法，不等于 Workflow 或 Tool；定义见 `docs/CapabilityModel.md`。
- 新增具体 Skill 前必须遵循 `docs/rfc/RFC-0003-AI-Skill-System.md`，并定义输入、输出、安全、验证与 Ownership。

所有分类当前状态均为 **Model only / Not implemented**。
