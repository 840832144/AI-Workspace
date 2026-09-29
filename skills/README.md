# Game Planner Skill Tree

## 可用的 CR 专项 Skills

根发现入口：[cr-project](../.agents/skills/cr-project/SKILL.md)。唯一正文位于 `projects/cr/.agents/skills/`：

- [cr-numerical-design](../projects/cr/.agents/skills/cr-numerical-design/SKILL.md)：数值设计与复盘。
- [cr-ingest-knowledge](../projects/cr/.agents/skills/cr-ingest-knowledge/SKILL.md)：资料筛选与 Git 落库。
- [cr-govern-workbooks](../projects/cr/.agents/skills/cr-govern-workbooks/SKILL.md)：源表治理。
- [cr-svn-submit](../projects/cr/.agents/skills/cr-svn-submit/SKILL.md)：已授权的公司 SVN 配置提交。
- [cr-capture-lessons](../projects/cr/.agents/skills/cr-capture-lessons/SKILL.md)：经验沉淀。

这些正文已存在；下方 Model only 状态仅指通用分类模型，不应据此判定 CR Skill 不可用。

本目录定义 Game Planner AI Workspace 的 Skill Tree。本目录维护分类模型；已导入的 CR 专项 Skill 正文另在项目目录唯一维护，见下方路由。

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
