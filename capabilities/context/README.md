# Context Capability

- ID: `CAP-CONTEXT`
- Status: Proposed / Waiting for ChatGPT Review
- Scope: Shared governance capability
- Contract owner: ChatGPT
- Implementation owner: Codex / approved Host adapters
- Related Task: `TASK-0021`
- Related ADR: [`ADR-0007-Workspace-Live-Context-Hub.md`](../../docs/adr/ADR-0007-Workspace-Live-Context-Hub.md)

## Outcome

Context Capability 让 ChatGPT、Codex、Generic Agent 和策划在开始 Task、Review 或状态查询前获得同一份可核验的新鲜上下文，并在 Git、协作文档和本地 pack 之间保持明确 authority、冲突保护和可回滚状态。

飞书 Wiki、Drive Docx、GitHub 和 local pack 都只是 Implementation Binding，不是 Capability 名称。Capability 不登记 endpoint、credential、document token 或本机 Registry。

## Operations

| Operation | Outcome | Class | Required Input | Success Evidence |
| --- | --- | --- | --- | --- |
| `CONTEXT_SYNC` | 计算 Git/provider 变化并刷新 local pack | READ / local WRITE | Manifest、Git、可选 provider snapshot | 每个对象得到 `current/stale/conflict/unavailable`，pack 带 commit 与时间 |
| `CONTEXT_STATUS` | 查看 freshness、mode 和冲突 | READ | Manifest 与 Host-local state | 返回脱敏状态，不返回 provider token/ref |
| `CONTEXT_DOCTOR` | 验证 schema、路径、Git、Secret 和行文 | READ | Repository 与 Manifest | 所有硬检查通过或 fail-closed |
| `CONTEXT_PUBLISH` | 生成并应用 Git → provider 的最小变更 | WRITE | Git-authoritative source、provider binding | 只发布 changed objects，回读 revision/fingerprint/权限 |
| `CONTEXT_CAPTURE_DRAFT` | 把 provider-authoritative 草稿送入 Candidate/Review | WRITE | Provider snapshot、真实 provenance | Memory Candidate/Outbox 可定位，Git canonical 未被覆盖 |
| `CONTEXT_RESOLVE_CONFLICT` | 记录人工决定并生成单向后续动作 | WRITE / Review | Conflict、decision reference | 双方内容保留，resolution record 可审计，无静默覆盖 |

## Authority Contract

每个 Context 对象必须声明唯一 authority：

- `git`：Git 是 canonical；provider 修改只形成 Conflict/Candidate。
- `feishu`：飞书是协作草稿界面；内容必须经 Candidate/Review 才进入 Git。
- `external-review`：引用其他正在 Review 的正式文档；本任务不复制或覆盖。

`scope` 与 `sensitivity` 必须同时声明。Public local pack 只能包含 `public/public`；Project Private、Local-only、Secret、Raw Capture、账号、完整响应和逐笔余额不得进入公共 Git、飞书 Hub 或日志。

## Freshness and Conflict

Context 状态只根据稳定 fingerprint、provider revision 和 acknowledged baseline 判定，不按标题猜测：

- `current`：两侧与已确认 baseline 一致；
- `stale`：单侧有待发布或待捕获变化；
- `conflict`：两侧都改变，或 provider 改动 Git-authoritative 内容；
- `unavailable`：provider/Git 当前不可达，使用最近验证 pack 并明确标记；
- `disabled`：对象等待 Review 或未进入当前 Live Set。

冲突时禁止覆盖。`keep-git` 只生成 publish 动作，`keep-provider` 只生成 Candidate；两者都需要真实 decision reference。

## Mode and Safety

- `OFF`：不自动传播，仍允许 User 显式运行同步。
- `ON_DEMAND`：Task、Review、状态查询前同步；当前批准默认。
- `WATCH`：持续监听；只有 User 明确批准外部资源和生产启用后才可设置。

Host-local state 使用单 writer lock、原子写入和失败回滚；故障时不删除原文档、不覆盖 canonical、不虚报已同步。Provider 不可用时保留 local pack 与 publish/Candidate plan。

## Current Binding

当前选择为飞书 Drive 文件夹 + 原生 Docx。AI Document Assistant 提供文档和目录操作；Workspace Sync reference implementation位于 `tools/context/`，Windows 入口位于 `bootstrap/workspace-sync/`。飞书 Wiki 因当前应用缺少 Wiki scope 而不满足 Gate，切换条件见 ADR。
