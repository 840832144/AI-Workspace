# Huuuge Android Research — Project Workflow

## Goal

将游戏策划研究请求路由到正确的 Huuuge 证据入口，在不修改游戏或服务端状态的前提下，形成可验证、可交接、可长期复用的结构或数值结论。

## Inputs and Preconditions

- User 明确研究问题、目标模块和期望输出。
- 先读本项目 [`STATUS.md`](STATUS.md)、[`MEMORY.md`](MEMORY.md)、[`Knowledge Index`](KNOWLEDGE/README.md) 和 [`Huuuge Evidence Standard`](../../standards/HUUUGE_EVIDENCE_STANDARD.md)，再进入外部对应 module dossier。
- 外部仓库必须安全同步；现有 Raw/local runtime 必须留在受控环境。
- 需要新采集、外部写入、机器级变更或权限时，先获得明确授权。
- TASK-0008 必须先通过 ChatGPT Review。

## Capability and Skills

- Planner Capabilities: Game Analysis、system structure analysis、evidence-backed report writing。
- Domain Skill categories: Battle Pass、Slot Analysis、Lottery、Task System。
- Analysis Skill categories: Excel、SQL、Python；当前 Workspace 只登记分类，不代表具体 Skill 已实现。
- Delivery: Report Writing、Feishu Document；只有在 User 授权且 Document Assistant contract 允许时使用。
- Tools: external Huuuge Collector、Git、sanitized module catalog；AI-Workspace 不承载这些实现。

## Routing

| Research request | Required first reads | Current safe path |
| --- | --- | --- |
| Battle Pass | `battle_pass.md` + `BattlePass_schema.md` | 先做 schema-level question；需要 live values 时等待 eligible account 和授权 capture |
| Slots | `slots.md` + broad capture summary | 优先复用现有 live evidence；选择 Extractor 前由 ChatGPT/User 定义问题和验收 |
| Lottery | `lottery.md` + TASK-0018 report | 明确区分直接 Toss 奖励、阈值返还、购买与升级关联产出；因果不足时保持 Estimate 并规划 UI/runtime 对照 |
| Task / Missions | `missions.md` + `mini_pass.md` | 分开 generic Missions 与 MiniPass task flow，禁止混写成同一系统 |
| Cross-module | `MODULE_INDEX.md` + collector capability/data-flow docs | 先更新结构目录，再决定是否进入单模块深挖 |

稳定链接见 [`README.md`](README.md)。

## Steps and Ownership

1. **Intake — ChatGPT**：澄清策划问题、模块、时间范围、所需粒度、输出形式和非目标。
2. **Evidence routing — ChatGPT**：从 Knowledge Index 选择 Category/module，再进入 dossier/schema/session entry；为每个关键 claim 标注 L0–L4、Citation ID、scope 和 limits，并区分 Confirmed、Hypothesis、Derived。
3. **Gap decision — ChatGPT + User**：判断现有 evidence 是否足够；若不足，选择等待、静态研究或未来授权 capture。
4. **Execution contract — ChatGPT**：写明 Capability、输入、输出、安全限制和验收证据；需要实现时交给 Codex。
5. **Implementation/analysis — Codex**：仅在明确授权后修改外部仓库、运行采集/分析、测试并提交工程证据。
6. **Review — ChatGPT**：审阅结论是否满足问题、证据纪律和 Game Design 可用性。
7. **Project memory — Codex/ChatGPT**：外部仓库先记录实现/证据；AI-Workspace 只同步长期 Confirmed/Decision 和当前 Status。
8. **Delivery — Owner by output**：报告只引用必要脱敏证据；Feishu/Git 发布遵循各自权限与 source-of-truth 规则。新生成云文档默认企业内可编辑，只有 User 明确要求其他权限时才覆盖。

## Validation

- Evidence required: 符合统一标准的 Schema/Config/Runtime/UI/Manual 引用、source commit、Session/descriptor/version lineage、dossier/schema link、测试或生成输出引用。
- Architecture/meaning reviewer: ChatGPT。
- Implementation/test reviewer: Codex。
- Final product/priority decision: User。
- A report cannot promote a field-name heuristic or incomplete sample to a final numerical rule.

## Failure and Escalation

- Evidence insufficient: record Hypothesis and exact missing evidence; do not invent values.
- Capture/decode failure: update external repo Status/COLLAB_LOG first; do not hide unknown/undecoded data.
- Permission/machine change required: stop and request User authorization.
- Normal BlueStacks target detected: stop immediately; never instrument it.
- ChatGPT/Codex disagree on meaning vs implementation evidence: present both and escalate to User.

## Outputs and Handoff

- Output: updated external evidence/code when authorized; otherwise an approved analysis plan or report reference.
- Workspace update: `MEMORY.md` for durable facts/decisions, `STATUS.md` for current state, `REPORTS/` for safe report indexes.
- Handoff target: ChatGPT for review; Codex receives only accepted implementation/automation tasks.
