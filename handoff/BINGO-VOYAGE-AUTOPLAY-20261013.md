# Bingo Voyage 自动玩接管入口 — 2026-10-13

- Kind: handoff
- User decision: Confirmed；执行数据优先的四卡自动玩可靠性修复。
- Canonical allocation: [TASK-0039](../tasks/TASK-0039-BINGO-VOYAGE-AUTOPLAY.md)，2026-10-13 由独立 linked worktree remote-CAS 分配；pending-main。
- Implementation status: 未在本会话实现或实跑；旧 90.9% 为待复核历史结果。

## 完整规格

读取 [EXECUTION_SPEC.md](../tasks/support/bingo-voyage-autoplay-20261013/EXECUTION_SPEC.md)，批准版本 `1c3683f`。范围已获 User 确认；任务状态以 TASK-0039 和 [STATUS](../projects/bingo-voyage/STATUS.md) 为准。下文 ChatGPT 分配限制为历史记录。

本规格硬要求数据驱动决策、独立证据核验；图像仅辅助导航与几何标定。验收为预登记连续 10 局四卡逐局填充率 >90%；整批加权 ≥95% 为优化目标，100% 不表示填满全卡或保证中奖。数据完整性/语义/局归属另设门槛，禁止假成功、跨局借帧与挑成功局。

## 本次读取与限制

ChatGPT 在线确认 AI-Workspace main 为 `b0a36c8e1b75299814b3354530a58bbf59518714`，交接分支 `bingovoyage-autoplay` 为 `90e97ccf99f699b08fb6707498da4d8950a52fa3`；读取 main 的完整 tasks 路径树、Registry canonical/companion 项、当前 Handoff/Status，以及交接代码和文档。在线 Bingo PR 关键词检索无匹配不代表本机没有未提交或并发工作。

ChatGPT 当前容器无法取得可运行 allocator 的联网 Git 工作副本，未运行 Registry validator、未创建 remote-CAS reservation、未分配正式编号。不能把路径枚举和 Registry 阅读当成 validator 通过，也不能凭 main 当前最大编号猜下一个编号。正式预检与分配由 Codex 在本机已有工作空间按现有工具完成；本次仅保存不占号的已批准规格与接管入口。

本次未独立读取本机 Raw、模拟器或公司 SVN。不要覆盖 dsh 的原工作树、原数据或原分支；也不要将交接探针整树直接合入治理 main。

## Codex 下一步

先按 Gate 0 核对 latest main、并发与完整 Registry，合法分配 canonical Task，显式使用 Project key BINGO-VOYAGE，引用本规格固定 commit；重建/验证 Registry、提交推送并更新本页真实 Task 入口后，按 Gate 1–3 实施和独立验收。失败即报告具体阻塞，不绕过规则。

实跑沿用本机已有明确资源授权；缺少押注/总额度等明确上限时先交付代码和离线验证，实跑停在 Blocked。不自行充值、提高押注、使用 Max Bet 引导、扩权、合并 PR 或提交 SVN。

完成后返回 Task/实现 commit、测试与批次聚合结果、受控证据入口，进入 Review 等待 ChatGPT。
