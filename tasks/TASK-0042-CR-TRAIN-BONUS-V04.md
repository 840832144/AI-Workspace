# TASK-0042 — CR 火车 Bonus V0.4 公司协作方案

- Status: Review
- Project key: CR
- Owner: User / ChatGPT
- Executor: Codex
- Priority: P1 / User 已授权发布
- Date: 2026-10-15
- Updated: 2026-10-15
- User decision: Approved
- Allocation relationship: new
- Subagents: none

## Goal

交付飞书原生可编辑《CR 火车机台新增 Bonus 开发方案 V0.4｜机器人 4v4》及技术附件 A/B，公司组织内获得链接者可编辑。保留旧版，使用既有飞书 CLI 写正文及权限。User 本轮随后明确独立创建、跳过目录定位与唯一导航登记；不将此例外推广为长期流程变更。

## Scope

完整输入为 User 2026-10-15 指令和《Codex_火车Bonus飞书开发方案任务.md》，研究来源为同日 DSH FireVsLightning 包。只整理已有材料，不重新采集。正文以策划自然语言说明 B01 长线集满入口、1 真人加 7 机器人、40 格参考方案、每轮和四类技能、阵营与个人奖励、禁跳、当前状态恢复及原 Free 衔接。POP 实证、CR 已定需求、建议参数、未确认事项分别标明。附件 A 整理九类步骤、批次与 ACK、结算和证据位置；附件 B 说明服务器时间线、完整快照、安全恢复点与唯一结算。PB 和模拟仅写总体思路。

## Non-goals / Safety

不开发游戏、模拟器或正式 PB，不进行 RTP 仿真，不运行采集工具、不等待稀有触发。不改 Base/Free/B01 收集口径，不新增定时送奖入口，不改配置或 SVN。只向当前已确认公司组织分享整理文档，不新增外部访问，不调整整个目录或无关文件权限。原始包、代码、身份数据、会话明细与 API 响应留受控本机。Git 只保留脱敏治理与交付说明。未获授权不合并或 finalize。

## Acceptance

1. 正确组织有真实原生主文档链接。
2. 主文及两份技术子文档组织内链接编辑权限设置成功并回读，不宣称未经执行的普通员工实测。
3. 策划能够理解完整玩法。
4. 禁跳、迟到入场、重连当前状态及唯一结算一致。
5. 技术附件可读，模拟与 PB 保持思路级别。

## Gate 0

安全 fetch 最新 main 898358f；工作区干净。读取根及 CR 规则、状态与相关历史任务，未发现同目标活动任务；不续 TASK-0036/0038。既有 Registry scan/validate valid，0 collision。独立 linked worktree 分支 codex/cr-train-bonus-v04，由 remote-CAS allocator 分配本号，reservation pending-main，凭据仅留受控环境。

## Progress

已交付主文与两份原生技术子文档，均在现有公司账号的独立文档空间，不移动到项目目录。完整入口见 [交付说明](../projects/cr/REPORTS/CR-TRAIN-BONUS-V04/README.md)，[专属交接](../handoff/CR-TRAIN-BONUS-V04-20261015.md)。主文 revision 4、附件 A revision 5、附件 B revision 4；三个正文与受控定稿直接文本比较一致，六个相互链接回读成功。主文 14 个一级标题、5 张原生表格，代码与字段结构只在附件。

三份权限分别以 CLI user 身份设置并 GET 回读：link_share_entity=tenant_editable，external_access=false，invite_external=false，share_entity=same_tenant。无普通员工测试身份，未宣称员工实测。未增加组织外访问，未修改旧版、目录或无关文件权限。

## User 补充决定与限制

- 飞书正文、子文档、权限与回读均用既有 CLI；不重新搭集成。
- 搜索缺 search:docs:read、知识空间列表缺 wiki:space:retrieve；补充授权已申请但尚未审批，User 明确可跳过。未完成新授权、不改旧凭据或扩大权限。已有根目录和导航只读核对未发现新版，不能声称完成全空间搜索。
- User 明确本轮不管项目位置，独立创建；对唯一导航专门确认后选择“本轮跳过导航登记”。已遵从，不调用替代 provider、不手改 Hub、不冒称已登记。此项不再作为本轮发布阻塞。
- 原方案、V0.2 与 DSH 所需材料已读；本机未找到 V0.3 与旧稿所指转换器/协议附件，文档披露范围，仅把兼容性列为后续接入核对，不阻塞本轮方案。
- 数值参数、RTP、正式 PB 与实际游戏联调均未实施；方案通过自洽及云端交付核对不等于实现验收或 ChatGPT Accepted。

## Validation / Handoff

五项本轮云端交付条件已核对；公司编辑状态仅做权限配置与正文/链接回读，未做普通员工登录实测。主文明确当前恢复是 CR 新设计，旧 POP 迟到顺序播放的证据保留在附件；九类步骤、完整快照、ACK 不决定派彩、唯一结算和原 Free 衔接均已写入。原始包、账号/会话明细、完整响应和本地发布脚本留受控目录，不入 public Git。

本轮云端发布阻塞项：无。等待 User / ChatGPT Review；reservation pending-main，不合并、不 finalize。Subagents: none。

仓库收口：Registry valid、20 canonical、0 collision；CR 既有目录工具完成14份工作簿结构读取（未计算哈希），仓库 validator 0错误/0警告。只验证治理及现有目录结构，不重做任何数值结果。工具产生的日期／大小目录刷新已撤回，不混入本轮；最终显式差异只含本 Task、Registry、Status、Handoff、交付说明、经验补充及 Changelog。
