# CANDIDATE-20260828-CASH-FRENZY-COLLECTOR-1-ENGINEERING — 【游戏】 Collector 1.0 Engineering

- Kind: candidate
- Status: Migrated
- Project key: CASH-FRENZY
- Suggested priority: P1
- User decision: Approved
- Source: User request 2026-08-28; formal repository https://github.com/840832144/CF_collect; selective source D:\CashFrenzy-DS-Lab
- Created: 2026-08-28
- Updated: 2026-08-28
- Migrated to: TASK-0026 (`tasks/TASK-0026-COLLECTOR-1-0-ENGINEERING.md`)
- Migrated at: 2026-08-28T10:08:18Z

## Goal

Engineer Collector 1.0 around adapters, a unified event envelope, and fixed local session artifacts without recovering more fields, expanding batch_spin schema, or changing the verified Android 9 capture route.

## Scope

本 Task 只在正式仓库 `https://github.com/840832144/CF_collect` 实施 Collector 1.0 工程化，并保持 Android 9 入站 Hook、Gadget/Frida 生命周期、部署入口与人工操作边界不变。

### Adapter architecture

建立正式 `adapters/` package：

- `batch_spin`：只匹配已确认的 scoped `lua-pcall-args → messageType=3 → command=batch_spin → payload → direct result object`；
- `keepalive`：只匹配既有已知命令和已知字段路径，不做新字段发现；
- `registry`：集中注册、确定性路由和 fail-closed 处理；未知命令不得被误识别为 Spin；
- 公共 Adapter contract：输入只读、结果确定、错误/截断显式、无全局高频日志。

`batch_spin` payload 只允许 TASK-0024 已确认的六个字段：

```text
base_win
bonus_base_win
total_win
coins
win_lines
win_pos_list
```

对象中即使出现其他键，也不得自动纳入 schema、字段发现结果或 Spin Record。

### Unified event contract

正式 Event 顶层固定为四段：

```json
{
  "event": {},
  "adapter": {},
  "source": {},
  "payload": {}
}
```

- `event`：事件名称、event schema version、local event index 与时间；
- `adapter`：adapter 名称和版本；
- `source`：只保存定位与复现所需的脱敏来源信息；
- `payload`：该 adapter 允许输出的固定字段、warnings 与截断状态。

不得把账号、token、完整响应、绝对余额、绝对路径或未批准字段复制到 Git、测试 fixture、README 或 Review 证据中。

### Session artifact contract

每个本地 Session 固定包含：

```text
data/sessions/<session_id>/
  session_manifest.json
  source_events.jsonl
  events.jsonl
  spin_records.jsonl
  summary.json
  summary.md
```

- `source_events.jsonl`：现有 Android 9 路线已经产生的 scoped source records，只留本机；
- `events.jsonl`：Adapter Registry 产生的统一 Event；
- `spin_records.jsonl`：`batch_spin` 统一 Event 的确定性子集；
- `session_manifest.json`：声明 schema version、运行 identity、开始/结束、最终状态、artifact 名称与聚合计数；
- `summary.*`：继续由现有一键流程生成，不扩大业务 schema。

离线重提取必须从 `source_events.jsonl` 确定性重建 `events.jsonl` 与 `spin_records.jsonl`；为兼容旧 Session，可只读回退旧版 raw `events.jsonl`，但新 Session 不再混用 raw 与 normalized contract。

### Selective DS Sidecar migration

只从本机 `D:\CashFrenzy-DS-Lab` 选择性采用以下设计与测试思想：

- exact-target `batch_spin` shape gate；
- fail-closed 输入处理、类型/截断 warning；
- 合成测试数据与输入只读断言。

明确不迁移：Git 历史、`.local/`、真实 Session、fixtures/artifacts、实验报告、schema expansion tool、`same_object_fields`、本机值导出 CLI 与其他 Sidecar 文件。

## Non-goals

- 不继续恢复 `result / win / balance / feature` 或任何新字段；
- 不扩大 `batch_spin` 六字段 schema，不做 20-Spin 或 F4 验证；
- 不改动已验证 Android 9 Hook scope、Lua serializer、启动顺序、人工 Spin 规则或 runtime 注入路线；
- 不建设其他游戏 Adapter，不研究 `BLMessage`、decrypt/framing、XXTEA、Stalker 或全局 Lua API；
- 不自动 Spin、购买、充值、挂机，不修改、伪造或重放请求/响应/余额/奖励；
- 不把 Collector 1.0 变成完整生产 Collector 或策划发布包。

## Deliverables

- 正式 `adapters/` package：`batch_spin`、`keepalive`、`registry` 与公共 event contract；
- Session writer / offline re-extract 对固定 artifact layout 的实现；
- Sidecar-derived、完全合成且不含真实值的 focused tests；
- 对现有 `run_collector.ps1`、setup/bootstrap/probe/stop/cleanup 调用链的回归证据；
- 面向用户的 README/部署说明以“【游戏】”表述，仓库名为 `CF_collect`；运行所需 package、command 和代码标识保持真实技术名称；
- AI-Workspace 中只保存 Task、边界、字段名、聚合测试结果、commit 与 Review Handoff，不复制业务源码或本地 Raw。

## Validation

进入 ChatGPT Review 前至少通过：

1. Adapter focused tests：exact target、wrong kind/message type/command、malformed input、类型 warning、截断、额外字段不扩 schema、输入只读；
2. Registry tests：`batch_spin`、`keepalive` 唯一路由和未知命令 fail closed；
3. Event tests：每行 JSON 可解析且顶层键严格为 `event + adapter + source + payload`；
4. Session tests：固定目录/文件名、manifest artifact map、计数、final status 与 deterministic re-extract；
5. Compatibility tests：旧 raw `events.jsonl` 可只读重提取，新 Session 使用 `source_events.jsonl`；
6. Existing deployment regression：`run_collector.ps1` 仍保持 setup → server → gadget → forward → bootstrap → scoped probe → player → stop → summarize → cleanup 的一键路径；
7. Secret/local-data scan：Git diff 中没有 `.local/`、真实 Session、raw JSONL、APK/SO、账号、token、绝对余额或 Sidecar artifact；
8. 未改 Android 9 JavaScript Hook/serializer 路线，未执行新的动态 Spin；
9. `CF_collect` 与 AI-Workspace 的适用测试、Task Registry、链接与工作树检查通过；
10. Handoff 明确 `Subagents: none`，等待 ChatGPT Review。

## Stop conditions

- 需要修改 Android 9 已验证采集路线、扩大业务 schema 或进入新协议层才能完成工程化；
- 无法在不复制 Sidecar 私有/实验材料的前提下建立测试；
- 新 event/session contract 破坏一键运行且无法通过兼容层解决；
- 发现需要 User 重新执行 Spin、购买、充值或提供真实 Session 才能验证。

出现任一条件即停止并报告 blocker，不通过恢复更多字段或迁移更多 Sidecar 内容绕过。

## Dependencies

TASK-0024 Accepted; CF_collect main; DS Sidecar batch_spin adapter and tests as selective reference only

## Risks

Schema creep, accidental migration of local/raw evidence, and deployment regression

## Promotion Gate

- Candidate 不是可执行入口，也不占用 `TASK-XXXX`。
- 只有 User 明确批准后，才可通过 allocator 完整校验并晋升。
- 晋升前必须检查相关 active Task、最新 `origin/main` 和分配锁。
