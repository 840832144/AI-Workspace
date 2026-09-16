# TASK-0032 — CR 并入 AI-Workspace 的 public subtree 迁移

PR：[AI-Workspace #5](https://github.com/840832144/AI-Workspace/pull/5) 已按 User 最终授权于 2026-09-16 15:03:31（北京时间）使用 Create a merge commit 合并，merge commit `3c214e2ca75eb82c16af6a186f7366fb3c249140`。当前日常入口为 AI-Workspace `main`，CR 资料与工具只写 `projects/cr/`；原 reservation 已 finalize。旧 cr_design 保留，不归档、不删除，权限不变。

- Status: Complete
- Review decision: Accepted（ChatGPT Round 1，83eadec）
- Execution status: 已合并、已切换 AI-Workspace 单仓入口；原 reservation finalized
- Project key: WORKSPACE
- Owner: User / ChatGPT
- Executor: Codex
- Priority: P1 / approved migration
- Date: 2026-09-16
- Updated: 2026-09-16
- User decision: Approved
- Allocation relationship: new
- Related tasks: TASK-0020, TASK-0021
- Subagents: none

## Goal

将 `840832144/cr_design` 以保留历史的 git subtree 原样导入 AI-Workspace 的 `projects/cr/`，单独适配规则、资料、Skills 与分析工具，实现一次克隆即可使用的 CR 策划入口，交付候选分支和 PR 经 Review；按 User 2026-09-16 最终授权完成合并、入口切换与原 reservation finalize。

## Contract 与授权

2026-09-16 User 后续明确决定：已报告的 `Top_Tycoon原始事件账.xlsx`、`Top_Tycoon数值模型.xlsx`、`Top_Tycoon数值模型_v0.2.xlsx` 及其中原始 Spin、金币前后值、逐笔资源记录允许入库，不再阻塞迁移。保留原始 Git 历史，不清洗这三份文件。User 同时要求省去多余哈希校验；不新增或重复文件哈希扫描，使用直接 diff、祖先关系及实际工具运行验证。其余凭据、账号、私有 Registry 和未批准敏感内容限制继续适用。

完整方案、公开决定、范围、验收和回滚均见 [RFC-0005](../docs/rfc/RFC-0005-CR-Subtree-Public-Migration.md)。User 明确要求 AI-Workspace 迁移期间及合并后保持 public，之后自行调整；不修改任何仓库可见性/协作者或外部分享权限。准备及 Review 收口阶段未获最终合并授权。User 于 2026-09-16 随后明确批准 PR #5 merge commit 合并、单仓切换和原 reservation finalize；旧库暂不归档、不删除，外部权限调整不在本次授权内。

## Gate 与来源（迁移准备时记录）

- AI-Workspace：`5b5414cf7ecb9df3c06d23b3325cfb90b4fa2d7e`；CR：`1409737648b15f602586b79ade7e0c3e7a3813a0`。
- 独立 linked worktree 分支：`codex/cr-subtree-migration`；main 已安全同步，原有 checkout 与 SVN 本机产物保留。
- main Registry：14 canonical / 0 collision / valid；已检查 Task、RFC、Roadmap、远端 heads、开放 PR，无同目标 active Task。
- remote-CAS 正式返回 TASK-0032；reservation 保持 pending-main，token 仅本地；canonical 合入 main 后才 finalize。
- 两仓完整 refs 的本机 bundle 已创建并 verify，并从 bundle 恢复后通过 full fsck。CR 16 commit / 121 tree / 299 blob、目标 197 commit / 1040 tree / 1185 blob 已完成可达对象枚举和文本/Office 扫描。
- Workspace Sync：ON_DEMAND / provider unavailable / stale 6 / conflicts 0；以最新 Git 为准，不自动发布。

## 阶段与成功证据

| 阶段 | 当前状态 | 必要证据 |
| --- | --- | --- |
| 规则、并发、备份、登记 | 已完成 | 两仓最新 SHA、bundle 恢复/full fsck、allocator；Task/RFC 首次提交 `52e3279e613858a0e691700bb5188b0a98cb8bc0` |
| 安全审查 | 通过本次授权范围 | 全图扫描与22张图片审查；三份工作簿已获公开批准，其他候选经语义核查；见迁移报告 |
| 原样导入 | 已完成 | `fe07557` 非 squash；276 文件直接 diff 为空，来源13提交成为祖先 |
| 单独适配 | 已完成 | 根/CR规则、四启动文件、三 Agent 入口、路由、上下文及同步路径 |
| 全新克隆验收 | 已通过 | 仅候选 AI-Workspace、根/CR 两入口、catalog/repository/卡包/相关校验、源表不变 |
| 推送/PR | 已合并；Round 1 Accepted | 评审基线 `83eadec`，完整评审见 [Round 1](../reviews/TASK-0032-CHATGPT-REVIEW-1.md)；User 最终授权后以 merge commit `3c214e2` 合并 |
| main 验证与切换 | 已完成 | main 保留 CR 来源 `1409737` 与原样导入 `fe07557` 祖先关系；根/CR 入口、14源表构建及仓库校验通过，唯一 Git 写入位置为 `projects/cr/` |
| 原 reservation finalize | finalized | canonical 已在最新 origin/main；既有 task_cli 使用原 TASK-0032 reservation 完成，远端 reservation ref 与本地 reservation 文件已释放，无重新分配 |

## 限制

除上方明确批准的三个工作簿记录外，Secret、账号信息、未批准原始采集数据、完整响应、逐笔余额、私有 Registry 和敏感日志禁止发布；任一发现即暂停发布并报告，不输出值，不静默清洗历史。保持 CR 结构、唯一 Skill 正文与历史来源映射。公司 SVN 仍是正式配置提交权威，不重建退役快照，不将 HuuugeCollector 副本升格，不混用 CR/101。不得执行同步 `--apply`、SVN 提交、真实采集、部署或修改源表。

## ChatGPT Review Round 1

[完整评审](../reviews/TASK-0032-CHATGPT-REVIEW-1.md)已从 PR 已发布正文固化，评审基线为 `83eadec13cb4a03fa5b75de8dcbdd1f83cb61048`，结论 Accepted，无必须修改项。
证据限制：Review 未独立复跑81项测试、工作簿检查或本机备份恢复，亦未重复完整历史敏感内容审查；这些运行结果来自原迁移报告，不是本轮独立执行或 GitHub CI。Round 1 收口提交 `04a7568` 只更新14个文档/Registry 文件；最终合并未修改已评审的业务工具、Skill 路由或源资料。完整评审按当时状态保留，不改写原文。

## 最终执行与后续边界

合并前 fetch 两仓 main 与 PR head：AI `5b5414c`、CR `1409737` 未变，PR head `04a7568` 相对评审只有已授权收口；PR #2 `4eb109b` / #4 `872e2dc` 的共享文件工作早于评审且仍在各自分支，PR #5 对 main 无冲突。合并后的树与候选无差异，两个来源提交仍为 main 祖先。

原 reservation 在 canonical 进入 main 且入口验证通过后返回 `finalized`，canonical_file 为本 Task、project_key 为 WORKSPACE；没有重新占号。实际合并、验证和回滚见[迁移报告](../docs/migrations/CR-MIGRATION-20260916.md)。日常从最新 main 建独立分支/PR，只写 `AI-Workspace/projects/cr/`；不再双写旧库。公司 SVN 正式配置流程不变。旧库归档、删除、外部权限和手工 Project Sources 上传均未执行。
