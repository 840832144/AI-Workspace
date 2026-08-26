# Codex Handoff

这是 Codex 的固定交接入口。实现细节以对应外部项目仓库为准。

- Updated: 2026-08-26
- Task: TASK-0008
- Current state: Huuuge Project initialized; waiting for ChatGPT Review

## Objective

使用 AI-Workspace Project Template 接管 `huuuge-android-research` 的项目控制面，建立 Context、Memory、Workflow、Status，并梳理 Battle Pass、Slots、Lottery、Task/Missions 研究入口。

## Completed

- 安全同步 AI-Workspace 与 `huuuge-android-research`。
- 从 `projects/TEMPLATE/` 建立 `projects/huuuge-android-research/` 完整目录。
- 将外部 commit `0590c2c37a0aa83b824920fa884f9f67007d3dcb` 固定为当前证据基线。
- 建立四条研究入口及当前 evidence 状态：
  - Battle Pass：schema-only / live-pending。
  - Slots：live-confirmed；已有 broad Session 与 sanitized Spin example。
  - Lottery：cross-cutting/config evidence；缺少专用 endpoint sample。
  - Task/Missions：generic Missions schema-only；MiniPass task flow live-confirmed。
- 更新项目索引、README 和 CHANGELOG。

## Confirmed Context

- AI-Workspace 只拥有项目 Context、Memory、Workflow、Status 和交接。
- External `huuuge-android-research` owns code、tests、runtime evidence、engineering logs and sanitized generated artifacts.
- 本次没有修改外部研究仓库、Collector、SVN release、Feishu 文档或本机研究环境。
- TASK-0006 Collector Architecture Baseline 在外部仓库仍为 Waiting for ChatGPT Review。
- Skill categories 只是模型，不代表 Battle Pass/Slot/Lottery/Task Skill 已实现。

## Risks

- Workspace 状态可能与外部仓库漂移，必须以 commit permalink 和“external first”更新顺序控制。
- 四个模块 evidence 完整度不一致，不能横向当作同等成熟。
- GitHub private links 需要已授权会话；不得为方便访问而复制 private data。

## Constraints

- 不在 Review 前开始新采集、Extractor、报告实现或外部发布。
- 不在 AI-Workspace 复制源码、Raw/decoded values、账号/会话标识、APK、binary 或 credential。
- 任何研究执行继续遵守被动、安全、隔离研究环境和证据纪律。

## Exact Next Action

ChatGPT 审阅 `projects/huuuge-android-research/`，返回 Accepted 或对 Context、Memory、Workflow、Status 和四条研究入口的具体修订意见。Codex 等待 Review，不开始实现。
