# 飞书官方 CLI｜文档能力并行接入交接

## 2026-09-09 Codex 接管记录

- 正式入口：[TASK-0029](../../tasks/TASK-0029-LARK-CLI-DOCUMENT-PARALLEL-PILOT.md)，由 remote-CAS allocator 分配；状态 In Progress，非猜号，reservation 保持 pending-main。
- Task 登记前 Registry 13 canonical / 0 collision / valid；已核对全部远端 heads，未见同目标任务。
- 两仓库均使用独立 `codex/lark-cli-document-pilot` 分支；document-assistant 原 checkout 的未提交图片改动保持原状。
- CLI 安装已完成：1.0.94；三个 Skills 同 tag / commit，Codex skills/list 三项 repo / enabled / 0 error，本轮会话已自动加载。真实文档试用尚未开始。
- User 暂停讨论后已明确恢复 TASK-0029：新建当前企业的独立企业自建应用，建议名称「AI Workspace CLI（试用）」，初期可用范围仅 User 本人；不改旧文档助手或晨会应用。
- 先核对向导默认权限，仅文档与必要认证 scopes；使用独立 CLI 配置和凭据存储，官方链接与二维码交 User 浏览器确认；遇额外权限/管理员审批先说明，不自动扩大。
- User 已浏览器确认创建新应用，CLI 初始化完成，隔离凭据为 keychain 引用；未完成用户登录或写入临时文档。旧 feishu-docs 配置和环境变量未改。
- 实际 userScopes 查询仅 offline_access；CLI 不以此证明 bot scopes 或可用范围。页面读取 timeout / Debugger unattached；仅本人可用和建议名称尚需后台确认。
- 实施说明和当前证据：document-assistant `docs/LARK_CLI_PILOT.md`，commit `cf8b9414a9feac547c2f7c94a14f80bff847107a`；secret scan 通过。
- 用户登录续跑已验证为 user / ready / token valid。实际 90 项权限由 User 明确说明为自己一键开启全部免审项；不自行撤销，实际操作范围仍为文档样例。
- 标题查重实际返回 missing_scope，尚未创建文档。User 随后选择一次补齐文档/云空间全部权限，含需审核项，不选择 CLI 全业务域；官方目录 docs / drive 共 40 个唯一 scope，加认证 offline_access。相对现有权限仅缺 search:docs:read 和 space:document:retrieve。
- User 在后台手动添加权限，回读 app userScopes=172、列表权限已开启、v2 search:docs:read 仍缺，旧搜索 drive:drive.search:readonly 已有；用户 token 仍 90 项。因此改用已开启权限集合的 OAuth，并以 drive.files.list 精确标题匹配完成本次查重/查找；不扩大后台范围，不把 v2 快捷搜索报告为通过。
- 唯一下一步：点击新的用户授权链接完成 OAuth（不必扫码），Codex 完成登录并核验列表权限后继续同一文档。旧补授权流程均不再使用，虚构 XML 草稿已通过本机 parse。
- Idea 防重：唯一 Roadmap 暂无同义条目。沿用本交接末尾同一 Idea，最小试用可归 Current；本轮 User 禁止修改正式文档/Hub，因此正式 Roadmap 发布保持待处理，不宣称已完成登记，不扩大授权。
- Subagents: none。

以下保留 ChatGPT 原始授权交接作为范围依据。

- 日期：2026-09-09。
- User decision：Approved；User 已同意并行试用，并要求说明 Codex 如何开始接入。
- 类型：实施准备交接；不是已分配编号的 canonical Task，不代表已经安装或切换 Provider。
- Owner：User / ChatGPT。Executor：Codex（目标本机，尚待接管）。
- Capability：CAP-DOC 的 DISCOVER / READ / CREATE / UPDATE；共享权限按最小需要处理。
- 关联研究：[飞书 CLI 与 Document Assistant 对比](LARK_CLI_DOCUMENT_CAPABILITY_ASSESSMENT.md)。
- 治理仓库：AI-Workspace。实施说明、必要的薄 Workflow 和脱敏运行证据：document-assistant 的独立分支。第三方程序、凭据和运行状态只保存在受控 Host，不复制到治理仓库。

## 1. 本轮目标与授权边界

让当前 Windows 本机的 Codex 能发现官方文档 Skills，直接执行官方 lark-cli，以 User 明确授权的身份完成一份虚构临时文档的创建、查找、局部读取、局部修改和回读。现有 feishu-docs MCP 与 Document Assistant 保留，不卸载、不停止、不批量迁移正式文档；不修改 EarlyMeeting 或恢复晨会功能开发。

本轮是并行试用，不是全面采用。可以完成隔离安装和临时样例操作；应用新建或复用、浏览器 OAuth、企业权限审批由 User 在实际授权页面确认。禁止借本轮试用开通邮箱、审批、群聊或通讯录等无关权限。遇到额外依赖、费用、系统安全修改或生产文档写入需求时，先报告并等待单独批准。

不创建新 MCP Server、不购买服务器、不配置回调/Webhook、不 fork 官方 CLI，不把它做成群聊通用助手。此次只接 Docs 与必要 Drive；Sheets、Base、Wiki 等下一轮再确认。

## 2. 当前核验基线

| 对象 | 已查询的基线 | 不能据此宣称的内容 |
| --- | --- | --- |
| 官方 CLI | GitHub latest release 为 v1.0.94，发布于 2026-09-07 UTC，target commit f065bf5b645af381f9b7475ce721451e6ca36a23 | 未在目标本机安装或认证；上一研究的 v1.0.93 是历史比较基线，不再称当前最新版本 |
| Document Assistant | main@e80fd8a7cb24edde876b492b9b575e2c092d06ab；当前分支清单已读取 | 代码存在不代表本次 Host 健康检查通过 |
| AI-Workspace | main@1dd6de3e244858c44b716cacd72961ea9419f564；Task Registry、Status、Handoff 及分支已读取 | 旧 Status 的现场结果不是当前运行状态；仅查询 Registry 不等于运行 validator |
| 研究入口 | 本分支 / PR #3；原研究提交 8c720a87e612e4eb8b13724cd2f23b51878ec46e | PR 仍为草稿，未合入 main；没有 CLI 正式 Task 已开始执行的证据 |

本次跨两仓库的默认分支 lark-cli 搜索没有返回结果，但本研究在非 main 分支已存在，因此搜索空结果不能当作完整防重结论。ChatGPT 容器直接 clone 最新 AI-Workspace 因 GitHub DNS 失败，未运行 Registry validator 或 remote allocator；不创建、预留或猜测任务编号。

## 3. Codex 的第一步：正式准备，不重做研究

安全 fetch 两仓库，保护本机未提交修改；读取 Global/Project AGENTS、CAP-DOC、最新 Task、Status、Handoff、本交接和已有研究。枚举远端活动任务，运行 Task Registry scan / validate，核对同目标工作和合法 project_key。已有同目标 active Task 时按治理规则继续；没有时在独立非 main linked worktree 用 remote-CAS allocator 完成正式登记，将本交接纳入 Task 的完整范围、验收和安全约束。

正式 Task 进入有效执行状态后，按本轮授权进行安装与试用。不能因前一研究写着“未授权执行”就忽略本次已批准的有限试用，也不能因本交接存在就跳过 Task Gate。不得把试用加入 EarlyMeeting TASK-0028。遇到冲突、Registry 漂移或锁问题，先停止实施并给出具体阻塞。

成功表现：有唯一正式任务与独立实施入口，旧文档助手的配置和调用入口保留。失败时只解决准备阻塞，不另猜编号或覆盖活动分支。

## 4. 接入顺序

### A. 安装官方 CLI 和匹配的文档 Skills

先检查当前本机是否已有 lark-cli、Node/npm、官方 Skills 或等价工具；存在时核对版本和来源，不重复覆盖。以本次核验的 v1.0.94 为试用候选，记录最终选定 tag、二进制版本及 Skills 对应提交。使用官方 npm 安装器或该版本官方 Release；执行前读取该版本安装说明及实际 --help。不能以“npx 包版本固定”推定安装器后续下载也固定；必须回验最终版本。安装器不能可靠固定版本或会覆盖已有配置时，使用可核验的官方发布资产与 checksums，或停下报告。

仅向当前试用范围暴露 lark-shared、lark-doc、lark-drive 及其实际必需参考文件。Skills 与 CLI 取同一 tag，不混用 main 最新说明。使用目标 Codex 支持的 Skill 安装/发现方式，保留原有 Skills；相对 reference 文件必须完整。官方资料当前说明 Codex 会读取仓库内 .agents/skills，并支持用户级 ~/.agents/skills；本轮优先项目范围，跨项目默认启用另行 Review。不要把第三方完整源码或运行时路径登记进 AI-Workspace。

成功表现：Codex 自己执行版本与帮助检查成功，并能在本试用会话发现和读取三个 Skill。终端可运行但 Agent 找不到 Skill不算完整接入；先核对扫描位置、必要时重启会话，不重建 MCP。

### B. 隔离配置并由 User 完成授权

先明确接入中国飞书还是 Lark，并核对当前已有 CLI 配置；不覆盖旧登录或现有文档助手环境变量。可复用获准的文档应用时走隔离配置并验证权限；不默认复用晨会机器人。需要新建试用应用时，先说明用途，由 User 通过官方配置流程确认，不擅自把 --new 当作无副作用命令。

官方配置入口为 lark-cli config init；面向 Agent 的新应用引导为 lark-cli config init --new。执行前以所选版本 reference / --help 核对。User 不需要把 App Secret 粘贴到聊天；凭据由官方受保护的本机存储或批准的受控输入处理，不写 Git、AGENTS 或日志。

本次文档试用默认显式 --as user；bot 身份仅在用途和授权均明确时单独验证。先依据命令 schema / scope 信息列出必要的文档与云空间权限，优先精确 --scope；不要照抄 --recommend 或 --domain all。Docs/Drive 业务域不是单份测试文档的权限隔离，若同意页权限覆盖更广，必须让 User 看清实际范围。

按官方 split-flow 发起 OAuth：使用带 --no-wait --json 的 auth login，给 User 展示真实授权链接和官方 auth qrcode 生成的二维码；交还控制权，等 User 完成后再由 Codex 用本次 device_code 完成登录。不要复用过期链接，不把链接/二维码/device_code 存进 Git，不静默轮询到用户根本看不到授权入口。

成功表现：在本机验证登录态、身份、token 有效及必要 scopes，仅输出脱敏摘要。官方参考命令为 lark-cli auth status --json --verify。权限失败时只补目标操作必需项，不静默切 bot/user，不反复新建应用。管理员审批与新的外部授权仍由 User 完成。

### C. 一份临时文档完成最小真实验证

仅使用虚构内容和显式 temporary 标识，在获准位置创建一份临时测试文档；按 CAP-DOC 默认共享规则处理并回读，若组织策略不允许，保留文档、报告权限失败，不创建副本。临时样例不登记成正式成果，不污染唯一导航中心。

验证：创建后保存稳定关联；按测试标题查找；读取目录或某一节；只替换目标段落；再次读取，确认目标内容已变、原 document ID/链接不变、非目标内容未被改动。可在同一文档追加一句再回读，不做压测或批量迁移。搜索尚未命中但创建已成功时保留原 ID，不能再创建一份。

优先官方 docs +fetch / docs +update 的局部命令；只在所选操作支持时用 --dry-run。检查顶层 ok、退出码以及 data.result / warnings，partial_success 不算完成；每次改后使用最新 block ID。高风险确认门禁不得静默添加 --yes 绕过。保存未知结果时先查询原资源，不盲重试。不要把正式报告拿来做破坏性验证；清理临时文档涉及删除时按门禁另行确认。

成功表现：User 用自然语言要求修改一句，Codex 能选中官方 Skill 并完成上述原位修改。失败时保留原样例和旧 Provider，给出真实缺口；不可用扩大权限或整篇覆盖来掩盖局部修改失败。

### D. 留下可复用入口，但不切换生产默认

试用通过后，在 document-assistant 独立分支沉淀短使用说明、版本锁定信息、薄 Workflow 和回退步骤；AI-Workspace 只保存 Task、评审、CAP-DOC 关系及状态引用。试用范围之外的正式发布仍走现有 Document Assistant，不能出现同一文档两套工具无记录地交替写入。

正式发布的来源关联、查重、正文回读、权限回读、唯一导航中心登记及登记失败恢复仍然是完成条件。本轮可以梳理官方 CLI 与旧发布层的衔接缺口，但不改写 Hub、复制私有 Registry或宣称正式发布已经全面兼容。若要将 CLI 成为默认 Provider、退役旧接口或迁移正式成果，另经 Review 与明确批准。

## 5. 交付与停止条件

交付：唯一正式 Task 路径、实施分支/commit、CLI 与 Skills 版本、本机安装及身份验证的脱敏结果、临时文档局部读写结果、失败尝试、旧 MCP 未被破坏的检查、回退方法与唯一下一步。原始响应、真实身份、租户/文档标识、完整正文和凭据均不进公共 Git。

首次接入完成标准是“可在约定范围使用的并行文档 Provider”，不是“已替代文档助手全部能力”。卸除本轮 Skills/安装或退出本轮隔离配置应能回到原方案；不要注销或删除其他应用的现有授权。登录信息和 API 返回字段仅在受控本机使用。

## 6. Idea Handoff 与本次记录边界

继续沿用研究中的同一 Idea：CAP-DOC 官方飞书 CLI 复用与薄发布层。建议把最小并行试用记为 Current（本次 User 已同意，执行状态待正式 Task）；全量迁移保持未批准，不另建同义产品条目。Codex 写入前重新读取唯一 Product Roadmap 防重，按正式 Task 更新治理记录。本交接自身没有修改 Roadmap。

本次只补充研究分支中的交接文本，没有在 User 本机安装、授权、执行命令、切换 Provider 或启动 Codex，也没有改动原工具和 EarlyMeeting。上一研究中的未授权描述保留其历史时点；本文件仅将有限的文档试用推进到正式任务准备。

## 官方依据

- [CLI v1.0.94 发布](https://github.com/larksuite/cli/releases/tag/v1.0.94)。
- [对应版本安装与快速开始](https://github.com/larksuite/cli/blob/v1.0.94/README.zh.md)。
- [共享规则](https://github.com/larksuite/cli/blob/v1.0.94/skills/lark-shared/SKILL.md)。
- [应用初始化](https://github.com/larksuite/cli/blob/v1.0.94/skills/lark-shared/references/lark-shared-config-init.md)。
- [身份与最小权限 / split-flow](https://github.com/larksuite/cli/blob/v1.0.94/skills/lark-shared/references/lark-shared-identity-and-permissions.md)。
- [Codex Skills 官方说明](https://developers.openai.com/codex/skills)。目标 Host 仍需按实际安装版本确认发现入口。
- [项目 CAP-DOC](../../capabilities/document/README.md)。
