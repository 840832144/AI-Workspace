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
