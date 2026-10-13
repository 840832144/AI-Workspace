# TASK-0039 — Bingo Voyage 四卡自动玩可靠性修复

- Status: In Progress
- Project key: BINGO-VOYAGE
- Owner: User / ChatGPT
- Executor: Codex
- Priority: P0
- Date: 2026-10-13
- Specification: [EXECUTION_SPEC.md](support/bingo-voyage-autoplay-20261013/EXECUTION_SPEC.md)，固定批准版本 `1c3683fb1b2f51a77e02ba2aca3a8a78d99975da`。
- Allocation: remote-CAS；pending-main，未 finalize。

## Goal

以结构化数据完成四卡买卡、开局、合法点格、可靠确认、有限补漏、结算与续局。独立计量及数据质量先通过，再证明预登记连续十局逐局严格 >90%；整批加权 ≥95% 为优化目标。完整执行规格为本 Task 的规范性附件，不删减其 Gate 或故障回归。

## Scope

先复核历史 90.9% 及逐卡超额，再修当前工具链。治理基于最新 main `b0a36c8`；实现隔离于原 `bingovoyage-autoplay@90e97cc` 来源，不将探针树迁入治理 main。图像仅用于低频导航与几何标定。

## Non-goals

其他游戏、通用采集平台、协议写入、奖励/余额修改、充值、Max Bet、Root/CA/iptables 扩权、云部署、飞书发布、SVN 提交、PR 合并均不在本次范围。

## Deliverables

最小实现修复、独立证据核验器、十类离线故障回归、真实可调用的检查/启动/停止/结果入口、受控逐局证据和批次聚合、脱敏 Review 摘要及回滚说明。

## Acceptance

按完整规格 Gate 0–3 和 §9–12 验收。E 为完整同局非 FREE 应填集合，N=|E∩C|；逐局 `10*N > 9*E`，批次 `20*sum(N) >= 19*sum(E)`。零分母 N/A；数据不完整或语义不明不能输出可验收百分比。连续十局不挑成功局，不以离线测试冒充真实验收。

## Safety

只用已有明确授权实例及资源额度；读不到押注/总资源等上限时完成可独立实施和离线验证，实跑保持 Blocked。保全原分支/工作树/Raw；单控制者。公开 Git 不含真实卡面、账号、Raw、完整响应/日志、截图原件或凭据。

## Validation

### Round 1 继续实施

2026-10-13：[唯一 Round 1 评审](support/TASK-0039/CHATGPT-REVIEW-1.md) 从 `191914b7811658ddb7d17e95709703903f15863d` 原样纳入；状态 `Review → Changes Requested → In Progress`。R1 真实数据与运行绑定、R2 生产来源/批次校验、R3 过期点击取消继续在原 PR #16/#17 内完成，不新建 Task。附件三个纯合成反例已复现；不代表真实设备结果。沿用最多2定位+10验收、每局≤8票/300秒、累计≤96票/45分钟；所有启动与失败保留。main 已核对仍为 b0a36c8；不重新分配、不 release/finalize。

2026-10-13 Gate 0：独立 linked worktree；scan/validate 18 canonical、0 collision/errors、6 个既有 legacy warning。main 安全同步；Bingo 关键词 PR 仅 #15，现有 canonical/candidate 无同目标；remote reservation 已检查并由 allocator 分配 TASK-0039。Workspace Sync ON_DEMAND、0 conflict、provider unavailable、6 stale；以 Git 为准。原实现工作树干净，当前仅采集桥与抓包进程，未发现自动玩控制器；任何实跑前再次核对唯一控制者。登记当时尚未实施，当前结果见下节。

### 本轮实际结果（局部候选，不是完整目标完成）

- 登记 commit `634fb56` 已推送后才修改实现。实现基线 `90e97cc`，修复代码 `5c643dc`，单独 [PR #16](https://github.com/840832144/AI-Workspace/pull/16) 以 `bingovoyage-autoplay` 为 base；不将探针树引入治理 main。
- `python -m unittest discover -s tests -v`：21 项通过（exit 0），synthetic 故障回归；编译通过。检查、启动、真实旧证据结果入口均实调返回 Blocked/Invalid（exit 2），不是端到端成功。
- 历史 90.9% 拒绝作为验收证明：包装误计已证实，剥离后逐卡 5/7/7/10 与可观察应填 8/7/6/12 仍有矛盾；原会话有 5 次 FIFO 兜配。填充语义、完整分母和整局关闭未证实，Unknown 33 不是已确认漏填 33。
- 定位局 0、验收局 0、资源消耗 0；最低单局、整批加权率、单局 100% 次数均未建立。Gate 1 未通过；Gate 2/3 仅部分代码与离线行为通过，前台/布局实际采样、可靠确认、买卡结算续局及真实批次仍未完成。
- User 后续明确让 Codex 自行判断资源。来源分支并发新增 `d5fb47c` 仅含 RUN_LIMITS，代码未变；引用其 ≤300秒/单局和四卡约8票边界。选定最多2局定位+10局验收、每局≤8票、累计支出≤96票、总时长≤45分钟；必须先核对当前押注与资源，不充值/Max Bet。此决定不关闭技术证据缺口，也不要求 User 重复批准规格。
- 完整结果、十类回归覆盖及未完成项见 [Review 摘要](../projects/bingo-voyage/REPORTS/TASK-0039-REVIEW.md)。未部署、未重启采集器、未改 Root/CA/iptables、未合并/发布/SVN/finalize。

## Handoff

入口：[接管与结果](../handoff/BINGO-VOYAGE-AUTOPLAY-20261013.md)；[项目状态](../projects/bingo-voyage/STATUS.md)。完成后等待 ChatGPT Review，不自行 Accepted、不合并、不 finalize。

Subagents: none
