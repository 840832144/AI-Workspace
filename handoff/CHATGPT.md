# ChatGPT Handoff

## 2026-09-17 — TASK-0034合并完成；TASK-0035薯片+777现值冻结准备

- PR #7已按User授权以merge commit `051a55195a6a483ce198fe432fe7af29d92444b3`合入main；canonical及三轮Review进入main后，原TASK-0034 reservation返回finalized，旧Task的Gate交付与Git收口Complete。
- [TASK-0035](../tasks/TASK-0035-CR-0922-SNACK-777-FREEZE-PREP.md)由allocator正式分配，In Progress；只覆盖9.22薯片+777。User补充“没有改动”，按现值制作零数值变更方案、清单和冻结候选；forceTurn完整口径已在PR #7正式闭合，不重开业务Gate。
- 相关trunk定向freshness check待执行，先锁实际版本，不直接沿用r6961；复用0033/0034已Accepted方法，排除拳击/挖矿，不做无关全量扫描或哈希。
- 新分支codex/cr-snack777-freeze-prep，原Task完整历史保留；新reservation pending-main。只准备候选，等待ChatGPT Review，不改源配置、不提交SVN、不调参、不正式冻结或发布。Subagents: none。


## 历史 — TASK-0034 Round 3 Accepted（合并前）

- [Task](../tasks/TASK-0034-CR-0922-FREEZE-GATES.md)为**Accepted**；[完整Round 3](../reviews/TASK-0034-CHATGPT-REVIEW-3.md)已落Git，受评d8f1b72，无必须修改项；Round 1/2及历史证据保留。
- [当前Matrix](../projects/cr/REPORTS/CR-20260922-FREEZE-GATES/FREEZE_GATE_MATRIX.md)保持**6 Closed / 4 Conditional / 12 Non-blocking**。G03/G09/G12/G16按原条件触发；规则Closed不等于源配置已满足冻结条件，活动组合仍由User决定。**尚未冻结或发布**。
- Review仅做轻量状态复核，未独立重跑前轮数值、Registry、链接、diff或其他Codex证据；本轮仅落库评审并同步治理状态，不重算、不重跑TASK-0033、不做哈希或全量业务扫描。完整数值留原受控目录。
- 原分支codex/cr-0922-freeze-gates / PR #7等待User明确合并授权；reservation保持pending-main，不新建Task、不提前finalize。不改源配置、不提交SVN、不调参、不冻结、不发布、不合并。Subagents: none。


## 历史Round 3候选 — TASK-0034 Gate状态修订（d8f1b72，已Accepted）

- [Task](../tasks/TASK-0034-CR-0922-FREEZE-GATES.md)为Review；[完整Round 2](../reviews/TASK-0034-CHATGPT-REVIEW-2.md) Needs changes，受评761b08c；经过Changes Requested后只修状态，原分支codex/cr-0922-freeze-gates / PR #7及pending-main reservation不变。Subagents: none。
- [当前Matrix](../projects/cr/REPORTS/CR-20260922-FREEZE-GATES/FREEZE_GATE_MATRIX.md)：**6 Closed / 4 Conditional / 12 Non-blocking**。无无条件业务规则阻塞；不能再写只有2类条件，业务规则Closed与候选配置可冻结分开。
- **G12 Conditional**：选挖矿时，r6961缺id4–12通关奖励必须补齐，或由User明确这些关无通关奖励；同ID/12关结束的规则Closed保留。
- **G16 Conditional**：选拳击或挖矿时，必须移除对应源配置中的相关建造币奖励；关闭建造/移除奖励的决定Closed，前轮分析层排除27槽位不能替代源修改。
- G03（剩余缺档需价值比较）和G09（选777补forceTurn）继续Conditional；其他状态/数值规则不变，不代选活动。
- [报告](../projects/cr/REPORTS/CR-20260922-FREEZE-GATES/README.md)已同步；本轮只做Gate/文档一致性、链接/diff及Registry校验，不重算数值、不读源表、不运行分析工具、不重跑TASK-0033、不做哈希或全量业务扫描。原受控Round 2包数值继续复用，旧Gate统计为历史。
- 下一轮轻量Review只核对上述分类和冻结条件；不改配置、不提交SVN、不调参、不冻结、不发布、不合并或finalize。下方“仅2类条件”为受评历史，当前以本节为准。


## 历史Round 2候选（761b08c，Gate分类已修正）— TASK-0034 请轻量Review Round 2

- [TASK-0034](../tasks/TASK-0034-CR-0922-FREEZE-GATES.md)仍为Review，原分支codex/cr-0922-freeze-gates / PR #7，原reservation pending-main；Subagents: none。
- [Round 1完整记录](../reviews/TASK-0034-CHATGPT-REVIEW-1.md)Needs changes，基线007202e；PR #7 User正式决定已逐项应用。状态经过Changes Requested，当前等待Round 2，不预先写Accepted。
- [Matrix](../projects/cr/REPORTS/CR-20260922-FREEZE-GATES/FREEZE_GATE_MATRIX.md)当前7 Closed、2 Conditional、13 Non-blocking，**无无条件业务阻塞，最多2类条件问题**：选777才补forceTurn；拳击/挖矿仍需比较缺档奖励价值才处理G03。G01/G02退出前置；其他原非阻塞缺口不要求本轮关闭。
- 积分改为溢出连续跨档/末档规则，Pass共享门槛；建造币从受影响模型排除，5处金币缺档仍在；777旧每格一次账本退出当前周期成本。四活动保留可选候选，不决定组合。
- 固定r6961；只读8张受影响表，550条阶段记录、30对Pass、27个建造币奖励槽位排除。源奖励只覆盖挖矿id1..3且有round，未用取模补4..12；G12规则Closed不代表现表齐备或完整12关EV。仅计算层覆盖，没有源配置写入。
- 4项连续结算回归及受影响输出定向核对；Registry工具重建/验证，变更链接/diff检查；不重跑TASK-0033、catalog、全仓业务扫描或哈希。完整数值及[增量复核包导航](../projects/cr/REPORTS/CR-20260922-FREEZE-GATES/README.md)留受控目录，旧Accepted及首轮包保持历史。
- Round 2只核对正式输入应用、旧假设退出当前结论、最多2类条件Gate及源表证据限制。PR保持OPEN，不改配置、提交SVN、调参、冻结、发布、合并或finalize。下方首轮8组问题是历史，不再要求重答。


## 历史首轮 — 2026-09-17 TASK-0034 CR冻结Gate，等待ChatGPT Review

- 新Task：[TASK-0034](../tasks/TASK-0034-CR-0922-FREEZE-GATES.md)，Review，独立分支codex/cr-0922-freeze-gates；TASK-0033保持Complete，不续写。原reservation pending-main，不提前finalize。Subagents: none。
- [报告](../projects/cr/REPORTS/CR-20260922-FREEZE-GATES/README.md)及[Matrix](../projects/cr/REPORTS/CR-20260922-FREEZE-GATES/FREEZE_GATE_MATRIX.md)已经交付；10项Needs Planner Decision、1项Conditional、11项Non-blocking。已闭合子项与整Gate状态分开，冻结依据尚不充分；没有执行冻结。
- 2026-09-17 10:40:04北京时间读取SVN：HEAD r6987，trunk最后内容r6918，相对r6961无路径变化，继续同版r6961。只读23张关联表和既有索引，没有重跑Accepted总表或文件哈希。
- User已确定常规USD Bet=1归95%；新受控CSV为220条参考组合增加决策覆盖，原总表不动。特殊RTP优先级仍待确认，不能把策划决定当配置已符合。
- 价格缺档收敛为同一金额的5处引用；4个阶段样例、9个777圈/轮的条件清盘账本和资源关系可复算。候选保留薯片/777/拳击/挖矿，不替User选四选二。G13因薯片/拳击仍在候选中保持条件阻塞。
- 9份当前正式知识库原文有revision证据；历史数值附件未作当前输入。全局搜索权限不足但已知CashRoyal目录读取成功；不扩大权限，也不声称已检索所有正式资料。8组最小问题集中在Matrix的Q1–Q8，由对应策划/User补规则，不要求程序/线上/运营/支付审计。
- 验证：新工具真实输出、3个RTP边界、220条新旧口径分离、4个阶段手算、777条件清盘、定向价格覆盖和22项Matrix状态一致；AST通过。Registry由工具重建后valid（17 canonical/0 collision，6项既有legacy提示）；新增文档14个相对链接有效，diff检查通过。未重复Accepted工作簿/源缓存/外链/catalog/全仓业务验收。
- 完整数值、受控复核包与证据仅在本机；public Git只有脱敏报告/工具/治理。未改源表、提交SVN、调参、冻结、发布、合并或权限。
- 唯一下一步：ChatGPT Review本轮Gate整理及条件边界；User/策划集中答复Q1–Q8。下方TASK-0033及其他任务记录保留原时点。


## 2026-09-17 — TASK-0033 PR #6已合并，原reservation已finalized

- User已明确批准Git收口；[PR #6](https://github.com/840832144/AI-Workspace/pull/6)于2026-09-17 09:50:41（北京时间）通过merge commit合入main：`998a4d8a90541df25b0cedbcaeba069bbd1a010d`。保留候选f6bf84b、受评bdcdb3d及TASK-0033历史；[Round 1](../reviews/TASK-0033-CHATGPT-REVIEW-1.md)和[Round 2](../reviews/TASK-0033-CHATGPT-REVIEW-2.md)原文未改。
- 合并树与候选直接diff为空；main中的canonical Task、CR Status、Handoff、Registry及两轮Review已核对。Registry valid/16 canonical/0 collision；canonical进入main后，原linked worktree安全快进，再以原reservation执行既有finalize，结果finalized。不新建Task。
- [Task](../tasks/TASK-0033-CR-0922-NUMERICAL-INVENTORY.md)为Complete（整理交付及Git收口），Review Round 2仍为Accepted。固定 trunk r6961 现值整理已通过；22项业务缺口保留；尚未冻结或发布。完整数值与受控附件仍留本机，不新增公开数值。
- 本次只做Git收口；未改配置、提交SVN、调参、冻结或发布，也未改权限。各轮证据限制继续保留，不把合并检查当业务复算重跑。Subagents: none。
- 下方为历史阶段记录；当前事实以本节、Task和[报告](../projects/cr/REPORTS/CR-20260922-NUMERICAL-INVENTORY/README.md)为准，其他任务交接保持原样。

## 历史阶段 — 2026-09-17 TASK-0033 Round 2 Accepted，等待User合并授权

- [完整Round 2](../reviews/TASK-0033-CHATGPT-REVIEW-2.md)已落库：Accepted，评审基线`bdcdb3da6d1367c38e62fe7d45428b752d7e3063`；[Task](../tasks/TASK-0033-CR-0922-NUMERICAL-INVENTORY.md)已更新为Accepted，保留Round 1历史，不新建Task。
- 固定 trunk r6961 现值整理已通过；22项业务缺口保留；尚未冻结或发布。R1/R2均通过，无必须修改项；不等于完整机台/活动周期EV或所有业务定义已闭合。
- 评审独立验证与未复跑项按原文保留；本次不改数值产物或重复业务测试。[报告](../projects/cr/REPORTS/CR-20260922-NUMERICAL-INVENTORY/README.md)提供当前状态，受控包及VALIDATION-R1.json保留受评版本证据，不将旧状态当当前状态。
- PR #6和原分支`codex/cr-0922-numerical-inventory`保留，等待User明确合并授权；原reservation pending-main。不改配置、不提交SVN、不调参、不冻结、不合并、不提前finalize；完整数值和受控附录继续留受控目录。Subagents: none。
- 下方为历史阶段记录；其他任务交接保持原样。

## 历史阶段 — 2026-09-16 TASK-0033 R1/R2修订完成，等待Round 2

- [完整 Review](../reviews/TASK-0033-CHATGPT-REVIEW-1.md)已落库：Needs changes，基线04f7b29；Task经过Changes Requested，修订后回到Review，等待ChatGPT Round 2。
- R1：特殊RTP条件页/CSV保留同版全部9行、空/重复ID、等级上下界、5个活动条件与本表枚举；与常规85/95分开。优先级/实际生效继续关联G01/G02。
- R2：6处缺缓存、2处Excel错误缓存、19处外链分别定位，G05补齐说明字段异常；不把错误字符串用作数值，不判派奖/运行故障。
- 最终XLSX实际5699个公式（XML `<f>`自动计数），全部缓存与Python复算一致；19964个数值输出一致，公式错误/缺缓存均0；16页、4923条阅读记录。4个改动页视觉复核；81个特殊配置源字段和2处错误原式/缓存独立读取一致；非编辑范围50625个既有阅读单元格值/类型保持一致。
- [整理报告](../projects/cr/REPORTS/CR-20260922-NUMERICAL-INVENTORY/README.md)与验证文件已统一实测数字，最终统计工具排除以“=”开头的说明。catalog/repository/Registry/diff通过；3项R1/R2回归通过。
- 固定trunk r6961，22项业务缺口保留；完整数值和受控附录留本机。没有重新访问SVN或混版，源公式/外链未独立求值，完整机台/活动EV仍未闭合。Round 1未独立复跑catalog/Registry/视觉的限制照录，不能将本轮Codex验证冒充第二轮Review。
- 原分支codex/cr-0922-numerical-inventory、PR #6；原reservation pending-main。不新建Task、不调参、不改源表、不提交SVN、不冻结、不合并、不finalize、不改权限；Subagents: none。
- 下方首轮交付为历史候选，当前交付以本节和报告为准；保留其他任务交接。

## 历史候选 — 2026-09-16 TASK-0033 首轮交付（04f7b29）

- [TASK-0033](../tasks/TASK-0033-CR-0922-NUMERICAL-INVENTORY.md)：Review；固定trunk r6961，读取2026-09-16 17:58:52（北京时间）；Subagents: none。
- [整理报告](../projects/cr/REPORTS/CR-20260922-NUMERICAL-INVENTORY/README.md)提供范围、版本、完整交付文件名、方法和验证。完整15页总表、资源关系、明细与22项缺口仅保存在本机受控复核包，未上传public Git。
- 请复核表/字段/行ID追溯、概率分母、阶段清零、枚举隔离、状态期望和毛下注/机器净耗/实付区别。不能把读取完成称为数值全部闭合；不得用历史资料补当前缺口。
- 首轮XLSX实际5699个公式（Round 1已纠正原计数误报），19909个数值一致，16个关键源格独立读取通过；源外链/缺缓存未独立复跑，完整机台/活动整轮EV尚未建立。当时ChatGPT Review尚未执行；已发布Round 1及当前修订见上文。
- User只授权现值整理/复算；不设优化目标、不选四活动组合或排期、不改配置、不作SVN提交/冻结/发布；排除广告、生命周期、线上运营与技术审计。附件v0.1扩展指令不覆盖本轮User范围。
- 候选 `codex/cr-0922-numerical-inventory` 待Review；原reservation pending-main，不重新分配、不提前finalize。既有TASK-0032合并/切换事实及下方其他任务交接保持历史。

这是 ChatGPT 的固定交接入口。长期事实必须同步到 Capability contract、项目 Memory / Status、Task、RFC、ADR 或正式 Review，而不是只留在聊天中。

## 2026-09-16 — TASK-0032：已合并并切换单仓入口

PR：[AI-Workspace #5](https://github.com/840832144/AI-Workspace/pull/5) 已按 User 最终授权于 2026-09-16 15:03:31（北京时间）使用 Create a merge commit 合并，merge commit `3c214e2ca75eb82c16af6a186f7366fb3c249140`。当前日常入口为 AI-Workspace `main`，CR 资料与工具只写 `projects/cr/`；原 reservation 已 finalize。旧 cr_design 保留，不归档、不删除，权限不变。

- Task：[TASK-0032](../tasks/TASK-0032-CR-SUBTREE-PUBLIC-MIGRATION.md)，Complete；Review Round 1 Accepted；Subagents: none。
- 合并前 main 与 CR 来源未变，候选 `04a7568` 相对 `83eadec` 只有已授权评审记录；PR #2/#4 既有共享文件工作留在各自分支，无新增 main 冲突。
- 合并后 `1409737` / `fe07557` 均为 main 祖先；根与 CR 两入口、5个唯一 Skill、276文件映射和工具边界通过，catalog 14工作簿/0异常，repository 0错误/0警告。
- canonical 进入 main 后按原 reservation 返回 `finalized`；没有新分配 Task。候选分支 `codex/cr-subtree-migration@04a7568` 保留作历史，后续从最新 main 建独立分支/PR。
- 日常 CR Git 资料和工具只写 `AI-Workspace/projects/cr/`，旧库不再双写。公司 SVN 正式配置流程、CR/101 隔离与 HuuugeCollector 历史副本定位不变。
- [迁移报告](../docs/migrations/CR-MIGRATION-20260916.md)记录实际合并、最小必要验证和回滚。下方候选/Review 为历史：Review 未独立复跑，81项测试是此前本机候选验收，不是本轮或 GitHub CI。
- 未执行旧库归档/删除、权限调整、源表修改、同步 apply、SVN 提交、采集、部署或云端发布；手工 Project Sources 尚未上传，联网 Agent 以最新 Git main 为准。

## 历史阶段：2026-09-16 TASK-0032 ChatGPT Review Round 1 Accepted（合并前）

PR：[AI-Workspace #5](https://github.com/840832144/AI-Workspace/pull/5)，ChatGPT Review Round 1 已 Accepted（基线 `83eadec`）；等待 User 批准最终合并与切换。须使用 merge commit 保留 CR 导入历史；本轮不合并、不切换、不 finalize，旧库归档仍需另行授权。

- Task：[TASK-0032](../tasks/TASK-0032-CR-SUBTREE-PUBLIC-MIGRATION.md)；分支 `codex/cr-subtree-migration`；Subagents: none。
- 完整评审：[Round 1](../reviews/TASK-0032-CHATGPT-REVIEW-1.md)，来源为 PR #5 已发布评审，基线 `83eadec13cb4a03fa5b75de8dcbdd1f83cb61048`；无必须修改项。Review 未独立复跑测试、工作簿检查或备份恢复，未重复历史敏感内容审查，不能把报告的81项本机测试称为本轮独立验收或 GitHub CI。
- Task: Accepted；Execution status: 等待 User 批准最终合并与切换。本轮只固化完整评审、更新记录、重建/验证 Registry 并推送候选，不启动后续合并或切换流程。
- User 已批准 public 迁移以及三个 Top Tycoon 工作簿的原始记录与历史；不再清洗这三份文件，不新增重复哈希工作。其他敏感内容限制不变，权限不改。
- 来源 CR main `1409737648b15f602586b79ade7e0c3e7a3813a0`；原样导入 `fe07557ce5052da6a0eaaaaa1207b416ac081474`，直接 diff 为空且13个原提交保留。适配另行提交。
- 根/CR 规则、四启动文件、三 Agent 入口、唯一 Skill 路由、Context 与同步路径已适配。公司 SVN 正式配置保持原流程，HuuugeCollector 为历史副本，CR/101 分离。
- [迁移报告](../docs/migrations/CR-MIGRATION-20260916.md)记录来源、276文件映射、审查、验收与回滚。全新克隆的根/CR 两入口验收通过：14源表、36卡包附件、845935单元格、81项测试通过；上述为原迁移验收记录，Round 1 未独立复跑；现已 Accepted，尚未正式切换。
- 不执行源表修改、同步 apply、SVN 提交、真实采集或部署。最终合并和旧库归档仍待 User 确认；reservation 保持 pending-main，canonical 进 main 后才 finalize。

## 既有 Review 记录（保留原时点）

- Updated: 2026-08-29
- Current Review request: TASK-0019 — 项目全景说明与独立进度文档
- TASK-0019 status: `Accepted`
- Project key: `WORKSPACE`
- Execution rule: 并行任务使用独立 branch / linked worktree；不得覆盖其他任务或未提交修改

## TASK-0019 — Accepted Closure

- Review branch：`codex/task-0019-overview-progress-refresh`，基于 `main@c74c85a9524d1524ea3696835509de2a55e9f524`；未 merge 旧 `task-0019-overview-progress`。
- TASK-0019 Review Round 1 正式记录为 `reviews/TASK-0019-CHATGPT-REVIEW-1.md`：Decision `Needs changes`，reviewed commit `9403a09a445fd37548c78b3fc21709e91f5406d9`；本次只修指定的文档事实与验收缺口。
- TASK-0019 Review Round 2 正式记录为 `reviews/TASK-0019-CHATGPT-REVIEW-2.md`：Decision `Needs changes`，reviewed commit `e05d781e8aa54a6d10f1d0e44a1f84310fdf847e`；`e05d` 是已审基线，不是本轮新提交。
- TASK-0019 Review Round 3 正式记录为 `reviews/TASK-0019-CHATGPT-REVIEW-3.md`：Decision `Accepted`，reviewed commit `ccc1610a69808f7516e4d215d2177454021d108a`；canonical Task 已更新为 `Accepted`。
- Git deliverables：`docs/overview/AI_WORKSPACE_PROJECT_OVERVIEW.md`（稳定说明）与 `docs/status/AI_WORKSPACE_PROJECT_PROGRESS.md`（动态状态），不得合并职责。
- 核验 main：Huuuge `4a5dddf`、CF_collect `4df10ec`、Document Assistant `b0292c3`；均与远端一致且工作树干净。
- 必查口径：Huuuge First Run 保持 `Blocked`；正式 RC4 记录仍为 `Pending`；User 实跑仍为 `Failed/Invalid`。正式 Collector READY 未被可复核证明；只确认临时 SSL 捕获后进入 User 操作阶段，游戏由 User 亲自操作。Bet/RTP `Unsupported`。
- 必查历史与入口：进度文档第 7 节已补历史 TASK-0018 文件冲突和 ChatGPT 直写飞书地区限制；全景说明六个核心 Git 入口已统一到 `c74c85a...` 核验基线。
- 必查 Provider 分离：Workspace Sync 为 `ON_DEMAND / provider unavailable / stale 6 / conflicts 0`；Document Assistant 为 `Available`，healthcheck token/API/Drive 全部 `ok`。
- 飞书验收：Round 3 只原位 replace 既有进度文档，没有创建副本，项目全景飞书文档未写；进度文档正文、document ID/链接和 `tenant_editable` 权限回读通过，Hub 保持 17 个登记项、`unique_links=true`，进度标题唯一。
- Scope：未修改业务仓库；未启动模拟器、Root、Frida、Collector，未执行 Spin；Subagents: none / OFF。
- Validation：Round 3 定向断言 12/12、Task 23/23、Context 13/13、Memory 44/44、Registry 13 canonical / 0 collision / valid、Context refresh 70 sources / 0 broken link / 0 secret issue、changed-document scan 11 files / 0 broken link / 0 secret assignment / 0 stale READY / 0 new Task、项目全景 hash 不变与 `git diff --check` 通过。
- 决策边界：P0 Reliability Hardening 只保留 Decision proposal；未获 User 批准不创建 Task、不进入实现或运行。
- Closure：治理分支 fast-forward 合入 AI-Workspace `main` 后结束 TASK-0019；后续唯一动作是等待 User 审议 P0 Reliability Hardening Decision proposal。

## TASK-0023 — Idea Governance & Product Roadmap

- ChatGPT Review Round 2：Accepted；正式记录为 `reviews/TASK-0023-CHATGPT-REVIEW-2.md`，reviewed commit 为 `bc0d3ad1e519fb908dce53a78a35f9c3687a5b51`。
- Idea Governance 与 Planner Writing Style 已转为 `Accepted / Active`；Product Roadmap 和统一技术术语规则正式生效。
- 收口前回归：Context / Source Pack 62 sources、0 broken link、0 secret issue；Task 23/23、Context 13/13、Memory 35/35、两个 PowerShell 入口、Registry 10 canonical / 0 collision 与 Doctor 全部通过。
- Workspace Sync 保持 `ON_DEMAND`、0 conflict；provider unavailable，6 个发布项保持 stale，没有启用 WATCH。

- ChatGPT Review Round 1 结论为 Needs changes；Roadmap / Idea Governance 主体已通过，唯一 Required Fix 是准确、克制、面向受众的技术术语规则。
- `standards/PLANNER_WRITING_STYLE.md` 已成为唯一 canonical 规则源；Core Rules、Repository/Bootstrap/Global AGENTS、Project Instructions、ChatGPT Bootstrap、Generic Agent 入口和 Context Hub 均引用同一标准。
- ChatGPT 单文件 Source Pack 与 6 个拆分来源清单均包含 canonical 规范正文，不再只依赖 Core Rules 摘要。
- 默认面向策划使用准确且可理解的研究表达；复现、工程判断、授权、合规、安全或风险依赖真实机制时必须保留 Root、Frida、Hook、逆向分析、协议解密、校验绕过、系统修改、exploit 等精确术语。
- 规则明确禁止通过改名或模糊化规避安全策略、权限检查、User 授权或 Review，不得弱化真实风险或夸大被动研究。
- Context / Source Pack 已刷新为 62 sources、0 broken link、0 secret issue；Task 23/23、Context 13/13、Memory 35/35、两个 PowerShell 入口、Registry 10 canonical / 0 collision 与 Doctor 均通过。
- Workspace Sync 保持 `ON_DEMAND`、0 conflict；provider unavailable，6 个发布项保持 stale，没有启用 WATCH。

- User 已批准建立新的独立治理任务；正式 Candidate 经 allocator 晋升为唯一 canonical TASK-0023，reservation 保持 `pending-main`，未手工指定编号或编辑 Registry。
- 已建立唯一 Git Product Roadmap，固定 `Current / Backlog / Ideas / Done`，并明确它不替代 Task、Documentation Hub、Knowledge、Memory 或项目 Status。
- ChatGPT 新规则：主动提出长期产品能力、Workflow、Capability、Collector 或 UX Idea 时，自动防重、分类，并在相关 Task 收尾时向 Codex 生成 Idea Handoff，不依赖 User 手工提醒。
- 唯一正式飞书 Product Roadmap 已创建、回读、企业内可编辑并自动登记；项目全景说明已原位增加 Roadmap 入口，导航中心当前登记 15 份正式文档。
- 真实临时 Idea 已进入 Ideas 并回读，随后删除；正式 Roadmap 已恢复，四分区各出现一次。
- Registry 10 canonical / 0 collision；Task 23/23、Context 13/13、Memory 35/35、两个 PowerShell 入口和 Workspace Doctor 通过；Context refresh 62 sources、0 broken link、0 secret issue。
- TASK-0022、Cash Frenzy、Huuuge、Document Assistant 和 Workspace Sync 状态均未修改；`ON_DEMAND` 保持不变，WATCH disabled，Subagents: none。
- Review 重点：分类 Gate 是否足够严格、Top Tycoon 的 Current 表达是否符合 User 给出的顺序、ChatGPT Idea Handoff 是否既主动又不会越权创建 Task。
- 收口：完成 deterministic regression 后合并并 push main，在原 allocator worktree finalize TASK-0023 reservation，复验 0 collision 后清理分支/worktree。

### Failed attempts

- Candidate 首次使用带说明的 User decision 文本，被 allocator 按枚举 Gate 拒绝；修正为规范 `Approved` 后才分配 canonical ID，首次失败未占号。
- 首次临时发布脚本因 CommonJS 不支持 top-level await，在编译阶段退出且没有云写入；改为 `async main()` 后完整发布与恢复通过。
- 当前 Codex 会话的旧 MCP 进程缺少 `register_document`；其 `get_document` 回读会按旧 Registry schema 写回，导致项目全景说明治理 metadata 暂时丢失。未创建副本；使用 Document Assistant 当前 `main` 新进程重新登记后，Hub 恢复 15 条、链接唯一，项目全景与 Roadmap 均存在。

## Allocation and Current Queue

创建 TASK-0021 前已从 Git 最新 `main@6610feff2acbb48e9058b237c3a12332394b7221` 完整枚举 `tasks/` 根目录；`TASK-0021` 未被占用，创建后复验为唯一 canonical 文件。

当前相关任务：

- `TASK-0016-Automatic-Cross-Conversation-Memory-Curation.md`：`Review`，安全加固继续在独立 worktree 处理；
- `TASK-0018-Huuuge-Lottery-Numerical-Breakdown-Report.md`：Huuuge Lottery 数值报告主线，范围不变；
- `TASK-0019-AI-Workspace-Overview-and-Separate-Progress-Documents.md`：`Ready`，其两份源稿将成为 Live Context 的重要输入；
- `TASK-0020-Task-Allocation-and-Namespace-Governance.md`：`Ready`，负责 Task Registry、allocator 和历史冲突治理；
- `TASK-0021-Workspace-Live-Context-Hub.md`：`Ready`，负责实时 Context、飞书协作、Workspace Sync 和行文规范。

历史 TASK-0018 编号冲突继续由 TASK-0020 处理。执行任何 0018 时必须使用完整文件名，不能只写编号。

## TASK-0021 Objective

解决 ChatGPT Project Sources 需要手工下载、编辑、重新上传，以及多个会话 / Agent 并行时上下文不能及时同步的问题。

目标链路：

```text
稳定 Bootstrap / Project Instructions / AGENTS
                    ↓
              Workspace Sync
                    ↓
       最新 Context Manifest 与相关文档
          ├─ Git canonical truth
          ├─ 飞书协作与展示层
          └─ Host-specific local context pack
                    ↓
       ChatGPT / Codex / Trae / 策划共同工作
```

核心要求：

1. 优先验证并采用飞书知识库；Wiki 条件不满足时使用专用飞书 Drive 文件夹 + Docx，不能回退到手工搬运 Markdown。
2. Git 继续是 Task、ADR、Capability、规则和实现状态的 canonical truth；飞书提供多人协作、在线编辑和面向人的入口。
3. Git-authoritative 内容只向飞书发布；飞书协作草稿进入 Memory Candidate / Review，不静默覆盖 Git。
4. ChatGPT 直接 Feishu MCP 暂不可用时，通过自动 Git mirror 获取最新 Context，不能把 Project Sources 当实时状态源。
5. 建立 `standards/PLANNER_WRITING_STYLE.md`，禁止单词 / 短句逐行排版，统一正常中文段落、结论—依据—下一步和策划步骤写法。
6. 为 ChatGPT、Codex、Trae / DeepSeek 提供各自的 Workspace Sync Binding；无法同步时明确显示 stale / unavailable。
7. 支持 OFF / ON_DEMAND / WATCH，Pilot 后默认 ON_DEMAND；未经 User 批准不得生产启用 WATCH。

## Confirmed Baseline

- ChatGPT Project Sources 是快照，动态状态当前仍需手工替换；
- AI Document Assistant 已支持飞书 Docx、Drive、搜索、创建、替换和权限管理；Wiki 工具目前只在架构中预留，尚未实现；
- ChatGPT 直接 Secure MCP Tunnel 目前受 OpenAI Control Plane 地区限制，Codex 本地 `feishu-docs` 正常；
- TASK-0016 已提供 Git-backed Memory Candidate、Review、Public / Private / Local-only 路由，可作为 Feishu 草稿入 Git 的基础；
- TASK-0019 将生成项目全景说明和项目进度文档，可由 TASK-0021 纳入 Live Context，但不得复制或覆盖其正在执行的工作。

## Shared Boundaries

- TASK-0021 必须先完成 Reuse-first Feasibility Audit，再决定 Feishu Wiki、Drive Folder 或其他 fallback；
- AI-Workspace 与 document-assistant 分别使用独立 branch / linked worktree；发现活动任务重叠时停止并报告；
- 不修改 Huuuge Collector、Lottery 报告数据、Capture、SVN、游戏请求、奖励、余额或服务器状态；
- 不把 Secret、Raw Capture、账号、完整响应、逐笔余额、Feishu token、document token、private URL 或本机 Registry 写入公共 Git、飞书正文或日志；
- 不把飞书设为代码、Task、ADR 或运行证据的唯一真相源；
- 不静默部署公网服务、付费 SaaS、GitHub Secret、管理员权限或生产 WATCH；
- 不自动合并冲突，不直接覆盖 `main`，不声称 Project Sources 已自动更新。

## Exact Next Action

TASK-0019 已 Accepted。User 审议 P0 Reliability Hardening Decision proposal；未经明确批准不创建 Task、不进入实现或运行。在新的 User 决定前不启动业务环境。
