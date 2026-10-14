# TASK-0039 — Bingo Voyage 四卡自动玩可靠性修复

- Status: In Progress
- Project key: BINGO-VOYAGE
- Owner: User / ChatGPT
- Executor: Codex
- Priority: P0
- Date: 2026-10-13
- Specification: [EXECUTION_SPEC.md](support/bingo-voyage-autoplay-20261013/EXECUTION_SPEC.md)，固定批准版本 `1c3683fb1b2f51a77e02ba2aca3a8a78d99975da`。
- Allocation: remote-CAS；pending-main，未 finalize。

## 当前执行：2026-10-14完整自动玩重编

User追加节约要求（2026-10-14）：开发阶段真实测试须用最低普通Bet和最少卡数，优先不消费票券的离线重放；正式四卡验收保持四卡最低普通Bet。本轮不另加开发试购，全部启动和保守预留共享原账本。完整运行前两位置已保留：首局真实漏填；第二位置STOP落地前已购买并中止。最多余8位置，修复前后版本不拼成同版十局。

依据6eba235的[AUTOPLAY-DELIVERY-REPLAN-20261014.md](support/TASK-0039/AUTOPLAY-DELIVERY-REPLAN-20261014.md)完整任务；Round3原文保留，但与重编稿冲突的单击前置顺序、禁止完整运行及否认闪动漏点的旧表述均为历史，不再生效。状态Review→Changes Requested→In Progress，仍为TASK-0039 / PR #16/#17。

Goal/Scope：持续普通四卡全目标自动玩、安全补漏、合法窗口内收尾及自动结算续局。先做不消费票券的跨来源时间准备和完整模式入口回归，再使用剩余最多10个完整启动位置；不追加单击定位。run_ready决定可安全运行，metric_ready独立认证成功；跨局语义可以在预登记完整批次取得，不机械要求两局整局单击才能运行。

Acceptance：同版连续十局、无人工纠错、每局严格>90%，争取加权≥95%；未知不计成功，保留独立来源、全部失败/接管、完整分母及整数判定。User反馈局末大量格闪动按明显漏点事实记录；精确率由结构化数据核验，不能用N/A否认。单击模式导致后续不填解释原因，不消除问题。

Safety/Validation：共享账本历史12票/514.483秒保留并按实时核对；每局≤8票/300秒，任务累计≤96票/45分钟，含本轮只读设备准备与导航。当前最多10个完整启动，失败不替换、不清零、不另建purpose绕限。STOP、身份/报价/实际叫号、来源与资源核验不删除；图像仅导航标定。普通问题连续处理，不逐阶段等Review。统一交付实际逐局结果、代码/治理提交与受控复算；不自动合并、发布、SVN、扩权或finalize。Subagents: none。

## Goal

以结构化数据完成四卡买卡、开局、合法点格、可靠确认、有限补漏、结算与续局。独立计量及数据质量先通过，再证明预登记连续十局逐局严格 >90%；整批加权 ≥95% 为优化目标。完整执行规格为本 Task 的规范性附件，不删减其 Gate 或故障回归。

## Scope

先复核历史 90.9% 及逐卡超额，再修当前工具链。初始治理基于 main `b0a36c8`，本轮同步 `898358f`；实现隔离于原 `bingovoyage-autoplay@90e97cc` 来源，不将探针树迁入治理 main。图像仅用于低频导航与几何标定。

## Non-goals

其他游戏、通用采集平台、协议写入、奖励/余额修改、充值、Max Bet、Root/CA/iptables 扩权、云部署、飞书发布、SVN 提交、PR 合并均不在本次范围。

## Deliverables

最小实现修复、独立证据核验器、十类离线故障回归、真实可调用的检查/启动/停止/结果入口、受控逐局证据和批次聚合、脱敏 Review 摘要及回滚说明。

## Acceptance

按完整规格 Gate 0–3 和 §9–12 验收。E 为完整同局非 FREE 应填集合，N=|E∩C|；逐局 `10*N > 9*E`，批次 `20*sum(N) >= 19*sum(E)`。零分母 N/A；数据不完整或语义不明不能输出可验收百分比。连续十局不挑成功局，不以离线测试冒充真实验收。

## Safety

只用已有明确授权实例及资源额度；读不到押注/总资源等上限时完成可独立实施和离线验证，实跑保持 Blocked。保全原分支/工作树/Raw；单控制者。公开 Git 不含真实卡面、账号、Raw、完整响应/日志、截图原件或凭据。

## Validation

## 历史：Round 2修改后统一Review

TASK-0039回Review，未Accepted，继续原PR #16/#17。实现717d8dc（代码0f1475e；第3局实际运行8b1145c），47项离线/实际入口集成回归通过；B1批次STOP、B2时区排序、D1公开摘要及累计3局限制已修。main同步898358f，Registry工具重建/验证，原reservation pending-main，不finalize。

定位3/3，有效受控差分仍1局；第3局设计只发一次点击，User随后确认看到闪动提示后手动补点，客户端Manual12次，不能算全量自动玩漏填率。源重放还存在发送/购买时间绑定不足，不放宽窗口或事后校准来升级失败局。记录扣减/预留12票，累计控制运行514.483秒；历史8票/309.061秒和全部失败保留。正式0/10，N/A是证据不足，不是十局已跑而未达标。三局定位已用满，不能追加第四局，也不用验收代替定位。

当前限制仍为单局四卡普通档≤8票/300秒、任务≤96票/45分钟、验收启动≤10；实际--start exit2零消费。受控入口为`%LOCALAPPDATA%\AI-Workspace\bingo-voyage-task0039\REVIEW_R2.md`，`recompute_r2.py`本机实调exit0，来源重新得到有效1局/正式0局。完整真机确认/结算/续局待证明，等待ChatGPT统一Review；不合并、发布、SVN、扩权或finalize。Subagents: none。


### 历史：2026-10-14 执行修订接纳

按[执行修订](support/TASK-0039/EXECUTION-UPDATE-20261014.md)（a74005d）与[Round 2](support/TASK-0039/CHATGPT-REVIEW-2.md)（3daf754）继续原Task/PR #16/#17；历史Review原样保留。状态Review→Changes Requested→In Progress。先修批次STOP、时区排序及公开摘要，经离线回归后最多补1局定位；满足既定两局不同目标语义判据后直接预登记十局，不逐阶段等待Review。

唯一当前额度：定位总计≤3（已有2全部计入），验收启动≤10，四卡普通档每局≤8票/300秒，任务总支出/保守预留≤96票、累计控制运行≤45分钟；账本不清零，奖励不抵扣。历史8票/309.061秒保留。旧2局上限为原时点记录，被本修订替代。main同步898358f，Registry重建后继续；不分配新Task，不合并PR/发布/SVN/扩权/finalize。


### 历史：Round 1 修改后实际结果

- 实现b428c47已推送原PR #16；评审原文接纳9153f37，原PR #17继续治理，未新建Task。
- R2生产来源/批次与R3过期点击取消离线通过；R1真实定位及来源门槛后运行流程已接入，但完整真机确认/结算/续局仍未证明。39项离线/入口集成回归、编译/help通过；当前生产启动由来源重放得到1/2而拒绝，不是常量占位。
- 定位2/2，消耗4+4=8票；控制运行309.061秒。第1局控制输入0、客户端ManualDaub2，来源未确认；第2局输入1、同格客户端/终态一致、捕获错误0并观察闭局。实际叫号/目标分别27/31、29/47。
- 有效受控差分仅1局，尚未证明至少两个不同目标/独立局的语义。已到2局定位上限，因此正式验收0/10；最低局/加权/100%为N/A。证据未证明与真实未达标分开，不追加定位、不把失败局改名或挑成功局。
- 完整修改、实际结果、运行版本限制与受控入口见[再次Review摘要](../projects/bingo-voyage/REPORTS/TASK-0039-REVIEW.md)。状态回Review等待ChatGPT，不自行Accepted；原副本、采集器不动，不合并/发布/SVN/扩权/finalize。

### Round 1 继续实施（接纳记录）

2026-10-13：[唯一 Round 1 评审](support/TASK-0039/CHATGPT-REVIEW-1.md) 从 `191914b7811658ddb7d17e95709703903f15863d` 原样纳入；状态 `Review → Changes Requested → In Progress`。R1 真实数据与运行绑定、R2 生产来源/批次校验、R3 过期点击取消继续在原 PR #16/#17 内完成，不新建 Task。附件三个纯合成反例已复现；不代表真实设备结果。沿用最多2定位+10验收、每局≤8票/300秒、累计≤96票/45分钟；所有启动与失败保留。main 已核对仍为 b0a36c8；不重新分配、不 release/finalize。

2026-10-13 Gate 0：独立 linked worktree；scan/validate 18 canonical、0 collision/errors、6 个既有 legacy warning。main 安全同步；Bingo 关键词 PR 仅 #15，现有 canonical/candidate 无同目标；remote reservation 已检查并由 allocator 分配 TASK-0039。Workspace Sync ON_DEMAND、0 conflict、provider unavailable、6 stale；以 Git 为准。原实现工作树干净，当前仅采集桥与抓包进程，未发现自动玩控制器；任何实跑前再次核对唯一控制者。登记当时尚未实施，当前结果见下节。

### 历史：首轮局部候选（已被Round 1要求修改）

- 登记 commit `634fb56` 已推送后才修改实现。实现基线 `90e97cc`，修复代码 `5c643dc`，单独 [PR #16](https://github.com/840832144/AI-Workspace/pull/16) 以 `bingovoyage-autoplay` 为 base；不将探针树引入治理 main。
- `python -m unittest discover -s tests -v`：21 项通过（exit 0），synthetic 故障回归；编译通过。检查、启动、真实旧证据结果入口均实调返回 Blocked/Invalid（exit 2），不是端到端成功。
- 历史 90.9% 拒绝作为验收证明：包装误计已证实，剥离后逐卡 5/7/7/10 与可观察应填 8/7/6/12 仍有矛盾；原会话有 5 次 FIFO 兜配。填充语义、完整分母和整局关闭未证实，Unknown 33 不是已确认漏填 33。
- 定位局 0、验收局 0、资源消耗 0；最低单局、整批加权率、单局 100% 次数均未建立。Gate 1 未通过；Gate 2/3 仅部分代码与离线行为通过，前台/布局实际采样、可靠确认、买卡结算续局及真实批次仍未完成。
- User 后续明确让 Codex 自行判断资源。来源分支并发新增 `d5fb47c` 仅含 RUN_LIMITS，代码未变；引用其 ≤300秒/单局和四卡约8票边界。选定最多2局定位+10局验收、每局≤8票、累计支出≤96票、总时长≤45分钟；必须先核对当前押注与资源，不充值/Max Bet。此决定不关闭技术证据缺口，也不要求 User 重复批准规格。
- 完整结果、十类回归覆盖及未完成项见 [Review 摘要](../projects/bingo-voyage/REPORTS/TASK-0039-REVIEW.md)。未部署、未重启采集器、未改 Root/CA/iptables、未合并/发布/SVN/finalize。

## Handoff

入口：[接管与结果](../handoff/BINGO-VOYAGE-AUTOPLAY-20261013.md)；[项目状态](../projects/bingo-voyage/STATUS.md)。完成后等待 ChatGPT Review，不自行 Accepted、不合并、不 finalize。

Subagents: none
