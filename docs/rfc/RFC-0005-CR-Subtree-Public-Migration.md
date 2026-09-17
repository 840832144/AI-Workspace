# RFC-0005：CR 资料与分析工具并入 AI-Workspace

- Status: Accepted / Implemented; PR #5 merged, cutover complete, reservation finalized
- Date: 2026-09-16
- Actors: User, Codex；最终 Review：ChatGPT / User
- Task: [TASK-0032](../../tasks/TASK-0032-CR-SUBTREE-PUBLIC-MIGRATION.md)
- Subagents: none

## 目标与已批准决定

2026-09-16 补充决定：User 明确允许审查指出的三份 Top Tycoon 工作簿及其原始 Spin / 金币前后值 / 逐笔资源数据公开入库，不再因此阻塞；这些文件及原 Git 历史保持原样。历史清洗提案不采用。User 要求避免额外哈希校验，本次用 Git diff、来源 commit 和祖先关系，加必要功能校验验收；不重复备份哈希或文件摘要扫描。此例外仅适用于明确批准的材料，不允许上传凭据、私有 Registry 或其他未授权敏感内容。

User 明确要求将 `840832144/cr_design` 并入 `840832144/AI-Workspace` 的 `projects/cr/`，使 Agent 只克隆 AI-Workspace 就能读取全局规则、CR 策划资料、Skills 与分析工具。目标仓库在迁移期间及合并后保持 public；后续可见性由 User 自行调整。来源为 private 不构成单独阻塞理由。不得修改任一仓库的可见性、协作者权限或飞书及其他外部分享权限。

准备阶段授权覆盖备份、完整历史审查、非 squash subtree 导入、入口适配、离线验收、推送候选分支和创建 PR，当时未授权最终合并。User 于2026-09-16随后明确批准 PR #5 以 merge commit 合并、切换单仓入口及 finalize 原 reservation；现已执行，详见迁移报告。旧库暂不归档、不删除，禁止权限调整、源历史清洗/重写或强推主分支。

## Capability 与仓库定位

现有 Catalog 没有独立的仓库迁移 Capability；本次以 User 明确批准的 Git 维护工作流、Task contract 和本 RFC 定义一次性结果，不虚构新的 Registered Capability。Context 适配复用现有 Context reference implementation；没有云文档操作需求。现行纯控制面限制按本次批准，调整为允许 `projects/cr/` 内的 CR 策划资料、唯一 Skill 正文和分析工具。其他项目实现、共享 provider 实现与运行时配置继续在其权威位置。

## 来源、备份与并发范围（准备时记录）

| 仓库 | 审查基线 main SHA | 当前可见性 |
| --- | --- | --- |
| AI-Workspace | `5b5414cf7ecb9df3c06d23b3325cfb90b4fa2d7e` | public |
| cr_design | `1409737648b15f602586b79ade7e0c3e7a3813a0` | private |

两仓均已 fetch 最新 origin，AI-Workspace 干净 main 已安全同步；CR 已有完整、非 shallow Git checkout，原 SVN 工作副本与本地未纳管文件保持原状。两仓 `git bundle create --all` 本地备份与 `bundle verify` 已通过；备份和完整本机证据只在受控本地目录，ACL 限当前用户与 SYSTEM，路径不进入公共 Git。发布前再核验两仓 main，源发生变化则重新审查。

已扫描 main Task Registry、候选、RFC、Roadmap、远端 heads 与开放 PR，无同目标 active Task。TASK-0032 由独立非 main linked worktree 的 remote-CAS allocator 返回，reservation 保持 pending-main，token 只在本地。PR #2 EarlyMeeting 与 PR #4 Huuuge 云端工作不由本 Task 修改；TASK-0030 Pop Slots 的业务内容及原 checkout 不覆盖。共享入口变更在本分支隔离，合并前需复查这几项并发差异。

## 执行顺序

1. 将本完整方案和 canonical Task 提交 Git，重建并验证 Registry。
2. 扫描待导入树、全部可达 commit/tree/blob/tag、已删除历史文件及归档内内容。核验缺失对象、嵌套 `.git` / `.svn`、submodule、凭据、账号信息、原始采集数据、完整响应、逐笔余额、私有 Registry 和敏感日志。保留脱敏路径、类别、对象定位与覆盖统计，不输出敏感值。
3. 发现禁止发布内容即暂停发布。报告具体类别、影响范围和处理方案；不得只从 HEAD 删除后仍公开旧历史，也不得静默重写来源历史。未完成审查不得把清单或工具成功等同于通过。
4. 审查通过后在 `codex/cr-subtree-migration` 执行 `git subtree add --prefix=projects/cr <本机CR Git来源> <固定SHA>`，不使用 `--squash` 或 submodule。该提交只做原样导入；用 Git 直接 diff 核对源树与导入子树的路径、模式与内容。不得复制整个本机目录。
5. 单独提交适配，保留 CR 内部结构。Skill 正文唯一保存在 CR 项目；根入口采用路由，避免复制正文。历史记录保留旧来源、日期和 SHA，以映射解释旧路径，不把旧记录改写成当前事实。
6. 更新现行入口、规则、架构、上下文与资料同步路径，离线验证后提交证据。通过安全 gate 后才推送迁移分支、创建 PR；要求 merge commit，禁止 squash/rebase 合并。

## 适配清单与路径映射

| 对象 | 目标与要求 |
| --- | --- |
| `cr_design/<path>` | `AI-Workspace/projects/cr/<path>`；原样导入前后清单逐项核对 |
| 根与项目规则 | 根 `AGENTS.md`、`README.md`、`AI_TEAM.md`、`ARCHITECTURE.md`、`CONTRIBUTING.md` 与 CR `AGENTS.md` 一致说明批准边界 |
| CR 项目入口 | 补齐 README / CONTEXT / MEMORY / WORKFLOW / STATUS / REPORTS / ASSETS；不提前占用 subtree 前缀 |
| 四份启动文件 | `bootstrap/chatgpt/00_CORE_RULES.md`、`01_SYSTEM_CONTEXT.md`、`02_CURRENT_STATE.md`、`03_NEW_CHAT_BOOTSTRAP.md`；当前状态与稳定规则分离 |
| ChatGPT / Codex / TRAE | 检查各实际入口，根目录和 CR 子目录都能找到根规则与相关 Skills |
| Skill 路由 | 以实际 CR `.agents/skills/*/SKILL.md` 为唯一正文；同步通用技能索引及 TRAE 入口 |
| 上下文 | 适配实际 Context manifest、`tools/context/workspace_context.py`、Source Pack 生成器和刷新路径，不上传原始数据 |
| 资料同步 | `projects/cr/数值策划/工具/config/` 及工具路径解析；源只读，默认 dry-run，不执行 `--apply` |
| CR 卡包资料 | `projects/cr/数值策划/数值文档/03_分析与复盘/CR卡包价值分析资料_20260915/` |
| 101 交接 | 修改 `handoff/101-CARD-PACK-VALUATION-20260915.md` 的双仓入口为单仓；CR 仅参考，101 参数必须来自101自己的环境和代码 |
| 历史快照 | 保留来源语义，不重建已退役的程序配置快照结构；不得称为当前配置 |
| HuuugeCollector | 导入内容仅作为随 CR 保存的历史副本，不自动升级为开发、采集或部署真相源 |

公司 SVN 仍是正式配置及提交链的权威；分析需记录 CR 环境、revision 与受控本地来源。不得混用 dev/trunk，不得以 Git 策划源表、历史快照或101参数替代当前 CR 配置。

## 验收标准

- 在全新目录只克隆 AI-Workspace 候选分支，不依赖第二个 CR checkout、符号链接到旧仓库、原 SVN 或本机工具副本。
- 从根和 `projects/cr/` 分别验证规则链、Skill 正文可达、卡包五份入口资料与工具路径；如工具需要第三方依赖，按实际声明核验，不以存在文件代表可用。
- 运行 `build_catalog.py`、`validate_repository.py`、现有相关离线校验、Task Registry、Context 校验与 `git diff --check`。源表前后不变；禁止同步 `--apply`、SVN 提交、真实采集、部署或101配置写入。
- 验证原样导入子树与源 tree 一致，源 main 与其全部祖先可达，提交数量与对象完整性可复核；非 main 的其他来源分支仅备份/审查，不隐式合并业务。
- 输出来源 SHA、文件清单、路径映射、历史验证、测试结果、缺口与回滚。更新 Task、Status、Handoff、相关长期记录；Review 未通过不得写成已合并或 Done。
- 发布前重新 fetch main、审查候选 diff/完整将发布图，确认禁止内容为零；创建 PR 标明必须保留导入历史，返回 commit 和 PR 等待 Review。

## 切换与防双写

2026-09-16 User 批准后，PR #5 已合并并完成切换。唯一日常 Git 入口为 AI-Workspace 最新 main，CR 策划资料和分析工具只写 `projects/cr/`；后续从最新 main 建独立分支/PR。迁移审查时未切换的候选记录仅供追溯，旧 Git 仓库保留但不再双写。公司 SVN 正式配置流程不变；旧库暂不归档、不删除。

## 回滚

- 合并前：不合入候选 PR 即保持现行入口；本机 bundle 可恢复两个原始图。保留候选分支和已分配 Task；canonical 尚未进 main，不 finalize、不提前 release。
- 合并后：经 User 授权，以新提交 revert 迁移的 merge commit（先确认 `-m 1` 的主线 parent），回退入口、路由和适配；不得强推或改写共享历史。
- Git revert 不能撤回已公开历史；因此发布前完整可达历史审查是硬 gate。若历史含敏感内容，须先决定清洗方案并重新审查，不能依赖事后 revert。
- 如需恢复旧 Git 写入口，需 User 明确指定切换时间和迁移期间新增内容归属，先停止双写，再选择性回迁；SVN 不受本迁移回滚影响。

## 当前实施状态

原样 subtree 导入 `fe07557ce5052da6a0eaaaaa1207b416ac081474` 已完成，来源 main 保持13个原提交、276个原文件。三个工作簿的公开授权已明确，清洗提案不采用。适配与验收证据见 [迁移报告](../migrations/CR-MIGRATION-20260916.md)；Round 1 已 Accepted；最终合并、切换与原 reservation finalize 已完成，merge commit `3c214e2`。旧库仍保留，归档和权限调整不在本次授权内；当前执行状态以 Task 为准。
