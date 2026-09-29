# Agent Collaboration Rules

## 当前定位：历史副本（2026-09-16）

本目录随 CR 历史导入，供只读研究参考。当前开发、采集与部署入口见 [Huuuge 项目控制面](../../huuuge-android-research/README.md) 指向的 `840832144/huuuge-android-research`。
下方旧流程保留原始来源，不是当前执行指令；不得因为读取本副本而自动 pull/rebase、写入配置、同步 SVN、提交、真实采集或部署。相关工作必须在当前真相源及正式 Task 的明确授权范围执行。本迁移只适配入口标识，不升级或启动本副本。

This repository is shared by ChatGPT and Codex. Treat the Git repository as the source of truth for cross-agent coordination.

The detailed modification/commit standard is in `CONTRIBUTING.md` and is mandatory for every agent.

## Before doing work

1. Sync the repository safely (`git pull --rebase` or equivalent).
2. Read `AGENTS.md` and `CONTRIBUTING.md`.
3. Read `CURRENT_STATUS.md`.
4. Read the newest section of `COLLAB_LOG.md`.
5. Check `TASKS.md` and `CHANGELOG.md` for recent work/tool/schema changes.
6. Reuse existing scripts and recovered artifacts before rebuilding anything.
7. Preserve unrelated existing user/agent changes; never reset or overwrite them.

## After doing work

Every meaningful work session must update all applicable records before the final push:

1. **`COLLAB_LOG.md`** — append one entry containing actor, date/time, objective, actions, confirmed results/evidence, files changed, validation, blockers/failed attempts, and next recommended action.
2. **`CURRENT_STATUS.md`** — update only confirmed current facts, current blocker, environment facts needed by the next agent, and exact next action.
3. **`CHANGELOG.md`** — append an entry when code, tooling, schemas, outputs, or workflow behavior changed.
4. **`TASKS.md`** — check off completed work and add useful newly discovered tasks.
5. Commit code + records together whenever practical, using the commit format in `CONTRIBUTING.md`.
6. Push completed work before handing off.
7. For planner-facing tooling/workflow/docs, mirror the validated safe allowlist to `trunk/HuuugeCollector` with `scripts\sync_svn_package.ps1`, review only that SVN path, and commit it without including unrelated SVN changes.
8. **Chinese SVN log messages are allowed only through a verified UTF-8 file workflow.** Never pass Chinese directly to `svn commit -m`. Use the CR `svn_submit.py` workflow or `svn commit --encoding UTF-8 --file <utf8-file>`, then read back `svn log --xml` and verify the exact Unicode text. Existing garbled logs are historical and should not be rewritten.

## Actor names

Use exactly one of:

- `ChatGPT`
- `Codex`
- `User`

## Evidence discipline

Separate:

- **Confirmed** — directly observed from APKs, runtime output, tool results, or generated files.
- **Hypothesis** — not yet verified.

Do not promote a hypothesis into `CURRENT_STATUS.md` as fact without evidence.

## Safety / scope

The research workflow is passive. Do not implement or perform:

- balance/coin/reward modification;
- request forgery or replay for gameplay advantage;
- server-state modification;
- bypasses intended to cheat or obtain paid goods.

Dynamic instrumentation should copy already-decoded/serialized client data for analysis.

## BlueStacks rule

Do not modify the user's normal BlueStacks instance for root/instrumentation experiments. Use a clone/research instance and back up configuration before changing it.

## Commit style

Use the full standard in `CONTRIBUTING.md`. Common prefixes include:

- `docs:` documentation / handoff / logs
- `probe:` live capture tooling
- `proto:` protobuf recovery / mapping
- `env:` emulator / Frida environment helpers
- `analysis:` derived system/activity analysis
- `export:` structured output tooling
- `fix:` focused bug fix
- `chore:` repository maintenance

Do not force-push shared `main`, rewrite another agent's pushed history, or use destructive Git commands on existing work.

## Handoff rule

Never finish a session with only an informal chat summary. The next agent must be able to continue by reading the repository alone.
