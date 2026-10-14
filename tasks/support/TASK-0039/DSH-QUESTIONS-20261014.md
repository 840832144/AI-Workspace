# TASK-0039｜给 DSH 的定位问题（2026-10-14）

> 后续进展：原实例面板字段与定址入口已实际取得，最终计价仍待合证；当前账本2363.776秒、准备余量6.224秒。详见[面板实读进展](PANEL-FIELDS-PROGRESS-20261014.md)。下文保留当时状态/原授权与问题历史，不用旧“无字段”、余量或待答问题覆盖新事实。

> 本稿原问题/授权历史保留。DSH答复后的当前事实、agent库卸载限制、绑定停止与剩余具体问题见[独立复核](DSH-ANSWER-REVIEW-20261014.md)。限定被动Hook授权未撤销；旧环境版本未知、旧准备余量与等待答复描述只代表当时状态。

User要求整理当前问题，供DSH解答。本文件不申请新任务、权限或额度；继续原PR #16/#17。请优先回答问题一，再给出可落地的最小修改与验证方法，不建议重做采集平台。

## 当前要解决什么

目标仍是普通四卡持续自动玩、可靠补漏、覆盖卡恢复、局末收尾、结算续局；一个冻结候选连续十局，每局严格>90%，争取整批加权≥95%。既有资源/STOP/过期点击/逐卡重标定/回放修复保留。

现在卡在**真实购买前面板来源尚未接入**。旧存档曾显示4票，而真实购买扣12票，不能再以存档或历史扣费授权购买。User已明确批准限定的进程内被动Hook，当前不是等待这项授权，而是观察组件在原模拟器上的兼容性失败。

本轮89项离线与入口回归通过，不能替代真实来源或整局验收。新十局0/10，零新增购买、零游戏点击；不是十局已经跑完而未达标。

## 一、优先问题：Frida无法进入现有ARM64翻译环境

### 已核实的环境与结果

- 原授权MuMu实例，设备ABI列表为`x86_64,arm64-v8a,x86`；原ADB已有uid0、SELinux为Permissive。没有新增Root或执行setenforce。Android具体版本尚未在本轮采集，不能假定。
- 游戏本地`libil2cpp.so`为ELF AArch64；已有`global-metadata.dat`为v31。进程映射同时包含游戏的ARM64库及`/system/lib64/libhoudini.so`。
- 本机Frida Python **16.7.19**；使用对应官方`frida-server-16.7.19-android-x86_64`。
- 辅助服务仅监听随机名称的Unix abstract socket，经本机ADB forward访问。正式尝试使用`-D -P -C`，不启用preload、crash reporter或设备TCP监听。
- 原服务端默认会修改SELinux策略。因此只在本机辅助二进制中，将唯一的`/sys/fs/selinux/policy`常量改为`/dev/null/`下不可能存在的子路径，使上游`g_file_test`失败并提前返回；原二进制保留，使用精确构建指纹约束，未改游戏或系统策略。静态指令验证了该检查及提前返回分支；每次实际前后策略摘要和enforcement一致。
- 第一次服务启动用了shell后台作业，ADB等待超时；已改为服务端自身`-D`就绪握手，服务能正常启动。
- 后续三次进入`device.attach(pid, realm='emulated', persist_timeout=0)`均返回：

```text
ProtocolError: process is not using emulation
```

- 两次定位尝试先以native realm成功建立会话并加载有限诊断脚本，再尝试emulated realm；失败仍相同。尚未加载面板业务观察脚本，未获得任何真实面板字段或自然业务回调。
- 一次诊断试读NativeBridge错误信息，返回指针不可读：`access violation accessing 0x310`。不能据此确定错误字符串、ABI或namespace原因；该主动诊断getter已从提交代码移除，不再盲读该指针。所有异常保留，游戏进程仍存活。
- 四次探索不是冻结验收候选；未完整冻结各探索版本，因此不作为正式运行版本绑定或成绩证据。交付入口现已增加运行前源文件快照；最终改动未再上机消耗余量。

### 已查上游源码，仍未确定的部分

在[16.7.19 agent.vala](https://github.com/frida/frida-core/blob/16.7.19/lib/agent/agent.vala#L1273)中，该错误在`load_library/load_library_ext`返回空时抛出；它不能直接证明进程没有ARM翻译。该版本对modern与legacy NativeBridge采用不同加载分支；legacy分支含固定namespace值，modern分支也有namespace相关TODO。我们**没有证据**确定当前失败就是namespace、文件访问或某一具体Houdini版本问题。

[linux-host-session.vala](https://github.com/frida/frida-core/blob/16.7.19/src/linux/linux-host-session.vala#L352)对AMD64选择`frida-agent-arm64.so`，所以不能简单认为x86_64服务端只支持ARM32。当前主线源码仍有上述加载分支，不应仅凭猜测升级依赖。

### 请DSH回答

1. 对这个“native attach成功、ARM64库实际映射、emulated attach在加载观察组件时失败”的组合，最可能的原因是什么？请区分已知兼容性事实与待验证假设，并指出需要的**最少只读证据**。
2. 在原实例、原进程、现有权限下，是否有已验证的被动观察接入方式？请给出适配Frida 16.7.19/Houdini的具体代码或官方实现入口，说明如何正确处理模块与namespace，如何卸载/撤销；不要靠修改游戏返回值、完整性校验或SELinux策略解决。
3. 如果必须更换运行环境、重启游戏、重打包APK、修改安全设置或使用新增技术权限，请明确标出来；这些不在本次授权内，不能默认执行。若现环境无法可靠实现，也请直说依据，不提供“先强行点购买试试”的方案。

## 二、接入后需确认的最小字段语义

以下只通过本地元数据证明存在，**尚未证明运行值、偏移、对象关系或业务含义**。当前代码只读元数据、在自然回调后读有限字段；未主动调用游戏业务getter或制造Daub。

| 用途 | 候选对象/字段 | 需要确认 |
| --- | --- | --- |
| 卡数/模式/当前面板 | `BuyCardPanel._cardIndex/CardAmounts/_panelModel`；`BuyCardPanelModel._currentChooseMode` | 对应当前可见面板的生命周期、卡数索引与普通模式值；关闭/销毁/换选择时如何撤销。 |
| Bet与实际报价 | `BuyCardPanel._betData/_betAddView/TicketCost`；`BetAddView._index/_usableMaxBetIndex/_betCost/_betListData` | `_betCost`是每卡价、总价还是其他值？当前可选普通档与最终票价如何对应？哪个自然回调是计算完成点？不能主动调用getter代替观察。 |
| 价格影响 | `BuyCardContext.CardCount/BetCost/MissionSaleBubbleVisible/DisableRoundBuffResIDs`；面板`_isShowingBuffCost/_multiFastBuffActive` | 哪些字段足以排除折扣/免费局/特殊模式的影响；未知影响继续不买。 |
| Bingo覆盖后可点击性 | `BaseBingoCardView.controller/_disableCellClick/canvasGroup/isPlayingBingo/isBingoPlay/MaxLevelBingoMask`；`BingoPlayView._isGameOver/_isGamePaused` | 如何绑定同局同卡并判断真实输入许可？几何可见与可交互分别验证，不能一张卡不可用就停止其他三张。 |
| 自然成功受理 | `DaubCell.positionComp/commonComp`；`DaubCellView.controller/isViewDaubed/isBingo`；自然`SetDaubed/ShowManualDaub` | 哪个事件证明普通自动输入被接受，如何区分能力自动填充、人工输入和只有显示变化？需要与原日志/协议及输入时间交叉核验。 |

请优先给出可从自然回调取得当前对象的路径、类型/字段关系及最小观测片段。不要全堆扫描，不采集账号、凭据或无关对象；不要把静态token当运行时地址、把可见闪动当已填成功。

## 三、现有边界与继续条件

- 已授权技术范围：原实例当前买卡面板与同局四卡的限定被动Hook；不主动调用业务方法，不改业务字段/返回值/协议，不新增Root/证书/网络权限，不重启原采集器。
- 单局≤16票且最低普通档、≤300秒；累计≤96票、5400秒、18完整位置，历史3局定位不再增加。
- 最新账本：**52票、2357.995秒、8个历史完整位置**。剩44票、3042.005秒、10位置。按十局3000秒+30秒收尾保留，只有**12.005秒新增准备空间**；不要建议无上界的设备试探。离线源码分析与回归可继续，不清零旧账本。
- 当前最低四卡价未知。只有真实价4票的条件场景可以覆盖十局40票；若8/12/16票，现总票额分别缺36/76/116票。单局≤16不能替代整批预算。
- 旧实际`--check`另有`quote_resource_clock_not_covered`：旧钱包变动时间不在新采样覆盖内。观察组件能加载也不代表余额、报价及整批条件已经通过；这个时间来源问题保留。
- 第6位置历史真实未达标、第8位置当时12>8票及User接管保留；不能拼入新十局，不用Unknown当成功。

请按“原因/置信度 → 最小代码改动 → 不消费票券的验证 → 成功与停止判据 → 是否需要超出现有授权”回答。若方案无法在现有准备时间内完成，请估计必要时间并说明依据，不自动增加额度。

## 代码与证据入口

- 原实现PR：[PR #16](https://github.com/840832144/AI-Workspace/pull/16)，原治理PR：[PR #17](https://github.com/840832144/AI-Workspace/pull/17)。
- 实现分支中的`bv_observer.py`、`bv_observer.js`、`bv_observer_bridge.js`、`tests/test_observer.py`：受控观察入口与失败撤销；不是已完成的生产PanelQuote reader。
- `bv_live.py`中的`Device.context`、`PanelQuote`、`preflight/start_batch`；`bv_autoplay.py`中的持续处理/补排；既有独立核验保留。
- 授权范围：[SOURCE-OBSERVATION-SCOPE-20261014.md](SOURCE-OBSERVATION-SCOPE-20261014.md)。
- 本机受控入口：`%LOCALAPPDATA%\AI-Workspace\bingo-voyage-task0039\execution16\hook\REVIEW_HOOK.md`，包括attempt-1至4的结果、观测错误、清理检查、离线复算和最终测试。完整日志、卡面、账号和辅助二进制不随公共问题稿转交。

Subagents: none。
