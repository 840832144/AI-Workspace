# Agent Entry Point

## 单次克隆与 CR 路由

全局稳定规则的版本化阅读入口是 `bootstrap/AGENTS.md`；无需改写 Host 的全局配置。
CR 任务继承本文件后读取 `projects/cr/AGENTS.md`、`README.md`、`STATUS.md`，从 `.agents/skills/cr-project/SKILL.md` 选择唯一专项正文。目录内相对路径以 `projects/cr/` 为准；从子目录启动也须读 Workspace 的 Task / Handoff。
迁移候选在 `codex/cr-subtree-migration`，Review 期间保留当前分支，安全 fetch main 后检查并发，不自动切换分支或把 main pull 进候选。仅 User 确认合并后切换日常入口。不要新增重复哈希校验；使用直接 diff、来源 commit、祖先关系及实际功能验收。

This repository is the governance and coordination control plane for the Game Planner AI Workspace. Its default and only business domain is Game Design; it is not a general-purpose AI platform. It also hosts the User-approved CR design materials and analysis tools under `projects/cr/` (RFC-0005).

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
- Apply the canonical terminology rule in `standards/PLANNER_WRITING_STYLE.md` to every Agent output. Default to accurate, restrained wording a planner can understand; retain exact terms such as Root, Frida, Hook, reverse engineering, decryption, bypass, modification, or exploit whenever reproducibility, engineering judgment, authorization, compliance, or risk depends on them. Never rename or blur an operation to evade safety checks, permission checks, User authorization, or Review, and never exaggerate passive research as an attack.
- Grant company-editable access to every newly generated cloud document by default unless the User explicitly requests private, read-only, or no-edit access. If an administrator policy blocks sharing, preserve the created document and report the permission failure; never create a duplicate as a retry.
- 所有正式飞书文档必须登记到唯一的《AI Workspace｜文档导航中心》；Git 仍是真相源，导航中心只提供飞书导航。正式创建必须完成 `create_document → 文档回读 → register_document → 文档导航中心回读 → Success`。导航中心更新失败时，不删除已创建文档、不重复创建，返回失败并等待修复；不允许出现“正式文档已创建，但导航中心没有登记”的完成状态。导航中心只能由 Document Assistant 自动维护。
- 任何值得跨对话长期保留的产品想法不得只停留在聊天；必须按 `standards/IDEA_GOVERNANCE.md` 防重并进入唯一 Product Roadmap 的 `Current / Backlog / Ideas / Done` 之一。ChatGPT 在相关 Task 收尾时主动生成 Idea Handoff，Codex 负责从最新 Git 更新 Roadmap；Roadmap 不自动授权或创建 Task。
- CR design materials and analysis tools approved by RFC-0005 belong in `projects/cr/`. The three explicitly approved Top Tycoon workbooks and their history are included; this does not authorize other account data, Secrets, private registries, raw captures, full responses or sensitive logs.
- Preserve external project repositories and company SVN as their implementation/configuration sources of truth. CR daily design/tool changes use this repository after cutover; do not write both repositories.
- Before creating, renumbering, promoting, or telling another Agent to execute a new Task, sync latest `main` and run the Task Registry validator. Use the remote-CAS allocator reservation from a non-main independent linked worktree; keep it until the canonical Task enters main and is finalized, or release it only when abandoned before creation. Never guess from chat, memory, a partial search, Project Sources, or `max + 1`. Canonical identity is global `TASK-XXXX`; new canonical Tasks require an explicit valid `project_key`, and optional alias does not replace the ID. On collision, stale Git, Registry drift, active-scope ambiguity, or lock conflict, fail closed and preserve the first canonical Task.
- Update the relevant handoff and project Status when work changes shared state.
- Commit documentation and coordination records together, then push before handoff.
- Keep Workspace Sync in `ON_DEMAND` unless the User explicitly approves `WATCH`. Provider drafts enter Candidate/Review; they never overwrite Git canonical content directly.

## Memory Check

After a substantive Task, Review, decision, reusable fix, workflow change or Handoff, silently check whether durable information was created. Follow `standards/MEMORY_GOVERNANCE.md`:

- at the start of a new session, sync latest Git `main`, read `memory/context/WORKSPACE.md`, then verify relevant Task, Review, Handoff and business evidence; use Project Source Pack only as a stale-marked fallback when Git is unavailable;
- never store a full transcript, Secret, Raw Capture, account data, full response or sensitive log;
- route Public-safe content to a Candidate, project-private content to its private repository, and unavailable/unclear routes to the local Outbox;
- run deterministic validation before Git write and never silently overwrite canonical memory;
- respect the Host-local OFF / ASSISTED / AUTO mode;
- update canonical Task, Status and Handoff directly when the current task already requires those changes; do not create a duplicate Candidate for the same edit.
- treat `sensitivity=secret` and `scope=local-only` as hard deny before any Registry routing; Registry may tighten but never loosen the Global Safety Contract.
