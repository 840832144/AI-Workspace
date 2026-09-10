# 飞书 CLI 与 Document Assistant 对比研究

- 日期：2026-09-07。
- 类型：Research note / Decision proposal；不是 RFC、ADR、canonical Task 或实施授权。
- 目标：为游戏策划团队判断 Document Capability 是否应采用官方 CLI，避免继续重复建设通用飞书接口。
- 范围：公开资料与当前实现代码对照。未安装 CLI、未登录租户、未修改已有文档、权限、Provider 或 EarlyMeeting。

## 结论

官方 CLI 的通用能力覆盖明显更广；针对本机 Agent 的文档发现、局部读取、局部编辑、媒体、Wiki、Sheets 和 Base，是值得优先验证的替代实现。实际操作成功率、耗时、复杂文档保真与公司租户可用性尚未实测，不能宣称已经全面优于当前服务。

建议采用官方 CLI 承担通用操作，保留一层团队专用的发布与登记规则。先并行试用，不立即删除 Document Assistant，不为复用官方 CLI 再建设一套大平台，也不直接 fork 官方仓库。

## 核验基线

| 对象 | 基线 | 说明 |
| --- | --- | --- |
| 官方 CLI | v1.0.93 / 2aebe8970f0a472dfc864b6ac3d19d080e75041f | 本次 GitHub latest release；published_at 为 2026-09-01 UTC。主要能力以该 tag 的 Skills / references 为依据，不混用搜索缓存中的旧版本。 |
| Document Assistant | main / e80fd8a7cb24edde876b492b9b575e2c092d06ab | 已读取 README、AGENTS、文档实现与 Registry 代码；包含多维表格能力。 |
| AI-Workspace | main / 1dd6de3e244858c44b716cacd72961ea9419f564 | 已读取 CAP-DOC、Task-0021、Status、Handoff、Memory、Product Roadmap 和协作规则；状态文档的历史现场检查不能作为本次在线健康检查。 |

公开 Git 连接器可读；容器直接访问 GitHub 时 DNS 失败。本次没有编译或运行官方 CLI，也没有验证用户设备、认证和目标租户。

## 源码与官方文档支持的差异

| 能力 | 当前 Document Assistant | 官方 CLI v1.0.93 | 判断 |
| --- | --- | --- | --- |
| 文档发现 | search_documents 依赖本地 Registry 的标题、项目与 ID；list_folder 浏览应用可见目录 | drive +search 对接 Search v2，可按资源类型、作者或时间等条件检索 | 官方方案能扩大受权限约束的发现范围；不是读取全公司所有文件。 |
| 内容读取 | getDocument 读取纯文本和简化 block；内部 fetchMarkdown 用于替换快照 | docs +fetch 支持目录、章节、区间、关键词，以及不同结构详细度、评论与资源引用信息 | 更适合大文档的局部读取。 |
| 内容修改 | 对外主要是追加与全文替换；replaceDocument 先删正文，失败后尝试恢复 Markdown 快照 | docs +update 提供 str_replace、block_replace、block_insert_after、block_delete、block_move_after 等 | 官方的局部编辑面更完整。两边的全文重写都不能当作无损操作。 |
| 图片、附件、画板 | README 明确图片能力不在当前范围 | doc Skill 有素材插入、预览、下载和画板流程 | 官方覆盖更广；具体素材的保真仍需样例验证。 |
| Wiki / Sheets / Slides | Wiki、Sheets 仍为预留，当前服务未提供对应完整工具 | 有 Wiki、Sheets、Slides Skills 与命令；Sheets 包括值、公式、样式、图表等 | 不建议继续从零增加同类通用接口。 |
| 多维表格 | 已有建表、字段、记录批量操作、视图和基础共享 | Base 覆盖记录、公式、视图、表单、仪表盘、Workflow、角色权限等 | 当前助手并非完全没有 Base，但官方范围明显更广。 |
| 身份与权限 | 当前使用应用身份、tenant token | 支持 user / bot 身份、OAuth、scope 检查与授权提示 | 灵活性更高；迁移必须明确操作者、资源权限及所有权。 |
| 团队发布规则 | CAP-DOC 与实现提供唯一导航中心、登记、回读、默认共享规则、失败时保留原文档 | 有通用权限与验证操作，但所查资料没有自动适配本项目导航中心与 Registry 的机制 | 保留或重写为薄 Workflow，不假定安装即可继承。 |

依据：下列 S1–S10。README 中的覆盖数是官方描述，不是本次逐命令实测统计；不引用“零配置”“三分钟”“成功率提升”等宣传作为本机验收。

## 哪些方面更好用

对拥有本机命令执行能力的 Agent，官方提供 Skills、命令帮助、schema、结构化成功/错误输出及部分写操作的 dry-run / 确认门禁。它不只是原始 API 的命令行转发。具体改善方向是少写接口封装、按需读文档、按 block 修改内容以及跨文档和表格取资料。[S1–S5]

这里的“更好用”是基于功能与交互设计的判断，不是实测速度或可靠性结论。它仍是工具，需要 Agent、凭据、权限和运行环境；不能因安装本机 CLI 就宣称网页客户端自动拥有调用通道。也不能把 CLI 当作后台托管服务或游戏报告推理引擎。

## 推荐边界

建议的组合：策划请求 → 已批准的 CAP-DOC / 团队发布 Workflow → 官方 CLI 通用文档操作；团队层继续管理来源、稳定文档关联、创建前查重、原位更新、权限回读及唯一导航中心登记。

普通读取可由 Agent 直接调用 CLI。正式发布必须经过项目 Workflow；是否继续保留现有 MCP 接口，只在需要兼容既有调用者时决定。官方 extension 提供凭据、传输、命令裁剪及审计扩展点，但本次不建议为了试用先构建 Go wrapper。[S11]

无需保留所有旧底层实现。验证通过的通用操作可以逐步退役，无法覆盖的组织规则仍保留；目标是减少维护面，不是永远维护两套同功能系统。CAP-DOC 契约本来就不绑定 MCP 或具体 Provider。[S10]

## 迁移前必须留意的限制

1. 只授权文档及必要的云空间能力，试用初期不请求邮箱、审批、聊天历史等无关权限。user 与 bot 的资源可见性、操作归属和 scope 不同，不在失败后静默切换身份。[S5]
2. 官方 Skills 是通用操作建议，不自动取代本项目的最小数据、Git 真相源、审批与强制回读规则。Base 文档的通用验证策略也不应降低项目正式发布标准。[S6、S10]
3. CLI 顶层 ok/退出码与内部操作结果都要检查；docs +update 还可能返回 partial_success / warnings，不能只看进程退出码就宣布完成。[S3、S5]
4. 官方发布迭代较快；v1.0.93 含移除旧 Sheets 命令面的变更。若纳入自动化，固定 CLI 与 Skills 的匹配版本，升级后验证用到的命令，不依赖 latest 静默改变。[S12]
5. 官方安全说明建议接入个人身份的通用助手不要放进多人群聊。本项目试用不复用晨会群机器人的群交互入口，也不扩大该应用权限。[S1]

## 建议下一步（未授权执行）

先做一次可回退的并行试用，不卸载当前助手。用一份脱敏测试文档完成“查找与局部读取 → 修改一个段落且保留原 ID 和非目标资源 → 按团队规则回读、授权与登记”，再选一张小型测试表验证当前最需要的 Sheets / Base 操作。

成功表现：目标内容、结构和权限符合要求，原链接不变，正式文档登记可用，失败不会重复创建。失败时保留当前 Provider，列明具体缺口，不扩大权限或批量重写历史文档。这里是建议的试用门槛，不是已执行测试或新 Task。

## Idea Handoff（待 Codex 按治理流程登记）

Idea title: CAP-DOC 官方飞书 CLI 复用与薄发布层
Suggested section: Ideas
Value: 扩大文档/表格能力，减少自研通用接口维护，同时保留团队发布和导航中心规则。
Source: 2026-09-07 User 对 larksuite/cli 的研究与比较请求。
Related object: CAP-DOC；Document Assistant；正式发布 Workflow。
Evidence / gate: 官方 v1.0.93 与当前实现已作资料/代码对照；采用、安装、授权和替换均未批准，需要最小场景实测。
Duplicate checked: yes（main Product Roadmap 未见等价条目，跨仓库 lark-cli 搜索无命中；检索非完整 Task 验证，正式登记前需重新防重）。

本记录不修改 Product Roadmap、正式 Task、Provider binding 或运行状态。Codex 是后续正式登记的默认 writer；未获实施授权不分配 Task、不安装、不扩大权限。

## 可复查来源

- S1：[官方 v1.0.93 README](https://github.com/larksuite/cli/blob/v1.0.93/README.zh.md)。
- S2：[文档读取](https://github.com/larksuite/cli/blob/v1.0.93/skills/lark-doc/references/lark-doc-fetch.md)。
- S3：[文档更新](https://github.com/larksuite/cli/blob/v1.0.93/skills/lark-doc/references/lark-doc-update.md)。
- S4：[云空间搜索](https://github.com/larksuite/cli/blob/v1.0.93/skills/lark-drive/references/lark-drive-search.md)。
- S5：[共享规则](https://github.com/larksuite/cli/blob/v1.0.93/skills/lark-shared/SKILL.md)与[身份权限](https://github.com/larksuite/cli/blob/v1.0.93/skills/lark-shared/references/lark-shared-identity-and-permissions.md)。
- S6：[Base](https://github.com/larksuite/cli/blob/v1.0.93/skills/lark-base/SKILL.md)。
- S7：[Sheets](https://github.com/larksuite/cli/blob/v1.0.93/skills/lark-sheets/SKILL.md)与[Doc Skill](https://github.com/larksuite/cli/blob/v1.0.93/skills/lark-doc/SKILL.md)。
- S8：[自研 README](https://github.com/840832144/document-assistant/blob/e80fd8a7cb24edde876b492b9b575e2c092d06ab/README.md)。
- S9：[自研文档实现](https://github.com/840832144/document-assistant/blob/e80fd8a7cb24edde876b492b9b575e2c092d06ab/src/feishu/docs.ts)与[Registry 实现](https://github.com/840832144/document-assistant/blob/e80fd8a7cb24edde876b492b9b575e2c092d06ab/src/registry.ts)。
- S10：[CAP-DOC](../../capabilities/document/README.md)。
- S11：[官方 extension](https://github.com/larksuite/cli/blob/v1.0.93/extension/README.md)。
- S12：[官方 v1.0.93 release](https://github.com/larksuite/cli/releases/tag/v1.0.93)。

## 本次文档验证与限制

本次只新增研究记录，不复制业务代码。已检查源链接结构、唯一标题、状态与未验证项、敏感标识/凭据赋值和 Markdown 空白；CAP-DOC 相对引用对应的文件已通过连接器回读。未运行全仓库 validator、未作租户健康检查，不能把文档检查作为产品实测。文档放在独立草稿分支，待 Review，不直接修改 main 或其他进行中分支。
