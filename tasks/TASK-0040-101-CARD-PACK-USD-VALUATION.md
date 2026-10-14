# TASK-0040 — 101 卡包美元价值计算

- Status: Complete
- Project key: GAME-101
- Owner: User / ChatGPT
- Executor: Codex
- Priority: P1 / User 已确认范围
- Date: 2026-10-13
- Updated: 2026-10-14
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

逐项执行规格第 8 节：输入版本与缓存身份、完整 packId 覆盖、实际抽取规则、美元单位、奖励不重复计值、各星级及不同规则独立复核、模型误差、工作簿实际数值/缓存/布局、只读边界、Registry 与交接。条件与缺失单列。Round 2已接受声明范围内的交付；Accepted独立于Git生命周期，本次合并及finalize另有User明确授权，见下文。

## Gate 0

- 最新 main b0a36c8 已 fetch 并 fast-forward 检查；独立 linked worktree 分支 codex/101-card-pack-usd-20261013，包含规格 commit 541e190。
- 完整 tasks scan/validator：18 canonical、0 collision、valid，6 条已审计 legacy 提示。已 fetch 全部远端分支并搜索 tasks，未发现 GAME-101 或同目标 canonical/candidate/companion/review；既有保留号与本范围无重叠。
- 既有 allocator remote-CAS 分配 TASK-0040，pending-main；token 留受控本机。GAME-101 未发现已有映射，使用规格合法 project key。
- Workspace Sync：ON_DEMAND，provider unavailable，stale 6，conflicts 0；以最新 Git 为准，不覆盖旧快照。
- 附件与 PR 中完整规格逐行一致。治理登记提交推送后开始业务读取及计算。

## 实际交付与证据

- Gate 0 登记 commit 为 `4f672ee`，业务计算在登记推送之后执行。输入为101指定只读trunk工作副本r15740，状态干净；22份相关工作簿冻结在源目录外。相关本地服务端实现另有独立SVN身份，未把配置版本当作代码版本或线上生效证明。
- 目标季29个packId、80条规则，覆盖1—6显示档；6档为Ace包，实际卡片只有1—5星。全部116个seasonId+packId组合保留身份，历史/未来不混算。没有按共享itemId合并变体。
- 8个可复算合成状态、2类实际UID权重档、每组50,000次抽样，共464条情景结果；另有29包权重敏感性对照。每组有种子、分半样本与抽样区间。持卡状态为Hypothesis，不是线上人群。
- 主值是单次领取窗口的条件模型估值：本包、最多一次指定星星箱及其返包、随后领取新增完成奖励；后续自然产包计划为空。章节、整册和兑换不重复计值。它不是全生命周期价值、已批准统一面值或实际售价；无面值/实售价证据列为N/A。
- 美元基准来自101自身已识别的纯钻石配置USD报价与钻石兑金币链，固定VIP0及常规复购条件；排除卡包附赠与其他道具混合，不用CR汇率或打点系数。类型18按101加成金币实现计算。
- 已实际生成《101_卡包美元价值.xlsx》、口径说明、输入/代码来源清单、参数、分析脚本、独立复核脚本、一键入口和执行记录。路径与验证入口见 [产物导航](support/TASK-0040/ARTIFACTS.md) 和 [脱敏验证摘要](support/TASK-0040/VALIDATION.json)。完整数值、源码及实现全部留受控本机，没有新增业务远端。
- 独立源表解析核对141,370个字段位置，7个整包例子覆盖全部显示档和专用单规则包，5,040个进度/天数概率边界组合；零候选、容量不足、有限重抽、重复星星、无增量对照、奖励不重计、兑换阈值/冷却和独立美元链均已检查。108项独立检查通过。
- 工作簿7页签具备公式、情景选择、缓存和来源定位；真实输入变更及选择器重算通过。最终导出与脚本结果进行1,972个关键单元格数值回读，检查错误值、空公式缓存与外部链接。原生Excel/WPS打开和线上游戏行为未验证。
- 失败记录保留在受控执行记录：生成类无SVN身份、未装scipy改用标准库、独立检查入口错误修正、长文本布局修正、结构不可能事件的抽样区间修正。未以删除业务断言通过验证。
- 没有源配置/业务代码写入、SVN写操作、购买、账号访问、采集、发布或权限调整。代码/源表直接比对未变。Subagents: none。

## Review 与剩余边界

### 当前 — PR #19已合并 / 原reservation已finalized

- 2026-10-14执行[User授权评论6159032032](https://github.com/840832144/AI-Workspace/pull/19#issuecomment-6159032032)，范围仅为TASK-0040 / PR #19及对应Git生命周期。未新建Task，不合并其他PR，不删除原分支。
- 最新main同步及Registry校验通过：19 canonical、0 collision、valid，6条已审计legacy提示。候选head保持`721768188f7910014428272abb72e41f4602e6c1`；相对受评基线`9ce1b6a`只有治理记录变更。GitHub返回statuses和PR触发workflow_runs均为空，不记为CI通过。Workspace Sync为ON_DEMAND / provider unavailable / stale 6 / conflicts 0，以Git为准。
- PR #19转为Ready后，按核对过的head使用merge commit于2026-10-14 09:56:27（北京时间）合入main：`898358ffccbfa4d9b909d43de48ae794a7129718`。GitHub回读merged=true；本机fetch后确认该提交在origin/main，canonical Task及三份Review与合并前候选直接diff一致。
- 原linked worktree快进到该main后，以本机原reservation调用既有`task_cli.py finalize`，返回`status=finalized`、`task_id=TASK-0040`、`project_key=GAME-101`；远端reservation ref与本机reservation元数据均确认已移除。token未进入Git、评论或日志。
- Task交付及原PR生命周期为Complete，Round 2仍为Accepted、R1 Closed。Complete状态记录随`codex/task-0040-git-closeout`单独候选PR提交；在该PR合并前，main中的Task状态文字仍为Accepted，不伪称Complete元数据已进入main。该收尾PR待Review及另行合并授权。
- 本轮仅治理收尾；工作簿、复核包、币价、业务脚本和源配置不动，不重算。原PR #18及业务证据边界保留。Subagents: none。

### 历史 — Round 2 Accepted / R1 Closed（合并前）

- [Round 2评审5506462225](../reviews/TASK-0040-CHATGPT-REVIEW-2.md)受评基线为`9ce1b6a9bbfa7e73e3946201aed9bb6649cbd94d`，结论Accepted、R1 Closed，无必须修改项。2026-10-14按User授权落Git；GitHub以COMMENTED承载该结论，不是平台APPROVED。
- 评审方实际读取User上传的受控ZIP并运行复核入口，53/53通过、固定预期重放一致；另行独立完成43项检查，并将11条情景结果的220个字段与原工作簿读值对照一致。前轮2151个工作簿公式核对沿用原记录。本轮Codex只登记评审，不把审阅容器实跑写成本机再次验收。
- 接受范围仍为已声明配置快照、合成持卡、币价基准及单次领取窗口的条件估值。不是固定售价、全服均价、统一内部面值或完整赛季价值，不支持把单包结果任意线性乘以连续发包数量；缺证据的面值/售价继续N/A。
- 6008个源字段与冻结XLSX一致仍为Codex打包前证据，评审方未独立重验原22张源表真实性或切片完整性。线上加载、导出顺序、PRNG关联、商品可见性、实付、原生Excel/WPS及完整赛季模型保持未验证，不新增为阻塞项。
- 本轮仅同步脱敏Review、Task/Status/Handoff/CHANGELOG、Registry及PR描述；不补包、不重算、不修改工作簿、币价或配置。首轮和补充评审原文保留。PR #19保持OPEN/Draft，未合并，reservation为pending-main，未finalize；Task为Accepted，Git生命周期未Complete。Subagents: none。

### 历史 — Round 1 补充材料 — 2026-10-13

- [首轮评审](../reviews/TASK-0040-CHATGPT-REVIEW-1.md)保存历史Needs changes依据；[补充评审5505803167](../reviews/TASK-0040-CHATGPT-REVIEW-1-SUPPLEMENT.md)覆盖其“未取得工作簿和说明”的前提，撤回已交付主表、截图、身份清单与币值算例的重复补包要求。补充评审记录工作簿层面2151个公式核对通过，剩余R1仅为核心模拟证据不足，不是已发现算法或价格错误。
- 按User本轮授权沿用原分支与PR #19，仅整理`TASK-0040_核心计算复核包.zip`：原calculate.py、check_results.py和model_parameters.json保持原样；附最小字段切片、来源定位、必要Python依赖声明及窄范围入口。完整原表、游戏源码、账号和敏感日志不进入包或公共Git。
- 复用原7个整包独立算例；补充5组同状态有包/无包账本、5条固定随机路径和7个概率例。账本显式扣除起点已完成奖励，列示重复卡星星、一次兑换及返包、窗口末库存。原状态均低于兑换门槛，无包路径无兑换；没有扩展估值窗口或改变币价。
- 从最终ZIP解压到独立本机目录，按随包PowerShell入口实际运行成功：53项检查通过，固定预期重放一致。最少源字段在打包前独立核对6008个位置；28个包内文件按白名单打包并读回，无全量原配置或游戏源码。仅复算代表范围，未重跑464行情景，未重建工作簿或截图。
- 补充材料已备齐，状态回到Review，等待ChatGPT实际接收ZIP后复核核心金币链；不把Codex自测当作R1已获接受。见[产物导航](support/TASK-0040/ARTIFACTS.md)与[本轮脱敏验证](support/TASK-0040/CORE_REVIEW_VALIDATION.json)。原reservation保持pending-main。Subagents: none。

### 原交付与持续边界

交付 commit：`04153ed`；[PR #19](https://github.com/840832144/AI-Workspace/pull/19)已合并。PR仅包含规格及脱敏治理，完整产物按本机导航审阅；原规格PR #18保留。

Round 2已接受本次单次领取窗口用途。完整赛季预算还需要明确后续获得包计划和兑换/交易策略；真实售价和统一内部面值分别需要对应依据。当前结果可用于已声明条件下的包间比较，不把这些缺口泛化为全部USD不可计算。

服务端时区、线上导出顺序、实际加载配置/代码版本与原生Excel/WPS未验证。6个本地生成描述类无独立SVN revision，已明确标注，不伪造一致性。星星箱共用冷却注释与按ID实现有差异，本窗口最多一次兑换不受多箱行为影响。

唯一下一步：审阅`codex/task-0040-git-closeout`的Complete状态记录并由User另行决定是否合并该收尾PR；PR #19已合并、原reservation已finalized，不重复执行。Subagents: none。
