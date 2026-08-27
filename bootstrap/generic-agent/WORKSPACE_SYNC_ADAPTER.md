# Generic Agent Workspace Sync Adapter

适用于 Trae + DeepSeek 和其他能执行 Python/PowerShell 的 Agent。开始 Task、Review 或状态查询前运行：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\bootstrap\workspace-sync\Invoke-WorkspaceSync.ps1
```

成功表现是生成 Host-local `LOCAL_CONTEXT_PACK.md`，并返回每个 context 的 `current/stale/conflict/unavailable`。没有飞书 writer 时只读取 local pack 和 Git，不声称 provider 已更新；publish plan 交给批准的 Codex Host。

发现 Feishu-authoritative 草稿时使用 `capture-draft`，保留真实 host、actor 和 revision provenance。发现 conflict 时停止写入，要求 User/Review decision；不得直接覆盖 Git 或飞书。

最终模式保持 `ON_DEMAND`。`WATCH` 只有 User 明确批准长期运行资源后才能启用。
