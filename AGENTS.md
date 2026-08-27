# Agent Entry Point

This repository is the governance and coordination control plane for the Game Planner AI Workspace. Its default and only business domain is Game Design; it is not a general-purpose AI platform or a business-code repository.

Before making changes:

1. Pull the latest `main` safely.
2. Run `bootstrap/workspace-sync/Invoke-WorkspaceSync.ps1` when available; treat `stale/conflict/unavailable` as explicit state, not permission to guess.
3. Read `AI_TEAM.md`, `ARCHITECTURE.md`, `CONTRIBUTING.md`, and `standards/PLANNER_WRITING_STYLE.md`.
4. Read the relevant file under `handoff/`.
5. Read the affected RFC, ADR, project Status, and `CHANGELOG.md`.

Rules:

- Keep confirmed facts separate from hypotheses.
- Keep all models, Skills, Workflows, Templates, and projects within the Game Design domain.
- Inherit cross-project Capability Discovery and shared Document Capability rules from Global Codex guidance. Resolve the Capability before selecting an implementation; do not turn this repository into a runtime tool catalog, installer, endpoint registry, credential store, or connection-status source.
- When describing domain boundaries, use the generic term “non-game domains” without listing specific examples.
- Write planner-facing and user-facing documents primarily in Chinese. Keep other languages only for proper names, commands, filenames, stable technical terms, or necessary side-by-side explanations.
- Grant company-editable access to every newly generated cloud document by default unless the User explicitly requests private, read-only, or no-edit access. If an administrator policy blocks sharing, preserve the created document and report the permission failure; never create a duplicate as a retry.
- 所有正式飞书文档必须登记到唯一的 `AI Workspace｜Documentation Hub`；Git 仍是真相源，Hub 只提供飞书导航。正式创建必须完成文档回读、自动登记与 Hub 回读，任一步失败都不能声称完成，也不能通过重试创建制造重复文档。Hub 只能由 Document Assistant 自动维护。
- Do not copy business code, credentials, private datasets, or full runtime logs into this repository.
- Preserve project repositories as the source of truth for implementation.
- Before creating, renumbering, promoting, or telling another Agent to execute a new Task, sync latest `main` and run the Task Registry validator. Use the remote-CAS allocator reservation from a non-main independent linked worktree; keep it until the canonical Task enters main and is finalized, or release it only when abandoned before creation. Never guess from chat, memory, a partial search, Project Sources, or `max + 1`. Canonical identity is global `TASK-XXXX`; new canonical Tasks require an explicit valid `project_key`, and optional alias does not replace the ID. On collision, stale Git, Registry drift, active-scope ambiguity, or lock conflict, fail closed and preserve the first canonical Task.
- Update the relevant handoff and project Status when work changes shared state.
- Commit documentation and coordination records together, then push before handoff.
- Keep Workspace Sync in `ON_DEMAND` unless the User explicitly approves `WATCH`. Provider drafts enter Candidate/Review; they never overwrite Git canonical content directly.

## Memory Check

After a substantive Task, Review, decision, reusable fix, workflow change or Handoff, silently check whether durable information was created. Follow `standards/MEMORY_GOVERNANCE.md`:

- never store a full transcript, Secret, Raw Capture, account data, full response or sensitive log;
- route Public-safe content to a Candidate, project-private content to its private repository, and unavailable/unclear routes to the local Outbox;
- run deterministic validation before Git write and never silently overwrite canonical memory;
- respect the Host-local OFF / ASSISTED / AUTO mode;
- update canonical Task, Status and Handoff directly when the current task already requires those changes; do not create a duplicate Candidate for the same edit.
