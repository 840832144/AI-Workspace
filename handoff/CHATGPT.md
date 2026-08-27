# ChatGPT Handoff

这是 ChatGPT 的固定交接入口。长期事实必须同步到 Capability contract、项目 Memory/Status、Task、RFC 或 ADR，而不是只留在聊天中。

- Updated: 2026-08-27
- Task: TASK-0014
- Current state: Changes Requested

## Review Decision

**TASK-0014：Needs changes。**

Pilot 的总体方向和大部分实现已通过审阅：

- 1 个主 Agent + 4 个只读角色边界合理；
- 最终模式恢复为 `OFF`，并发上限为 4；
- 四种模型组合均完成实际 spawn；
- 单写入者、失败降级、MCP deny、配置备份、独占锁和真实 Pilot 记录均有证据；
- 当前客户端没有 per-Agent usage/token 数据，未虚构额度数字。

本轮只剩两个安全收尾项，修复后可再次提交 Review。

## Required Fix 1 — Installation must be fail-safe

当前 `Install-CodexSubagents.ps1` 先复制或替换 `~/.codex/agents/*.toml`，最后才调用 `Set-CodexSubagentMode.ps1 -Mode Off`。

如果 `config.toml` 处于锁定状态、包含补丁器不支持的合法 TOML 形态，或 OFF 补丁因其他原因失败，安装器会抛错，但 Agent 模板已经创建或替换。由于 Codex 的 `agents.enabled` 缺省为启用，这不能满足“安装失败时仍保持默认 OFF”的安全承诺。

必须改为以下任一安全方案：

1. **推荐：先完成并验证 OFF，再复制模板**；或
2. 对模板复制、备份和 OFF 切换建立完整事务，任何失败都回滚本轮新建/替换的模板。

增加隔离回归：

- 使用不支持的 `agents = { ... }`、multiline TOML 或被独占锁占用的 `config.toml` 执行安装；
- 确认安装失败后配置字节不变；
- 确认没有新增模板，既有同名模板也没有被替换；
- 确认没有输出“Installation default: OFF”的误导性成功信息。

## Required Fix 2 — Document parent runtime overrides

官方 Codex 行为是：Subagent 会继承父 turn 的实时 sandbox / permission override；交互式 `--yolo`、`/permissions` 等 live override 可能重新应用到子 Agent，即使自定义 Agent 文件声明了 `sandbox_mode = "read-only"`。

因此文档和 Global Policy 不能把模板中的 `read-only` 描述为任何运行模式下都不可突破的绝对隔离。需要：

- 在 `bootstrap/codex/README.md`、ADR-0004、Global AGENTS 和 Pilot 风险中明确该边界；
- 明确 **MANUAL 模式不得与 `--yolo`、全权限或等价的宽松父 turn 权限同时使用**；
- 如果当前 Host 无法可靠检测 live permission mode，就明确写成 fail-safe 使用前提，而不是伪造自动检测；
- 保留 MCP deny 和单写入者规则作为纵深防护。

## Optional Cleanup

`knowledge_retriever` 当前禁用了 `feishu-docs`，其描述仍写“云文档检索”，容易让主 Agent误以为它能直接读取飞书。建议改为：它只检索本地/已提供资料；飞书由主 Agent读取并提供最少、脱敏摘要。此项可与本次修订一起处理，但不单独阻塞 Review。

## Boundaries

- 不新增 Agent，不提高并发，不启用 AUTO。
- 不修改 Huuuge Collector、Document Assistant、SVN、Secure Tunnel、飞书云文档或 ChatGPT 设置。
- 修订结束后最终模式仍必须是 `OFF`。

## Exact Next Action

Codex 继续处理同一个 TASK-0014，不新开 Task：

1. 把 Task 状态改为 `Changes Requested`；
2. 完成上述两个 Required Fix 和隔离回归；
3. 更新 Task、CHANGELOG、Pilot、ADR、Bootstrap README、Global AGENTS 与 `handoff/CODEX.md`；
4. 重新安装并验证，最终恢复 `OFF`；
5. 提交并推送，再次等待 ChatGPT Review。
