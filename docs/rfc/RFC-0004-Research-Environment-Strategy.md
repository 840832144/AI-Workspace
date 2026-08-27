# RFC-0004: Research Environment Strategy

- Status: Proposed
- Date: 2026-08-27
- Actors: User, ChatGPT, Codex

## Summary

提出长期 Research Environment 规范：`One Research Environment → Multiple Games → Independent Evidence`。多个游戏可以共享同一个 Research 模拟器及底层运行能力，但每个游戏的研究证据必须严格隔离。

本 RFC 只记录后续方向，不修改当前 Cash Frenzy Candidate、TASK-0022 或正在执行的环境决定。

## Motivation

每个游戏都建立完整独立模拟器会重复维护 Root、Frida、ADB、证书、运行依赖和基础诊断；完全共用数据目录又会导致 Session、Raw 与 Evidence 串线。需要把“运行环境复用”和“业务证据隔离”拆开治理。

## Goals

- 多个游戏可安装在同一个 Research 模拟器。
- Root、Frida、Runtime 和基础诊断能力可以共用。
- Session、Capture、Manifest、Raw 与 Evidence 必须按游戏建立独立命名空间和目录。
- 任意时刻只允许一个游戏进入 Capture，避免网络流量、前台状态和证据归属混杂。
- Collector Start 必须验证前台包名与目标游戏完全一致；不一致时拒绝进入 `READY`。

## Non-goals

- 本 RFC 不立即修改 Collector、模拟器、Capture 脚本或业务仓库。
- 本 RFC 不改变当前 Cash Frenzy Candidate、TASK-0022 的独立环境要求。
- 本 RFC 不定义多游戏并行采集，也不允许跨游戏复用 Raw、账号数据或 Evidence。

## Proposal

### 1. Shared Research Runtime

一个受控 Research 模拟器可以安装多个已批准游戏，并复用 Root、Frida Server、ADB 连接、Runtime 依赖和基础健康检查。共享只发生在运行基础设施层，不代表游戏数据共享。

### 2. Game Isolation Boundary

每个游戏必须使用稳定 `game_key`，并将以下对象隔离：

```text
research/<game_key>/
├── sessions/
├── captures/
├── manifests/
├── raw/
└── evidence/
```

任何导出、报告或 Handoff 必须携带 `game_key`、目标包名、Session 与 Capture 引用。Collector 不得扫描其他游戏目录作为当前证据。

### 3. Single Active Capture

Research Environment 维护一个全局 Capture 锁。开始 Capture 前必须确认没有其他游戏处于 `STARTING`、`READY`、`CAPTURING` 或 `FINALIZING`；发现活动锁时 fail closed，不抢占、不合并流量。

### 4. Foreground Package Gate

Collector Start 在输出 `READY` 前读取当前前台包名，并与目标游戏 manifest 中声明的包名做精确匹配：

```text
target package == foreground package
    → 可以继续完成探针检查并进入 READY

target package != foreground package
    → 拒绝 READY，提示切换到目标游戏后重新检查
```

运行期间前台包名变化时应记录边界事件；是否自动暂停由后续实现 Task 决定，不能在本 RFC 阶段假定。

## Alternatives

- 每游戏独立模拟器：隔离最直观，但基础设施重复、维护成本高；当前任务继续按既有决定执行，不由本 RFC 回溯修改。
- 多游戏同时 Capture：吞吐更高，但证据归属和前台状态难以证明，当前提案拒绝。
- 只按文件名区分：不足以阻止目录、锁、Manifest 或运行证据串线，拒绝。

## Risks and Security

- 游戏更新、反调试或 Runtime 差异可能破坏共享环境，需要保留升级前快照与逐游戏兼容性记录。
- 账号、Raw、完整响应和私有 Evidence 继续留在对应受控项目路径，不进入 AI-Workspace。
- 前台包名只能证明当前界面归属，不能单独证明网络流量完整归属；仍需 Session、Capture 锁和 Manifest 共同验收。

## Validation / Acceptance Criteria

后续实现 Task 至少验证：两个游戏可安装且基础 Runtime 可复用；目录和 Manifest 不串线；并发 Capture 被拒绝；前台包名不匹配时不能出现 `READY`；切换到正确游戏后可以重新检查；停止与 Finalize 后锁被可靠释放。

## Open Questions

- 全局 Capture 锁由 Collector、Supervisor 还是 Host service 持有？
- 游戏切到后台时采用暂停、终止还是仅记录边界事件？
- 哪些 Runtime 差异需要自动升级为独立 Research Environment？
