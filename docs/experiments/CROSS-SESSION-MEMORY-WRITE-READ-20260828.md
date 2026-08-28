# Cross-session Memory Write → Read Validation — 2026-08-28

## Purpose

验证 TASK-0016 的实际跨会话链路，而不是只验证两个会话能读取既有 Memory：

`ChatGPT 会话 A 产生新信息 → Git Memory Candidate → ASSISTED Curator 晋升 Workspace Memory → 另一个会话 B 从最新 main 读取`

## User approval

User 于 2026-08-28 明确批准执行本次测试（“好，试试这个”）。

## Probe

- Memory key: `workspace.cross-session-write-read-validation`
- Probe marker: `XS-MEM-RW-20260828-070949-A8F0`
- Candidate ID: `MEM-20260828-DB2FE1FE9590`
- Scope: `public`
- Sensitivity: `public`
- Canonical destination: `memory/context/WORKSPACE.md`

## Expected validation sequence

1. ChatGPT 会话 A 只提交 public-safe Candidate，不直接手工修改 `memory/context/WORKSPACE.md`。
2. 另一授权 Codex 会话同步最新 `main`，使用 Memory Validator / Curator 在 `ASSISTED` 模式下显式批准该 Candidate。
3. Candidate 成功晋升后，最新 `main` 的 `memory/context/WORKSPACE.md` 出现上述 memory key 与 probe marker。
4. 会话 B 再次同步最新 `main`，在未由 User 告知 marker 内容的情况下准确返回 key 与 marker，即判定跨会话写→读链路通过。

## Guardrails

- 本次仅验证 Memory Capability，不修改任何现有 Task、Handoff、业务逻辑或执行范围。
- 不包含 Secret、账号标识、原始业务数据、完整聊天或私有 Registry。
- Candidate 未晋升前不得把本记录视为 canonical Workspace Memory。
- 在会话 B 准确返回 probe marker 前，不宣称端到端写→读验证成功。

## Related governance

- Capability: `CAP-MEM`
- Related Task: `TASK-0016`
- Production mode: `ASSISTED`
