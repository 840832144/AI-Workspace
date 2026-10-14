# TASK-0039 当前来源缺口与最小观察范围

2026-10-14，配合 EXECUTION-16T-20261014 与 Round 5；状态为**具体待授权方案，未部署**。新资源额度已经批准，新增进程内被动运行时插桩 / Hook 未批准。完整四卡自动玩尚未交付。

## 已检查的路径

| 已有来源 | 能证明什么 | 不能用于放行的原因 |
| --- | --- | --- |
| 当前生产 `Device.context` 的选卡存档、GDS配置 | 持久化选择及静态价格关系 | 不绑定正在显示的面板；第8位置已实证旧4票与实际12票不同。不能包装成PanelQuote。 |
| 既有客户端日志 | 实际叫号、部分接受记录、闭局和扣费 | 第4–8位置已有日志检索没有购买前实时Bet/可选档位；Prepay属于扣费后证据。 |
| 既有协议采集 | 同局四卡、购买请求、终态 | 买卡请求已晚于购买决策，不能授权其自身。保持原采集器，不改请求。 |
| 已有UI hierarchy | 导航层级 | 历史结构没有卡数/Bet/报价语义节点；图像只导航/标定，不OCR补价。没有宣称已排除所有可能接口。 |
| 本机已有IL2CPP元数据 v31 | 下表字段与方法存在、所属类型、token | 静态名称不是运行值，不证明字段语义/当前对象/最终交互许可。 |

本轮本地静态读取核对了30,655条类型记录，字段/方法范围和声明类型一致。旧dump脚本错移头部、把字节数当条数，故没有运行该脚本；受控 `map_metadata.py` 只读取已有本地文件。结构参考来自[Il2CppDumper原项目定义](https://github.com/Perfare/Il2CppDumper/blob/master/Il2CppDumper/Il2Cpp/MetadataClass.cs)。没有连接游戏进程或安装新的运行时服务。

## 拟观察对象与更新点

以下均为已找到的**候选观察点**，仍需在获得明确授权后证明字段关系；没有调用这些方法。

| 用途 | 原类型/字段 | 游戏自然执行时的观察点 |
| --- | --- | --- |
| 当前卡数、面板及普通模式 | `BuyCardPanel._cardIndex/CardAmounts/_panelModel`，`BuyCardPanelModel._currentChooseMode` | `Init`、`RefreshCards`、`OnModeChange`、`Close/OnDestroy` |
| 当前Bet、可选范围与最终价格 | `BuyCardPanel._betData/_betAddView/TicketCost/TextCostNum`；`BetAddView._betListData/_index/_usableMaxBetIndex/_betCost` | `RefreshBetList`、`OnBetChanged`、`RefreshTicketText`；只记录游戏自然计算结果，不主动调用getter。 |
| 价格影响项 | `BuyCardContext.CardCount/BetCost/MissionSaleBubbleVisible/DisableRoundBuffResIDs`，面板 `_isShowingBuffCost/_multiFastBuffActive` | `RefreshDiscountBuff`、`OnDiscountBuffEnd`、`OnRoundBuffEnd`，与现有GDS配置版本交叉核对。未知影响项即不买。 |
| 同局同卡输入许可/覆盖 | `BaseBingoCardView._disableCellClick/canvasGroup/isPlayingBingo/isBingoPlay/MaxLevelBingoMask`；`BingoPlayView._isGameOver/_isGamePaused/_bingoCardViews` | `DisableCellClick`、`ShowMaxLevelBingoMask`、`OnCellClick/CanDaub/TryDaub` 的自然调用及对应字段；关闭、对象销毁或未知覆盖立即撤销该目标。 |
| 自然接受与目标身份 | `DaubCell.positionComp/commonComp`、`DaubCellView.controller/isViewDaubed/isBingo` | 自然 `Daub/SetDaubed/ShowManualDaub` 事件，交叉核对原日志/协议与自动输入时间；不调用这些方法制造填充。 |

## 一次性最小权限请求

仅在原授权实例、原游戏进程，对上述买卡面板及当前一局四卡对象增加**进程内被动Hook**：读取其正常路径已有字段、参数和结果。作用是为生产PanelQuote和逐卡输入许可提供真实来源，不重做采集平台。观察方法地址、字段偏移和对象归属还须验证，不能把静态token当地址。

实现约束：不主动调用游戏业务方法，不修改字段/返回值/业务状态，不发改游戏协议；不新增Root、证书、网络权限或重启原采集器；不采集无关账号、凭据、其他应用或完整内存。若现有运行条件不能完成该限定观察，停止并报告，不扩大范围。

观察输出只落受控本机，包含实例、进程启动身份、对象/面板版本、配置版本、单调观测时间和来源定位。进程变化、面板关闭/选择变化/折扣变化即失效；购买前重读同一面板关系，最终输入仍检查原STOP/截止时间/前台/身份。覆盖卡的几何与交互许可分别核验；不以可见格当成可点击格，未知目标暂停而非全卡停摆。

停止与撤销：沿用批次STOP并让观察器同步退出；观察进程断连、字段/版本不符、延迟异常或游戏异常时撤销快照并停止受影响输入，卸载本观察器。不得通过忽略错误维持购买。被动Hook仍可能影响兼容性、性能或账号状态，不能称为零风险。没有另买定位局；真实接受只在条件齐备后批准的新十局内核验。

本文件只提出上述技术权限；96票/18位置/5400秒等资源不再申请扩大。当前尚未执行Hook、真实面板接入或新十局；获准后先验证真实只读快照与失效，再冻结完整候选、核对最新整批预算，满足条件直接连续运行，无需逐阶段Review。

Subagents: none。
