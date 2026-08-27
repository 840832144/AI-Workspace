# TASK-0016 Automatic Memory Pilot

- Status: Completed / Waiting for ChatGPT Review
- Date: 2026-08-27
- Executor: Codex
- Environment: disposable linked worktree、disposable private Git repository 与 isolated Host state directory
- Production activation: disabled
- Final mode: `ASSISTED`
- Subagents: none

## Objective

验证 ChatGPT、Codex、Generic IDE Agent 三类 source-side adapter，以及 Public / approved Project Private / Local-only 路由、ASSISTED/AUTO/OFF、Secret、provenance、Review、Outbox、branch-safe transactional promotion 和 Context refresh。Pilot 不读取完整聊天、不访问真实私有业务仓库、不安装 hook、不修改 Global runtime。

## Scenarios

### 1. ChatGPT explicit decision

- Event：User 已授权隔离测试 AUTO，但 production 默认保持 ASSISTED，等待 ChatGPT Review。
- Route：`public/public`。
- Mode：ASSISTED。
- Confirmed result：Candidate captured 1；Curator routed to Review 1；没有 canonical overwrite。

### 2. Codex completed solution

- Event：使用 source-side structured event 与 transcript-free SessionEnd marker，不上传 rollout JSONL。
- Route：`public/public`。
- Mode：AUTO（non-main disposable linked worktree only）。
- Confirmed result：Candidate captured 1；新 Solution auto-promoted 1；原 Candidate archived 1；index 记录 provenance；目标此前不存在；public target/Candidate/Archive/index 同一事务完成。

### 3. Generic IDE approved private skill

- Event：可复用但属于 Project Private 的 Generic Agent procedure。
- Route：`project-private/internal`。
- Registry：Host-local alias `private-pilot`，classification=`project-private`，writer/scope/sensitivity/source-project 均显式批准，目标是 disposable private Git root。
- Confirmed result：private repository Candidate 1；public Inbox 写入 0；没有读取真实 Huuuge/CR 数据。

### Additional gates

- Read-only ChatGPT writer：`--force-outbox`，公共 Inbox 写入 0，Outbox 1。
- 未批准 private alias：private/public Inbox 写入 0，Outbox 1。
- 错误 repository classification：private/public Inbox 写入 0，Outbox 1。
- Secret scan：模拟 key 被识别为 `openai-key` category；Outbox 中 literal 不存在，公共 Inbox 写入 0。
- OFF：capture suppressed 1，Candidate/Outbox 均未新增。
- Context refresh：生成 Manifest、Source Pack 和 replacement list；`manual upload required=true`，私有仓库未读取。

## Metrics

Round 2 隔离 Pilot 命令墙钟时间：3.7 秒。该时间只代表本机 disposable Git/worktree 脚本运行，不代表人工 Review 或真实 Host 延迟。

| Metric | Actual |
| --- | ---: |
| captured | 3 |
| captured to approved private Git | 1 |
| promoted | 1 |
| review | 1 |
| local-only / Outbox | 4 |
| suppressed by OFF | 1 |
| conflicts | 0 |
| failed | 0 |
| required human review | 1 |
| Project Source manual upload | 1 |
| false captures | Not measured — requires User/ChatGPT review of live Host events |
| missed captures | Not measured — requires live Host observation |

没有根据八个 synthetic-but-realistic events 推断准确率、precision 或 recall。

## Regression Evidence

`python -m unittest discover -s tools/memory/tests -v`：34/34 passed。

覆盖：

- OFF / ASSISTED / AUTO；
- Public / Project Private / Cross-project Private / Local-only；
- approved private Git routing、未批准 writer、classification/sensitivity mismatch、禁止 private destination 回指 public repository；
- CLI、Event file、Generic Agent 三入口的 placeholder provenance Outbox gate；
- Secret redaction；
- schema/fingerprint tamper；
- pre-write destination traversal gate；
- deterministic duplicate；
- conflict；
- concurrent capture lock；
- existing canonical no-overwrite；
- AUTO main branch、primary checkout、unrelated dirty state fail-closed；
- target 写入后、Archive 前、Archive 后、index save、Git status change 五类 fault injection；每次 target/Candidate/Archive/index 恢复执行前状态，`promoted=0`，无 recovery record；
- non-main clean Candidate commit gate；
- writer unavailable Outbox；
- Manifest/Source Pack/manual upload。
- dirty repository 下请求 sync 时 fail-closed，不声称已是 latest。
- Windows PowerShell named-parameter capture wrapper。

Round 2 最终 AI-Workspace refresh：42 public control-plane sources、0 Secret issue、0 broken link、private repositories not read、manual upload required。TASK-0017 已由独立任务合并，本轮没有修改其网络脚本、分支或 Codex 配置。

## User Decision Applied

Execution Authorization 要求 AUTO 只做隔离验证，不静默成为生产默认。Pilot 结束后 Host-local mode 已恢复 ASSISTED；repository default 也是 ASSISTED。Global hook、`~/.codex/AGENTS.md` runtime replacement、Codex restart 和其他 Host activation 均未执行。

## Limits

- ChatGPT Project 没有在本任务中使用安全 API 自动替换 Sources；必须手动上传。
- 本 Pilot 没有真实 Trae lifecycle hook，只验证了 Generic Agent rule + CLI/Outbox contract。
- 本 Pilot 没有遍历 ChatGPT Project chats 或 Codex local memory；因此不能测量漏捕获率。
- 当前没有批准的真实业务 Private Registry 或 Cross-project Private Hub；实现与 disposable tests 已就绪，但 production writer 仍需 User/管理员逐仓库授权。
- Semantic dedup、graph retrieval 和 production scheduled curator 留给后续 User 决定。

## Reproduce

```powershell
python .\tools\memory\Run-MemoryPilot.py
python -m unittest discover -s .\tools\memory\tests -v
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\memory\Refresh-ProjectContext.ps1
```
