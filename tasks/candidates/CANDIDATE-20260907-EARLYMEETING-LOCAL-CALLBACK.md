# CANDIDATE-20260907-EARLYMEETING-LOCAL-CALLBACK — EarlyMeeting 本机长连接与真实卡片表单回调修复

- Kind: candidate
- Status: Migrated
- Project key: EARLYMEETING
- Suggested priority: P1
- User decision: Approved
- Source: https://github.com/840832144/EarlyMeeting/pull/3 ; User 2026-09-07 takeover instruction
- Created: 2026-09-07
- Updated: 2026-09-07
- Migrated to: TASK-0028 (`tasks/TASK-0028-EARLYMEETING.md`)
- Migrated at: 2026-09-07T07:03:50Z

## Goal

在 User 实际 Windows 测试目录定位 SDK_ERROR / UNCLASSIFIED，最小修复长连接并验证现有测试卡片真实表单回调；不保存、不更新公共卡片、不启用定时。

## Dependencies

EarlyMeeting docs/codex-callback-takeover@b18e393；本机受控凭据与现有测试卡片

## Risks

不得输出凭据、原始回调、完整日志；不得修改全局网络安全配置

## Promotion Gate

- Candidate 不是可执行入口，也不占用 `TASK-XXXX`。
- 只有 User 明确批准后，才可通过 allocator 完整校验并晋升。
- 晋升前必须检查相关 active Task、最新 `origin/main` 和分配锁。
