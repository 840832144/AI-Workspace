# CR 迁移清单与验收

- 日期：2026-09-16
- Task：[TASK-0032](../../tasks/TASK-0032-CR-SUBTREE-PUBLIC-MIGRATION.md)
- 方案：[RFC-0005](../rfc/RFC-0005-CR-Subtree-Public-Migration.md)；决策：[ADR-0008](../adr/ADR-0008-CR-Single-Repository.md)
- 分支：`codex/cr-subtree-migration`；独立 linked worktree。
- 状态：全新克隆验收通过，候选等待 PR Review；尚未合并或切换。
- Subagents: none

## 来源与历史保留

| 对象 | SHA / 结果 |
| --- | --- |
| AI-Workspace 原 main | `5b5414cf7ecb9df3c06d23b3325cfb90b4fa2d7e` |
| cr_design 来源 main | `1409737648b15f602586b79ade7e0c3e7a3813a0` |
| Task / RFC 首次提交 | `52e3279e613858a0e691700bb5188b0a98cb8bc0`，完整计划先于导入 |
| User 后续公开范围确认 | `68b94b6c6ef1a2110dfe14ac4ecbb81845025408` |
| 原样 subtree 导入 | `fe07557ce5052da6a0eaaaaa1207b416ac081474` |
| 导入父提交 | 第一父为上述授权提交，第二父为 CR 来源 main |
| 原样一致性 | `git diff <CR来源SHA> <导入SHA>:projects/cr` 为空；276 个路径/模式与内容一致 |
| 历史保留 | `git merge-base --is-ancestor <CR来源SHA> <导入SHA>` 成功，CR main 的13个原提交成为祖先，无 squash、无重写 |
| 非 main 分支 | 全 refs 的16个 CR 提交均已备份/审查；另外3个非 main 提交不隐式合入 |

两仓全部已获取 refs 已分别创建受控本地 bundle，verify 后恢复为独立 bare 仓库，full fsck 均通过。备份目录 ACL 限当前用户与 SYSTEM，备份、扫描明细、token 与本机 Registry 不入 Git。没有为本次补做或重复文件哈希校验。

## 公开决定与审查结果

AI-Workspace 在迁移期间及合并后保持 public，后续可见性由 User 自行调整；cr_design 保持原 private 状态。本任务不修改任一仓库可见性、协作者、飞书或其他分享权限。

首次审查暂停后，User 于 2026-09-16 明确允许下列三个工作簿中的原始 Spin 样本、金币前后值、逐笔资源记录及其 Git 历史公开入库。按最新授权原样导入，不清洗其历史，也不再次作为阻塞。该授权不放宽其他 Secret、账号、私有 Registry、完整响应、未批准采集数据或敏感日志的边界。

三文件原路径前缀：`数值策划/数值文档/03_分析与复盘/Top_Tycoon素材/`；均自原初始导入 `2285678335321217143b58aaf31d28a2f098dac5` 可达：

- `Top_Tycoon原始事件账.xlsx`：SpinLog 与 ResourceLedger。
- `Top_Tycoon数值模型.xlsx`：Spin 样本。
- `Top_Tycoon数值模型_v0.2.xlsx`：Spin、建造样本及分段记录。

完整可达图审查覆盖：CR 436 个对象（16 commit / 121 tree / 299 blob），AI-Workspace 2422 个对象（197 commit / 1040 tree / 1185 blob）。包括已删除历史文件、Git 元数据、文本、53 个 Office 压缩对象及1038个成员；所有对象可读。22张内嵌图片已逐张查看，属于游戏设计、商城和表格参考，未确认凭据或账号登录信息；无其他嵌入附件。

候选命中经语义核查：Collector 的 device_id 是代码字段；SQL 中的 uid 是查询字段；三份 JSON/HTML 逐步余额属于仿真输出；AI 的安全测试字符串属于合成样例，公共 Task Registry 不是私有 Registry。除已明确授权的三份工作簿外，未确认其他禁止公开内容。扫描是本次已获取全部可达内容的审查结果，不声称对未来新增文件自动授权。

## 文件与入口映射

[完整原样导入文件清单](CR-FILE-MAP-20260916.csv)记录276个纳管文件的原路径、目标路径与模式；未复制本机未纳管产物。统一映射：`cr_design/<path>` → `AI-Workspace/projects/cr/<path>`。

| 原位置 / 责任 | 当前候选位置 / 规则 |
| --- | --- |
| CR AGENTS / README | `projects/cr/`，继承根规则与全局模板 |
| `.agents/skills/` | `projects/cr/.agents/skills/` 是五个正文唯一位置；根 `.agents/skills/cr-project/SKILL.md` 仅路由 |
| 数值文档、数据源、知识库、工具 | 保留原内部结构，加 `projects/cr/` 前缀 |
| CR 卡包资料 | `projects/cr/数值策划/数值文档/03_分析与复盘/CR卡包价值分析资料_20260915/`，trunk/dev r6880 附件为历史证据 |
| HuuugeCollector | 同前缀下历史副本；当前实现以 Huuuge 项目控制面所指外部仓库为准 |
| 公司 SVN | 正式配置制作与提交流程保留；明确项目、URL、环境、revision 与策略后操作 |
| 101 | 只引用 CR 方法；配置、代码和结果仍在101自己的受控位置 |

旧文档中的 `CR_design`、`cr_design`、`D:\cr_design` 和旧 SVN revision 保留当时 provenance。当前文档链接使用新前缀；历史 Git 查看仍用原来源 SHA 的原路径（如 `git show <CR来源SHA>:README.md`），不能用新前缀查询旧提交。既有历史报告不批量重写日期或结论。

适配覆盖根 AGENTS / README / AI_TEAM / ARCHITECTURE / CONTRIBUTING、项目七类入口、四份 ChatGPT 启动文件、ChatGPT/Codex/TRAE 路由、Skill 索引、Context 生成器与同步路径。Source Pack 只增加 CR CONTEXT 摘要；不递归收录 CR 正文/工作簿，也未新增 Live Context 发布项或读取私有 Registry。Host-local Context 的既有内容指纹机制保留，不把它扩展为迁移文件哈希验收。

目录工具默认跳过文件哈希，仍读取工作簿结构；卡包检查直接比较 Excel 与 CSV 内容及业务引用。同步目标使用便携路径并以 CR 项目目录解析；SVN 提交工具要求显式 `--root`，防止误把 Git 根当 SVN 工作副本。未修改源表、SVN 策略或 Collector 运行代码。

## 验收结果

验收代码提交：`51a8287e800a2e797e536c00d5297fbb615ee14f`（适配主体 `f18a0f11d01aaf530390378a21ef0dbc8981a364`）。在全新目录执行 `git clone --no-local --single-branch --branch codex/cr-subtree-migration <本机AI候选仓库> <全新目录>`；没有克隆 CR、没有对象 alternates，也没有使用原 SVN。之后仅从同一 AI-Workspace 获取 main 引用，供既有治理校验使用。

| 检查 | 结果 |
| --- | --- |
| 根与 CR 子目录阅读入口 | 两处均能读取全局模板、根/项目 AGENTS、项目状态与入口；五个 Skill 唯一正文可达 |
| 原始导入文件 | 276 个路径均保留；无 submodule、嵌套 Git/SVN 纳管元数据；不重建退役快照 |
| `build_catalog.py` | 根与 CR 两处运行均为14工作簿、0读取异常；默认 hashes_included=false |
| `validate_repository.py` | 根与 CR 两处运行均为0错误、0警告；未启用哈希选项 |
| 卡包 `tools/check_bundle.py` | 36份 XLSX、845935个 CSV 单元格一致；trunk/dev 各4290状态检查，无无效权重组或声明张数不匹配 |
| 原有卡包风险 | trunk/dev 各102个候选容量不足状态为来源既有研究结果，不是迁移新增，也不是玩家概率；未修改配置或代替估值模拟 |
| Memory / Context / Task 现有测试 | 45 + 13 + 23 = 81 项通过，含新 Context 入口 allowlist 检查；测试使用隔离合成仓库，不连接真实服务 |
| Context 生成 | 从 CR 调用根 memory_cli refresh 成功：83来源、0敏感模式问题、0断链、private_repositories=not read；只增加入口摘要，仍需人工上传，本任务未上传 |
| Context doctor / Task Registry | doctor ok；15 canonical、0 collision、valid；6条原有 grandfather 提示保留 |
| 资料同步路径 | CR 目标解析正确，越出项目到101的测试路径被拒绝；只加载配置，不执行 apply 或来源同步 |
| SVN 参数边界 | 未传 --root 即 argparse 拒绝，未调用 SVN；现有策略未放宽 |
| Skill / 文档 / diff | 根路由通过 quick_validate；60份适配 Markdown 的链接检查无断链；diff --check 通过 |
| 原始源表 | 相对原样导入及验收运行后的 Git diff 中，所有 XLSX/XLS/XLSM 均无变更；无额外文件哈希复验 |

验收命令（在新克隆内，先设置 `PYTHONDONTWRITEBYTECODE=1`）：

```powershell
# Workspace 根
git fetch origin main:refs/remotes/origin/main
python projects/cr/数值策划/工具/build_catalog.py
python projects/cr/数值策划/工具/validate_repository.py
python projects/cr/数值策划/数值文档/03_分析与复盘/CR卡包价值分析资料_20260915/tools/check_bundle.py
python -m unittest discover -s tools/memory/tests
python -m unittest discover -s tools/context/tests
python -m unittest discover -s tools/tasks/tests
python tools/tasks/task_cli.py validate
# CR 子目录
cd projects/cr
python 数值策划/工具/build_catalog.py
python 数值策划/工具/validate_repository.py
python ../../tools/memory/memory_cli.py refresh
```

构建只改三个派生目录文件；Context refresh 只改五个既有治理派生文件/受管段。验收目录保留这些可解释差异，未把测试临时产物提交。没有修改原始源表、执行 sync --apply、SVN 提交、真实采集、部署或云端发布。

失败与处理：单分支克隆最初缺 origin/main，既有 Task 校验按设计拒绝；从同一个 AI-Workspace fetch main 后通过，已补入新人说明，未降低治理要求。Skill 工具最初受 Windows 默认 GBK 解码影响，改用 `python -X utf8` 后通过。后续仅修订说明、状态和生成物，未改变已验收的业务工具。


## 切换、并发与未完成项

本候选尚未合并，不能宣称正式切换。Review 使用候选分支；User 确认合并并切换后，唯一日常 Git 入口为 AI-Workspace，CR 资料和工具只写 `projects/cr/`。旧 CR Git 与 SVN 资料镜像不再双写；公司 SVN 正式配置不是资料镜像，继续原流程。

已从最新 main 完成防重与 remote-CAS 正式分配，TASK-0032 reservation 保持 pending-main，只有 canonical 合入 main 后才能 finalize，不提前 release。开放 PR #2 EarlyMeeting / #4 Huuuge 及 TASK-0030 Pop Slots 具有共享入口潜在冲突；本分支不覆盖它们，合并前再次核对并发与来源增量。

仍待完成：PR Review、User 确认最终合并与切换、canonical 进入 main 后 finalize、旧库是否归档。发布前再次 fetch：两仓 main SHA 与表中基线一致；AI-Workspace PUBLIC、cr_design PRIVATE；开放 PR 仍为 #2 和 #4。Context provider unavailable 不影响离线迁移；未发布云文档、未上传 Project Sources，也未扩大任何外部权限。

## 回滚步骤

1. 合并前：保留候选 PR / 分支，不切换日常入口即可保持原状；原两仓和受控 bundle 完整保留。不要删除旧库、强推 main 或释放已形成 canonical 的 reservation。
2. 若需本机恢复：在全新空目录执行 `git clone --mirror <受控bundle绝对路径> <恢复目录>`，用原来源 SHA 创建工作分支；不覆盖已有 checkout。两份 bundle 已通过恢复验证。
3. 合并后需经 User 授权，在最新 AI-Workspace main 创建回滚分支，确认 PR merge commit 的第一父为原目标主线，再 `git revert -m 1 <PR merge commit>`。检查导入目录、根入口、路由与生成物一起回退，验收后通过 PR 合并；不改写共享历史。
4. Revert 无法撤回已公开历史。若后续发现凭据，先由所有者处置凭据，再单独评审历史处理；本次三个明确批准文件无需清洗。
5. 恢复旧 Git 日常入口前，先冻结两端资料写入，核对迁移后的新增内容并由 User 指定去向与切换时点，防止双写丢失。公司 SVN 正式配置不受本迁移回滚影响。

PR 合并必须选择 **Create a merge commit**，禁止 Squash and merge / Rebase and merge；否则无法保留 CR 原提交为主线祖先。最终合并和旧库归档不属于本次自动执行范围。
