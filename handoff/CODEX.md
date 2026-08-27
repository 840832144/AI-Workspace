# Codex Handoff

这是 Codex 的固定交接入口。实现细节以对应外部项目仓库和本机受控配置为准。

- Updated: 2026-08-27
- Task: TASK-0014
- Current state: TASK-0014 Required Fixes implemented and validated; final mode OFF; waiting ChatGPT Review
- Subagents: none（本轮 Review Fix 在宽松权限环境保持 OFF）

## Objective

建立默认关闭、可一键切换、1 个主 Agent 加 4 个只读 Agent、同一工作区单写入者的 Codex Subagent Pilot，不影响现有 MCP、项目配置和单 Agent 工作流。

## Completed

- 建立 4 个 Agent TOML：探索与资料使用 `gpt-5.6-luna` / `medium`，核验与 Review 使用 `gpt-5.6-terra` / `high`，全部 `read-only`。
- 建立安装、`OFF` / `MANUAL` 开关、状态和隔离回归测试脚本，兼容 Windows PowerShell 5.1。
- 安装器同步模板、覆盖前备份、最终强制 OFF；模式脚本修改配置前创建时间戳备份，只补丁 `[agents]`。
- Global AGENTS、本机 `~/.codex/AGENTS.md`、AI Team、Architecture、ADR Index 和 Bootstrap 已加入单写入者与失败降级规则。
- 新增 ADR-0004 与真实 Pilot 记录；没有虚构 usage/token。

## Required Fixes Completed

1. 安装器先验证四个源模板，再完成并验证 OFF，之后才创建或替换 `~/.codex/agents/` 内容。OFF 失败时不触碰模板，也不输出安装成功。
2. inline、multiline、config lock 三种安装失败回归确认：配置字节不变、既有模板不变、其他模板未新增、无 `Installation default: OFF`。
3. Global AGENTS、Bootstrap README、ADR 和 Pilot 明确：MANUAL 严禁与 `--yolo`、Full access、`danger-full-access`、宽松 `/permissions` 或等价父 turn 权限并用。
4. 当前脚本不能可靠检测 live permission；无法确认受限父会话时保持 OFF。本轮环境为宽松权限，因此没有启用 MANUAL 或启动 Subagent。
5. `knowledge_retriever` 改为本地/已提供资料检索；飞书由主 Agent 代读并提供最少、脱敏摘要。

## Actual Models

| Agent | Model | Reasoning | Pilot evidence |
| --- | --- | --- | --- |
| `repo_explorer` | `gpt-5.6-luna` | `medium` | 当前会话与 MANUAL 新会话均成功 spawn |
| `knowledge_retriever` | `gpt-5.6-luna` | `medium` | 当前会话成功 spawn |
| `evidence_test_verifier` | `gpt-5.6-terra` | `high` | 当前会话成功 spawn，并触发脚本返工 |
| `reviewer` | `gpt-5.6-terra` | `high` | 当前会话成功 spawn，发现 4 项提交前阻断 |

Host 接受了上述显式模型与推理组合；运行状态没有独立回显 model/effort 字段，因此证据是 Host 可用模型元数据、成功 spawn 和版本化 Agent contract 的组合。

## Commands

```powershell
# MANUAL
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\bootstrap\codex\Set-CodexSubagentMode.ps1 -Mode Manual

# OFF
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\bootstrap\codex\Set-CodexSubagentMode.ps1 -Mode Off

# STATUS
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\bootstrap\codex\Get-CodexSubagentStatus.ps1
```

模式切换后需要关闭重开 Codex 或新建会话。

## Validation

1. OFF：新会话报告 `Subagent unavailable`，仍以单 Agent 完成 `17 + 25 = 42`。
2. MANUAL：新会话成功启动 `repo_explorer`，主线程等待并汇总。
3. 简单任务：MANUAL 下由主 Agent 单独更新一行 Pilot 记录，没有启动新 Agent。
4. 复杂只读：3 个 Agent 并行完成探索、官方资料核对和证据 Review；主线程核对了相互冲突的工作区证据。
5. 复杂实现演练：Subagent 全部只读，仅主 Agent 修改脚本和文档，没有并行写冲突。
6. 切换回 OFF：最终 `enabled=false`、并发值 4，四个模板保留；新会话报告 `Subagent unavailable` 并完成普通任务。
7. 配置完整性：最终切换即时前后非 `[agents]` 语义哈希均为 `B1BEA162553918B79E8809CE90451280518BA95C638F5B7A6AB44E3ED813160F`；Global 模板与本机文件一致。两轮之间观测到来源未确认的 `service_tier` 与 `projects` 变化；脚本没有对应写入路径，最终通过独占锁避免并发丢失更新。
8. MCP 隔离：READ allowlist 首次新会话验证失败；改为禁用 `feishu-docs` 与 `node_repl` 后，新会话两个无副作用探针均报告 unavailable，且元数据不再显示对应名称。
9. 安装失败原子性：inline、multiline、config lock 三类 OFF 失败均未改变 config 或模板，也没有成功提示。
10. MANUAL 权限边界：模式脚本输出互斥前提与不可自动检测声明；Global Policy 和 ADR 与官方 live override 行为一致。
11. Review Fix 真实重装：安装器先报告 `Current mode: OFF` 与 `OFF verified before template installation: True`，再同步四个模板；非 `[agents]` 语义哈希前后均为 `8CB66F625293ACC45D81E009DC9F13D9362BCB244CED7D4F0F7F7AB484C746E0`。
12. 最终状态：`enabled=false`、并发值 4；四个本机 Agent 模板与版本化模板逐一一致，Global AGENTS 本机文件与仓库模板一致。

## Failed Attempts and Corrections

- WindowsApps 的 `codex.exe` 可定位但 Shell 直接执行返回“拒绝访问”，因此没有假设存在安全 CLI 配置命令。
- 首版脚本会删除 legacy alias、对部分合法 TOML 形态处理不足、覆盖同名 Agent 无备份；由 `evidence_test_verifier` 发现后修复并加入隔离回归。
- 一次超长 inline 临时测试命令被执行策略拒绝；改为版本化、可审阅的 `Test-CodexSubagentScripts.ps1`。
- `knowledge_retriever` 报告的仓库 commit/路径与主线程不一致；主 Agent 没有采信该部分，只保留可由官方来源复查的配置结论。
- `reviewer` 发现 MCP 继承、多行 TOML 和并发丢失更新风险；分别通过禁用当前 MCP、multiline fail-closed、独占配置锁和隔离回归修复。
- ChatGPT Review 发现安装顺序仍可能在 OFF 失败前复制模板；安装器改为 OFF-first commit gate，并加入三类失败原子性回归。

## Usage / Token

当前 Codex 会话与 Subagent 协作接口没有提供可归因 usage/token 数字。已记录 Agent 数、显式模型、推理强度、墙钟窗口和返工，不做额度数字推断。

## Risks and Next-task Candidates

- 候选 1：当官方安全配置命令可从当前客户端调用时，评估替代自维护 TOML 补丁器。
- 候选 2：调查 Subagent 工作目录/commit 证据不一致，建立强制回报 `cwd`、HEAD 和 source scope 的只读前置。
- 候选 3：客户端若未来暴露 per-Agent usage/model telemetry，再建立真实成本与收益对比。
- 候选 4：若未来能可靠证明 per-Agent MCP `enabled_tools` 生效，再恢复 `knowledge_retriever` 直接读取飞书；当前 Pilot 由主 Agent 代读。
- MANUAL 的长期安全前提是受限父会话。除非 Codex 提供可靠 live permission introspection，否则不得把提示信息升级为“自动检测通过”。
- 以上只是下一个 Task 候选，本轮不实施；是否长期开启 MANUAL 由 User 决定。


<!-- MEMORY-REFRESH:START -->
## Memory Context Refresh

- Generated: 2026-08-27T04:17:31Z
- Effective mode: `ASSISTED`
- Manifest: `CONTEXT_MANIFEST.yaml`
- ChatGPT Project Sources: `manual upload required`
- Private repositories: not read unless explicitly registered and authorized
<!-- MEMORY-REFRESH:END -->
## Exact Next Action

ChatGPT 复审两个 Required Fix，给出 `Accepted` 或 `Needs changes`。Review 前不启用 MANUAL，不扩大角色、并发或 Host 范围。
