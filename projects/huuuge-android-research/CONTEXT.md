# Huuuge Android Research — Project Context

## Identity

- Project: `huuuge-android-research`
- Owner: User
- Architecture / RFC / Review / Workflow / Skill: ChatGPT
- Implementation / Automation / Git / Testing / Deployment: Codex
- Game / Product: Huuuge Casino Android numerical research
- Genre: Social Casino
- Platform: Android client in an isolated BlueStacks 5 China research environment
- Target users: 游戏策划、游戏数值策划、系统/活动策划、数据分析
- External repository: [`840832144/huuuge-android-research`](https://github.com/840832144/huuuge-android-research)
- Current evidence baseline: [`bfed5f3`](https://github.com/840832144/huuuge-android-research/commit/bfed5f30e098522ffb98ef5eb7d63e824d68b1c4)

## Objective

建立可长期复用的 Huuuge Casino 游戏策划研究工作台：通过隔离环境中的被动广泛采集、Protobuf 解码、模块结构目录和按需分析，支持策划理解 Slots、Lottery、Missions、Battle Pass、活动、奖励、Offer、经济与成长系统。

AI-Workspace 负责项目控制面和跨 Agent 交接；外部仓库负责采集器实现、验证证据、脱敏结构产物和工程历史。

## Scope

### In scope

- Huuuge Android 客户端中可被动观察的游戏系统结构与数值研究。
- Battle Pass、Slots、Lottery、Task/Missions 四个当前研究入口。
- RPC/Protobuf、静态 schema、ZPK/Lua/native 结构等被动证据渠道。
- 结构优先的 module catalog、normalized data 规划和按需策划报告。
- 策划可部署的采集器工作流及其安全、证据和版本治理。

### Out of scope

- 修改金币、余额、奖励、概率、请求或服务端状态。
- 请求伪造、重放、付费物品获取或作弊绕过。
- 在普通 BlueStacks 环境执行 Root/instrumentation 实验。
- 把 Raw capture、账号/会话标识、APK、`.so`、Frida binary、credential 或完整业务数据复制到 AI-Workspace。
- 在 ChatGPT Review 前开始 TASK-0008 之后的研究实现。

## Dependencies

- External Git engineering source: `huuuge-android-research/main`。
- Planner release: company SVN `trunk/HuuugeCollector`，当前记录版本 `1.0.1`。
- Local sensitive runtime/captures: 仅存在于受控 Windows 研究环境，不进入本项目目录。
- Shared infrastructure: Git、可选 Feishu Document、未来 Document Assistant/Workspace Sync。

## Constraints

- Product constraints: Battle Pass 不是全局 blocker；保持跨模块 broad capture。
- Data constraints: Workspace 只保存脱敏结构事实和稳定链接，不保存 value-bearing capture。
- Security constraints: 只允许隔离研究环境；机器级变更必须显式授权并保留回滚证据。
- Evidence constraints: Confirmed、Hypothesis、Derived 必须分开；目录覆盖不等于完整数值模型。

## Success Criteria

- ChatGPT/Codex 脱离原聊天后，可从本目录恢复项目目标、边界、当前证据和唯一下一步。
- 每个研究请求可明确路由到 Battle Pass、Slots、Lottery、Task/Missions 或跨模块入口。
- 项目状态引用外部 commit/文件，不复制实现或敏感数据。
- 研究执行遵循 Review → Evidence → Implementation → Validation → Memory/Status 的闭环。
- TASK-0008 通过 ChatGPT Review 后才进入下一研究阶段。
