# ADR-0008 — CR 单仓库日常入口

- Status: Accepted
- Date: 2026-09-16
- Decision owner: User
- Implementation: TASK-0032，候选等待 Review；本决策不等于已合并。
- Related RFC: [RFC-0005](../rfc/RFC-0005-CR-Subtree-Public-Migration.md)
- Supersedes: 仅替代旧架构对 CR 必须独立 Git 仓库/不得纳入设计工具的限定，其他项目真相源不变。

## 决策

以非 squash git subtree 将 cr_design main 纳入 public AI-Workspace 的 `projects/cr/`，保留内部路径与来源历史。合并并切换后，CR 策划资料、Skills、分析工具只在此目录日常写入；旧库暂保留追溯，归档需 User 另行确认。

User 明确要求 AI-Workspace 迁移期间及合并后保持 public，后续自行调整可见性；不修改任一仓库可见性或协作者权限。2026-09-16 后续授权包含三个 Top Tycoon 工作簿的原始 Spin、金币前后值与逐笔记录及历史。该特定授权不放宽其他 Secrets、账号、私有 Registry、完整响应或敏感日志限制。

公司 SVN 继续负责正式配置制作与提交。日期附件只证明历史版本，不重建退役快照结构；HuuugeCollector 副本不成为开发/部署真相源，101 保持自己的配置与写入位置。

## 后果与验收

只克隆 AI-Workspace 即可读取根/项目规则与全部 CR 资料工具。Skill 正文唯一，历史引用通过前缀映射保留来源。Context 只生成入口摘要，不扩大外部分享。
导入提交与适配提交分开；通过直接 diff、祖先关系和全新克隆实际运行验收，不增加重复哈希工作。PR 必须 merge commit，禁止 squash/rebase merge，否则来源历史不再是 main 的祖先。
回滚需同时撤回导入、适配与入口指向；合并前保留分支不切换，合并后经批准用 revert 创建新提交。详细清单和限制见 [迁移报告](../migrations/CR-MIGRATION-20260916.md)。
