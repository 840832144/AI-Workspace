# Codex Subagent Bootstrap

本目录为 Codex 提供默认关闭、可手动开启、单写入者的子 Agent 试运行配置。它只管理 Codex Global 子 Agent，不修改 MCP、项目配置、Document Assistant、ChatGPT 或其他 Host。

## 模式

| 模式 | 配置 | 行为 |
| --- | --- | --- |
| `OFF` | `agents.enabled = false` | 不加载多 Agent 工具；任务继续由单 Agent 完成 |
| `MANUAL` | `agents.enabled = true`，并发上限 4 | 仅限父会话权限受限，且明确允许至少两个独立只读工作流时委派 |

本 Pilot 没有 `AUTO` 模式。安装完成以及每次试验结束后都应保持 `OFF`。

## MANUAL 权限前提

官方 Codex 行为是：父 turn 的 live sandbox / permission override 会在 spawn 时重新应用到子 Agent，包括 `--yolo` 或交互式 `/permissions` 变更，即使 Agent TOML 声明了 `sandbox_mode = "read-only"`。

因此本 Pilot 明确禁止以下组合：

- `MANUAL` + `--yolo`；
- `MANUAL` + Full access / `danger-full-access`；
- `MANUAL` + 宽松 `/permissions` 或任何等价的父 turn 权限。

当前脚本无法可靠读取正在运行的父 turn live permission。启用 MANUAL 前必须由操作者确认父会话处于受限 sandbox；无法确认时保持 `OFF`，关闭宽松权限并新建受限会话。模板 `read-only`、MCP deny、developer instructions 和单写入者规则是纵深防护，不替代这个前提。

## 四个只读 Agent

| Agent | 用途 | 实际模型 | 推理强度 |
| --- | --- | --- | --- |
| `repo_explorer` | 仓库结构、调用链、文件与符号定位 | `gpt-5.6-luna` | `medium` |
| `knowledge_retriever` | 文档、Memory、RFC 和外部资料检索 | `gpt-5.6-luna` | `medium` |
| `evidence_test_verifier` | Evidence、验收、测试与复现核验 | `gpt-5.6-terra` | `high` |
| `reviewer` | 正确性、安全、回归和范围审查 | `gpt-5.6-terra` | `high` |

四个模板默认设置 `sandbox_mode = "read-only"`，并在子 Agent 中完全禁用当前 Host 的 `feishu-docs` 与 `node_repl`。父 turn 的 live override 仍可能覆盖 sandbox 默认值，因此必须同时满足上一节的受限权限前提。飞书 READ 由主 Agent 完成后，只把任务所需的最少、脱敏资料交给子 Agent。主 Agent 仍是文件、配置、Git、云文档和外部系统的唯一写入者。

## 安装

在 AI-Workspace 根目录执行：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\bootstrap\codex\Install-CodexSubagents.ps1
```

安装器会：

1. 先确认四个版本化模板齐全；
2. 在不触碰 Agent 目录前，把 `%USERPROFILE%\.codex\config.toml` 切换并验证为 `OFF`；
3. OFF 成功后才把模板同步到 `%USERPROFILE%\.codex\agents\`；
4. 覆盖同名但不同的模板前，备份到该目录的 `.backup\<timestamp>\`；
5. 修改配置前创建 `config.toml.bak.<timestamp>`，最终再次报告安装默认 `OFF`。

如果 config 被占用、使用补丁器不支持的 TOML 形态或 OFF 验证失败，安装立即停止：配置字节保持不变，不创建新模板，不替换既有模板，也不输出 `Installation default: OFF`。这保证 OFF 是模板提交前的安全门，而不是安装结束后的补救步骤。

安装器不会覆盖 `~/.codex/AGENTS.md`。Global Policy 必须先审阅并合并 [`../AGENTS.md`](../AGENTS.md)；本机现有文件与模板一致时，才可直接同步。这样可以避免删除个人或组织已有规则。

## 开关命令

启用保守 MANUAL：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\bootstrap\codex\Set-CodexSubagentMode.ps1 -Mode Manual
```

该命令会提示 MANUAL 与宽松 live permissions 互斥，但不会伪造自动检测结果。只有确认父会话为受限权限后才可使用；否则执行 OFF 命令。

关闭：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\bootstrap\codex\Set-CodexSubagentMode.ps1 -Mode Off
```

查看状态：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\bootstrap\codex\Get-CodexSubagentStatus.ps1
```

模式切换后需要关闭重开 Codex 或新建会话。已打开的会话不能作为新配置是否生效的证据。

## 配置安全

- 脚本只修改 `[agents]` 中的 `enabled`、`max_concurrent_threads_per_session`，并在已有 legacy `max_threads` 时将其同步为同一上限。
- 其他 Agent 设置、模型、MCP、权限、通知、Plugin 和 secret 引用保持原样。
- 模式脚本在整个读取—备份—写入期间持有独占文件锁；存在竞争写入者时 fail-closed，避免覆盖同时发生的 Desktop 配置更新。
- 带空格或引号的合法 `[agents]` table/key 可以识别；dotted key、inline table、`[[agents]]` array table 或 multiline string 等当前补丁器不安全支持的形态会 fail-closed，不写配置。
- 状态脚本只输出模式、并发上限、Agent 名称、配置来源和重启提示，不读取或输出凭据值。
- `OFF` 只关闭运行能力，不删除 Agent 模板，因而可以随时恢复 `MANUAL`。
- MCP 限制按当前 server 名称生效。以后新增、改名或替换 MCP server 时，必须先审阅 Agent deny 配置；未知 server 不能被假定为只读。

## 委派规则

1. 简单任务不委派。
2. 复杂任务只把独立只读工作拆给子 Agent。
3. 主 Agent 等待全部相关结果，主动核对相互冲突的证据。
4. 子 Agent 不可用时继续单 Agent，不更换完成标准。
5. 每次 Handoff 写明实际 Agent；没有使用时写 `Subagents: none`。

Pilot 证据见 [`../../docs/experiments/CODEX_SUBAGENT_PILOT.md`](../../docs/experiments/CODEX_SUBAGENT_PILOT.md)。官方配置依据见 [Codex Subagents](https://developers.openai.com/codex/subagents/) 与 [Configuration Reference](https://developers.openai.com/codex/config-reference/)。

维护者可以使用 Windows PowerShell 5.1 运行隔离回归测试：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\bootstrap\codex\Test-CodexSubagentScripts.ps1
```

该测试只在系统临时目录创建隔离 `USERPROFILE`，覆盖 legacy alias、保留非 Agent 配置、并发锁、特殊 TOML/multiline 形态 fail-closed、OFF 失败时模板零变更、模板冲突备份、MCP deny 配置和安装后 OFF；结束后清理临时目录。
