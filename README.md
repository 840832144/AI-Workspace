# Cash Royal 数值策划资源库

本仓库用于沉淀 Cash Royal（CR）项目的数值源表、推导工具、设计文档和 AI 协作知识。所有可交付结论都应做到：来源可追溯、假设可见、公式可复算、脚本可复跑、结果可复核。

## 目录

```text
CR_design/
├─ AGENTS.md                         # AI/协作者的项目级约束
├─ .agents/skills/                   # TRAE/Agent Skills
├─ .trae/rules/                      # TRAE 项目规则
└─ 数值策划/
   ├─ 数值文档/                      # 方案、规范、系统设计与复盘
   ├─ 工具/                          # Python 3 同步、索引和校验工具
   ├─ 数据源/                        # 原始策划表与程序配置快照
   └─ 知识库/                        # AI 可检索的目录和来源说明
```

## 首次使用

在仓库根目录执行：

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:CR_DESIGNER_WORKBOOKS_DIR = "本机的 CR 策划源表目录"
$env:CR_EXPORTED_CONFIGS_DIR = "本机的程序配置导出目录"
python .\数值策划\工具\sync_data_sources.py
python .\数值策划\工具\sync_data_sources.py --apply
python .\数值策划\工具\build_catalog.py
python .\数值策划\工具\validate_repository.py
```

第一条命令只预览变更；确认后才使用 `--apply`。仓库仅保存环境变量名，不保存任何策划的电脑路径。数据源约定维护在 `数值策划/工具/config/data_sources.json`。

## 协作约定

1. 原始表放入“数据源”，不要直接在索引文件中维护业务数据。
2. 推导过程使用 Python 3；关键参数不得散落为无法解释的“魔法数字”。
3. 数值方案使用 `数值文档/00_规范/数值方案模板.md`，同时给出输入、公式、中间结果、边界校验和最终结论。
4. 程序导出 Excel 是快照，不是权威编辑源；变更应回到原配置流程完成。
5. 禁止提交 Excel 临时文件（`~$*`）、缓存、运行日志和本机密钥。

## 推荐入口

- 项目使用说明：[使用说明](使用说明.md)
- 业务方案：`数值策划/数值文档/README.md`
- 策划源表阅读顺序：`数值策划/知识库/策划源表导航.xlsx`
- Excel 全量结构检索：`数值策划/知识库/工作簿目录.csv`
- 飞书原文归档：`数值策划/数值文档/04_飞书归档`
- TRAE_CN Skills：`.agents/skills`

`数值策划/数据源/程序配置导出快照` 为只读区域，不接受人工整理或直接修改。

## TRAE_CN Skill

项目内置 5 个可复用 Skill，分别覆盖数值推导、资料落库、源表治理、配置快照审计和 SVN 安全提交。
TRAE_CN 打开整个仓库后，根据任务读取对应 `SKILL.md`；详细规则按需从各 Skill 的
`references` 目录加载。
