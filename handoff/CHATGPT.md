# ChatGPT Handoff

这是 ChatGPT 的固定交接入口。长期事实必须同步到 Capability contract、项目 Memory / Status、Task、RFC、ADR 或正式 Review，而不是只留在聊天中。

- Updated: 2026-08-27
- New User-authorized task: `TASK-0021-Workspace-Live-Context-Hub.md`
- TASK-0021 status: `Ready`
- Project key: `WORKSPACE`
- Human alias: `WORKSPACE-LIVE-CONTEXT-001`
- Execution rule: 并行任务使用独立 branch / linked worktree；不得覆盖其他任务或未提交修改

## Allocation and Current Queue

创建 TASK-0021 前已从 Git 最新 `main@6610feff2acbb48e9058b237c3a12332394b7221` 完整枚举 `tasks/` 根目录；`TASK-0021` 未被占用，创建后复验为唯一 canonical 文件。

当前相关任务：

- `TASK-0016-Automatic-Cross-Conversation-Memory-Curation.md`：`Review`，安全加固继续在独立 worktree 处理；
- `TASK-0018-Huuuge-Lottery-Numerical-Breakdown-Report.md`：Huuuge Lottery 数值报告主线，范围不变；
- `TASK-0019-AI-Workspace-Overview-and-Separate-Progress-Documents.md`：`Ready`，其两份源稿将成为 Live Context 的重要输入；
- `TASK-0020-Task-Allocation-and-Namespace-Governance.md`：`Ready`，负责 Task Registry、allocator 和历史冲突治理；
- `TASK-0021-Workspace-Live-Context-Hub.md`：`Ready`，负责实时 Context、飞书协作、Workspace Sync 和行文规范。

历史 TASK-0018 编号冲突继续由 TASK-0020 处理。执行任何 0018 时必须使用完整文件名，不能只写编号。

## TASK-0021 Objective

解决 ChatGPT Project Sources 需要手工下载、编辑、重新上传，以及多个会话 / Agent 并行时上下文不能及时同步的问题。

目标链路：

```text
稳定 Bootstrap / Project Instructions / AGENTS
                    ↓
              Workspace Sync
                    ↓
       最新 Context Manifest 与相关文档
          ├─ Git canonical truth
          ├─ 飞书协作与展示层
          └─ Host-specific local context pack
                    ↓
       ChatGPT / Codex / Trae / 策划共同工作
```

核心要求：

1. 优先验证并采用飞书知识库；Wiki 条件不满足时使用专用飞书 Drive 文件夹 + Docx，不能回退到手工搬运 Markdown。
2. Git 继续是 Task、ADR、Capability、规则和实现状态的 canonical truth；飞书提供多人协作、在线编辑和面向人的入口。
3. Git-authoritative 内容只向飞书发布；飞书协作草稿进入 Memory Candidate / Review，不静默覆盖 Git。
4. ChatGPT 直接 Feishu MCP 暂不可用时，通过自动 Git mirror 获取最新 Context，不能把 Project Sources 当实时状态源。
5. 建立 `standards/PLANNER_WRITING_STYLE.md`，禁止单词 / 短句逐行排版，统一正常中文段落、结论—依据—下一步和策划步骤写法。
6. 为 ChatGPT、Codex、Trae / DeepSeek 提供各自的 Workspace Sync Binding；无法同步时明确显示 stale / unavailable。
7. 支持 OFF / ON_DEMAND / WATCH，Pilot 后默认 ON_DEMAND；未经 User 批准不得生产启用 WATCH。

## Confirmed Baseline

- ChatGPT Project Sources 是快照，动态状态当前仍需手工替换；
- AI Document Assistant 已支持飞书 Docx、Drive、搜索、创建、替换和权限管理；Wiki 工具目前只在架构中预留，尚未实现；
- ChatGPT 直接 Secure MCP Tunnel 目前受 OpenAI Control Plane 地区限制，Codex 本地 `feishu-docs` 正常；
- TASK-0016 已提供 Git-backed Memory Candidate、Review、Public / Private / Local-only 路由，可作为 Feishu 草稿入 Git 的基础；
- TASK-0019 将生成项目全景说明和项目进度文档，可由 TASK-0021 纳入 Live Context，但不得复制或覆盖其正在执行的工作。

## Shared Boundaries

- TASK-0021 必须先完成 Reuse-first Feasibility Audit，再决定 Feishu Wiki、Drive Folder 或其他 fallback；
- AI-Workspace 与 document-assistant 分别使用独立 branch / linked worktree；发现活动任务重叠时停止并报告；
- 不修改 Huuuge Collector、Lottery 报告数据、Capture、SVN、游戏请求、奖励、余额或服务器状态；
- 不把 Secret、Raw Capture、账号、完整响应、逐笔余额、Feishu token、document token、private URL 或本机 Registry 写入公共 Git、飞书正文或日志；
- 不把飞书设为代码、Task、ADR 或运行证据的唯一真相源；
- 不静默部署公网服务、付费 SaaS、GitHub Secret、管理员权限或生产 WATCH；
- 不自动合并冲突，不直接覆盖 `main`，不声称 Project Sources 已自动更新。

## Exact Next Action

Codex 执行 `TASK-0021-Workspace-Live-Context-Hub.md`：

1. 同步最新 AI-Workspace 与 document-assistant，完整读取 Task、Handoff、TASK-0016、0019、0020 和活动工作区；
2. 建立独立 linked worktree / branch，先做 Feishu Wiki / Drive / fallback Feasibility Audit；
3. 按 Task 实施行文规范、Context Capability、Workspace Sync、Feishu Hub 和三类 Host Pilot；
4. 若需要 User 新建知识空间、发布飞书权限或批准外部资源，只给一次性操作清单并停在可继续状态；
5. 完成后更新两个仓库的 CHANGELOG / Handoff，把 TASK-0021 设为 Review，推送独立 branch，返回 commit / PR、飞书安全链接和验证结果；
6. 等待 ChatGPT Review，不自动合并或启用 WATCH。
