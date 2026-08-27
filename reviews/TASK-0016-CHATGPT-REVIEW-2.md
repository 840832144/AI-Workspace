# TASK-0016 ChatGPT Review — Round 2

- Decision: **Needs changes**
- Reviewed implementation commit: `797bb79e2fb335261fdd0f9d587efa09e613fa9f`
- Review date: 2026-08-27
- Final mode observed: `ASSISTED`
- Production Hook / AUTO: not activated

## Passed

本轮三个原 Required Fix 的主体实现已经通过：

1. **Approved Project-private Git routing**：Host-local Registry 对 alias、writer、classification、scope、sensitivity、source project 和外部 Git root 做确定性校验；错配或未授权进入 sanitized Outbox，公共仓库零写入。
2. **AUTO branch / worktree 与事务保护**：AUTO 只允许 non-main linked worktree；canonical target、Candidate、Archive、index 进入统一事务，五类 fault injection 均恢复执行前状态并保持 `promoted=0`。
3. **Provenance gate 主体生效**：CLI、Event file、Generic Agent 已覆盖 `unknown`、`n/a`、`none` 等占位来源。

34/34 回归、Round 2 Pilot、最终 `ASSISTED`、Hook/AUTO 未激活，以及未触碰真实 Huuuge / CR / Collector / Capture 的边界可以保留。

## Required Fix 1 — ASCII `-` 仍可作为 Git provenance

Governance 和交付说明明确把 `-` 列为无效占位值，但实现中的 `PROVENANCE_PLACEHOLDERS` 当前没有 ASCII `-`。`normalize_text("-")` 仍返回 `-`，因此 `source_host`、`source_project`、`source_actor_alias` 或 `source_reference` 使用单个 `-` 时可以绕过 provenance gate。

当前测试只覆盖：

- CLI：`unknown`
- Event file：`n/a`
- Generic Agent：`none`

必须：

1. 将 `-` 纳入确定性拒绝规则，或采用更稳健的“必须包含有效字母 / 数字且不属于占位集合”规则；
2. 对文档声明的全部占位值建立参数化测试；
3. 至少分别通过 CLI、Event file、Generic Agent 三条入口验证 `-` 进入 Outbox，Public / Private Git Inbox 均为 0。

## Required Fix 2 — `sensitivity=secret` 必须是不可被 Registry 放开的硬边界

Memory Capability 与 Governance 规定 Secret、Token、Raw Capture、账号数据等不得进入 Git。当前 Project-private 路由按 Registry 的 `allowed_sensitivities` 判断；若 Registry 被误配为允许 `secret`，实现没有额外的不可绕过 hard deny。只要正文没有命中 Secret pattern，`project-private + sensitivity=secret` 仍可能写入私有 Git Inbox。

必须：

1. 在 Registry 路由前加入确定性 hard deny：`sensitivity=secret` 永远只进入经过脱敏的本机 Outbox；
2. `scope=local-only` 同样不得被任何 repository alias / classification 提升为 Git 写入；
3. 增加恶意 / 误配 Registry 回归：即使 `allowed_sensitivities` 显式包含 `secret`，公共和私有 Inbox 仍为 0，Outbox 中不含 Secret literal；
4. 文档明确：Registry 只能进一步收紧权限，不能放宽 Global Safety Contract。

## Boundaries

- 继续同一个 TASK-0016，不新增 Memory 架构或外部 Provider。
- 最终模式保持 `ASSISTED`；不激活 Hook 或 production AUTO。
- 不影响 TASK-0018 Lottery 报告、TASK-0019、Huuuge、Collector、Capture、飞书或 Document Assistant。

## Acceptance for Round 3

- 上述两个漏洞均有实现修复和回归证据；
- 原 34 项测试继续通过；
- 新增测试覆盖全部 documented placeholder 与 Secret Registry override；
- Context refresh 仍为 0 Secret issue、0 broken link；
- Git 工作区干净并推送，等待 ChatGPT Review。
