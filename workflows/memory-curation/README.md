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
- Router：Public/private/local-only 目标明确；unknown fail closed。
- Curator：没有 canonical overwrite；conflict 有 Review record。
- Git：单写入者、lock、branch/PR 隔离、可 rollback。
- Refresh：Manifest/Source Pack 只含批准的 public-safe sources，并明确 manual upload 状态。

## Failure handling

任何 writer、schema、secret、conflict 或 permission 失败都不得丢弃事件或假装上传；写 sanitized local Outbox，给出一次明确下一动作。
