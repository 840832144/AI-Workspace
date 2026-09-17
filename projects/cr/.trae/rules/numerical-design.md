# CR 数值策划项目规则

先读取 `../../AGENTS.md` 和 `../../bootstrap/AGENTS.md`，然后继承本项目 `AGENTS.md`。以下“根目录”均指 CR 项目目录 `projects/cr/`。日常资料提交 Git 分支/PR；公司 SVN 提交需单独明确授权与目标。新增问题经验使用 `cr-capture-lessons`；HuuugeCollector 仅历史参考。

你正在处理 Cash Royal 数值策划资源库。

1. 先阅读根目录 `README.md`、`AGENTS.md` 和相关目录 README。
2. 按任务加载 `.agents/skills` 中的 Skill：
   - 数值设计、经济、成长、奖励、概率和玩法推导：`cr-numerical-design`
   - 飞书/本地资料筛选与落库：`cr-ingest-knowledge`
   - 策划源表入口、版本和历史页整理：`cr-govern-workbooks`
   - 程序配置核对：直接只读目标 `dev` 或 `trunk`，记录 SVN URL 与 revision
   - SVN 检查、添加、提交和提交后核验：`cr-svn-submit`
3. 任何结论都必须能从“数据源 → 假设 → 公式/代码 → 中间结果 → 校验 → 结论”追溯。
4. Python 3 是唯一新增脚本语言；优先标准库，函数添加类型标注和业务注释。
5. 原始 Excel 不直接改写；如需产出修改版，写入独立输出路径并保留原文件。
6. 不在资源库维护程序配置本地快照；必须直接读取目标 `dev` 或 `trunk`，且不得在分析流程中修改配置。
7. 修改完成后运行目录构建和仓库校验工具；报告失败项，不得隐藏异常。
8. SVN 提交先运行 `svn_submit.py` 演练；用户明确要求提交后才使用 `--execute`。
