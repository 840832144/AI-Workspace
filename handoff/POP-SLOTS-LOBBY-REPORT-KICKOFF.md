# Codex 启动交接：Pop! Slots 大厅氛围系统拆解

- Kind: kickoff-handoff
- Updated: 2026-09-09
- User decision: Approved
- Scope: Pop 策划版拆解报告 + 私有 CR 对照讨论表；不做 CR 开发。
- Status: Review；TASK-0030首版完成，研究06f1d1e、私有对照43779f5均已推送，等待ChatGPT Review。
- Canonical Task: [TASK-0030](../tasks/TASK-0030-POP-SLOTS-LOBBY-REPORT.md)

## 唯一启动规格

先读 [完整执行规格](../tasks/support/pop-slots-lobby-report/EXECUTION_SPEC.md)，严格先完成第 0 节的 latest-main / Registry / 同目标检查 / remote-CAS 分配与登记，再进入报告任务。不得把本文件当成已分配的 canonical Task，不得手工猜编号。

本轮 ChatGPT 容器的 Git clone 因网络解析失败，无法运行真实 allocator；GitHub Connector 的读取与文档写入可用。因此不绕过分配 Gate，交由 Codex 在获准本机完成正式登记。User 已授权报告范围，不需要再次询问是否启动相同工作。

## 材料入口

Pop 原研究位于 `840832144/huuuge-android-research/artifacts/toptycoon/POP_SLOTS_LOBBY_FORENSICS.md`；User 指定历史 ref 为 `d7828f1`。本轮读取研究 main 为 `7df687ec18f904e6c44ed5bfb05a7a6de30bb46c`，原报告 blob 为 `e09ad16d974dd617fdfffa20bbd5ec251e60bf96`。

CR 私有对照要求位于 `840832144/cr_design/reviews/briefs/2026-09-09_POP_SLOTS_LOBBY_REPORT_CR_CONTEXT.md`，首次提交 `36c8146ef32e92ac4d56b7f8b0b25b76e3e7ce2c`。其中列出两份 Word、Pop 录屏、CR 概念图的哈希、原文位置与需负责人讨论的问题；不要把内容复制到公共 Git。

会话附件不会因同步 Git 自动到达 Codex。先找 User 指定目录与批准来源；仍缺失时仅问缺失文件路径。研究原件保持本机只读。

## 本轮交付与停止点

交付 Pop 中文图文报告、证据索引及 CR 对照讨论表。复用已有报告和录屏；原报告主张、可见观察、推断和待验证分开，不能用 CR 参数填补 Pop 空白。

不开发 CR、不修改其原需求/配置/SVN，不启动新采集、自动点击或资源消耗，也不发布飞书或联系负责人。需要补录则列最小缺口与步骤，等 User 单独确认。

完成后按完整规格更新 Task/Status/Handoff，返回实际 commit 与报告入口，状态为 Review，等待 ChatGPT 审阅及 User 与负责策划对齐。

## 启动交接历史记录（首次分配前）

写入前 AI-Workspace main 为 `1dd6de3e244858c44b716cacd72961ea9419f564`；已读取 Task Registry、Task 规则、allocator 说明、Codex Handoff 和项目进度源稿；研究仓库已读取 Task/Status/Handoff；CR 已读取审阅镜像边界与历史提案。没有从这些读取推定业务已实现或本机环境仍可用。

本轮只新增启动规格、独立交接和 CR 私有对照说明；未分配 TASK ID，未修改 Registry、既有 Task、原研究报告、CR 原需求、配置或 SVN，未启动 Codex 进程或采集。

## 本次执行完成与交接

正式分配、Ready提交e64ed8c和校验先于研究完成；随后完成六主题报告、离线完整HTML、6张脱敏图、19条证据索引及私有12项CR对照。研究仓库06f1d1e，CR私有仓库43779f5；入口与未证实项见canonical Task。原研究和CR原案均保留，未新采集、未写SVN或云文档。

User最终要求：先验收离线图文版，通过后再做飞书云文档；聚焦核心产物，不追加哈希或外围门禁。当前状态Review，不自动Accepted或合并main；reservation待canonical进入main后按原流程处理。唯一下一步：ChatGPT Review。Subagents: none。
