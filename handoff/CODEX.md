# Codex Handoff

这是 Codex 的固定交接入口。实现细节以对应外部项目仓库为准。

- Updated: 2026-08-26
- Task: TASK-0011
- Current state: First Run Guide and Feishu edition ready; independent planner validation required before completion

## Objective

以新策划视角建立由 Codex 或 Trae + DeepSeek 主导的 Huuuge First Run，使新人无需手工排查底层命令，并用真实独立策划盲测验证 Git + 飞书文档是否足以完成首跑。

## Completed

- 安全同步 AI-Workspace 与外部 `huuuge-android-research@0590c2c37a0aa83b824920fa884f9f67007d3dcb`，外部仓库保持只读。
- 新增 `projects/huuuge-android-research/FIRST_RUN_GUIDE.md`，覆盖：
  - 新电脑软件、权限与安全准备；
  - 必需/按需 Git repositories 与 Git/SVN 职责边界；
  - Codex、Trae + DeepSeek 两种 AI 入口和统一首跑提示词；
  - 环境预检、正式 SVN 包安装、独立实例、READY、normal play、clean stop/finalize；
  - 脱敏中文 Markdown 生成；
  - AI Document Assistant 创建/更新/回读；
  - 成功标准和常见问题。
- 新增 `REPORTS/TASK-0011-FIRST-RUN-VALIDATION.md`，只允许填写真实测试者、卡点、耗时、AI 引导结果和文档修订。
- 创建飞书文档《Huuuge 新人上手指南（First Run Guide）》：
  - URL：`https://gfok27asqq.feishu.cn/docx/Ffibd2Cx2oXFgfxdKnJcE6uUnZf`；
  - create/replace 无 conversion warning；
  - `get_document` 回读标题和正文成功；
  - `grant_company_edit` 回读 `link_share_entity=tenant_editable`、`verified=true`。
- 将长期文档规则写入 AGENTS、CONTRIBUTING 和 Standards：
  - 面向策划/用户的文档默认中文；
  - 新生成云文档默认企业内可编辑，除非 User 明确要求其他权限。
- 更新项目 README、Memory、Status、Reports Index、CHANGELOG 和 ChatGPT Handoff。

## Confirmed Context

- Git 工程/知识源与 SVN 策划运行包不能混用：正式运行目录仍是 `C:\HuuugeCollector`，Git clone 不替代 SVN package。
- 新人只处理首次认证、验证码、游戏登录、机器级修改审批和正常游戏操作；AI 默认完成其余可执行步骤。
- 当前飞书 MCP 健康检查通过；文档已写入、回读且公司编辑权限已确认。
- 本次没有修改采集器、外部研究仓库、SVN、BlueStacks、运行环境或任何业务功能。
- 独立策划盲测尚未发生；耗时、卡点和 AI 独立引导结果不能推断或模拟。

## Validation Performed

- AI-Workspace、Huuuge、Document Assistant 与 non-secret mirror Git 工作树在开始时均为 clean/up-to-date。
- 飞书 `feishu_healthcheck`：environment present、token ok、API connectivity ok、Drive permission probe ok。
- 同名文档搜索结果为空后才 create；更新使用 replace，没有重复创建。
- `get_document` 确认标题、中文正文、云文档权限规则和独立盲测章节存在。
- 新版 STDIO MCP 单次调用 `grant_company_edit` 成功并回读权限。

## Failed Attempts

- 第一次权限验证通过 `pnpm` 启动时，当前 shell 的 PATH 没有 Node.js；没有产生外部修改。
- 第二次使用多行 `tsx -e` 时参数被截断，编译失败；没有产生外部修改。
- 改为直接使用 Codex bundled Node 运行已提交的 MCP Server 后，权限设置与回读成功。

## Blocker

尚未指定一位未参与开发的策划执行盲测。Codex 不能冒充真实新人，也不能虚构操作耗时或卡点，因此 TASK-0011 目前不能标记完成、不能发布正式 0.7.0、不能进入最终 ChatGPT Review。

## Exact Test Package

只提供以下两项，不提供其他口头说明：

1. Git：`https://github.com/840832144/AI-Workspace.git`
2. 飞书：`https://gfok27asqq.feishu.cn/docx/Ffibd2Cx2oXFgfxdKnJcE6uUnZf`

## Exact Next Action

User 指定一位未参与开发的策划并发送上述两项。测试过程中只记录，不补充说明。测试结束后把真实记录写入 `REPORTS/TASK-0011-FIRST-RUN-VALIDATION.md`；Codex 只根据发现修改文档和流程，更新 CHANGELOG/Handoff，提交正式完成版本，再等待 ChatGPT Review。
