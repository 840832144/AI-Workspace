# TASK-0041 实施进度与人工试玩交接

本报告为阶段实测，不是最终Accepted。完整执行规格不变；Subagents: none。

## 治理和隔离

- remote-CAS已分配TASK-0041；Gate 0最终校验与推送d65039f，随后开始业务实现。Registry20个canonical、0冲突/错误、6项既有grandfather警告。
- 原TASK-0039暂停同步af46b8b，PR #16/#17保持原分支、历史和账本；新Demo未操作原实例，不继承线上预算。
- 业务源码为独立本地Git `D:\BingoCoreDemo`，分支codex/task-0041-core-demo；实现c31f0c8。没有批准远端，业务代码尚未远端推送；公共治理PR #21只放治理和摘要。

## 已实现与实测

独立netstandard2.1 C#规则、单权威本地服务、1/2/4/6卡、九道具、充能/自动道具、连锁、补填、上限、结算返回。固定合成场景与三层证据标记见业务docs/RULES.md和QUESTIONS.md，DSH-VERIFY.md已准备，尚未收到dsh结果，不假称已二次确认。

46项规则测试通过，覆盖部分填充、七类buff零目标已用、E1先放后赚、动态/冻结补填、炸弹与魔方、重复×2等。真实发布的自包含服务39项HTTP集成通过，四种卡数各自然结束一局并返回再开；120条真实时间/动作记录独立离线复算，接受/拒绝、资源总数和新增事件一致。

Windows PowerShell5.1实际包入口启动、检查、重复启动、停止、重复停止通过。实际浏览器入口完成大厅→选12秒固定场景→开局扣1本地票→自然结束（未填格，0 Bingo）→返回大厅。以上不是Unity客户端验收或User体验反馈。

自动审批审查拒绝了“另起服务占端口，确认启动器拒绝且不误杀”的测试命令，原因仅blocked by policy；未改命令/换工具绕过，此项未验证。最初本机代理导致回环健康检查502，已用仅该包的直连回环修复；未改变系统代理。复算运行中日志曾遇到共享锁，停止该服务后复算成功，方法已写入移交文档。

## 可玩阶段包和受控证据

- 临时浏览器试玩包：`D:\BingoCoreDemo\artifacts\packages\BingoCoreDemo-0.1.0-browser-preview.zip`；完整解压后双击启动.cmd，不需要SDK/Editor。明确标temporary browser，不能代替Unity最终交付。
- 规则/HTTP/复算/启停证据：`D:\BingoCoreDemo\artifacts\evidence`；实际对局复算源：`artifacts/server/runs/20261015-045004-8aafd7d5`。本地日志不上传公共Git。
- 普通试玩由User接手；Codex负责专业边界、协议、复算和包测试。人工试玩清单在业务README.md，尚未反馈，不写已验收。

## 剩余项

Unity最小工程/表现层及导入一致性脚本已写；未找到团队模板。User已授权本机安装Unity。独立.NET10.0.402已安装并用于自包含服务；Unity6000.3.25f1官方大包下载遇到超时，尚未安装Editor。通过现有WinGet安装官方Unity Hub进行中；许可证和团队模板兼容尚未验证。

后续继续Unity安装、同一核心包导入一致性、原生Windows包构建和真实客户端入口验证；普通试玩反馈与专业测试分列。TASK仍In Progress，不逐阶段等待Review；完成后统一交Review，不合并、发布、提交SVN或finalize。

## 后续专业边界修复与版本区分

业务提交426b145补齐显式endBonusCharge配置：结束补填可按配置增加进度，仍不抽新道具；已接受且进入收尾的连锁成功填格也记录进度。最新规则测试47项通过，新核心离线重放原120条实际输入仍一致。此前39项HTTP集成属于c31f0c8服务；新版独立端口回归启动命令同样被自动审批审查以blocked by policy拒绝，未执行或换方式绕过，新版HTTP复测待补。

已经给User的临时包固定c31f0c8，未在试玩中覆盖。受控复算入口为D:\BingoCoreDemo\artifacts\TASK-0041-Repro-9f9b019.zip，内含自包含复算程序、此前46项规则与120条实际输入；在独立目录实际运行通过，不要求SDK。对应源码归档BingoCoreDemo-source-9f9b019.zip。最新426b145与已交包清楚分列，不将旧服务成绩写为新版本集成通过。

User确认已有Unity账号、许可证未知；Hub安装完成后由User登录核对，不代购或假定Personal资格。Editor下载超时且续传未完成；WinGet远程MSIX安装停在下载阶段，已取消该尝试，改为从同一官方URL下载完整签名包再本地安装，不调整系统代理/安全设置。当前还没有Unity Editor或原生包通过证据。

最新安装结果：Unity Hub官方MSIX已完整下载并通过WinGet声明SHA256与Authenticode Valid/Unity Technologies签名校验，本地Add-AppxPackage成功，3.22.3.65535状态Ok。Editor授权安装继续在后台进行单次有界续传，最多14400秒；只有完整长度和官方签名通过才静默安装到D:\Apps\Unity\6000.3.25f1。状态文件D:\Apps\BingoBuildDownloads\unity-install-status.json，启动PID44780（需现场复核，不凭历史PID停止）。许可证和构建仍未验证，User被请到Hub登录查看，不索取密码。最新源码归档BingoCoreDemo-source-426b145.zip，业务Git干净。

## CLI接入及首次Unity原生构建（取代上文安装中状态）

User随后在Hub安装Unity6.6.5f1，并要求核对CLI接入。旧6.3续传已以curl56停止，状态明确未运行安装器；未恢复旧下载或重复安装。官方Unity CLI通过WinGet安装为1.0.0-beta.13，版本、已安装列表与editors verify通过。Hub包内受保护二进制不能直接运行，未改ACL；采用官方独立CLI的标准安装入口。

业务提交fefe61a79d47e58f40c1ecec27ff947261ca51cd：Build.ps1通过CLI按ProjectVersion.txt匹配精确Editor版本，沿用User的6000.6.5f1；保留显式-Unity路径。编译仍调用既有BingoBuild.Windows的batchmode，未安装Pipeline/MCP/Agent插件，未创建Cloud项目，未改变业务规则。Unity生成的工程设置、场景、meta与packages-lock纳入本地源码。

真实Build.ps1退出0；47项规则测试通过，Unity JsonUtility配置加载与同一核心运行结果逐字等于.NET期望，Windows构建成功（报告95,940,944字节）。最初CLI许可查询报LICENSING_CLIENT_UNAVAILABLE，随后Editor实际取得许可并完成构建；这是查询入口与构建证据的区别，不报告无许可证。原生窗口点击/包启动尚未验证，User接手普通体验；最新HTTP未通过证据仍保留，不用构建或旧版39项成绩替代。

原生候选包：D:\BingoCoreDemo\artifacts\packages\BingoCoreDemo-0.2.0-unity-preview.zip；87,290,883字节，186个条目，版本绑定fefe61a，主要exe/启停入口存在，无运行中会话日志或.runtime。源码归档BingoCoreDemo-source-fefe61a.zip。证据入口为artifacts/evidence/unity-cli-build-summary.json、unity-build.log、unity-interop.txt及rules-tests.txt；均受控本地，不上传完整日志。此前c31f0c8浏览器包未覆盖。

本轮main仍898358f且为当前治理分支祖先。Workspace Sync的Windows PowerShell脚本入口被本机执行策略拒绝，未宣称同步成功；Git直接fetch/祖先检查与Registry单独验证。Subagents: none；TASK仍In Progress，沿用PR #21，不合并、发布、SVN或finalize。
