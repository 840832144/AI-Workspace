# CANDIDATE-20260827-CASH-FRENZY-COLLECTOR-FEASIBILITY — Cash Frenzy Android Collector Feasibility Audit

- Kind: candidate
- Status: Migrated
- Project key: CASH-FRENZY
- Human alias: CF-FEASIBILITY-001
- Suggested priority: P1 candidate
- User decision: Approved
- Source: Restored from Git commit `7f6d9a5f315c27e829e2dda75396200ee91cdf98`
- Created: 2026-08-27
- Updated: 2026-08-27
- Migrated to: TASK-0022 (`tasks/TASK-0022-CASH-FRENZY-ANDROID-COLLECTOR-FEASIBILITY-AUDIT.md`)
- Migrated at: 2026-08-27T09:25:45Z
- Historical collision: `tasks/TASK-0018-Cash-Frenzy-Android-Collector-Feasibility-Audit.md`

## Non-execution Notice

本文件恢复误建 Task 的完整规格，仅用于防止需求丢失和后续 Review。它不是可执行 Task；不得据此创建模拟器、拉取 APK、启动 Root/Frida/Capture、修改 Collector 或访问业务数据。

## Goal

用最小、可复查的静态与动态证据判断：

> Cash Frenzy 是否能达到与当前 Huuuge Collector 相近的“被动广泛采集 → 结构化解码 → Raw 保全 → 模块目录 → 按需数值分析”能力，以及需要采用什么 Adapter 路线。

本方向只做**可行性审计与最小链路证明**，不构建完整 Cash Frenzy Collector，不输出 RTP/EV 或长期概率结论。

## Historical Metadata

- Target game: Cash Frenzy / 爆有钱 Online
- Candidate package: `slots.pcg.casino.games.free.android`（执行时必须重新确认）
- Business repository: Not created; feasibility-only
- Original Subagent mode: MANUAL allowed under restrictions；实际执行必须重新检查当时权限与 Task 决定

## Execution Gate

若未来由 User 批准并晋升为唯一 canonical Task，仍须满足：

1. Huuuge Lottery 实时 Capture 已结束或 Collector 明确 idle；不得打断限时证据保全。
2. 同步 AI-Workspace 与业务真相源最新 main，读取届时 Task、Status、Handoff 和 Collector 能力边界。
3. 使用独立模拟器实例和独立本机数据目录；不得复用或修改 `Pie64_1 / HuuugeResearch`。
4. 新建实例、安装游戏、账号登录、商店认证等需要 User 操作或授权时，由 User 决定并执行。
5. Cash Frenzy、Top Tycoon、绯闻港口一个一个建立 Feasibility Audit，不并行开发。

Gate 未满足时必须报告阻塞并停止，不得扩大权限或绕过 P0 任务。

### Research Environment Decision

历史 main commit `7eb16b0` 曾记录“多个游戏共用同一 Research 模拟器”。该内容已被 User 在 TASK-0022 启动指令中的更晚、范围更具体决定 supersede：

- 为 Cash Frenzy 建立独立 `CashFrenzyResearch` 环境；
- 不修改或复用 `HuuugeResearch`；
- Cash Frenzy 使用独立 Session、Capture、Manifest、Raw、Database 与 Evidence；
- Cash Frenzy Adapter 不得读取 Huuuge 或其他游戏数据；
- 任何共用 Host 级 Root / Frida 变更必须先证明必要性、影响与回滚，并取得 User 确认。

开始 Cash Frenzy 采集前仍必须验证前台包名等于本次确认的 Cash Frenzy package；否则拒绝进入 READY。

## Success Questions

未来审计必须明确回答：

1. Cash Frenzy 的 Android 包、版本、ABI、引擎和主要运行模块是什么？
2. 它使用何种网络协议和序列化：Protobuf、FlatBuffers、JSON、MessagePack、自定义二进制或其他？
3. 是否存在可恢复的 descriptor/schema、符号、Lua/managed metadata、配置表或资源容器？
4. User 正常执行一次 Spin 时，能否被动捕获可关联的 request/response/update 或本地状态变化？
5. 当前证据能稳定还原 `game/machine id、bet、result、win、feature/free-spin、jackpot、balance/state` 中哪些字段？
6. Huuuge Collector 的哪些通用能力可以 Adopt/Wrap，哪些必须新建 Cash Frenzy Adapter？
7. 建议结论是 `Adopt / Wrap / Fork / Build / Stop` 中哪一种，置信度和主要风险是什么？

## Scope

### Phase A — Reuse-first discovery

主 Agent 先读取届时最新 Core Rules、Capability / Workflow / Evidence 文档、Huuuge Collector 文档与已验证能力，形成 Reuse Matrix：

```text
可直接复用：Bootstrap / GUI / Session / manifest / Raw / inventory / catalog / privacy
需要包装：模拟器实例、包名、ABI、启动与 hook 生命周期
必须新建：协议 decoder、hook target、schema mapping、模块分类
暂不采用：与 Cash Frenzy 不匹配的 Huuuge-specific code
```

不得先复制 Huuuge 工程再寻找理由。

### Phase B — Public and package identity verification

确认并记录：

- 官方游戏名称与地区名称关系；
- 官方开发/发行主体；
- Android package；
- 当前实际安装版本与 versionCode；
- 是否存在地区包、商店包或 ABI 差异。

公开资料结论必须有来源；商店描述只能证明产品功能，不可证明客户端协议。

### Phase C — Isolated research environment

建立或确认独立研究实例，建议显示名 `CashFrenzyResearch`。要求：

- 独立于 HuuugeResearch；
- 独立账号/实例/session 目录；
- 不把不同游戏 Raw 混合；
- 记录 Android 版本、实例 ID、ADB serial、ABI list 和 native bridge；
- 只在真正需要时申请 Root/Frida 等机器级变更，先复用已审计方案或官方/成熟方案；
- 任何共用 Host 修改前说明影响、备份与回滚，并取得 User 确认。

### Phase D — APK acquisition and static audit

在 User 自己的研究环境中定位并拉取 base/split APK，保存在受控本机目录，不提交 Git/SVN/飞书。至少检查：

- package/version/split/ABI；
- Unity、IL2CPP、Cocos、Unreal、自研引擎或其他运行框架；
- Java/Kotlin、managed assemblies、native `.so`、Lua/LuaJIT；
- Protobuf descriptor、`.proto` 名称、FlatBuffers schema、MessagePack、JSON、SQLite；
- 网络库、WebSocket、HTTP/2、gRPC、自定义 socket、TLS；
- AssetBundle、资源包、配置表和本地数据库；
- 主要业务模块和可疑 hook target；
- anti-debug、integrity、签名校验和 native bridge 风险。

只提交脱敏结构、文件名、hash、字段/符号摘要和证据位置，不提交 APK、`.so`、完整 strings、账号数据或私有响应。

### Phase E — Minimal dynamic proof

目标不是长时间抓取，而是证明一条真实数值链。由 User 在正常游戏中亲自执行：

1. 进入一个可用 Slots 机台；
2. 记录当前可见 Bet 档位；
3. 进行 1–5 次本来就准备进行的普通 Spin；
4. 若自然触发 Feature / Free Spin / Jackpot，只被动记录，不诱导额外付费或大量资源消耗。

Codex 负责在操作前确认被动采集 Ready，捕获网络/序列化/本地状态层的最小证据，关联 request/response/update/balance change，区分观察与推断，并 Clean Finalize。Raw 只留本机。

无法捕获时必须给出精确 blocker，例如协议仍加密且尚未到明文层、native bridge / anti-debug 阻塞、结果只在本地对象、schema 缺失、账号/玩法未解锁，或需要新 hook / Local State Adapter。不得用“应该可以”代替证据。

### Phase F — Feasibility and architecture decision

按以下层次评分：

```text
F0 Unknown
F1 Static-only
F2 Live raw observed
F3 Live structured fields recovered
F4 Repeatable Huuuge-like collection path proven
```

分别评估 Slots/Spin、Feature/Free Spin/Jackpot、Missions/Pass/Club/Events、Offers/Economy/Rewards、Local config/static math、跨 Session 复现和策划一键包装潜力。最终给出当前等级、F4 缺口、预计 Adapter、Adopt/Wrap/Fork/Build 决策和是否值得进入完整实现 Task。

## Subagent Policy

原规格允许在满足条件时使用 MANUAL Subagents；未来 canonical Task 必须重新确认。只读委派可包括：

1. `repo_explorer`：分析 Huuuge Collector 可复用层和 adapter seam；
2. `knowledge_retriever`：收集官方商店、官方帮助中心和已提供文档；
3. `evidence_test_verifier`：检查 Evidence 标签、验收矩阵和复现条件；
4. `reviewer`：只读审查结论、范围漂移和安全风险。

主 Agent 始终是唯一写入者、Git 提交者和外部操作执行者。Subagent 不访问账号/session Raw、完整 APK/`.so`、Secret、飞书 WRITE 或其他外部 WRITE。MANUAL 不得与 full-access 类权限并用；不满足时保持 OFF 并由单 Agent 完成。

## Deliverables

若未来获批执行，在 `AI-Workspace/reviews/cash-frenzy/` 提交脱敏结果：

```text
FEASIBILITY.md
REUSE_MATRIX.md
STATIC_INVENTORY.md
PROTOCOL_EVIDENCE.md
DYNAMIC_PROOF.md
NEXT_TASK_PROPOSAL.md
```

- `FEASIBILITY.md`：一页结论、F0–F4、Huuuge 对比、Adopt/Wrap/Fork/Build/Stop 与证据标签。
- `REUSE_MATRIX.md`：通用层、Huuuge-specific、Adapter 边界、依赖与退出成本。
- `STATIC_INVENTORY.md`：package/version/ABI/engine、结构摘要、hash 和工具版本，不含二进制或完整 strings。
- `PROTOCOL_EVIDENCE.md`：网络/序列化候选、schema、hook target、保护风险和证据等级。
- `DYNAMIC_PROOF.md`：Session 别名、User 最小动作、捕获结果、确认字段与 blocker，不含敏感明细。
- `NEXT_TASK_PROPOSAL.md`：只提出 Collector Adapter、Static Config Adapter、Local State Adapter 或停止投入，不自动执行。

## Non-goals

- 不构建完整 Cash Frenzy Collector；
- 不复制/改名 Huuuge Collector 后发布；
- 不做长时间 Spin、RTP、EV、概率表或服务端 RNG 结论；
- 不绕过付费、伪造/重放请求、修改奖励/余额；
- 不解锁付费内容、自动购买或替 User 消耗资源；
- 不研究 Top Tycoon 或绯闻港口；
- 不发布飞书正式报告；
- 不创建业务仓库或 SVN 正式包，除非未来 Task 明确批准。

## Safety and Data Boundaries

- User 负责账号登录、游戏内操作、付费和资源消耗决定。
- Codex 只做被动采集、静态读取、工具验证和脱敏结论。
- Raw capture、APK、`.so`、完整响应、账号 ID、token、逐笔余额和私有路径保持受控本机。
- Git 只保存脱敏结构、hash、字段/符号摘要、复现步骤和判断。
- 不修改游戏请求、返回值、内存状态、余额、奖励或服务器状态。
- Cash Frenzy 数据不写入 Huuuge session/database；按实例、账号别名、Session、版本和 schema 隔离。

## Dependencies

- TASK-0020 经 ChatGPT Review Accepted；
- User 再次确认执行顺序并授权晋升；
- 届时 P0 Capture / Lottery 工作不存在冲突；
- 独立研究实例和受控本机数据目录可用。

## Risks

- 历史 package、版本、保护机制和客户端实现可能已变化，执行时必须重验。
- 动态研究可能受 native bridge、anti-debug、TLS、schema 或账号解锁条件阻塞。
- 不同游戏数据隔离失败会污染 Evidence，必须 fail closed。

## Validation

未来执行至少验证 APK/split hash 与版本、静态工具版本、serialization signature、Session start/stop 与捕获计数、敏感扫描、Huuuge 业务仓库 clean/diff，以及最终 Subagent mode。完整日志留本机，Git 只保存脱敏摘要。

## Acceptance Criteria

未来 canonical Task 只有同时满足以下条件才可进入 Review：

1. package、version、ABI、Android 实例和引擎信息已现场确认。
2. 静态审计覆盖主要 code、native、serialization、network、config/resource 和保护机制。
3. 至少完成一次 User 正常 Spin 的最小动态尝试；成功时给出可复查 structured/raw evidence，失败时给出精确 blocker 和下一验证动作。
4. 明确列出当前可还原与不可还原的数值字段，不把字段存在写成字段有值。
5. 完成 Huuuge Reuse Matrix 和 Cash Frenzy Adapter 边界。
6. 给出 F0–F4 分项等级、置信度、风险和 Adopt/Wrap/Fork/Build/Stop 决策。
7. 所有结论标为 Confirmed / Estimate / Hypothesis / Decision proposal。
8. Huuuge 生产 Collector、SVN 策划包和 `HuuugeResearch` 实例未被修改。
9. 本机 Raw/二进制/账号数据未进入 Git、飞书或聊天。
10. 若使用 Subagents，父会话为受限权限、主 Agent 唯一写入、Handoff 列出实际 Agents，并在结束后恢复 OFF。
11. 更新 canonical Task、CHANGELOG 和 `handoff/CODEX.md`，提交并 push，等待 ChatGPT Review。

## Handoff Required

未来执行完成后必须返回：AI-Workspace commit、实际 package/version/ABI/engine、动态证明与 Evidence Level、F0–F4 结果、Adopt/Wrap/Fork/Build/Stop 建议、可复用 Huuuge 能力与新增 Adapter、下一 Task 建议、`Subagents: <names>` 或 `none`、最终 Subagent mode（应为 OFF），并等待 ChatGPT Review。

## Promotion Gate

本 Candidate 当前**不满足自动晋升条件**。TASK-0020 Accepted 后仍须由 User 明确确认，allocator 完整验证最新 main、active Task overlap、唯一 ID 和分配锁，再生成新 canonical Task；不得复用 `TASK-0018`。
