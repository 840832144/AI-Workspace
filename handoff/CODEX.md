# Codex Handoff

- Updated: 2026-08-27
- Latest completed task: TASK-0018 Review Round 1 fixes
- Review source main: `b278afa`
- Current state: TASK-0018 waiting ChatGPT Review Round 2；other active Tasks remain independent
- Final Memory Mode: `ASSISTED`
- Production Hook/AUTO: disabled
- Subagents: none

## TASK-0018 Review Round 1 Fix Outcome

- TASK-0015 已确认 Finalize 并更新为 `Complete`；TASK-0018 已更新为 `Review`；TASK-0014 保持 `Accepted`。
- Review Round 1 `Needs changes` 已按 `reviews/TASK-0018-HUUUGE-LOTTERY-CHATGPT-REVIEW-1.md` 完整修订。
- 外部业务仓库已推送 [`4a5dddf`](https://github.com/840832144/huuuge-android-research/commit/4a5dddf7782307c6a8f368c9f1dc6390eec6f65b)，包含策划优先中文报告、7 份脱敏 CSV、购买链 Extractor 与 7 个测试。
- 原飞书文档 [`Huuuge Lottery 活动数值拆解（2026-08-27）`](https://gfok27asqq.feishu.cn/docx/IK5adiJyWoHVJzxlovEcjxiWnO3) 已原位替换；没有创建副本。最终回读 367 blocks、4568 个正文字符、一个标题，并验证企业内可编辑。
- Finalized alias `LOT-20260827-A`：8712/8712 decode、LotteryToss 346/346、普通筹码下注 588/588、FreeSpin 45/45。
- 四次真实货币购买全部成功，合计 54.43 SGD、763 张 Lottery 票和 235 loyalty points；每个礼包都有其他奖励，表观每票成本不能当作独立票价。
- 933 张票消耗产生 133 张阈值返还；直接 Lottery 奖励 60 张；六次升级后的 +16 Bronze 余额变化为 `Confirmed L3`，升级因果为 `Estimate L3`。
- Spin/FreeSpin payload 没有直接 Lottery ticket grant，因此报告未把升级产出写成单局随机掉落，也未输出伪掉率。
- Lottery Knowledge 从 L2 提升到 L3；项目分布更新为 L3 × 12、L2 × 3、L1 × 22、L0/L4 × 0。
- 117.516 只保留在技术附录，定义为排除真实货币购买的筹码奖励输出与普通 Spin 筹码成本描述性比值；不是 RTP、ROI 或付费回报。
- 未提交 Raw、真实 Session/account/request/product/store/order 标识、绝对余额、完整余额轨迹或 credentials；未改 Collector、CR、SVN、游戏或服务端状态。
- Subagents: none；宽松父会话下保持 Pilot OFF。

## TASK-0018 Review Files

- `projects/huuuge-android-research/REPORTS/TASK-0018-LOTTERY-NUMERICAL-REPORT.md`
- `projects/huuuge-android-research/STATUS.md`
- `projects/huuuge-android-research/MEMORY.md`
- `projects/huuuge-android-research/KNOWLEDGE/README.md`
- `projects/huuuge-android-research/KNOWLEDGE/EVENTS.md`
- `tasks/TASK-0018-Huuuge-Lottery-Numerical-Breakdown-Report.md`
- 外部 [`PURCHASES.csv`](https://github.com/840832144/huuuge-android-research/blob/4a5dddf7782307c6a8f368c9f1dc6390eec6f65b/reports/lottery/20260827_lottery-ticket-puzzle/PURCHASES.csv)
- 外部 [`Extractor tests`](https://github.com/840832144/huuuge-android-research/tree/4a5dddf7782307c6a8f368c9f1dc6390eec6f65b/tools/analysis/lottery/tests)

## Prior Review Context — TASK-0016

ChatGPT Review 1 的三个 blocking fixes 已完成：

1. Project Private Candidate 可以在 Host-local approved Registry 全部 gate 通过时写入对应私有 Git repository；未批准或错配保持 Outbox。
2. AUTO canonical promotion 只允许 non-main linked worktree，并把 target、Candidate、Archive、index 作为一个可恢复事务。
3. Public/Private Git Candidate 的 host/project/actor/reference 禁止占位 provenance，CLI、Event file、Generic Agent 三条入口一致。

架构方向、ASSISTED 默认和 Candidate-first contract 未改变。没有激活 Hook、AUTO 或新外部 provider。

## Required Fix 1 — Approved Private Git Routing

Repository classification contract：

- `public-control-plane` → 只允许 `public/public`；
- `project-private` → 对应单项目私有 Git repository；
- `cross-project-private-hub` → User 批准的跨项目私有 Hub。

Private capture 必须提供 `repository_alias`。Host-local Registry 同时验证唯一 alias、`enabled`、`writer_enabled`、classification、allowed scope、allowed sensitivity、allowed source project、绝对 Git root，并拒绝目标等于或位于 public AI-Workspace 内。任一 gate 不满足时输出 sanitized Outbox，不写 public Inbox。

Disposable test / Pilot：approved private Candidate 1，private repo 中存在，public Inbox 0；unapproved alias、wrong classification、sensitivity mismatch 和 public-root 回指全部 fail closed。没有读取真实 Huuuge/CR 数据。

## Required Fix 2 — Branch-safe Transactional AUTO

AUTO curate 前置 gate：

- Git repository；
- branch 非 `main/master`；
- independent linked worktree；
- 初始 dirty path 仅允许 `memory/inbox/`；
- 事务中 branch、HEAD、Git status 不出现非 managed 变化。

每次 promotion 保存 target、Candidate、Archive、index 的执行前字节快照。任一步失败恢复四者；rollback 自身失败时写 Host-local recovery record，存在未解决 record 时阻断后续 AUTO。

Fault injection 全部通过：

| Fault | Result |
| --- | --- |
| target 写入后失败 | 四资源恢复；promoted 0 |
| Archive 前失败 | 四资源恢复；promoted 0 |
| Archive 后失败 | 四资源恢复；promoted 0 |
| index save 失败 | 四资源恢复；promoted 0 |
| Git status 发生外部变化 | 四资源恢复；promoted 0 |
| main branch / unrelated dirty worktree | 写入前 fail closed |

## Required Fix 3 — Stable Provenance

所有进入 Git 的 Candidate 必须提供稳定、可复查的 `source_host`、`source_project`、`source_actor_alias`、`source_reference`。空值与 `unknown`、`n/a`、`none`、`null`、`-`、`tbd`、`unspecified` 等占位值无效。

- CLI placeholder → Outbox，public Inbox 0；
- Event file placeholder → Outbox，public Inbox 0；
- Generic Agent placeholder → Outbox，public Inbox 0。

Local-only / route-required 事件不因来源缺失而伪造 provenance；它们只保留最小 Outbox 说明。

## Validation and Pilot

- `python -m unittest discover -s tools/memory/tests -v`：34/34 passed。
- `python tools/memory/Run-MemoryPilot.py`：passed；disposable linked worktree + disposable private Git repo。
- Round 2 Pilot：captured 3、private Git captured 1、promoted 1、review 1、local-only/Outbox 4、OFF suppressed 1、conflicts 0、failed 0。
- false captures / missed captures：not measured；仍需真实 Host observation，不从 synthetic Pilot 推断。
- Production `Get-MemoryStatus`：`ASSISTED`，source=`repository-default`。
- AI-Workspace Context refresh：42 public control-plane sources、0 Secret issue、0 broken link、private repositories not read、`manual upload required=true`。

## Changed Contracts and Files

- Implementation/tests：`tools/memory/memory_cli.py`、PowerShell capture wrapper、34-test suite、Pilot runner。
- Contracts：Memory Capability、Governance 1.1、ADR-0005、Memory Workflow。
- Adapters/templates：Codex、ChatGPT、Generic Agent、Event/Candidate templates。
- Records：TASK-0016、CHANGELOG、Pilot 和本 Handoff。

## Safety and Boundaries

- 最终 mode 为 `ASSISTED`；没有 Host-local AUTO override。
- 没有安装/激活 Global Hook，没有修改 `~/.codex/config.toml` 或 Global runtime。
- 没有读取或修改 Huuuge、CR、Collector、Capture、SVN、飞书、Document Assistant 或真实私有 Registry。
- TASK-0017 已在此前独立任务完成；本轮未修改其网络脚本、Git 分支或 Codex proxy 配置。
- Fault injection 只有同时设置测试环境变量和 disposable marker 才启用；production worktree 默认不可触发。

## Known Limits

- 尚无 User 批准的真实 Project Private Registry 或 Cross-project Private Hub；production 私有 writer 仍需逐仓库授权。
- ChatGPT Project Sources 仍需 manual upload；没有安全 API 时不自动替换。
- Semantic dedup、graph retrieval、真实 false-positive/missed-capture 与 scheduled curator 仍是独立后续评估项。




<!-- MEMORY-REFRESH:START -->
## Memory Context Refresh

- Generated: 2026-08-27T06:39:23Z
- Effective mode: `ASSISTED`
- Manifest: `CONTEXT_MANIFEST.yaml`
- ChatGPT Project Sources: `manual upload required`
- Private repositories: not read unless explicitly registered and authorized
<!-- MEMORY-REFRESH:END -->
## Exact Next Action

ChatGPT 对 `huuuge-android-research@4a5dddf7782307c6a8f368c9f1dc6390eec6f65b`、本仓库 TASK-0018 索引和原飞书文档执行 Review Round 2，重点复核策划结构、购买表、礼包限制、普通下注术语、Extractor 测试和飞书排版，返回 `Accepted` 或具体修改项。其他活动任务继续在各自独立 worktree 推进；不得互相覆盖。
