# TASK-0039｜DSH 答复复核与接入停止记录

> 后续进展：原实例面板字段与定址入口已实际取得，最终计价仍待合证；当前账本2363.776秒、准备余量6.224秒。详见[面板实读进展](PANEL-FIELDS-PROGRESS-20261014.md)。下文保留当时状态/原授权与问题历史，不用旧“无字段”、余量或待答问题覆盖新事实。

2026-10-14，继续原 Task / PR #16/#17。DSH 原答复属于外部分析材料，不是新的授权或正式 ChatGPT Review。原文在受控目录保留，公共[答复副本](DSH-ANSWER-20261014.md)只脱敏设备连接标识。本文件记录 Codex 独立核验后采用的结论；Round 1–5、旧问题稿及全部失败不改写。

## 已确认与尚未确认

| 项目 | 本次结论与证据边界 |
| --- | --- |
| 直接失败点 | 接受：Frida 16.7.19 的 NativeBridge 加载函数返回空后抛出当前错误，不能按文案判断没有 ARM 翻译。源码的 API 缺失与资源缺失使用其他错误分支；已有映射与 native 诊断结果也支持已到加载阶段。 |
| 环境 | 原实例一次只读查询实测 **Android 15 / SDK 35**，bridge 属性为 libnb.so；maps 含 libnativebridge.so、libart.so、libhoudini.so、libnb.so。DSH 的 Android 12 描述不适用于本实例。没有 attach、点击、购买或修改环境。 |
| namespace 根因 | 保留假设。modern 无 namespace 参数、legacy 固定值、源码 FIXME 均可核实；没有 bridge 错误原因或当前 namespace/文件访问证据，不能把 SDK≥30 加映射存在直接提升为 H1/H2 已证实。 |
| Android 版本分水岭 | 不采用确定性结论。issue #3421 原报告版本为 16.6.6，不是 16.7.x；#3497 还包含 Android 9 / LDPlayer 的同类失败报告。第三方换环境成功不是本机保证。 |
| 撤销与驻留 | 接受库卸载限制：modern/legacy 的 unload 都为 null，加载参数包含 eternal/sticky。停止脚本、解除 Interceptor、断开 session 与卸载 emulated agent 库不同。不能再承诺 detach 即干净卸载；这次没有成功加载该 agent 的证据，也不能反向宣称已经驻留。未杀游戏进程、未重启清理。 |
| 辅助二进制 | 本次直接字节比较：官方/准备版均114,292,664字节，仅路径常量内19字节不同；四个 attempt 的 helper 与准备版逐字节相同。常量起点0xaff81、含终止零23字节；实际差异范围0xaff82..0xaff96。替换值为 `/dev/null/` 加12个x。证明没有额外二进制改写及 helper 维度一致，不追认 Python/JS/控制器完整冻结，也不以“仅改常量”证明所有环境因果已排除。未运行会修改策略的官方版作对照。 |
| ARM64 内嵌资源 | 单个文件名字符串命中不足以独立证明载荷完整、释放可访问或 ABI 可加载；当前错误与资源缺失分支不同，支持故障阶段区分。 |
| 0x310 | 保留为异常报告中的不可读地址；没有证据确定它一定是 NULL+字段偏移。旧栈出现在诊断 getter/字符串读取，不能推出模块基址为 null、namespace 或 ABI 原因。主动诊断 getter 已移除。 |
| 内存轮询 | 仅为未实现候选，不承诺可用，也不证明必然超权限。v31 metadata 的字段名/token 不是物理偏移；需匹配二进制的 MetadataRegistration.fieldOffsets、对象入口及生命周期证据。单有字段采样也不证明自然接受；是否可与既有独立协议/日志合证，仍需具体方案。 |
| Java 旁路 | 已对本地 APK 三个 DEX 字符串表离线筛查，未命中指定面板/报价/卡视图类型；存在 UnityPlayer/BillingClient 名称。只排除这些名称的直接命中，不宣称已排除全部 Java 调用链，BillingClient 也不等于局内票券报价。 |

源码依据：[Frida 16.7.19 加载分支](https://github.com/frida/frida-core/blob/16.7.19/lib/agent/agent.vala#L1361)、[驻留参数](https://github.com/frida/frida-core/blob/16.7.19/lib/agent/agent.vala#L1401)、[两类 NativeBridge 绑定](https://github.com/frida/frida-core/blob/16.7.19/lib/agent/agent.vala#L1534)、[资源选择](https://github.com/frida/frida-core/blob/16.7.19/src/linux/linux-host-session.vala#L384)。案例依据：[issue #3421](https://github.com/frida/frida/issues/3421)、[issue #3497](https://github.com/frida/frida/issues/3497)；后者本次读取仍 Open。字段偏移依据：[Il2CppDumper GetFieldOffsetFromIndex](https://github.com/Perfare/Il2CppDumper/blob/master/Il2CppDumper/Il2Cpp/Il2Cpp.cs#L274)及同文件 MetadataRegistration 初始化。社区报告只作为案例，不当作上游保证。

## 已完成的最小修改与验证

原 emulated 绑定已有三次相同加载失败，且新增库驻留限制与预期撤销不符，因此**停止这个绑定**。停止依据不依赖 SDK 阈值是否为根因。`bv_observer.py` 的普通 CLI、内部 worker、直接 inspect/worker 调用均在导入 Frida、加载 helper、创建输出目录、连接 ADB 或写账本前拒绝；返回可读停止原因，CLI exit2。没有运行时强制开关；历史实现与证据保留供审阅，不部署新读取方式。

92项离线及实际函数/CLI回归通过，unittest 32.854秒、exit0；正式账本前后字节不变。新增三项覆盖普通入口、worker 绕行和实际两个 CLI 调用，均不产生设备侧动作。既有持续四卡、覆盖恢复、结算、来源、资源与 STOP 回归保留；旧观察管线的预算/清理单测在隔离替身内测试，不放开生产停止。此结果不证明面板接入、真实受理或十局完成。

唯一新增设备读取0.407秒已记入原账本。累计 **52票 / 2358.402秒 / 8个完整位置**，历史定位3局不变；剩44票、3041.598秒、10位置。预留十局3000秒及30秒收尾后，准备余量 **11.598秒**。本次零新购买、零游戏输入、零 attach；新十局仍 **0/10，证据不足、未运行**。第6位置真实未达标、第8位置旧8票限额下12票扣减/接管保留，不能与新候选拼接。

当前 `Device.context` 尚无真实面板 reader，旧 `quote_resource_clock_not_covered` 与 `current_panel_quote_unavailable` 没有被本次查询解决。保留购买阻断。单局16票不替代整批预算；44票仅可覆盖真实四卡最低报价4票时的十局40票，不能用历史报价假定该条件成立。

## 给 DSH 的剩余问题，可原样转交

> 已确认原实例为 Android15/SDK35，并停止现有 emulated 绑定；无需再证明 SDK≥30。请只给出现有授权下可行的具体只读路径，或明确缺少哪项证据：
>
> 1. 若考虑 native realm 读取，如何从**匹配版本二进制**确定 fieldOffsets 和当前 BuyCardPanel/BetAddView 活跃实例，而不全堆扫描、不主动调用业务方法、不重启或重打包？请给出最小离线定位代码/依据，不能仅给 metadata token。
> 2. 该路径如何同时绑定当前面板生命周期、卡数、最低普通 Bet、价格影响及最终 TicketCost？如何判定快照计算完成、过期与撤销？字段采样与自然业务受理应分开，再说明如何与既有独立协议/客户端日志关联同一局/卡/动作。
> 3. 提供具体撤销边界与必要设备时间估计。当前准备余量11.598秒、原账本不清零；若无法满足，请明确需改变的环境或额度及依据，不把估计当批准，不直接执行。

对象候选沿用[原问题稿表二](DSH-QUESTIONS-20261014.md)：BuyCardPanel/BetAddView/BuyCardContext → 当前报价；BaseBingoCardView/BingoPlayView → 同局同卡交互与闭局；DaubCell/DaubCellView及既有独立日志 → 自然受理。它们目前仅为静态候选，未填入虚构运行值。

没有采用换实例、重打包 APK/Gadget、切换 server 架构、升级依赖、改安全策略或杀游戏进程的方案。上述环境变更超出现有原实例范围；原限定被动 Hook 授权仍有效，不重复申请。当前结论是**现有绑定不可用且没有已验证替代**，不能扩大为“所有授权路径必然不可能”。

## 受控复算入口

本机 `execution16/hook/dsh-review/REVIEW.md` 为入口，包含 environment.json、helper-comparison.json、dex-screen.json、tests.txt、test-summary.json 和离线复算脚本；官方源码快照用于行号复核。DSH原文、原脚本、旧attempt及唯一runtime/budget.jsonl留本机。公共仓库只保留脱敏答复与本复核，不上传二进制、APK、账号、卡面、余额或完整日志。

任务 In Progress，等待方案答复与统一 Review；尚未完成持续四卡交付。不合并、发布、SVN、扩权或finalize。Subagents: none。
