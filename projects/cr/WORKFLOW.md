# CR 工作流

1. 安全读取最新 Git 与项目规则、Task、Status、Handoff；已有未提交修改时保留原现场并使用独立 worktree。使用根 Task Registry 防重和 allocator，不能猜编号。
2. 确认问题、材料范围、项目与版本；选择对应唯一 Skill。资料索引先于正文，业务输入优先从明确来源只读获取。
3. 设计资料与分析工具在 `projects/cr/` 制作候选，结论标记假设和限制。原始源表默认只读；新材料需确认公开范围。
4. 运行 catalog、repository 和受影响业务工具验证。只对实际风险做最小验证，不增加重复哈希。若需资料同步，仅先 dry-run；`--apply` 必须有该任务明确授权。
5. 正式配置修改必须回到公司 SVN 的目标工作副本，核对项目、URL、环境、revision 和授权文件；沿用原制作、审阅、提交后回读流程。Git 迁移不产生 SVN 提交授权。
6. 更新根 Task/Handoff、项目 Status 与必要长期记录，提交候选分支和 PR 等待 Review。当前不双写旧 CR Git 或 SVN 资料镜像。HuuugeCollector 副本不用于启动采集、自动同步或部署。

验收命令见 [README](README.md)；来源与回滚见 [迁移报告](../../docs/migrations/CR-MIGRATION-20260916.md)。
