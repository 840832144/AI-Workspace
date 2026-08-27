# Memory Curation Workflow

- Status: Proposed / Waiting for ChatGPT Review
- Capability: [`CAP-MEM`](../../capabilities/memory/README.md)
- Standard: [`MEMORY_GOVERNANCE`](../../standards/MEMORY_GOVERNANCE.md)

## Trigger

实质 Task、Review、长期决定、可复用修复、Workflow/Skill 变化、重要失败或 Handoff 完成。

## Flow

```text
Memory Check
→ Event/Candidate
→ schema + secret + scope + dedup + destination validation
→ OFF: suppress
→ ASSISTED: Review Queue
→ AUTO: allowlist promotion / otherwise Review
→ Archive + index
→ Context refresh
→ Git commit / Handoff
```

## Checkpoints

- Source-side：没有 transcript、Secret、Raw 或敏感业务内容。
- Router：Public/private/local-only 目标明确；private alias 必须通过 Host-local Registry 的 classification/scope/sensitivity/source-project/writer gate，unknown fail closed。
- Provenance：所有 Git Candidate 的 host/project/actor/reference 稳定、可复查且不是占位值。
- Curator：没有 canonical overwrite；conflict 有 Review record；AUTO 的 target/Candidate/Archive/index 是同一事务。
- Git：单写入者、lock、非 main/master linked worktree、允许范围内的 clean status；identity/status 变化立即 rollback。
- Refresh：Manifest/Source Pack 只含批准的 public-safe sources，并明确 manual upload 状态。

## Failure handling

任何 writer、schema、provenance、secret、classification、conflict、Git isolation 或 permission 失败都不得丢弃事件或假装上传；写 sanitized local Outbox，或在 AUTO 事务中恢复执行前四资源状态。回滚失败写 recovery record 并阻断后续 AUTO。
