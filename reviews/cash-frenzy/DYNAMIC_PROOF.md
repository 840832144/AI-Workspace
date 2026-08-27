# TASK-0022 Dynamic Proof

- Status: **Blocked at User installation gate**
- Current level: F0 for dynamic path
- Target environment: independent `CashFrenzyResearch`

## Completed Preconditions

- package、sample version、split、ABI 与 engine 已完成 static audit。
- Host-local Cash Frenzy root 已创建，APK/static 文件与 Huuuge Session/Raw 隔离。
- Huuuge repository 已核对 clean；Huuuge Collector 未启动、停止、修改或复用。
- 当前运行实例确认为 `HuuugeResearch`，不会用于 TASK-0022 动态 proof。

## Pending User Actions

需要 User 在 BlueStacks Multi-instance Manager 创建全新 Pie 64-bit 实例、命名 `CashFrenzyResearch`，并从 Google Play 安装 Cash Frenzy。登录、验证码和商店操作由 User 完成。

安装完成后 Codex 将先做只读 preflight：instance name、ADB serial、package、version、ABI、foreground package 与隔离目录全部匹配，才允许进入 READY。1–5 次普通 Spin 将在后续单独提示，绝不自动购买或大量消耗资源。

