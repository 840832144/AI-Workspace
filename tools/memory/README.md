# Memory Tooling

本目录是 TASK-0016 的 reference implementation。核心只依赖 Python 3 标准库；PowerShell 文件是 Windows 一键入口。工具不会读取完整聊天、本机 Codex memory 正文、私有业务仓库或 Capture 数据。

## First run

```powershell
.\tools\memory\Get-MemoryStatus.ps1
.\tools\memory\Set-MemoryMode.ps1 -Mode Assisted
```

看到 `mode=ASSISTED` 即成功。失败时先确认 `python --version`，不要安装外部 Memory 服务。

## Capture

```powershell
.\tools\memory\Capture-MemoryCandidate.ps1 `
  -Title "Reusable public solution" `
  -Type solution `
  -Scope public `
  -Sensitivity public `
  -SourceHost codex `
  -SourceProject AI-Workspace `
  -SourceActorAlias Codex `
  -SourceReference TASK-0016 `
  -RelatedTask TASK-0016 `
  -DurabilityScore 5 `
  -ReuseScore 5 `
  -EvidenceScore 5 `
  -Confidence 0.95 `
  -Summary "Short durable summary without transcript or secrets." `
  -Evidence "commit and test reference" `
  -CanonicalDestination solutions/example/README.md
```

成功表现：输出一行 JSON，`status=captured` 且给出 `memory/inbox/` 路径。Private、Local-only、unknown 或 writer unavailable 会输出本机 Outbox 路径，不写公共 Git。

## Validate and curate

```powershell
.\tools\memory\Validate-MemoryCandidate.ps1 .\memory\inbox\MEM-....md
.\tools\memory\Curate-MemoryCandidates.ps1
```

- ASSISTED：安全 Candidate 进入 `memory/review/`。
- AUTO：只有高分、高置信、有 evidence、目标不存在的 `solutions/<slug>/README.md` 可自动晋升。
- 已存在目标、冲突、规则、ADR、Capability 和跨项目策略始终 Review。

## Refresh Project context

```powershell
.\tools\memory\Refresh-ProjectContext.ps1
```

生成/更新：

- `CONTEXT_MANIFEST.yaml`
- `bootstrap/chatgpt/02_CURRENT_STATE.md` managed block
- `bootstrap/chatgpt/generated/PROJECT_SOURCE_PACK.md`
- `bootstrap/chatgpt/generated/PROJECT_SOURCE_REPLACEMENT_LIST.md`

成功输出固定包含 `manual_upload_required=true`。请按替换清单手动更新 ChatGPT Project Sources；不要用浏览器脚本模拟可靠 API。

默认不读取私有仓库。管理员可在 Host-local state directory 创建 `repositories.json`，并显式使用 `-IncludeRegisteredRepositories`；需要在 clean repository 先做 `git pull --ff-only` 时再加 `-Sync`。私有仓库细节不会写进公共 Manifest。

Host-local registry 格式：

```json
{
  "schema_version": "1.0",
  "repositories": [
    {"alias": "approved-private-project", "path": "<absolute-local-path>", "enabled": false}
  ]
}
```

只有 User/管理员明确授权后才把条目设为 `enabled=true`。`-Sync` 遇到 dirty repository 或 pull 失败会返回非零并标记 `sync_complete=false`，不会声称已读取 latest。

## Git writer policy

默认 capture 只写本地工作树。需要自动 commit 时，先在 clean repository 创建非 `main` branch，再显式传入 `--git-commit`；需要 push 再加 `--git-push`。工具发现 main/master 或无关 dirty change 时 fail closed 并写 Outbox。

## Local state and kill switch

Host-local mode、lock 与 Outbox 默认位于操作系统 state directory，不进入 Git。测试可传全局参数：

```powershell
.\tools\memory\Invoke-MemoryCli.ps1 --root C:\temp\repo --state-dir C:\temp\state status
```

`OFF` 不生成 Candidate。生产默认是 `ASSISTED`；AUTO 需要 User 明确决定后才可成为长期默认。
