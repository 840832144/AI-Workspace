# Changelog

本文件记录 AI-Workspace 治理结构、标准、工作流和协作行为的变化。

## [0.12.1] - 2026-08-27

### Added

- 新增 `docs/overview/AI_WORKSPACE_PROJECT_OVERVIEW.md`，以稳定视角说明立项原因、能力蓝图、整体架构、设计框架、核心逻辑、角色和安全边界，不承载实时 Task 清单。
- 新增 `docs/status/AI_WORKSPACE_PROJECT_PROGRESS.md`，独立维护当前能力、已完成、未完成、阻塞、主线、支线 Candidate、证据、最后核验时间和同文档更新规则。
- 通过 Document Capability 防重创建两份互相链接的飞书正式文档，并保留 Git 源稿作为真相源。

### Changed

- TASK-0019 进入 Review；进度文档同步至 `main@0707449`，纳入 TASK-0018 冲突止损、Cash Frenzy Cancelled、TASK-0020、Huuuge Lottery 报告交接、TASK-0021 与最新 ChatGPT Handoff。

### Validation

- `feishu_healthcheck` 全部通过；精确标题搜索各命中 1 份，项目搜索恰好命中 2 份正式文档。
- 两份飞书文档回读标题、正文、互链、基线与表格通过（全景 7 张，进度 9 张）；权限均验证为 company edit / `tenant_editable`，转换 warning 为 0。
- Git 源稿完成职责边界、相对链接、敏感模式和 `git diff --check` 验证；Huuuge、SVN 与 Document Assistant 仅做只读核验。

### Boundaries

- 未创建第三份正式文档，未把动态 Task 清单写入项目全景说明，未把 Candidate/Planned/Blocked 状态升格为已完成。
- 未修改 TASK-0016、两个 TASK-0018、TASK-0020/0021、Huuuge 业务工作树、SVN、Document Assistant 或本机敏感配置；Subagents: none。

## [0.12.0] - 2026-08-27

### Added

- TASK-0018 Lottery 数值拆解交付索引，固定外部 Git 报告 commit 与企业内可编辑飞书文档。

### Changed

- TASK-0015 从 `Ready` 更新为 `Complete`，TASK-0018 从 `Ready` 更新为 `Review`；TASK-0014 保持 `Accepted`。
- Huuuge Project Status、Memory 和 Knowledge Index 同步 Lottery L3 Runtime Observed 基线；证据分布调整为 L3 × 12、L2 × 3、L1 × 22。
- Lottery 知识明确区分直接 Toss 奖励、阈值返还、购买发放与升级关联产出；升级后的余额变化为 Confirmed，升级因果保持 Estimate。

### Validation

- 外部 `huuuge-android-research@bfed5f30e098522ffb98ef5eb7d63e824d68b1c4` 已推送，报告与 6 份脱敏 CSV 可定位。
- 飞书正文回读 565 blocks，关键 Finalize、升级关联与 CR 章节存在；企业内可编辑权限验证通过。
- 未复制 Raw、decoded values、真实 Session/account ID、绝对余额、付费价格或 credentials；未修改 Collector、CR、SVN、游戏或服务端状态。

## [0.11.2] - 2026-08-27

### Fixed

- TASK-0016 Review Fix 1：新增 repository classification 与 Host-local approved destination contract；Project Private Candidate 只有在 alias、writer、classification、scope、sensitivity、source project 和外部 Git root 全部匹配时写入私有 repository，否则进入 Outbox。
- TASK-0016 Review Fix 2：AUTO canonical promotion 现在要求非 main/master linked worktree、仅允许 Inbox dirty scope，并将 target、Candidate、Archive、index 作为可回滚事务；Git identity/status 变化 fail closed。
- TASK-0016 Review Fix 3：CLI、Event file、Generic Agent 三条 Git Candidate 入口拒绝空值及 `unknown` / `n/a` / `none` / `-` 等占位 provenance。

### Validation

- 34/34 单元测试通过；新增 disposable private Git routing、未批准/无效 Registry、classification/sensitivity mismatch、public alias 冲突、private path 回指 public repository、main/dirty worktree gate 与三入口 provenance 回归。
- 五类 fault injection（target 后、Archive 前、Archive 后、index save、Git status change）均恢复 target/Candidate/Archive/index 执行前状态，`promoted=0`，无 recovery record。
- Round 2 隔离 Pilot：captured 3（其中 approved private Git 1）、promoted 1、review 1、local-only/Outbox 4、OFF suppressed 1、failed 0；最终模式 `ASSISTED`。

### Boundaries

- Private 测试只使用 disposable Git repository；未读取或修改真实 Huuuge、CR、Collector、Capture、SVN、飞书或 Document Assistant。
- 未激活 Hook、Global runtime 或 production AUTO；未修改 TASK-0017 网络脚本、分支或 Codex proxy 配置。

## [0.11.1] - 2026-08-27

### Added

- TASK-0017：新增 Windows PowerShell 5.1 Codex Desktop 网络状态、transport matrix、最小修复、恢复和脚本回归入口。
- 新增脱敏实验记录与可复用 reconnecting-proxy Solution，记录 Aurora / WinINET / WebSocket / HTTPS / TLS 的分层证据。

### Fixed

- Codex 用户配置启用当前版本已验证的 `features.respect_system_proxy = true`，使 Responses WebSocket 经 WinINET loopback proxy 建立 HTTP 101；没有修改 Windows 或 Aurora 全局路由。
- Restore 以 post-fix hash 选择精确恢复或仅撤销本任务键，保留 Codex 后续写入的无关设置，并兼容 Windows PowerShell 5.1 JSON 对象属性扩展；键冲突时 fail-closed，Repair 与 Restore 失败都回到操作前配置。

### Validation

- Baseline 稳定复现 WebSocket timeout 与 HTTPS inference reachable；temporary system-proxy override、explicit proxy 和持久修复均得到 HTTP 101，未观察到 TLS 或 DNS failure。
- 完成 restore exact-hash、保留后续配置的 surgical restore、reapply、Repair 幂等和 PowerShell 5.1 回归。
- 三个新 Codex 任务连续返回完整验证串，每次随后 transport probe 均为 WebSocket HTTP 101、HTTPS ok、TLS ok。
- `feishu-docs` healthcheck 与 Git fetch / branch push 正常。

### Boundaries

- 未修改 TASK-0016 worktree、Huuuge 仓库、Collector、Capture、Aurora 配置、Windows 全局 proxy、TLS trust、Provider 或 MCP 配置。
- 未强制结束当前 Codex Desktop 外壳；新任务和新 CLI 进程已验证配置重载，完整外壳退出重开留给 User 在 Review 后正常执行。

## [0.11.0] - 2026-08-27

### Added

- TASK-0016：新增 Git-backed Memory Capability、治理标准、ADR-0005、Memory Event/Candidate/Review schema、Inbox/Review/Archive/Index 与 Public-safe Solution 目录。
- 新增跨平台 Python 标准库实现和 Windows PowerShell 入口，支持 Capture、Validate、Curate、Refresh、Status 与 OFF/ASSISTED/AUTO 模式切换。
- 新增 ChatGPT Project、Codex、Generic IDE Agent adapters，以及默认禁用的 Codex SessionEnd hook reference。
- 新增 Context Manifest、ChatGPT Project Source Pack、Source replacement list 和隔离 Pilot。

### Changed

- Global/Project AGENTS、ChatGPT 00–03 Sources、AI Team、Architecture、Capability Catalog 和相关 README 加入 source-side Memory Check 与安全路由。
- Reuse-first 结论采用 OpenAI 原生 recall/lifecycle 能力与 Git 真相源的组合；不安装外部 Memory SaaS、数据库或高权限 App。
- Production 和仓库默认模式为 `ASSISTED`；`AUTO` 只在隔离 Pilot 验证受限的低风险新 Solution 晋升。

### Fixed

- 最终回归发现 PowerShell `ValueFromRemainingArguments` 会把省略参数转成空字符串；薄 wrapper 现在构造显式命令数组并以命名参数交给通用 launcher，Status/Mode/Curate/Refresh 一键入口均加入真实回归。

### Validation

- 17/17 单元测试通过，覆盖 schema/fingerprint、Secret、dedup、conflict、concurrency、rollback/no-overwrite、Git gate、dirty sync fail-closed、Windows named parameters 和所有无额外参数的薄 wrapper。
- 隔离 Pilot：captured 2、promoted 1、review 1、local-only/Outbox 3、OFF suppressed 1、conflicts 0、failed 0；未虚构 false-positive 或 missed-capture rate。
- 最终 AI-Workspace refresh：41 public control-plane sources、0 Secret issue、0 broken link、private repositories not read、manual upload required。

### Boundaries

- 未安装或激活 Global hook，未切换 production AUTO，未自动替换 ChatGPT Project Sources，未创建外部服务、私有 Context Hub 或新权限。
- 未修改 Huuuge 仓库、运行中的 Collector、当前 Capture、SVN、飞书云文档、Document Assistant 或其他业务仓库。

## [0.10.1] - 2026-08-27

### Fixed

- TASK-0014 Review Fix：安装器现在先完成并验证 OFF，再创建或替换 Agent 模板；config OFF 失败不会触碰 Agent 目录或输出误导性成功信息。
- Global AGENTS、Bootstrap README、ADR-0004 与 Pilot 明确禁止 MANUAL 和 `--yolo`、Full access、`danger-full-access`、宽松 `/permissions` 或等价父 turn 权限并用。
- `knowledge_retriever` 定位改为读取本地/已提供资料；飞书继续由主 Agent 代读并提供最少、脱敏摘要。

### Validation

- 新增安装失败原子性回归：inline、multiline、config lock 三类 OFF 失败均保持配置字节和既有模板哈希不变，不新增其余模板，不输出 `Installation default: OFF`。
- MANUAL 切换输出明确的权限前提和“无法自动检测 live permission”；本轮宽松权限环境保持 OFF，没有启动 Subagent。
- Windows PowerShell 5.1、幂等安装、配置完整性、Global 模板同步和最终 OFF 状态重新验证通过。

### Boundaries

- 未实现不可靠的 live permission 自动检测，也未在宽松权限环境启用 MANUAL。
- 未修改 Agent 数、并发上限、MCP Server、业务仓库、飞书云文档或 ChatGPT 设置。

## [0.10.0] - 2026-08-27

### Added

- TASK-0014：新增 4 个版本化只读 Codex Agent 模板，分别负责仓库探索、资料检索、证据测试核验和独立 Review。
- 新增 Windows PowerShell 5.1 安装、`OFF` / `MANUAL` 开关、脱敏状态与隔离回归测试脚本。
- 新增 [`ADR-0004`](docs/adr/ADR-0004-Codex-Subagent-Pilot.md)、[`Codex Subagent Bootstrap`](bootstrap/codex/README.md) 与 [`Pilot 记录`](docs/experiments/CODEX_SUBAGENT_PILOT.md)。

### Changed

- Global AGENTS 增加保守 Subagent Policy：默认单 Agent、简单任务不委派、主 Agent 唯一写入、失败自动降级。
- AI Team 和 Architecture 明确 Subagent 只承担独立只读工作，不改变 Capability Discovery、完成标准或外部写入授权。
- 本机安装 4 个 Agent，`config.toml` 只增加/维护 `[agents]` 开关和并发上限；试验结束必须恢复 `OFF`。

### Validation

- 四个 Agent TOML 均通过 `tomllib`，且 `sandbox_mode = "read-only"`；PowerShell 脚本通过 Windows PowerShell 5.1 语法与运行测试。
- 隔离回归覆盖 legacy alias、非 Agent 配置保留、特殊 TOML 形态 fail-closed、同名模板备份、幂等安装和安装后 OFF。
- OFF 新会话无法启动 Subagent，但普通单 Agent 任务成功；MANUAL 新会话成功启动并汇总指定 `repo_explorer`。
- 复杂只读场景并行运行 3 个 Agent；子 Agent 发现的脚本阻断经主 Agent 修复并复测，未发生并行写冲突。
- Reviewer 发现 MCP 继承风险后，当前 Pilot 改为在子 Agent 中禁用 `feishu-docs` 和 `node_repl`；新会话无副作用探针确认二者均不可用。
- 模式补丁器新增独占锁、多行 TOML fail-closed 与并发竞争回归，避免覆盖同时发生的非 Agent 配置更新。
- 最终恢复 `OFF`；新会话确认 Subagent tools 不可用、普通单 Agent 任务仍可完成，四个模板继续保留。
- 当前客户端没有暴露可归因 usage/token 数字，因此没有记录虚构额度对比。

### Boundaries

- 未实现 AUTO、1+8、多 Agent 并行写、Git worktree 调度器或额度系统。
- 未修改 Huuuge Collector、Document Assistant、MCP Server、SVN package、飞书云文档、ChatGPT 设置或其他业务仓库。

## [0.9.0] - 2026-08-26

### Added

- TASK-0013：建立 [`Capability Catalog`](capabilities/README.md)，定义 Capability-first 发现顺序、Catalog schema、契约状态与实现状态分离规则。
- 建立首个共享 [`Document Capability`](capabilities/document/README.md)，定义 7 个结果 Operations、READ/WRITE/ADMIN 等级、成功证据、默认权限、failure semantics 和当前 provider mapping。
- 新增 ADR-0003，正式决定“先发现 Capability，再选择 Implementation Binding 与 Tool”。

### Changed

- Global AGENTS 顶层入口从 Tool-first 调整为 Capability Discovery；Tool 的检查与选择只属于 Capability 实现层。
- `Document Assistant` 从“Capability 本身”校正为 `Document Capability` 的当前实现 provider；Feishu MCP tools 明确为 provider-specific interfaces。
- ADR-0002 标记为 Superseded，由 ADR-0003 取代；历史内容保留，不重写原决策。
- Architecture、Workspace Kernel、Capability Model、AI Team、Manifest、Roadmap、RFC-0002、Document Assistant Roadmap、Feishu Document Skill 与 Bootstrap 统一采用 Capability-first 模型。
- 本机 `C:\Users\admin\.codex\AGENTS.md` 与仓库模板同步更新；公共 AI-Workspace 和现有 First Run 路径保持不变。

### Validation

- 对照 OpenAI 官方 `AGENTS.md` 文档确认 Global 与项目级指令仍按既有顺序叠加；Capability-first 是本 Workspace 的治理契约，不冒充 Codex 内置 resolver。
- `bootstrap/AGENTS.md` 与本机 `~/.codex/AGENTS.md` 的 SHA-256 一致，且没有 Global override 遮蔽。
- Catalog、Document Capability、ADR、Architecture、Kernel 和 Manifest 内部链接、边界与术语验证通过。
- 全仓敏感值、禁用词、diff 和私有新人前置检查通过。

### Boundaries

- 未实现 Capability Registry、resolver、自动选择器或新 Tool。
- 未修改 Document Assistant、MCP 配置、ChatGPT 设置、First Run 飞书文档、采集器、SVN package 或业务功能。

## [0.8.0] - 2026-08-26

### Added

- TASK-0012：新增 `bootstrap/AGENTS.md`，作为 `~/.codex/AGENTS.md` 的版本化 Global Codex 模板。
- 建立 Tool Discovery 规则：读取生效指令、检查当前 Host 实际能力、优先专用接口、区分 READ/WRITE/ADMIN、先确认再修改、失败时不建立未经批准的替代入口。
- 将 Document Assistant 定义为所有项目共享工具，记录实现真相源、非敏感资料入口、工具分级、搜索防重、回读验证和凭据边界。
- 新增 ADR-0002，正式记录 Global Tool Discovery 与 AI-Workspace 职责分离。

### Changed

- 本机安装 `C:\Users\admin\.codex\AGENTS.md`，与仓库模板内容一致；当前没有 `AGENTS.override.md` 遮蔽该文件。
- AI-Workspace 不再承担运行时工具入口职责，只定义 Game Design 的 Capability、Workflow、Skill、Template、项目治理和工具使用契约。
- Architecture、Workspace Kernel、Capability Model、Manifest、Roadmap、RFC-0002、Feishu Document Skill 和 AI Team 统一移除工具目录、安装入口、endpoint、credential 与连接状态职责。
- 新生成云文档的默认企业内可编辑规则提升为 Global Codex 规则；管理员策略失败时保留文档并报告，不重复创建。
- 根据当前权限现实发布 First Run RC4：公共 AI-Workspace 成为新人唯一必需 Git 仓库，私有实现仓库只供维护者追溯，不再作为新人 Clone 或安装前置。
- 将公司 SVN 和管理员预配置的 Document Assistant 加入前三分钟 fail-fast；保留“新策划在新电脑 30 分钟完成采集、Markdown、AI 写飞书”的真实盲测目标，不预填成功或耗时。
- 同一篇飞书 First Run Guide 使用 replace 同步 RC4，保持原 document ID 与既有企业内可编辑权限，不创建副本。

### Validation

- 对照 OpenAI 官方 `AGENTS.md` 发现顺序确认 Global 与项目级叠加规则。
- `bootstrap/AGENTS.md` 与本机 `~/.codex/AGENTS.md` 的 SHA-256 一致。
- First Run 全文检查确认新人主线不再要求访问或 Clone 私有 Git 仓库。
- 飞书回读确认 RC4、30 分钟目标、公共单仓入口和前三分钟预检均存在，两条私有仓库 Clone 指令均不存在。
- 对原飞书 document ID 再次执行公司编辑权限回读，确认 `link_share_entity=tenant_editable`、`verified=true`。
- 全仓检查确认没有 credential、token 或运行时 endpoint 值写入；内部链接、禁用词、diff 与 Workspace 边界验证通过。

### Boundaries

- 未修改 Document Assistant、`feishu-doc-mcp`、MCP 配置、ChatGPT 设置、采集器、SVN package 或业务功能。
- Global 文件只包含稳定规则和公开仓库引用，不包含项目状态、私有 Registry、文档正文或 secrets。

## [0.7.0-rc.3] - 2026-08-26

### Changed

- 将新人首次打开的工作目录从一次性首跑目录统一为长期复用的 `C:\AI-Workspace`。
- 从零提示词新增目录状态判断：空目录 Clone AI-Workspace、已有正确仓库安全更新、非空且不是目标仓库时停止并报告冲突，不得覆盖。
- 明确该目录后续继续承载 Knowledge、Status、Handoff 和其他游戏策划项目，不在首跑后丢弃。
- 飞书原文档使用 replace 同步 RC3，保持同一 document ID 和企业内可编辑权限。

### Boundaries

- 只修改文档和流程；未开发功能，未修改采集器、外部研究仓库、SVN package 或本机环境。

## [0.7.0-rc.2] - 2026-08-26

### Changed

- 根据 User 预验收反馈，将 First Run Guide 从“AI/技术流程说明”重构为新人可直接执行的主线。
- 在文档最前新增 12 个连续步骤：打开 AI、发送从零提示词、完成登录、安装缺失软件、确认专用实例、登录游戏、等待 READY、正常操作、停止、核对结果、检查 Markdown/飞书、最终验收。
- 每一步补充新人应该说什么、AI 应该完成什么、看到什么算通过，以及卡住时可直接发送的回复。
- 新增“新人全过程只需要说的五句话”，后续技术章节保留为 AI 与排障参考。
- 飞书原文档使用 replace 更新，无 conversion warning；回读确认新人主线、第 12 步和五句话均存在。

### Boundaries

- 此反馈来自参与项目的 User，不计入未参与开发策划的独立盲测。
- 未开发新功能，未修改采集器、外部研究仓库、SVN package、BlueStacks 或本机研究实例。

## [0.7.0-rc.1] - 2026-08-26

### Added

- TASK-0011 盲测前版本《Huuuge 新人上手指南（First Run Guide）》，覆盖新电脑准备、仓库 Clone、AI 主导启动、采集、Markdown、Document Assistant、成功验证和常见问题。
- `REPORTS/TASK-0011-FIRST-RUN-VALIDATION.md`，用于真实记录未参与开发策划的卡点、阶段耗时、AI 独立引导能力与后续文档修订。
- 飞书版本 [`Huuuge 新人上手指南（First Run Guide）`](https://gfok27asqq.feishu.cn/docx/Ffibd2Cx2oXFgfxdKnJcE6uUnZf)。

### Changed

- 将 First Run 默认入口设为 Codex 或 Trae + DeepSeek；新人只处理登录、审批和正常游戏操作，AI 处理检查、启动、停止、整理、Markdown 与飞书发布。
- 文档规范新增：面向策划/用户的正文默认使用中文，其他语言只用于必要技术内容。
- 云文档规范新增：除非 User 明确要求其他权限，新生成文档默认企业内可编辑；管理员策略失败不得触发重复创建。
- Huuuge 项目 README、Memory、Workflow、Status 与 Reports Index 接入 First Run Guide、云文档默认权限和验证记录。

### Validation

- `feishu_healthcheck` 通过环境、token、API connectivity 和 Drive permission probe。
- 创建飞书文档无 conversion warning；`get_document` 回读标题、正文、公司编辑规则和盲测章节成功。
- 通过当前 Document Assistant STDIO Server 执行 `grant_company_edit`，回读 `link_share_entity=tenant_editable`、`verified=true`。

### Pending

- 尚未由未参与开发的策划执行盲测，因此真实卡点、耗时和 AI 是否能独立引导仍为 Pending。
- 完成盲测后只允许修订文档和流程，再发布正式 0.7.0 并进入 ChatGPT Review。

### Boundaries

- 未修改 `huuuge-android-research`、采集器、SVN package、BlueStacks 或本机研究实例。
- 未开发任何新功能，也未复制 Raw、decoded values、账号/Session 数据、credential 或完整运行日志。

## [0.6.0] - 2026-08-26

### Added

- TASK-0010：建立 `Huuuge Evidence Standard`，统一 L0 Unverified、L1 Schema、L2 Configured / Visible、L3 Runtime Observed、L4 Triangulated 五级判定标准。
- 定义 Schema、Config、Runtime、UI、Manual 五类引用的合格来源、必填定位信息和单类证据上限。
- 定义 `HGR-YYYYMMDD-TYPE-NNN` Citation ID、完整/紧凑引用格式、claim scope、limits 以及升级、降级、冲突和过期规则。

### Changed

- Knowledge Index 与 Slots、Systems、Events、Others 全部 37 个模块迁移到统一等级：L3 × 11、L2 × 4、L1 × 22、L0/L4 × 0。
- 将模块证据摘要统一为 Runtime、Schema 和 Schema hint，明确 ZPK 文件名命中不能单独提升等级。
- 项目 README、Memory、Workflow、Status 与 Codex/ChatGPT Handoff 接入统一 Evidence Standard。
- TASK-0009 的 E0–E3 临时导航模型由 L0–L4 标准取代；历史 CHANGELOG 保留原始记录。

### Boundaries

- 未修改 `huuuge-android-research`、采集器、module catalog generator、SVN release 或本机研究环境。
- 未虚构或回填当前外部 artifact 尚不存在的 Citation ID，也未把任何模块提升到 L4。
- 未复制 Raw/decoded values、账号/会话数据、截图、完整日志、APK、binary 或 credential。
- 未开发 Evidence Registry、采集、Extractor、Exporter 或报告功能。

## [0.5.0] - 2026-08-26

### Added

- TASK-0009：建立 `Huuge Research Knowledge Index` 作为整个研究知识的统一入口。
- 建立 Slots、Systems、Events、Others 四类导航，覆盖外部 catalog 全部 37 个模块。
- 为每个模块记录 evidence level、live/schema/static 数据来源、结构完成度和 Review 后下一步计划。
- 定义 E3 Primary live、E2 Cross-cutting/config live、E1 Schema-only、E0 Inferred/static 四级知识证据模型。

### Changed

- Huuuge Project README、Memory、Workflow、Status 接入 Knowledge Index，并将当前 milestone 更新为 TASK-0009 Review。
- 将 Huuuge 项目 README 与 Knowledge Index README 的策划入口文案改为中文，同时保留固定模块名和技术文件名。
- Codex/ChatGPT Handoff 更新为 Knowledge Base Review gate。

### Boundaries

- 未修改 `huuuge-android-research`、采集器、module catalog generator、SVN release 或本机研究环境。
- 未复制 Raw/decoded values、账号/会话数据、APK、binary、credential 或完整外部 dossier 正文。
- 未开发新采集、分类器、Extractor、Exporter 或报告功能。

## [0.4.0] - 2026-08-26

### Added

- TASK-0008：从 Workspace Project Template 初始化 `projects/huuuge-android-research/`。
- 建立 Huuuge 项目 Context、Memory、Workflow、Status、Reports 和 Assets 控制面。
- 建立 Battle Pass、Slots、Lottery、Task/Missions 四条稳定研究入口，并锁定外部 evidence baseline commit `0590c2c`。

### Changed

- `projects/README.md` 从“仅提供模板”更新为包含首个正式登记的游戏研究项目。
- Codex/ChatGPT Handoff 更新为 TASK-0008 Review gate。

### Boundaries

- 未迁移或修改 `huuuge-android-research` 的源码、采集器、脱敏产物或运行配置。
- 未复制 Raw/decoded values、账号/会话数据、APK、native/Frida binary、credential 或外部文档正文。
- 未开始新采集、Extractor、报告开发或 Feishu 发布。

## [0.3.0] - 2026-08-26

### Added

- TASK-0007 `Document Assistant Capability Roadmap`，规划公司文档中台的 15 个 Capability、六阶段演进、Review 问题与非目标。
- 新增 `docs/roadmaps/` 作为服务与工具 Capability Roadmap 的索引入口。

### Changed

- 明确 `Document Assistant` 暂不改名，现有实现保持不变，外部仓库继续作为实现真相源。
- 将 Workspace Phase 2 标记为 Planning / Waiting for ChatGPT Review。
- 明确共享公司基础设施可以服务多个使用方，但 AI-Workspace 只治理其 Game Design 使用边界，不导入其他领域业务内容。

### Boundaries

- 未修改 Document Assistant、`feishu-doc-mcp`、MCP 配置或 ChatGPT 设置。
- 未开发 transport、permission、sync、monitoring 或 deployment 功能。
- 未调用 Feishu API，未迁移仓库或文档数据。

## [0.2.0] - 2026-08-26

### Changed

- 将 AI-Workspace 从通用 AI 工作空间正式收敛为 Game Planner AI Workspace。
- 明确目标用户为游戏策划、游戏数值策划、系统策划、活动策划和数据分析，并排除非游戏领域。
- 将 Roadmap 重构为 Workspace Foundation、Document Assistant、Workspace Sync、Planner Toolkit 四阶段。
- 完善 AI Team 的 Decision、Review、Ownership、Tool Ownership、Security 和 Escalation 规则。
- 将项目标准从 Context、Memory、Workflow、Status 四件套扩展为包含 Reports、Assets 的统一游戏项目结构。
- 将项目模板的唯一入口收敛到 `projects/TEMPLATE/`，移除旧的重复四件套模板。

### Added

- 新增 Workspace Kernel，定义 Workspace、Project、Skill、Workflow、Capability、Template、Tool、Agent、Memory、Status 及 Mermaid 关系图。
- 新增 Capability Model，定义 Capability、Skill、Workflow、Template、Tool 的分层关系。
- 新增 Game Analysis、Slot Analysis、Battle Pass、Economy Design、Lottery、Task System、Excel、SQL、Python、Report Writing、Feishu Document 共 11 类 Skill 目录。
- 新增 `projects/TEMPLATE/` 游戏项目标准模板。
- 新增仅作规范示例的 `workspace.yaml.example`。
- 新增 ADR-0001，记录 Game Design 领域收敛决定。

### Boundaries

- 未实现任何业务代码、Skill 运行时、manifest loader 或同步程序。
- 未迁移任何现有仓库或游戏项目。
- 未修改 `feishu-doc-mcp` / `document-assistant`。
- 未加入任何非游戏领域内容。

## [0.1.0] - 2026-08-26

### Added

- 初始化 AI 协作总控仓库，不包含业务代码。
- 建立 RFC、ADR、Skills、Workflows、Templates、Standards、Projects、Handoff 和 Bootstrap 目录。
- 建立 README、AI Team、Architecture、Roadmap、Contributing 和 Agent 入口文档。
- 建立 Workspace Charter、Document Assistant、AI Skill System 三份初始 RFC。
- 建立 ChatGPT 与 Codex 固定交接文档。
- 定义项目 Context、Memory、Workflow、Status 四件套及可复制模板。
- 建立 RFC、ADR、项目和交接模板，以及各目录入口说明。

### Boundaries

- 未实现任何业务代码。
- 未迁移或修改任何现有项目仓库。
- 未修改 `feishu-doc-mcp` / `document-assistant`。
