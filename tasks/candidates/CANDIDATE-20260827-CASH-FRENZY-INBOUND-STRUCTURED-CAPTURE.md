# CANDIDATE-20260827-CASH-FRENZY-INBOUND-STRUCTURED-CAPTURE — Cash Frenzy Inbound Structured Capture Spike

- Kind: candidate
- Status: Candidate
- Project key: CASH-FRENZY
- Suggested priority: P1 / focused research spike
- User decision: Approved
- Source: User instruction in Codex task on 2026-08-27; this request is the execution contract
- Created: 2026-08-27
- Updated: 2026-08-27
- Migrated to:
- Migrated at:

## Goal

在 Cash Frenzy Android 9 上按稳定性 Gate、inbound-scoped Lua 参数、BLMessage 解码对象、decrypt/framing fallback、Local State Adapter 的顺序，恢复一次普通 Spin 的 direct result/win/balance/feature 至少一项，或按停止条件给出可复查 blocker。

## Dependencies

- `TASK-0022` 已通过 ChatGPT Review 并停止扩大；本 Spike 只复用其 Confirmed evidence、受控本机探针与边界定位。
- User 已删除旧 `AppResearch2`，重新创建同名 Android 9 实例并安装 Cash Frenzy；执行前必须重新确认实例 ID、ADB serial、Android 版本、package、ABI 与前台包，不能沿用旧实例身份。
- Raw、APK、`.so`、完整响应、账号和绝对余额继续留在 `D:\CashFrenzyResearch\local-only\` 或等价受控本机目录，不进入 Git。

## Risks

- Android 9 clean Gadget 仍可能触发 `gum-js-loop`、GLThread 或 native-bridge crash；任何结构化 Hook 前先通过零操作稳定性 Gate。
- Lua API 为高频全局边界；若 scope 限制或序列化预算失效，会导致性能下降、崩溃或采集噪声。
- `BLMessage` 结构、decrypt/framing 路线或 Local State 可能随版本变化；所有字段结论必须以当前安装版本的运行时证据确认。
- 若 Android 9 clean Gadget 仍连续崩溃，或一天内只能证明必须进入全新协议层，则停止并给出 blocker，不无限消耗。

## Execution Contract

本 Candidate 获 User 明确批准；晋升后由 Codex 按以下固定顺序执行，后序路线只有在前序失败并留下证据时才可进入：

1. **稳定性 Gate**：先完成无操作 clean Gadget 稳定性测试，记录 attach/load、进程存活、前台包、crash signature、持续时间和清理结果；此阶段 0 Spin。
2. **Inbound-scoped Lua 参数**：仅在 Cash inbound dispatch thread 且 `onUIThreadReceiveMessage` 调用 scope 内，采集 `LuaStack/lua_pcall` 入参；禁止全局高频 Lua API 日志。
3. **`BLMessage` 解码后对象**：在已确认 inbound type/dispatch/conversion boundary 上读取解码后对象的 shape 与受限字段路径，不把边界命中等同于字段恢复。
4. **decrypt/framing fallback**：只有 Lua 与 `BLMessage` 两条结构化路线都有失败证据时，才研究 `libEncryptorP`、`libsigner`、XXTEA 调用链；Stalker 仅允许单消息 summary，不做持续 trace。
5. **Local State Adapter**：前四步无法得到 direct 字段时，最后评估受控、本地只读状态变化；不得把相邻 outbound `client_coins` 再包装成 direct inbound Balance。

## Serializer Safety Budget

优先实现受限递归 Lua stack serializer，并把限制做成显式常量与测试：

- 默认最大递归深度 `4`；
- 默认每 table / collection 最大元素数 `64`；
- 默认单消息序列化上限 `64 KiB`；
- 循环引用检测、不可安全读取的 userdata/function/thread 只输出类型摘要；
- 超限时写入 `truncated`、`reason`、计数与字段路径，不继续展开；
- 仅在已标记 inbound scope 的目标 thread 激活，离开 scope 立即关闭。

若当前运行时需要调整预算，必须先用 synthetic/offline test 证明边界行为，并在 Task 中记录实际值；不得通过取消限制换取命中率。

## Dynamic Interaction Gate

- 动态阶段先完成无操作稳定性测试。
- 需要真实 gameplay event 时必须暂停并明确通知 User，由 User 手动执行 `3–5` 次普通 Spin；Codex 不点击 Spin、不启用 Auto Spin。
- 只被动观察自然出现的 Feature；禁止自动购买、充值、领取付费奖励、长时间挂机、请求重放、返回值修改、余额或服务器状态修改。
- 第一目标是一次普通 Spin 的 direct `result / win / balance / feature` 中至少一项；未达到时报告每条路线的失败证据与下一边界。

## Deliverables and Evidence

Git 只提交：

- canonical Task 与执行/停止条件；
- 受限 serializer、scope guard、聚合器等工具和 focused tests；
- 脱敏结构、字段路径、类型、聚合计数、稳定性结论与 crash signature 摘要；
- Confirmed / Derived / Blocker、F3/F4 判断和 Adopt / Wrap / Build 建议。

本机保存：Raw、APK、`.so`、完整 response/object dump、账号/session 值、绝对余额、逐 Spin 完整值与机器敏感路径。不得复制到 AI-Workspace、Huuuge Git、SVN、飞书或聊天。

## Acceptance and Stop Conditions

进入 ChatGPT Review 前必须返回并写入 canonical evidence：

1. 实际 Android 9 clean Gadget 稳定性与无操作时长；
2. 命中的结构化边界，以及 scope/thread 证据；
3. direct 恢复的 `result / win / balance / feature` 字段，或每条路线的失败证据；
4. 有足够人工样本时给出 `20-Spin` 复现率；若本轮只获准 3–5 Spin，则明确样本不足，不虚构 20-Spin 结论；
5. F3/F4 判断与 Adopt / Wrap / Build 建议；
6. 0 自动 Spin、0 购买/充值、0 请求/返回修改，Raw/敏感扫描通过；
7. `Subagents: none`（当前 full-access 父会话禁止 MANUAL Subagents）；
8. 提交并 push 后等待 ChatGPT Review，不自行扩大为完整 Collector。

任一停止条件命中时，清理临时 Hook/forward/process，保留本机证据，记录 blocker 后停止：

- Android 9 clean Gadget 连续崩溃；
- 一天内只能证明必须进入全新协议层；
- scope 无法被可靠限制到 Cash inbound dispatch；
- 需要自动 gameplay、付费、请求/响应修改或其他超出授权的操作。

## Promotion Gate

- Candidate 不是可执行入口，也不占用 `TASK-XXXX`。
- 只有 User 明确批准后，才可通过 allocator 完整校验并晋升。
- 晋升前必须检查相关 active Task、最新 `origin/main` 和分配锁。
