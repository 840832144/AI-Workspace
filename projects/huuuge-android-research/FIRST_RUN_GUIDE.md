# Huuuge 新人上手指南（First Run Guide）

- 适用对象：第一次使用 Huuuge 数据采集流程的游戏策划、数值策划和数据分析人员
- 默认操作入口：Codex，或 Trae + DeepSeek
- 适用系统：Windows 10/11 64 位
- 当前状态：TASK-0011 独立策划盲测前修订版（RC3）
- 更新日期：2026-08-26
- 飞书版本：[`Huuuge 新人上手指南（First Run Guide）`](https://gfok27asqq.feishu.cn/docx/Ffibd2Cx2oXFgfxdKnJcE6uUnZf)

这份指南的目标是：新人只需要把任务交给 AI、完成本人才能完成的登录/授权、正常操作游戏，其余检查、安装、启动、整理和文档发布由 AI 主导。不要让新人手工执行长串 PowerShell、ADB、Frida 或 Proto 命令。

## 0. 新人照着做：第一次只看这一节

下面是新人真正需要完成的全部步骤。第一次不要先读后面的技术说明；遇到问题时让 AI 查后面的章节。

### 第 1 步：打开一个 AI 工具

二选一：

- 打开 Codex；或
- 打开 Trae，选择公司批准的 DeepSeek。

如果电脑还没有这两个工具，请先从公司批准的软件入口安装其中一个并完成登录。不要同时配置两套；第一次先选一套跑通。

打开后，新建或选择长期使用的 Workspace 目录：

```text
C:\AI-Workspace
```

这个目录以后继续用于 Knowledge、Status、Handoff 和其他游戏策划项目，不是首跑结束后丢弃的临时目录。你现在不需要手工 Clone 仓库，也不要打开 PowerShell；下一步让 AI 判断当前目录是空目录、已有仓库还是需要安全更新。

### 第 2 步：把这段话完整发给 AI

```text
我是第一次使用 Huuuge 数据采集的新策划，请你直接作为我的本机操作员完成 First Run。

请先准备下面两个仓库，不覆盖任何现有文件：
- 当前 C:\AI-Workspace 如果还不是 Git 仓库且目录为空，把 https://github.com/840832144/AI-Workspace.git Clone 到当前目录；如果已经是该仓库，安全更新 main；如果目录非空且不是该仓库，停止并说明冲突，不要覆盖。
- https://github.com/840832144/huuuge-android-research.git → C:\HuuugeResearchSource

Clone 后先读取：
- C:\AI-Workspace\projects\huuuge-android-research\FIRST_RUN_GUIDE.md
- C:\AI-Workspace\projects\huuuge-android-research\STATUS.md
- C:\HuuugeResearchSource\AGENTS.md
- C:\HuuugeResearchSource\CONTRIBUTING.md
- C:\HuuugeResearchSource\CURRENT_STATUS.md
- C:\HuuugeResearchSource\HUUUGE_COLLECTOR_DEPLOYMENT_MANUAL.md
- C:\HuuugeResearchSource\AI_DEPLOYMENT_PLAYBOOK.md
- C:\HuuugeResearchSource\AGENT_DATA_USAGE_GUIDE.md

然后请你直接完成：
1. 检查这台电脑缺少什么；
2. 安装或更新正式的 SVN 采集器；
3. 检查专用 HuuugeResearch 模拟器；
4. 启动采集并验证 READY；
5. 等我正常操作游戏；
6. 我说“可以停止”后 clean stop/finalize；
7. 生成中文脱敏 Markdown；
8. 通过 AI Document Assistant 写入飞书、设置企业内可编辑并回读验证。

你能自己执行的检查和命令直接执行，不要让我手工复制命令或解释底层日志。
只有 Git/SVN/AI/游戏首次登录、验证码、Windows 管理员确认和机器级修改审批可以让我操作。

不得修改我日常使用的 BlueStacks 实例；只允许使用独立的 HuuugeResearch。
任何 BlueStacks 主机文件、配置、Root 或虚拟磁盘修改前，必须先告诉我修改目标、备份位置、影响和恢复方法，并等待我明确同意。
不得上传 Raw、完整 decoded values、账号、Session 标识或凭据，不得修改游戏请求、奖励、余额或服务器状态。

现在开始。每次只告诉我：你已经确认了什么、你正在做什么、我下一步只需要做哪一件事。
```

发送后先等 AI 工作。不要因为 AI 正在检查就自己去下载一堆工具，也不要同时运行旧脚本。

### 第 3 步：出现登录窗口时，由你完成登录

AI 可能依次要求你完成：

- GitHub 登录；
- 公司 SVN 登录；
- Codex 或 Trae 登录；
- Windows 管理员确认；
- BlueStacks / Google Play / Huuuge Casino 登录；
- 飞书登录或由管理员完成 Document Assistant 的受控配置。

你只在系统或官方登录窗口输入账号、密码和验证码。不要把密码、access token、飞书密钥或验证码发到 AI 聊天里。

完成一个登录后，只回复：

```text
我已完成这个登录，请继续检查。
```

### 第 4 步：让 AI 安装缺少的软件

AI 会检查 Git、SVN command line client、Python、BlueStacks 和采集器。缺少软件时：

1. 让 AI 说明“缺什么、为什么需要、准备从哪里安装”；
2. AI 能执行的安装让它直接执行；
3. 出现 Windows 安装或管理员确认窗口时，你点击确认；
4. 安装结束后回复：

```text
安装窗口已经完成，请你继续验证，不要只凭安装成功提示判断。
```

你不需要自己创建 Python 虚拟环境、选择依赖版本或复制安装命令。

### 第 5 步：确认只使用专用模拟器

AI 必须找到或准备一个名为 `HuuugeResearch` 的独立 BlueStacks 实例。

你需要确认两件事：

- AI 明确说不会修改日常使用的 BlueStacks 实例；
- 如果需要修改研究实例，AI 已经列出备份位置和恢复方法。

只有两项都明确时，才回复：

```text
我确认只允许修改 HuuugeResearch 专用实例，并且已经看到备份和恢复方法。请继续。
```

如果 AI 没有提供这些信息，回复：

```text
先停止修改。请说明目标实例、修改文件、备份位置、影响和恢复方法。
```

### 第 6 步：在专用模拟器中登录游戏

当 AI 打开 `HuuugeResearch` 后：

1. 确认窗口标题或 AI 报告的是 `HuuugeResearch`，不是日常实例；
2. 在这个实例里登录 Huuuge Casino；
3. 等游戏进入大厅；
4. 回复 AI：

```text
HuuugeResearch 已进入游戏大厅，请继续启动并验证采集。
```

### 第 7 步：等到 AI 明确说 READY

AI 会启动采集器并自行检查数据是否真的开始保存。你必须看到 AI 明确回复：

```text
READY，可以开始玩了
```

没有看到这句话，就不要开始操作游戏。只回复：

```text
目前还没有 READY，请你读取最新环境和控制器报告继续排查。
```

不要把大段错误日志手工复制给其他人；让当前 AI 自己读取本机报告。

### 第 8 步：正常操作 5 分钟

看到 READY 后，在 `HuuugeResearch` 中正常完成：

1. 在大厅停留并切换一个页面；
2. 进入一个可用的 Slots，正常完成至少一次操作；
3. 打开一个当前可见的活动、任务、奖励或商店页面；
4. 总计正常操作至少 5 分钟。

不需要选择采集模块，不需要手工打标，也不要为了补数据购买、修改条件或触发异常操作。

### 第 9 步：告诉 AI 停止

操作完成后回到 AI，发送：

```text
我已完成正常操作，可以停止。请 clean stop/finalize，并自行验证结果完整后再告诉我。
```

等待 AI 完成。在 AI 明确说 finalized 前，不要强制关闭采集器或 BlueStacks。

### 第 10 步：检查 AI 给你的结果

AI 完成后，应给你一段简短结果，至少包含：

```text
采集状态：stopped/finalized
RPC：大于 0
Decoded：大于 0
结果目录：<本机脱敏路径>
Markdown：C:\HuuugeCollector\.local\reports\first-run\Huuuge_First_Run_Report.md
飞书：<文档链接>
权限：企业内可编辑 / 管理员策略阻塞
```

如果缺少其中一项，发送：

```text
请按 First Run Guide 第 9 节逐项验证，并补齐缺少的成功证据。不要用旧 Session 代替本轮结果。
```

### 第 11 步：打开 Markdown 和飞书文档

1. 打开 AI 给出的 Markdown，确认正文是中文；
2. 确认里面没有账号、token、完整余额轨迹或原始 payload；
3. 打开 AI 给出的飞书链接；
4. 确认标题和正文与 Markdown 对应；
5. 确认企业同事可以编辑；如果管理员策略阻止，只记录失败，不让 AI 重复创建。

### 第 12 步：判断是否完成

下面全部为“是”才算完成：

- AI 是主要操作入口；
- 使用的是 `HuuugeResearch`；
- 日常 BlueStacks 实例没有被修改；
- 出现过 READY；
- 本轮 Session 已 stopped/finalized；
- RPC 和 decoded 均大于 0；
- Markdown 已生成且脱敏；
- 飞书已写入并回读；
- 云文档权限为企业内可编辑，或已明确记录管理员策略阻塞。

如果有任何一项为“否”，不要宣布完成。把该项原样发给 AI，让它按“常见问题”继续处理。

### 新人全过程只需要说的五句话

除了最开始的完整提示词，新人通常只需要说：

```text
1. 我已完成这个登录，请继续检查。
2. 安装窗口已经完成，请你继续验证。
3. 我确认只允许修改 HuuugeResearch 专用实例，并且已经看到备份和恢复方法。请继续。
4. HuuugeResearch 已进入游戏大厅，请继续启动并验证采集。
5. 我已完成正常操作，可以停止。请 clean stop/finalize，并自行验证结果完整后再告诉我。
```

后面的章节是 AI、维护人员和遇到故障时的详细参考。

## 1. 第一次完成后，你会得到什么

一次成功的 First Run 应同时得到：

1. 一个独立的 `HuuugeResearch` BlueStacks 研究实例；
2. 一次显示 `READY，可以开始玩了` 的采集；
3. 一次 clean stop / finalized 的 Session；
4. 可打开的 RPC 清单、字段清单和模块目录；
5. 一份不含账号和原始值的 Markdown 总结；
6. 一份由 AI Document Assistant 写入并回读验证的飞书文档。

采集流程只被动记录客户端已经收到的数据，不修改游戏、奖励、筹码、请求或服务器状态。

## 2. 新人只负责哪些事情

新人只负责 AI 无法代替的操作：

- 完成公司 GitHub、SVN、飞书、Codex/Trae 的首次登录；
- 在本人界面输入账号或验证码，不把密码、token、密钥发给 AI；
- 在 AI 展示备份范围与恢复方法后，确认是否允许修改专用研究实例；
- 在 `HuuugeResearch` 实例中登录 Huuuge Casino；
- 看到 READY 后正常操作游戏，结束时告诉 AI“可以停止”。

仓库同步、环境检测、错误日志读取、脚本执行、结果路径定位、Markdown 生成和飞书发布默认由 AI 完成。

## 3. 新电脑需要准备什么

### 必需软件与权限

| 项目 | 用途 | 谁处理 |
| --- | --- | --- |
| Windows 10/11 64 位 | 运行采集器和 BlueStacks | 新人确认 |
| Git | 获取 AI 协作与工程资料 | AI 检测/安装；首次认证由新人完成 |
| TortoiseSVN，包含 command line client tools | 安装公司正式采集器包 | AI 检测；首次认证由新人完成 |
| Python 3 | 运行采集与整理脚本 | AI 检测/安装 |
| BlueStacks 5 | 运行独立研究实例 | AI 检测；游戏登录由新人完成 |
| Codex 或 Trae + DeepSeek | First Run 主要操作入口 | 新人登录，AI 执行 |
| 公司 GitHub、SVN、飞书访问权限 | 读取资料、安装运行包、发布文档 | 新人/管理员提供 |

如果这台电脑需要本地运行 AI Document Assistant，还需要 Node.js 20+ 与 pnpm。AI 应先检测，缺失时再安装，不要求新人自己判断版本。

### 必须保护的现有环境

- 不得把日常使用的 BlueStacks 实例用于研究。
- 不得对日常实例执行 Root、Frida 或 Host 修改。
- 专用实例统一命名为 `HuuugeResearch`；当前已验证环境对应 `Pie64_1`。
- 任何 BlueStacks 主机文件、配置或虚拟磁盘修改前，AI 必须给出目标、备份路径、影响和回滚方法，并等待新人明确确认。

## 4. Clone 哪几个仓库

以下命令由 AI 执行；新人只在认证窗口完成首次登录。

### 必需仓库

| 仓库 | 地址 | 用途 |
| --- | --- | --- |
| AI-Workspace | `https://github.com/840832144/AI-Workspace.git` | First Run Guide、Evidence Standard、Knowledge、Status 与 Handoff |
| huuuge-android-research | `https://github.com/840832144/huuuge-android-research.git` | 工程资料、部署 Playbook、数据使用规范和模块目录 |

默认使用下面两个长期路径。AI 必须先检查目录；只有目标不存在或为空时才 Clone，已经是正确仓库时改为安全更新，存在其他内容时停止并报告：

```powershell
git clone https://github.com/840832144/AI-Workspace.git C:\AI-Workspace
git clone https://github.com/840832144/huuuge-android-research.git C:\HuuugeResearchSource
```

### 按需仓库

只有本机尚未配置 AI Document Assistant 时，才需要：

```powershell
git clone https://github.com/840832144/document-assistant.git C:\DocumentAssistant
```

`document-assistant` 只负责飞书文档能力。飞书应用凭据只能由管理员通过受控环境变量配置，不能写进 Git、配置正文、聊天或日志。

Codex 路径由 AI 在 clone 后执行：

```powershell
Set-Location C:\DocumentAssistant
pnpm install
pnpm check
codex mcp add feishu-docs -- powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\DocumentAssistant\scripts\start-server.ps1
```

管理员通过受控 Windows 用户环境配置 Document Assistant 所需变量后，完全退出并重新打开 Codex，再由 AI 调用 `feishu_healthcheck`。命令和 Codex 配置中只能引用变量名，不能出现真实值。Trae 只有在公司已经配置相同 MCP 时才直接发布；否则按第 8 节交给已配置的 Codex。

### Git 与 SVN 的职责不要混淆

- Git 仓库是工程、知识与 AI 协作真相源。
- 策划日常运行的正式采集器来自公司 SVN，安装目录是 `C:\HuuugeCollector`。
- 不要直接在 Git clone 目录中替代正式 SVN 运行包，也不要把本地 Session 提交到 Git。

## 5. 用 AI 开始 First Run

### Codex 入口

1. 打开 Codex，选择 `C:\AI-Workspace` 作为工作区；
2. 把下面的“统一首跑提示词”发给 Codex；
3. Codex 应自行读取仓库、检查环境并执行安全步骤；
4. 只有登录、游戏操作或机器级修改审批才交还新人。

### Trae + DeepSeek 入口

1. 用 Trae 打开 `C:\AI-Workspace`；
2. 选择公司批准的 DeepSeek 配置；
3. 把下面的“统一首跑提示词”交给 Agent；
4. 允许 Agent 在本机读取仓库和脱敏结果，但是否上传模型服务必须服从公司数据政策；原始 Session 不得上传。

### 统一首跑提示词

```text
请作为我的 Huuuge First Run 操作员。

先读取：
1. projects/huuuge-android-research/FIRST_RUN_GUIDE.md
2. projects/huuuge-android-research/STATUS.md
3. standards/HUUUGE_EVIDENCE_STANDARD.md
4. huuuge-android-research 仓库中的 AGENTS.md、CONTRIBUTING.md、CURRENT_STATUS.md、
   HUUUGE_COLLECTOR_DEPLOYMENT_MANUAL.md、AI_DEPLOYMENT_PLAYBOOK.md、AGENT_DATA_USAGE_GUIDE.md。

目标：完成新电脑准备检查、安装/更新正式 SVN 采集器、验证专用 HuuugeResearch 实例、
启动并确认 READY、在我正常操作后 clean stop/finalize、生成脱敏 Markdown，
再通过 AI Document Assistant 写入飞书并回读验证。

你能在本机完成的检查和命令请直接完成，不要让我手工复制长命令。
只有首次登录、验证码、游戏操作和机器级修改审批可以询问我。
不得修改日常 BlueStacks 实例，不得上传 Raw、完整 decoded values、账号或 Session 标识，
不得修改游戏请求、奖励、余额或服务器状态。

每个阶段只告诉我：当前状态、已确认结果、需要我做的一件事。
```

## 6. AI 应执行的完整流程

### 阶段 A：读取与预检

AI 应：

1. 安全同步两个必需 Git 仓库，保留本地修改；
2. 读取仓库规则、当前状态、部署手册和 Agent 数据规范；
3. 检查 Windows、Git、SVN CLI、Python、BlueStacks 和选定 AI；
4. 检查 `C:\HuuugeCollector` 是否已安装；
5. 检查是否已有独立的 `HuuugeResearch` 实例；
6. 输出“已满足 / 需要登录 / 需要审批 / 阻塞”，不要直接倾倒底层日志。

### 阶段 B：安装或更新正式采集器

若尚未安装，AI 从公司 SVN 正式入口取得 [`HuuugeCollector_Installer.zip`](http://140.143.33.242/svn/cr/x_proj_design/trunk/HuuugeCollector/release/HuuugeCollector_Installer.zip)，解压后启动：

```text
HUUUGE_BOOTSTRAP.cmd
```

若已安装，AI 使用：

```text
C:\HuuugeCollector\HUUUGE_BOOTSTRAP.cmd
```

Bootstrap 负责 SVN 更新、Python 环境、运行组件同步和预检。SVN 首次认证由新人在系统界面完成；AI 不读取或保存密码。

### 阶段 C：准备独立研究实例

AI 按 `AI_DEPLOYMENT_PLAYBOOK.md` 判断 S0–S8 中已经完成到哪一级，不重复执行已完成步骤。

如果缺少专用实例或采集组件：

1. 保持日常实例不变；
2. 展示专用目标、备份、修改范围和回滚路径；
3. 等待新人确认；
4. 只在 `HuuugeResearch` 上继续；
5. 用真实 `uid=0(root)`、Frida attach、ARM64 Gadget、真实 decoded RPC 作为验证，不用“看起来已安装”代替证据。

### 阶段 D：开始采集

AI 启动 `C:\HuuugeCollector\HUUUGE_COLLECTOR.cmd`，或在已打开 GUI 中执行“1. 开始采集”。

只有同时满足以下条件，AI 才能告诉新人开始操作：

- hooks 已安装；
- 至少一个真实 RPC 已保存并解码；
- Raw 和 decoded 文件写入正确的本地 Session；
- GUI 或控制器显示：

```text
READY，可以开始玩了
```

未出现 READY 时，新人不要开始操作。AI 应读取 `.local\bootstrap\` 和 `.local\controller\` 的最新报告自行诊断。

### 阶段 E：新人正常操作

新人可以进入任意当前可用系统并正常操作。无需提前选择模块，也无需手工打标。

First Run 建议至少进行 5 分钟正常操作，并覆盖：

- 大厅进入；
- 一次可正常完成的 Slots 操作；
- 一个当前可见的活动、任务、奖励或商店页面。

这只是首跑完整性验证，不用于输出概率、RTP、EV 或正式数值结论。

### 阶段 F：停止并整理

新人说“可以停止”后，AI 执行“2. 结束采集并整理”，等待 clean stop 和 finalized 完成，不强制关闭 BlueStacks 或采集器。

AI 随后验证：

- `manifest.json` 状态为 stopped/finalized；
- RPC 总数大于 0；
- decoded 总数大于 0；
- `rpc_inventory.csv` 已生成；
- `field_paths.csv` 已生成；
- 最近一次 analysis/module catalog 可打开；
- Raw 与含值 JSON 仍只在本机受控目录。

## 7. 如何让 AI 生成 Markdown

把下面提示交给当前 Agent：

```text
请分析最近一次已经 finalized 的 Huuuge Session。
先读 AGENT_DATA_USAGE_GUIDE.md、manifest、rpc_inventory、field_paths 和相关 module dossier，
不要一开始扫描全部 Raw。

生成一份中文 Markdown《Huuuge First Run 采集结果》，包含：
- Session 时间范围与游戏/descriptor lineage（脱敏）
- RPC 与 decoded 计数
- 本轮实际出现的模块和 endpoint 数量
- L0-L4 Evidence Level
- 已确认结构、缺口和下一步建议
- 验证清单

删除账号 ID、token、绝对用户目录、完整余额轨迹和原始 payload。
没有足够样本时，不输出确定性的概率、RTP、EV 或付费价值结论。
把文件保存到 C:\HuuugeCollector\.local\reports\first-run\Huuuge_First_Run_Report.md。
```

AI 生成后必须自检：Markdown 能打开；没有凭据或玩家标识；所有关键结论有范围和 Evidence Level；引用能回到本机 Session 或 commit-pinned dossier。

## 8. 如何通过 AI Document Assistant 写入飞书

### Codex 或已配置 MCP 的 Trae

让 AI 执行以下逻辑，不让新人复制飞书 API 请求：

1. 调用 `feishu_healthcheck`；
2. 调用 `search_documents` 搜索目标标题，避免重复创建；
3. 没有旧文档时调用 `create_document`；已有文档且确定需要整篇更新时调用 `replace_document`；
4. 调用 `get_document` 回读标题和正文；
5. 除非 User 明确要求私有、只读或不授予编辑权限，新生成云文档一律设置为企业内可编辑并回读验证；如果管理员策略拒绝，不要重试创建，记录文档已创建、权限待管理员处理。

可直接交给 AI：

```text
读取 C:\HuuugeCollector\.local\reports\first-run\Huuuge_First_Run_Report.md。
先调用 feishu_healthcheck，再搜索《Huuuge First Run 采集结果》。
不存在则通过 AI Document Assistant 创建，存在则先告诉我将更新哪一篇。
创建/更新后调用 get_document 回读，确认标题、正文和权限状态。
不要把凭据、token、Raw、完整 decoded values 或本地 Registry 内容写入飞书。
```

### Trae 尚未配置 MCP

Trae 继续负责采集与 Markdown；飞书发布交给已配置 AI Document Assistant 的 Codex 或其他批准的 MCP Host。只交接脱敏 Markdown 文件路径，不把飞书密钥交给 Trae，也不直接拼接飞书 OpenAPI。

## 9. 如何验证 First Run 成功

只有以下项目全部通过，才算成功：

| 验收项 | 成功证据 |
| --- | --- |
| AI 主入口 | 新人从 Codex 或 Trae 提示词开始，没有被要求手工排查底层命令 |
| 独立环境 | 使用 `HuuugeResearch`，日常 BlueStacks 实例未改动 |
| 采集启动 | 出现 READY，且至少一个真实 RPC 已保存/解码 |
| 安全停止 | manifest 为 stopped/finalized，clean stop 完成 |
| 整理输出 | inventory、field paths、module catalog 可打开 |
| Markdown | 中文、脱敏、Evidence Level 与限制完整 |
| 飞书 | Document Assistant 创建/更新成功，`get_document` 回读成功 |
| 权限 | 自动权限成功，或明确记录管理员策略阻塞且没有重复创建 |
| 隐私 | Git、SVN、飞书中没有 Raw、账号、token 或完整含值日志 |

## 10. 常见问题

### AI 一开始就让我复制很多命令

把“统一首跑提示词”重新交给 AI，并要求它先自行执行 read-only 检查。只有登录、验证码、游戏操作和机器级修改审批需要新人参与。

### GitHub Clone 要求登录

新人只在 Git/浏览器认证界面完成登录。不要把密码或 access token 粘贴到聊天。认证完成后让 AI 继续。

### 找不到 SVN

让 AI 检查 TortoiseSVN 是否安装了 command line client tools。安装完成后需要打开新进程再运行 Bootstrap。

### SVN 认证失败

新人用 TortoiseSVN 完成一次公司 SVN 登录，然后让 AI 重试。采集器和 AI 都不应保存 SVN 密码。

### 找不到 Python

让 AI 安装 Python 3 并验证 `py` 可调用，再重新运行 Bootstrap。不要让新人手工维护虚拟环境。

### GUI 能打开，但没有 READY

不要开始操作游戏。让 AI 读取 `.local\bootstrap\` 和 `.local\controller\` 最新报告，并按 Deployment Playbook 判断 S0–S8。不得改动日常实例。

### AI 想直接修 Root 或 BlueStacks 文件

必须先展示专用实例、目标文件、备份、影响和回滚路径并获得明确批准；否则停止该步骤。

### 停止后没有结果

先检查本轮是否真正出现 READY、是否存在 active Session、manifest 状态和控制器报告。不要把旧 Session 当成本轮结果。

### Markdown 含有账号或完整数值轨迹

不要发布。让 AI重新生成，只保留聚合计数、结构、字段路径和去标识化结论。

### 飞书出现同名重复文档

停止再次创建。先调用 `search_documents`，确认 Registry 中的 document ID；更新旧文档应使用 append 或 replace，而不是重复 create。

### 文档创建成功，但企业编辑权限失败

记录 `document_created=true` 与权限失败状态，不要重试创建。由企业管理员确认共享策略后，再对原 document ID 调用权限工具。

### Trae 无法调用 Document Assistant

不要改用明文密钥或自写飞书请求。保留脱敏 Markdown，由已配置 MCP 的 Codex 完成发布。

## 11. 最短首跑路线

```text
把统一提示词交给 Codex 或 Trae + DeepSeek
  → AI 同步 Git、检查新电脑
  → AI 安装/更新 C:\HuuugeCollector
  → 新人完成登录和必要审批
  → AI 验证 HuuugeResearch 并启动
  → 看到 READY，新人正常操作
  → 新人说“可以停止”
  → AI clean stop/finalize
  → AI 生成脱敏中文 Markdown
  → AI Document Assistant 写入并回读飞书
  → 按验收表确认成功
```

## 12. 独立策划盲测

TASK-0011 的完成必须由一位未参与开发的策划验证。测试者只收到：

- Git 仓库地址；
- 《Huuuge 新人上手指南（First Run Guide）》飞书文档。

不得提供口头补充、私聊命令或开发者代操作。测试记录使用 [`REPORTS/TASK-0011-FIRST-RUN-VALIDATION.md`](REPORTS/TASK-0011-FIRST-RUN-VALIDATION.md)。如果测试者需要额外说明，说明本身就是文档缺口；只允许修改文档和流程，不新增功能。
