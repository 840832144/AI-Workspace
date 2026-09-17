# CR 项目上下文

CR（Cash Royal）策划目标是形成有来源、假设、公式与验证的数值设计和分析资料。Owner 为 User，执行按 Workspace 正式 Task 分配。全局治理和跨项目 Task 位于仓库根；本目录维护 CR 设计资料、Skills 和分析工具。2026-09-16 PR #5 已使用 merge commit `3c214e2` 合并并切换；当前从最新 main 建独立分支/PR，只在 AI-Workspace/projects/cr 写入，旧库保留且不再双写。

入口：[README](README.md)、[规则](AGENTS.md)、[状态](STATUS.md)、[工作流](WORKFLOW.md)、[记忆](MEMORY.md)。Skill 唯一正文在 `.agents/skills/`，从根可通过 `.agents/skills/cr-project/SKILL.md` 路由。卡包参考入口位于 `数值策划/数值文档/03_分析与复盘/CR卡包价值分析资料_20260915/README.md`。

正式配置依赖公司 SVN 的明确目标 dev/trunk 和 revision；仓库内日期附件只证明当时版本。101 必须使用其自身配置与代码。HuuugeCollector 只是历史副本，当前实现见 `projects/huuuge-android-research/` 指向的外部仓库。

公开导入和单入口决策见 [RFC-0005](../../docs/rfc/RFC-0005-CR-Subtree-Public-Migration.md)。本上下文仅提供路径与边界；生成器不得递归打包 CR 工作簿、正文归档、原始记录或完整附件，也不自动上传 ChatGPT、飞书或其他服务。
