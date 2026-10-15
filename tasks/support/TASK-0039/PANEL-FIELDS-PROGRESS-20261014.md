# TASK-0039｜原实例面板字段读取进展与剩余阻塞

2026-10-14，User要求优先继续完成目标，常规开发自行解决，具体问题可转DSH。本文件更新[DSH答复初次复核](DSH-ANSWER-REVIEW-20261014.md)后的进展；不新建Task、不扩大权限或资源。

## 已实际推进

emulated绑定停止，但原实例不是“所有接入方式均不可行”。已从现有本地ARM64 ELF与v31 metadata解析字段偏移表，再用方法反汇编核对UIManager静态实例、面板列表和BuyCardPanel对象链。通过原有ADB权限，仅定址读取原游戏这些对象，没有attach、装载agent、全堆扫描、调用游戏方法或修改安全设置。

过程中保留三次失败/未完成观察：0.125秒因两个offset0映射无法唯一选择；离线按全部PT_LOAD关系修正，拒绝只读整文件映射；0.156秒因原始读取流不符合长度；查询Toybox/ADB源实现后改用dd status=none；0.594秒已读到UIManager，但大厅没有BuyCardPanel。没有重复emulated尝试。

图像仅用于导航。一次截图读取1.078秒，随后一次新鲜截图及前台核对后的非消费导航1.046秒打开选卡面板。下一次定址读取**2.375秒、52个ADB命令、846字节**，获得当前面板字段；保留映射ELF头/root方法指令比对、类型与回指、前后列表版本、进程start_ticks核验及原始读取序列。

| 当前结构化读数 | 结论边界 |
| --- | --- |
| 四卡；卡数索引2 | 来自当前面板数组与索引，不来自截图或旧存档。 |
| Bet索引0；最高可用索引0 | 当前可用范围候选，不靠历史Max Bet或手填最低档标签。 |
| BET_NP_SYMBOL_3；BaseBetConfig.cost=3 | 当前基础每卡3票，未调整四卡乘积12；**尚非最终可支付报价**。 |
| _betCost缓存3；mode raw1 | 离线解码枚举默认值确认raw1=Bingo13；仍不证明最终价格或完整普通模式绑定。 |
| _canPlay=true；_isShowingBuffCost=false；_multiFastBuffActive=false | 仅原始字段，不直接提升为购买许可或price_effects=[]。 |

发现`BuyCardPanel.TicketCost`实际为GameObject，不是数值票价。`BetAddView.get_BetCost`常规分支经过RuntimeBetListData索引及BetData.get_Cost；RefreshTicketText还调用免费局、折扣与相关资源逻辑，PlaySelectCard另有MissionSale/MultiFast/引导分支。这些业务方法只离线分析，没有调用。

补充离线定位已把管理器获取链追到GameComponentRoot静态实例及组件表；折扣适用性涉及到期时间和最低Bet，不能用面板布尔标志替代。枚举默认值按[Il2CppDumper压缩整数解码](https://github.com/Perfare/Il2CppDumper/blob/master/Il2CppDumper/Extensions/BinaryReaderExtensions.cs)核对；这些静态结论不证明当前动态分派或价格影响状态。

## 代码、验证与尚未交付的部分

新增`bv_panel_fields.py`纯解码器，复用已观察的有限对象路径；返回原始字段候选，明确不是PanelQuote。生产Device.context尚未装配最终报价reader，购买继续阻断。原四卡自动玩、覆盖恢复、末球收尾、结算与STOP修复均保留，没有以字段读取替代完整对局。

既有92项离线/实际函数与CLI回归通过（32.854秒、exit0、正式账本不变）。新增解码器另通过**6项受控离线复放**：真实读取顺序/字段完全一致、错误根类型拒绝、Bet回指变化拒绝、非法卡数索引拒绝、面板列表版本变化拒绝、原始候选不能通过购买报价校验。后五项是负例扰动/隔离验证，不伪装成新增真机观察；编译与diff检查通过。

剩余技术问题已经具体化：完整免费/折扣/其他价格影响字段集合、计价完成与面板生命周期绑定、MethodInfo动态分派分支，以及覆盖后真实受理的独立证明。当前尚不能把基础12票升级为最终报价；旧资源时钟覆盖缺口也未消除。已整理给DSH的具体代码问题，User回复“ok 我现在告诉它”。同时继续可独立完成的离线工作，不逐阶段等待Review。

## 资源与验收

累计**52票 / 2363.776秒 / 8个历史完整位置**，定位3局不追加。剩**44票 / 3036.224秒 / 10位置**；保留十局3000秒与30秒收尾后，准备余量**6.224秒**。本轮仅一次非消费导航，无购买、填格、attach或agent；账本未清零。

新十局仍0/10，属于未运行/最终来源证据不足。第6位置真实未达标、第8位置旧8票上限下12票扣减和User接管保留，不混版、不挑局。若最终普通四卡价格确认12票，十局需120票，较剩余44票缺76票；这是条件资源计划，不是假定报价已认证或追加授权。16票单局上限不能替代整批96票总额。

## 受控复算与DSH入口

本机`execution16/hook/dsh-review/REVIEW.md`及`DSH-FOLLOWUP.md`：后者给出字段偏移、定址对象路径、计价调用链、三个精确问题和余量。`offline_fields.py`、`offline_methods.py`仅处理已有本地二进制与metadata。`panel-field-observation-4/reads.jsonl`和精确源快照保留真实读数；`replay_panel_fields.py`通过实现解码器重放，`panel-replay-result.json`为6项结果。前3次结果、导航记录与唯一账本均保留。

不把二进制、账号、卡面、真实指针地址、全部配置或原始内存片段放入公共Git。原DSH答复保留作为参考，当前实际结果以本报告及独立证据为准。

继续TASK-0039 / PR #16/#17，Task In Progress；完整交付未完成。限定被动观察授权有效，不新增权限、环境或任务。不合并、发布、SVN或finalize。Subagents: none。
