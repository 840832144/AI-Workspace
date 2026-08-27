# Codex Memory Adapter

本适配器把 Codex 的实质 Task/Review/Handoff 结果接入 `CAP-MEM`。它不依赖 Subagent；TASK-0016 Pilot 最终 Subagent 仍为 `OFF`。

## During a substantive turn

1. 完成正常任务和验证，不让 Memory 流程替代原始交付。
2. 执行静默 Memory Check：长期决定、可复用修复、状态变化、被证伪假设或新 Workflow 才捕获。
3. 当前 Task 已直接更新 Task/Status/Handoff 时不重复生成 Candidate。
4. 需要 Candidate 时调用 `tools/memory/Capture-MemoryCandidate.ps1`，提供最小摘要、稳定 source reference、scope、sensitivity 和 evidence。
5. 运行 validator；ASSISTED 下交给 Review，AUTO 只允许治理标准中的低风险 allowlist。

## Git writer

- 默认只写工作树，由当前 Task 的 Git 流程统一提交。
- 自动 Candidate commit 必须在 clean、非 `main` branch 上显式使用 `--git-commit`；push 需要再显式使用 `--git-push`。
- writer/permission 失败时由 CLI 写本机 Outbox；输出不得说“已上传”。

## Hooks

`tools/memory/hooks/codex-hooks.disabled.json` 是官方 `SessionEnd` contract 的禁用参考。其脚本只保存 transcript-free check marker，不读取 `transcript_path` 或 `last_assistant_message`。本 Task 不安装该 hook、不改 `~/.codex/config.toml`、不重启 Codex；生产激活需要 User 单独授权。
