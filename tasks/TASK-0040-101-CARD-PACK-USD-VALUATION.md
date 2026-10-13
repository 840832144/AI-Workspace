# TASK-0040 — 101 卡包美元价值计算

- Status: Ready
- Project key: GAME-101
- Owner: User / ChatGPT
- Executor: Codex
- Priority: P1 / User 已确认范围
- Date: 2026-10-13
- Updated: 2026-10-13
- User decision: Approved
- Allocation relationship: new
- Subagents: none

## Goal

按 101 实际星级与 packId 交付每包美元价值主表、口径说明和可复算脚本，实际计算并独立复核。配置定价或内部面值、条件模型估值、真实售价参考分别展示，不把条件估值称为统一售价。

## Scope

执行 [User 已批准完整规格](../docs/plans/101-CARD-PACK-USD-VALUATION-20261013.md)，来源 PR #18 / 541e190。仅只读 User 指定的 101 trunk 与定向相关实现。复用 CR 提取及验证方法，所有业务输入来自 101。缺口只影响对应结果。

## Non-goals / Safety

不修改源表，不执行 SVN update/revert/commit，不购买、访问账号、采集或发布，不改变权限，不占用其他任务工作区。完整配置、数值、代码和原始日志留受控本机；公共 Git 只保存脱敏治理。没有已批准的 101 实现仓库时脚本留受控本机，不创建私有远端。

## Deliverables

受控本机《101_卡包美元价值.xlsx》、说明、输入清单、模型参数、复算脚本、独立检查与运行摘要。Git 保存本 Task、[状态](support/TASK-0040/STATUS.md)、规格及 [交接](../handoff/101-CARD-PACK-USD-VALUATION-20261013.md)。

## Acceptance / Validation

逐项执行规格第 8 节：输入版本与缓存身份、完整 packId 覆盖、实际抽取规则、美元单位、奖励不重复计值、各星级及不同规则独立复核、模型误差、工作簿实际数值/缓存/布局、只读边界、Registry 与交接。条件与缺失单列。交付后状态进入 Review，等待 ChatGPT Review，不自动 Accepted/Complete、合并或 finalize。

## Gate 0

- 最新 main b0a36c8 已 fetch 并 fast-forward 检查；独立 linked worktree 分支 codex/101-card-pack-usd-20261013，包含规格 commit 541e190。
- 完整 tasks scan/validator：18 canonical、0 collision、valid，6 条已审计 legacy 提示。已 fetch 全部远端分支并搜索 tasks，未发现 GAME-101 或同目标 canonical/candidate/companion/review；既有保留号与本范围无重叠。
- 既有 allocator remote-CAS 分配 TASK-0040，pending-main；token 留受控本机。GAME-101 未发现已有映射，使用规格合法 project key。
- Workspace Sync：ON_DEMAND，provider unavailable，stale 6，conflicts 0；以最新 Git 为准，不覆盖旧快照。
- 附件与 PR 中完整规格逐行一致。治理登记提交推送后开始业务读取及计算。

## Handoff

当前下一步：完成本登记提交推送后直接冻结只读输入并执行。Subagents: none。
