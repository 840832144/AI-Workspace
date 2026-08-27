# Workspace Sync Workflow

## 目标与触发

在 Task、Review、状态查询、Handoff 或正式文档发布前刷新 Context，避免 Host 继续使用过期 Project Sources。当前模式为 `ON_DEMAND`。

## 输入

- 最新 AI-Workspace Git checkout；
- `LIVE_CONTEXT_MANIFEST.json`；
- Host-local state 与可选 provider snapshot；
- 当前 Host 可用的 Document Capability binding。

## 步骤

1. 运行 `Install-WorkspaceSync.ps1` 或 `doctor`。成功表现是 schema、Git、路径、Secret 与行文检查全部通过；失败时停止发布并修复唯一错误。
2. fetch 最新 `main`，确认当前工作分支包含它。工作树有其他 Task 修改时使用独立 linked worktree，不 stash/reset。
3. 运行 `Invoke-WorkspaceSync.ps1`。成功表现是 local pack、状态和 changed-only publish plan 生成；provider 不可达时 pack 仍可用但状态明确为 `unavailable/stale`。
4. Codex Host 通过 Document Capability 对唯一 Drive Context Hub 执行 search/list → create/replace → get → permission verify。Git-authoritative 文档使用 company readable，协作草稿使用 company editable。
5. 任何正式文档发布完成正文回读后，调用 `register_document` 更新唯一 `AI Workspace｜Documentation Hub`，再回读 Documentation Hub；登记失败即发布失败，不允许创建未登记的正式文档或通过重试制造副本。
6. 回读后用 `acknowledge` 记录 revision、source fingerprint 和 provider ref。provider ref 只进 Host-local state。
7. 对 Feishu-authoritative 草稿运行 `capture-draft`。成功表现是 Memory Candidate/Review 或安全 Outbox 可定位；Git canonical 不被直接修改。
8. 发现 `conflict` 时停止自动发布，使用 `resolve-conflict` 记录 User/Review decision。失败时双方内容都保留。
9. Task 完成后更新 Status/CHANGELOG/Handoff，再同步一次。

## Host Binding

- ChatGPT：先 fetch/read Git mirror 和 local pack；直连飞书不可用时不得凭 Project Sources 猜测。
- Codex：执行完整 provider publish/readback/permission workflow，是当前默认 writer。
- Generic Agent：使用相同 PowerShell/Python 入口；没有 provider writer 时只生成 plan/outbox。
- Planner：只打开飞书 Hub；可编辑协作草稿，规则和状态文档通过建议/Candidate 变更。

## 失败与恢复

- Provider offline：使用最近一次 local pack，显示 stale，不声称已同步。
- Lock timeout：说明已有 writer，等待或检查 stale lock，不启动第二 writer。
- Secret/path/schema failure：fail-closed，不生成公开 publish plan。
- 写入中失败：保留 provider 原文档，由 Document Assistant replace rollback 与 Workspace Sync state transaction 恢复。
- Documentation Hub 更新失败：保留已发布文档，流程保持失败；修复后对原链接补充登记，不重试创建。
- Revision conflict：不自动 retry 覆盖；进入 Conflict Review。
