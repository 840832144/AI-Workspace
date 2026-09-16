# TASK-0032 — CR 并入 AI-Workspace 的 public subtree 迁移

- Status: In Progress
- Execution status: Resumed; original-history import authorized
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

将 `840832144/cr_design` 以保留历史的 git subtree 原样导入 AI-Workspace 的 `projects/cr/`，单独适配规则、资料、Skills 与分析工具，实现一次克隆即可使用的 CR 策划入口，交付候选分支和 PR 等待 Review。

## Contract 与授权

2026-09-16 User 后续明确决定：已报告的 `Top_Tycoon原始事件账.xlsx`、`Top_Tycoon数值模型.xlsx`、`Top_Tycoon数值模型_v0.2.xlsx` 及其中原始 Spin、金币前后值、逐笔资源记录允许入库，不再阻塞迁移。保留原始 Git 历史，不清洗这三份文件。User 同时要求省去多余哈希校验；不新增或重复文件哈希扫描，使用直接 diff、祖先关系及实际工具运行验证。其余凭据、账号、私有 Registry 和未批准敏感内容限制继续适用。

完整方案、公开决定、范围、验收和回滚均见 [RFC-0005](../docs/rfc/RFC-0005-CR-Subtree-Public-Migration.md)。User 明确要求 AI-Workspace 迁移期间及合并后保持 public，之后自行调整；不修改任何仓库可见性/协作者或外部分享权限。最终合并和旧库归档未获授权。

## Gate 与来源

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
| 单独适配 | 已完成，待提交验收 | 根/CR规则、四启动文件、三 Agent 入口、路由、上下文及同步路径 |
| 全新克隆验收 | 正在执行 | 仅候选 AI-Workspace、根/CR 两入口、catalog/repository/卡包/相关校验、源表不变 |
| 推送/PR | 待验收通过 | commit、PR、merge commit 要求；不自行 squash/rebase/merge |

## 限制

除上方明确批准的三个工作簿记录外，Secret、账号信息、未批准原始采集数据、完整响应、逐笔余额、私有 Registry 和敏感日志禁止发布；任一发现即暂停发布并报告，不输出值，不静默清洗历史。保持 CR 结构、唯一 Skill 正文与历史来源映射。公司 SVN 仍是正式配置提交权威，不重建退役快照，不将 HuuugeCollector 副本升格，不混用 CR/101。不得执行同步 `--apply`、SVN 提交、真实采集、部署或修改源表。

## 下一步

完成全新候选克隆验收并回填 [迁移报告](../docs/migrations/CR-MIGRATION-20260916.md)，推送分支和创建保留历史的 PR 等待 Review。最终合并、切换与旧库归档仍需 User 确认；Task reservation 保持 pending-main，不重新分配或提前 finalize。
