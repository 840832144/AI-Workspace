# TASK-0033 — CR 9.22 全数值整理

- Status: In Progress
- Execution status: 范围已登记；待锁定最新 trunk 并盘点复算
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

范围已正式登记。下一步读取远端 trunk HEAD，锁定统一 revision，补全覆盖目录，优先复算资源换算、常规 Bet/RTP 边界、四活动阶段成本/奖励与卡包关联；不能由配置确定的项目保留缺口。
