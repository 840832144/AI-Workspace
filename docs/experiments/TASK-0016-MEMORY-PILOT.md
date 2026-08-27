# TASK-0016 Automatic Memory Pilot

- Status: Completed / Waiting for ChatGPT Review
- Date: 2026-08-27
- Executor: Codex
- Environment: disposable Git-like repository and isolated Host state directory
- Production activation: disabled
- Final mode: `ASSISTED`
- Subagents: none

## Objective

验证 ChatGPT、Codex、Generic IDE Agent 三类 source-side adapter，以及 Public / Project Private / Local-only 路由、ASSISTED/AUTO/OFF、Secret、Review、Outbox、promotion 和 Context refresh。Pilot 不读取完整聊天、不访问私有业务仓库、不安装 hook、不修改 Global runtime。

## Scenarios

### 1. ChatGPT explicit decision

- Event：User 已授权隔离测试 AUTO，但 production 默认保持 ASSISTED，等待 ChatGPT Review。
- Route：`public/public`。
- Mode：ASSISTED。
- Confirmed result：Candidate captured 1；Curator routed to Review 1；没有 canonical overwrite。

### 2. Codex completed solution

- Event：使用 source-side structured event 与 transcript-free SessionEnd marker，不上传 rollout JSONL。
- Route：`public/public`。
- Mode：AUTO（disposable repository only）。
- Confirmed result：Candidate captured 1；新 Solution auto-promoted 1；原 Candidate archived 1；index 记录 provenance；目标此前不存在。

### 3. Generic IDE private skill

- Event：可复用但属于 Project Private 的 Generic Agent procedure。
- Route：`project-private/internal`。
- Confirmed result：公共 Inbox 写入 0；sanitized local Outbox 1。

### Additional gates

- Read-only ChatGPT writer：`--force-outbox`，公共 Inbox 写入 0，Outbox 1。
- Secret scan：模拟 key 被识别为 `openai-key` category；Outbox 中 literal 不存在，公共 Inbox 写入 0。
- OFF：capture suppressed 1，Candidate/Outbox 均未新增。
- Context refresh：生成 Manifest、Source Pack 和 replacement list；`manual upload required=true`，私有仓库未读取。

## Metrics

隔离 Pilot 命令墙钟时间：1.76 秒。该时间只代表本机脚本运行，不代表人工 Review 或真实 Host 延迟。

| Metric | Actual |
| --- | ---: |
| captured | 2 |
| promoted | 1 |
| review | 1 |
| local-only / Outbox | 3 |
| suppressed by OFF | 1 |
| conflicts | 0 |
| failed | 0 |
| required human review | 1 |
| Project Source manual upload | 1 |
| false captures | Not measured — requires User/ChatGPT review of live Host events |
| missed captures | Not measured — requires live Host observation |

没有根据六个 synthetic-but-realistic events 推断准确率、precision 或 recall。

## Regression Evidence

`python -m unittest discover -s tools/memory/tests -v`：16/16 passed。

覆盖：

- OFF / ASSISTED / AUTO；
- Public / Project Private / Cross-project Private / Local-only；
- Secret redaction；
- schema/fingerprint tamper；
- pre-write destination traversal gate；
- deterministic duplicate；
- conflict；
- concurrent capture lock；
- existing canonical rollback/no-overwrite；
- non-main clean Git commit gate；
- writer unavailable Outbox；
- Manifest/Source Pack/manual upload。
- dirty repository 下请求 sync 时 fail-closed，不声称已是 latest。
- Windows PowerShell named-parameter capture wrapper。

实际 AI-Workspace refresh：40 sources、0 Secret issue、0 broken link、private repositories not read。

## User Decision Applied

Execution Authorization 要求 AUTO 只做隔离验证，不静默成为生产默认。Pilot 结束后 Host-local mode 已恢复 ASSISTED；repository default 也是 ASSISTED。Global hook、`~/.codex/AGENTS.md` runtime replacement、Codex restart 和其他 Host activation 均未执行。

## Limits

- ChatGPT Project 没有在本任务中使用安全 API 自动替换 Sources；必须手动上传。
- 本 Pilot 没有真实 Trae lifecycle hook，只验证了 Generic Agent rule + CLI/Outbox contract。
- 本 Pilot 没有遍历 ChatGPT Project chats 或 Codex local memory；因此不能测量漏捕获率。
- Semantic dedup、graph retrieval、跨项目私有 Context Hub 和生产 scheduled curator 留给后续 User 决定。

## Reproduce

```powershell
python .\tools\memory\Run-MemoryPilot.py
python -m unittest discover -s .\tools\memory\tests -v
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\memory\Refresh-ProjectContext.ps1
```
