# TASK-0039 — Bingo Voyage 四卡自动玩可靠性修复

- Status: In Progress
- Project key: BINGO-VOYAGE
- Owner: User / ChatGPT
- Executor: Codex
- Priority: P0
- Date: 2026-10-13
- Specification: [EXECUTION_SPEC.md](support/bingo-voyage-autoplay-20261013/EXECUTION_SPEC.md)，固定批准版本 `1c3683fb1b2f51a77e02ba2aca3a8a78d99975da`。
- Allocation: remote-CAS；pending-main，未 finalize。

## 当前进展：16票修订已实施，生产来源待具体授权

附件和649fcad唯一Round 5已由45d4c92原样接纳；本轮未找到或虚构所谓新附件commit。实现交付[588a1ec](https://github.com/840832144/AI-Workspace/commit/588a1ec581a651c9d23b66da1167826476785fbe)，功能代码1d2d694。原PR #16/#17继续Draft/Open，Task保持In Progress，完整目标未交付，未Accepted；不以局部回归进入完成状态。

当前代码统一单局16票/300秒、累计18个完整位置/5400秒/96票，定位仍3。批次固定新10局，不将18个位置当成18局验收；前8个位置不拼入。整批预算先过再登记，每次预留重算剩余局数，额外预留30秒保存/收尾空间；不是新增额度。报价与扣费少扣/多扣均停止后续消费。新授权绑定预留、冻结及批次核验，历史8票判据仍保留。

81项离线/实际函数与CLI集成回归通过（31.424秒，exit0），编译/diff通过。真实只读--check exit2：run_ready=false、metric_ready=true，阻断为quote_resource_clock_not_covered/current_panel_quote_unavailable。新限制真实回读正确，但没有实时当前面板来源、没有新增Hook、没有真实--start、零购买/零游戏输入。新十局0/10，填充率未产生；不是已运行十局未达标。

原账本最新累计**52票/2346.105秒、8个历史完整位置和3局定位**。本次只读检查78.828秒计入；旧离线单测曾追加0.015秒正式计时，记录保留并修正该单测隔离，最终整套回归后正式账本字节不变。剩44票/3053.895秒/10位置；按十局3000秒与收尾30秒，准备余量仅23.895秒，不重复设备检查。当前真实最低价未知；4票场景十局可覆盖，8/12/16票场景总额分别差36/76/116票，不能以16票单局合法先买。

已有第4–7位置实际--results均exit2，复算E/N/U/未填保持35/28/4/3、37/30/7/0、35/27/4/4、46/28/13/5。第6位置上界88.57%是真实未达标，第8位置当时12>8违规和User接管保留；12个dry补排机会不计成功。旧阈值/旧禁购顺序下方仅为历史，不覆盖本次资源授权与新十局顺序。

本地静态字段映射定位到BuyCardPanel卡数/Bet/价格影响、BetAddView可选范围、BaseBingoCardView禁点/覆盖、BingoPlayView闭局/暂停及自然Daub候选；字段token不是运行时地址或真实快照。既有存档/协议/扣费后日志/历史UI层级不足以绑定当前面板。下一步仅请求原实例当前面板与同局四卡的限定进程内被动Hook；User明确“额度调整不授予新增技术权限”，尚未执行。具体对象、更新点、排除路径、STOP/异常撤销及不调用业务方法/不改状态或协议/不新增Root证书网络权限，见下列方案。不是重新请求已批准额度，也不额外买定位局。

受控复算入口：%LOCALAPPDATA%\AI-Workspace\bingo-voyage-task0039\execution16\REVIEW_16T.md，含ENTRY_CHECKS.json、RECOMPUTED.json、tests-final.txt、map_metadata.py/static-observation-map.json、recompute.py。原始卡面、账号、逐次余额、完整日志/协议不上Git。生产读取与覆盖后真实受理、完整结算续局和同版连续十局仍待完成。

main安全同步并确认898358f为祖先；Registry重建/validate，原reservation pending-main；Workspace Sync ON_DEMAND、0冲突、provider unavailable、6 stale，Git为准。完成真实主线后再统一Review；不合并、发布、提交SVN、扩权或finalize。Subagents: none。

[执行修订](support/TASK-0039/EXECUTION-16T-20261014.md) · [Round 5](support/TASK-0039/CHATGPT-REVIEW-5.md) · [具体观察方案（未授权）](support/TASK-0039/SOURCE-OBSERVATION-SCOPE-20261014.md)。

## 本轮接纳记录：16票执行修订

接纳User本机附件TASK-0039-16T-Execution.md（原样保存为EXECUTION-16T-20261014.md），以及其引用的649fcad唯一Round 5原文。不存在本次额度修订的先前Git提交；附件自述“尚未写入Git”保留为历史来源说明。状态Review → Changes Requested → In Progress，继续原TASK-0039 / PR #16/#17，不新建任务或重新分配。

当前向后生效的限制：单局≤16票，仍选当前最低普通档；每局购买/填充/结算输入共用300秒截止；累计完整位置≤18、定位仍3、总票额≤96、控制运行≤5400秒。原8个跨版本位置、3定位、52票/2267.262秒账本保留。新16票不追认第8局当时12>8违规，也不容许报价与实际支出失配。

连续推进生产面板与交互状态接入、覆盖卡补排、局末收尾和结算续局。保留已修成果；先核对全部实际入口和旧硬编码、离线回归及既有权限内只读来源，再以最新报价/账本核对完整十局预算并冻结候选。验收仍十局，不是18局；旧8局不拼入。当前44票仅在真实四卡最低价为4票时可覆盖十局；90分钟余量紧凑，不试购、追加定位、挑局或改版拼接。

本次只调整资源授权，不批准新增进程内Hook等技术方式；具体只读新增范围确有必要时另行明确。正常实际受理在后续完整批次中验证，不增加单击定位前置。业务判断/成绩依结构化来源，图像仅导航/标定。

main核对898358f；Workspace Sync ON_DEMAND、0冲突、provider unavailable、6 stale，Git为准。Registry重建/validate后提交推送，原reservation pending-main。统一交付真实结果和受控复算入口等待Review；不合并、发布、提交SVN、扩权或finalize。Subagents: none。

[16票执行修订](support/TASK-0039/EXECUTION-16T-20261014.md) · [Round 5](support/TASK-0039/CHATGPT-REVIEW-5.md)。

## 历史交付：Round 4（新资源值以上文为准）

状态In Progress → Review，未Accepted。唯一Round 4 d58e4eb原文由5b1c8b3接纳，历史评审保留；沿用TASK-0039 / PR #16/#17，不新建任务。功能候选6488ee6实现逐卡重新标定/恢复补排、末球/闭局取消及同局300秒输入截止；报价身份/时效校验契约已回归，但生产实时面板reader及覆盖后实际点击受理仍未证明。

71项离线/入口集成回归通过（23.097秒，exit0）。第4–7位置153格按结构化来源归因，确认未填3/0/4/5；新候选仅出现12个dry发送机会，不改写任何成绩。真实Device.sample以36张历史截图回放恢复链，无设备调用/输入。实际只读--check及四次--results均exit2，购买项不变；本轮未运行真实--start，明确不购买第9/10位置。

原8个跨版本完整启动、3局定位、52票保留；累计控制运行2267.262秒。第6局上界88.57%是真实未达标，第8局12票超单局上限/User接管与证据不足分列。同版十局目标未完成。统一报告含最小只读观测缺口及新10局条件计划：若实时4票/局，需40票、累计92；建议累计完整启动上限18、时长90分钟。仅提案未授权执行，当前96票/2700秒/10位置代码不变。

受控入口：`%LOCALAPPDATA%\AI-Workspace\bingo-voyage-task0039\round4\REVIEW_R4.md`与VALIDATION_R4.json，保留原冻结来源/账本。main安全核对898358f；Registry重建/validate、原reservation pending-main。Workspace Sync ON_DEMAND，0冲突、provider unavailable、6 stale，Git为准。不合并、发布、提交SVN、扩权或finalize。Subagents: none。

## 历史：Round 4接纳及执行范围

接纳d58e4eb的[唯一Round 4](support/TASK-0039/CHATGPT-REVIEW-4.md)，保留全部历史评审。状态Review → Changes Requested → In Progress，继续TASK-0039 / PR #16/#17；6eba235完整重编稿仍为目标规范。

本轮先连续完成离线修复与既有授权内只读准备：第4–7位置逐格关联叫号/覆盖/布局/排队/发送/确认/闭局，修复覆盖卡重标定、恢复补排及局末收尾；调查购买前实时卡数/Bet/报价来源并绑定同一有效面板身份。旧存档/历史成本/手填标签均不得授权购买。当前明确不购买第9/10位置，不要求User手动代买。

原52票/2244.981秒、8个跨版本购买位置和3局定位完整保留；只读设备准备继续入账，离线回放不消费。单局8票/300秒及累计96票/2700秒不变，Round 4不增加额度。第8局12票超限是已发生事故，第6局上界88.57%是真实未达标，二者不得用证据不足混淆。统一交付原候选/新候选回放差异、实际入口回归、报价来源或明确缺口及新候选同版十局所需最小资源计划；不逐步骤等待Review。

main已安全核对898358f；Workspace Sync ON_DEMAND、0冲突、provider unavailable、6 stale，以Git为准。沿用原reservation、重建校验Registry；不新增任务、合并、发布、提交SVN、扩权或finalize。Subagents: none。

## 历史交付（Round 4要求修改）

## 当前交付：2026-10-14重编后统一Review，未达标

TASK-0039继续原PR #16/#17，状态Review，未Accepted。完整购买位置8/10，无同版连续十局通过；历史三局定位和所有失败/未购买尝试完整保留。原规范为6eba235重编稿及Round3，治理接纳67a2cc8，阶段记录3912ca5；旧Review原文保留，与重编稿冲突的单击前置顺序和否认闪动漏点说明仅为历史。

最新User反馈“脚本看起来没有生效，我介入了”对应第8位置：旧存档报价4票，实际Bet3四卡扣12票，超过8票单局上限。程序在扣费后停控，自动填充0次；User确认人工接管。后补证观察应填35/终态亮35，不能归为自动成功。购买前价格核验失效是已发生事故，不以总额剩余或补证Unknown淡化。

实现[1c43e6a](https://github.com/840832144/AI-Workspace/commit/1c43e6afa1484c5825d0f1906a47eefe68075ff3)（最新代码171cf41，报价保护a5c7665）。63项离线/实际入口集成回归通过；真实--check/--start exit2且最终启动零新增购买，stopped_confirmed=true。存档与历史成本仅作观察，预检、资源预留和最终发送均拒绝非实时面板报价；现有授权来源没有可靠购买前价格，当前run_ready=false。不得宣传持续自动玩已完成或当前最低Bet选择已证明。

逐局、Bingo/末段漏点和证据边界见[统一Review摘要](../projects/bingo-voyage/REPORTS/TASK-0039-REVIEW.md)。第5局同批同冻结规则复核可信下界81.08%，尚未证明>90%；第6局下界77.14%，即使Unknown全成功也只有88.57%，真实未达标。第7局有未归属输入；不自动指责User。Bingo覆盖卡安全标定及完整结算/升级续局仍有缺口，其他卡继续运行的修复已经实跑；不把覆盖卡删出分母。

唯一账本累计52票、2244.981秒，含原12票/514.483秒；剩2个启动位置、44票、约455秒不等于可立即消费。每局≤8票/300秒、累计≤96票/2700秒不变；第8局12>8单独列违规。本轮没有开发试购或新增单击定位；开发真实测试须最低普通Bet与最少卡数，正式验收仍四卡。现有剩余位置不能凑出新候选同版十局，不自行增加授权。

受控入口：`%LOCALAPPDATA%\AI-Workspace\bingo-voyage-task0039\REVIEW_REPLAN.md`；recompute_replan.py实际exit0，只代表重建完成，RECOMPUTED_REPLAN.json记录8位置/52票/全部批次不通过。原冻结来源、as-run核验、后续研究重放和补证分别保留，不挑成功局、不改Raw。图像仅导航/标定。

main安全同步898358f；Workspace Sync ON_DEMAND，0冲突、provider unavailable、6 stale，以Git为准。Registry重建并validate，原reservation pending-main，不重新分配。等待ChatGPT统一Review；不合并、发布、提交SVN、扩权或finalize。Subagents: none。

## Goal

以结构化数据完成四卡买卡、开局、合法点格、可靠确认、有限补漏、Bingo目标优先及结算续局。run_ready通过后完整运行，同时按冻结规则取得metric_ready证据；最终以同版连续十局逐局严格>90%、争取加权≥95%验收。6eba235重编稿为当前规范性附件；旧单击定位前置顺序仅为历史。

## Scope

历史90.9%及逐卡超额计量已审计，不作为当前成绩。当前修复全局实际调用链并保留全部失败、Unknown及局末漏点反馈。初始治理基于 main `b0a36c8`，本轮同步 `898358f`；实现隔离于原 `bingovoyage-autoplay@90e97cc` 来源，不将探针树迁入治理 main。图像仅用于低频导航与几何标定。

## Non-goals

其他游戏、通用采集平台、协议写入、奖励/余额修改、充值、Max Bet、Root/CA/iptables 扩权、云部署、飞书发布、SVN 提交、PR 合并均不在本次范围。

## Deliverables

最小实现修复、独立证据核验器、十类离线故障回归、真实可调用的检查/启动/停止/结果入口、受控逐局证据和批次聚合、脱敏 Review 摘要及回滚说明。

## Acceptance

按当前重编稿§5–6验收；原规格不冲突的来源与安全规则继续有效。E 为完整同局非 FREE 应填集合，N=|E∩C|；逐局 `10*N > 9*E`，批次 `20*sum(N) >= 19*sum(E)`。零分母 N/A；数据不完整或语义不明不能输出可验收百分比。连续十局不挑成功局，不以离线测试冒充真实验收。

## Safety

只用已有明确授权实例及资源额度，最低普通Bet；开发试跑应选最少卡数，本轮不另购开发局。正式四卡验收仍四卡；报价/实际消耗不可核对时停止消费。保全原分支/工作树/Raw；单控制者。公开 Git 不含真实卡面、账号、Raw、完整响应/日志、截图原件或凭据。

## Validation

当前63项离线/入口回归、真实拒绝入口和八位置复算见上方当前交付及统一Review摘要；代码/局部验证通过不等于真实十局达标。

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
