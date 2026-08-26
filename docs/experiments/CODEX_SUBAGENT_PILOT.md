# Codex Subagent Pilot

本文记录 TASK-0014 的真实试运行证据。目标是验证默认关闭、保守 MANUAL、1 个主 Agent 加 4 个只读 Agent、同一工作区单写入者；不估算或虚构额度数字。

## 环境与范围

- 日期：2026-08-26 至 2026-08-27（Asia/Shanghai）
- Host：Codex Windows Desktop
- 仓库：AI-Workspace
- 初始 commit：`07d9b32`
- 配置：`%USERPROFILE%\.codex\config.toml`
- Global Policy：`%USERPROFILE%\.codex\AGENTS.md`
- 不触碰：Huuuge Collector、Document Assistant、SVN package、飞书云文档、ChatGPT 设置和其他业务仓库

Shell 能定位 WindowsApps 中的 `codex.exe`，但直接执行 `codex --version` / `codex --help` 返回“拒绝访问”，因此没有使用未经确认的 CLI 配置命令。Pilot 改用有时间戳备份、可验证语义完整性的 `[agents]` 最小补丁。

## 实际模型

当前 Host 的模型元数据列出并接受以下组合，实际 spawn 请求均使用对应显式模型与推理强度：

| Agent | Model | Reasoning | Sandbox | 实际调用 |
| --- | --- | --- | --- | --- |
| `repo_explorer` | `gpt-5.6-luna` | `medium` | `read-only` | 是 |
| `knowledge_retriever` | `gpt-5.6-luna` | `medium` | `read-only` | 是 |
| `evidence_test_verifier` | `gpt-5.6-terra` | `high` | `read-only` | 是 |
| `reviewer` | `gpt-5.6-terra` | `high` | `read-only` | 是；发现 4 项提交前阻断 |

## 安装与完整性基线

- 首次安装创建 4 个 Agent 模板，并把模式设为 `OFF`、并发上限设为 4。
- 第二次重复安装报告配置未改变，证明当前环境下幂等。
- `config.toml` 修改前自动生成时间戳备份。
- 首轮 OFF → MANUAL 的每次切换前后，移除 `[agents]` 后的配置语义 SHA-256 均为 `2AD5F739A4C3D95E203D483A8973F52291E09644EFA7276BBE6CCE10B5461837`。后续观测到非 Agent 顶层设置变化，先后涉及 `service_tier` 与 `projects`；其来源未确认，脚本源码没有对应写入路径，因此不归因给任何进程。最终切换会以同一时点的新基线做前后对比，并通过独占锁避免丢失并发更新。
- 初始 Global AGENTS SHA-256 为 `3BA984FEA9C4DC7981DD8D9C172493FF498EFD10A330D142C8B8AD42DF8497F3`；最终同步结果在结束校验记录。
- 验证输出只保存哈希、模式和 Agent 名称，没有输出 MCP 或 secret 值。

## MANUAL 复杂只读场景

23:21:10 开始并行启动 3 个 Agent，约 6 分 29 秒内全部返回：

- `repo_explorer` 找到缺失 Pilot/Bootstrap 文档、Global Policy 尚未同步和集成风险。
- `knowledge_retriever` 核对官方字段、开关、并发与模型继承规则，但其仓库状态报告与主线程不一致。
- `evidence_test_verifier` 发现 legacy alias 被删除、合法 TOML 形态可能误判、同名模板覆盖无备份三个阻断问题。

主 Agent 没有直接接受冲突事实：以当前工作区和配置重新核对，确认资料 Agent 的仓库状态证据不适用于主工作区；其官方资料结论仍可由来源复查。三个脚本阻断问题由主 Agent 修复后再次交给核验 Agent 只读 Review。

最终 `reviewer` 进一步发现：只读沙箱没有限制继承的写入 MCP、多行 TOML 字符串可能被逐行正则误判、配置读取与写入之间存在竞争窗口。READ allowlist 在新会话的工具元数据中仍暴露写入 tools，因此不能作为隔离证据；主 Agent 改为在子 Agent 中完全禁用当前 Document provider 与 `node_repl`，对 multiline 配置 fail-closed，并把模式切换改为独占锁内完成读取、备份和写入。飞书 READ 改由主 Agent 代读后提供脱敏摘要，隔离测试随之增加。

重新安装 deny 配置后，新 MANUAL 会话启动 `knowledge_retriever` 做两个无副作用探针：`feishu_healthcheck` 与 `node_repl` 均为 unavailable，工具元数据也不再显示对应名称。没有调用 Document WRITE/ADMIN，也没有修改外部系统。这证明当前 Host、当前 server 名称和新会话下的技术隔离生效；未来 MCP 新增或改名仍需重新审阅。

本轮说明 Subagent 可以产生有效独立发现，也证明主 Agent 必须核对工作目录、commit 和证据位置，不能把子 Agent 摘要直接提升为 Confirmed。

## Validation Matrix

| 场景 | 结果 | 证据 / 说明 |
| --- | --- | --- |
| OFF 模式 | 通过 | OFF 后新建只读会话，明确报告 `Subagent unavailable`；仍以单 Agent 完成 `17 + 25 = 42` |
| MANUAL 模式 | 通过 | `enabled=true`、并发 4；新会话成功启动 `repo_explorer`，等待完成后由主线程汇总 |
| 简单任务 | 通过 | MANUAL 下仅由主 Agent 更新本行验证记录，没有启动新 Subagent |
| 复杂只读任务 | 通过 | 3 个 Agent 并行探索、资料读取和证据 Review；主线程等待并核对冲突 |
| 复杂实现演练 | 通过 | 子 Agent 全部只读期间，仅主 Agent 修改 Global Policy、ADR 和文档；未发生并行写冲突 |
| 切换回 OFF | 通过 | 最终 `enabled=false`、并发值保留 4；四个模板仍安装；新会话报告 `Subagent unavailable` 并单 Agent 完成 `9 × 7 = 63` |
| 配置完整性 | 通过 | 最终切换即时前后非 `[agents]` 语义哈希均为 `B1BEA162553918B79E8809CE90451280518BA95C638F5B7A6AB44E3ED813160F`；Global、MCP deny 和外部仓库检查通过 |

新会话 OFF 验证耗时约 2 分钟；MANUAL 新会话启动、等待并汇总 `repo_explorer` 耗时约 5 分 32 秒；MCP deny 新会话验证耗时约 4 分 52 秒。这些会话都没有修改文件或外部系统，完成后作为临时 Pilot 任务归档。

最终 OFF 新会话耗时约 2 分 50 秒，确认 Subagent tools 不可用、普通任务继续完成、usage/token 仍为 `null`。验证结束后 5 个临时 Pilot 任务均已归档。

## Usage / Token

当前会话没有提供可归因到各 Subagent 的 usage/token 数字，无法做可靠前后额度对比。只记录了 Agent 数（并行 3 个）、显式模型、推理强度、墙钟窗口和返工：证据核验触发了脚本返工；资料检索的工作区冲突触发了主 Agent 复核。

## 当前判断

- 1+4 的角色边界足以开展 Pilot，不应立即扩到 1+8。
- 默认 OFF 与单写入者必须保留。
- MANUAL 的价值主要来自独立缺陷发现，不等于所有任务都更快。
- 最终模式是 `OFF`。是否长期启用 MANUAL、是否扩大角色或并发，由 User 在 ChatGPT Review 后决定。
