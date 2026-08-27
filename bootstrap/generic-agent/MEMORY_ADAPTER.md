# Generic IDE Agent Memory Adapter

适用于 Trae + DeepSeek 和其他能执行 Python/PowerShell 的项目 Agent。复制本规则到项目级 Agent instructions，不需要安装插件、访问私有实现仓库或配置 Secret。

## Rule

完成长期决定、可复用修复、Task/Handoff、Workflow/Skill 或重要失败经验后：

1. 只生成 `templates/memory/MEMORY_EVENT.yaml` 的结构化摘要，不附完整聊天或日志。
2. 标记 `scope` 与 `sensitivity`。不明确时使用 `unknown`，禁止写公共 Git。
3. 有 AI-Workspace writer：运行 `Capture-MemoryCandidate`；无 writer：加 `--force-outbox`，把返回的 Outbox 路径交给 Codex/Curator。
4. Public candidate 的自动 commit 只在 clean、非 `main` branch 上使用 `--git-commit`；未经授权不 push、不创建 PR。
5. 任何 Secret、Raw Capture、账号数据、逐笔余额、完整响应或敏感日志只记录被拦截 category，不复制 value。

## Minimal command

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\memory\Capture-MemoryCandidate.ps1 `
  -Event .\event.yaml -ForceOutbox
```

成功表现：得到 `captured` 或 `local-only` JSON；`failed` 时保留 Outbox 路径并停止重试上传。
