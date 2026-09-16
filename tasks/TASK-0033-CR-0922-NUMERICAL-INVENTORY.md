# TASK-0033 — CR 9.22 全数值整理

- Status: Review
- Execution status: R1/R2 修订完成，等待 ChatGPT Review Round 2；固定 trunk r6961，22项业务缺口保留，原 reservation 保持 pending-main
- Project key: CR
- Owner: User
- Executor: Codex
- Priority: P1 / 2026-09-19 前配置冻结依据
- Date: 2026-09-16
- Updated: 2026-09-16
- User decision: Approved（仅整理与复算）
- Related tasks: TASK-0032
- Subagents: none

## Goal

为 CR 2026-09-22 上线前的数值核对提供“全系统数值总表＋资源产消及系统关联说明＋可复算公式/阶段成本/奖励期望/返还率＋疑问与缺失清单”，交 ChatGPT Review。配置希望本周内冻结，最晚2026-09-19；本 Task 不授权改配置、冻结提交或发布。

## 来源与边界

- 唯一现行数值输入为公司 SVN 最新 trunk；先记录实际读取时间、完整 URL、revision，再以同一固定 revision 读取本轮所有配置。完整内部 URL 与配置值保存在本机受控产物；Git 记录版本、范围、方法和脱敏交接。
- 不混用 dev、101、日期附件、旧报告或本机未提交配置。已有 CR Skill/脚本仅复用读取和推导方法，旧硬编码数值不得成为本轮输入。
- 仅还原、整理和复算现有数值。优化目标未定，不自定留存、付费、回收目标，不提出或执行调参，不写源配置，不提交 SVN。
- 覆盖实际存在的货币与价值换算、Bet/RTP、机台奖励、等级/VIP、免费福利、任务/常驻系统、活动、卡包/卡册、商城/礼包/Pass；以 trunk 目录补全。只有确认不存在才标“不适用”；无法访问或不明字段标缺口，不等同不存在。
- 薯片、777、拳击、挖矿分别列获取、消耗、阶段成本、奖励、返还。实际组合未定，一般同时开两个，不默认四个全开，不决定组合或排期。每个系统单独复算，组合量只保留参数关系。
- 常规机器 RTP 沿用 User 规则：美金 Bet>1 为85%，<1 为95%；美金 Bet 换算和=1归属读 trunk。无法确定或冲突时单列待确认，不修改。新手或其他覆盖配置单列适用条件，不混入常规规则。
- 排除广告经济、生命周期与老客迁移、线上生效与观测、买量运营需求，以及程序、埋点、支付链、部署等技术审计。线上日志、运营数据和技术验收不是本 Task 前置。

## 交付与敏感性

1. 首次反馈锁定的 trunk revision/时间、实际系统及配置目录、初始缺口，并继续可整理部分。
2. 受控本机交付完整总表和明细，字段至少含系统、表名/Sheet、字段、行ID/Excel行、现行值、条件、单位、公式、分母、来源 revision。
3. 分开毛下注、机器返还、净金币消耗、系统消耗、实付美元和配置折算价值；不把价值分/美元折算金币当真实现金，不猜不明除数。概率用归一化权重，门槛和奖励按同组主键关联；无法计算保留缺口。
4. 缺口逐项写明缺什么、影响哪项计算、需谁补充。对于状态相关/无放回/保底规则，只计算配置能证明的条件量，不伪造统一玩家期望。
5. AI-Workspace 保持 public：不上传完整 trunk 配置、内部 URL、本机受控路径、账号、日志或未经明确批准的完整商业数值。公开 Git 保存工具、脱敏目录与任务交接；本轮不自动发布云文档，不回写旧 cr_design。

## 执行与验收

- Git 基线 `a75630ac14eb60c7caf5b7663e58428516614f62`；独立 linked worktree/branch `codex/cr-0922-numerical-inventory`。
- 完整 Task Registry 查重：15 canonical、0 collision、valid；现有迁移 TASK-0032 已 Complete，无同目标 active Task。开放 PR #2/#4 不属于本范围，共享 Handoff/Registry 只增补本任务。
- 正式 allocator 返回 TASK-0033，原 reservation 保持 pending-main；不提前 finalize、不重新占号。
- Workspace Sync：ON_DEMAND，provider unavailable，stale 6、conflicts 0；Git 为真相源，不把外部服务缺失作为整理前置。
- 先锁定 SVN 版本并完成目录盘点，再按依赖读取/复算。只读原表；本机固定版本输入不进入 Git，不重建退役资料快照库。
- 复用只读 XLSX 提取器，核对字段、行ID、单位和关联；对输出做实际来源抽样、代表性手算、缺口传播和公式边界检查，不新增文件哈希校验。
- 按项目规则运行 catalog、validate_repository 及相关最小校验；Task/Status/Handoff 随状态更新，Registry 由工具重建。最终提交/推送候选分支并交 ChatGPT Review，不自行合并或写 Accepted。

## 当前进展与下一步

2026-09-16 已接收并落库 [ChatGPT Review Round 1](../reviews/TASK-0033-CHATGPT-REVIEW-1.md)，评审基线 `04f7b2953dfbd792523ee89778f2fc1d0fc9562f`，结论 Needs changes。状态从 Review 转 Changes Requested；User 仅授权 R1 特殊 RTP 阅读层和 R2 源错误缓存/最终 XLSX 计数修订，不新建 Task。R2已纠正初轮公式数量误报；下方交付与验证数字已更新为最终XLSX实测。完整数值和受控附录不进入 public Git。

本轮统一读取trunk r6961，锁定时间为2026-09-16 17:58:52（北京时间）；trunk最近内容提交r6918。965个工作簿目录已登记，862个工作簿提取177102行、11850字段、1736156个非空/公式单元格；210份机台/地图JSON中209份可提取，1份语法读取缺口，44份其他文件只列目录。没有使用dev、101或历史资料数值。

[整理报告](../projects/cr/REPORTS/CR-20260922-NUMERICAL-INVENTORY/README.md)记录交付清单与重建方法。完整16页总表、资源关系、CSV/JSON明细、公式和22项具名缺口保存在本机受控交付包，未上传public仓库。可复算部分包括63840条Bet参考换算、51072条四活动获取条件和548个阶段、状态边际奖、VIP/福利/Pass/卡包组成和商品标价；不能计算的完整机台/活动EV、返还及当前枚举规则保留缺口，不称全部数值闭合。

附件 `CR_922_Codex_首轮审计任务_v0.1.md` 是参考材料；其广告、生命周期、线上/技术审计、优化和哈希等扩展指令不覆盖本Task中User明确范围。

## 本轮验证与Review要求

- 16个关键源格以独立XLSX读取器抽核一致；6个缺值、除数及离散门槛检查通过。
- 最终XLSX实际5699个公式（XML `<f>`自动计数），全部缓存与Python复算一致；19964个数值输出一致，公式错误/缺缓存均0；16页、4923条阅读记录。本轮渲染复核4个改动页及特殊条件的完整横向字段/末行；首轮15页视觉记录保留为历史，未声称本轮重跑全部视觉检查。
- 源表19处外链、6处缺缓存和2处Excel错误缓存分别保留；源公式未独立重跑，1份JSON模板读取缺口不自动判为程序加载失败。配置表存在不证明9.22已启用。
- 提交前main安全fetch仍为 `a75630a`，PR #2/#4 未出现新共享文件增量；保留其他任务Handoff及历史记录。
- catalog实际执行：14工作簿、0读取异常；repository：0错误、0警告。Task Registry工具重建后valid、16 canonical、0 collision；本轮新增/修改的三份Python工具AST通过，3项R1/R2最小回归通过，git diff --check通过。catalog只生成本机时间/mtime变化，已排除该无业务变化。本任务原reservation仍pending-main，未重新分配、未finalize。
- 后续由ChatGPT Round 2 Review本轮R1/R2及其相关输出一致性；对应策划/配置负责人补充现行定义。本轮不改配置、不冻结、不发布，不作User未指定的组合或优化目标，不要求技术审计/线上数据作为整理前置。

## Round 1 修订交接（2026-09-16）

- 流程：Review → Changes Requested（Review落库提交3f6b042）→ Review / 等待Round 2；Needs changes结论原文未改写为Accepted。
- R1：新增特殊RTP条件阅读页/CSV，保留同版全部9行、空/重复ID、5个活动条件、等级上下界、rtpTier原值和本表注释；常规85/95规则不变。G01/G02继续保留优先级、边界和实际生效缺口，不推断线上行为。
- R2：补齐2处错误缓存；6处缺缓存、2处错误缓存、19处外链各自可追溯。G05明确为说明字段异常，不判定派奖/运行故障；原公式和缓存照录，不补0、不修源表。
- 计数根因：旧验证器把全系统总览E7中以“=”开头的说明字符串误当公式。现按最终XLSX的`<f>`元素计数，并用实际单元格公式类型和逐页复核数交叉确认；不硬编码公式数量。
- 新增特殊配置81个源字段位置与同版原XLSX一致；2处错误缓存的原式/缓存由独立读取器核对。50625个非本轮编辑范围的既有阅读单元格值/类型保持一致。源公式及外链没有重新求值。
- Task/Status/Handoff/报告/验证文件与PR正文以最终产物实测为准。完整总表、受控附录及固定版本源表仅在本机；复核包增加两份同版源表用于R1/R2复查。首轮ZIP/XLSX留受控备份。
- main仍a75630a、候选受评基线04f7b29；PR #2/#4 head未变化，共享文件仅修改本Task段落与工具生成Registry。Workspace Sync为ON_DEMAND、provider unavailable、stale 6/conflict 0，无外部发布。
- 22项缺口不要求本轮关闭；原reservation保持pending-main。本轮无重新分配、调参、源表写入、SVN提交、冻结、合并、finalize或权限变更。Subagents: none。
