# TASK-0026 — 【游戏】 Collector 1.0 Engineering

- Status: Accepted
- Project key: CASH-FRENZY
- Human alias:
- Owner: User / ChatGPT
- Executor: Codex
- Priority: P1
- Date: 2026-08-28
- Updated: 2026-08-29
- Candidate provenance: `tasks/candidates/CANDIDATE-20260828-CASH-FRENZY-COLLECTOR-1-ENGINEERING.md`
- Allocation relationship: new
- Related tasks: TASK-0024

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

## Safety

- Raw、source events、完整响应、真实 Session、账号、token、绝对余额、APK、SO 和本机绝对路径只留本机；
- Git 只提交代码、合成测试、字段名、聚合计数、commit 与 Confirmed / Derived / Blocker；
- Adapter 只能复制现有 scoped source record 中已经解码的允许字段，不修改 runtime、请求、返回或业务状态；
- 新 output contract 必须通过兼容层接入现有一键流程，不以改写 Android 9 Hook 换取工程便利；
- 所有 GitHub rename/push 仅作用于 User 明确指定的正式仓库；不复制 DS Sidecar 历史或其他仓库内容。

## Implementation Evidence

### Confirmed

- GitHub 正式仓库已从 `840832144/CashFrenzy_collect` 改名为 `840832144/CF_collect`；default branch 仍为 `main`，公开 Description 使用“【游戏】”。
- ChatGPT Review Round 1 正式记录为 `reviews/TASK-0026-CHATGPT-REVIEW-1.md`：Decision `Needs changes`；READY 与 Root 已通过，唯一 required fix 为 cleanup 未停止本轮 `cf_rt_mon -D` 后台进程。
- 实现分支为 `codex/collector-1-engineering`，Round 1 cleanup 修订 commit 为 `4e6f0625e2e39dfeb6ebb4dfb2fd6a29d5c1999c`。
- ChatGPT Review Round 2 正式记录为 `reviews/TASK-0026-CHATGPT-REVIEW-2.md`：Decision `Needs changes`；LIFO、精确 PID+path、READY、Root、Hook/serializer 与六字段通过，唯一 required fix 为 cleanup 列表函数的 `return ,$array` 与调用方 `@()` 形成嵌套数组。
- Round 2 集合返回语义修订 commit 为 `4df10ec20e79bb737912c8d1b847fae3659031ae`：run/helper 列表函数移除一元逗号，调用方继续用 `@()` 接收扁平 0/1/N 项；空 PID 不触发 ownership residual，空 residual 不生成空 verify error。
- ChatGPT Review Round 3 正式记录为 `reviews/TASK-0026-CHATGPT-REVIEW-3.md`：Decision `Accepted`；reviewed commit 为 `4df10ec20e79bb737912c8d1b847fae3659031ae`，Cleanup 集合返回语义及全部既有边界通过。
- `CF_collect` 实现分支已 fast-forward 合入并推送 `main@4df10ec20e79bb737912c8d1b847fae3659031ae`。
- 新增正式 `adapters/batch_spin.py`、`adapters/keepalive.py`、`adapters/registry.py` 与公共 event helpers；Registry 只路由 exact `kind=lua-pcall-args / messageType=3 / command`，未知命令返回 `None`。
- `batch_spin` allowlist 严格固定六字段；合成 extra `feature/result` 与任意额外字段不会进入 Event、warning schema 或 Spin Records。
- 新 Session 预创建 `source_events.jsonl / events.jsonl / spin_records.jsonl`，finalize 写 `session_manifest.json`，一键流程再生成 `summary.json / summary.md`；manifest 只含相对 artifact path。
- 旧 raw `events.jsonl` 通过只读 compatibility path 重建到 `normalized_events.jsonl`，原文件 hash 保持不变。
- DS Sidecar 仅作为 exact shape、fail-closed/type/truncation、合成测试与输入只读的设计来源；正式 commit 不含 Sidecar 文件、fixture、artifact、`.local/`、真实 Session 或 schema expansion。
- `run_collector.ps1` 保持既有 preflight → server → gadget → forward → bootstrap → scoped probe → User phase → stop → re-extract/summary → cleanup 顺序；cleanup engine 使用可注入 action、严格 LIFO、幂等 stop/verify 与错误聚合。
- Frida helper 返回 `pid / remote_path / started_by_run`；finally 只停止本轮拥有、PID 与 remote path 精确匹配的 server，再删除本轮文件。外部/先前 Session 资源通过 ownership gate 保留并使运行 fail closed。
- cleanup 后回读验证 Probe、server、forward、Gadget/config 与 `/data/local/tmp/cf_*` 均无残留；运行错误、停止失败、验证失败和残留统一聚合，不再静默或互相覆盖。
- READY 现只由已验证的 `hook-status` 建立；`onUIThreadReceiveMessage` 与 `lua_pcall` 必须同时报告已安装。`script.load()`、任意 Frida 消息、错误或 detach 均不能误报 READY。
- Root 口径已统一：Collector 只检测、不改变 BlueStacks Root；自动 cleanup 不包含 Root，Session 后由 User 手动关闭 Root、重启实例并验证 `su -c id` 不再返回 `uid=0`。

### Derived / not dynamically rerun

- 本 Task 为离线工程化，没有启动模拟器、Frida、Gadget 或新 Session，也没有要求 User 再次 Spin；因此只证明 host pipeline 与静态部署 contract，未新增动态稳定性、字段命中率、20-Spin 或 F4 证据。
- Probe `build_javascript` 与 bootstrap JavaScript 经换行归一化后和正式 main 基线逐字一致；Android 9 运行路线据此判定未改，但不把静态相同比作一次新的 runtime 验证。

### Failed attempts / resolved

- Candidate CLI 首次使用 `YYYY-MM-DD` 日期格式被拒绝，未创建文件或占用 ID；第二次 slug 重复项目 key，产生的未提交错误 Candidate 已删除并由 Registry writer 恢复，再使用规范 slug 成功分配 TASK-0026。
- `CF_collect` 首次 commit 因新 clone 没有作者身份而失败；远端仅创建了指向基线的分支，未发布未提交内容。随后只在该仓库复用 AI-Workspace 现有 noreply identity，commit/push 成功，未修改 global Git config。
- AI-Workspace Task 回归的 23 个 disposable tests 全部通过，但套件尾部一次真实仓库二次 validate 因瞬时 `cannot fetch origin/main` 失败；立即独立 `git fetch origin` + `task_cli validate` 复验为 13 canonical / 0 collision / valid，HEAD 与 origin/main 为 0/0。

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

实际结果：Round 1 cleanup 修订 baseline `unittest` 15/15；Round 1 后 focused `unittest` 16/16、可注入 cleanup tests 7/7。Round 2 集合语义修订继续通过 focused `unittest` 16/16、原 cleanup injection 7/7，并新增实际生产函数 shape tests 10/10，覆盖 run/helper 的 0/1/2 PID、ADB 行、路径、residual error、空 PID 与空 verify suppression。Round 3 复验 focused 16/16、cleanup 7/7、production shape 10/10，并正式 `Accepted`。Python compileall、PowerShell 5.1 parser 5/5、六字段冻结、secret/local-data diff scan 与 `git diff --check` 均通过。`cf_cleanup.ps1`、`cf_probe.py`、`adapters/batch_spin.py` 与 `docs/ROOT_TOGGLE.md` SHA-256 保持不变，READY 函数与 reviewed baseline 相同；AI-Workspace Task tests 23/23，Registry 为 13 canonical / 0 collision。Workspace Sync 为 `ON_DEMAND`、0 conflict，provider unavailable、6 stale。未启动模拟器、Root、Frida、Collector，未执行 Spin。Subagents: none。

## Stop conditions

- 需要修改 Android 9 已验证采集路线、扩大业务 schema 或进入新协议层才能完成工程化；
- 无法在不复制 Sidecar 私有/实验材料的前提下建立测试；
- 新 event/session contract 破坏一键运行且无法通过兼容层解决；
- 发现需要 User 重新执行 Spin、购买、充值或提供真实 Session 才能验证。

出现任一条件即停止并报告 blocker，不通过恢复更多字段或迁移更多 Sidecar 内容绕过。

## Handoff

TASK-0026 已经 ChatGPT Review Round 3 `Accepted`。正式实现为 `CF_collect main@4df10ec20e79bb737912c8d1b847fae3659031ae`；AI-Workspace 保存 Task、三轮 Review、Registry、CHANGELOG 与 Handoff。任务结束后不扩大为字段恢复、20-Spin/F4 或其他模块研究；Subagents: none。
