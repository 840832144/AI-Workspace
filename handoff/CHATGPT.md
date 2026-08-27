# ChatGPT Handoff

这是 ChatGPT 的固定交接入口。长期事实必须同步到 Capability contract、项目 Memory/Status、Task、RFC 或 ADR，而不是只留在聊天中。

- Updated: 2026-08-27
- Task: TASK-0015
- Current state: Ready for Codex execution — capture only

## Review Decision

- TASK-0014：Accepted。
- Codex Subagent Pilot 的原子安装、OFF/MANUAL 开关、父会话权限限制、单写入者、MCP deny、回归测试和最终 OFF 均已通过 Review。
- 当前默认模式继续保持 `OFF`。

## Revised Objective

执行 [`TASK-0015 — Huuuge Lottery 限时活动实时采集与体验证据保全`](../tasks/TASK-0015-Huuuge-Lottery-Live-Numerical-Breakdown.md)。

User 将亲自体验活动并决定所有游戏内操作，尤其是任何付费、充值、礼包、Ticket 购买或高价值资源消耗行为。Codex 不代替 User 做付费判断或操作。

本轮只负责：

- 立即完成 Environment Check 并启动 Lottery 专用 Capture；
- 看到 READY 后，用短步骤提醒 User 观察哪些页面和状态；
- 被动记录 User 自己执行的正常游戏行为；
- Clean Finalize 并验证 Session 完整性；
- 输出已捕获、未捕获和后续可分析的证据清单。

## Explicitly Deferred

本轮暂不处理：

- 掉落概率和 Bet 关系分析；
- 完成消耗、付费压力和奖励返还；
- CR 可迁移方案；
- Git 数值报告；
- AI Document Assistant / 飞书报告；
- 双仓提交作为完成条件。

等 User 明确说“体验完成，可以开始分析”后，再建立独立任务。

## Boundaries

- 任何付费动作都由 User 自主决定并亲自执行；Codex 在动作前等待明确说明，不点击、不自动化、不推荐是否购买。
- Raw/value-bearing capture、账号信息、逐笔余额和截图原件保持本机。
- 不修改请求、奖励、余额或服务器状态。
- 不为本任务重构 Collector、开发 Extractor、Normalized Fact Layer 或 AI Report Engine。
- Subagents 不是前置条件；保持 OFF，不得为切换模式延误采集。

## Exact Next Action

Codex 同步 AI-Workspace 与 `huuuge-android-research`，读取修订后的 TASK-0015 和 Huuuge 当前规则。立即做 Environment Check，启动 Lottery 专用 Capture；看到 READY 后，再逐步引导 User 自主体验。结束时 clean finalize，只返回 Session 完整性和证据覆盖情况。
