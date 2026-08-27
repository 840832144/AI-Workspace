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

成功表现：输出一行 JSON，`status=captured` 且给出目标 repository 的 `memory/inbox/` 路径。Public 内容写当前 `public-control-plane`；Private 只有通过下一节 Registry contract 才写批准私有 Git repository。Local-only、unknown、writer unavailable 或 Registry 不匹配输出本机 Outbox 路径，不写公共 Git。

所有 Git Candidate 必须提供真实且稳定的 `SourceHost`、`SourceProject`、`SourceActorAlias`、`SourceReference`。`unknown`、`n/a`、`none`、`-` 等占位值会进入 Outbox，不会被“非空”检查误放行。

## Approved private Git routing

Project-private 示例：

```powershell
.\tools\memory\Capture-MemoryCandidate.ps1 `
  -Event .\private-event.yaml `
  -RepositoryAlias approved-private-project
```

Host-local `repositories.json` contract：

```json
{
  "schema_version": "1.0",
  "repositories": [
    {
      "alias": "approved-private-project",
      "path": "<absolute-private-git-root>",
      "enabled": true,
      "writer_enabled": true,
      "classification": "project-private",
      "allowed_scopes": ["project-private"],
      "allowed_sensitivities": ["internal", "confidential"],
      "allowed_source_projects": ["approved-project-alias"]
    }
  ]
}
```

Cross-project hub 使用 `classification=cross-project-private-hub` 与 `allowed_scopes=["cross-project-private"]`。Registry 必须位于 Host-local state directory；目标必须是 public AI-Workspace 外部的独立 Git root。alias 不唯一、writer disabled、classification/scope/sensitivity/source project 不匹配、相对路径、非 Git root 或回指 public repository 均 fail closed 到 Outbox。不要把 Registry 提交 Git。

## Validate and curate

```powershell
.\tools\memory\Validate-MemoryCandidate.ps1 .\memory\inbox\MEM-....md
.\tools\memory\Curate-MemoryCandidates.ps1
```

- ASSISTED：安全 Candidate 进入 `memory/review/`。
- AUTO：只有高分、高置信、有 evidence、目标不存在的 `solutions/<slug>/README.md` 可自动晋升，并且 Curator 必须运行在非 main/master 的 independent linked worktree；工作树除 `memory/inbox/` 外有变化时 fail closed。
- 已存在目标、冲突、规则、ADR、Capability 和跨项目策略始终 Review。
- AUTO promotion 把 target、Candidate、Archive、index 作为一个 transaction；任一失败恢复四者执行前状态且 `promoted=0`。回滚失败会生成 Host-local recovery record，并阻断后续 AUTO 直到人工解决。

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

仅用于 Context refresh 的只读/同步条目也可使用简化 Registry，但 `writer_enabled` 缺失等同于 false，不能用于 Private capture：

```json
{
  "schema_version": "1.0",
  "repositories": [
    {"alias": "approved-private-project", "path": "<absolute-local-path>", "enabled": false, "writer_enabled": false}
  ]
}
```

只有 User/管理员明确授权后才把条目设为 `enabled=true`。`-Sync` 遇到 dirty repository 或 pull 失败会返回非零并标记 `sync_complete=false`，不会声称已读取 latest。

## Git writer policy

默认 capture 只写目标本地工作树。需要自动 Candidate commit 时，先在 clean repository 创建非 `main` branch，再显式传入 `--git-commit`；需要 push 再加 `--git-push`。AUTO canonical promotion 的门槛更高：必须使用 linked worktree。工具发现 main/master、主 checkout、无关 dirty change或 Git identity/status 变化时 fail closed。

## Local state and kill switch

Host-local mode、lock 与 Outbox 默认位于操作系统 state directory，不进入 Git。测试可传全局参数：

```powershell
.\tools\memory\Invoke-MemoryCli.ps1 --root C:\temp\repo --state-dir C:\temp\state status
```

`OFF` 不生成 Candidate。生产默认是 `ASSISTED`；AUTO 需要 User 明确决定后才可成为长期默认。
