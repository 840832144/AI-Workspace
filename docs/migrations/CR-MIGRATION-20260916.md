# CR 迁移审查记录

## 2026-09-16 后续决定：恢复原历史迁移

User 已明确允许下文指出的三份 Top Tycoon 工作簿及其原始 Spin、金币前后值和逐笔资源记录入库；不清洗相关文件或历史，不再以此阻塞。User 同时要求省去多余哈希校验，后续只使用直接 diff、Git 祖先关系和必要功能检查。当前恢复 TASK-0032；下面暂停与清洗提案保留为前一阶段审计记录，不再是当前待决条件。

## 前一阶段审查（已被上述授权更新）

- 日期：2026-09-16
- 状态：Blocked before import / Not published / No cutover
- Task：[TASK-0032](../../tasks/TASK-0032-CR-SUBTREE-PUBLIC-MIGRATION.md)
- 方案：[RFC-0005](../rfc/RFC-0005-CR-Subtree-Public-Migration.md)
- Subagents: none

本次已完成两仓安全同步、正式分配、Task/RFC Git 提交和受控本地备份。内容审查发现 CR 已纳管的原始记录与逐笔资源数据，触发 User 明确要求的暂停发布条件。尚未执行 subtree，未推送候选分支、未创建迁移 PR，未切换日常入口。来源 private、目标 public 本身不是阻断原因。

## 来源与备份

| 对象 | 固定 SHA / 结果 |
| --- | --- |
| AI-Workspace main | `5b5414cf7ecb9df3c06d23b3325cfb90b4fa2d7e` |
| cr_design main | `1409737648b15f602586b79ade7e0c3e7a3813a0` |
| Task/RFC 首次提交 | `52e3279e613858a0e691700bb5188b0a98cb8bc0` |
| 迁移分支 | `codex/cr-subtree-migration`，独立非 main linked worktree |
| 正式分配 | remote-CAS 返回 TASK-0032，pending-main；token 只保留本地 |
| 备份方式 | 两仓 `git bundle create --all`，包含全部已获取 refs 的可达图 |
| 备份验收 | 两个 bundle verify 均通过；各从 bundle 恢复为独立 bare 仓库，`git fsck --full` 均通过 |
| 备份隔离 | 当前用户及 SYSTEM 专用本地目录；备份、manifest、扫描明细不进 Git |

AI-Workspace 当前仍 public，cr_design 当前仍 private。本 Task 未改变可见性或任何协作者、飞书及外部共享权限。原 SVN 副本、本机未纳管文件与其他任务 worktree 保持原状。

## 已确认的禁止发布内容

以下三个文件均在当前 CR main，且自初始导入提交 `2285678335321217143b58aaf31d28a2f098dac5` 起进入可达历史。只记录工作表名称、记录数量和对象位置，不输出账号、金币值、逐笔明细或原始响应。

路径公共前缀：`数值策划/数值文档/03_分析与复盘/Top_Tycoon素材/`。

| 文件 | 已确认内容 | Git blob |
| --- | --- | --- |
| `Top_Tycoon原始事件账.xlsx` | `SpinLog` 140 条记录；金币前值 138 个数值单元格、后值 139 个；`ResourceLedger` 315 条资源变化记录 | `2735611640b022f56997cdc9a664ad88facc9e32` |
| `Top_Tycoon数值模型.xlsx` | `Spin样本` 140 条记录，包含 `coins_before / coins_after / coin_gain_observed` | `9a49c795feec0e3c1fb05fa2da7f179d094906be` |
| `Top_Tycoon数值模型_v0.2.xlsx` | `Spin样本` 140 条；`建造样本` 48 条，包含 `coin_before / coin_after / coin_cost`；另有 391 条分段记录 | `d8c7fdeac6e3653a2be8d41f9d124979b5c3319b` |

检查直接读取 Git 已纳管工作簿的 Office XML，不运行游戏、不修改工作簿。工作表确有数值和数据行，因此不是仅凭文件名或空表头判断。两份模型包含原始样本副本，不能只删除“原始事件账”文件就认为安全。

## 历史保留与暂停依据

CR 当前 main 有 13 个可达提交、276 个文件，完整现存 refs 合计 16 个提交；目标 AI-Workspace 全 refs 有 197 个提交。全部源文件路径已生成一一对应清单，目标前缀统一为 `projects/cr/`。当前源树没有嵌套 `.git` / `.svn` 或 mode `160000` submodule。

这些受影响 blob 处于待导入 main 的祖先图内。无 `--squash` 的 subtree 会公开其可达历史；在适配提交删除文件，或者日后 revert，都不会让旧对象退出可达图。因此尚不能同时做到“保留原始 SHA 历史”与“禁止公开这些逐笔数据”。本次未静默改变原历史，也未用 squash 或单快照替代 User 要求。

本地扫描已遍历 CR 全 refs 的 436 个对象（16 commit / 121 tree / 299 blob），检查 53 个 Office 压缩对象、1038 个成员；AI-Workspace 全 refs 为 2422 个对象（197 commit / 1040 tree / 1185 blob）。检查覆盖文本、Git 元数据、已删除历史 blob、文件路径及 Office XML，全部对象已可读取。非文本嵌入图片尚未逐张进行视觉审查；这也是清洗后发布复验范围，不能声称已穷尽所有敏感内容。

正则命中仅作为候选，AI-Workspace 的合成安全测试字符串、代码字段与 Registry 文件名不直接视为泄漏。CR 的三份仿真 JSON/HTML 含逐步余额字段，需核对合成来源与公开范围，不能直接当作真实采集或自动放行；两份 SQL 查询记录与 Collector 字段匹配也须语义核查。已确认的发布阻断证据是上述三个工作簿。扫描明细只在本机，安全 gate 保持未通过。

## 建议处理方案（待 User 决定）

建议保留两仓原图与受控备份，仅在新的隔离 CR 副本清洗受影响文件的全部可达历史。先移除上述三个工作簿的原始样本/逐笔数据，核验派生文件、HTML 内嵌数据、Office 嵌入附件与历史版本是否重复携带；可复用模型只保留经审核的聚合、公式和明确标注的合成示例。原始策划源表及原两个仓库不修改、不强推。

清洗会改变受影响提交及后继提交的 SHA。应生成“原 SHA → 清洗后 SHA”的完整映射，保留父子关系和来源说明；从清洗副本再以非 squash subtree 原样导入，单独提交适配。映射中的原 SHA 只能作为 provenance 文本，不能通过 parent、tag 或 remote ref 把旧敏感对象重新纳入公共候选图。必须重新执行全图审查与全新单仓克隆验收。

需要 User 明确接受的变化：允许导入**清洗后的历史**，原历史 SHA 仅在本地备份和映射保留；不再要求原始 CR 提交对象直接在公共候选中可达。若必须保持原 SHA 可达，则继续暂停迁移，不能以放宽敏感数据禁入条件处理。

## 入口与文件映射

目前尚未切换。旧 CR Git 仓库继续是现行 Git 参考入口，公司 SVN 正式配置与提交流程不变；候选分支不作为日常写入口，避免在两个位置并行更新。

| 原位置 | 审查通过并合并后的唯一位置 |
| --- | --- |
| `cr_design/AGENTS.md` | `AI-Workspace/projects/cr/AGENTS.md`，同时继承根规则 |
| `cr_design/.agents/skills/` | `AI-Workspace/projects/cr/.agents/skills/`，正文保持唯一，根/其他 Agent 入口仅路由 |
| `cr_design/数值策划/` | `AI-Workspace/projects/cr/数值策划/`，策划资料与工具在此写入 |
| CR 卡包分析资料目录 | 原内部结构加 `projects/cr/` 前缀；dev/trunk 分开，20260915 附件是固定版本证据，不代表当前配置 |
| `cr_design/HuuugeCollector/` | 相同前缀下的历史副本；不成为自动开发、采集或部署权威 |
| 公司 SVN 配置 | 保持既有 SVN 权威流程，不进入新的程序配置快照结构 |
| 101 分析 | 仍在101自己的受控项目，只引用 CR 方法；不复用 CR 参数作为101输入 |

四启动文件实际为 `00_CORE_RULES.md`、`01_SYSTEM_CONTEXT.md`、`02_CURRENT_STATE.md`、`03_NEW_CHAT_BOOTSTRAP.md`。根/项目 AGENTS、README、架构、ChatGPT/Codex/TRAE、Skill 路由、Context/Source Pack 和资料同步路径的修改清单已在 RFC 登记，等待安全 gate 后实施。

## 验证与未完成项

| 检查 | 结果 |
| --- | --- |
| 最新 main、并发范围与正式分配 | 通过；无同目标 active Task，保护现有开放 PR 范围 |
| 初始 Task Registry | 14 canonical / 0 collision / valid |
| 登记后 Task Registry | 15 canonical / 0 collision / valid；6 条既有 grandfather 警告 |
| Task 状态兼容 | canonical `Status: Review`（审查清洗决定）；`Execution status: Blocked before import` 明确执行暂停。现有 allocator 不接受 `Blocked` 为主状态，已按既有枚举修正，未修改治理工具 |
| 治理记录校验 | Task Registry 15 canonical / 0 collision / valid；Context doctor `ok=true`；9 份 Markdown 的 28 个本地链接全部可达；10 个变更文件的敏感模式检查无命中；`git diff --check` 通过 |
| Workspace Sync | ON_DEMAND / provider unavailable / stale 6 / conflicts 0；不作云端同步成功声明 |
| 本地 bundle、恢复与全图 fsck | 两仓通过 |
| 源树纳管范围 | 276 文件；无嵌套 Git/SVN 元数据或 submodule |
| 内容与完整历史发布 gate | 未通过，已确认三个含原始记录的工作簿 |
| subtree / 原样文件一致性 / 历史祖先可达性 | 未执行，待清洗历史决定与新一轮安全检查 |
| 适配与新克隆的根/CR 两入口验收 | 未执行，不能用原 CR checkout 的可用性替代 |
| `build_catalog.py` / `validate_repository.py` / 卡包相关校验 | 未在迁移候选中执行，不声明迁移验收通过 |
| 原始源表 / 同步 apply / SVN 提交 / 真实采集 / 部署 | 均未修改或执行 |
| 迁移分支推送 / PR / merge / 旧库归档 | 均未执行；仅 allocator 创建了已授权的最小 reservation ref |

收尾只读复核两仓远端 main SHA 未变化，AI-Workspace 为 PUBLIC、cr_design 为 PRIVATE，迁移分支尚不存在于远端。扫描过程中初版对大量仿真余额命中逐一计算行号导致耗时，已只终止本 Task 明确识别的扫描进程，改为全部计数、限量行号定位和 Office 分块检查后完成；没有跳过历史对象，也没有操作其他运行进程。

## 回滚与唯一下一步

当前没有导入和日常入口切换，因此保持现状即可回退；不要合并候选。两个 bundle 已验证可恢复。TASK-0032 canonical 尚未进入 main，reservation 不 finalize、不提前 release；恢复本 Task 时继续原编号。

未来如获准清洗并迁移，合并只能采用保留导入历史的 merge commit，禁止 squash/rebase。合并后要回滚，需 User 授权后确认 merge 的主线 parent，再提交 revert；这只能回退可见文件，不会撤销已经公开的历史，所以不能代替发布前审查。

唯一下一步：User 决定是否接受隔离副本历史清洗及新旧 SHA 映射；批准前保持导入/发布暂停。
