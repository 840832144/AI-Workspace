# Cash Royal（CR）策划资料与分析工具

这是 AI-Workspace 的 CR 项目目录。合并并切换后，CR 日常设计、资料、Skills 与分析工具只写入 `AI-Workspace/projects/cr/`，不与旧 `cr_design` 双写。正式配置仍在公司 SVN 的明确目标环境制作、审阅与提交。

## 阅读顺序

1. [全局稳定规则模板](../../bootstrap/AGENTS.md)与[Workspace 规则](../../AGENTS.md)。
2. [项目规则](AGENTS.md)、[当前状态](STATUS.md)、[工作流](WORKFLOW.md)、相关根 Task / Handoff。
3. [项目上下文](CONTEXT.md)、[项目记忆](MEMORY.md)与本次资料入口。
4. 按 [Skill 路由](AGENTS.md#skill-路由)阅读唯一正文；无需复制或安装第二份。

## 只需克隆 AI-Workspace

迁移 Review 使用 `codex/cr-subtree-migration`，合并后日常使用 `main`。从 Workspace 根执行：

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
python projects/cr/数值策划/工具/build_catalog.py
python projects/cr/数值策划/工具/validate_repository.py
```

或进入 CR 目录执行：

```powershell
cd projects/cr
python 数值策划/工具/build_catalog.py
python 数值策划/工具/validate_repository.py
```

工具从脚本位置定位 CR 项目，不依赖终端当前目录；仅需 Python 3 标准库。构建只写派生目录，原始源表只读。默认不计算或核对文件哈希；重点检查结构、读取结果和实际内容。首次阅读不需要本机源表目录、SVN 或在线服务。

## 资料与工具

- [卡包与卡片价值分析资料](数值策划/数值文档/03_分析与复盘/CR卡包价值分析资料_20260915/README.md)：含 trunk/dev r6880 日期附件、文本提取与现有检查脚本。它们是该次研究证据，不代表当前环境配置，也不能作为 101 的计算输入。
- [数值文档](数值策划/数值文档/README.md)、[知识库](数值策划/知识库/README.md)、[使用说明](使用说明.md)、[工具说明](数值策划/工具/README.md)。
- `数值策划/数据源/策划源表/`：14 份纳管源表，默认只读。
- `.agents/skills/`：五个专项 Skill 的唯一正文；根目录只保留路由。
- `HuuugeCollector/`：历史副本，当前开发与部署真相源见 [Huuuge 项目](../huuuge-android-research/README.md)。

## 写入与公开范围

按根分配器登记 Task，隔离分支修改，验收后提交 PR。资料同步先 dry-run，只有对应任务明确授权才使用 `--apply`；公司 SVN 提交另按明确项目、URL、环境和 revision 执行。本迁移不执行这些操作。

AI-Workspace 保持 public。User 已批准此次 CR 内容，以及 Top Tycoon 三个工作簿中的原始 Spin、金币前后值和逐笔记录连同历史入库；这不授权其他凭据、账号、私有 Registry、完整响应或敏感日志。迁移不扩大飞书或其他分享权限。

保留 CR 内部结构；不重建已退役的 `数值策划/数据源/程序配置导出快照`。旧绝对路径、SVN revision 与文档日期保留为历史来源，通过[迁移报告](../../docs/migrations/CR-MIGRATION-20260916.md)映射到现路径。
