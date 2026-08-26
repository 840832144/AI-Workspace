# Huuuge Evidence Standard

- Version: 1.0
- Status: Proposed — waiting for ChatGPT Review
- Updated: 2026-08-26
- Scope: `huuuge-android-research` 的研究结论、模块目录、Knowledge Base、报告与交接
- Owner: User；Architecture/Review: ChatGPT；Evidence execution/Git: Codex

本标准统一 Huuuge Research 的证据等级与引用方式。它评价“某项结论当前由什么证据支持”，不评价功能重要性，也不把结构目录完成度、样本数量或主观信心混入 Evidence Level。

## 核心规则

1. Evidence Level 评给一项明确 claim；Knowledge 导航中的模块等级，是该模块当前最强、且满足完整判定条件的代表等级。
2. 等级取“全部条件均满足”的最高一级，不能因单个文件名、字段名、样本量或人工判断跳级。
3. Level、Completion 和 Confidence 是三个独立维度：Level 表示证据强度，Completion 表示研究覆盖度，Confidence 只能作为分析备注。
4. Derived 结论必须引用全部关键输入和计算方法，其等级不得高于最弱的关键输入。
5. 外部研究仓库是实现与原始证据真相源；AI-Workspace 只保存脱敏引用、等级和长期结论。

## Evidence Level（L0–L4）

| 等级 | 名称 | 必须满足的判定标准 | 可以表达 | 不可以表达 |
| --- | --- | --- | --- | --- |
| L0 | Unverified | 只有待验证线索、关键词、未复核 Manual 记录或推断；没有可审计的直接引用 | “存在待验证线索”与明确验证计划 | 结构存在、功能可用、流程或数值规则 |
| L1 | Schema | 至少一条可定位、可版本化的 Schema 引用，能指向 descriptor、service、message、field 或静态结构；没有已关联的当前 Config/Runtime/UI | “结构或接口在该版本中存在” | 当前账号可见、当前服务启用、真实交互已发生 |
| L2 | Configured / Visible | 满足 L1，并有可版本化 Config，或与模块相关的 cross-cutting Runtime/UI 证据；能确认特定 build、时间或账号条件下的配置/可见状态，但没有模块 primary action 的解码闭环 | “在所记录上下文中已配置、下发或可见” | 专用交互已捕获、因果流程、稳定业务规则 |
| L3 | Runtime Observed | 满足 L1，并有脱敏、可定位、可解码的模块 primary Runtime 证据；能够关联 endpoint/message、方向、Session 与 action/result 或状态变化 | “该行为/结构在所记录样本中真实出现” | 跨版本普遍规则、完整概率/经济结论、UI 含义已完全确认 |
| L4 | Triangulated | 满足 L3；同一 build/版本 lineage 下同时具有匹配的 Runtime、UI、Manual 时间线，以及至少一条 Schema 或 Config 引用；关键行为至少有两个独立观察周期且没有未解释冲突 | “在声明的版本、场景与样本范围内完成多源验证” | 未覆盖版本、账号群体或场景的普遍化结论；样本不足时的概率结论 |

### 等级说明

- L0 不是“没有价值”，而是明确阻止线索被误写成事实。
- L2 可以由 Config 或间接 Runtime/UI 支持，但缺少 primary action 时不能升级到 L3。
- L3 的“Runtime”必须是已解码并能回溯到 Session/endpoint 的直接观察；只有计数或关键词命中不够。
- L4 是证据包，不是“样本更多的 L3”。缺少 UI 或 Manual action timeline 时，即使 Runtime 很丰富也保持 L3。
- 模块等级可以高于模块内某条具体 claim；报告必须为关键 claim 单独标级，不能借用模块总等级。

## 引用类型

| 类型 | 代码 | 合格来源 | 必填定位信息 | 单独使用的上限 |
| --- | --- | --- | --- | --- |
| Schema | `SCH` | descriptor、recovered schema、service/message/field map、可审计的静态结构索引 | repository + commit、artifact path、symbol/message/service/field、build/schema version | L1 |
| Config | `CFG` | 脱敏的 feature/config payload、schedule、eligibility、reward/config bundle | repository + commit、artifact path、config key/field path、build、观察时间/有效窗口 | L2 |
| Runtime | `RUN` | 脱敏且已解码的 request/response、event、状态转换或运行输出 | repository + commit、Session/artifact、endpoint/message、方向、时间或序号、decoder/schema lineage | primary 可支持 L3；cross-cutting 最高 L2 |
| UI | `UI` | 脱敏截图、录屏或可复查的界面状态记录 | artifact、build、界面/状态、语言/必要账号条件、时间、关联 action | 单独最高 L2 |
| Manual | `MAN` | 结构化人工操作/观察日志，而非聊天印象 | actor、绝对时间与时区、环境、步骤、观察结果、关联 artifact | 单独保持 L0；只用于关联和复核 |

ZPK 文件名、关键词命中和目录计数只能作为 Schema locator hint，不能单独提升等级。缺少完整 provenance 的截图、日志摘录或人工记忆不构成合格引用。

## Citation ID 与记录格式

Citation ID 使用固定格式：

```text
HGR-YYYYMMDD-<TYPE>-NNN
```

其中 `<TYPE>` 只能是 `SCH`、`CFG`、`RUN`、`UI`、`MAN`。ID 在所属 evidence catalog 中唯一；同一 artifact 支持多个 claim 时复用同一 ID，不复制证据。

每条正式引用必须包含：

```markdown
- Evidence ID: HGR-20260826-RUN-001
  Type: Runtime
  Source: huuuge-android-research@<full-commit>
  Locator: <artifact-path>#<endpoint/message/time-or-sequence>
  Context: <build/schema/decoder/session lineage; sanitized>
  Supports: <one precise claim>
  Limits: <what this evidence does not establish>
  Observed: 2026-08-26T18:23:00+08:00
```

正文可使用紧凑引用：

```text
[HGR-20260826-RUN-001 · Runtime · repo@commit · path#locator]
```

紧凑引用必须能回到完整记录。Git 引用使用完整 commit 固定路径；本地 artifact 必须给出稳定的脱敏相对路径，不记录账号、token、原始 payload 或个人数据。

## Claim 写法

每项结论使用以下最小结构：

```text
Claim: <单一、可证伪的陈述>
Level: L0 | L1 | L2 | L3 | L4
Evidence: <one or more Citation IDs>
Scope: <build/version/account cohort/time window/scenario>
Limits: <仍不能推出什么>
```

禁止使用“已证实”“完整”“稳定”等无范围词。数值、概率、奖励和经济结论还必须声明样本选择、分母、计算方法与不确定性。

## 升级、降级与冲突

- 升级：新增引用后逐条核对目标等级的全部条件，由 ChatGPT Review claim scope，Codex 核对 artifact 与 lineage。
- 降级：引用失效、版本 lineage 不明、解码错误、证据冲突未解释或 source commit 不可访问时，立即降到仍满足条件的最高等级。
- 冲突：保留相互冲突的 Citation ID、版本与场景，不通过删除异常样本制造一致性。
- 过期：新 build 不会自动使旧证据失效，但必须把旧结论限定在原 build/时间范围；跨版本结论需要新证据。
- 审批：L4、概率结论、经济结论和面向策划的最终规则必须等待 ChatGPT Review；User 保留最终产品判断。

## Knowledge Base 映射

TASK-0010 对 TASK-0009 临时等级执行如下迁移，不改变外部 evidence baseline：

| TASK-0009 临时等级 | TASK-0010 统一等级 | 当前模块数 |
| --- | --- | ---: |
| E0 Inferred/static | L0 Unverified | 0 |
| E1 Schema-only | L1 Schema | 22 |
| E2 Cross-cutting/config live | L2 Configured / Visible | 4 |
| E3 Primary live | L3 Runtime Observed | 11 |
| 无对应等级 | L4 Triangulated | 0 |

迁移只统一术语和判定门槛，不把任何模块提升为 L4，也不宣称已有 UI/Manual 三角验证。

## 安全边界

- 不提交 credential、token、玩家标识、逐笔余额、原始 payload、完整 runtime log、APK 或 binary。
- 只引用为复查结论所需的最小脱敏 artifact；敏感 evidence 留在外部受控环境。
- 不通过伪造、重放、修改请求或服务端状态获取证据。
- 人工操作仅限正常产品路径；涉及购买、账号、权限或机器级变更时遵循 User 授权。

## Review Gate

本标准在 TASK-0010 中应用到 Knowledge Base，等待 ChatGPT 对等级门槛、引用字段、L4 三角验证和迁移结果给出 Accepted 或具体修订。在 Review 完成前不据此启动新采集或开发 Evidence Registry。
