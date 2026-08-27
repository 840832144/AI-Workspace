# Codex Handoff

- Updated: 2026-08-27
- Task: TASK-0021 — Workspace Live Context Hub
- Status: Accepted — pending integration to main
- Branch: `codex/task-0021-live-context`
- Original implementation: `0e902b2ef4c60044a7cb5bac3e75de8cb07c76ad`
- TASK-0020 main merge: `31475bd`
- Latest-main semantic merge: `637840a`
- Final integration commit: this handoff's commit; use branch HEAD from Git
- Workspace Sync mode: `ON_DEMAND`
- WATCH: disabled
- Memory mode: `ASSISTED`
- Subagents: none

## Outcome

ChatGPT Review Round 1 已返回 **Accepted**。正式 Review 记录为 `reviews/TASK-0021-CHATGPT-REVIEW-1.md`；TASK-0021 与 ADR-0007 已更新为 Accepted。最终模式继续为 `ON_DEMAND`，本次 Acceptance 不授权启用 `WATCH`。

TASK-0020 已通过 ChatGPT Review，并先以 merge commit `31475bd` 合入、推送 main。TASK-0021 随后同步该 main，在共享规则中语义保留两套已批准治理：

- Task Registry、显式 `project_key`、latest-main writer gate、remote-CAS reservation、release/finalize 和严格 companion 分类；
- Workspace Sync、Planner Writing Style、Git/飞书 authority、冲突保护、Memory Candidate/Review 和 `ON_DEMAND` freshness。

TASK-0020、TASK-0021、ADR-0006 与 ADR-0007 现均为 Accepted。没有覆盖 Lottery 或其他并行 Task 的正文。

## Context Hub Decision

Wiki scope Gate 未通过，因此最终 binding 保持飞书 Drive 文件夹 + 原生 Docx，不伪称 Wiki。Git 是规则、Task、ADR 与状态的 canonical truth；飞书协作草稿只进入 Candidate/Review。

原 Drive Pilot 保持不变：唯一 Hub、7 个唯一标题、6 个 Git-authoritative `tenant_readable` 文档、1 个协作草稿 `tenant_editable`。本轮 latest-main 集成没有调用飞书写入，没有再次发布、改名、创建重复文档或改变权限。

Document Assistant PR [#1](https://github.com/840832144/document-assistant/pull/1) 保持 OPEN / MERGEABLE，head `29fd9f1a58f2626f180e351133f2cd7571c7b43d`。PR 内容和状态未修改；其 body 记录 8 files / 24 tests 与 live Drive permission/readback Pilot。

## Workspace Sync

交付包括：

- `capabilities/context/README.md`
- `workflows/workspace-sync/README.md`
- `LIVE_CONTEXT_MANIFEST.json`
- `tools/context/workspace_context.py`
- `bootstrap/workspace-sync/`
- ChatGPT、Codex、Generic Agent bindings
- `standards/PLANNER_WRITING_STYLE.md`

正式 `doctor` 通过 manifest、Git、path traversal、Secret 与行文检查。`ON_DEMAND` sync 生成 Host-local `LOCAL_CONTEXT_PACK.md` 与 publish plan。本轮没有提供 provider snapshot，结果为 stale 6、unavailable 1、disabled 2、conflict 0；这表示待 Review 的 Git 变化尚未发布，不虚报 Drive 已同步。

`WATCH` 仍需显式 `--user-approved`，本轮没有启用、安装或调度 watcher、webhook、Scheduled Task 或长期进程。

## Registry and Validation

正式 Task Registry 重建后的真实 inventory：

| Kind | Count |
| --- | ---: |
| canonical | 8 |
| companion | 2 |
| candidate | 1 |
| review | 6 |
| canonical collision | 0 |

关键状态：TASK-0020 Accepted；TASK-0021 Accepted。

- Context Python tests：13/13 passed。
- PowerShell Workspace Context entry：PASS。
- Task tests：23/23 passed。
- Memory tests：35/35 passed。
- PowerShell Task Registry entry：compile、23 fixtures、真实 scan/validate、incident repair 全部 PASS。
- Workspace Sync doctor：`ok=true`，mode=`ON_DEMAND`。
- Context refresh：0 Secret issue、0 broken link，Project Sources=`manual upload required`。

## Generated Artifacts

以下内容已在 latest-main 语义合并后重新生成：

- `tasks/TASK_REGISTRY.yaml`
- `CONTEXT_MANIFEST.yaml`
- `bootstrap/chatgpt/02_CURRENT_STATE.md`
- `bootstrap/chatgpt/generated/PROJECT_SOURCE_PACK.md`
- `bootstrap/chatgpt/generated/PROJECT_SOURCE_REPLACEMENT_LIST.md`
- `CHANGELOG.md`
- 本 Handoff

Project Sources 没有自动替换；Source Pack 只是 Bootstrap / offline fallback，动态状态优先读取 latest Git 与 Live Context。

## Safety and Boundaries

- 未执行或晋升 Cash Frenzy Candidate。
- 未修改 Huuuge、Lottery、Collector、Capture、SVN 或其他业务仓库；仅通过 main 同步已存在的历史提交。
- 未修改 Document Assistant PR、飞书正文、Hub 权限、Document token 或私有 Registry。
- 未读取 Raw Capture、账号、Secret、完整响应或逐笔余额。
- Workspace Sync=`ON_DEMAND`；WATCH disabled；Memory=`ASSISTED`。
- Subagents: none。



<!-- MEMORY-REFRESH:START -->
## Memory Context Refresh

- Generated: 2026-08-27T09:22:42Z
- Effective mode: `ASSISTED`
- Manifest: `CONTEXT_MANIFEST.yaml`
- ChatGPT Project Sources: `manual upload required`
- Private repositories: not read unless explicitly registered and authorized
<!-- MEMORY-REFRESH:END -->
## Exact Next Action

将 Accepted 的 `codex/task-0021-live-context` 合入 AI-Workspace `main`，合并 Document Assistant PR #1；保持 `ON_DEMAND`，不得启用 `WATCH`。
