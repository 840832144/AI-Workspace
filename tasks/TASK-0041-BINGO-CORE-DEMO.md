# TASK-0041 — Bingo核心玩法本地Demo

- Status: Review
- Project key: BINGO-CORE-DEMO
- Owner: User / ChatGPT
- Executor: Codex
- Priority: P0
- Date: 2026-10-15
- Goal: 可独立游玩、可复用和移交的本地Bingo核心闭环。
- User decision: Confirmed；2026-10-15正式启动，随后明确授权本机缺少Unity时安装。
- Reservation: remote-CAS pending-main；独立linked worktree分配，未finalize。

## Goal

交付可独立游玩的本地Bingo完整核心循环，并将规则、协议、配置和核心包移交Unity团队；不依赖原客户端或线上资源。

## Scope

唯一正文为[完整执行规格](support/bingo-core-demo-20261015/EXECUTION_SPEC.md)，来源f42e249/330f754；本机附件已逐段核对。覆盖冲突旧提案，尤其双格可部分执行、放buff排除已有buff、无目标仍已使用、补填先放buff且填中才赚次数。

独立C#规则内核、本地规则服务、Unity表现层；1/2/4/6卡、五档暂定Bet/上限、固定合成场景、九道具、充能/连锁、结束补填、结果/返回再开局、一键Windows试玩与移交。无团队模板时保持可替换的最小Unity工程，规则不依赖UnityEngine。

## Non-goals

不恢复TASK-0039原客户端自动玩，不继承其额度；不做真实账号/原资源迁移、多人匹配、局外奖励发放、复杂特效、数字Auto Play/GM或云服务。

## Deliverables

可玩Windows包及启停/检查入口；纯C#核心、协议/配置/合成场景、Unity源码/导入验证；RULES.md/QUESTIONS.md/DSH-VERIFY.md、真实测试、差异清单与回滚说明。

## Acceptance

执行规格第9节逐项验收：四种卡数完整循环、九道具的目标不足/无目标、buff去重与连锁、补填赚取/消费、结束一次性、动作幂等、确定性及Unity导入结果一致。临时浏览器切片只能计临时交付，不能称Unity最终通过。原自动玩十局和填充率不适用于本Task。

## Safety

只使用本地测试资源和自制合成场景；本地服只监听回环。不调用原游戏、不消费线上票券、不带入Raw/账号/二进制。治理在AI-Workspace，业务工程已建独立本地Git `D:\BingoCoreDemo`，未批准业务远端前仅本地提交。不合并、发布、SVN、强推或finalize。Subagents: none。

## Validation

登记前完整scan/validate通过：19 canonical、0collision/error、6既有legacy警告；main898358f为祖先，remote-CAS实际分配TASK-0041。登记后重建Registry并验证、推送再实施。开发按规则单测、实际服务集成、真实客户端与包启动分别取证；未知原规则采用显式DemoAssumption，不冒称OriginalConfirmed。

本轮提交[Review交接](support/bingo-core-demo-20261015/CHATGPT-REVIEW-HANDOFF-20261016.md)：业务08529d8、原生包0.2.1；47项核心、Unity/.NET同核心一致性、Windows构建及真实客户端启动通过。User初步试玩反馈“看起来没啥太大问题”；本次1卡手动结束局的49条记录复算一致，未冒称多卡/九道具全量人工验收。历史c31f0c8的39项HTTP和120条复算单列，新版完整HTTP、断外网及其余Unity端到端覆盖仍待补；dsh核验/团队模板仍待返回。Review不是Accepted，完整进程与失败记录见原[实施进度](support/bingo-core-demo-20261015/IMPLEMENTATION-PROGRESS-20261015.md)。

## Handoff

User于2026-10-16要求整理汇报ChatGPT，当前等待统一Review。已准备受控Review ZIP，含冻结源码、规格、证据、实际试玩快照与离线复算入口；普通初步体验反馈已收到，但逐项验收缺口不自动关闭。原生启动早期误判已撤回，0.2.0失败与0.2.1成功证据均保留。

[原接管入口](../handoff/BINGO-CORE-DEMO-20261015.md)；[项目状态](../projects/bingo-core-demo/STATUS.md)。保留PR #21规格历史，本地治理分支codex/bingo-core-demo-20261015推送到原chatgpt/bingo-core-demo-candidate-20261015。TASK-0039暂停在其原治理分支/PR #17单独记录。登记推送后连续实施，不等待再次开工批准。
