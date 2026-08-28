# Generic IDE Agent Memory Adapter

适用于 Trae + DeepSeek 和其他能执行 Python/PowerShell 的项目 Agent。复制本规则到项目级 Agent instructions，不需要安装插件、访问私有实现仓库或配置 Secret。

Task、Review 或状态查询前先按 [`WORKSPACE_SYNC_ADAPTER.md`](WORKSPACE_SYNC_ADAPTER.md) 刷新 Context；本文件只负责 Memory Candidate 路由。

新会话或新 Agent 实例在同步最新 Git 后，先读取 `memory/context/WORKSPACE.md`，再按其中来源核对相关 Task、Review、Handoff 和业务证据。Project Source Pack 只在 Git unavailable 时作为可能过期的快照回退。

## Rule

完成长期决定、可复用修复、Task/Handoff、Workflow/Skill 或重要失败经验后：

1. 只生成 `templates/memory/MEMORY_EVENT.yaml` 的结构化摘要，不附完整聊天或日志。
2. 标记 `scope` 与 `sensitivity`。不明确时使用 `unknown`，禁止写公共 Git。
3. `source_host`、`source_project`、`source_actor_alias`、`source_reference` 必须包含有效字母或数字并且是稳定、可复查的真实来源；`unknown`、`n/a`、`none`、`null`、`-`、`tbd` 等占位值只能进入 Outbox，不能写 Git Candidate。
4. Public 内容有 AI-Workspace writer 时运行 `Capture-MemoryCandidate`；无 writer时加 `--force-outbox`。Project Private / Cross-project Private 还必须提供 Host-local Registry 中已批准的 `-RepositoryAlias`，并由 classification、scope、sensitivity、source project 四重 gate 决定是否写对应私有 Git repository；缺失或不匹配继续 Outbox。
5. Public candidate 的自动 commit 只在 clean、非 `main` branch 上使用 `--git-commit`；未经授权不 push、不创建 PR。
6. 任何 Secret、Raw Capture、账号数据、逐笔余额、完整响应或敏感日志只记录被拦截 category，不复制 value。
7. Registry 只能收紧权限；`sensitivity=secret` 与 `scope=local-only` 永远进入本机 Outbox。只有 Curator 能把经明确批准的 public-safe Candidate 写入唯一 Workspace Memory 读视图。

## Minimal command

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\memory\Capture-MemoryCandidate.ps1 `
  -Event .\event.yaml -ForceOutbox
```

成功表现：得到 `captured` 或 `local-only` JSON；`failed` 时保留 Outbox 路径并停止重试上传。
