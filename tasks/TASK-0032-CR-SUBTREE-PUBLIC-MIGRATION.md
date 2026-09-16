# TASK-0032 — CR 并入 AI-Workspace 的 public subtree 迁移

- Status: In Progress
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

完整方案、公开决定、范围、验收和回滚均见 [RFC-0005](../docs/rfc/RFC-0005-CR-Subtree-Public-Migration.md)。User 明确要求 AI-Workspace 迁移期间及合并后保持 public，之后自行调整；不修改任何仓库可见性/协作者或外部分享权限。最终合并和旧库归档未获授权。

## Gate 与来源

- AI-Workspace：`5b5414cf7ecb9df3c06d23b3325cfb90b4fa2d7e`；CR：`1409737648b15f602586b79ade7e0c3e7a3813a0`。
- 独立 linked worktree 分支：`codex/cr-subtree-migration`；main 已安全同步，原有 checkout 与 SVN 本机产物保留。
- main Registry：14 canonical / 0 collision / valid；已检查 Task、RFC、Roadmap、远端 heads、开放 PR，无同目标 active Task。
- remote-CAS 正式返回 TASK-0032；reservation 保持 pending-main，token 仅本地；canonical 合入 main 后才 finalize。
- 两仓完整 refs 的本机 bundle 已创建并 verify；完整文件和可达历史审查尚未完成。
- Workspace Sync：ON_DEMAND / provider unavailable / stale 6 / conflicts 0；以最新 Git 为准，不自动发布。

## 阶段与成功证据

| 阶段 | 当前状态 | 必要证据 |
| --- | --- | --- |
| 规则、并发、备份、登记 | 已准备 | 最新 SHA、bundle verify、allocator、Task/RFC Git commit |
| 安全审查 | 待执行 | 完整对象覆盖、归档检查、脱敏问题及处理结论 |
| 原样导入 | 待 gate | 非 squash subtree commit；树、清单、内容及祖先可达性一致 |
| 单独适配 | 待导入 | 根/CR规则、四启动文件、三 Agent 入口、路由、上下文及同步路径 |
| 全新克隆验收 | 待适配 | 仅候选 AI-Workspace、根/CR 两入口、catalog/repository/相关校验、源表不变 |
| 推送/PR | 待审查通过 | commit、PR、merge commit 要求；不自行 squash/rebase/merge |

## 限制

Secret、账号信息、原始采集数据、完整响应、逐笔余额、私有 Registry 和敏感日志禁止发布；任一发现即暂停发布并报告，不输出值，不静默清洗历史。保持 CR 结构、唯一 Skill 正文与历史来源映射。公司 SVN 仍是正式配置提交权威，不重建退役快照，不将 HuuugeCollector 副本升格，不混用 CR/101。不得执行同步 `--apply`、SVN 提交、真实采集、部署或修改源表。

## 下一步

先提交本 Task/RFC 和自动 Registry，然后执行完整历史与待导入文件的本地审查；通过后才进行 subtree 与发布。
