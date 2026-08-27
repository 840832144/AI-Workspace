# Codex Handoff

- Updated: 2026-08-27
- Current task: TASK-0022 — Cash Frenzy Android Collector Feasibility Audit
- Status: Ready — issuance pending merge to main and allocator finalize
- Branch: `codex/cash-frenzy-feasibility-issuance`
- Initial base: `origin/main@ac6d3edc6168c486f5c82f1f272dd4047de7dc4e`
- Latest-main merge: `569f504` includes `origin/main@7eb16b0`
- Workspace Sync: `ON_DEMAND`
- WATCH: disabled
- Memory mode: `ASSISTED`
- Subagents: none

## Closed TASK-0021

- ChatGPT Review Round 1：Accepted。
- AI-Workspace merge commit：`ac6d3edc6168c486f5c82f1f272dd4047de7dc4e`，已推送 main。
- Document Assistant PR #1：MERGED；merge commit `3a959a7e801def913cd5c8a3d78e3f8da9093ca8`。
- TASK-0021、ADR-0007 和正式 Review 已进入 main；最终模式保持 `ON_DEMAND`，未启用 WATCH。

## TASK-0021 Phase 2 — 文档导航中心

- 第一阶段 Accepted 状态已从最新 main 确认；本阶段沿用 TASK-0021，不创建新 Task，当前状态为 Review。
- 唯一《AI Workspace｜文档导航中心》已建立并真实回读，登记 14 份正式文档；八分类、链接唯一和企业内可编辑权限验证通过。
- 正式测试文档已完成“创建、文档回读、自动登记、Hub 回读”，随后删除并确认 Hub 恢复为 14 条。
- Document Assistant 新增 `register_document` 和正式创建治理；AI-Workspace 已更新 Core Rules、Project Instructions、两级 AGENTS、Document Capability、Document Assistant Workflow 与 Workspace Sync Workflow。
- Git 不保存 Hub 独立 ID、token、私有 Registry 或敏感返回值；安全链接仅通过当前交付消息返回。
- 当前运行中的 Codex MCP 仍是已合并版本；新 tool 需在 Review 通过、实现分支合并并重启 MCP 会话后正式载入。
- Workspace Sync：`ON_DEMAND`；WATCH disabled；ChatGPT 设置未修改；Subagents: none。
- 下一步：ChatGPT Review 本阶段两个分支；Accepted 后合并，并在新 Codex 会话确认 `register_document` 出现在工具清单。

## TASK-0021 Final UX Closeout

- ChatGPT Review 2 的主体实现已通过；中文标题和项目全景入口两项收尾已完成，TASK-0021 最终状态为 Accepted。
- 唯一入口已在同一 URL 原位更名为《AI Workspace｜文档导航中心》，保留 14 条正式文档、八分类、链接唯一和企业内可编辑权限。
- `Game Planner AI Workspace｜项目全景说明` 已原位增加“📚 下一步推荐阅读”，其后新增“🗺 项目工作流总览”；章节位置、导航链接、飞书原生白板图和权限均已回读。
- `docs/overview/AI_WORKSPACE_PROJECT_OVERVIEW.md` 已从 TASK-0019 历史分支恢复为 Git 源稿；公共 Git 不保存租户文档 URL，发布时由 Document Assistant 绑定唯一链接。
- “核心规则”“实时 Context Hub”和“当前状态与任务入口”已原位同步最新 Git 源稿，并逐份完成正文回读、自动登记和导航中心回读。
- Documentation Governance 最终流程：`create_document → 文档回读 → register_document → 文档导航中心回读 → Success`。导航失败时不删除已创建文档、不重复创建，返回失败并等待修复。
- 新增 Proposed RFC-0004，记录“一套 Research Environment、多游戏、Evidence 独立”的长期方向；没有修改当前 Cash Frenzy Candidate、TASK-0022 或执行环境。
- Document Assistant：12 个 test files / 36 tests，真实创建—登记—删除—恢复烟测通过；Workspace：Task 23/23、Context 13/13、Memory 35/35、Doctor 通过。
- 最终模式：`ON_DEMAND`；WATCH disabled；ChatGPT 设置未修改；Subagents: none。
- Merge commits：待本分支与 Document Assistant 分支按 Review 2 要求合入 main 后，在 closeout commit 中回填。

## TASK-0022 Allocation

User 已明确批准 `tasks/candidates/CANDIDATE-20260827-CASH-FRENZY-COLLECTOR-FEASIBILITY.md`。在包含 latest `origin/main` 的独立 linked worktree 中执行正式：

```text
python tools/tasks/task_cli.py promote tasks/candidates/CANDIDATE-20260827-CASH-FRENZY-COLLECTOR-FEASIBILITY.md
```

allocator 实际分配 `TASK-0022`，没有猜号或手工编辑 Registry。Candidate 现为 Migrated；canonical 文件为 `tasks/TASK-0022-CASH-FRENZY-ANDROID-COLLECTOR-FEASIBILITY-AUDIT.md`。Remote reservation `refs/heads/task-reservations/TASK-0022` 保持 `pending-main`；token 只留 Host-local allocator state，不进入 Git 或 Handoff。

正式 Registry validate 已通过：9 canonical、2 companion、1 个已 Migrated Candidate record、6 Review、0 collision；当前待决 Candidate 为 0。

## Execution Boundary

Task issuance 合入 main 并完成 `finalize` 后，必须从最新 main 新建独立执行 linked worktree。先完成 Reuse-first、package/version/ABI/engine、APK/split、protocol 和 static resource audit，再建立独立 `CashFrenzyResearch` 环境。

- 不修改或复用 `HuuugeResearch`。
- Cash Frenzy Session / Raw / APK / SO / 完整响应 / 账号数据只留本机，不与 Huuuge 混用。
- 不自动付费，不替 User 消耗大量资源，不伪造或重放请求。
- 需要安装、登录、验证码或 1–5 次普通 Spin 时，停下并只给 User 明确界面操作顺序。
- 当前会话为宽松文件权限，按 Subagent 安全规则保持 OFF；主 Agent 单独执行并唯一写入。

`origin/main@7eb16b0` 增加的“共用 Research 模拟器”历史说明与本轮直接指令冲突，现已在 Candidate 中保留审计引用并明确标记为 superseded；当前有效决定是独立 `CashFrenzyResearch`。





<!-- MEMORY-REFRESH:START -->
## Memory Context Refresh

- Generated: 2026-08-27T10:36:02Z
- Effective mode: `ASSISTED`
- Manifest: `CONTEXT_MANIFEST.yaml`
- ChatGPT Project Sources: `manual upload required`
- Private repositories: not read unless explicitly registered and authorized
<!-- MEMORY-REFRESH:END -->
## Exact Next Action

提交并合并 TASK-0022 issuance 到 main；在原 issuance linked worktree 同步 latest main 后执行 `task_cli.py finalize`，然后建立独立 execution linked worktree继续 TASK-0022。
