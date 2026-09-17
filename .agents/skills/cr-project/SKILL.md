---
name: cr-project
description: 处理 Cash Royal（CR）的数值设计、资料阅读与整理、源表治理或配置提交任务时使用；从 AI-Workspace 根目录路由到 projects/cr 的唯一专项 Skill 正文。
---

# CR 项目路由

先读仓库根 `AGENTS.md` 和 `projects/cr/AGENTS.md`，再读项目 `README.md`、`STATUS.md` 与相关 Task。以下路径相对 AI-Workspace 根目录；只加载与任务有关的正文，不复制或安装第二份。

| 任务 | 唯一正文 |
| --- | --- |
| 数值设计与复盘 | `projects/cr/.agents/skills/cr-numerical-design/SKILL.md` |
| CR 资料筛选与落库 | `projects/cr/.agents/skills/cr-ingest-knowledge/SKILL.md` |
| 策划源表治理 | `projects/cr/.agents/skills/cr-govern-workbooks/SKILL.md` |
| 公司 SVN 正式配置提交 | `projects/cr/.agents/skills/cr-svn-submit/SKILL.md` |
| 问题与用户纠正沉淀 | `projects/cr/.agents/skills/cr-capture-lessons/SKILL.md` |

正文中相对路径以 `projects/cr/` 为基准。日常 CR 资料与分析工具写入本仓库 `projects/cr/`；正式配置仍在明确核验的公司 SVN 环境处理。卡包资料入口见项目 README。CR 参数不得作为 101 配置；HuuugeCollector 目录只是历史副本。来源与切换边界见 `docs/migrations/CR-MIGRATION-20260916.md`。
