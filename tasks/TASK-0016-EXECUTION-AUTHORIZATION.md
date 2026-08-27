# TASK-0016 Execution Authorization

- Kind: companion
- Status: Ready
- Authorized by: User
- Authorized at: 2026-08-27
- Canonical design: [`TASK-0016-Automatic-Cross-Conversation-Memory-Curation.md`](TASK-0016-Automatic-Cross-Conversation-Memory-Curation.md)
- Concurrent operation: TASK-0015 Huuuge Lottery capture remains active

## Decision

User has explicitly said **“开始 TASK-0016”**. The execution gate in the canonical TASK-0016 is satisfied. Codex may begin implementation now.

The canonical task header still says `Draft` because this authorization is being recorded without rewriting the long task body. Codex must treat this authorization as the current `Ready` state and, in its first implementation commit, normalize the canonical task header to `In Progress`.

## Parallel-safety boundary

TASK-0016 may run in parallel with the active Lottery capture only under these limits:

- Work in `AI-Workspace`; do not modify `huuuge-android-research`, the running Collector, the current Capture Session, company SVN, AI Document Assistant or Feishu documents.
- Do not stop, restart, reconfigure or inspect the live Collector Session.
- Do not analyze or summarize TASK-0015 capture data until User explicitly says the experience is complete.
- Reuse-first research, architecture, repository implementation, schemas, templates and isolated tests may start immediately.
- Production activation that would restart Codex, replace Global runtime instructions, install always-on hooks or alter another running Host must remain disabled until it is proven non-disruptive and User authorizes activation.
- Memory automation must finish the Pilot in a safe mode; `AUTO` may be tested in isolation, but must not silently become the production default.

## Required first actions

1. Pull latest `AI-Workspace/main`.
2. Read Global/Project `AGENTS.md`, the canonical TASK-0016, this authorization, current Handoff, relevant ADRs and current ChatGPT source pack.
3. Mark the canonical TASK-0016 `In Progress` in the first implementation commit.
4. Perform Reuse-first Solution Discovery before building.
5. Keep TASK-0015 capture completely out of scope.

## Completion

When implementation is ready for Review, Codex must update the canonical task to `Review`, update `CHANGELOG.md` and `handoff/CODEX.md`, report the final Memory mode, tests, affected Hosts, unresolved blockers and commit, then wait for ChatGPT Review.
