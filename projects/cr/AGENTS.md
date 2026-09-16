# CR 数值策划协作规则

## Workspace 与项目边界（2026-09-16）

先继承 [根 AGENTS](../../AGENTS.md) 与 [全局模板](../../bootstrap/AGENTS.md)，读取根 Task / Status / Handoff；从本目录启动也不能跳过根治理。本文及专项 Skill 中的相对路径均以 `projects/cr/` 为基准，不等于 Git 根目录。
日常设计资料和分析工具在此目录通过 Git 分支/PR 写入；切换后不再向旧 `cr_design` 或 SVN 资料镜像双写。公司 SVN 的正式配置制作与提交链路继续保留，先明确项目、URL、dev/trunk 和 revision；不得使用 101 配置替代 CR，也不得反向套用 CR 配置到 101。
日期资料包内的配置附件仅代表标注版本，不重建退役快照。`HuuugeCollector/` 是历史副本，不执行其中旧的自动同步、提交或部署指令。
User 已批准 Top Tycoon 三个工作簿及其原始样本/逐笔数据历史公开导入，范围见 [RFC-0005](../../docs/rfc/RFC-0005-CR-Subtree-Public-Migration.md)。其他敏感内容限制继续适用。
默认不做重复哈希校验。保留来源 commit 和有意义的文件 diff、结构与业务检查；原始表默认只读。

## 工作语言与脚本

- 使用中文解释业务语义，字段名和配置名保持源文件原文。
- 所有新增自动化脚本使用 Python 3，优先标准库。
- 输出数值结论时必须展示数据源、假设、公式、关键中间值、边界条件和校验结果。
- 不得把推测写成事实；缺少口径时明确标记“待确认”。

## 数据安全

- 原始文件默认只读分析，不覆盖源文件。
- 同步工具先 dry-run，只有明确要求后才执行写入。
- 不提交账号、令牌、用户隐私、线上敏感明细或本机临时文件。
- 程序配置不在本仓库保存本地快照；分析时只读目标环境的 `dev` 或 `trunk` 版本化配置，并记录环境、SVN URL 与 revision。

## 文档与代码质量

- 数值方案从 `数值策划/数值文档/00_规范/数值方案模板.md` 复制创建。
- Python 函数使用类型标注；入口使用 `if __name__ == "__main__":`。
- 在仓库内运行 Python 前设置 `PYTHONDONTWRITEBYTECODE=1`，避免产生缓存文件。
- 随脚本提供清晰命令示例，并保证无第三方依赖或明确记录依赖。
- 完成修改后运行：

```powershell
python .\数值策划\工具\build_catalog.py
python .\数值策划\工具\validate_repository.py
```

## 问题经验沉淀

- 任务中出现非日常问题、失败尝试、阻塞、用户纠正或高风险决策时，结束前必须使用 `cr-capture-lessons`。
- 无论问题最终是否解决，都把现象、证据、尝试、结果、可复用方案和后续动作写入共享经验库。
- 未解决问题必须明确标记，不得把推测、临时绕过或待授权事项写成已解决。
- 经验条目不得包含账号密码、令牌、用户隐私或线上敏感明细。

## Skill 路由

| Skill | 适用任务 |
|---|---|
| [cr-numerical-design](.agents/skills/cr-numerical-design/SKILL.md) | 数值推导、经济/成长/概率设计、评审与复盘 |
| [cr-ingest-knowledge](.agents/skills/cr-ingest-knowledge/SKILL.md) | 飞书及本地 CR 资料筛选、正文落库和分区整理 |
| [cr-govern-workbooks](.agents/skills/cr-govern-workbooks/SKILL.md) | 策划源表盘点、Sheet 分类、版本边界和导航维护 |
| [cr-svn-submit](.agents/skills/cr-svn-submit/SKILL.md) | SVN 状态检查、安全添加、自动提交和提交后核验 |
| [cr-capture-lessons](.agents/skills/cr-capture-lessons/SKILL.md) | 沉淀任务问题、失败尝试、解决方案和未解决事项，供其他策划 Agent 复用 |

TRAE_CN 应只加载与当前任务相关的 Skill；跨板块任务再组合加载，避免无关资料占用上下文。
